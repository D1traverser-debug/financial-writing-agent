---
name: financial-writing-agent
description: Create and continue A-share financial articles or image-first WeChat finance sticker posts through a compatible persisted MCP workflow, or through an explicit standalone Skill execution profile when the Runtime is unavailable or incompatible with the current Agent contract. Use for new financial-writing tasks from links/PDFs/news/research and for continuing an unfinished writing task. Do not use for standalone stock-picking/recommendation or post-close review unless the user explicitly asks to turn that work into publishable content.
---

# Financial Writing Agent

## 0. Choose and verify the execution profile before doing anything else
Do not begin research, outlining or drafting until the control plane is selected **and its capability contract is compatible**.

Tool presence alone does not make a Runtime authoritative. Before a new Runtime task begins, perform a cold-start capability/schema handshake against the current Skill invariants. At minimum, the available Runtime must not contradict:
- DUAL is deep-first, not parallel;
- `FINANCE_DEEP` can complete before `FINANCE_BROAD` derivation begins;
- Broad can be submitted through a phased `BROAD_DERIVATION`-equivalent path rather than requiring both mode plans/drafts up front;
- current research/evidence boundaries can be represented without dropping material source-completion, market-data capability or failure receipts;
- current editorial acceptance can preserve section-level promise/payoff/hierarchy obligations rather than silently discarding them.

Execution-profile rules:
- If Financial Writing Agent MCP Runtime tools are available **and compatible with the current Skill contract**, use `RUNTIME`. The MCP runtime checkpoint is the executable task authority.
- If the Runtime is unavailable/not deployed **or is present but contract-incompatible**, use `STANDALONE_SKILL` and load `references/standalone.md` before the task begins. Create its mandatory `ShadowTaskLedger` and record the unavailable/incompatible Runtime reason rather than pretending that no Runtime was checked.
- Do **not** choose standalone merely because a compatible Runtime is inconvenient.
- If incompatibility is discovered only after a Runtime task was already created, stop mixing control planes. Treat the Runtime task as blocked by version/capability mismatch. Do not import stale Runtime PASS receipts into standalone. Restart the user task under a fresh ShadowTaskLedger using only reusable research facts/evidence whose provenance remains valid, and record the mismatch as a `SYSTEM_ERROR` for maintenance.
- A normal tool/gate failure inside a **compatible** Runtime does not authorize silent fallback. Repair/resume the Runtime task or report it BLOCKED.
- In standalone mode, never invent MCP calls, task IDs, gate receipts, checksums or render resources. `STANDALONE_COMPLETE` is a disciplined self-audited completion state, not Runtime `COMPLETE`.

The standalone profile exists so a fresh conversation can execute this Agent without deployment while retaining explicit stage accounting, acceptance contracts, invalidation, evidence and completion barriers. It reduces drift but does not become deterministic simply because the rules are written down.

## 1. Decide resume vs new before doing anything else
- Under `RUNTIME`, explicit continuation intent such as “继续昨天那篇/接着写/刚才那篇” may restore an unfinished task through `list_recent_writing_tasks` → `get_writing_task`; a blocked task is repaired through `resume_writing_task` and resumed, not duplicated.
- Under `RUNTIME`, a genuinely new task starts with `start_writing_task` before research or drafting; do not inspect unrelated unfinished tasks just because they exist.
- Under `STANDALONE_SKILL`, a genuinely new task always starts with a fresh `ShadowTaskLedger`. Cross-conversation continuation requires an actual unambiguous prior checkpoint/artifact set.
- New work may reuse durable knowledge/experience, but must not inherit an old task's stage, blockers, selected title/outline, draft, artifacts, pending actions or next step. **Inherit learning, not unfinished work.**

Under Runtime the MCP checkpoint is task authority. Under standalone the current ShadowTaskLedger is only an in-session execution record and must not be overstated as durable Runtime state.

