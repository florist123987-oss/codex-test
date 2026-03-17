# Codex vs Claude Code quick notes

## Web lookup attempt (environment)
- Attempted to fetch official pages via `curl`/`urllib`:
  - https://openai.com/index/introducing-codex/
  - https://help.openai.com/en/articles/11096431-codex-faq
  - https://docs.anthropic.com/en/docs/claude-code/overview
- Result in this runtime: outbound requests failed with `Tunnel connection failed: 403 Forbidden`.

## Conceptual comparison (high level)
- Codex (current OpenAI usage context): a coding-focused agent/model experience used to read/edit code, run commands, and help with software tasks in repositories and terminals.
- Claude Code: Anthropic's terminal-centric coding agent experience built around Claude models for repository editing, command execution, and development workflows.
- Relationship: they are separate products from different companies (OpenAI vs Anthropic), not one being a submodule of the other.
- Similarities: both target code generation/refactoring, repo-aware assistance, shell/tool usage, and iterative agent workflows.
- Common practical differences people evaluate:
  - model family + coding behavior/style,
  - tool/runtime integrations,
  - latency/context limits/pricing,
  - ecosystem and enterprise controls,
  - default workflow ergonomics in CLI/editor.
