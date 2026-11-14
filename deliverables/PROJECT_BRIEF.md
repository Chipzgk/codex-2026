# Project Brief — PondGuard

> Status: v1 · 14/11/2026 · Sự kiện "AI Trong Lòng Bàn Tay", Hà Nội. Nguồn: bản đặc tả "PondGuard — Đặc tả Prototype
> Android" và source `0e71707`. Yêu cầu chức năng: [PRD.md §3](PRD.md).

## 1. Bối cảnh và vấn đề

- **Người dùng đầu tiên:** hộ nuôi cá ao quy mô nhỏ, tự quản lý ao, dùng điện thoại Android.
- **Đã xác nhận với hộ nuôi U01** ([USER_RESEARCH.md](USER_RESEARCH.md)): cá chết do thiếu oxy; thường cá chết rồi mới biết; tối phải ra ao xem cá, tốn thời gian. Hộ này chưa dùng thiết bị đo nào.
- **Giả thuyết cho hộ đã có cảm biến** (chưa phỏng vấn):
  - Khó biết biến động nào là bình thường theo nhịp ngày đêm, biến động nào là dấu hiệu nguy hiểm.
  - Ngưỡng cố định chỉ báo khi DO đã quá thấp.
  - Cảm biến báo sai (kẹt, nhiễu) làm người nuôi mất niềm tin vào cảnh báo.
- **Tình huống điển hình:** buổi tối, nhiệt độ nước cao, DO giảm dần. Người nuôi cần quyết định có bật quạt nước/sục khí sớm không.

**Job-to-be-done:** "Khi nước ao thay đổi, tôi muốn biết sớm đó là nguy hiểm thật hay chỉ là máy đo sai, và cần làm gì ngay, để không mất cá và không phải thức canh cả đêm."

## 2. Giải pháp

Ứng dụng di động cho người nuôi biết ao đang an toàn hay có nguy cơ, và vì sao.

| Thành phần | Việc chính |
|---|---|
| App di động ([`mobile-expo/`](../mobile-expo/)) | Thẻ rủi ro có màu, lý do, hành động gợi ý, biểu đồ DO, thông báo, so sánh với ngưỡng cố định |
| Backend ([`api/`](../api/)) | Chèn sự cố vào dữ liệu cảm biến thật, chấm điểm, phát lại theo thời gian thực qua WebSocket |
| AI ([`ai/`](../ai/)) | Lớp độ tin cậy dữ liệu → Isolation Forest → Fuzzy Mamdani → mức rủi ro và lý do |

**Điểm khác biệt cần chứng minh:** tách lỗi cảm biến khỏi rủi ro thật, nên không báo động giả mỗi khi số liệu nhảy; giải thích bằng tiếng Việt kèm hành động cụ thể.

## 3. Ràng buộc cốt lõi

| Ràng buộc | Nội dung |
|---|---|
| Không bịa số đo | Số đo luôn từ dữ liệu cảm biến thật cộng bộ chèn sự cố có nhãn. LLM chỉ viết kịch bản, không sinh số |
| Không báo nguy hiểm khi dữ liệu không tin được | DO không đáng tin → "Kiểm tra cảm biến", không nâng lên "Nguy hiểm" |
| Ngưỡng cố định trước khi đánh giá | DO < 3 mg/L nguy hiểm, 3–5 stress, > 5 tốt, lấy từ tài liệu; không chỉnh theo kết quả |
| Đánh giá trên seed giữ riêng | Điều chỉnh trên seed 1–3, báo cáo trên seed 11–15 |
| Không phụ thuộc phần cứng IoT | Demo bằng dữ liệu cảm biến thật phát lại và kịch bản mô phỏng |
| Nói đúng giới hạn | Isolation Forest chưa đóng góp trên bộ dữ liệu này; dữ liệu là ao aquaponics Nigeria, không phải ao rô phi Việt Nam |

## 4. Phạm vi một ngày

- **Trong phạm vi:** 1 ao demo trở lên, kịch bản mô phỏng, kết quả rủi ro có giải thích, biểu đồ, đóng/mở lại app, một lượt AI mới trên máy thật.
- **Bổ sung nếu kịp:** phản hồi "Cảnh báo đúng/sai", thông báo đẩy, ngưỡng theo loài (tôm), dự báo DO lúc rạng sáng.
- **Ngoài phạm vi:** phần cứng cảm biến/ESP32, điều khiển quạt nước tự động, tài khoản và thanh toán, nhiều loài cùng lúc, deep learning, tích hợp thời tiết.

## Tài liệu liên quan

- [PRD.md](PRD.md) — tính năng, trạng thái, chỉ số
- [AI_MODEL_DESIGN.md](AI_MODEL_DESIGN.md) — mô hình
- [`docs/architecture_diagram.md`](../docs/architecture_diagram.md) — kiến trúc
- [MARKET_ANALYSIS.md](MARKET_ANALYSIS.md) — tiếp cận và mở rộng thị trường