## 2. Workflow invariant
Single formal mode / sticker:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE/STANDALONE_COMPLETE`

DUAL:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL[FINANCE_DEEP] → TITLE[FINANCE_DEEP] → DRAFT[FINANCE_DEEP] → BROAD_DERIVATION[FINANCE_BROAD: EDITORIAL → TITLE → DRAFT] → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE/STANDALONE_COMPLETE`

### DUAL is deep-first, not parallel
`FINANCE_DEEP` is the analytical mother version. `FINANCE_BROAD` may begin only after the Deep draft and acceptance contract are frozen. Under Runtime, `BROAD_DERIVATION` reuses `submit_editorial_plan` → `submit_headlines` → `submit_draft`; under standalone the ShadowTaskLedger enforces the same sequence.

A revision targets the earliest valid stage and invalidates every dependent downstream PASS/artifact. Runtime enforces revision budgets; standalone self-counts them and blocks instead of silently resetting or looping.

## 3. Current defaults
Unless the user explicitly overrides a soft preference:
- unspecified formal platform → `DUAL`;
- language → Simplified Chinese financial prose;
- delivery → `WORD_FILE_ONLY`;
- direct chat only → `CHAT_TEXT`;
- explicit chat body + Word → `WORD_AND_CHAT`; Word mechanical/render/final-audit gates remain mandatory;
- new Word articles use the integrated visual workflow unless opted out or the task is only review of an existing document;
- Under `WORD_FILE_ONLY`, do not paste the article body into chat.

### Publication-density defaults
- Research may be exhaustive; writing should be the **shortest complete expression** of the material evidence and judgment.
- `FINANCE_DEEP`: preserve all independent facts/numbers/causal steps/comparisons that can change the conclusion, but remove repeated explanation, textbook background and generic filler. Roughly 6,000 Chinese characters triggers a density review; ~10,000 remains the hard ceiling, not a target.
- For a **complex thematic stock article** with several causal layers and roughly five or more material companies, use **6,000–9,000 Chinese characters as a diagnostic range, not a quota**. A Deep draft below roughly 5,500 characters is presumptively at risk of over-compression and must prove it did not drop causal bridges, counterevidence, `why_this / why_not`, realization-stage differences, current stock judgments or the mechanism connecting adjacent analytical layers.
- `FINANCE_BROAD`: optimize for click-through, first-screen retention, continuation and end-of-article reach. Preferred default is roughly **900–1500 Chinese characters**; default hard cap **1800**. Shorter is valid when the hook, one complete causal chain, decisive company/stock judgment and evidence/risk boundary remain intact.
- Formal hierarchy is `一、二、三 → （1）（2）（3） → ①②③`. Use it proactively when real logic exists: multi-block H1 → H2; H2 with three or more explicit evidence/condition/dimension units → H3 when helpful. Do not create decorative hierarchy, but do not hide real structure in walls of text.
- Word article title is **left-aligned**, not centered.
- Formal public-finance risk disclosure is mandatory under this Agent's publication policy but should use **minimum sufficient disclosure**: normally ~60–120 Chinese characters, with a configured hard cap. A disclaimer never legalizes actionable securities advice.

Explicit user instructions may override soft presentation preferences, but cannot bypass evidence support, compliance, required outputs, file identity or stage order.

## 4. Load stage references progressively
- `STANDALONE_SKILL`: `references/standalone.md` once before execution.
- RESEARCH: `references/research.md` + `references/knowledge.md` + `references/professional_analysis.md`.
- RESEARCH_AUDIT: `references/audit.md` + `references/professional_analysis.md`.
- EDITORIAL: `references/editorial.md` + `references/style.md` + `references/reader_value.md` + `references/professional_analysis.md`; use `references/structure_patterns.md` only after TopicDNA candidate structures exist, as a collision check rather than a template source.
- TITLE: everything required by EDITORIAL plus **`references/headline_craft.md`**. The title skill pack is mandatory for formal headline generation/selection rather than optional inspiration.
- DRAFT / BROAD_DERIVATION: everything required by EDITORIAL plus **`references/human_voice_craft.md`**; during Broad headline selection also load **`references/headline_craft.md`**.
- EDITORIAL_AUDIT: `references/audit.md` + `references/style.md` + `references/human_voice_craft.md` + `references/reader_value.md` + `references/professional_analysis.md`.
- FINAL_AUDIT: `references/audit.md` + `references/reader_value.md` + `references/professional_analysis.md` + **`references/human_voice_craft.md` + `references/headline_craft.md`** so the final reader-visible artifact is rechecked for human voice and title-promise payoff.
- Platform and post-publication experience: `references/platforms.md`; combine with `references/reader_value.md` only when interpreting reader/business value, not to invent platform rules.
- Visuals: `references/visuals.md`.
- Word/output/compliance: `references/delivery.md`.
- Durable changes/system errors: `references/maintenance.md`.

