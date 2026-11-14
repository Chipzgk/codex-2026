"""End-to-end: real base data -> injected labelled events -> 4 methods -> metrics."""
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from .data import load_all, clean, longest_valid_segment
from .inject import inject
from .features import add_features, feature_columns, reliability, smooth
from . import fuzzy_risk

DO_DANGER = 3.0
DEBOUNCE = 2  # an alarm needs N consecutive points (applied to every method, so the comparison stays fair)


def debounce(mask, n):
    m = pd.Series(np.asarray(mask, bool)).astype(int)
    return (m.rolling(n, min_periods=n).sum() == n).astype(int).values
PH_RANGE = (6.5, 9.0)


def prepare(raw_dir, seed=42, min_hours=24, n_events=8, exclude=(), freq="10min", return_bases=False):
    rng = np.random.default_rng(seed)
    ponds = load_all(raw_dir)
    train, test, info, bases = [], [], [], []
    for name, raw in ponds.items():
        if name in exclude:
            info.append({"pond": name, "raw_rows": len(raw), "freq": freq, "segment_hours": None, "used": False, "note": "excluded"})
            continue
        g, freq = clean(raw, freq)
        seg = longest_valid_segment(g)
        sph = 3600 / pd.Timedelta(freq).total_seconds()
        hours = len(seg) / sph
        info.append({"pond": name, "raw_rows": len(raw), "freq": freq,
                     "segment_hours": round(hours, 1), "used": hours >= min_hours})
        if hours < min_hours:
            continue
        seg["pond"] = name
        half = len(seg) // 2
        tr = seg.iloc[:half].copy()
        te = inject(seg.iloc[half:], rng, sph, n_events=n_events)
        te["pond"] = name
        tr["sph"] = sph; te["sph"] = sph
        bases.append(seg.iloc[half:].assign(sph=sph).reset_index(drop=True))
        train.append(tr); test.append(te)
    if not train:
        raise SystemExit(f"No pond has >= {min_hours}h of usable data: {info}")
    if return_bases:
        return train, test, pd.DataFrame(info), bases
    return train, test, pd.DataFrame(info)


class Detector:
    """Everything learned from clean training data. Picklable, so the API can load it without raw data."""

    def __init__(self, train):
        # diel profile per pond, learned on that pond's clean training half only
        self.profiles = {t["pond"].iloc[0]: {v: smooth(t[v]).groupby(t["time"].dt.hour).median()
                                             for v in ["do", "ph", "temp"] if v in t} for t in train}
        trf = [add_features(t, t["sph"].iloc[0], self.profiles[t["pond"].iloc[0]]) for t in train]
        self.cols = [c for c in feature_columns(trf[0]) if all(c in d for d in trf)]
        Xtr = pd.concat(trf)[self.cols].fillna(0).values
        self.mu, self.sd = Xtr.mean(0), Xtr.std(0) + 1e-9
        self.model = IsolationForest(n_estimators=200, contamination="auto", random_state=0)
        self.model.fit((Xtr - self.mu) / self.sd)
        s_tr = -self.model.score_samples((Xtr - self.mu) / self.sd)
        self.lo, self.hi = np.quantile(s_tr, 0.5), np.quantile(s_tr, 0.995)
        allr = pd.concat(trf)
        self.ref_std = {v: allr[f"{v}_rstd"].median() for v in ["do", "ph"] if f"{v}_rstd" in allr}
        # robust noise scale (MAD); real data has its own spikes
        self.ref_diff = {v: (allr[v] - allr[v].rolling(5, center=True, min_periods=3).median()).abs().median() * 1.4826
                         for v in ["do", "ph"] if v in allr}

    def score(self, t):
        """t: one pond's series (columns time, do, ph, temp, sph, pond). Returns t + scores + 4 methods' alerts."""
        sph = t["sph"].iloc[0]
        prof = self.profiles.get(t["pond"].iloc[0])
        if prof is None:  # unseen pond: fall back to the median diel profile of the training ponds
            prof = {v: pd.concat([p[v] for p in self.profiles.values() if v in p], axis=1).median(axis=1)
                    for v in ["do", "ph", "temp"]}
        t = add_features(t, sph, prof)
        X = (t[self.cols].fillna(0).values - self.mu) / self.sd
        a = np.clip((-self.model.score_samples(X) - self.lo) / (self.hi - self.lo), 0, 1)
        rel, rel_any, reasons = reliability(t, sph, self.ref_std, self.ref_diff)
        t["anomaly"] = a
        t["reliability"] = rel          # trust in DO (drives risk)
        t["reliability_any"] = rel_any  # worst sensor (drives "check sensor")
        t["reasons"] = reasons
        ph_bad = t["ph"].lt(PH_RANGE[0]) | t["ph"].gt(PH_RANGE[1]) if "ph" in t else False
        do_s = t["do_s"]  # spike-robust DO for risk assessment
        t["alert_threshold"] = debounce(t["do"].lt(DO_DANGER) | ph_bad, DEBOUNCE)
        t["alert_iforest"] = debounce(pd.Series(a > 0.6), DEBOUNCE)
        t["risk_fuzzy_only"] = fuzzy_risk.infer(do_s, np.zeros(len(t)), rel)
        t["alert_fuzzy_only"] = debounce(t["risk_fuzzy_only"] >= 60, DEBOUNCE)
        t["risk"] = fuzzy_risk.infer(do_s, a, rel)
        t["alert_hybrid"] = debounce(t["risk"] >= 60, DEBOUNCE)
        t["level"] = fuzzy_risk.level(t["risk"].values)
        t["sensor_check"] = (rel < 0.6).astype(int)  # DO untrusted -> ask to check the sensor, not "danger"
        t["other_sensor_issue"] = ((rel_any < 0.6) & (rel >= 0.6)).astype(int)  # e.g. pH probe; informational
        return t


