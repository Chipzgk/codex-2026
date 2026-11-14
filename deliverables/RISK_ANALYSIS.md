# Phân tích rủi ro — PondGuard

> Status: draft v1 · 14/11/2026 · Phạm vi: rủi ro sản phẩm, mô hình, kỹ thuật và trình diễn; biện pháp **đã có trong code**
> tại `0e71707`. Điểm "Còn lại" là đánh giá của nhóm.

## 1. Thang đo

**Điểm = Khả năng (L) × Mức nghiêm trọng (S)**, mỗi trục 1–5.
S: 1 bất tiện · 2 mất niềm tin nhẹ · 3 xử lý muộn hoặc làm việc thừa · 4 cá stress, hao hụt một phần · 5 cá chết hàng loạt.
Mức: 1–6 thấp · 8–12 trung bình · 15–25 cao.

## 2. Rủi ro sản phẩm và mô hình

| Mã | Rủi ro | L | S | Điểm | Biện pháp đã có | Còn lại |
|---|---|:-:|:-:|:-:|---|:-:|
| R-01 | Bỏ sót nguy cơ thật vì dữ liệu bị đánh dấu không đáng tin (khoảng 30% dữ liệu nền) | 3 | 5 | **15** | Luật 7: DO rất thấp dù không đáng tin vẫn lên mức vừa; app hiện "Kiểm tra cảm biến" kèm hành động kiểm tra máy đo | **Cao**: chưa có kênh nhắc đo tay lại |
| R-02 | Trôi hiệu chuẩn bị nhầm với DO giảm thật (hoặc ngược lại) | 3 | 4 | **12** | Ghi rõ là giới hạn; có kịch bản `sensor_drift` để trình diễn | Trung bình: cần cảm biến thứ hai hoặc đo tay |
| R-03 | Cảnh báo chậm hơn ngưỡng cố định khoảng 10 phút | 4 | 3 | **12** | Chính sách thông báo `danger` chỉ cần 2 điểm (20 phút) | Trung bình: chưa có lead time tốt hơn |
| R-04 | Ngưỡng từ tài liệu nước ngoài không khớp ao Việt Nam | 4 | 3 | **12** | Ngưỡng tập trung ở `fuzzy_risk.py`, dễ đổi | Trung bình đến khi người nuôi hoặc chuyên gia xác nhận |
| R-05 | Mô hình học trên ao aquaponics Nigeria, không khớp ao đất | 4 | 3 | **12** | Ao chưa thấy dùng nhịp ngày đêm trung vị; thí nghiệm drift cho thấy cần train lại | Trung bình |
| R-06 | Concept drift khi cá lớn làm DO nền giảm | 4 | 2 | 8 | Có thí nghiệm; train lại giảm báo giả 23% | Trung bình: chưa tự train lại |
| R-07 | Báo quá nhiều làm người nuôi bỏ qua thông báo | 3 | 3 | 9 | Phải kéo dài + thời gian chờ; tắt `watch` sau `danger` | Thấp |
| R-08 | LLM viết kịch bản sai, gây hiểu nhầm là số đo do LLM bịa | 2 | 2 | 4 | LLM không sinh số; server kiểm schema; nhãn nguồn kịch bản trên app | Thấp |
| R-09 | Pitch nói quá về vai trò ML | 4 | 3 | **12** | Báo cáo ghi rõ Isolation Forest chưa đóng góp | Thấp nếu nói đúng |

## 3. Rủi ro kỹ thuật và trình diễn

| Mã | Rủi ro | L | S | Điểm | Biện pháp | Còn lại |
|---|---|:-:|:-:|:-:|---|:-:|
| R-10 | Demo ở chế độ offline bị chấm "không AI live" | 4 | 5 | **20** | Có chế độ live (`OFFLINE = false`) | Thấp khi chạy live |
| R-11 | Backend không chạy được sau khi clone vì thiếu mô hình | 4 | 4 | **16** | `/health`, lỗi 503 rõ ràng; lệnh train ở [DEPLOYMENT.md](DEPLOYMENT.md) | Trung bình |
| R-12 | Điện thoại không vào được backend (khác mạng, IP LAN đổi) | 4 | 4 | **16** | `API_URL` cấu hình được; checklist trước demo | Trung bình |
| R-16 | Lộ key LLM | 2 | 3 | 6 | Key đọc từ `.env` ở server, `.env` bị gitignore, không nằm trong app | Thấp |

## 4. Ứng phó khi demo gặp lỗi

1. Chuyển sang mạng dự phòng, chạy lại.
2. Backend chết: khởi động lại uvicorn (mô hình nạp trong vài giây).
3. Vẫn không được: chuyển `OFFLINE = true` và **nói rõ** đây là kết quả đóng gói sẵn từ mô hình thật, không phải lượt AI mới.