Do not dump every reference into every stage. The Runtime checkpoint or ShadowTaskLedger is the control plane; the references are the stage-specific cognition/rules.

## 5. Research before selection
Knowledge recall is an explicit pre-research decision: use relevant durable StockBase/EventBase/knowledge when actually accessible, record real refs, and reverify current/material claims. Under Runtime, a successful recall/context decision is recorded explicitly through `record_knowledge_context(status="PASS", ...)`; unavailable or blocked recall must be recorded with the appropriate non-PASS status rather than invented. StockBase remains READ ONLY; stable corrections go to the review queue.

Research must know materially more than the article says. Cover catalyst/timeline, concept graph, industry/economic transmission, relevant A-share universe, company fundamentals/realization stage, `why_this / why_not`, negative evidence/counterexamples, market-selection logic and relevant short-term roles/signals.

For recommendation-oriented or stock-comparison articles, **selection comes after research**. Build the material universe first and deeply verify every candidate that can change the ranking. Do not start from familiar names and rationalize them later.

User-supplied links/PDFs/reports/attachments are source obligations. Account for each material input as FULL/PARTIAL/UNAVAILABLE (or duplicate-original equivalent where supported); snippets/tool-success are not source completion.

Respect `effective_time_boundary`, omission/count checks and the `market_data_boundary`. Ordinary quote data does not authorize Level-2 order-book/tick/抢筹 claims. Core title/lead/H1/conclusion evidence cannot remain unresolved.

### Professional financial-analysis integrity
When a thesis spans layers, validate the applicable chain rather than jumping from a correct upstream fact to an unsupported stock conclusion:

`event/policy/technology/demand shock → industry variable → company exposure/competitive position → revenue/margin/earnings/cash-flow realization → valuation/expectation gap → market pricing/stock role`.

Each material arrow is a separate claim. Industry benefit is not automatically company profit; revenue is not profit; profit is not cash; a good company is not automatically a cheap stock; a positive fundamental change is not automatically an expectation surprise; a positive surprise does not guarantee price appreciation; market leadership is not proof of strongest fundamental realization. Reduce downstream conclusion strength when an intermediate link is unresolved.

For material financial/operating numbers, preserve enough definition to test comparability: entity/segment, period, unit/currency, actual versus preliminary/forecast/guidance, consolidated versus segment scope, gross versus net where material, ratio numerator/denominator, accounting-standard versus company-defined metric, source/date and material definition/restatement changes. Do not confuse YoY/QoQ, TTM/FY/forward periods, nominal/real growth, capacity/output/shipment/order/backlog/revenue, or mismatched peer metrics.

When earnings quality matters, inspect recurring versus one-off contribution, current PRC non-recurring-gain/loss treatment, cash/working-capital support and material accounting-estimate effects. When valuation/“超预期” is material, require a real valuation/expectation baseline and time boundary rather than decorative adjectives or invented consensus. Separate fundamental value, expectations, catalyst, current pricing and short-term liquidity/sentiment.

For material causal claims, test mechanism, intermediate observations, competing explanations and an observable falsification condition. Correlation or chronology alone is not causation.

