# Tiếp cận và mở rộng thị trường — PondGuard

> Status: v1 · 14/11/2026 · Theo bản đặc tả §15 (tiêu chí 3, tối đa 25 điểm). Mọi nội dung về doanh thu, quy mô và giá
> là **giả thuyết**.

## 1. Bãi đáp đầu tiên

Hộ nuôi cá rô phi ao đất đã có hoặc sắp mua máy đo, dùng Android. Nhóm hẹp để dễ tìm người dùng đầu tiên và dễ kiểm chứng ngưỡng.

Mở rộng sang loài khác chỉ cần đổi bộ ngưỡng và luật fuzzy (`ai/pondguard/fuzzy_risk.py`), giữ nguyên pipeline.

## 2. Các lựa chọn người nuôi đang dùng

| Lựa chọn | Hạn chế PondGuard nhắm vào |
|---|---|
| Kinh nghiệm, quan sát cá nổi đầu | Phát hiện khi cá đã stress |
| Bút đo cầm tay, bộ test nhanh | Số rời rạc, không có diễn biến; phải tự diễn giải |
| Hệ thống IoT có cảnh báo ngưỡng | Ngưỡng cố định báo giả khi cảm biến lỗi, không tính nhịp ngày đêm |

Khác biệt cần kiểm chứng: tách lỗi cảm biến khỏi rủi ro thật, giải thích bằng tiếng Việt, hành động cụ thể. **Không** tuyên bố tốt hơn mọi hệ thống giám sát. So sánh đối thủ có tên, giá: chưa làm.

## 3. Lộ trình

| Giai đoạn | Kênh và hành động | Tín hiệu để đi tiếp |
|---|---|---|
| Trong sự kiện | Phỏng vấn 3–5 người nuôi qua quan hệ, cho xem màn hình cảnh báo | Người nuôi hiểu cảnh báo và nêu được hành động sẽ làm |
| 1 tháng sau (kế hoạch) | 3–5 ao pilot nhập tay số đo 2 lần/ngày, hỗ trợ trực tiếp | Số hộ nhập đều; số cảnh báo được xác nhận đúng/sai |
| Việt Nam, khi có tín hiệu | Hợp tác xã, đại lý thức ăn/thuốc thủy sản, đơn vị bán cảm biến IoT; mở rộng sang cá tra, tôm (thay độ đục bằng độ mặn) | Retention theo tuần; tỷ lệ cảnh báo đúng; chi phí hỗ trợ mỗi hộ |
| Toàn cầu, theo từng thị trường | Thị trường nuôi rô phi lớn dùng Android; ngôn ngữ và ngưỡng theo vùng | Ngưỡng và luật đã kiểm chứng với chuyên gia địa phương |

## 4. Giả thuyết doanh thu

- Miễn phí cho nhập tay.
- Thu phí theo ao/tháng khi kết nối cảm biến tự động và có cảnh báo đẩy; hoặc bán kèm gói với đơn vị cung cấp cảm biến.
- MVP chưa cần thanh toán; chỉ thử giá khi đã biết giá trị với người nuôi.

## 5. Chi phí vận hành

Mô hình nhỏ chạy CPU (Isolation Forest + Fuzzy), không tốn phí API theo lượt; LLM chỉ dùng để viết kịch bản demo và là tùy chọn. Chi phí chính là server, lưu trữ và hỗ trợ người dùng — cần đo khi pilot, không tự đặt số.

## 6. Lợi thế cần tích lũy

- Bộ luật và ngưỡng đã kiểm chứng theo loài và vùng.
- Dữ liệu phản hồi "cảnh báo đúng/sai" từ người nuôi (chỉ dùng trong phạm vi họ cho phép), dùng để train lại theo giai đoạn nuôi (xem kết quả concept drift).
