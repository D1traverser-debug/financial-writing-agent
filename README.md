# Financial Writing Agent v0.4

A deterministic A-share financial-writing runtime with material-complete deep analysis, multi-hypothesis market explanation, dedicated Hook and Natural Authorial Prose audits, and Word delivery.

## Core behavior
- `FINANCE_DEEP`: material-complete within the bounded audited research universe.
- `FINANCE_BROAD`: traffic-oriented selective compression with evidence boundaries preserved.
- Publication content: Word only; no article body in chat.
- QA: `WRITING_AUDIT_REPORT.docx` plus a visible chat checklist.
- No tables.
- No image, cover, section-visual, avatar or sticker workflow.
- Numbering hierarchy: `一、二、三 → （1）（2）（3） → ①②③`.
- Bold skim path: title + H1s + bold spans must reconstruct the main line.

## Market Explanation Completeness
For stock/theme/price-reaction topics, separate economic benefit from market selection/price formation. Use competing explanations rather than a fixed hindsight chain. Grade material explanations as:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

FINANCE_DEEP preserves material `why_this / why_not`, continuation and exhaustion/reversal conditions, counterevidence and unresolved boundaries.

## Hook Gate
Independently audit cross-finance title clickability, current WeChat search intent, the first three sentences, H1 continuation power, paragraph forward pull and title/opening payoff.

## Natural Authorial Prose Gate
Do not optimize for AI-detector evasion. Audit template fingerprint, discourse variability, semantic progression, transition continuity, repetition control, rhythm naturalness, concrete evidence density, reader modeling, narrative flow, authorial specificity, uncertainty calibration and extreme-language control.

## Word typography
- H1: `24px = 18pt`
- H2: `20px = 15pt`
- Body: `18px = 13.5pt`
- H3: `12pt`

Typography drift and tables are Mechanical Hard Fail conditions.

## Runtime and legacy policy
The only public MCP implementation is `financial_writing_agent/plugin_server.py`; `runtime_service.py` owns business operations. v0.4 is a hard cutover: there is no compatibility shim, no legacy `CHAT_TEXT` delivery contract, and no visual/sticker contract on `main`.

`main` is code/rule truth. Promotion requires SDK/MCP smoke, unit/trajectory/static checks, contract evaluation, isolated wheel install and DOCX render smoke.