## 6. Editorial, reader value, hooks, hierarchy and concrete application
Build TopicDNA before structure. Candidate structures come from the current topic, not a fixed “event → industry → stocks → market → next” template.

For DUAL, solve FINANCE_DEEP completely first: causal chain, actual company comparison, realization stage, market-selection logic, present stock judgments, counterevidence and risk boundary. Broad is then a controlled compression/repackaging: title/lead/order/density may change, but facts, evidence strength, decisive causal chain, ranking, stock judgment and risk boundary may not silently change.

### Reader value and commercial value
Before selecting structure, make the existing TopicDNA/editorial fields resolve: target reader, primary reader need, starting misunderstanding/question, the non-obvious information delta beyond source restatement, the concrete decision/understanding delta after reading, and the trust reason that makes the judgment worth relying on.

Professional depth is not fact count. A publishable article should contribute a material synthesis layer—such as a non-obvious causal link, definition/denominator correction, company divergence, `why_this / why_not` elimination, market-vs-fundamental mismatch, counterevidence that narrows a thesis, or another evidence-bounded perspective. Do not manufacture novelty when the evidence only supports a straightforward update.

Optimize the reader-value chain as `truthful acquisition → immediate information scent → sustained value density → useful perspective/judgment → completion → trust/repeat value`. Account-specific monetization, comments, follows, search or downstream inventory may be optimized only when current platform/account evidence makes them relevant; they never authorize clickbait, delayed payoff, manufactured controversy, keyword stuffing or weaker evidence/compliance.

At paragraph level, front-load the real job when feasible: do not routinely bury the decisive fact, number, comparison or conclusion at the end. Title + lead + headings + bold anchors + material paragraph openings should form a coherent scan path. This is a semantic standard, not a fixed sentence/paragraph-length formula; do not create choppy pseudo-web prose.

### No generic finance filler
Material analytical paragraphs should normally add a specific event/fact, number, mechanism, named company/stock, comparison, market role or present judgment. If a paragraph could be pasted into an unrelated sector article with only nouns changed, revise it.

When stocks matter, do not stop at “行业受益/政策催化/景气提升”. Show the actual transmission to companies/stocks: factual exposure, realization stage, narrative-only elements, current market role/身位 when supported, meaningful alternatives and why the relative judgment follows.

Do not turn professional-analysis checks into a generic six-section template. Use only the financial layers material to the current thesis. Technical detail that does not change the conclusion or help the reader test it should be cut.

### Hook engine
Treat hooks as a linked system:
1. headline hook earns the click truthfully;
2. first-screen/opening hook pays the click in the first 1–3 sentences;
3. every material H1 carries a continuation gap and payoff;
4. company/stock comparison may itself be the hook by resolving `why_this / why_not`, realization-stage or 身位 divergence.

Formal applicable modes generate 8–12 **genuinely different** headline mechanisms, not paraphrases. Each candidate stays inside the evidence boundary and records its factual anchor, reader stake, primary information gap, opening payoff and cognitive load.

At TITLE, the `headline_craft.md` pack is mandatory. Extract `HeadlineRawMaterial` before wording candidates, then run a destructive title tournament: reject candidates that fail accuracy, natural-reader interpretation, subject clarity, first-screen payoff, uniqueness or backstage-leak checks. Prefer **recognizable anchor + reader stake/tension + one valuable information gap + credible payoff signal**. A headline may withhold the answer; it must not withhold the subject or reason to care.

Do not select a title merely because it sounds more dramatic. The winner is the strongest truthful promise with enough information scent to be understood out of context and enough unresolved value to justify the click. Repeated headline skeletons are an AI/template smell even when each title is individually grammatical.

### H1 / H2 / H3 acceptance
Every H1 must advance a judgment, not act as a directory label. Freeze per-H1 `directional_conclusion`, `reader_gap`, `payoff_requirement`, `logical_blocks` and any real H3 requirement before drafting. Genuine multi-level logic should be surfaced through the formal Chinese hierarchy rather than hidden in dense paragraphs.

