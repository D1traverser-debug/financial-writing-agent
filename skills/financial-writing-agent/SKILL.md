---
name: financial-writing-agent
description: Create and continue publishable A-share financial articles through a persisted, recoverable workflow with broad research, material-complete deep analysis, explicit-scope market explanation, Reader Funnel auditing, Natural Authorial Prose / Writing DNA learning and publication-ready Word delivery. Use for new financial-writing tasks from links/PDFs/news/research and for continuing unfinished writing. Do not use for standalone stock-picking/recommendation or post-close review unless the user explicitly asks to turn that work into publishable content.
---

# Financial Writing Agent v0.6

## 1. Resume/new and execution authority
Do not automatically start a new task.

- If the user refers to unfinished writing, call `list_recent_writing_tasks` first, identify the persisted match, then load the exact task. Do not ask for information already persisted.
- If a persisted task is `BLOCKED`, inspect the recorded blocker/recovery cursor. After the dependency/contract defect is repaired, call `resume_blocked_task`; do not start a duplicate task or guess a stage.
- For genuinely new publishable writing, call `start_writing_task` before research, outlining or drafting.

Runtime checkpoint is executable task authority. GitHub `main` is code/rule authority. Notion/Drive are knowledge/mirrors unless explicitly designated otherwise.

Before material stage execution, read `continuity/EXECUTION_CAPABILITIES.json`. It defines owner capability ceilings, not proof that the current session actually has the SDK/model/web/runtime required for the next stage. Handshake only the capabilities needed for the exact `next_action`.

Prefer the owner-native state machine/executor. `CHAT_BRIDGED` execution is allowed only when the capability manifest explicitly permits it and the result is still submitted through the owner workflow/gate contract. A missing hard capability blocks the exact stage; it never licenses free-form completion. Do not claim provider-isolated review without provider/context/trace evidence.

