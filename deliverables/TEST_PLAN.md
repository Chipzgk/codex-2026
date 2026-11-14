# Test Plan — PondGuard

> Status: v1 · 14/11/2026 · Phạm vi: source `0e71707`. Test case lấy từ bản đặc tả và [USER_STORIES.md](USER_STORIES.md).
> Kết quả chất lượng AI: [`eval/results/report.md`](../eval/results/report.md).

## 1. Chiến lược

| Tầng | Công cụ |
|---|---|
| Đánh giá AI trên dữ liệu có nhãn | `ai/scripts/run_pipeline.py`, `multi_seed.py`, `drift_experiment.py` |
| Typecheck app | `npm run typecheck` trong `mobile-expo/` |
| Kiểm tay trên điện thoại | Kịch bản mục 3 |

## 2. Ma trận yêu cầu → test

| ID | Yêu cầu | Story | Test |
|---|---|---|---|
| F01 | Cài và mở lại app | US-1.1 | T01 |
| F02 | Chọn nguồn: ngày bình thường, các kịch bản sự cố | US-2.1, US-2.2 | T02, T03, T04 |
| F04 | Sụt DO cho anomaly cao rõ so với ngày bình thường | US-1.1 | T02, T04 |
| F05 | Cảm biến kẹt và nhiễu trả `sensor_check`, không trả nguy hiểm | US-1.3 | T03 |
| F06 | Risk, mức, giải thích tiếng Việt, ≥ 1 hành động | US-1.2 | T02 |
| F08 | Lỗi mạng / backend: báo rõ, hết loading | US-3.4 | T06, T08 |

## 3. Kịch bản kiểm tay

| Test | Bước | Kết quả đạt |
|---|---|---|
| T01 · Cold start | Force-stop app → mở từ icon → chọn ao → "Máy sục khí hỏng" → Chạy | App không crash; nhãn **Live**; thẻ chuyển sang Nguy hiểm, có lý do nêu DO và hành động |
| T02 · Sụt DO | Chọn "Máy sục khí hỏng" hoặc gõ "3 giờ sáng mất điện" | Nguy hiểm, lý do nêu DO, thông báo "NGUY HIỂM: oxy trong ao" |
| T03 · Lỗi cảm biến | Chọn "Cảm biến kẹt", rồi "Cảm biến nhiễu", rồi ao 2 | "KIỂM TRA CẢM BIẾN", lý do đứng yên / thay đổi nhanh; **không** hiện Nguy hiểm trong đoạn lỗi |
| T04 · Ngày bình thường | Chọn "Bình thường" | Phần lớn An toàn hoặc Cần theo dõi |
| T06 · Mạng lỗi | Tắt Wi-Fi điện thoại khi đang chạy | Hiện lỗi, nút Chạy dùng lại được; bật mạng chạy lại được |
| T08 · Backend lỗi | Tắt uvicorn rồi bấm Chạy; đổi tên `simulator.joblib` rồi gọi `/ponds` | Lỗi rõ; `/ponds` trả 503 "Chưa có mô hình" |

## 4. Kiểm nhanh backend (không cần điện thoại)

```bash
curl http://<IP>:8000/health
curl http://<IP>:8000/ponds
curl -X POST http://<IP>:8000/simulate -H "Content-Type: application/json" \
     -d '{"pond":"IoTPond3","event":"do_drop","start_hour":8}'
curl -X POST http://<IP>:8000/simulate -H "Content-Type: application/json" \
     -d '{"pond":"IoTPond3","event":"stuck","start_hour":8}'
```

Kiểm: lượt `do_drop` có `summary.pondguard_first_danger` khác null; lượt `stuck` có `summary.pondguard_first_sensor_check` khác null và không có điểm `flags.danger` trong đoạn kẹt.
