# Triển khai và chạy demo — PondGuard

> Status: v1 · 14/11/2026 · Lệnh lấy từ README của `ai/`, `api/`, `mobile-expo/` tại `0e71707`.

## 1. Môi trường

| Môi trường | Backend | App |
|---|---|---|
| Dev / demo | Laptop chạy uvicorn, cùng Wi-Fi với điện thoại | Expo Go, `API_URL` = IP LAN của laptop |

## 2. Backend

Yêu cầu: Python 3.11, tài khoản Kaggle (`~/.kaggle/kaggle.json`) để tải dữ liệu.

```bash
conda create -n pondguard python=3.11 -y && conda activate pondguard
pip install -r ai/requirements.txt

# 1. Tải dữ liệu (một lần)
kaggle datasets download -d ogbuokiriblessing/sensor-based-aquaponics-fish-pond-datasets -p ai/data/raw --unzip

# 2. Train + chấm điểm → ai/data/processed/simulator.joblib, scored.csv
python ai/scripts/run_pipeline.py --raw ai/data/raw --out ai/reports --processed ai/data/processed --exclude IoTPond2 IoTPond8

# 3. (tùy chọn) Số đánh giá trên seed giữ riêng → ai/reports/heldout.csv cho /metrics
python ai/scripts/multi_seed.py --raw ai/data/raw --seeds 11 12 13 14 15 --out ai/reports/heldout.md

# 4. Chạy API ở gốc repo
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Kiểm: `curl http://localhost:8000/health` phải trả `{"ok": true}`.

Không tải được dữ liệu: `python ai/scripts/make_fake_raw.py ai/data/fake_raw` rồi chạy bước 2 với `--raw ai/data/fake_raw`. Dữ liệu giả **chỉ để thử code**, không dùng làm số đánh giá hay demo chính.

## 3. Biến môi trường (file `.env` ở gốc repo, đã gitignore)

| Biến | Bắt buộc | Ý nghĩa |
|---|---|---|
| `OPEN_API_KEY` hoặc `OPENAI_API_KEY` | Không | Key LLM tương thích OpenAI để viết kịch bản |
| `MODEL_ID` | Không (cần nếu có key) | Tên model |
| `OPENAI_BASE_URL` | Không | Mặc định `https://api.openai.com/v1` |

Không có key → kịch bản mẫu theo từ khóa, demo vẫn chạy. Key chỉ ở server, **không** đưa vào app.

## 4. App Expo

```bash
cd mobile-expo
npm install
npx expo start      # quét QR bằng Expo Go (SDK 58)
```

Sửa [`config.ts`](../mobile-expo/config.ts):

| Hằng | Demo AI live | Dự phòng |
|---|---|---|
| `OFFLINE` | `false` | `true` (đọc `assets/demo.json`) |
| `API_URL` | `http://<IP LAN>:8000` | — |

Tìm IP LAN trên Windows: `ipconfig` → IPv4. Không dùng `localhost` khi chạy trên điện thoại. Windows Firewall có thể chặn cổng 8000: cho phép Python qua tường lửa ở mạng Private.

Tạo lại `demo.json` sau khi train lại: `python api/export_demo.py`.

## 5. Checklist trước giờ demo

- [ ] `/health` trả `ok: true` trên laptop demo
- [ ] Mở `http://<IP>:8000/ponds` từ **trình duyệt điện thoại** thành công
- [ ] `OFFLINE = false`, nhãn trên app là **Live**
- [ ] Laptop cắm sạc, tắt chế độ ngủ
- [ ] Có mạng dự phòng (hotspot) và đã thử `API_URL` với mạng đó