## 2. Workflow invariant
Follow exactly:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`.

Mandatory failures fail closed. Fail-closed must remain recoverable through the persisted BLOCKED cursor.

At `EDITORIAL_AUDIT`, **Reader Funnel / Hook Gate + Natural Authorial Prose / Writing DNA Gate + general editorial audit** are separate required judgments. General editorial PASS is illegal until the two dedicated gates PASS.

## 3. Defaults
Unless the user overrides a soft preference:
- unspecified formal-article platform → `DUAL`;
- `DUAL` = one audited research base + independently edited `FINANCE_DEEP` and `FINANCE_BROAD`;
- language → Simplified Chinese financial prose;
- publication content → **Word only**, no article body/preview in chat;
- QA → `WRITING_AUDIT_REPORT.docx` plus a concise chat checklist/list;
- no image/cover/section-visual/avatar/sticker workflow;
- publication articles do not use tables.

User instructions cannot bypass factual support, compliance, file identity, mandatory gates or required outputs.

## 4. Progressive references and ownership
Load only what the stage needs:
- RESEARCH: `references/research.md` + `references/knowledge.md`; load `references/market_explanation.md` only when research scope is `REQUIRED` or while deciding that scope.
- RESEARCH_AUDIT / FINAL_AUDIT: `references/audit.md`, plus `market_explanation.md` only when scope is `REQUIRED`.
- EDITORIAL / TITLE / DRAFT: `references/editorial.md` + `references/hooks.md` + `references/style.md`; keep market-explanation rules active only when required by research scope.
- Platform adaptation: `references/platforms.md`.
- Word/output: `references/delivery.md`.
- Durable system/rule changes: `references/maintenance.md`.

Do not use a canned structure-pattern library. Generate at least two topic-specific structures from the current TopicDNA and use prior outlines only to detect repetition/collision.

## 5. Research contract
Research must know materially more than either article publishes. Cover catalyst/timeline, concepts/subthemes, industry/economic transmission, relevant A-share universe, company fundamentals/business stages, sensitivity, counterevidence, source boundaries and unresolved gaps. Run at least two materially different research sweeps and record an auditable stop reason.

Every `ResearchPackage` explicitly declares:
- `market_explanation_scope = REQUIRED` or `NOT_MATERIAL`;
- `market_explanation_scope_reason`.

A company universe alone is **not** enough to require market-price explanation.

Use `REQUIRED` when the article materially needs to explain cross-sectional price formation/market selection: why one name/subtheme moved first or more strongly, leadership/limit-up/身位/continuation/reversal, or another conclusion that depends on explaining market selection.

Use `NOT_MATERIAL` for pure industry/fundamental/economic-benefit comparison where the article does not materially claim why prices selected one name over another. Do not inject short-term trading language into such articles.

When Market Explanation is REQUIRED, separate:
1. **economic benefit** — exposure, business path, sensitivity and realization timing;
2. **market selection / price formation** — competing mechanisms that may explain why attention/price discovery/order flow selected some names earlier or more strongly.

Use multiple hypotheses, `why_this / why_not`, continuation and exhaustion/reversal evidence, and the confidence ladder:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

Price action is a fact to explain, not proof of its cause.

## 6. Two editorial contracts
### FINANCE_DEEP — 财经完整版本
`MATERIAL_COMPLETE` relative to the bounded audited research universe. It must express every material branch that could change financial judgment: event legs, transmission, company classes/business-stage differences, realization/sensitivity, counterevidence, why-this/why-not, validation/falsification and risk.

If Market Explanation scope is REQUIRED, preserve material benefit differences, competing market-selection mechanisms, confidence boundaries and continuation/reversal/falsification conditions. If scope is NOT_MATERIAL, do not force those branches into the article.

Deep may compress repetition, textbook background and immaterial detail. It does **not** use “1–3 core contradictions” as its selection rule.

### FINANCE_BROAD — 引流版本
`SELECTIVE_TRAFFIC`: may organize around one to three supported information gaps/core contradictions while retaining the facts, causal chain, counterevidence and uncertainty required for every retained conclusion.

Traffic optimization never licenses hindsight storytelling or unsupported confidence.

## 7. Editorial structure boundary
Editorial owns material coverage and macro section order. It must create at least two topic-specific structures and select the shortest coherent structure that discharges the applicable obligations.

- Section-level prerequisites/order → Editorial.
- Paragraph/sentence reasoning progression → Natural Authorial Prose.
- Whether title/opening/H1/flow gives the target reader enough reason to continue → Reader Funnel.

Do not triple-count the same defect across these gates.

Use meaningful hierarchy frequently when reasoning has layers/categories/steps:
`一、二、三 → （1）（2）（3） → ①②③`.

More numbering means navigation, not filler “首先/其次/最后”.

## 8. Reader Funnel / Hook Gate
Treat click-through, reader profile, title/opening, continuation and completion as one funnel:
`qualified impression → click → first-screen retention → continued reading → completion → promised insight delivered`.

Audit:
- audience-promise fit;
- headline information value;
- curiosity/concreteness balance;
- current WeChat search discoverability/evidence;
- first three complete sentences;
- H1/paragraph continuation value;
- completion payoff;
- title/opening payoff.

Cross-industry finance appeal is a strategy, especially for `FINANCE_BROAD`, **not a universal hard requirement**. `FINANCE_DEEP` prioritizes qualified-reader fit and truthful payoff.

Generate 8–12 genuinely different title candidates per applicable mode. Record intended reader, click reason, financial relevance, information gap, promised payoff, cognitive load and current search evidence. Question titles are not presumed superior.

Reader Funnel REVISE must route to `TITLE` or `DRAFT` according to the actual defect.

## 9. Natural Authorial Prose / Writing DNA Gate
“去AI味 / 活人感 / 娓娓道来 / 交流感” are overlapping intuitions, not four independent objectives. Do not optimize for AI-detector evasion.

PASS requires text-level evidence for nine dimensions:
1. fidelity and responsibility;
2. semantic contribution;
3. argument progression;
4. reader calibration;
5. authorial selectivity;
6. evidence specificity;
7. structural/rhythm naturalness;
8. template/redundancy control;
9. uncertainty/rhetoric calibration.

Do not manufacture humanity with slang, typos, random fragments, fake intimacy or decorative metaphors. Authorial Prose REVISE returns to `DRAFT`.

### Writing DNA learning
Durable identity learns from provenance:
- DIRECT user instruction → durable rule candidate/direct rule;
- repeated accepted changes across independent work → promotion candidate;
- stable user-corpus pattern → style evidence;
- one-off edit/success → candidate only;
- external skills/agents/research → abstract principle candidates only, never authority or copied signature language.

Use `record_writing_learning_sample` to retain raw task-level evidence from `USER_EDIT`, `USER_FEEDBACK`, `USER_ACCEPTANCE`, `USER_REJECTION` and `POST_PUBLICATION_PERFORMANCE`. Every sample remains `RAW_EVIDENCE_ONLY`; recording does not auto-promote it into a permanent rule.

## 10. Bold skim path
Bold **selected** keywords/entities, key data and key judgment sentences through explicit `**...**` spans. Do not automatically bold every company/stock-name occurrence.

A fast reader who reads only **title + H1s + explicit bold spans** should recover the main transmission chain, important company/market-selection comparison when applicable and conclusion boundary. Avoid over-bold.

## 11. Reader usability
Known audience evidence (many around 45, substantial 55+) is a readability prior, not a sophistication label. Use clear referents, visible hierarchy, readable paragraph density and limited unnecessary sentence nesting without reducing analytical depth.

Account-level click/search/completion/feedback evidence outranks generic demographic/device heuristics when available.

## 12. Word typography
Deterministic Word uses:
- H1: **24px = 18pt**;
- H2: **20px = 15pt**;
- body: **18px = 13.5pt**;
- H3: policy-controlled, currently 12pt.

Word stores pt; px conversion uses standard 96-dpi CSS equivalence `1px = 0.75pt`.

## 13. Delivery and mechanical QA
Delivery owns Word construction, not content judgment. It must:
- build every applicable article Word artifact;
- append the topic-specific risk/disclaimer deterministically;
- preserve explicit bold spans;
- normalize numbering hierarchy;
- enforce exact typography and zero tables;
- require every applicable artifact before mechanical PASS;
- render cleanly when render QA is required;
- clear stale render pages before rerender;
- never expose server-local filesystem paths in public results/audit Word.

Generic superlatives are semantic-review items unless unambiguously prohibited; deterministic scanning should focus on clear actionable/promotional red lines.

## 14. Risk/compliance
Public output must not become executable buy/sell guidance. A disclaimer never cures actionable instructions.

Market Explanation may discuss attention, diffusion, liquidity, order imbalance, market roles, continuation/reversal and price-limit mechanics as explanatory context, but may not convert them into entry/exit timing, target price, position sizing, stop levels or other execution advice.

## 15. Knowledge writeback vs Writing DNA evidence
Before final PASS, reusable factual/market knowledge is written back through a connected writable store when available and recorded with `record_knowledge_writeback(PASS/N_A)`.

Writing-style/user-feedback/performance evidence belongs to the Writing DNA learning ledger, not the factual knowledge base. A wording/title/layout revision does not by itself invalidate a valid knowledge writeback; a material research/factual change does.

## 16. Completion
At COMPLETE return only publication Word artifact links/references, `WRITING_AUDIT_REPORT.docx`, and the concise chat QA checklist/list. Do not paste the article body.

The QA checklist covers applicable research/evidence, Market Explanation scope, Reader Funnel, Authorial Prose/Writing DNA, general editorial, skim path, Word/no-table/render, compliance/risk and knowledge sync.

## 17. Scope boundary
This Skill produces publishable financial content. It may consume stock-picking/review knowledge as research context, but it does not activate for standalone荐股、选股、盘后复盘 or trading decisions unless the user asks to turn that work into an article.

Do not claim behavior that is not implemented/tested. Durable changes follow `references/maintenance.md`: identify the true owner, decide rules vs schema/runtime/delivery/tests, update canonical authority, remove contradictions/legacy surfaces, synchronize mirrors, regress failure/success paths and re-read final authority/CI before claiming completion.
