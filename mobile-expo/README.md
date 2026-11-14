# PondGuard mobile — Expo (SDK 58)

App Expo/React Native của PondGuard. App Flutter của team nằm ở `../mobile/`.

```bash
cd mobile-expo
npm install
npx expo start        # quét QR bằng Expo Go (SDK 58)
```

**Chế độ** (`config.ts`):
- `OFFLINE = true` (mặc định): đọc `assets/demo.json`, không cần mạng. Ao 3 với 6 kịch bản + ao 2 (cảm biến lỗi thật).
- `OFFLINE = false`: kết nối WebSocket tới API, gõ tình huống tự do cho LLM, chọn mọi ao/sự cố/cường độ. Sửa `API_URL` thành IP LAN của máy chạy API.

**Thông báo**: thông báo cục bộ (`expo-notifications`) chạy được trong Expo Go — cho phép quyền thông báo khi mở app lần đầu. Push từ xa không dùng (Expo Go không hỗ trợ). Trên web chỉ có banner trong app.

Tạo lại `assets/demo.json` sau khi chạy lại pipeline: `python api/export_demo.py` (ở gốc repo).