def fit_and_score(train, test):
    det = Detector(train)
    out = pd.concat([det.score(t) for t in test], ignore_index=True)
    return out, det, det.cols


def _runs(mask):
    m = np.asarray(mask, bool)
    d = np.diff(np.r_[0, m.astype(int), 0])
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def evaluate(df, methods=("threshold", "iforest", "fuzzy_only", "hybrid"), grace_h=1.0):
    rows = []
    for m in methods:
        tot = {"method": m, "tp": 0, "fp": 0, "fn": 0, "risk_events": 0, "risk_detected": 0,
               "delays_min": [], "false_alarm_episodes": 0, "fault_events": 0, "fault_false_danger": 0,
               "hours": 0.0}
        for pond, g in df.groupby("pond", sort=False):
            g = g.reset_index(drop=True)
            sph = g["sph"].iloc[0]; grace = int(grace_h * sph)
            al = g[f"alert_{m}"].values.astype(bool)
            y = g["is_risk"].values.astype(bool)
            tot["hours"] += len(g) / sph
            tot["tp"] += int((al & y).sum()); tot["fp"] += int((al & ~y).sum()); tot["fn"] += int((~al & y).sum())
            risk_zone = np.zeros(len(g), bool)
            for eid, ev in g[g.event_id >= 0].groupby("event_id"):
                s, e = ev.index.min(), ev.index.max() + 1
                if ev["is_risk"].iloc[0]:
                    tot["risk_events"] += 1
                    risk_zone[s:min(len(g), e + grace)] = True
                    hit = np.where(al[s:min(len(g), e + grace)])[0]
                    if len(hit):
                        tot["risk_detected"] += 1
                        tot["delays_min"].append(hit[0] / sph * 60)
                else:
                    tot["fault_events"] += 1
                    if al[s:e].any():
                        tot["fault_false_danger"] += 1
            for s, e in _runs(al):
                if not risk_zone[s:e].any():
                    tot["false_alarm_episodes"] += 1
        p = tot["tp"] / max(1, tot["tp"] + tot["fp"]); r = tot["tp"] / max(1, tot["tp"] + tot["fn"])
        rows.append({
            "method": m,
            "precision": round(p, 3), "recall": round(r, 3),
            "f1": round(2 * p * r / max(1e-9, p + r), 3),
            "event_recall": f'{tot["risk_detected"]}/{tot["risk_events"]}',
            "median_delay_min": round(float(np.median(tot["delays_min"])), 1) if tot["delays_min"] else None,
            "false_alarms_per_day": round(tot["false_alarm_episodes"] / max(tot["hours"], 1e-9) * 24, 2),
            "sensor_faults_raised_as_danger": f'{tot["fault_false_danger"]}/{tot["fault_events"]}',
        })
    return pd.DataFrame(rows)


def sensor_check_rate(df):
    n = hit = 0
    for _, g in df[(df.event_id >= 0) & (df.is_fault == 1)].groupby(["pond", "event_id"]):
        n += 1; hit += int((g["sensor_check"] | g["other_sensor_issue"]).any())
    return hit, n
