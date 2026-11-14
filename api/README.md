# PondGuard API

```bash
# ở gốc repo, sau khi đã chạy ai/scripts/run_pipeline.py
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

| Endpoint | Mô tả |
|---|---|
| `GET /health` | Có mô hình chưa |
| `GET /ponds` | Danh sách ao (`showcase: true` = ao có lỗi cảm biến thật, không dùng để train) |
| `GET /events` | Các loại sự cố có thể giả lập |
| `POST /simulate` | `{pond, event?, intensity 0.5–1.5, start_hour, hours}` → chèn 1 sự cố vào dữ liệu thật, chấm điểm, trả cả chuỗi `points` + `summary` |
| `POST /scenario` | `{prompt}` → LLM viết kịch bản JSON (không chạy mô hình), để xem trước |
| `WS /ws/run` | **Real-time**: gửi `{pond, prompt? \| event?, intensity?, tick_ms?}` → nhận `scenario`, `history`, rồi từng `point`, cuối cùng `end` |
| `GET /metrics` | Bảng so sánh 4 phương pháp (trung bình seed giữ riêng) |
| `GET /drift` | Kết quả thí nghiệm concept drift |

Mỗi phần tử `points`: `time, do, do_smooth, ph, temp, anomaly, reliability, risk, level, sensor_check,
other_sensor_issue, threshold_alert, event, reasons[], action`. Quy tắc hiển thị: `sensor_check` ưu tiên hơn `level`.
`event` là nhãn thật, chỉ để chú thích khi trình diễn.

**Cờ và thông báo** (mỗi `point`):
- `flags: {watch, danger, sensor_check}` — trạng thái hiện tại, có ở mọi điểm → tô màu UI.
- `alert: {kind, title, body, severity} | null` — chỉ khác `null` khi **nên bắn thông báo**:
  `kind` ∈ `watch`, `danger`, `sensor`, `resolved`. Trạng thái phải kéo dài đủ lâu (watch 30', danger/sensor 20')
  và không lặp lại trong thời gian chờ (danger 1 h, watch/sensor 4 h); sau `danger` thì không báo `watch`.

**LLM**: đặt `OPEN_API_KEY` (hoặc `OPENAI_API_KEY`) và `MODEL_ID` trong `.env` ở gốc repo (tùy chọn `OPENAI_BASE_URL`).
LLM chỉ viết kịch bản JSON (loại sự cố, giờ, cường độ, câu chuyện); số liệu luôn là dữ liệu cảm biến thật + bộ chèn sự cố.
Không có key hoặc gọi lỗi → tự dùng kịch bản mẫu theo từ khóa (`source` = `fallback:...`). Kịch bản LLM chỉ dùng cho demo,
**không** dùng để tính Precision/Recall.

`python api/export_demo.py` → `mobile/assets/demo.json` cho chế độ offline (nếu có key, 3 kịch bản mẫu sẽ do LLM viết rồi đóng băng).
