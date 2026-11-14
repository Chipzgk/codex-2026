"""Concept drift: fish grow (~7 cm in June -> 20-28 cm in August), oxygen demand rises, DO baseline falls.
Compare a detector trained on EARLY data (June) vs one RETRAINED on the most recent clean window,
both tested on the LATEST segment (with labelled events injected, several seeds).

python ai/scripts/drift_experiment.py --raw ai/data/raw --out ai/reports
"""
import argparse, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from pondguard.data import load_pond, clean, valid_segments
from pondguard.inject import inject
from pondguard.pipeline import Detector, evaluate

ap = argparse.ArgumentParser()
ap.add_argument("--raw", default="data/raw"); ap.add_argument("--out", default="reports")
ap.add_argument("--ponds", nargs="+", default=["IoTpond1", "IoTPond3", "IoTPond4", "IoTPond6"])
ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
a = ap.parse_args()
SPH = 6.0

setups, info = {"early": ([], []), "recent": ([], [])}, []
for name in a.ponds:
    d, _ = load_pond(Path(a.raw) / f"{name}.csv")
    d = d[d.time >= "2021-06-01"]  # a few rows carry broken early dates
    g, _ = clean(d, "10min")
    segs = [s.assign(pond=name, sph=SPH) for s in valid_segments(g, min_len=int(SPH * 48))]
    if len(segs) < 3:
        continue
    test, early, recent = segs[-1], segs[0], segs[-2]
    info.append({"pond": name,
                 "early": f"{early.time.iloc[0]:%d/%m}", "early_fish_cm": round(early.fish_len.mean(), 1), "early_do": round(early["do"].mean(), 2),
                 "recent": f"{recent.time.iloc[0]:%d/%m}", "recent_fish_cm": round(recent.fish_len.mean(), 1), "recent_do": round(recent["do"].mean(), 2),
                 "test": f"{test.time.iloc[0]:%d/%m}", "test_fish_cm": round(test.fish_len.mean(), 1), "test_do": round(test["do"].mean(), 2)})
    setups["early"][0].append(early); setups["recent"][0].append(recent)
    setups["early"][1].append(test); setups["recent"][1].append(test)

info = pd.DataFrame(info)
print(info.to_string(index=False))
rows = []
for label, (train, tests) in setups.items():
    det = Detector(train)
    for seed in a.seeds:
        rng = np.random.default_rng(seed)
        scored = []
        for t in tests:
            clean_score = det.score(t)  # no injected events: how jumpy is the ML on normal late data?
            te = inject(t, rng, SPH, n_events=6); te["pond"] = t["pond"].iloc[0]
            scored.append(det.score(te))
            rows.append({"train": label, "seed": seed, "pond": t["pond"].iloc[0],
                         "iforest_alarm_rate_clean": float(clean_score["alert_iforest"].mean()),
                         "mean_anomaly_clean": float(clean_score["anomaly"].mean())})
        m = evaluate(pd.concat(scored, ignore_index=True))
        for _, r in m.iterrows():
            rows.append({"train": label, "seed": seed, "method": r["method"], "f1": r["f1"],
                         "precision": r["precision"], "recall": r["recall"],
                         "false_alarms_per_day": r["false_alarms_per_day"]})
r = pd.DataFrame(rows)
clean_tbl = r.dropna(subset=["iforest_alarm_rate_clean"]).groupby("train")[["iforest_alarm_rate_clean", "mean_anomaly_clean"]].mean().round(3)
met = r.dropna(subset=["method"]).groupby(["method", "train"])[["precision", "recall", "f1", "false_alarms_per_day"]].mean().round(3)
print(clean_tbl.to_string()); print(met.to_string())
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
met.reset_index().to_csv(out / "drift.csv", index=False)
(out / "drift.md").write_text(
    "# Concept drift: train sớm vs train lại gần đây (test trên giai đoạn muộn nhất)\n\n"
    + info.to_markdown(index=False) + "\n\n## Isolation Forest trên dữ liệu muộn chưa chèn sự cố\n\n"
    + clean_tbl.to_markdown() + "\n\n## Chỉ số khi có sự cố chèn (trung bình seed " + str(a.seeds) + ")\n\n"
    + met.to_markdown() + "\n", encoding="utf-8")
print("saved", out / "drift.md")
