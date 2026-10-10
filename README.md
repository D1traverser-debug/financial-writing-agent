# Financial Writing Agent v0.5

A deterministic A-share financial-writing runtime with material-complete deep analysis, multi-hypothesis market explanation, a unified Reader Funnel, Natural Authorial Prose / Writing DNA learning, and Word delivery.

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

## Reader Funnel / Hook Gate
Treat CTR, title hooks, reader profile, first-screen retention, H1/paragraph continuation and completion as one funnel:
`qualified impression → click → first-screen retention → continued reading → completion → promised insight delivered`.

Audit audience-promise fit, headline information value, curiosity/concreteness balance, current WeChat search discoverability, the first three sentences, continuation flow, completion payoff and title/opening payoff.

Cross-industry finance appeal is a strategy, especially for `FINANCE_BROAD`, not a universal hard title requirement. `FINANCE_DEEP` prioritizes qualified-reader fit and truthful payoff over maximum imagined reach.

## Natural Authorial Prose / Writing DNA Gate
Do not optimize for AI-detector evasion. Treat “去AI味 / 活人感 / 娓娓道来 / 交流感” as overlapping symptoms of one authorial-writing system.

Audit nine consolidated dimensions: fidelity/responsibility, semantic contribution, argument progression, reader calibration, authorial selectivity, evidence specificity, structural/rhythm naturalness, template/redundancy control and uncertainty/rhetoric calibration.

Writing DNA learns with provenance:
- explicit durable user instruction → direct rule;
- repeated accepted changes across independent work → durable candidate;
- stable patterns from a broad user corpus → style evidence;
- one-off edits/successes → candidate only;
- external skills/research → principle candidates only, never authority or signature-phrase copying.

Account-level click/search/completion data outranks generic demographic assumptions when available.

## Word typography
- H1: `24px = 18pt`
- H2: `20px = 15pt`
- Body: `18px = 13.5pt`
- H3: `12pt`

Typography drift and tables are Mechanical Hard Fail conditions.

## Runtime and legacy policy
The only public MCP implementation is `financial_writing_agent/plugin_server.py`; `runtime_service.py` owns business operations. v0.5 remains a hard cutover: there is no compatibility shim, no legacy `CHAT_TEXT` delivery contract, and no visual/sticker contract on `main`.

`main` is code/rule truth. Promotion requires SDK/MCP smoke, unit/trajectory/static checks, contract evaluation, isolated wheel install and DOCX render smoke.
