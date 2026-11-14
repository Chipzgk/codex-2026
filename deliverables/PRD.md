# PRD — PondGuard

> Status: v2 · 14/11/2026 · Đối chiếu source `0e71707`. Đây là **nguồn chính** cho yêu cầu chức năng (FR), phi chức năng (NFR)
> và quy tắc nghiệp vụ (BR); tài liệu khác dùng đúng các mã này.

## 1. Mục tiêu sản phẩm

Người nuôi xem ao của mình và nhận ngay mức rủi ro hiện tại kèm lý do. PondGuard phân biệt nước ao biến động thật với cảm biến lỗi, nên không báo động giả mỗi khi số liệu nhảy.

Vấn đề đã được xác nhận với một hộ nuôi thật: cá chết vì thiếu oxy, phát hiện muộn, phải canh ao buổi tối ([USER_RESEARCH.md](USER_RESEARCH.md)).

## 2. Người dùng và stakeholder

| Vai | Nhu cầu / quan tâm | Ghi chú |
|---|---|---|
| Hộ nuôi cá ao (rô phi, rô, chép) | Biết sớm ao nguy hiểm, biết làm gì, không phải canh đêm | Người dùng chính; U01 |
| Hộ đã lắp cảm biến IoT có cảnh báo ngưỡng | Không bị báo động giả khi cảm biến lỗi | Nhóm hưởng lợi rõ nhất từ lớp kiểm tra độ tin cậy |
| Đơn vị bán cảm biến / hợp tác xã / đại lý thức ăn | Kênh phân phối, gói kèm thiết bị | [MARKET_ANALYSIS.md](MARKET_ANALYSIS.md) |
| Ban giám khảo (khi demo) | Thấy AI chạy trực tiếp trên điện thoại | — |

## 3. Yêu cầu chức năng

Ưu tiên theo MoSCoW: **M** = phải có cho demo, **S** = nên có, **C** = có thì tốt.

| Mã | Yêu cầu | Ưu tiên | Code |
|---|---|:-:|---|
| FR-01 | Chọn ao từ dữ liệu cảm biến thật, gồm ao 2 có cảm biến DO lỗi thật | M | `GET /ponds`, `App.tsx` |
| FR-02 | Chạy kịch bản sự cố chọn sẵn: Bình thường, Máy sục khí hỏng, DO giảm dần, Cảm biến kẹt, Cảm biến nhiễu, Cảm biến trôi hiệu chuẩn; cường độ Nhẹ / Vừa / Nặng | M | `GET /events`, `/ws/run` |
| FR-03 | Mô tả tình huống bằng lời, LLM dựng kịch bản; không có key thì dùng kịch bản mẫu | S | `llm_scenario.py` |
| FR-04 | Phát từng điểm đo theo thời gian thực, thẻ rủi ro cập nhật liên tục | M | `/ws/run` |
| FR-05 | Thẻ rủi ro: An toàn / Cần theo dõi / Nguy hiểm / Kiểm tra cảm biến, điểm 0–100, DO, % bất thường, % tin cậy, tối đa 3 lý do, 1 hành động | M | `to_point()`, `App.tsx` |
| FR-06 | Biểu đồ DO 12 giờ: vùng đỏ dưới 3 mg/L, tô cam đoạn không đáng tin, vạch lúc sự cố bắt đầu | S | `Chart` trong `App.tsx` |
| FR-07 | So sánh trực tiếp với ngưỡng cố định, thời điểm báo đầu tiên của mỗi bên | S | `threshold_alert`, `summary` |
| FR-08 | Thông báo trong app và thông báo cục bộ, có chống báo lặp | S | `annotate_alerts()`, `notify.ts` |
| FR-09 | Bảng số đánh giá 4 phương pháp | C | `GET /metrics` |
| FR-10 | Chế độ offline phát lại kết quả đã chấm sẵn | C | `assets/demo.json` |

## 4. Yêu cầu phi chức năng

| Mã | Yêu cầu | Cách đáp ứng trong code |
|---|---|---|
| NFR-01 | Phát hiện lỗi cảm biến chỉ dùng dữ liệu quá khứ (không nhìn trước), để chạy được theo thời gian thực | `reliability()`, lọc trung vị trượt về phía sau |
| NFR-02 | Mô hình nạp một lần khi khởi động, chạy CPU, không cần GPU hay API trả phí | `state()` trong `api/main.py`, `simulator.joblib` |
| NFR-03 | Demo không hỏng khi LLM lỗi hoặc không có key | Kịch bản mẫu theo từ khóa |
| NFR-04 | Key LLM chỉ ở server, không nằm trong app | `.env` (gitignore), `llm_scenario.py` |
| NFR-05 | Có phương án dự phòng khi mất mạng | `OFFLINE = true` |
| NFR-06 | Đánh giá tái lập được, báo cáo trên seed không dùng để điều chỉnh | `multi_seed.py`, seed 11–15 |
| NFR-07 | Giao diện cho người nuôi: chữ lớn, 4 màu cố định, mỗi cảnh báo có 1 hành động | `App.tsx` |

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nơi thực thi |
|---|---|---|
| BR-1 | `sensor_check` ưu tiên hơn mức rủi ro khi hiển thị | `App.tsx` `status()` |
| BR-2 | Dữ liệu DO không tin được (`reliability < 0,6`) không được nâng rủi ro lên nguy hiểm, trừ khi số đọc rất thấp (khi đó chỉ ở mức vừa) | Luật 6–7 trong `fuzzy_risk.py` |
| BR-3 | Cảnh báo chỉ bắn khi trạng thái kéo dài đủ lâu và hết thời gian chờ | `annotate_alerts()` |
| BR-4 | LLM không sinh số đo | `llm_scenario.py` |
| BR-5 | Nhãn sự cố thật chỉ để chú thích khi demo, không đưa vào mô hình | `to_point()`, dòng "Sự thật (chỉ để trình diễn)" |
| BR-6 | Mọi phương pháp so sánh dùng cùng bộ chống dội 2 điểm | `pipeline.py` `DEBOUNCE` |

## 6. Chỉ số và bước tiếp theo

| Chỉ số | Mục tiêu | Kết quả |
|---|---|---|
| Lỗi cảm biến bị báo thành nguy hiểm | Thấp hơn ngưỡng cố định | 15% so với 26% |
| Báo giả mỗi ngày | Thấp hơn ngưỡng cố định | 1,66 so với 2,43 |
| Bắt được sự cố rủi ro thật | Không kém ngưỡng cố định | 100% (bằng nhau) |
| Trễ phát hiện | — | 52 phút so với 42 phút của ngưỡng cố định |

Nguồn số: [`eval/results/report.md`](../eval/results/report.md).

Bước tiếp theo, rút ra từ phỏng vấn U01: hỗ trợ hộ chưa có cảm biến (nhận số đo nhập tay hoặc kết nối cảm biến DO giá rẻ), sau đó pilot 3–5 ao.
