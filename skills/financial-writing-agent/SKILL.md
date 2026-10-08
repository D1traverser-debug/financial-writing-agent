---
name: financial-writing-agent
description: Create and continue A-share financial articles or image-first WeChat finance sticker posts through a persisted MCP workflow, or through an explicit standalone Skill execution profile when the Runtime is not deployed. Use for new financial-writing tasks from links/PDFs/news/research and for continuing an unfinished writing task. Do not use for standalone stock-picking/recommendation or post-close review unless the user explicitly asks to turn that work into publishable content.
---

# Financial Writing Agent

## 0. Choose the execution profile before doing anything else
Do not begin research, outlining or drafting until the control plane is selected.

- If Financial Writing Agent MCP Runtime tools are available, use `RUNTIME`. The MCP runtime checkpoint is the executable task authority.
- If the Runtime is genuinely unavailable/not deployed and the conversation is executing by reading this Skill, use `STANDALONE_SKILL` and load `references/standalone.md` before the task begins. Create its mandatory `ShadowTaskLedger` and use it as the in-session control plane.
- Do **not** choose standalone merely because Runtime is inconvenient, and do not silently switch an already-started Runtime task into standalone after a tool/gate failure. Repair/resume the Runtime task or report it BLOCKED.
- In standalone mode, never invent MCP calls, task IDs, gate receipts, checksums or render resources. `STANDALONE_COMPLETE` is a disciplined self-audited completion state, not Runtime `COMPLETE`.

The standalone profile exists so a fresh conversation can execute this Agent without deployment while retaining explicit stage accounting, acceptance contracts, invalidation, evidence and completion barriers. It reduces drift but does not become deterministic simply because the rules are written down.

## 1. Decide resume vs new before doing anything else
Do not automatically start or resume the wrong task.

- Under `RUNTIME`, if the user says “继续昨天那篇”, “接着写”, “刚才那篇”, or otherwise refers to unfinished writing, call `list_recent_writing_tasks` first, identify the best match from prompt/topic previews, then call `get_writing_task`. Do not ask the user to repeat information already persisted.
- If the matched Runtime task is `BLOCKED`, inspect `blocked_reason`, repair the external dependency/contract defect, then call `resume_writing_task`. The Runtime restores the recorded original stage; never start a duplicate task or choose an arbitrary stage to bypass a block.
- If more than one unfinished task is genuinely plausible after reading the previews/checkpoints, ask one targeted disambiguation question rather than guessing.
- Under `RUNTIME`, for a genuinely new writing task, call `start_writing_task` before connected-knowledge retrieval, web research, outlining, drafting or image planning. Do **not** inspect or restore unrelated unfinished task state merely because another task exists.
- Under `STANDALONE_SKILL`, a genuinely new task always starts with a fresh `ShadowTaskLedger`. Cross-conversation continuation is allowed only when an actual prior checkpoint/artifact set is available and can be identified unambiguously; otherwise do not pretend to remember an old task.
- A new task may reuse durable knowledge/experience, but it must **not** inherit an old task's stage, blockers, selected title/outline, draft, artifacts, visual package, pending actions or next step merely because an unfinished/recent task exists. Only explicit continuation intent restores task state. In short: inherit learning, not unfinished work.

GitHub `main` is code/rule authority after promotion. Notion/Drive status pages are mirrors or research/governance inputs, not competing executable checkpoints. Under Runtime the MCP checkpoint is task authority; under standalone the current ShadowTaskLedger is only an in-session execution record and must not be overstated as durable Runtime state.

## 2. Workflow invariant
For a normal single formal mode or sticker task, follow exactly:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE/STANDALONE_COMPLETE`.

For a `DUAL` formal task, follow exactly:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL[FINANCE_DEEP] → TITLE[FINANCE_DEEP] → DRAFT[FINANCE_DEEP] → BROAD_DERIVATION[FINANCE_BROAD: EDITORIAL → TITLE → DRAFT] → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE/STANDALONE_COMPLETE`.

