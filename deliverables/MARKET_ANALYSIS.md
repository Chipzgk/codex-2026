# Tiếp cận và mở rộng thị trường — PondGuard

> Status: v2 · 14/11/2026 · Doanh thu và quy mô là **giả thuyết**. Thông tin đối thủ lấy từ các trang ở mục Nguồn.

## 0. Quy mô thị trường

| Chỉ số | Giá trị | Nguồn |
|---|---|---|
| Diện tích nuôi cá rô phi Việt Nam, 2024 | 42.716 ha | Cục Thủy sản và Kiểm ngư, qua [Nông nghiệp & Môi trường, 10/11/2025](https://nongnghiepmoitruong.vn/ca-ro-phi-viet-nam-nhieu-loi-the-nhung-chua-but-pha-d782970.html) |
| Sản lượng cá rô phi Việt Nam, 2024 | hơn 316.000 tấn | Như trên |
| Sản lượng cá rô phi Việt Nam, 2015 → 2025 | 188.000 → 420.000 tấn | [Nông nghiệp & Môi trường, 04/08/2026](https://nongnghiepmoitruong.vn/thao-go-diem-nghen-de-phat-trien-nganh-hang-ca-ro-phi-d824589.html) |
| Sản lượng rô phi thế giới, 2021 | hơn 7,2 triệu tấn | [Aqua Culture Asia Pacific](https://aquaasiapac.com/2025/02/04/the-global-tilapia/) (bài số 7–8/2023) |
| Nước sản xuất lớn nhất | Trung Quốc 1,75 triệu tấn (2022), Indonesia 1,2 triệu tấn, Ai Cập hơn 1 triệu tấn — ba nước chiếm gần 75% | Như trên |
| Dự báo thế giới, 2030 | 9 triệu tấn | Như trên |

Chưa có số liệu về số hộ nuôi hay số ao đã lắp cảm biến; đây là con số cần thu thập khi pilot.

## 1. Bãi đáp đầu tiên

Hộ nuôi cá ao quy mô nhỏ dùng Android. Phỏng vấn U01 ([USER_RESEARCH.md](USER_RESEARCH.md)) cho thấy hai nhóm:

| Nhóm | Đặc điểm | PondGuard cần gì để phục vụ |
|---|---|---|
| Hộ chưa có thiết bị đo (như U01) | Nuôi theo kinh nghiệm, canh ao buổi tối, phát hiện cá chết muộn | Cảm biến DO giá rẻ hoặc số đo nhập tay |
| Hộ đã lắp IoT có cảnh báo ngưỡng | Bị báo động giả khi cảm biến lỗi | Dùng được ngay lớp kiểm tra độ tin cậy + Fuzzy |

Mở rộng sang loài khác chỉ cần đổi ngưỡng và luật fuzzy (`ai/pondguard/fuzzy_risk.py`), giữ nguyên pipeline.

## 2. Đối thủ và lựa chọn hiện có

| Lựa chọn | Có gì | Khoảng trống PondGuard nhắm vào |
|---|---|---|
| Kinh nghiệm, ra ao xem cá | Không tốn tiền | Phát hiện khi cá đã chết (U01) |
| [E-Sensor Aqua](https://apps.apple.com/vc/app/e-sensor-aqua/id1444251288) | Thiết bị giám sát nước ao, xem trên điện thoại, cảnh báo SMS khi vượt ngưỡng, điều khiển máy sục khí và máy bơm | Cảnh báo theo ngưỡng; không phân biệt cảm biến lỗi với nguy hiểm thật |
| [Green AIoT](https://nongnghiepmoitruong.vn/bai-3-tom-khoe-nho-ung-dung-ai-d767545.html) (sinh viên IUH và BTEC FPT) | Cảm biến nhiệt độ, độ mặn, pH, oxy hòa tan, độ kiềm cho ao tôm; khi oxy giảm kéo dài 12 giờ thì khuyến nghị thay nước hoặc tăng sục khí | Hệ thống hoàn chỉnh "có thể tốn hàng trăm triệu đồng" — quá đắt với hộ nuôi cá nhỏ |
| [Aquasense](https://nongnghiepmoitruong.vn/cam-bien-giup-nuoi-trong-thuy-san-thich-ung-bien-doi-khi-hau-d385808.html) (Aqsen Innovations, Scotland) | Cảm biến chất lượng nước giá rẻ, nhắm giá 25–30% so với sản phẩm tương đương | Phần cứng; PondGuard có thể là lớp phần mềm chạy trên dữ liệu của cảm biến rẻ như vậy |

Khác biệt cần chứng minh: tách lỗi cảm biến khỏi rủi ro thật (báo nhầm lỗi cảm biến thành nguy hiểm 15% so với 26% của ngưỡng cố định), giải thích bằng tiếng Việt kèm hành động. PondGuard là phần mềm, có thể chạy trên dữ liệu của các thiết bị sẵn có.

## 3. Lộ trình

| Giai đoạn | Kênh và hành động | Tín hiệu để đi tiếp |
|---|---|---|
| Trong sự kiện | Phỏng vấn người nuôi (đã có U01), cho xem màn hình cảnh báo | Người nuôi hiểu cảnh báo và nêu được hành động |
| 1 tháng sau | 3–5 ao pilot; hộ chưa có cảm biến dùng cảm biến DO giá rẻ hoặc nhập số đo 2 lần/ngày | Số hộ dùng đều; số cảnh báo được xác nhận đúng/sai |
| Việt Nam | Hợp tác xã, đại lý thức ăn/thuốc thủy sản, đơn vị bán cảm biến IoT (tích hợp phần mềm vào thiết bị sẵn có); mở rộng sang cá tra, tôm | Retention theo tuần; tỷ lệ cảnh báo đúng |
| Toàn cầu | Các thị trường nuôi rô phi lớn; ngôn ngữ và ngưỡng theo vùng | Ngưỡng và luật được chuyên gia địa phương xác nhận |

## 4. Giả thuyết doanh thu và chi phí

- Miễn phí bản cơ bản; thu phí theo ao/tháng khi kết nối cảm biến tự động và cảnh báo đẩy; hoặc bán kèm gói với đơn vị cung cấp cảm biến.
- Mô hình nhỏ chạy CPU (Isolation Forest + Fuzzy), không tốn phí API theo lượt; LLM chỉ dùng cho demo và là tùy chọn. Chi phí chính là server và hỗ trợ người dùng.

## 5. Lợi thế cần tích lũy

- Bộ luật và ngưỡng được kiểm chứng theo loài và vùng.
- Dữ liệu phản hồi "cảnh báo đúng/sai" để train lại theo giai đoạn nuôi (train lại giảm báo giả 23% trong thí nghiệm concept drift).

## Nguồn (truy cập 14/11/2026)

- [Cá rô phi Việt Nam nhiều lợi thế nhưng chưa bứt phá — Nông nghiệp & Môi trường, 10/11/2025](https://nongnghiepmoitruong.vn/ca-ro-phi-viet-nam-nhieu-loi-the-nhung-chua-but-pha-d782970.html)
- [Tháo gỡ điểm nghẽn để phát triển ngành hàng cá rô phi — Nông nghiệp & Môi trường, 04/08/2026](https://nongnghiepmoitruong.vn/thao-go-diem-nghen-de-phat-trien-nganh-hang-ca-ro-phi-d824589.html)
- [The global tilapia — Aqua Culture Asia Pacific](https://aquaasiapac.com/2025/02/04/the-global-tilapia/)

- [E-Sensor Aqua — App Store](https://apps.apple.com/vc/app/e-sensor-aqua/id1444251288)
- [Phòng chống dịch bệnh thủy sản bằng công nghệ: Bài 3 — Tôm khỏe nhờ ứng dụng AI — Nông nghiệp & Môi trường, 16/08/2025](https://nongnghiepmoitruong.vn/bai-3-tom-khoe-nho-ung-dung-ai-d767545.html)
- [Cảm biến giúp nuôi trồng thủy sản thích ứng biến đổi khí hậu — Nông nghiệp & Môi trường, 11/05/2024](https://nongnghiepmoitruong.vn/cam-bien-giup-nuoi-trong-thuy-san-thich-ung-bien-doi-khi-hau-d385808.html)
