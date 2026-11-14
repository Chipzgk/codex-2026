// OFFLINE = true: dùng dữ liệu đóng gói sẵn trong assets/demo.json (không cần mạng) — an toàn khi lên sân khấu.
// OFFLINE = false: gọi API thật (POST /simulate) để giám khảo tự chọn kịch bản/cường độ.
export const OFFLINE = true;
// IP LAN của máy chạy API (ipconfig -> IPv4). Không dùng localhost khi chạy trên điện thoại.
export const API_URL = "http://192.168.1.10:8000";
