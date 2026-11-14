# PondGuard — kết quả (dữ liệu cảm biến thật, Kaggle aquaponics IoT)

Tái tạo: xem `ai/README.md`. Số liệu lấy từ `heldout.md` và `drift.md` trong thư mục này.

## Thiết kế đánh giá
- Nền: dữ liệu cảm biến thật ao 1, 3, 4, 6 (gom 10 phút). Loại: ao 2 (cảm biến DO kẹt thật → dùng làm ví dụ demo), ao 8 (lỗi định dạng thời gian), ao 10–12 (quá ngắn).
- Mỗi ao: nửa đầu sạch để train, nửa sau chèn sự cố có nhãn: rủi ro thật (`do_drop`, `do_decline`) và lỗi cảm biến (`stuck`, `spike`).
- Điều chỉnh thiết kế trên seed 1–3; **báo cáo trên seed 11–15 chưa từng dùng để điều chỉnh**.
- Ngưỡng Fuzzy cố định theo tài liệu cá nước ấm (DO < 3 nguy hiểm, 3–5 stress), không chỉnh theo kết quả.
- Phát hiện lỗi cảm biến chỉ dùng dữ liệu quá khứ (không nhìn trước), độ tin cậy tính riêng cho từng cảm biến.

## Kết quả chính (seed giữ riêng 11–15)
| Phương pháp | F1 | Báo giả/ngày | Bắt sự cố thật | Lỗi cảm biến bị báo thành nguy hiểm | Trễ (trung vị) |
|---|---|---|---|---|---|
| Ngưỡng cố định (DO<3, pH ngoài 6,5–9) | 0,579 | 2,43 | 100% | 26% | 42 phút |
| Isolation Forest | 0,018 | 0,51 | 18% | 5% | 122 phút |
| Fuzzy (không ML) | 0,581 | 1,66 | 100% | 15% | 52 phút |
| **Hybrid** | **0,581** | **1,66** | **100%** | **15%** | 52 phút |

## Nhận xét trung thực
- Hybrid ngang Ngưỡng về F1, nhưng **ít báo giả hơn 32%** và **ít báo nhầm lỗi cảm biến thành nguy hiểm hơn** (15% vs 26%), đổi lại chậm hơn ~10 phút.
- Giá trị đến từ **lớp độ tin cậy dữ liệu + Fuzzy**. Isolation Forest phân hạng gần như ngẫu nhiên trên dữ liệu này (ROC-AUC ≈ 0,57) vì DO thấp xuất hiện thường xuyên ngay trong dữ liệu nền → Hybrid = Fuzzy-only. Câu trả lời cho research question hiện là: **ML chưa giúp thêm** trên bộ dữ liệu này.
- Cảm biến DO trong bộ dữ liệu rất nhiễu: ~30% dữ liệu nền bị đánh dấu "không đáng tin". Hệ thống không báo nguy hiểm trong những đoạn đó — đúng nếu là nhiễu, nhưng có thể bỏ sót nếu là nguy cơ thật.
- Ví dụ thật: ao 2 — Ngưỡng cố định báo động 31% thời gian; PondGuard đánh dấu 99% dữ liệu DO là không đáng tin (đứng gần như phẳng) và **không** báo nguy hiểm lần nào.

## Concept drift
Cá lớn từ ~7 cm (tháng 6) lên 22–29 cm (tháng 8–9), DO trung bình giảm từ ~9 xuống ~2–5 mg/L.
- Isolation Forest train từ tháng 6 coi dữ liệu bình thường tháng 8 là bất thường (điểm bất thường TB 0,30 vs 0,11 khi train lại trên cửa sổ gần nhất).
- Train lại trên dữ liệu gần đây giảm báo giả của Hybrid 23% (2,63 → 2,03/ngày); F1 gần như không đổi.
- Kết luận: mô hình cần cập nhật định kỳ theo giai đoạn nuôi.

## Giới hạn
- Sự cố được chèn (semi-synthetic), không phải sự cố thật có nhãn; nền thật có thể chứa nguy cơ thật chưa gán nhãn → precision có thể bị đánh giá thấp.
- **Trôi hiệu chuẩn cảm biến** trông giống hệt DO giảm dần thật: hệ thống không phân biệt được (có trong demo như giới hạn). Cần kiểm tra chéo cảm biến khác hoặc đo tay.
- Ao cá aquaponics (Nigeria), không phải ao tôm; ngưỡng theo cá nước ấm.