`BROAD_DERIVATION` is a mandatory internal stage only for DUAL formal tasks. Under Runtime it does **not** add a new MCP tool: follow `next_action` and reuse the existing `submit_editorial_plan`, `submit_headlines`, and `submit_draft` tools in that order. Under standalone, enforce the same order through the ShadowTaskLedger. FINANCE_BROAD planning/title/draft is forbidden before the FINANCE_DEEP mother draft has been frozen.

Never silently fall back to free-form writing when a mandatory tool/gate fails. Runtime failure does not authorize a profile switch. In standalone mode, inability to prove a required gate becomes explicit `BLOCKED`/`N_A` according to `references/standalone.md`; it never becomes an assumed PASS.

A revision is not a cosmetic side path. Use the earliest correct revision target (`RESEARCH`, `EDITORIAL`, `TITLE`, `DRAFT` or `DELIVERY`); invalidate every affected downstream PASS state and delivery artifact. Never assume an old audit remains valid after a change. Stage-specific research/title/draft revision budgets apply in both profiles: Runtime enforces them; standalone self-counts them in the ShadowTaskLedger and blocks rather than silently resetting counters or looping forever.

## 3. Defaults
Unless the current user explicitly overrides a soft preference:
- unspecified formal-article platform → `DUAL`;
- `DUAL` = one exhaustive research base → completed `FINANCE_DEEP` analytical mother version → derived/compressed `FINANCE_BROAD` distribution version; do **not** independently invent two analyses;
- formal language → Simplified Chinese financial prose;
- delivery → `WORD_FILE_ONLY`;
- explicit direct-chat/plain-text only → `CHAT_TEXT`;
- explicit request for both chat body **and** Word → `WORD_AND_CHAT`; both output families are required and Word mechanical/render/audit gates still run;
- new Word articles use the current integrated visual workflow unless the user opts out or the task is only about an already-existing document;
- do not paste the article body/preview in chat under `WORD_FILE_ONLY`.

Explicit user instructions can override soft editorial preferences for the current run. They cannot bypass factual support, compliance, file identity, required-output or stage-order gates.

## 4. Load only the references needed for the current stage
Supporting references are part of this Skill bundle. Load them progressively:
- EXECUTION PROFILE: load `references/standalone.md` once at the beginning only when `STANDALONE_SKILL` is active.
- RESEARCH: `references/research.md` + `references/knowledge.md`.
- RESEARCH_AUDIT / FINAL_AUDIT: `references/audit.md`.
- EDITORIAL / TITLE / DRAFT / BROAD_DERIVATION: `references/editorial.md` + `references/style.md`; load `references/structure_patterns.md` only after TopicDNA/current-mode candidate structures exist, for collision checking rather than template generation.
- Platform routing / WeChat sticker: `references/platforms.md`.
- Visual planning / insertion: `references/visuals.md`.
- Word/output: `references/delivery.md`.
- Durable rule changes: `references/maintenance.md`.

Do not dump every reference into every stage. Runtime or the standalone ShadowTaskLedger is the stable control plane for the active run; references provide the cognition needed for the active stage.

## 5. Research/cognition before selective writing
Knowledge recall is an explicit pre-research gate, not an optional silent side effect.

Under Runtime, after task start and before `submit_research`:
- when relevant connected EventBase/StockBase/knowledge assets are accessible, retrieve them and call `record_knowledge_context(status="PASS", refs=[...])` with real references plus reuse/conflict notes when useful;
- for an A-share company/concept topic, connected StockBase/EventBase is relevant by default when actually accessible and StockBase remains READ ONLY;
- when no relevant durable source is available or the connector/destination is genuinely unavailable, call `record_knowledge_context(status="N_A", notes=[...])` with the explicit reason.

Under standalone, perform the same recall decision and record PASS with real refs or N_A with reason in the ShadowTaskLedger. Do not mark `N_A` merely to skip a source that is actually available and relevant. Reverify current/material claims even when prior knowledge is reused.

