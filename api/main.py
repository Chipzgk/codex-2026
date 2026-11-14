"""PondGuard API.
Run from repo root:  uvicorn api.main:app --host 0.0.0.0 --port 8000
Needs ai/data/processed/simulator.joblib + scored.csv  (python ai/scripts/run_pipeline.py ...)
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Literal, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai"))
from pondguard.inject import inject_one  # noqa: E402
sys.path.insert(0, str(ROOT))
from api import llm_scenario  # noqa: E402

PROC = ROOT / "ai" / "data" / "processed"
REPORTS = ROOT / "ai" / "reports"

EVENTS = {
    "do_drop": {"label": "Máy sục khí hỏng (DO sụt đột ngột)", "kind": "risk"},
    "do_decline": {"label": "DO giảm dần", "kind": "risk"},
    "stuck": {"label": "Cảm biến kẹt", "kind": "sensor"},
    "spike": {"label": "Cảm biến nhiễu", "kind": "sensor"},
    "sensor_drift": {"label": "Cảm biến trôi hiệu chuẩn (giới hạn)", "kind": "sensor"},
}

app = FastAPI(title="PondGuard API", version="0.3")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_state = {}


def state():
    if not _state:
        f = PROC / "simulator.joblib"
        if not f.exists():
            raise HTTPException(503, "Chưa có mô hình. Chạy: python ai/scripts/run_pipeline.py --raw ai/data/raw ...")
        obj = joblib.load(f)
        _state["det"] = obj["detector"]
        _state["bases"] = obj["bases"]
    return _state


def to_point(r):
    reasons = list(r["reasons"]) if isinstance(r["reasons"], list) else json.loads(r["reasons"] or "[]")
    if r["level"] != "SAFE" and r["reliability"] >= 0.6:
        if r["do_s"] < 3:
            reasons.insert(0, f"DO thấp {r['do_s']:.1f} mg/L")
        elif r["anomaly"] > 0.55:
            reasons.insert(0, "DO lệch khỏi nhịp ngày đêm bình thường của ao")
        else:
            reasons.insert(0, f"DO {r['do_s']:.1f} mg/L trong vùng gây stress (3–5)")
    sensor = bool(r["sensor_check"])
    other = bool(r.get("other_sensor_issue", 0))
    action = ("Kiểm tra / vệ sinh cảm biến trước khi xử lý ao" if sensor else
              "Bật máy sục khí ngay, kiểm tra cá nổi đầu" if r["level"] == "DANGER" else
              "Theo dõi sát trong 1 giờ tới" if r["level"] == "WATCH" else "Bình thường")
    num = lambda v, d=2: None if pd.isna(v) else round(float(v), d)
    return {"time": pd.Timestamp(r["time"]).isoformat(), "do": num(r["do"]), "do_smooth": num(r["do_s"]),
            "ph": num(r.get("ph")), "temp": num(r.get("temp")),
            "anomaly": num(r["anomaly"], 3), "reliability": num(r["reliability"]), "risk": num(r["risk"], 1),
            "level": r["level"], "sensor_check": sensor, "other_sensor_issue": other, "threshold_alert": bool(r["alert_threshold"]),
            "event": r["event_type"] if isinstance(r["event_type"], str) else "",
            "reasons": list(dict.fromkeys(reasons))[:3], "action": action}


@app.get("/health")
def health():
    return {"ok": (PROC / "simulator.joblib").exists()}


@app.get("/ponds")
def ponds():
    b = state()["bases"]
    sc = b["showcase"] if "showcase" in b else pd.Series(False, index=b.index)
    return [{"pond": p, "points": int(len(g)), "hours": round(len(g) / g["sph"].iloc[0], 1),
             "showcase": bool(sc[g.index].fillna(False).any())} for p, g in b.groupby("pond", sort=False)]


@app.get("/events")
def events():
    return [{"id": k, **v} for k, v in EVENTS.items()]


class SimRequest(BaseModel):
    pond: str
    event: Optional[Literal["do_drop", "do_decline", "stuck", "spike", "sensor_drift"]] = None
    intensity: float = Field(1.0, ge=0.5, le=1.5)
    start_hour: float = Field(12.0, ge=1, description="giờ (tính từ đầu chuỗi) bắt đầu sự cố")
    hours: float = Field(24.0, ge=6, le=72, description="độ dài chuỗi trả về")
    seed: int = 0


# Notification policy (separate from the model): a state must persist before we notify, so a noisy
# sensor hovering around a threshold does not spam the farmer.
PERSIST_STEPS = {"danger": 2, "sensor": 2, "watch": 3, "resolved": 3}   # consecutive points (10 min each)
COOLDOWN_MIN = {"danger": 60, "sensor": 240, "watch": 240, "resolved": 60}
RANK = {"safe": 0, "watch": 1, "sensor": 1, "danger": 2}


def annotate_alerts(points, step_minutes):
    """Add per-point flags + an edge-triggered `alert` for push/local notifications.

    flags: watch / danger / sensor_check (current state, every point) -> the UI colour.
    alert: only when a state has persisted PERSIST_STEPS points and was not notified within COOLDOWN_MIN.
    After a danger alert, 'watch' is muted for its cooldown (de-escalation is not news); 'resolved' fires
    once the pond is SAFE again after a danger.
    """
    last_sent, run_state, run_len, in_danger = {}, None, 0, False
    for i, p in enumerate(points):
        state = "sensor" if p["sensor_check"] else p["level"].lower()
        p["flags"] = {"watch": state == "watch", "danger": state == "danger", "sensor_check": state == "sensor"}
        p["alert"] = None
        run_len = run_len + 1 if state == run_state else 1
        run_state = state
        kind = "resolved" if (state == "safe" and in_danger) else (state if state != "safe" else None)
        if not kind or run_len != PERSIST_STEPS[kind]:
            continue
        t = i * step_minutes
        if t - last_sent.get(kind, -1e9) < COOLDOWN_MIN[kind]:
            continue
        if kind == "watch" and t - last_sent.get("danger", -1e9) < COOLDOWN_MIN["watch"]:
            continue
        reasons = [r for r in p["reasons"] if kind == "sensor" or not r.startswith("PH")]
        title = {"watch": "Ao cần theo dõi", "danger": "NGUY HIỂM: oxy trong ao",
                 "sensor": "Kiểm tra cảm biến DO", "resolved": "Ao đã ổn định trở lại"}[kind]
        body = ("Các chỉ số đã về mức an toàn." if kind == "resolved"
                else f"{' · '.join(reasons[:2]) or 'Chỉ số bất thường'}. {p['action']}.")
        p["alert"] = {"kind": kind, "title": title, "body": body,
                      "severity": {"resolved": 0, "watch": 1, "sensor": 1, "danger": 2}[kind]}
        last_sent[kind] = t
        in_danger = kind == "danger" or (in_danger and kind != "resolved")
    return points


def run_events(pond, events, hours=24.0, seed=0):
    """Inject a list of events [{type,start_hour,intensity}] into real data of `pond`, score, add alerts."""
    st = state()
    base = st["bases"][st["bases"].pond == pond].reset_index(drop=True)
    if base.empty:
        raise HTTPException(404, f"Không có ao {pond}")
    sph = float(base["sph"].iloc[0])
    df = base.iloc[: int(hours * sph)].drop(columns=["showcase"], errors="ignore")
    df = df.assign(event_id=-1, event_type="", is_risk=0, is_fault=0)
    for k, ev in enumerate(events):
        df = inject_one(df, ev["type"], int(ev["start_hour"] * sph), sph, ev.get("intensity", 1.0), seed + k)
    scored = st["det"].score(df)
    step = int(60 / sph)
    pts = annotate_alerts([to_point(r) for _, r in scored.iterrows()], step)
    start = int(events[0]["start_hour"] * sph) if events else 0
    return {"pond": pond, "start_index": start if events else None, "step_minutes": step, "points": pts}


def _summary(pts, start):
    first = lambda cond: next((i for i, p in enumerate(pts) if cond(p) and i >= start), None)
    return {"threshold_first_alarm": first(lambda p: p["threshold_alert"]),
            "pondguard_first_danger": first(lambda p: p["flags"]["danger"]),
            "pondguard_first_sensor_check": first(lambda p: p["sensor_check"])}


@app.post("/simulate")
def simulate(req: SimRequest):
    """Chèn MỘT sự cố vào dữ liệu cảm biến thật của ao, chấm điểm bằng mô hình đã train, trả cả chuỗi."""
    evs = [{"type": req.event, "start_hour": req.start_hour, "intensity": req.intensity}] if req.event else []
    r = run_events(req.pond, evs, req.hours, req.seed)
    r["event"] = req.event
    r["summary"] = _summary(r["points"], r["start_index"] or 0)
    return r


class ScenarioRequest(BaseModel):
    prompt: str = Field("", max_length=500)


@app.post("/scenario")
def scenario(req: ScenarioRequest):
    """LLM viết kịch bản (JSON) từ mô tả; không chạy mô hình. Dùng để xem trước/debug."""
    sc, source = llm_scenario.generate(req.prompt)
    return {"scenario": sc, "source": source}


@app.websocket("/ws/run")
async def ws_run(ws: WebSocket):
    """Real-time: client gửi {pond, prompt? | event?, intensity?, tick_ms?}.
    Server trả: {"type":"scenario"} -> nhiều {"type":"point", i, point(flags, alert)} -> {"type":"end", summary}."""
    await ws.accept()
    try:
        req = await ws.receive_json()
        pond = req.get("pond") or "IoTPond3"
        if req.get("prompt"):
            await ws.send_json({"type": "status", "text": "LLM đang viết kịch bản…"})
            sc, source = await asyncio.to_thread(llm_scenario.generate, req["prompt"])
        elif req.get("event"):
            sc = {"title": EVENTS[req["event"]]["label"], "narrative": "",
                  "events": [{"type": req["event"], "start_hour": float(req.get("start_hour", 12)),
                              "intensity": float(req.get("intensity", 1.0))}]}
            source = "manual"
        else:
            sc, source = {"title": "Bình thường", "narrative": "", "events": []}, "manual"
        run = await asyncio.to_thread(run_events, pond, sc["events"], float(req.get("hours", 24)))
        pts, start = run["points"], run["start_index"] or 0
        await ws.send_json({"type": "scenario", "scenario": sc, "source": source, "pond": pond,
                            "start_index": run["start_index"], "step_minutes": run["step_minutes"], "total": len(pts)})
        tick = max(0.05, min(5.0, float(req.get("tick_ms", 500)) / 1000))
        begin = max(0, start - 18)  # history before the first event is sent at once for the chart
        await ws.send_json({"type": "history", "points": pts[:begin]})
        for i in range(begin, len(pts)):
            await ws.send_json({"type": "point", "i": i, "point": pts[i]})
            await asyncio.sleep(tick)
        await ws.send_json({"type": "end", "summary": _summary(pts, start)})
    except WebSocketDisconnect:
        return
    except HTTPException as e:
        await ws.send_json({"type": "error", "detail": e.detail})
    except Exception as e:  # report instead of silently dropping the socket
        await ws.send_json({"type": "error", "detail": f"{type(e).__name__}: {e}"})
    finally:
        try:
            await ws.close()
        except Exception:
            pass


@app.get("/metrics")
def metrics():
    """Prefer the held-out multi-seed average (ai/scripts/multi_seed.py --out ai/reports/heldout.md)."""
    h = REPORTS / "heldout.csv"
    if h.exists():
        d = pd.read_csv(h)
        d["sensor_faults_raised_as_danger"] = d["faults_as_danger"].map(lambda x: f"{x:.0%}")
        d["event_recall"] = d["event_recall"].map(lambda x: f"{x:.0%}")
        d["source"] = "heldout seeds " + d["seeds"].astype(str)
        return d.replace({np.nan: None}).to_dict("records")
    f = REPORTS / "metrics.csv"
    return pd.read_csv(f).replace({np.nan: None}).to_dict("records") if f.exists() else []


@app.get("/drift")
def drift():
    f = REPORTS / "drift.csv"
    return pd.read_csv(f).replace({np.nan: None}).to_dict("records") if f.exists() else []
