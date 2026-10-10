# Financial Writing Agent v0.7

A deterministic A-share financial-writing runtime with material-complete deep analysis, explicit-scope market explanation, recoverable checkpoints, a unified Reader Funnel, Natural Authorial Prose / Writing DNA assurance, raw learning-evidence capture and Word-only delivery.

## Core behavior
- `FINANCE_DEEP`: material-complete within the bounded audited research universe.
- `FINANCE_BROAD`: selective traffic-oriented compression while preserving evidence and uncertainty boundaries; title/opening must expose a non-niche financial stake so readers do not need pre-existing sector interest.
- Multi-company topics preserve complete material coverage in Deep and leave an evidence-based company comparison map rather than an undifferentiated basket.
- Publication content: Word only; article body is not pasted into chat.
- QA: `WRITING_AUDIT_REPORT.docx` plus a concise visible chat checklist.
- No publication tables, no underlines, no publication-tail source appendix, and no image/cover/section-visual/avatar/sticker workflow.
- Final risk disclaimer is one inline italic `风险提示：...` paragraph.
- Numbering hierarchy: `一、二、三 → （1）（2）（3） → ①②③`.
- Bold skim path uses explicit selected anchors; company names are not blanket-bolded on every occurrence.

## Market Explanation scope
Every ResearchPackage explicitly declares `market_explanation_scope` as `REQUIRED` or `NOT_MATERIAL` with a reason. A company universe alone does not activate price-formation analysis.

Use `REQUIRED` when the article materially explains market selection, leadership, price reaction, continuation/reversal or another cross-sectional price-formation question. When active, separate economic benefit from market selection, compare competing mechanisms, preserve `why_this / why_not`, continuation/reversal conditions and causal confidence:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

## Reader Funnel
CTR, title hooks, reader profile, first-screen retention, continuation and completion are one funnel:
`qualified impression → click → first-screen retention → continued reading → completion → promised insight delivered`.

Cross-industry finance appeal is optional and mode-sensitive rather than a universal hard title rule. `FINANCE_BROAD` instead has a cold-reader requirement: the title/opening must make the relevant money/profit/orders/cash-flow/capital-allocation/company-differentiation stake legible without assuming prior interest in the niche sector. Current WeChat search evidence remains part of formal headline selection.

## Company comparison without covert recommendations
For multi-company topics, the editorial contract compares relevant names/classes on evidence-bounded dimensions such as current order visibility, realization speed, earnings sensitivity, validated overseas exposure and technology optionality. It may express research order or evidence strength, but cannot become a buy/sell list, price-performance ranking, entry/exit plan or euphemistic attempt to evade the same boundary.

## Natural Authorial Prose / Writing DNA
The independent prose gate audits nine consolidated dimensions: fidelity/responsibility, semantic contribution, argument progression, reader calibration, authorial selectivity, evidence specificity, structural/rhythm naturalness, template/redundancy control and uncertainty/rhetoric calibration.

Argument progression now explicitly includes **major-section bridges**: one H1 should create the reason for the next through cause, consequence, chronology, comparison, narrowing, correction or inference rather than a generic transition phrase.

`record_writing_learning_sample` stores raw task-level evidence from user edits, feedback, acceptance/rejection and post-publication performance. A single sample is `RAW_EVIDENCE_ONLY` and never auto-promotes itself into a durable rule.

## Recoverable fail-closed runtime
Mandatory failures route to `BLOCKED` with a persisted recovery cursor. After the blocker is repaired, `resume_blocked_task` resumes the exact saved stage instead of starting a duplicate workflow or falling back to free-form writing.

Changes to research, editorial plans, titles or drafts invalidate the affected downstream evidence and stale artifacts. Material research changes also invalidate prior factual knowledge-writeback decisions.

## Word contract
- H1: `24px = 18pt`
- H2: `20px = 15pt`
- Body: `18px = 13.5pt`
- H3: currently `12pt`
- zero publication tables
- zero underlines
- no end-of-article `资料来源 / 参考资料 / 参考来源 / 来源汇总` appendix; evidence remains in Research/Audit and material source identity is attributed naturally in prose
- one final italic `风险提示：...` paragraph, with no numbered risk H1
- deterministic numbering and explicit bold preservation
- required artifact presence before Mechanical PASS
- stale render pages cleared before rerender
- no server-local filesystem paths in public artifact contracts or audit Word

## Runtime surface
`financial_writing_agent/plugin_server.py` is the single public MCP registration surface. v0.7 exposes 17 typed tools and one Word resource template, including `resume_blocked_task` and `record_writing_learning_sample`.

There is no compatibility shim, legacy `CHAT_TEXT`, visual/sticker contract or canned `structure_patterns.md` library on current `main`.

`main` is code/rule truth. Promotion requires SDK/MCP smoke, unit/trajectory tests, executable contract evals, static authority/version checks, isolated wheel install and DOCX render smoke.