Research must know materially more than the article says: catalyst/timeline, concept graph, industry/transmission chain, relevant A-share universe, fundamentals, `why_this / why_not`, market-selection logic and relevant short-term roles/signals. Research coverage must state repeated-sweep coverage and an explicit stop reason so “全面” is bounded and auditable rather than infinite or hand-wavy.

For recommendation-oriented or stock-comparison articles, **selection comes after research**. Do not research only the final familiar names. Build the relevant universe first, then deeply verify every material company that may affect the ranking/selection: real business exposure, industry-chain position, business/earnings realization stage, customers/orders/revenue/profit/capacity/price where material, positive and negative evidence, `why_this / why_not`, industrial-beneficiary role, sentiment/market role, liquidity role and current short-term身位/structure when supported by the declared market-data capability. The final written subset may be selective; the research basis must not be shallow.

User-supplied links/PDFs/reports/attachments are source obligations, not decorative inputs. Account for each material source as actually read, partially read/truncated, duplicative of another original, or unavailable with a fallback/impact boundary. Tool success, snippets and summaries do not equal source completion.

Run omission/count/time checks as part of research judgment: ask what should exist but is missing; reconcile trustworthy source/universe counts where applicable; refresh mutable company/policy/order/customer/capacity facts; timestamp market-state claims; and never use later information as if it were known after the frozen `effective_time_boundary` in the Runtime contract or ShadowTaskLedger.

Market microstructure claims must remain inside the declared `market_data_boundary`. Ordinary quotes do not authorize Level-2 inferences. Order-book/封单/queue claims require real Level-2 order-book receipts; 逐笔/tick claims require tick capability; 抢筹 inference requires actual order-book or tick evidence. When unavailable, omit/downgrade the claim and record the limitation rather than fabricating precision.

Use the evidence ledger as an executable boundary, not decorative notes. Core title/lead/H1/bold/conclusion facts cannot remain `UNRESOLVED`. Distinguish `SINGLE_SOURCE_ATTRIBUTED` from `INDEPENDENTLY_CROSS_CHECKED`, including real source-group independence. Writing keeps StockBase read-only; stable corrections go to the research `review_queue`, not directly into StockBase.

A temporary same-path research failure may be retried at most once when there is a reason to believe the failure is transient. Quota/permission exhaustion is not a reason for blind retry. Consolidate same-path failure history into one failure receipt and switch to an independent reliable fallback or keep the evidence boundary explicit.

## 6. Editorial, hook system, DUAL derivation and acceptance contract
Use topic-specific structure, continuous report prose and real paragraph/section transitions. Formal hierarchy is `一、二、三 → （1）（2）（3） → ①②③`; `·` is not a structural level marker. Conclusion-first is a soft preference, not a fixed opening template.

### DUAL is deep-first, not parallel
For DUAL, `FINANCE_DEEP` is the analytical mother version. Solve it first: complete the causal chain, company comparison, `why_this / why_not`, industry realization stage, market-selection logic, current stock judgments, counterevidence and risk boundary. There is no default short length target; preserve useful reasoning and use roughly **10,000 Chinese characters as an upper guardrail rather than a target**.

Only after the FINANCE_DEEP **draft and acceptance contract are frozen** may `FINANCE_BROAD` be planned, titled and drafted through `BROAD_DERIVATION`. The broad version may change title, lead, section order, density and explanatory burden to improve click-through and continuation for a wider finance audience, but it must not invent new facts, upgrade evidence strength, reverse company/stock ranking, change the decisive causal conclusion or weaken the risk boundary. It should be materially lower-friction and more acquisition-oriented than the deep mother version while preserving at least one complete core causal chain.

A FINANCE_BROAD-only task may still be written directly from TopicDNA/research because no deep output exists in that task. The deep-first derivation rule applies specifically when DUAL requires both versions.

### Hook engine
Treat hooks as a linked system, not a title-only trick:
1. headline hook earns the click truthfully;
2. first-screen/opening hook proves the click was worth it within the first 1–3 sentences;
3. every material H1 preserves a real continuation gap and pays it off;
4. when stocks are material, company/stock comparison can itself be the hook by resolving `why_this / why_not`, realization-stage or 身位 divergence.

