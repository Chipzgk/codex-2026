"""Temporal features + rule-based data reliability."""
import numpy as np
import pandas as pd

FEATURE_VARS = ["do", "ph", "temp"]
MODEL_VARS = ["do"]  # pH/temp barely move in this data and only add noise to the detector


def smooth(s, k=3):
    """Trailing rolling median: removes isolated sensor spikes without looking into the future."""
    return s.rolling(k, min_periods=1).median()


def add_features(df, steps_per_hour, profile=None):
    """profile: dict var -> Series(hour -> median value) learned on training data (diel cycle)."""
    df = df.copy()
    w = max(3, int(steps_per_hour))  # ~1h window
    hour = df["time"].dt.hour + df["time"].dt.minute / 60
    df["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    df["hour_cos"] = np.cos(2 * np.pi * hour / 24)
    for v in [c for c in FEATURE_VARS if c in df]:
        s = smooth(df[v])
        df[f"{v}_s"] = s
        df[f"{v}_diff"] = s.diff().fillna(0)
        df[f"{v}_slope3h"] = (s - s.shift(3 * w)).fillna(0) / (3 * w)
        if profile is not None and v in profile:
            df[f"{v}_prof"] = s - df["time"].dt.hour.map(profile[v]).values
        df[f"{v}_rstd"] = s.rolling(w, min_periods=2).std().bfill().fillna(0)
        df[f"{v}_dev"] = (s - s.rolling(4 * w, min_periods=2).mean()).bfill().fillna(0)
        df[f"{v}_slope"] = (s - s.shift(w)).fillna(0) / w
    return df


def feature_columns(df):
    cols = ["hour_sin", "hour_cos"]
    for v in [c for c in MODEL_VARS if c in df]:
        cols += [f"{v}_s", f"{v}_diff", f"{v}_rstd", f"{v}_dev", f"{v}_slope", f"{v}_slope3h"]
        if f"{v}_prof" in df:
            cols.append(f"{v}_prof")
    return cols


MAX_RATE_PER_H = {"do": 15.0, "ph": 6.0}  # faster swings are physically implausible for a pond -> sensor issue


def reliability(df, steps_per_hour, ref_std, ref_diff):
    """Per-sensor trust in the current reading, using ONLY past and present data (causal).

    Drops on: frozen value, spikes (far from recent median or implausibly fast change), missing data.
    Returns (rel_do, rel_any, reasons): risk uses rel_do (risk is driven by DO);
    rel_any feeds the "check sensor" flag (any sensor misbehaving).
    ref_std: typical rolling std; ref_diff: robust noise scale (MAD) — both learned on training data.
    """
    w = max(4, int(steps_per_hour))
    n = len(df)
    rel = {v: np.ones(n) for v in ["do", "ph"]}
    reasons = [[] for _ in range(n)]
    for v in [c for c in ["do", "ph"] if c in df]:
        s = df[v]
        # frozen: over ~1 h the reading barely moves (<5% of this sensor's normal 1-h variability).
        # A real stuck probe still jitters a little, so exact equality is not required.
        flat = s.rolling(w, min_periods=w).std().fillna(np.inf) < 0.05 * ref_std[v]
        frozen = flat & (ref_std[v] > 1e-6)
        past_med = s.shift(1).rolling(5, min_periods=2).median()
        far = (s - past_med).abs() > 5 * max(ref_diff[v], 1e-3)
        fast = s.diff().abs() > MAX_RATE_PER_H[v] / steps_per_hour
        spike = (far | fast).fillna(False)
        spike_zone = spike | spike.shift(1, fill_value=False)
        missing = s.isna()
        for i in np.where(frozen)[0]:
            rel[v][i] = min(rel[v][i], 0.2); reasons[i].append(f"{v.upper()} đứng yên bất thường (nghi cảm biến kẹt)")
        for i in np.where(spike_zone & ~missing)[0]:
            rel[v][i] = min(rel[v][i], 0.3); reasons[i].append(f"{v.upper()} thay đổi nhanh phi vật lý (nghi nhiễu cảm biến)")
        for i in np.where(missing)[0]:
            rel[v][i] = min(rel[v][i], 0.1); reasons[i].append(f"mất dữ liệu {v.upper()}")
    rel_any = np.minimum(rel["do"], rel["ph"])
    return rel["do"], rel_any, reasons
