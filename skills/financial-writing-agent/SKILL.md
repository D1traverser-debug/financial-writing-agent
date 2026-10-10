---
name: financial-writing-agent
description: Create and continue publishable A-share financial articles through a persisted, recoverable workflow with class-accounted research, material-complete deep analysis, explicit-scope market explanation, Reader Funnel auditing, Natural Authorial Prose / Writing DNA learning and publication-ready Word delivery. Use for new financial-writing tasks from links/PDFs/news/research and for continuing unfinished writing. Do not use for standalone stock-picking/recommendation or post-close review unless the user explicitly asks to turn that work into publishable content.
---

# Financial Writing Agent v0.7

## 1. Resume/new and execution authority
Do not automatically start a new task.

- If the user refers to unfinished writing, call `list_recent_writing_tasks` first, identify the persisted match, then load the exact task. Do not ask for information already persisted.
- If a persisted task is `BLOCKED`, inspect the recorded blocker/recovery cursor. After the dependency/contract defect is repaired, call `resume_blocked_task`; do not start a duplicate task or guess a stage.
- For genuinely new publishable writing, call `start_writing_task` before research, outlining or drafting.

Runtime checkpoint is executable task authority. GitHub `main` is code/rule authority. Notion/Drive/StockBase/ArticleBase are research/knowledge inputs or mirrors unless explicitly designated otherwise; they must not restore an older writing controller, QA contract or task pointer over the current GitHub runtime.

Before material stage execution, read `continuity/EXECUTION_CAPABILITIES.json`. It defines owner capability ceilings, not proof that the current session actually has the SDK/model/web/runtime required for the next stage. Handshake only the capabilities needed for the exact `next_action`.

Prefer the owner-native state machine/executor. `CHAT_BRIDGED` execution is allowed only when the capability manifest explicitly permits it and the result is still submitted through the owner workflow/gate contract. A missing hard capability blocks the exact stage; it never licenses free-form completion.

