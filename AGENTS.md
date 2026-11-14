# Agent guide — codex-2026

## Code navigation: dùng CodeGraph trước
- Repo có CodeGraph MCP (`codegraph serve --mcp`). Khi cần tìm symbol, caller/callee, hay hiểu luồng code,
  gọi tool `codegraph_*` (vd `codegraph_explore`) TRƯỚC khi Grep/Read nhiều file — tiết kiệm token.
- Subagent / agent không có MCP: chạy `codegraph explore "<câu hỏi>"` trong shell.
- Nếu tool báo file đang pending sync (⚠️), Read trực tiếp file đó.

## Quy trình
- Planning / spec / story: dùng các skill BMAD trong `.agents/skills/` (output vào `_bmad-output/`).

## Commit
- `type(scope): subject`, scope theo `commitlint.config.cjs`. Hook husky sẽ chặn commit sai format.
