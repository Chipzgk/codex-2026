"""Average metrics over several injection seeds. Tune on --seeds 1 2 3, report on --seeds 11 12 13 14 15."""
import argparse, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from pondguard.pipeline import prepare, fit_and_score, evaluate, sensor_check_rate

ap = argparse.ArgumentParser()
ap.add_argument("--raw", default="data/raw"); ap.add_argument("--seeds", type=int, nargs="+", default=[11, 12, 13, 14, 15])
ap.add_argument("--exclude", nargs="*", default=["IoTPond2", "IoTPond8"]); ap.add_argument("--out", default=None)
a = ap.parse_args()
rows = []
for s in a.seeds:
    tr, te, _ = prepare(a.raw, seed=s, exclude=a.exclude)
    df, _, _ = fit_and_score(tr, te)
    m = evaluate(df); h, n = sensor_check_rate(df)
    m["seed"] = s
    for c in ["event_recall", "sensor_faults_raised_as_danger"]:
        m[c + "_n"] = m[c].str.split("/").str[0].astype(int); m[c + "_d"] = m[c].str.split("/").str[1].astype(int)
    m["sensor_check_hit"] = h; m["sensor_check_n"] = n
    m["base_untrusted"] = (df[df.event_id < 0].reliability < 0.6).mean()
    rows.append(m)
r = pd.concat(rows)
g = r.groupby("method", sort=False)
out = pd.DataFrame({
    "precision": g.precision.mean().round(3), "recall": g.recall.mean().round(3), "f1": g.f1.mean().round(3),
    "event_recall": (g.event_recall_n.sum() / g.event_recall_d.sum()).round(3),
    "median_delay_min": g.median_delay_min.mean().round(1),
    "false_alarms_per_day": g.false_alarms_per_day.mean().round(2),
    "faults_as_danger": (g.sensor_faults_raised_as_danger_n.sum() / g.sensor_faults_raised_as_danger_d.sum()).round(3),
}).reset_index()
print(out.to_string(index=False))
print("sensor-check hit rate %.3f | base marked untrusted %.3f" % (r.sensor_check_hit.sum() / r.sensor_check_n.sum(), r.base_untrusted.mean()))
if a.out:
    out.assign(seeds=" ".join(map(str, a.seeds))).to_csv(Path(a.out).with_suffix(".csv"), index=False)
    Path(a.out).write_text(out.to_markdown(index=False) + f"\n\nSeeds: {a.seeds}\n", encoding="utf-8")
