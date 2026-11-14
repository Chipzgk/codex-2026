"""LLM writes a SCENARIO (JSON), never the sensor numbers.

The numbers always come from real sensor data + our controlled injector, so the physics stays plausible
and the model's prediction is not just echoing what the LLM wrote.

Env (read from repo-root .env if present):
  OPEN_API_KEY or OPENAI_API_KEY   API key (OpenAI-compatible chat completions)
  MODEL_ID                         model name
  OPENAI_BASE_URL                  optional, default https://api.openai.com/v1
Without a key, or if the call fails, a keyword-based fallback scenario is used (demo never breaks).
"""
import json
import os
import re
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
EVENT_TYPES = ["do_drop", "do_decline", "stuck", "spike", "sensor_drift"]


def _load_env():
    f = ROOT / ".env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$", line)
        if m and m.group(1) not in os.environ:
            os.environ[m.group(1)] = m.group(2).strip().strip('"').strip("'")


_load_env()

SYSTEM = """Bạn là chuyên gia nuôi cá ao. Từ mô tả tình huống của người dùng, hãy tạo MỘT kịch bản giả lập
cho hệ thống giám sát ao. Chỉ trả về JSON hợp lệ, đúng schema:
{"title": str (<= 60 ký tự, tiếng Việt),
 "narrative": str (2-3 câu tiếng Việt, giải thích diễn biến theo cơ chế sinh học/thiết bị),
 "events": [ {"type": one of ["do_drop","do_decline","stuck","spike","sensor_drift"],
              "start_hour": số từ 2 đến 20 (giờ tính từ đầu chuỗi 24 giờ),
              "intensity": số từ 0.5 đến 1.5} ]  (1 đến 3 sự kiện, không chồng lấn, cách nhau >= 3 giờ)}
Ý nghĩa: do_drop = oxy sụt nhanh (máy sục khí hỏng/mất điện); do_decline = oxy giảm dần (tảo tàn, quá tải hữu cơ, trời âm u);
stuck = cảm biến DO kẹt một giá trị; spike = cảm biến DO nhiễu nhảy vọt; sensor_drift = cảm biến trôi hiệu chuẩn dần.
Không bịa số đo. Không thêm trường khác."""


def _validate(obj):
    if not isinstance(obj, dict):
        raise ValueError("not an object")
    evs = []
    for e in obj.get("events", [])[:3]:
        t = e.get("type")
        if t not in EVENT_TYPES:
            continue
        sh = float(min(20, max(2, float(e.get("start_hour", 8)))))
        it = float(min(1.5, max(0.5, float(e.get("intensity", 1.0)))))
        if any(abs(sh - x["start_hour"]) < 3 for x in evs):
            continue
        evs.append({"type": t, "start_hour": sh, "intensity": it})
    if not evs:
        raise ValueError("no valid events")
    return {"title": str(obj.get("title", "Kịch bản"))[:60],
            "narrative": str(obj.get("narrative", ""))[:400],
            "events": sorted(evs, key=lambda x: x["start_hour"])}


FALLBACKS = [
    (r"điện|sục khí|aerat|quạt|máy", {"title": "Mất điện, máy sục khí ngừng", "narrative": "Máy sục khí ngừng chạy, oxy hòa tan sụt nhanh trong vài chục phút.", "events": [{"type": "do_drop", "start_hour": 8, "intensity": 1.2}]}),
    (r"tảo|âm u|mưa|nồng|đục|hữu cơ", {"title": "Tảo tàn sau mưa", "narrative": "Trời âm u, tảo quang hợp kém rồi tàn, vi sinh phân hủy tiêu tốn oxy khiến DO giảm dần.", "events": [{"type": "do_decline", "start_hour": 6, "intensity": 1.1}]}),
    (r"kẹt|đứng|treo|không đổi", {"title": "Cảm biến DO bị kẹt", "narrative": "Đầu dò bám bẩn, số đọc đứng yên trong nhiều giờ.", "events": [{"type": "stuck", "start_hour": 8, "intensity": 1.0}]}),
    (r"nhiễu|nhảy|sét|chập", {"title": "Cảm biến nhiễu", "narrative": "Nhiễu điện làm số đọc DO nhảy vọt rồi bật về.", "events": [{"type": "spike", "start_hour": 8, "intensity": 1.0}]}),
]
DEFAULT = {"title": "Đêm khó khăn", "narrative": "Cảm biến nhiễu lúc chiều, sau đó máy sục khí hỏng ban đêm.",
           "events": [{"type": "spike", "start_hour": 6, "intensity": 1.0}, {"type": "do_drop", "start_hour": 14, "intensity": 1.2}]}


def fallback(prompt):
    p = prompt or ""
    sensor = re.search(r"nhiễu|nhảy|sét|chập|kẹt", p, re.I)
    aerator = re.search(r"điện|sục khí|aerat|quạt", p, re.I)
    if sensor and aerator:  # combined story: sensor trouble first, real oxygen crash later
        return _validate(DEFAULT)
    for pat, sc in FALLBACKS:
        if re.search(pat, prompt or "", re.I):
            return _validate(sc)
    return _validate(DEFAULT)


def generate(prompt, timeout=20.0):
    """Returns (scenario, source) where source is 'llm' or 'fallback:<reason>'."""
    key = os.environ.get("OPEN_API_KEY") or os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("MODEL_ID")
    if not key or not model:
        return fallback(prompt), "fallback:no_key"
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    body = {"model": model, "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": prompt or "Một đêm bình thường"}]}
    try:
        r = httpx.post(f"{base}/chat/completions", timeout=timeout, headers={"Authorization": f"Bearer {key}"}, json=body)
        if r.status_code == 400:  # some models reject response_format: retry without it
            body.pop("response_format")
            r = httpx.post(f"{base}/chat/completions", timeout=timeout, headers={"Authorization": f"Bearer {key}"}, json=body)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]
        m = re.search(r"\{.*\}", text, re.S)
        return _validate(json.loads(m.group(0) if m else text)), "llm"
    except Exception as e:  # never break the demo
        return fallback(prompt), f"fallback:{type(e).__name__}"