## 2. Workflow invariant
Follow exactly:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`.

Mandatory failures fail closed. Fail-closed must remain recoverable through the persisted BLOCKED cursor.

At `EDITORIAL_AUDIT`, **Reader Funnel / Hook Gate + Natural Authorial Prose / Writing DNA Gate + general editorial audit** are separate required judgments. General editorial PASS is illegal until the two dedicated gates PASS.

Semantic PASS requires an evidenced **independent stage-bound judge run**. `CHAT_SELF_REVIEW` may identify defects, but it may not certify Research Audit, Reader Funnel, Authorial Prose, General Editorial or Final Audit as PASS. If the current session cannot run the required judge, report QA as incomplete instead of claiming COMPLETE.

## 3. Defaults
Unless the user overrides a soft preference:
- unspecified formal-article platform → `DUAL`;
- `DUAL` = one audited research base + independently edited `FINANCE_DEEP` and `FINANCE_BROAD`;
- language → Simplified Chinese financial prose;
- publication content → **Word only**, no article body/preview in chat;
- QA → `WRITING_AUDIT_REPORT.docx` plus a concise chat checklist/list;
- no image/cover/section-visual/avatar/sticker workflow;
- publication articles do not use tables;
- publication articles do not use underlines;
- publication articles do not append a `资料来源 / 参考资料 / 参考来源 / 来源汇总` tail section; provenance stays in research/audit and material source identity is attributed naturally in prose;
- the final risk disclaimer is one inline *italic* paragraph beginning `风险提示：`, not a numbered H1.

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

For every company/theme topic, build a **Universe Coverage Ledger before narrowing to familiar names**:
- enumerate every economically material value-chain class;
- recall A-share candidates class by class using at least two materially different recall sources;
- classify each researched company as `MATERIAL / SECONDARY / REFERENCE_ONLY` and bind it to `value_chain_class`;
- record included, excluded and unresolved candidates plus evidence refs and stop reason;
- use `COMPLETE` only after class-level reconciliation; otherwise preserve `BOUNDED_WITH_GAPS`.

A second search about the same two or three stocks is not universe saturation. Do not let easier disclosures or a cleaner narrative silently remove a material company/class.

Every `ResearchPackage` explicitly declares:
- `market_explanation_scope = REQUIRED` or `NOT_MATERIAL`;
- `market_explanation_scope_reason`.

A company universe alone is **not** enough to require market-price explanation.

When Market Explanation is REQUIRED, separate economic benefit from market selection/price formation, use multiple hypotheses, `why_this / why_not`, continuation and reversal evidence, and the confidence ladder:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

Price action is a fact to explain, not proof of its cause.

## 6. Two editorial contracts
### FINANCE_DEEP — 财经完整版本
`MATERIAL_COMPLETE` relative to the bounded audited research universe. It is **not** a “挑几个代表股讲深” product.

It must express every material branch that could change financial judgment and carry explicit `company_coverage_obligations` from the Universe Coverage Ledger:
- every `MATERIAL` company must appear by name with an intelligible role/sensitivity/boundary;
- `SECONDARY` companies may be grouped by value-chain class only when grouping preserves the material distinction;
- `REFERENCE_ONLY` names need not be published;
- `BOUNDED_WITH_GAPS` research must remain visibly bounded rather than pretending exhaustive coverage.

If a Deep section says what to **watch / validate / falsify / track next**, its signals must map back to named stocks or clearly identified value-chain classes. A generic “看招标、看交付、看收入” checklist detached from the company universe fails.

For multi-company topics, Deep must additionally leave the reader with an evidence-based **company comparison decision map**. Compare material names/classes on relevant dimensions such as current order visibility, realization speed, earnings sensitivity, validated overseas exposure and technology optionality. It may state research order or evidence strength; it must not become a buy list or price-performance ranking.

If Market Explanation scope is REQUIRED, preserve material benefit differences, competing market-selection mechanisms, confidence boundaries and continuation/reversal/falsification conditions. If scope is NOT_MATERIAL, do not force those branches into the article.

### FINANCE_BROAD — 引流版本
`SELECTIVE_TRAFFIC`: may organize around one to three supported information gaps/core contradictions while retaining the facts, causal chain, counterevidence and uncertainty required for every retained conclusion.

The Broad reader should not need to care about the niche industry in advance. Title and first screen normally expose the broader financial stake—**money, orders, profits, cash flow, capital expenditure, company/asset differentiation or policy transmission**—before asking the reader to absorb sector detail.

For multi-company topics, Broad may compress the full Universe ledger but must still communicate a simple truthful differentiation (for example current visibility vs operating sensitivity vs overseas evidence vs longer-term option) rather than presenting an undifferentiated basket.

Traffic optimization may be more forceful than Deep in contrast and information-gap framing, but it never licenses fabricated urgency, unsupported confidence, hindsight storytelling or guaranteed-return language.

## 7. Editorial structure boundary
Editorial owns material coverage and macro section order. It must create at least two topic-specific structures and select the shortest coherent structure that discharges the applicable obligations.

- Section-level prerequisites/order → Editorial.
- Paragraph/sentence reasoning progression → Natural Authorial Prose.
- Whether title/opening/H1/flow gives the target reader enough reason to continue → Reader Funnel.

Do not triple-count the same defect across these gates.

Use meaningful hierarchy when reasoning has layers/categories/steps:
`一、二、三 → （1）（2）（3） → ①②③`.

For `FINANCE_DEEP`, lower-level numbering is conditionally mandatory when the article has several company classes, multiple realization stages, three or more comparison dimensions, multiple causal branches, or otherwise dense branching. Do not bury those branches in long unnumbered paragraphs. Do not force exactly three children per section; the logic determines the count.

Major H1 sections must also be **earned transitions**, not isolated research cards. The end of one section should create the reason for the next through cause, consequence, chronology, comparison, narrowing, correction, unresolved question or inference. Empty bridges such as “接下来我们来看” do not satisfy this requirement.

## 8. Reader Funnel / Hook Gate
Treat click-through, reader profile, title/opening, continuation and completion as one funnel:
`qualified impression → click → first-screen retention → continued reading → completion → promised insight delivered`.

Audit audience-promise fit, headline information value, curiosity/concreteness balance, **headline strategy diversity**, current WeChat search discoverability/evidence, first three complete sentences, H1/paragraph continuation value, completion payoff and title/opening payoff.

Cross-industry finance appeal remains optional; do not bolt unrelated macro themes onto a sector story. But `FINANCE_BROAD` must pass a **cold-reader test**: a finance reader with no prior sector interest should still understand from the title why the event may matter to money, profits, company differentiation or capital allocation.

Generate 8–12 genuinely different title candidates per applicable mode. Every candidate records an `angle_family`; the pool must contain at least five genuinely distinct supported families such as hard fact, profit/orders, supply-demand, company divergence, policy transmission, expectation gap, valuation/capital, global comparison, validation/risk, or market selection when applicable.

Unique strings are not enough. Pools dominated by one reusable shell such as “真正的X不在Y”“X又动了这次看什么”“别只看X要看Y”“拐点来了？” fail even if the nouns change.

The selected title should earn the click through topic-specific information, normally combining at least two of: concrete change/entity/event, financially consequential stake, real distinction/information gap. `FINANCE_BROAD` may use sharper truthful contrast and money language than Deep, but question titles and sensational adjectives are not presumed superior.

Reader Funnel REVISE routes to `TITLE` or `DRAFT` according to the actual defect.

## 9. Natural Authorial Prose / Writing DNA Gate
“去AI味 / 活人感 / 娓娓道来 / 交流感” are overlapping intuitions, not four independent objectives. Do not optimize for AI-detector evasion.

PASS requires text-level evidence for nine dimensions:
1. fidelity and responsibility;
2. semantic contribution;
3. argument progression, including earned major-section bridges;
4. reader calibration;
5. authorial selectivity;
6. evidence specificity;
7. structural/rhythm naturalness;
8. template/redundancy control;
9. uncertainty/rhetoric calibration.

Before semantic judgment, compute the deterministic **template-cluster guard**. Repeated staging families such as “真正的X不是Y而是Z / 如果只看 / 这正是 / 最值得写清楚 / 核心在于 / 值得注意的是 / 换句话说” are not banned individually, but a repeated/clustered pattern forces REVISE and cannot be waved through with “整体自然”.

Do not manufacture humanity with slang, typos, random fragments, fake intimacy or decorative metaphors. Authorial Prose REVISE returns to `DRAFT`.

### Writing DNA learning
Durable identity learns from provenance:
- DIRECT user instruction → durable rule candidate/direct rule;
- repeated accepted changes across independent work → promotion candidate;
- stable user-corpus pattern → style evidence;
- one-off edit/success → candidate only;
- external skills/agents/research → abstract principle candidates only, never authority or copied signature language.

Use `record_writing_learning_sample` for raw task-level evidence. Recording never auto-promotes a sample.

For a persisted writing task, any **material explicit user edit, feedback, rejection or acceptance that changes how the system should write, review or deliver** must be captured through `record_writing_learning_sample` (or an equivalent durable owner receipt) before the turn claims durable learning or closes the affected revision loop, unless an equivalent sample for the same evidence already exists. If the learning-evidence executor is unavailable, still obey the user's current revision request, but report that durable learning was not persisted; do not pretend the next chat has learned it.

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
- append the topic-specific risk disclaimer as one final *italic* paragraph beginning `风险提示：`, with no separate risk H1;
- preserve explicit bold spans;
- normalize numbering hierarchy;
- enforce exact typography, zero tables and **zero underlines**;
- prohibit publication-tail `资料来源 / 参考资料 / 参考来源 / 来源汇总` sections while preserving source provenance in research/audit and natural attribution when material;
- for branching/long Deep articles, mechanically require visible lower-level numbered navigation;
- require every applicable artifact before mechanical PASS;
- render cleanly when render QA is required;
- clear stale render pages before rerender;
- never expose server-local filesystem paths in public results/audit Word.

Generic superlatives are semantic-review items unless unambiguously prohibited; deterministic scanning should focus on clear actionable/promotional red lines.

## 14. Risk/compliance
Public output must not become executable buy/sell guidance. A disclaimer never cures actionable instructions.

A company comparison may explain operating evidence, current realization visibility, earnings sensitivity, validated overseas exposure, technology optionality and what future evidence would change the comparison. It may state a research order or evidence hierarchy. It must not use explicit or euphemistic language whose practical purpose is to tell the reader what to buy/sell, when to enter/exit, what target to use, how much to hold, or how to evade the same boundary through “首选/上车/重点配置” style phrasing.

Market Explanation may discuss attention, diffusion, liquidity, order imbalance, market roles, continuation/reversal and price-limit mechanics as explanatory context, but may not convert them into entry/exit timing, target price, position sizing, stop levels or other execution advice.

## 15. Knowledge writeback vs Writing DNA evidence
Before final PASS, reusable factual/market knowledge is written back through a connected writable store when available and recorded with `record_knowledge_writeback(PASS/N_A)`.

Writing-style/user-feedback/performance evidence belongs to the Writing DNA learning ledger, not the factual knowledge base. A wording/title/layout revision does not by itself invalidate a valid knowledge writeback; a material research/factual/universe change does.

## 16. Completion
At COMPLETE return only publication Word artifact links/references, `WRITING_AUDIT_REPORT.docx`, and the concise chat QA checklist/list. Do not paste the article body.

The QA checklist covers applicable research/evidence, Universe Coverage Ledger, Market Explanation scope, Reader Funnel/title-strategy diversity and Broad cold-reader stake, Authorial Prose/template/major-section bridge, Deep material-company completeness, company comparison usefulness, numbered navigation, general editorial, skim path, Word/no-table/no-underline/no-source-tail/risk-italic/render, compliance/risk, audit provenance and knowledge sync.

## 17. Scope boundary
This Skill produces publishable financial content. It may consume stock-picking/review knowledge as research context, but it does not activate for standalone荐股、选股、盘后复盘 or trading decisions unless the user asks to turn that work into an article.

Do not claim behavior that is not implemented/tested. Durable changes follow `references/maintenance.md`: identify the true owner, decide rules vs schema/runtime/delivery/tests, update canonical authority, remove contradictions/legacy surfaces, synchronize mirrors, regress failure/success paths and re-read final authority/CI before claiming completion.
