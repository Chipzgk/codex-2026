# User Stories — PondGuard

> Status: v1 · 14/11/2026 · Đối chiếu source `0e71707`. Mã FR/NFR theo [PRD.md](PRD.md); ma trận story → test: [TEST_PLAN.md](TEST_PLAN.md).

## Epic 1 — Biết ao đang an toàn hay nguy hiểm

### US-1.1 Xem mức rủi ro hiện tại · FR-04, FR-05

Là người nuôi, tôi muốn thấy ngay mức rủi ro của ao, để biết có cần làm gì không.

- **Given** backend có dữ liệu ao, **when** tôi chạy một lượt, **then** thẻ lớn hiện mức (An toàn / Cần theo dõi / Nguy hiểm / Kiểm tra cảm biến) bằng màu xanh / vàng / đỏ / cam và điểm rủi ro 0–100.
- **Given** một lượt đã chạy, **then** thẻ hiện thời điểm của số đo mới nhất.

### US-1.2 Hiểu vì sao và cần làm gì · FR-05

Là người nuôi, tôi muốn biết lý do và việc cần làm, để xử lý ngay mà không phải tự suy luận.

- **Given** mức khác An toàn, **then** thẻ có ít nhất 1 lý do tiếng Việt nêu DO và đúng 1 hành động.
- **Given** mức Nguy hiểm, **then** hành động là "Bật máy sục khí ngay, kiểm tra cá nổi đầu".

### US-1.3 Không bị báo động giả khi cảm biến hỏng · FR-01, FR-05

Là người nuôi, tôi muốn app nói rõ khi máy đo có vấn đề, để không hoảng loạn vì một số đo sai.

- **Given** kịch bản "Cảm biến kẹt" hoặc "Cảm biến nhiễu", **then** app hiện "KIỂM TRA CẢM BIẾN" kèm lý do (đứng yên / thay đổi nhanh phi vật lý) và **không** hiện "NGUY HIỂM" trong đoạn đó.
- **Given** ao 2 (cảm biến lỗi thật), **then** app không báo nguy hiểm.

### US-1.4 Xem diễn biến · FR-06

Là người nuôi, tôi muốn xem biểu đồ gần đây, để thấy DO đang đi xuống hay chỉ dao động.

- **Given** một lượt đang chạy, **then** biểu đồ DO 12 giờ gần nhất có vùng đỏ dưới 3 mg/L và tô cam đoạn dữ liệu không đáng tin.

## Epic 2 — Đưa dữ liệu vào cho AI

### US-2.1 Chọn kịch bản mô phỏng · FR-02

Là người trình diễn, tôi muốn chọn một sự cố có sẵn, để cho thấy AI phản ứng thế nào.

- **Given** chế độ "Chọn sự cố", **then** có Bình thường, Máy sục khí hỏng, DO giảm dần, Cảm biến kẹt, Cảm biến nhiễu, Cảm biến trôi hiệu chuẩn.
- **Given** chế độ live, **then** chọn được cường độ Nhẹ / Vừa / Nặng.

### US-2.2 Mô tả tình huống bằng lời · FR-03

Là người trình diễn, tôi muốn gõ một tình huống như "3 giờ sáng mất điện", để AI tự dựng kịch bản.

- **Given** chế độ live có key LLM, **then** app hiện tiêu đề, diễn biến và nhãn "Kịch bản do LLM viết".
- **Given** không có key hoặc LLM lỗi, **then** vẫn chạy với nhãn "Kịch bản mẫu (không gọi được LLM)".

## Epic 3 — Tin được app

### US-3.1 Nhận thông báo khi ao chuyển trạng thái · FR-08

- **Given** ao chuyển sang Nguy hiểm và kéo dài ≥ 20 phút, **then** nhận 1 thông báo; không nhận lại trong 60 phút.
- **Given** ao về An toàn sau Nguy hiểm, **then** nhận "Ao đã ổn định trở lại".

### US-3.2 Thấy AI tốt hơn ngưỡng cố định ở đâu · FR-07, FR-09

- **Given** một lượt đang chạy, **then** thấy song song "Ngưỡng cố định" và "PondGuard" cùng thời điểm báo đầu tiên.
- **Given** app đã tải xong, **then** thấy bảng F1, báo giả/ngày, % lỗi cảm biến bị báo thành nguy hiểm.

### US-3.3 Biết khi mất kết nối · NFR-05

- **Given** backend tắt hoặc mất mạng, **then** hiện lỗi "Không kết nối được …" và nút chạy dùng lại được.
