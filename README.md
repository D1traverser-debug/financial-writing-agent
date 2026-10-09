# Financial Writing Agent v0.3

A deterministic A-share financial-writing runtime for research-heavy formal articles with mode-specific completeness, dedicated hook/human-voice audits and publication-ready Word delivery.

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
- Unspecified destination → `DUAL`.
- `FINANCE_DEEP` = bounded research universe with **material-complete expression**; it may compress repetition/immaterial detail but not omit material branches for elegance or brevity.
- `FINANCE_BROAD` = traffic-oriented selective expression around 1–3 core contradictions/information gaps while preserving full support for retained claims.
- Default formal language = Simplified Chinese financial prose.
- Publication content = **Word only**; do not paste article body/preview in chat.
- QA = `WRITING_AUDIT_REPORT.docx` + visible chat checklist/list.
- No image, cover, section-visual, avatar or sticker-post workflow exists in Financial Writing.
- Publication articles contain **no tables**.
- Formal hierarchy is normalized to `一、二、三 → （1）（2）（3） → ①②③` and used frequently when the reasoning contains real layers/categories/steps.
- Key terms, key numbers and selected key judgment sentences form an explicit bold skim path; company/stock names are bold on every occurrence.
- Public financial output requires a concise, topic-specific risk warning/disclaimer.

## Dedicated Hook Gate
Hook quality is independently audited on the frozen draft:
- total-title cross-finance clickability;
- current WeChat search-intent consideration with real evidence refs;
- first three complete sentences;
- H1 continuation power;
- paragraph forward pull;
- title/opening payoff.

Formal modes generate 8–12 headline candidates. Current search terms are researched per task rather than stored as a permanent keyword list; exact search volume is never invented.

## Dedicated Human Voice Gate
A separate Human Voice Judge audits:
- template fingerprints;
- transition continuity;
- repetition;
- rhythm naturalness;
- reader dialogue / 交流感;
- reasoning narrative / 娓娓道来;
- visible author judgment/persona;
- extreme-language control.

“Human” never means adding slang, typos, random fragments or decorative filler.

## Reader/completion design
The current audience profile supplied by the user skews older (45 common, substantial 55+). The runtime therefore favors strong visible hierarchy, frequent meaningful numbering, readable paragraph density, clear referents and a bold skim path while preserving analytical depth.

The final substantive section must still add information or close an earlier question/causal loop; recap-only mechanical endings are discouraged.

## Cognition and connected knowledge
Research remains deliberately broad/deep: catalyst, concept map, industry chain, relevant A-share universe, fundamentals/business stage, why-this/why-not, counterevidence, market selection and relevant short-term roles/signals. At least two materially different sweeps are required with an auditable stop reason.

Connected Notion/Drive/StockBase/EventBase access is orchestrated by ChatGPT with the actual connector. Retrieved references are recorded with `record_knowledge_context`; reusable writeback receipts are recorded with `record_knowledge_writeback` before final audit when available.

## MCP surface
The hosted/plugin-facing runtime exposes task recovery, research/editorial stages, a dedicated Hook Gate, a dedicated Human Voice Gate, deterministic Word delivery/mechanical audit, knowledge writeback receipt and final red-team audit. There is no visual-package tool.

## Validation policy
`main` is code/rule truth. Promotion requires SDK/MCP smoke, unit/trajectory/static checks, contract evaluation and real DOCX render smoke. A documentation change alone is not proof that the Agent executes the behavior.