Before generating titles, identify target reader, why the topic matters now, primary contradiction/consequence/anti-expectation, default expectation, strongest verified anchor, concrete stake, one primary information gap, cognitive-load risk and the exact opening payoff.

Generate 8–12 candidates from **genuinely different reasons to click**, not superficial paraphrases. When evidence permits, candidate angles may include contradiction/anti-expectation, consequence/stakes, verified number/scale, company divergence, market selection/身位, timing/policy inflection, causal “why”, result-first framing and finance-wide relevance. Do not force any hook mechanism that the evidence does not support.

Every headline candidate must stay inside the evidence boundary, keep the topic identifiable, preserve a real information gap and have an opening payoff. Reject generic “重磅/机会来了/风口来了/谁将受益” packaging without a specific verified tension, emotional certainty stronger than evidence, fake mystery boxes, complete-answer dumps and multiple candidates that are really the same angle with different wording.

For FINANCE_DEEP prioritize specificity + analytical tension + selection value. For FINANCE_BROAD prioritize cross-sector relevance + low entry cost + curiosity + concrete stakes, but derive those hooks from conclusions already established by the deep mother version.

### H1 and acceptance
Every H1 must function as an advancing judgment, not a directory label. The final article should make recoverable for each material H1: its directional conclusion, the remaining information gap/mechanism/contrast worth reading for, and where the body pays that promise off. Use H2/H3 only when real logical sub-blocks require them; do not add hierarchy for decoration or hide obvious multi-block logic in a wall of text.

After applicable selected titles and structures are ready, freeze a `WritingAcceptanceContract` before drafting: Runtime freezes it in persisted state; standalone serializes the equivalent contract in the ShadowTaskLedger. Formal draft payloads start with exactly one independent `lead`, immediately followed by the first H1. In DUAL, the deep acceptance contract freezes first; the broad acceptance contract is added only during `BROAD_DERIVATION` after the deep mother draft exists. If title/structure/section promises need changing, revise through the legal stage rather than altering the draft behind the contract.

### Stock/company judgment must be current and explicit
When evidence is sufficient, do **not** replace a stock/company judgment with an observation checklist. State what is already confirmed, what remains only expected, where the company sits in the industrial realization chain, its current market role/身位 when supported, why it ranks stronger/weaker/ahead/behind meaningful alternatives, and the decisive limitation preventing a higher ranking when relevant.

Avoid empty endings such as “接下来先看A再看B”, “后续继续观察”, “能否走出来还要看市场”, “值得关注”, “有待验证” or equivalent phrases when the available evidence already supports a present-tense conclusion. Conditions/falsification points may follow the judgment; they must not substitute for it.

When evidence genuinely cannot support a firmer conclusion, say exactly **what is unknown, why it is unknown, what concrete fact/data would resolve it and how the possible outcomes would change the judgment**. Do not manufacture certainty, but do not use vague hedging to avoid the best evidence-bounded conclusion.

This is analytical clarity, not a license for actionable trading instructions. Do not turn it into buy/sell imperatives, position size, entry timing, target price, stop-loss or guaranteed-return language.

Keep confirmed fact, industrial/economic inference, market-traded expectation and unverified rumor/hypothesis distinct in the prose. Industry benefit and market selection may corroborate one another but must not be presented as the same claim.

At `EDITORIAL_AUDIT`, run the independent style judge first. Under Runtime call `submit_style_audit` before the general editorial audit. Under standalone, record the style evidence and verdict separately in the ShadowTaskLedger before the general editorial verdict. Remove unsupported extreme/superlative rhetoric, prompt leakage, template fingerprints and empty hedge language without mechanically banning genuine uncertainty.

## 7. Risk/compliance
Every formal public-finance payload carries `risk_disclaimer` as a separate required field. Delivery appends/preserves the risk/disclaimer section deterministically where the environment supports it. Keep it concise but materially complete and topic-specific. A disclaimer never cures actionable buy/sell guidance.

