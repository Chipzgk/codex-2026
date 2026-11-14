# Kịch bản demo 5 phút — PondGuard

> Status: v1 · 14/11/2026 · Dựa trên bản đặc tả §16, chỉnh theo tính năng tại `0e71707`. App chạy với `OFFLINE = false`.

| Thời lượng | Thao tác | Bằng chứng giám khảo nhìn thấy | Ghi chú |
|---|---|---|---|
| 00:00–00:35 | Nêu vấn đề của người nuôi cá ao | — | Job-to-be-done ở [PROJECT_BRIEF.md](PROJECT_BRIEF.md) |
| 00:35–01:00 | Force-stop app, mở lại từ icon trên điện thoại | App thật, nhãn **Live** | |
| 01:00–01:50 | Chọn ao → gõ "3 giờ sáng mất điện, máy sục khí ngừng" → Chạy real-time | Kịch bản do LLM viết; thẻ chuyển Nguy hiểm, lý do nêu DO, hành động "Bật máy sục khí ngay"; thông báo bật lên | |
| 01:50–02:40 | Chọn "Cảm biến kẹt" (hoặc ao 2 · cảm biến lỗi thật) → Chạy | "KIỂM TRA CẢM BIẾN", **không** báo nguy hiểm; cột Ngưỡng cố định vẫn "BÁO ĐỘNG" | Điểm khác biệt chính |
| 02:40–03:20 | Mời giám khảo tự gõ một tình huống bất kỳ → Chạy; xem biểu đồ | AI nhận đầu vào mới, không phải kịch bản cứng | Số đo là dữ liệu cảm biến thật + sự cố chèn |
| 03:20–04:10 | Cuộn xuống bảng đánh giá; nêu giới hạn | Báo giả 1,66 so với 2,43/ngày; lỗi cảm biến → nguy hiểm 15% so với 26% | Nói luôn: chậm hơn khoảng 10 phút; Isolation Forest chưa đóng góp trên bộ dữ liệu này |
| 04:10–05:00 | Kênh tìm người nuôi đầu tiên, mở rộng loài, dùng Codex | Kế hoạch pilot 3–5 ao | [MARKET_ANALYSIS.md](MARKET_ANALYSIS.md) |

## Câu mở đầu

"Người nuôi cá ao nhìn từng con số đo và khó biết lúc nào là nguy hiểm thật, lúc nào chỉ là máy đo lỗi. Với PondGuard, họ biết ngay khi nào ao nguy hiểm thật và không bị báo động giả khi máy đo lỗi. Bây giờ chúng tôi sẽ đóng hẳn, mở lại app trên điện thoại này và chạy một lượt AI mới."

## Câu hỏi có thể gặp

| Câu hỏi | Trả lời dựa trên số liệu |
|---|---|
| AI có thật không, hay chỉ là kịch bản? | Số đo là dữ liệu cảm biến thật từ Kaggle; sự cố được chèn có kiểm soát; mô hình chấm điểm ngay trên server. LLM chỉ viết loại sự cố và giờ, không viết số |
| ML đóng góp gì? | Trên bộ dữ liệu này, Isolation Forest chưa cải thiện so với Fuzzy. Giá trị đến từ lớp kiểm tra độ tin cậy dữ liệu cộng Fuzzy. Đây là kết quả trung thực trên seed giữ riêng |
| Sao không dùng ngưỡng cố định cho đơn giản? | Ngưỡng cố định bắt được sự cố như nhau, nhưng báo giả nhiều hơn khoảng 32% và báo nhầm 26% lỗi cảm biến thành nguy hiểm |
| Dữ liệu có phải ao Việt Nam không? | Không. Ao aquaponics Nigeria. Ngưỡng từ tài liệu cá nước ấm, cần người nuôi và chuyên gia Việt Nam xác nhận |
| Trôi hiệu chuẩn thì sao? | Không phân biệt được với DO giảm thật; cần cảm biến thứ hai hoặc đo tay |
