# Thiết kế API — PondGuard

> Status: v1 · 14/11/2026 · Đối chiếu [`api/main.py`](../api/main.py) tại `0e71707` (FastAPI, `version="0.3"`).

Chạy: `uvicorn api.main:app --host 0.0.0.0 --port 8000` ở gốc repo, sau khi đã có `ai/data/processed/simulator.joblib`.
CORS mở cho mọi nguồn.

## 1. Endpoint

| Method | Path | Request | Response | Lỗi |
|---|---|---|---|---|
| GET | `/health` | — | `{"ok": bool}`: `true` khi có file mô hình | Không nạp thử mô hình |
| GET | `/ponds` | — | `[{pond, points, hours, showcase}]`; `showcase=true` là ao có lỗi cảm biến thật, không dùng để train | 503 khi chưa có mô hình |
| GET | `/events` | — | `[{id, label, kind}]`, `kind` ∈ `risk` / `sensor` | — |
| POST | `/simulate` | `SimRequest` (mục 2) | Cả chuỗi `{pond, start_index, step_minutes, points[], event, summary}` | 404 ao không có; 422 sai schema; 503 chưa có mô hình |
| POST | `/scenario` | `{prompt}` (≤ 500 ký tự) | `{scenario, source}`; `source` = `llm` hoặc `fallback:<lý do>` | Không gọi mô hình |
| WS | `/ws/run` | Tin đầu tiên: `{pond, prompt? \| event?, intensity?, start_hour?, hours?, tick_ms?}` | Chuỗi tin, mục 3 | Gửi `{"type":"error","detail"}` rồi đóng |
| GET | `/metrics` | — | Bảng so sánh 4 phương pháp; ưu tiên `heldout.csv` (trung bình seed giữ riêng) | `[]` khi chưa có file |
| GET | `/drift` | — | Kết quả thí nghiệm concept drift | `[]` khi chưa có file |

## 2. Schema

### `SimRequest`

| Trường | Kiểu | Mặc định | Ràng buộc |
|---|---|---|---|
| `pond` | string | — | Tên ao trong `/ponds` |
| `event` | `do_drop` / `do_decline` / `stuck` / `spike` / `sensor_drift` / null | null | null = ngày bình thường |
| `intensity` | float | 1,0 | 0,5–1,5 |
| `start_hour` | float | 12 | ≥ 1, giờ tính từ đầu chuỗi |
| `hours` | float | 24 | 6–72 |
| `seed` | int | 0 | — |

### `Point` (mỗi điểm 10 phút)

| Trường | Ý nghĩa |
|---|---|
| `time` | ISO 8601 |
| `do`, `do_smooth`, `ph`, `temp` | Số đo gốc và DO đã lọc spike; `null` nếu thiếu |
| `anomaly` | Điểm Isolation Forest 0–1 |
| `reliability` | Độ tin cậy DO 0–1 |
| `risk`, `level` | 0–100; `SAFE` / `WATCH` / `DANGER` |
| `sensor_check` | DO không đáng tin → hiển thị "Kiểm tra cảm biến", **ưu tiên hơn `level`** |
| `other_sensor_issue` | Cảm biến khác (pH) có vấn đề, DO vẫn tốt |
| `threshold_alert` | Kết quả của phương pháp ngưỡng cố định (DO < 3 hoặc pH ngoài 6,5–9), để so sánh |
| `event` | Nhãn thật của sự cố đã chèn; **chỉ để chú thích khi trình diễn** |
| `reasons[]`, `action` | Tối đa 3 lý do tiếng Việt, 1 hành động |
| `flags` | `{watch, danger, sensor_check}`: trạng thái hiện tại để tô màu |
| `alert` | `{kind, title, body, severity}` hoặc `null`; khác `null` chỉ khi nên bắn thông báo ([AI_MODEL_DESIGN.md §4](AI_MODEL_DESIGN.md)) |

### `Scenario`

```json
{"title": "Mất điện, máy sục khí ngừng",
 "narrative": "Máy sục khí ngừng chạy, oxy hòa tan sụt nhanh trong vài chục phút.",
 "events": [{"type": "do_drop", "start_hour": 8, "intensity": 1.2}]}
```

Server kiểm lại kết quả LLM: tối đa 3 sự kiện, đúng loại, `start_hour` 2–20, `intensity` 0,5–1,5, các sự kiện cách nhau ≥ 3 giờ.

## 3. Tin nhắn WebSocket `/ws/run`

| `type` | Thứ tự | Nội dung |
|---|---|---|
| `status` | khi có `prompt` | "LLM đang viết kịch bản…" |
| `scenario` | 1 lần | `scenario`, `source`, `pond`, `start_index`, `step_minutes`, `total` |
| `history` | 1 lần | Các điểm trước sự cố (tối đa 18 điểm trước `start_index`) để vẽ biểu đồ ngay |
| `point` | nhiều lần | `{i, point}`, cách nhau `tick_ms` (50–5000 ms, mặc định 500) |
| `end` | 1 lần | `summary`: chỉ số điểm đầu tiên ngưỡng cố định báo, PondGuard báo nguy hiểm, PondGuard báo kiểm tra cảm biến |
| `error` | khi lỗi | `detail` |

Mỗi lượt WebSocket chấm lại toàn bộ chuỗi rồi phát lại từng điểm. Đây là **phát lại dữ liệu đã chấm**, không phải dữ liệu cảm biến đổ về theo thời gian thực.