Compliance applies to title, lead, H1, bold anchors, ending and interaction text as well as ordinary body prose.

## 8. Integrated visual workflow
The current single Writing Agent includes its visual/Word-insertion path. Under Runtime, when visuals are enabled, ChatGPT generates real images and submits them at DELIVERY with `submit_visual_package` using authorized ChatGPT file parameters. Never invent a server path or arbitrary image URL.

Under standalone, use real image/file capabilities when available and record actual assets in the ShadowTaskLedger. If required visual capability is unavailable, record the real limitation rather than fabricating an asset or pretending visual QA passed.

Formal article defaults: exactly one 16:9 hero per applicable article plus semantic section images at roughly one per 700 Chinese characters, with meaning taking priority over counting. Image hook text may differ from H1. Use the approved user avatar as a small circular integrated element when the active visual profile requires it.

## 9. WeChat sticker posts
Explicit 微信贴图 requests use `WECHAT_STICKER_POST`, not a shortened DUAL article. Verify current platform limits/mechanics at execution time and record them in `PlatformConstraintSnapshot` or the standalone shadow record; do not hard-code remembered limits. Numeric title/body/image limits are enforced when current evidence supplies them. The image hook, title, useful body, interaction prompt and risk text must complement rather than duplicate one another.

When the user asks for platform recommendation/click/search/retention optimization and a connected platform/ArticleBase experience store is available, retrieve the current relevant evidence. Platform/account experience informs packaging but never overrides research accuracy or generic editorial rules; one viral/failed article is an experience sample, not a universal formula.

## 10. Mechanical QA is not final QA
Under Runtime, `build_and_mechanically_audit_delivery` builds the required publication artifacts and runs deterministic Word/render checks. Under standalone, perform the same observable checks with the available document/file/render tools and explicitly mark anything genuinely unavailable; “not checked” is never PASS.

Mechanical success does not prove semantic quality, research/source completeness or visual page correctness. `WORD_AND_CHAT` still requires Word mechanical/render/audit gates; only pure `CHAT_TEXT` makes Word-specific checks N/A.

When render pages are available, inspect **every returned/generated page** before claiming page QA. Check clipping, overlap, pagination, orphan headings, abnormal blank space/pages, broken image placement and risk-section layout. Do not infer page quality merely because rendering succeeded.

Bold emphasis must form a useful skim-reading information skeleton; deterministic checks can verify formatting but semantic audit must decide whether title + headings + body bold anchors reconstruct the central line without decorative over-bold.

## 11. Knowledge writeback is an explicit decision
Before final PASS, write reusable evidence-bounded knowledge through the connected store when available. Under Runtime call `record_knowledge_writeback(status="PASS", refs=[...])`; if there is no reusable item or writable destination, call it with `status="N_A"` and an explicit reason.

Under standalone, make and record the same PASS/N_A decision in the ShadowTaskLedger and perform the writeback only through an actually available/authorized durable store. Do not claim persistence if no durable destination exists.

Reusable cognition may include event chronology, industry relationships, evidence/source-quality notes and article/platform experience according to their connected-store semantics. Article-specific rhetoric and temporary task choices are not market knowledge. StockBase corrections remain in the review queue and cannot be smuggled through generic writeback.

Writing does not directly mutate a future stock-picking/review Agent's executable state. Do not claim cross-agent synchronization until those agents share the same implemented knowledge layer.

## 12. Final red-team and completion
At FINAL_AUDIT, treat the current result as potentially wrong. Re-read the frozen acceptance contract, final draft/state, research evidence boundary, mechanical results and every required render page.

Under Runtime, submit `FinalAuditDecision`, not a generic PASS. Under standalone, build the **same criterion-keyed evidence inventory** in the ShadowTaskLedger and do not set `STANDALONE_COMPLETE` until every applicable key has concrete final-content/artifact evidence. Generic statements such as “checked” do not count.

