# Báo cáo đánh giá — PondGuard

> **Cập nhật:** 14/11/2026 · **Nguồn số:** [`ai/reports/heldout.md`](../../ai/reports/heldout.md), [`ai/reports/drift.md`](../../ai/reports/drift.md),
> [`ai/reports/REPORT.md`](../../ai/reports/REPORT.md) trong source `0e71707`. Báo cáo này **chỉ tổng hợp**, không chạy lại
> pipeline; dữ liệu thô không có trong repo (`ai/data/` bị gitignore).

## 1. Thiết kế đánh giá

| Hạng mục | Nội dung |
|---|---|
| Dữ liệu nền | Cảm biến thật, Kaggle aquaponics IoT (Nigeria), gom 10 phút |
| Nhãn | Chèn sự cố có nhãn vào nửa sau mỗi ao (semi-synthetic): rủi ro thật `do_drop`, `do_decline`; lỗi cảm biến `stuck`, `spike`. 8 sự cố/ao |
| Train | Nửa đầu sạch của mỗi ao |
| Điều chỉnh / báo cáo | Điều chỉnh thiết kế trên seed 1–3; **báo cáo trên seed 11–15, chưa từng dùng để điều chỉnh** |
| Ngưỡng | DO < 3 nguy hiểm, 3–5 stress (tài liệu cá nước ấm), cố định trước khi đo |
| So sánh | 4 phương pháp, cùng bộ chống dội 2 điểm: `threshold` (DO < 3 hoặc pH ngoài 6,5–9), `iforest` (anomaly > 0,6), `fuzzy_only` (Fuzzy với anomaly = 0), `hybrid` (Fuzzy + Isolation Forest) |
| Chỉ số | Precision / recall / F1 theo điểm; event recall (bắt được trong lúc sự cố + 1 giờ); trễ phát hiện trung vị; số đợt báo giả/ngày; % lỗi cảm biến bị báo thành nguy hiểm |

## 2. Kết quả chính (trung bình seed 11–15)

| Phương pháp | Precision | Recall | F1 | Bắt sự cố thật | Trễ trung vị | Báo giả/ngày | Lỗi cảm biến → nguy hiểm |
|---|---:|---:|---:|---:|---:|---:|---:|
| Ngưỡng cố định | 0,620 | 0,542 | 0,579 | 100% | **42 phút** | 2,43 | 25,6% |
| Isolation Forest | 0,172 | 0,010 | 0,018 | 18,2% | 122 phút | 0,51 | 5,1% |
| Fuzzy (không ML) | 0,633 | 0,539 | 0,581 | 100% | 52 phút | 1,66 | 15,4% |
| **Hybrid (PondGuard)** | 0,633 | 0,539 | **0,581** | 100% | 52 phút | **1,66** | **15,4%** |

## 3. Đọc kết quả

| Câu hỏi | Trả lời từ số liệu |
|---|---|
| PondGuard có ít báo giả hơn ngưỡng cố định không? | **Có**: 1,66 so với 2,43 đợt/ngày (ít hơn khoảng 32%) |
| Có ít báo nhầm lỗi cảm biến thành nguy hiểm hơn không? | **Có**: 15% so với 26% |
| Có bắt được sự cố thật không? | Có, 100% như ngưỡng cố định |
| Có cảnh báo **sớm** hơn không? | **Không**: chậm hơn khoảng 10 phút (52 so với 42 phút trung vị). Không được nói "cảnh báo sớm hơn" khi pitch |
| F1 có tốt hơn không? | Gần như bằng (0,581 so với 0,579) |
| Isolation Forest có giúp không? | **Chưa** trên bộ dữ liệu này: một mình recall 0,01; Hybrid cho kết quả trùng Fuzzy. Theo REPORT.md, ROC-AUC khoảng 0,57 vì DO thấp xuất hiện thường xuyên ngay trong dữ liệu nền |

Giá trị hiện tại đến từ **lớp độ tin cậy dữ liệu cộng Fuzzy**, không phải từ ML.

## 4. Ví dụ lỗi cảm biến thật — ao 2

Theo [REPORT.md](../../ai/reports/REPORT.md): ngưỡng cố định báo động 31% thời gian; PondGuard đánh dấu 99% dữ liệu DO là không đáng tin (gần như phẳng) và không báo nguy hiểm lần nào. Ao này không dùng để train.

## 5. Concept drift

Cá lớn từ khoảng 7 cm (tháng 6) lên 22–29 cm (tháng 8–9); DO trung bình giảm từ khoảng 9 xuống 2–5 mg/L.

| Train trên | Tỷ lệ Isolation Forest báo trên dữ liệu muộn chưa chèn sự cố | Anomaly trung bình |
|---|---:|---:|
| Đầu vụ | 3,0% | 0,303 |
| Gần đây | 1,1% | 0,112 |

Khi có sự cố chèn (seed 1–3): train lại gần đây giảm báo giả của Hybrid từ 2,63 xuống 2,03 đợt/ngày (khoảng 23%); F1 gần như không đổi (0,395 → 0,398). Kết luận: cần train lại định kỳ theo giai đoạn nuôi.

## 6. Giới hạn

- Sự cố được chèn, không phải sự cố thật có nhãn. Nền thật có thể chứa nguy cơ thật chưa gán nhãn, nên precision có thể bị đánh giá thấp.
- Khoảng 30% dữ liệu nền bị đánh dấu không đáng tin; trong các đoạn đó hệ thống không báo nguy hiểm.
- Trôi hiệu chuẩn cảm biến trông giống DO giảm dần thật; hệ thống không phân biệt được.
- Ao aquaponics Nigeria, không phải ao rô phi Việt Nam.
- [REPORT.md](../../ai/reports/REPORT.md) và [data_summary.csv](../../ai/reports/data_summary.csv) không khớp nhau về danh sách ao dùng làm nền (1, 3, 4, 6 so với thêm 7, 9). Cần chạy lại và chốt một lần trước khi nộp.

Tái tạo: [`ai/README.md`](../../ai/README.md).
