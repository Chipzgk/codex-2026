"""Inject labelled events into a clean real-sensor base series.

Risk events (true environmental danger):   do_drop (sudden aerator failure), do_decline (gradual)
Sensor-fault events (NOT danger):          stuck (frozen DO reading), spike (isolated DO/pH outliers)
"""
import numpy as np
import pandas as pd

RISK_TYPES = ["do_drop", "do_decline"]
FAULT_TYPES = ["stuck", "spike"]
SIM_TYPES = RISK_TYPES + FAULT_TYPES + ["sensor_drift"]


def inject(df, rng, steps_per_hour, n_events=8, margin=None):
    df = df.copy().reset_index(drop=True)
    n = len(df)
    df["event_id"] = -1
    df["event_type"] = ""
    df["is_risk"] = 0
    df["is_fault"] = 0
    sph = steps_per_hour
    margin = margin or int(3 * sph)
    types = (RISK_TYPES + FAULT_TYPES) * (n_events // 4 + 1)
    rng.shuffle(types)
    types = types[:n_events]
    taken = np.zeros(n, bool)
    eid = 0
    for t in types:
        dur = {"do_drop": rng.integers(int(2 * sph), int(4 * sph) + 1),
               "do_decline": rng.integers(int(5 * sph), int(8 * sph) + 1),
               "stuck": rng.integers(int(2 * sph), int(5 * sph) + 1),
               "spike": rng.integers(max(3, int(0.5 * sph)), max(4, int(1 * sph)) + 1)}[t]
        dur = int(dur)
        for _ in range(200):
            s = int(rng.integers(margin, max(margin + 1, n - dur - margin)))
            if not taken[max(0, s - margin): s + dur + margin].any():
                break
        else:
            continue
        e = s + dur
        sl = df.index[s:e]
        do0 = df.loc[s, "do"]
        if t == "do_drop":
            target = rng.uniform(1.0, 2.5)
            ramp = max(2, int(0.25 * sph))
            k = np.minimum(np.arange(dur) / ramp, 1.0)
            df.loc[sl, "do"] = df.loc[sl, "do"].values * (1 - k) + (target + rng.normal(0, .1, dur)) * k
        elif t == "do_decline":
            target = rng.uniform(1.5, 2.8)
            k = np.linspace(0, 1, dur)
            df.loc[sl, "do"] = df.loc[sl, "do"].values * (1 - k) + target * k
        elif t == "stuck":
            df.loc[sl, "do"] = do0
        elif t == "spike":
            var = "ph" if ("ph" in df and rng.random() < .4) else "do"
            idx = np.arange(s, e)
            hit = rng.choice(idx, size=max(2, dur // 3), replace=False)
            if var == "do":
                df.loc[hit, "do"] = rng.choice([0.2, 0.4, 14.0, 16.0], size=len(hit))
            else:
                df.loc[hit, "ph"] = rng.choice([2.5, 3.0, 12.0, 12.5], size=len(hit))
        taken[s:e] = True
        df.loc[sl, "event_id"] = eid
        df.loc[sl, "event_type"] = t
        df.loc[sl, "is_risk" if t in RISK_TYPES else "is_fault"] = 1
        eid += 1
    return df


def inject_one(df, kind, start, steps_per_hour, intensity=1.0, seed=0):
    """Insert ONE event at index `start` (simulator). intensity 0.5 (mild) .. 1.5 (severe).
    sensor_drift = calibration drift: reading slides down slowly. It looks like a real gradual decline;
    PondGuard cannot reliably tell them apart (documented limitation)."""
    rng = np.random.default_rng(seed)
    df = df.copy().reset_index(drop=True)
    for c, v in [("event_id", -1), ("event_type", ""), ("is_risk", 0), ("is_fault", 0)]:
        if c not in df:  # keep earlier events when several are injected one after another
            df[c] = v
    eid = int(df["event_id"].max()) + 1
    sph = steps_per_hour
    dur = int({"do_drop": 3 * sph, "do_decline": 6 * sph, "stuck": 4 * sph,
               "spike": max(4, sph), "sensor_drift": 10 * sph}[kind])
    start = int(np.clip(start, 0, max(0, len(df) - dur - 1)))
    e = min(len(df), start + dur)
    ix = df.index[start:e]; n = len(ix)
    do = df.loc[ix, "do"].values
    if kind == "do_drop":
        target = max(0.5, 3.2 - 1.6 * intensity)
        k = np.minimum(np.arange(n) / max(2, int(0.25 * sph)), 1.0)
        df.loc[ix, "do"] = do * (1 - k) + (target + rng.normal(0, .1, n)) * k
    elif kind == "do_decline":
        target = max(0.8, 3.6 - 1.4 * intensity)
        k = np.linspace(0, 1, n)
        df.loc[ix, "do"] = do * (1 - k) + target * k
    elif kind == "stuck":
        df.loc[ix, "do"] = do[0]
    elif kind == "spike":
        hit = rng.choice(np.arange(n), size=max(2, n // 3), replace=False)
        df.loc[ix[hit], "do"] = rng.choice([0.2, 0.4, 14.0, 16.0], size=len(hit))
    elif kind == "sensor_drift":
        df.loc[ix, "do"] = do - np.linspace(0, 3.0 * intensity, n)
    else:
        raise ValueError(f"unknown event {kind}; choose from {SIM_TYPES}")
    df.loc[ix, "event_id"] = eid
    df.loc[ix, "event_type"] = kind
    df.loc[ix, "is_risk" if kind in RISK_TYPES else "is_fault"] = 1
    return df
