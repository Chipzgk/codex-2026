"""python scripts/run_pipeline.py --raw data/raw --out reports
Produces: reports/metrics.csv, reports/metrics.md, reports/data_summary.csv,
          data/processed/scored.csv (used by the API/app), reports/figures/*.png
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import joblib
from pondguard.pipeline import prepare, fit_and_score, evaluate, sensor_check_rate

ap = argparse.ArgumentParser()
ap.add_argument("--raw", default="data/raw")
ap.add_argument("--out", default="reports")
ap.add_argument("--processed", default="data/processed")
ap.add_argument("--seed", type=int, default=42)
ap.add_argument("--min-hours", type=float, default=24)
ap.add_argument("--events", type=int, default=8)
ap.add_argument("--exclude", nargs="*", default=[], help="ponds left out of the base (e.g. a pond whose DO sensor is stuck)")
ap.add_argument("--freq", default="10min")
ap.add_argument("--showcase", nargs="*", default=["IoTPond2"], help="ponds kept out of training and shown as-is in the demo (real sensor problems)")
a = ap.parse_args()
out, proc = Path(a.out), Path(a.processed)
(out / "figures").mkdir(parents=True, exist_ok=True); proc.mkdir(parents=True, exist_ok=True)

train, test, info, bases = prepare(a.raw, seed=a.seed, min_hours=a.min_hours, n_events=a.events, exclude=a.exclude, freq=a.freq, return_bases=True)
print(info.to_string(index=False))
info.to_csv(out / "data_summary.csv", index=False)
df, det, cols = fit_and_score(train, test)
from pondguard.data import load_pond, clean, longest_valid_segment
for name in a.showcase:
    f = next(Path(a.raw).glob(f"{name}.csv"), None)
    if f is None:
        continue
    g, fr = clean(load_pond(f)[0], a.freq)
    seg = longest_valid_segment(g).assign(pond=name, sph=3600 / pd.Timedelta(fr).total_seconds())
    seg = seg.iloc[:int(seg["sph"].iloc[0] * 72)]  # 3 days is plenty for the demo
    sc = det.score(seg)
    print(f"showcase {name}: {len(seg)} pts, untrusted {(sc.reliability < 0.6).mean():.0%}, "
          f"threshold alarms {sc.alert_threshold.mean():.0%}, hybrid DANGER {(sc.level == 'DANGER').mean():.0%}")
    bases.append(seg.assign(showcase=True))
bases = pd.concat(bases, ignore_index=True)
joblib.dump({"detector": det, "bases": bases}, proc / "simulator.joblib")
met = evaluate(df)
hit, n = sensor_check_rate(df)
print(met.to_string(index=False))
print(f"Hybrid flagged 'check sensor' on {hit}/{n} injected sensor faults")
met.to_csv(out / "metrics.csv", index=False)
(out / "metrics.md").write_text(
    met.to_markdown(index=False) + f"\n\nHybrid 'kiểm tra cảm biến': {hit}/{n} sự cố cảm biến được chèn\n",
    encoding="utf-8")

keep = ["pond", "time", "do", "ph", "temp", "anomaly", "reliability", "risk", "level",
        "sensor_check", "other_sensor_issue", "do_s", "alert_threshold", "event_type", "is_risk", "is_fault", "reasons"]
s = df[[c for c in keep if c in df]].copy()
s["reasons"] = s["reasons"].apply(json.dumps, ensure_ascii=False)
s.to_csv(proc / "scored.csv", index=False)

for pond, g in list(df.groupby("pond"))[:3]:
    fig, ax = plt.subplots(3, 1, figsize=(13, 7), sharex=True)
    ax[0].plot(g.time, g.do, lw=.7, color="#2a6f97"); ax[0].set_ylabel("DO mg/L"); ax[0].axhline(3, ls="--", c="gray", lw=.7)
    for _, ev in g[g.event_id >= 0].groupby("event_id"):
        c = "#d62828" if ev.is_risk.iloc[0] else "#f4a261"
        for x in ax: x.axvspan(ev.time.min(), ev.time.max(), color=c, alpha=.15)
        ax[0].text(ev.time.min(), g.do.max(), ev.event_type.iloc[0], fontsize=7)
    ax[1].plot(g.time, g.anomaly, lw=.7, label="anomaly"); ax[1].plot(g.time, g.reliability, lw=.7, label="reliability"); ax[1].legend(fontsize=7)
    ax[2].plot(g.time, g.risk, lw=.7, color="#d62828"); ax[2].axhline(60, ls="--", c="gray", lw=.7); ax[2].set_ylabel("risk")
    ax[0].set_title(f"{pond} — đỏ: sự cố thật, cam: lỗi cảm biến")
    fig.tight_layout(); fig.savefig(out / "figures" / f"timeline_{pond}.png", dpi=110); plt.close(fig)
print("done ->", out)