After structure/title selection, freeze the `WritingAcceptanceContract`. Drafts may not silently alter frozen title/structure/promises; revisions go back through the legal stage.

### Stock/company judgment must be current and explicit
When evidence is sufficient, do not substitute an observation checklist for a judgment. State what is confirmed, what remains expected, where the company sits in the economic realization chain, its current market role/身位 when supported, why it ranks ahead/behind meaningful alternatives, and the decisive limitation.

Avoid empty endings such as “接下来先看A再看B/后续继续观察/能否走出来还要看市场/值得关注/有待验证” when evidence already supports a present conclusion. Conditions/falsification points follow the judgment; they do not replace it.

If uncertainty is real, say exactly what is unknown, why, what concrete fact/data resolves it and how each outcome changes the judgment.

Keep confirmed fact, industrial/economic inference, market-traded expectation and rumor/hypothesis distinct.

## 7. Style and anti-AI
At `EDITORIAL_AUDIT`, run the independent style judge before general editorial audit. It checks template fingerprints, transition continuity, repetition, natural rhythm, extreme language, prompt/backstage leakage, empty hedge language and concrete application.

For public-facing long-form finance articles, default to the **NARRATIVE_FINANCE_EXPLAINER** house voice in `references/style.md` unless a memo/report tone is clearly more appropriate. This is not imitation of a named writer. It means:
- enter through a verified concrete situation/action/object/number/contradiction when useful;
- keep one live reader question/tension moving through the piece;
- move between concrete fact and abstraction rather than staying in jargon;
- introduce companies because the reasoning now needs them, not as rearrangeable profile cards;
- use dry/light humor only when it clarifies mechanism or reduces cognitive load;
- make major sections depend on one another so the article deepens instead of merely changing categories.

`human_voice_craft.md` is the mandatory execution pack for public-facing prose. Borrow only truth-safe craft from narrative nonfiction/fiction/essay writing: verified scene/action, selective detail, real friction, setup→complication→payoff, movement up/down the ladder of abstraction, authored judgment and responsive sentence rhythm. Never invent a scene, dialogue, inner thought or cinematic detail merely to sound human.

Run a **non-permutability check** on company passages and a **tic-density check** on long prose. If company blocks can be shuffled without changing the argument, or one rhetorical family (“不是X而是Y / 真正 / 核心 / 所以 / 如果…那么…”) repeats across many sections, revise rather than calling the prose human.

Before final release, run the finance **Fresh Reader blind pass** from `human_voice_craft.md` on reader-visible text only. It must identify the first real engagement point, likely exit points, productive curiosity versus confusion, checklist/report smell, repeated rhetorical devices, the most generic AI-like paragraph, the most memorable concrete detail and whether the author sounds like a real analyst with a point of view. A serious Fresh Reader failure is a DRAFT/EDITORIAL defect even if factual checks pass.

### Source invisibility
The published article should digest research material rather than expose the production process. Unless attribution itself is necessary for truthfulness or explicitly requested, keep backstage phrases such as “用户给的报告 / 原报告 / 原摘要 / 选股通认为 / 我们查到 / 我检索了 / 付费墙 / 抓取 / 工具限制” out of final prose. Evidence provenance remains in the research ledger/audit. This rule never authorizes plagiarism or removal of attribution when a named claim/source must be identified.

Do not “humanize” with random slang/fragments. Human quality means evidence-led prioritization, natural pacing, topic-specific choices, controlled humor, a recognizable authored voice and clear analytical judgment.

For FINANCE_BROAD, any paragraph that does not advance the hook, add an independent fact/mechanism, sharpen a company/stock comparison or change the conclusion should normally be cut. A Broad version is defective when it is merely shorter but still slow to reveal relevance, jargon-heavy or difficult to scan.

## 8. Risk/compliance
Every formal public-finance payload carries a separate `risk_disclaimer`. Delivery appends it deterministically. Keep it compact and materially sufficient; do not create a long boilerplate tail that harms completion.

