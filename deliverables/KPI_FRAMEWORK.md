# Khung chỉ số — PondGuard

> Status: v1 · 14/11/2026 · Số đo AI ở [`eval/results/report.md`](../eval/results/report.md).

## 1. Chất lượng AI (so với ngưỡng cố định, cùng dữ liệu có nhãn, seed giữ riêng 11–15)

| Chỉ số | Mục tiêu | Kết quả | Đạt? |
|---|---|---|---|
| Recall sự cố rủi ro thật | Không kém ngưỡng cố định | 100% sự cố (bằng nhau) | ✅ |
| F1 theo điểm | Không kém ngưỡng cố định | 0,581 so với 0,579 | ✅ (ngang) |
| Lỗi cảm biến bị báo thành nguy hiểm | Thấp hơn ngưỡng cố định | 15% so với 26% | ✅ |
| Đợt báo giả mỗi ngày | Thấp hơn ngưỡng cố định | 1,66 so với 2,43 | ✅ |
| Trễ phát hiện trong kịch bản sụt DO | Sớm hơn ngưỡng cố định | Chậm hơn khoảng 10 phút | Chưa đạt |
| Đóng góp của Isolation Forest | Hybrid tốt hơn Fuzzy-only | Bằng nhau | Chưa đạt |

## 2. Chỉ số theo dõi khi pilot

| Chỉ số | Ghi chú |
|---|---|
| Số hộ nhập số đo đều đặn | Pilot 3–5 ao |
| Tỷ lệ cảnh báo được người nuôi xác nhận đúng | — |
| Retention theo tuần | — |
| Chi phí hỗ trợ mỗi hộ | Đo khi pilot |
