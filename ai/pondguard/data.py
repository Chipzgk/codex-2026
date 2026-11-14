"""Load + clean raw pond sensor CSVs (Kaggle aquaponics IoT dataset, robust to column names)."""
import re
from pathlib import Path
import numpy as np
import pandas as pd

VARS = ["do", "ph", "temp", "turbidity", "nh3", "no3", "fish_len"]
PATTERNS = {
    "time": r"created|timestamp|date|time",
    "do": r"dissolved|oxygen|\bdo\b",
    "ph": r"^\s*ph\b|\bph\b",
    "temp": r"temp",
    "turbidity": r"turbid",
    "nh3": r"ammon",
    "no3": r"nitrate",
    "fish_len": r"length",
}
# Physically plausible ranges; values outside are sensor garbage -> NaN
VALID = {"do": (0, 20), "ph": (0, 14), "temp": (0, 45), "turbidity": (0, 3000),
         "nh3": (0, 100), "no3": (0, 5000)}


def map_columns(cols):
    out = {}
    for key, pat in PATTERNS.items():
        for c in cols:
            if c in out.values():
                continue
            if re.search(pat, str(c), re.I):
                out[key] = c
                break
    return out


def load_pond(path):
    df = pd.read_csv(path, low_memory=False)
    m = map_columns(df.columns)
    if "time" not in m or "do" not in m:
        raise ValueError(f"{path}: cannot find time/DO columns in {list(df.columns)}")
    raw_t = df[m["time"]].astype(str).str.replace(r"\s+(CET|UTC|GMT|WAT)$", "", regex=True)
    out = pd.DataFrame({"time": pd.to_datetime(raw_t, errors="coerce", utc=True, format="mixed")})
    for v in VARS:
        if v in m:
            out[v] = pd.to_numeric(df[m[v]], errors="coerce")
    out = out.dropna(subset=["time"]).sort_values("time")
    out = out.drop_duplicates("time")
    out["time"] = out["time"].dt.tz_convert(None)
    return out, m


def clean(df, freq=None):
    """Resample to a fixed grid (mean); invalid readings -> NaN (kept, not filled)."""
    df = df.copy()
    for v, (lo, hi) in VALID.items():
        if v in df:
            df.loc[(df[v] < lo) | (df[v] > hi), v] = np.nan
    if freq is None:
        dt = df["time"].diff().dt.total_seconds().median()
        freq = f"{max(60, int(round(dt / 60.0)) * 60)}s"
    g = df.set_index("time").resample(freq).mean()
    return g.reset_index(), freq


def longest_valid_segment(df, var="do", max_gap=3):
    """Longest stretch where `var` has no gap longer than max_gap steps."""
    ok = df[var].notna().values
    best, cur_start, gap, best_rng = 0, None, 0, (0, 0)
    for i, v in enumerate(ok):
        if v:
            if cur_start is None:
                cur_start = i
            gap = 0
            if i - cur_start + 1 > best:
                best, best_rng = i - cur_start + 1, (cur_start, i + 1)
        else:
            gap += 1
            if gap > max_gap:
                cur_start, gap = None, 0
    seg = df.iloc[best_rng[0]:best_rng[1]].copy()
    num = [c for c in VARS if c in seg]
    seg[num] = seg[num].interpolate(limit=max_gap, limit_direction="both")
    return seg.reset_index(drop=True)


def load_all(raw_dir):
    ponds = {}
    for f in sorted(Path(raw_dir).rglob("*.csv")):
        try:
            df, m = load_pond(f)
        except ValueError as e:
            print("skip:", e)
            continue
        ponds[f.stem] = df
    return ponds


def valid_segments(df, var="do", max_gap=3, min_len=1):
    """All stretches where `var` has no gap longer than max_gap steps (gaps <= max_gap interpolated)."""
    ok = df[var].notna().values
    segs, start, gap = [], None, 0
    for i, v in enumerate(ok):
        if v:
            start = i if start is None else start
            gap = 0
        else:
            gap += 1
            if gap > max_gap and start is not None:
                segs.append((start, i - gap + 1)); start, gap = None, 0
    if start is not None:
        segs.append((start, len(ok)))
    out = []
    for a, b in segs:
        if b - a >= min_len:
            seg = df.iloc[a:b].copy()
            num = [c for c in VARS if c in seg]
            seg[num] = seg[num].interpolate(limit=max_gap, limit_direction="both")
            out.append(seg.reset_index(drop=True))
    return out