The substantive compliance boundary is more important than the disclaimer: do not turn public content into executable buy/sell/hold guidance, position sizing, entry timing, target price, stop-loss or guaranteed-return language. A disclaimer cannot cure otherwise prohibited/regulated conduct.

Compliance applies to title, lead, H1, bold anchors, ending and interaction text as well as ordinary body prose.

## 9. Integrated visual workflow
When visuals are enabled, Runtime delivery uses `submit_visual_package` with real authorized ChatGPT file parameters; never invent server paths/URLs. Under standalone, use real available file/image capability and record actual assets.

Formal articles default to one 16:9 hero plus semantic section images at roughly one per 700 Chinese characters, with meaning taking priority over counting. Use the approved avatar as a small circular integrated element when required by the active visual profile.

## 10. Platform-specific work and performance learning
Explicit 微信贴图 uses `WECHAT_STICKER_POST`, not a shortened DUAL article. Verify current platform mechanics/limits at execution time; do not hard-code remembered numeric platform limits.

Connected platform/account experience may inform recommendation/click/search/retention packaging when relevant, but one viral or failed article is an experience sample, not a universal formula.

For FINANCE_BROAD, distribution optimization includes not just the click but **completion/end reach**. Do not add low-value background, repeated examples, ceremonial summaries or oversized disclaimers that delay the final payoff.

When real post-publication performance later becomes available, preserve it through the structured `ArticleExperienceSample` discipline in `references/platforms.md`: stable article identity, platform/account context, observation window, only actually available metrics, baseline/cohort when available, material confounders, qualitative reader feedback kept separate from behavioral metrics, hypothesis/confidence, and `promotion_status=SAMPLE_ONLY` by default. `0`, missing and unavailable are distinct; never invent metrics to fill gaps.

Do not promote one high/low performer or one reader comment into an algorithm law. The current Writing Agent does not expose an automatic cross-task causal-learning/promotion workflow; experience promotion remains platform/maintenance governance until an executable path exists.

## 11. Delivery and mechanical QA
Mechanical formatting is deterministic where possible. Article title is left-aligned. H1 is red/bold (~18pt); H2/H3 use Normal + bold; body ~12pt. Stock/company names supplied by research are bolded on every occurrence. Underline is not an article emphasis system.

`build_and_mechanically_audit_delivery` verifies required Word/output mechanics under Runtime. Under standalone, perform the equivalent observable checks with available tools and never convert “not checked” into PASS.

Mechanical QA checks title alignment, hierarchy/numbering, stock bolding, disclaimer presence/compactness, prohibited action language, content-length guardrails, images and render success. Render success is not visual inspection: when page images exist, inspect **every page** for clipping, overlap, pagination, orphan headings, abnormal whitespace and image placement.

Bold emphasis should form a useful skim-reading skeleton; semantic audit judges whether title + headings + bold anchors reconstruct the article's central line.

## 12. Knowledge writeback
Before final PASS, make an explicit reusable-knowledge writeback decision. Under Runtime, record that decision through `record_knowledge_writeback`; write back only evidence-bounded durable cognition through an actually authorized durable store. Article rhetoric/title/temporary emphasis are not market knowledge. StockBase corrections stay in the review queue.

When structured platform-performance experience is persisted later, preserve the platform-owned sample's article identity, measurement window, available-vs-unavailable metrics, baseline/context, confounders, hypothesis, confidence and promotion status. Knowledge storage must not silently upgrade `SAMPLE_ONLY` into a durable rule.

Do not claim automatic causal learning, durable rule promotion or cross-agent synchronization unless those agents/workflows actually share an implemented knowledge layer and executable promotion path.

## 13. Final red-team and completion
At FINAL_AUDIT, treat the result as potentially wrong. Re-read frozen acceptance, final content/artifacts, research evidence, mechanical results and every required render page.

