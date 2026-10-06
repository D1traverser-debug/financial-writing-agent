# Financial Writing Agent v0.2

A deterministic A-share financial-writing runtime for research-heavy formal articles and image-first WeChat sticker posts.

## Identity
- Repository: `D1traverser-debug/financial-writing-agent`
- Canonical branch: `main`
- Python package: `financial_writing_agent`
- CLI: `financial-write`
- Skill: `financial-writing-agent`

## Runtime
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Failures or unavailable mandatory dependencies route to `BLOCKED`; there is no silent free-form fallback.

## Core behavior
- Unspecified formal-article destination → `DUAL`.
- `DUAL` = one broad/deep research base + independently edited `FINANCE_DEEP` and `FINANCE_BROAD` articles.
- Default formal language = Simplified Chinese financial prose.
- Default formal delivery = `WORD_FILE_ONLY`.
- New Word articles enable publication visuals by default unless explicitly disabled or the task concerns an existing document.
- Formal hierarchy is normalized to `一、二、三 → （1）（2）（3） → ①②③`.
- A dedicated anti-AI/style judge must pass before general editorial audit can pass.
- Public financial output requires a concise but materially complete risk warning/disclaimer.
- Completion returns Word artifact(s), `WRITING_AUDIT_REPORT.docx`, visual manifest when applicable, and a visible completion checklist.

## Cognition and connected knowledge
Research is deliberately broader/deeper than the article. It covers catalyst, concept map, industry chain, A-share universe, fundamentals, why-this/why-not, market selection and relevant short-term roles/signals.

Connected Notion/Drive/StockBase/EventBase access is orchestrated by ChatGPT with the actual connector, not impersonated by the standalone Python process. Retrieved references are recorded with `record_knowledge_context`; reusable writeback receipts are recorded with `record_knowledge_writeback` before final audit when available.

## Visual delivery
Creative generation stays model-side. Runtime accepts a validated `VisualPackage`, records `VISUAL_MANIFEST.json`, and deterministically inserts assets into Word. Formal article defaults: 16:9 hero + semantic section images at roughly one per 700 Chinese characters, centered and uncropped. Image copy may use a shorter hook rather than repeating the section heading. The user's approved avatar is treated as a small integrated circular element when required by the task profile.

## WeChat sticker posts
Explicit 微信贴图 requests route to `WECHAT_STICKER_POST`, not DUAL. The draft carries a current `PlatformConstraintSnapshot` with verification time and source references. Remembered title/body/image limits are not hard-coded; numeric limits are enforced only when current evidence supplies them. Output is `WECHAT_STICKER_POST.docx` plus the visual manifest when visuals are enabled.

## MCP surface
The hosted/plugin-facing runtime exposes 15 tools covering task recovery, connected-knowledge receipts, research/editorial stages, a dedicated style audit, visual package submission, deterministic delivery/mechanical audit, knowledge writeback receipt and final audit.

## Validation policy
`main` is executable truth. Clean CI must pass SDK smoke, MCP HTTP smoke, unit/trajectory tests, executable contract evals, static ownership audit and real DOCX render smoke. v0.2 still remains a candidate until a user-authorized real article E2E runs through the live model chain and a deliberate interruption/recovery.