The final evidence must prove, not merely assert: source/evidence boundary and material supplied-source completion; omission/count/time/market-data boundaries where applicable; title/opening/H1 payoff and hook fidelity; side focus/company-selection basis; stock/company judgment specificity; bold skim skeleton; causal continuity; fact/inference/market-expectation separation; anti-AI and prompt-leakage cleanliness; compliance/risk; DUAL mother-to-derivative consistency; required artifact identity/readback; and every inspected render page.

For the current formal keys, each applicable mode includes:
- `selected_title`;
- `independent_lead`;
- `opening_first_three_sentences`;
- `h1_structure`;
- `side_focus`;
- `company_selection_basis`;
- `headline_anchor`;
- `opening_payoff`;
- `hook_quality`;
- `stock_judgment_clarity`;
- `bold_scan_skeleton`;
- `reasoning_continuity`;
- `compliance_risk`.

DUAL additionally requires all four explicit derivation checks:
- `DUAL.cross_version_consistency`;
- `DUAL.deep_master_quality`;
- `DUAL.broad_derivation_fidelity`;
- `DUAL.broad_hook_strength`.

Enabled visuals add the applicable `visual_alignment` key. All tasks require the full global evidence set from `references/audit.md`, including `GLOBAL.evidence_boundary`, `GLOBAL.source_completion`, `GLOBAL.omission_scan`, `GLOBAL.count_reconciliation`, `GLOBAL.time_integrity`, `GLOBAL.market_data_boundary`, `GLOBAL.counterexample_scan` and `GLOBAL.required_outputs`.

Unsupported/new material facts, silently incomplete supplied sources, time-contaminated claims or market-data capability overreach revise to RESEARCH rather than being silently accepted, and repair targets must point to the earliest correct legal stage.

Runtime may reach `COMPLETE` only after its mandatory gate inventory, knowledge decisions, criterion evidence, artifact checksums/readback and final audit pass. Standalone may reach `STANDALONE_COMPLETE` only after the completion barrier in `references/standalone.md` is fully satisfied. Under `WORD_FILE_ONLY`, do not paste the article body. Under explicit `WORD_AND_CHAT`, return both the requested chat body and audited Word/audit artifacts when those artifacts can actually be produced.

When connected governance mirrors are available, copy final formal artifacts to the configured destination and update mirrors after completion. Mirror failure must be reported separately and must not rewrite a valid Runtime checkpoint or standalone audit result. If claiming an external copy/upload succeeded, verify it by connected readback/metadata rather than by tool-call success alone.

## 13. Durable-rule changes and system errors
If the user changes an “以后都这样” requirement, retracts an old one, or points out that an existing rule was skipped, load `references/maintenance.md` rather than patching multiple files ad hoc. Classify the change, update one owner, clean contradictory wording and add regression coverage under a no-current-chat-memory assumption.

If a defect should have been caught by an existing rule/gate, treat it as a `SYSTEM_ERROR` candidate and repair the execution/test boundary. For standalone-specific misses, strengthen `references/standalone.md`/its cold-start regressions rather than merely adding another reminder sentence to the article rules. Do not falsely claim automated cross-task repeat-count escalation unless such a ledger is actually implemented.

## 14. Scope boundary
This Skill is for producing publishable financial content. It may use stock-picking/review knowledge as research context, but it must not activate merely because the user asks for a standalone荐股、选股、盘后复盘 or trading decision. Those are separate future workflows unless the user explicitly asks to turn the analysis into an article/post.

Do not claim deterministic support for a use case that has not been implemented and tested. Runtime-backed real article live-model E2E remains **unverified until an actual user-authorized run produces the final required files, every returned Word page is inspected, artifacts are re-read, and a deliberate interruption/BLOCKED recovery is demonstrated**. A mock/fixture/unit run is not a real article E2E.

A `STANDALONE_SKILL` run can be highly disciplined and should require no user reminders for ordinary gates, but it remains self-enforced rather than code-enforced. Never describe it as deployment-grade determinism or 100% guaranteed execution.
