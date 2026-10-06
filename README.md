# Financial Writing Agent v0.2

A deterministic financial-writing agent runtime for A-share research articles.

## Identity

- Repository: `D1traverser-debug/financial-writing-agent`
- Canonical branch: `main`
- Python package: `financial_writing_agent`
- CLI: `financial-write`
- Skill name: `financial-writing-agent`

## Design

- **Python state machine owns workflow order and hard gates.**
- **Pydantic owns task/state contracts and structured model outputs.**
- **SQLite owns per-run checkpoints and resume.**
- **OpenAI Agents SDK is optional and only used inside high-judgment stages.**
- **Deterministic Python owns Word generation, required-output checks, mechanical audit and visible audit packaging.**
- **No silent degradation:** missing executors or tool failures route to `BLOCKED`; the runtime must not fall back to free-form writing.

## Runtime

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

## Core behavior

- Default `delivery_channel=WORD_FILE_ONLY`.
- `DUAL` means one complete research base plus independently edited `FINANCE_DEEP` and `FINANCE_BROAD` versions.
- TopicDNA and current-topic outlines are produced before historical-outline collision checks.
- Headline generation is a high-judgment hook stage, not a fixed formula.
- No default word-count target; preserve reasoning and compress repetition.
- `WRITING_AUDIT_REPORT.docx` is a required visible output for Word delivery.
- Cross-conversation recovery is separate from SQLite runtime checkpointing and must be persisted/read back through the configured external task pointer.

## Validation policy

`main` is the executable source of truth, but v0.2 remains a candidate until at least one real article completes end-to-end, including a deliberate interruption/resume, Word render/mechanical QA, semantic red-team and visible audit report.
