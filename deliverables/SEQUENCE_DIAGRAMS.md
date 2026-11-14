# Sơ đồ tuần tự — PondGuard

> Status: v1 · 14/11/2026 · Đối chiếu source `0e71707`.

## 1. Chạy real-time từ mô tả tình huống (chế độ live)

```mermaid
sequenceDiagram
    actor U as Người dùng
    participant A as App Expo
    participant W as API /ws/run
    participant L as llm_scenario
    participant X as LLM (tùy chọn)
    participant D as inject + Detector

    U->>A: Chọn ao, gõ "3 giờ sáng mất điện…", bấm Chạy
    A->>W: mở WebSocket, gửi {pond, prompt, tick_ms}
    W-->>A: {type: status, "LLM đang viết kịch bản…"}
    W->>L: generate(prompt)
    alt có key và gọi được
        L->>X: chat/completions (JSON)
        X-->>L: {title, narrative, events}
        L-->>W: kịch bản đã kiểm, source=llm
    else không có key hoặc lỗi
        L-->>W: kịch bản mẫu theo từ khóa, source=fallback:…
    end
    W->>D: run_events(pond, events, 24h)
    D-->>W: points[] (risk, level, sensor_check, reasons, action, flags, alert)
    W-->>A: {type: scenario}
    W-->>A: {type: history, points trước sự cố}
    loop mỗi tick_ms
        W-->>A: {type: point, i, point}
        opt point.alert khác null
            A->>U: banner + thông báo cục bộ
        end
    end
    W-->>A: {type: end, summary}
```

## 2. Chạy một sự cố chọn sẵn

Giống mục 1 nhưng app gửi `{pond, event, intensity}`; server tạo kịch bản một sự cố lúc `start_hour` (mặc định 12), không gọi LLM, `source = manual`.
Chọn ao `showcase` (ao 2) thì app chỉ gửi `{pond}`: phát lại dữ liệu lỗi cảm biến thật, không chèn sự cố.

## 3. Chế độ offline

```mermaid
sequenceDiagram
    actor U as Người dùng
    participant A as App Expo
    participant J as assets/demo.json

    U->>A: Mở app
    A->>J: loadPonds / loadEvents / loadMetrics
    U->>A: Chọn kịch bản, bấm Chạy
    A->>J: lấy chuỗi đã chấm sẵn
    loop theo nhịp
        A->>A: phát từng điểm, bắn banner/thông báo
    end
```

`demo.json` được tạo bằng `python api/export_demo.py` từ mô hình thật, nhưng **không gọi AI khi chạy**. Chỉ dùng làm phương án dự phòng; khi trình diễn phải nói rõ là kết quả đóng gói sẵn.
