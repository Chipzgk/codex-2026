# codex-2026

Repo cho hackathon Codex 2026. Hiện tại repo mới chỉ có bộ công cụ hỗ trợ làm việc với AI agent và quy ước commit, chưa có code ứng dụng.

## Có gì trong repo

| Thành phần | Mục đích |
| --- | --- |
| **BMAD Method** | Quy trình làm sản phẩm có AI dẫn dắt: brainstorm → PRD → kiến trúc → epic/story → code → review |
| **CodeGraph** | MCP server lập chỉ mục code cho agent, giúp agent tìm symbol/luồng code mà không phải đọc nhiều file → tiết kiệm token |
| **commitlint + husky** | Kiểm tra message commit theo format `type(scope): subject` ngay khi commit |

## Cấu trúc thư mục

```
codex-2026/
├── .agents/skills/        # Các skill BMAD (agent dev, architect, pm, code-review, ...)
├── _bmad/                 # Config BMAD (ngôn ngữ tài liệu: tiếng Việt)
├── _bmad-output/          # Nơi BMAD ghi kết quả
│   ├── planning-artifacts/        # PRD, kiến trúc, epic
│   └── implementation-artifacts/  # spec, story
├── .codegraph/            # Index của CodeGraph (chỉ commit .gitignore)
├── .codex/config.toml     # MCP CodeGraph cho Codex
├── .mcp.json              # MCP CodeGraph cho Claude Code
├── .husky/commit-msg      # Hook chạy commitlint
├── AGENTS.md              # Hướng dẫn cho agent (CLAUDE.md trỏ về file này)
├── commitlint.config.cjs  # Quy ước scope/type cho commit
└── package.json
```

## Yêu cầu

- Node.js >= 20
- pnpm (hoặc npm)
- Git

## Cài đặt

```bash
# 1. Cài dependency, đồng thời kích hoạt git hook của husky
pnpm install

# 2. Cài CodeGraph (chỉ cần 1 lần cho cả máy)
npm i -g @colbymchenry/codegraph

# 3. Tạo index CodeGraph cho repo này
codegraph init
```

Sau đó mở lại Claude Code hoặc Codex để agent nạp MCP server CodeGraph. Lần đầu mở bằng Codex, cần chọn tin cậy thư mục này thì Codex mới đọc `.codex/config.toml`.

## Quy ước commit

Format bắt buộc:

```
type(scope): subject
```

| Scope | Dùng cho | Type được phép |
| --- | --- | --- |
| `repo` | Cấu hình chung, tooling, CI | build, chore, ci, docs, refactor, test, revert |
| `web` | Frontend | feat, fix, perf, refactor, style, test, docs, chore, revert |
| `api` | Backend | như `web` |
| `ai` | Model, pipeline, prompt | như `web` |
| `docs` | Tài liệu | docs, chore |

Ví dụ:

```bash
git commit -m "feat(web): add login page"
git commit -m "fix(api): handle empty request body"
git commit -m "chore(repo): update commitlint scopes"
```

Commit sai format sẽ bị husky chặn. Khi repo có thêm app hoặc package mới, thêm scope vào `SCOPE_TYPE_MAP` trong `commitlint.config.cjs`.

## Làm việc với AI agent

### CodeGraph

Agent được dặn trong `AGENTS.md` là phải dùng CodeGraph **trước** khi Grep/Read nhiều file:

- Agent có MCP: gọi tool `codegraph_explore` và các tool `codegraph_*` khác.
- Subagent hoặc agent không có MCP: chạy `codegraph explore "<câu hỏi>"` trong shell.

Index tự đồng bộ khi file thay đổi. Nếu cần tạo lại từ đầu: `codegraph uninit` rồi `codegraph init`.

### BMAD

Gọi skill BMAD bằng tên trong agent (ví dụ `bmad-help` để xem nên bắt đầu từ đâu). Luồng gợi ý cho hackathon:

1. `bmad-brainstorming` hoặc `bmad-product-brief`: chốt ý tưởng
2. `bmad-create-prd`: viết PRD
3. `bmad-create-architecture`: thiết kế kiến trúc
4. `bmad-create-epics-and-stories` → `bmad-create-story`: chia việc
5. `bmad-dev-story` hoặc `bmad-quick-dev`: code
6. `bmad-code-review`: review

Khi gấp, dùng `bmad-quick-dev` để đi thẳng từ yêu cầu đến code.

Tài liệu sinh ra nằm trong `_bmad-output/`. Muốn đổi cấu hình BMAD cho cả team thì sửa `_bmad/custom/config.toml`. Cấu hình cá nhân để ở `_bmad/custom/config.user.toml` (đã gitignore).
