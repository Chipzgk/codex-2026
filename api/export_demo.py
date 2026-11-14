"""Bundle demo runs as JSON for the app's OFFLINE mode (no network needed on stage).
python api/export_demo.py  ->  mobile/assets/demo.json
If OPEN_API_KEY/MODEL_ID are set (.env), the prompt scenarios are written by the LLM once here and frozen.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.main import simulate, SimRequest, ponds, events, metrics, drift, EVENTS, run_events, _summary  # noqa: E402
from api import llm_scenario  # noqa: E402

DEMO_POND = "IoTPond3"  # cleanest DO sensor in the dataset
PROMPTS = [
    "3 giờ sáng mất điện, máy sục khí ngừng chạy",
    "Trời âm u mấy ngày, tảo tàn, nước đục",
    "Chiều có sấm sét làm cảm biến nhiễu, đêm máy sục khí hỏng",
]
out = {"ponds": ponds(), "events": events(), "metrics": metrics(), "drift": drift(), "scenarios": {}}
for ev in [None, *EVENTS]:
    r = simulate(SimRequest(pond=DEMO_POND, event=ev, start_hour=12, hours=24))
    r["scenario"] = {"title": EVENTS[ev]["label"] if ev else "Bình thường", "narrative": "",
                     "events": [{"type": ev, "start_hour": 12, "intensity": 1.0}] if ev else []}
    r["source"] = "manual"
    out["scenarios"][f"{DEMO_POND}|{ev or 'none'}"] = r
for p in out["ponds"]:
    if p["showcase"]:
        r = simulate(SimRequest(pond=p["pond"], hours=24))
        r["scenario"], r["source"] = {"title": "Cảm biến lỗi thật", "narrative": "", "events": []}, "manual"
        out["scenarios"][f"{p['pond']}|none"] = r
for prompt in PROMPTS:
    sc, source = llm_scenario.generate(prompt)
    r = run_events(DEMO_POND, sc["events"], 24.0)
    r["summary"] = _summary(r["points"], r["start_index"] or 0)
    r["scenario"], r["source"], r["event"] = sc, source, None
    out["scenarios"][f"prompt|{prompt}"] = r
    print(f"prompt: {prompt!r} -> {source}: {sc['title']} {[e['type'] for e in sc['events']]}")
dst = Path(__file__).resolve().parents[1] / "mobile" / "assets" / "demo.json"
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"wrote {dst} ({dst.stat().st_size / 1024:.0f} KB), {len(out['scenarios'])} scenarios")