The final evidence inventory must prove source/evidence boundary, supplied-source completion, omission/count/time/market-data checks, headline/opening/H1 payoff, hierarchy realization, concrete company/stock application, stock-judgment clarity, bold skim skeleton, causal continuity, fact/inference/market-expectation separation, anti-AI cleanliness, compliance/risk, DUAL mother-to-derivative consistency and artifact identity. Applicable formal modes must include the explicit final evidence keys `opening_first_three_sentences` and `bold_scan_skeleton` rather than merely asserting that the opening and bolding were checked.

Use the existing final-evidence keys to prove reader value rather than creating a second checklist vocabulary. `hook_quality`, `opening_first_three_sentences`/`opening_payoff`, per-H1 `promise_payoff`, `reasoning_continuity`, `bold_scan_skeleton`, `side_focus`, `company_selection_basis`, `DUAL.deep_master_quality` and `DUAL.broad_hook_strength` must collectively show what the target reader learns that was not obvious before reading, how quickly that value becomes visible, and whether the scan path preserves it. Factual correctness without a material reader-information gain is an EDITORIAL/DRAFT defect, not an automatic PASS.

Final `hook_quality` evidence must now also demonstrate the headline-craft contract: recognizable subject, reader stake, one useful unresolved hinge, no stronger natural interpretation than the evidence supports, and visible first-screen payoff. Final style/`reasoning_continuity` evidence must include the Fresh Reader blind-pass result and identify any revised exit point/template smell rather than merely asserting that prose was checked.

Also use the existing evidence keys to prove professional financial-analysis integrity. `GLOBAL.evidence_boundary`, `GLOBAL.time_integrity`, `GLOBAL.counterexample_scan`, `<MODE>.company_selection_basis`, `<MODE>.stock_judgment_clarity`, `<MODE>.reasoning_continuity`, `<MODE>.side_focus` and per-H1 `promise_payoff` must show that material layer transitions are supported or explicitly bounded, numeric/expectation comparisons are definition- and time-consistent, competing explanations were considered, and fundamentals/earnings quality/valuation/expectations/market role were not silently conflated. Revise rather than PASS when a headline or conclusion depends on a missing analytical bridge.

DUAL additionally proves:
- `DUAL.cross_version_consistency`;
- `DUAL.deep_master_quality`;
- `DUAL.broad_derivation_fidelity`;
- `DUAL.broad_hook_strength`.

All tasks require the global evidence keys from `references/audit.md`, including `GLOBAL.evidence_boundary`, `GLOBAL.source_completion`, `GLOBAL.omission_scan`, `GLOBAL.count_reconciliation`, `GLOBAL.time_integrity`, `GLOBAL.market_data_boundary`, `GLOBAL.counterexample_scan` and `GLOBAL.required_outputs`.

Runtime reaches `COMPLETE` only after mandatory gates, knowledge decisions, criterion evidence, artifact identity/readback and final audit pass. Standalone reaches `STANDALONE_COMPLETE` only after its completion barrier passes.

## 14. Durable-rule changes and system errors
When the user changes an “以后都这样” rule or an existing rule is skipped, load `references/maintenance.md`. Classify the change, modify one semantic owner, remove/supersede contradictory wording, add cold-start/regression coverage and validate before promotion.

If a defect should have been caught by an existing rule/gate, treat it as `SYSTEM_ERROR`: repair the execution/test boundary instead of duplicating reminder prose.

Runtime/Skill capability drift is a `SYSTEM_ERROR`. Tool availability without schema/behavior compatibility must never be treated as proof that the deployed Runtime implements the current Agent.

## 15. Scope and assurance boundary
This Skill produces publishable financial content. Standalone荐股/选股/盘后复盘 are separate workflows unless the user explicitly asks to turn that analysis into an article/post.

Runtime-backed real-article live-model E2E remains unverified until an actual authorized run produces final files, every returned Word page is inspected, artifacts are re-read and interruption/BLOCKED recovery is demonstrated.

A `STANDALONE_SKILL` run should require no user reminders for ordinary gates, but it remains self-enforced rather than code-enforced. Never describe it as deployment-grade determinism or 100% guaranteed execution.