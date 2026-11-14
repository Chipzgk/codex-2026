"""Mamdani fuzzy risk engine (vectorised NumPy; same semantics as scikit-fuzzy control).

Inputs : do (mg/L), anomaly (0-1, from Isolation Forest), reliability (0-1)
Output : risk (0-100), centroid defuzzification.
Thresholds for warm-water fish (tilapia/catfish): DO < 3 mg/L dangerous, 3-5 stress, > 5 good.
They were fixed from literature BEFORE looking at evaluation results.
"""
import numpy as np


def trap(x, a, b, c, d):
    x = np.asarray(x, float)
    up = np.where(b > a, (x - a) / (b - a + 1e-12), (x >= a).astype(float))
    down = np.where(d > c, (d - x) / (d - c + 1e-12), (x <= d).astype(float))
    return np.clip(np.minimum(up, down), 0, 1)


DO = {"low": (-1, -1, 2.5, 3.5), "mid": (2.5, 3.5, 4.5, 5.5), "good": (4.5, 5.5, 30, 30)}
AN = {"low": (-1, -1, 0.35, 0.55), "high": (0.35, 0.55, 2, 2)}
REL = {"low": (-1, -1, 0.4, 0.6), "high": (0.4, 0.6, 2, 2)}
U = np.linspace(0, 100, 201)
RISK = {"low": trap(U, -1, -1, 20, 40), "med": trap(U, 25, 40, 55, 70), "high": trap(U, 55, 75, 101, 101)}

# (do, anomaly, reliability) -> risk   ; None = any
RULES = [
    ("low", None, "high", "high"),   # trusted low oxygen -> danger
    ("mid", "high", "high", "high"),  # oxygen falling into stress zone abnormally -> danger
    ("mid", "low", "high", "med"),   # stress zone but normal pattern (e.g. pre-dawn dip)
    ("good", "high", "high", "med"),  # abnormal pattern while DO still fine -> watch
    ("good", "low", None, "low"),
    (None, None, "low", "low"),       # untrusted data -> do NOT raise danger, ask to check sensor
    ("low", None, "low", "med"),      # ...unless the untrusted reading itself is very low
]


def infer(do, anomaly, rel):
    do, anomaly, rel = (np.atleast_1d(np.asarray(a, float)) for a in (do, anomaly, rel))
    do = np.nan_to_num(do, nan=5.0)
    mu = {"do": {k: trap(do, *p) for k, p in DO.items()},
          "an": {k: trap(anomaly, *p) for k, p in AN.items()},
          "rel": {k: trap(rel, *p) for k, p in REL.items()}}
    agg = np.zeros((len(do), len(U)))
    for d, a, r, out in RULES:
        w = np.ones(len(do))
        if d: w = np.minimum(w, mu["do"][d])
        if a: w = np.minimum(w, mu["an"][a])
        if r: w = np.minimum(w, mu["rel"][r])
        agg = np.maximum(agg, np.minimum(w[:, None], RISK[out][None, :]))
    s = agg.sum(1)
    risk = np.where(s > 0, (agg * U).sum(1) / np.maximum(s, 1e-12), 0.0)
    return risk


def level(risk):
    return np.where(risk >= 60, "DANGER", np.where(risk >= 40, "WATCH", "SAFE"))
