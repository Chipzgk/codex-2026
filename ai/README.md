# PondGuard AI core

Phát hiện bất thường (Isolation Forest) + đánh giá rủi ro (Mamdani fuzzy) cho ao cá, đánh giá trên
**dữ liệu cảm biến thật** (Kaggle: `ogbuokiriblessing/sensor-based-aquaponics-fish-pond-datasets`)
**có chèn sự kiện được gán nhãn** (semi-synthetic) để tính Precision/Recall.

## Chạy

```bash
conda create -n pondguard python=3.11 -y && conda activate pondguard
pip install -r ai/requirements.txt
# tải dữ liệu (cần ~/.kaggle/kaggle.json) hoặc tải tay rồi giải nén vào ai/data/raw/
kaggle datasets download -d ogbuokiriblessing/sensor-based-aquaponics-fish-pond-datasets -p ai/data/raw --unzip
python ai/scripts/run_pipeline.py --raw ai/data/raw --out ai/reports --processed ai/data/processed --exclude IoTPond2 IoTPond8
# -> scored.csv + simulator.joblib (mô hình cho API); ao 2 giữ lại làm ví dụ cảm biến kẹt thật
```

Đánh giá trên nhiều seed (điều chỉnh trên 1–3, báo cáo trên 11–15):
`python ai/scripts/multi_seed.py --raw ai/data/raw --seeds 11 12 13 14 15 --out ai/reports/heldout.md`

Concept drift (cá lớn → DO nền giảm): `python ai/scripts/drift_experiment.py --raw ai/data/raw --out ai/reports`

Chưa có dữ liệu thật, muốn thử code: `python ai/scripts/make_fake_raw.py ai/data/fake_raw` rồi chạy với `--raw ai/data/fake_raw`.

## Thiết kế đánh giá

- Mỗi ao: lấy đoạn liên tục dài nhất; 50% đầu (sạch) để train Isolation Forest, 50% sau chèn sự kiện để test.
- Sự kiện **rủi ro thật**: `do_drop` (máy sục khí hỏng), `do_decline` (DO giảm dần). Sự kiện **lỗi cảm biến**: `stuck`, `spike`.
- 4 phương pháp: `threshold` (DO<3, pH ngoài 6.5–9), `iforest`, `fuzzy_only` (không dùng ML), `hybrid`.
- Chỉ số: precision/recall/F1 theo điểm, event recall, độ trễ phát hiện, cảnh báo giả/ngày,
  số lỗi cảm biến bị báo thành "nguy hiểm" (càng thấp càng tốt).
- Ngưỡng mờ cho cá nước ấm cố định từ tài liệu (DO<3 nguy hiểm, 3–5 stress, >5 tốt), không tinh chỉnh theo kết quả.

Giới hạn: nền thật có thể chứa bất thường thật chưa gán nhãn → precision bị đánh giá hơi thấp.
