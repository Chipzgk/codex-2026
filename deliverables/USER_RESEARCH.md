# Phỏng vấn người dùng — PondGuard

> Status: v1 · 14/11/2026 · Ghi nhận từ cuộc phỏng vấn thật của nhóm. Chỉ ghi điều đã nghe được, không suy diễn thêm.

## 1. Kết quả phỏng vấn

| ID | Ngày | Người dùng | Cách nuôi và đo hiện tại | Sự cố đã gặp | Khó khăn |
|---|---|---|---|---|---|
| U01 | 14/11/2026 | Hộ nuôi cá rô và cá chép, 2 năm kinh nghiệm, thu hoạch 2 lần/năm | Không dùng thiết bị đo hay công nghệ nào, nuôi theo kinh nghiệm | Cá chết do thiếu oxy và do bệnh nấm | Tối phải ra ao xem cá, tốn thời gian; thường cá chết rồi mới biết |

## 2. Đối chiếu với giả thuyết

| Giả thuyết ([PROJECT_BRIEF.md](PROJECT_BRIEF.md)) | U01 | Kết luận |
|---|---|---|
| Thiếu oxy là rủi ro gây chết cá | Đã gặp cá chết do thiếu oxy | **Ủng hộ** |
| Người nuôi phát hiện muộn | "Thường cá chết rồi mới biết" | **Ủng hộ** |
| Người nuôi phải canh ao ban đêm | "Tối phải ra ao xem cá" | **Ủng hộ** — khớp với job-to-be-done "không phải thức canh cả đêm" |
| Người nuôi có máy đo / cảm biến và bị báo sai | Không có thiết bị đo nào | **Chưa áp dụng** cho hộ này |

## 3. Ảnh hưởng tới sản phẩm

- Vấn đề cốt lõi (thiếu oxy, phát hiện muộn, canh đêm) được xác nhận với một hộ nuôi thật.
- Hộ U01 chưa có số đo nào. Muốn dùng PondGuard, hộ này cần một cảm biến DO giá rẻ, hoặc app phải nhận số đo nhập tay. Điều này xác định bước phát triển tiếp theo ([PRD.md §6](PRD.md)).
- Giá trị "không báo động giả khi cảm biến lỗi" chỉ phát huy khi người nuôi đã có cảm biến. Nhóm khách hàng phù hợp nhất cho tính năng này là hộ đã lắp IoT có cảnh báo ngưỡng ([MARKET_ANALYSIS.md §2](MARKET_ANALYSIS.md)).

Cỡ mẫu: 1 hộ. Đủ để xác nhận vấn đề tồn tại, chưa đủ để kết luận về mức độ phổ biến.
