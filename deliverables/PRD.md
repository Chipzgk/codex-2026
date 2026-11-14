# PRD — PondGuard

> Status: v1 · 14/11/2026 · Đối chiếu source `0e71707`. Đây là **nguồn chính** cho tính năng và quy tắc nghiệp vụ;
> tài liệu khác link về đây.

## 1. Mục tiêu sản phẩm

Người nuôi mở app, xem ao của mình và nhận ngay mức rủi ro hiện tại kèm lý do. PondGuard phân biệt nước ao biến động thật với cảm biến lỗi, nên không báo động giả mỗi khi số liệu nhảy.

## 2. Người dùng

| Vai | Nhu cầu |
|---|---|
| Hộ nuôi cá rô phi ao đất | Biết sớm ao nguy hiểm, biết làm gì, không bị báo giả |
| Ban giám khảo (khi demo) | Thấy AI chạy trực tiếp trên điện thoại với đầu vào mới |

## 3. Tính năng

| # | Tính năng | Mô tả |
|---|---|---|
| F1 | Chọn ao | Danh sách ao từ dữ liệu cảm biến thật, kể cả ao 2 có cảm biến DO lỗi thật (`showcase`) |
| F2 | Simulation Lab | Chọn sự cố: Bình thường, Máy sục khí hỏng, DO giảm dần, Cảm biến kẹt, Cảm biến nhiễu, Cảm biến trôi hiệu chuẩn; cường độ Nhẹ / Vừa / Nặng |
| F3 | Mô tả tình huống bằng lời | Gõ tình huống tiếng Việt, LLM dựng kịch bản; không có key thì dùng kịch bản mẫu |
| F4 | Chạy real-time | Phát từng điểm đo qua WebSocket, thẻ rủi ro cập nhật liên tục |
| F5 | Thẻ rủi ro | Mức An toàn / Cần theo dõi / Nguy hiểm / Kiểm tra cảm biến (xanh / vàng / đỏ / cam), điểm 0–100, DO, % bất thường, % tin cậy, tối đa 3 lý do, 1 hành động |
| F6 | Biểu đồ DO 12 giờ | Vùng đỏ dưới 3 mg/L, tô cam đoạn dữ liệu không đáng tin, vạch đánh dấu lúc sự cố bắt đầu |
| F7 | So sánh với ngưỡng cố định | Hai cột "Ngưỡng cố định" và "PondGuard", thời điểm báo đầu tiên |
| F8 | Thông báo | Banner trong app và thông báo cục bộ (`expo-notifications`), có chống báo lặp |
| F9 | Bảng số đánh giá | F1, báo giả/ngày, lỗi cảm biến bị báo thành nguy hiểm |
| F10 | Chế độ offline | Phát lại kết quả đã chấm sẵn từ mô hình thật (`assets/demo.json`) khi không có mạng |

## 4. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nơi thực thi |
|---|---|---|
| BR-1 | `sensor_check` ưu tiên hơn mức rủi ro khi hiển thị | `App.tsx` `status()` |
| BR-2 | Dữ liệu DO không tin được (`reliability < 0,6`) không được nâng rủi ro lên nguy hiểm, trừ khi số đọc rất thấp (khi đó chỉ ở mức vừa) | Luật 6–7 trong `fuzzy_risk.py` |
| BR-3 | Cảnh báo chỉ bắn khi trạng thái kéo dài đủ lâu và hết thời gian chờ | `annotate_alerts()` |
| BR-4 | LLM không sinh số đo | `llm_scenario.py` |
| BR-5 | Nhãn sự cố thật chỉ để chú thích khi demo, không đưa vào mô hình | `to_point()`, dòng "Sự thật (chỉ để trình diễn)" trong app |
| BR-6 | Mọi phương pháp so sánh dùng cùng bộ chống dội 2 điểm để so sánh công bằng | `pipeline.py` `DEBOUNCE` |

## 5. Chỉ số

| Chỉ số | Mục tiêu | Kết quả |
|---|---|---|
| Lỗi cảm biến bị báo thành nguy hiểm | Thấp hơn ngưỡng cố định | 15% so với 26% |
| Báo giả mỗi ngày | Thấp hơn ngưỡng cố định | 1,66 so với 2,43 |
| Bắt được sự cố rủi ro thật | Không kém ngưỡng cố định | 100% (bằng nhau) |
| Trễ phát hiện | — | 52 phút so với 42 phút của ngưỡng cố định |

Nguồn số: [`eval/results/report.md`](../eval/results/report.md).
