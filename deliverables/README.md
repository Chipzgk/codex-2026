# Tài liệu dự án PondGuard — mục lục

> Status: v1 · 14/11/2026 · Đối chiếu source `0e71707`. Nội dung theo bản đặc tả
> "PondGuard — Đặc tả Prototype Android" và code hiện có.

Mỗi thông tin chỉ có **một nguồn chính**; tài liệu khác link tới đó:

| Thông tin | Nguồn chính |
|---|---|
| Trạng thái từng tính năng, quy tắc nghiệp vụ | [PRD.md](PRD.md) |
| Mô hình, ngưỡng, luật fuzzy, chính sách thông báo | [AI_MODEL_DESIGN.md](AI_MODEL_DESIGN.md) |
| Endpoint, schema, tin nhắn WebSocket | [API_DESIGN.md](API_DESIGN.md) |
| Số đánh giá | [`eval/results/report.md`](../eval/results/report.md) |
| Kiến trúc, chỗ lệch so với đặc tả | [`docs/architecture_diagram.md`](../docs/architecture_diagram.md) |

## 1. Nghiệp vụ

| Tài liệu | Nội dung |
|---|---|
| [PROJECT_BRIEF.md](PROJECT_BRIEF.md) | Vấn đề, giải pháp, ràng buộc cốt lõi, phạm vi một ngày |
| [PRD.md](PRD.md) | Tính năng và trạng thái, quy tắc nghiệp vụ, chỉ số, ưu tiên việc còn lại |
| [USER_STORIES.md](USER_STORIES.md) | Story và tiêu chí chấp nhận Given–When–Then |
| [MARKET_ANALYSIS.md](MARKET_ANALYSIS.md) | Bãi đáp, lộ trình mở rộng, giả thuyết doanh thu |

## 2. Trải nghiệm

| Tài liệu | Nội dung |
|---|---|
| [WIREFRAME_UI_FLOW.md](WIREFRAME_UI_FLOW.md) | Luồng người dùng, wireframe, ánh xạ màn hình ↔ API |

## 3. Kỹ thuật

| Tài liệu | Nội dung |
|---|---|
| [`docs/architecture_diagram.md`](../docs/architecture_diagram.md) | Thành phần, luồng dữ liệu, chỗ lệch so với đặc tả |
| [AI_MODEL_DESIGN.md](AI_MODEL_DESIGN.md) | Dữ liệu, feature, độ tin cậy, Isolation Forest, Fuzzy, vai trò LLM, giới hạn |
| [API_DESIGN.md](API_DESIGN.md) | Endpoint, schema, tin nhắn WebSocket |
| [SEQUENCE_DIAGRAMS.md](SEQUENCE_DIAGRAMS.md) | Chạy real-time, chế độ offline |

## 4. Kiểm chứng và vận hành

| Tài liệu | Nội dung |
|---|---|
| [TEST_PLAN.md](TEST_PLAN.md) | Chiến lược, ma trận yêu cầu → test, kịch bản kiểm tay |
| [`eval/results/report.md`](../eval/results/report.md) | Kết quả so sánh 4 phương pháp, concept drift, giới hạn |
| [KPI_FRAMEWORK.md](KPI_FRAMEWORK.md) | Chỉ số, mục tiêu, hiện trạng |
| [RISK_ANALYSIS.md](RISK_ANALYSIS.md) | Ma trận rủi ro L×S, ứng phó khi demo lỗi |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Chạy backend, app, biến môi trường, checklist trước demo |

## Nộp bài

| Tài liệu | Nội dung |
|---|---|
| [SUBMISSION_MVP.md](SUBMISSION_MVP.md) | Checklist gói nộp và trạng thái |
| [DEMO_SCRIPT.md](DEMO_SCRIPT.md) | Kịch bản 5 phút, câu hỏi có thể gặp |
| [`WORKLOG.md`](../WORKLOG.md) | Nhật ký theo commit |

## Khi sửa code

Sửa schema, endpoint, luật fuzzy hay ngưỡng thì sửa tài liệu nguồn chính tương ứng trong cùng PR, và cập nhật trạng thái trong [PRD.md](PRD.md).
