---
name: financial-writing-agent
description: Create and continue A-share financial articles or image-first WeChat finance sticker posts through a persisted MCP workflow with broad/deep research, independent audits, integrated visuals and publication-ready Word delivery. Use for new financial-writing tasks from links/PDFs/news/research and for continuing an unfinished writing task. Do not use for standalone stock-picking/recommendation or post-close review unless the user explicitly asks to turn that work into publishable content.
---

# Financial Writing Agent

## 1. Decide resume vs new before doing anything else
Do not automatically start or resume the wrong task.

- If the user says “继续昨天那篇”, “接着写”, “刚才那篇”, or otherwise refers to unfinished writing, call `list_recent_writing_tasks` first, identify the best match from prompt/topic previews, then call `get_writing_task`. Do not ask the user to repeat information already persisted.
- If the matched task is `BLOCKED`, inspect `blocked_reason`, repair the external dependency/contract defect, then call `resume_writing_task`. The Runtime restores the recorded original stage; never start a duplicate task or choose an arbitrary stage to bypass a block.
- If more than one unfinished task is genuinely plausible after reading the previews, ask one targeted disambiguation question rather than guessing.
- For a genuinely new writing task, call `start_writing_task` before connected-knowledge retrieval, web research, outlining, drafting or image planning.
- A new task may reuse durable knowledge/experience, but it must **not** inherit an old task's stage, blockers, selected title/outline, draft, artifacts, visual package, pending actions or next step merely because an unfinished/recent task exists. Only explicit continuation intent restores task state. In short: inherit learning, not unfinished work.

The MCP runtime checkpoint is the executable task authority. GitHub `main` is code/rule authority after promotion. Notion/Drive status pages are mirrors or research/governance inputs, not competing runtime checkpoints.

## 2. Workflow invariant
Follow exactly:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`.

Never silently fall back to free-form writing when a mandatory tool/gate fails. Repair the legal stage or report `BLOCKED` clearly. `BLOCKED` is recoverable only through the explicit resume path after the defect is repaired.

A revision is not a cosmetic side path. Use the earliest correct revision target (`RESEARCH`, `EDITORIAL`, `TITLE`, `DRAFT` or `DELIVERY`); the runtime invalidates affected downstream PASS state and delivery artifacts. Never assume an old audit remains valid after a change.

## 3. Defaults
Unless the current user explicitly overrides a soft preference:
- unspecified formal-article platform → `DUAL`;
- `DUAL` = one broad/deep research base + independently edited `FINANCE_DEEP` and `FINANCE_BROAD`;
- formal language → Simplified Chinese financial prose;
- delivery → `WORD_FILE_ONLY`;
- new Word articles use the current integrated visual workflow unless the user opts out or the task is only about an already-existing document;
- do not paste the article body/preview in chat under `WORD_FILE_ONLY`.

Explicit user instructions can override soft editorial preferences for the current run. They cannot bypass factual support, compliance, file identity, required-output or stage-order gates.

## 4. Load only the references needed for the current stage
Supporting references are part of this Skill bundle. Load them progressively:
- RESEARCH: `references/research.md` + `references/knowledge.md`.
- RESEARCH_AUDIT / FINAL_AUDIT: `references/audit.md`.
- EDITORIAL / TITLE / DRAFT: `references/editorial.md` + `references/style.md`; load `references/structure_patterns.md` only after TopicDNA/current-mode candidate structures exist, for collision checking rather than template generation.
- Platform routing / WeChat sticker: `references/platforms.md`.
- Visual planning / insertion: `references/visuals.md`.
- Word/output: `references/delivery.md`.
- Durable rule changes: `references/maintenance.md`.

Do not dump every reference into every stage. The runtime is the stable control plane; references provide only the cognition needed for the active stage.

## 5. Research/cognition before selective writing
Knowledge recall is an explicit pre-research gate, not an optional silent side effect. After Runtime start and before `submit_research`:
- when relevant connected EventBase/StockBase/knowledge assets are accessible, retrieve them and call `record_knowledge_context(status="PASS", refs=[...])` with real references plus reuse/conflict notes when useful;
- for an A-share company/concept topic, connected StockBase/EventBase is relevant by default when actually accessible and StockBase remains READ ONLY;
- when no relevant durable source is available or the connector/destination is genuinely unavailable, call `record_knowledge_context(status="N_A", notes=[...])` with the explicit reason.

Do not mark `N_A` merely to skip a source that is actually available and relevant. Reverify current/material claims even when prior knowledge is reused.

Research must know materially more than the article says: catalyst/timeline, concept graph, industry/transmission chain, relevant A-share universe, fundamentals, `why_this / why_not`, market-selection logic and relevant short-term roles/signals. `ResearchPackage.coverage` must state repeated-sweep coverage and an explicit stop reason so “全面” is bounded and auditable rather than infinite or hand-wavy.

User-supplied links/PDFs/reports/attachments are source obligations, not decorative inputs. Account for each material source as actually read, partially read/truncated, duplicative of another original, or unavailable with a fallback/impact boundary. Tool success, snippets and summaries do not equal source completion.

Run omission/count/time checks as part of research judgment: ask what should exist but is missing; reconcile trustworthy source/universe counts where applicable; refresh mutable company/policy/order/customer/capacity facts; timestamp market-state claims; and never use later information as if it were known at an earlier stated boundary.

Use the evidence ledger as an executable boundary, not decorative notes. Core title/lead/H1/bold/conclusion facts cannot remain `UNRESOLVED`. Distinguish `SINGLE_SOURCE_ATTRIBUTED` from `INDEPENDENTLY_CROSS_CHECKED`, including real source-group independence. Writing keeps StockBase read-only; stable corrections go to the research `review_queue`, not directly into StockBase.

## 6. Editorial, DUAL separation and acceptance contract
Use topic-specific structure, continuous report prose and real paragraph/section transitions. Formal hierarchy is `一、二、三 → （1）（2）（3） → ①②③`; `·` is not a structural level marker. Conclusion-first is a soft preference, not a fixed opening template.

For every applicable formal mode create its own `ModeEditorialPlan`. In DUAL, `FINANCE_DEEP` and `FINANCE_BROAD` each generate 2–3 candidate structures and select independently after the shared TopicDNA is known. Do not reuse one selected structure with two emphasis lists merely to satisfy DUAL.

Every H1 must function as an advancing judgment, not a directory label. The final article should make recoverable for each material H1: its directional conclusion, the remaining information gap/mechanism/contrast worth reading for, and where the body pays that promise off. Use H2/H3 only when real logical sub-blocks require them; do not add hierarchy for decoration or hide obvious multi-block logic in a wall of text.

Every headline candidate carries a verified factual anchor, a real information gap and an opening-payoff design. After selected titles and mode structures are submitted, the runtime freezes a `WritingAcceptanceContract`. Do not enter drafting unless the returned state shows both `title_audit=PASS` and `acceptance_contract=PASS`.

Formal draft payloads must start with exactly one independent `lead`, immediately followed by the first H1. Draft title and H1 sequence must remain faithful to the frozen acceptance contract. If the title or structure needs changing, revise through the legal stage instead of altering the draft behind the contract.

Keep confirmed fact, industrial/economic inference, market-traded expectation and unverified rumor/hypothesis distinct in the prose. Industry benefit and market selection may corroborate one another but must not be presented as the same claim.

At `EDITORIAL_AUDIT`, run the independent style judge first and call `submit_style_audit`. Its rubric makes anti-AI output explicit. General editorial audit cannot PASS until style audit passes. Remove unsupported extreme/superlative rhetoric without mechanically banning factual temporal words such as “最近/最后”. Published prose must not leak user prompts, hidden selection instructions, gate/tool names or backstage workflow language.

## 7. Risk/compliance
Every formal public-finance payload carries `risk_disclaimer` as a separate required field. Delivery appends the risk/disclaimer section deterministically so the writer cannot omit or duplicate it through formatting drift. Keep it concise but materially complete and topic-specific. A disclaimer never cures actionable buy/sell guidance.

Compliance applies to title, lead, H1, bold anchors, ending and interaction text as well as ordinary body prose.

## 8. Integrated visual workflow
The current single Writing Agent includes its visual/Word-insertion path. When visuals are enabled, ChatGPT generates real images and submits them at DELIVERY with `submit_visual_package` using authorized ChatGPT file parameters. Never invent a server path or arbitrary image URL.

Formal article defaults: exactly one 16:9 hero per applicable article plus semantic section images at roughly one per 700 Chinese characters, with meaning taking priority over counting. Image hook text may differ from H1. Use the approved user avatar as a small circular integrated element when the active visual profile requires it.

The server copies validated image bytes into task storage and Word inserts them centered and uncropped; very tall images are height-capped while preserving aspect ratio. File retrieval follows public-HTTPS/network-safety checks.

## 9. WeChat sticker posts
Explicit 微信贴图 requests use `WECHAT_STICKER_POST`, not a shortened DUAL article. Verify current platform limits/mechanics at execution time and record them in `PlatformConstraintSnapshot`; do not hard-code remembered limits. Numeric title/body/image limits are enforced when current evidence supplies them. The image hook, title, useful body, interaction prompt and risk text must complement rather than duplicate one another.

When the user asks for platform recommendation/click/search/retention optimization and a connected platform/ArticleBase experience store is available, retrieve the current relevant evidence. Platform/account experience informs packaging but never overrides research accuracy or generic editorial rules; one viral/failed article is an experience sample, not a universal formula.

## 10. Mechanical QA is not final QA
`build_and_mechanically_audit_delivery` builds the required publication artifacts and runs deterministic Word/render checks. Mechanical success does not prove semantic quality, research/source completeness or visual page correctness.

When render is enabled, the tool returns `writing-render://...` page resources. Inspect **every returned page** before claiming page QA. Check clipping, overlap, pagination, orphan headings, abnormal blank space/pages, broken image placement and risk-section layout. Do not infer page quality merely because render succeeded.

Bold emphasis must form a useful skim-reading information skeleton; deterministic checks can verify formatting but semantic audit must decide whether title + headings + body bold anchors reconstruct the central line without decorative over-bold.

## 11. Knowledge writeback is an explicit decision
Before final PASS, write reusable evidence-bounded knowledge through the connected store when available and call `record_knowledge_writeback(status="PASS", refs=[...])`. If there is no reusable item or writable destination, call it with `status="N_A"` and an explicit reason. The Runtime must not complete while this decision is still NOT_RUN.

Reusable cognition may include event chronology, industry relationships, evidence/source-quality notes and article/platform experience according to their connected-store semantics. Article-specific rhetoric and temporary task choices are not market knowledge. StockBase corrections remain in the review queue and cannot be smuggled through generic writeback.

Writing does not directly mutate a future stock-picking/review Agent's executable state. Do not claim cross-agent synchronization until those agents share the same implemented knowledge layer.

## 12. Final red-team and completion
At FINAL_AUDIT, treat the current result as potentially wrong. Re-read the frozen acceptance contract, final draft/state, research evidence boundary, mechanical results and every required render page.

Submit `FinalAuditDecision`, not a generic PASS. `acceptance_evidence` uses exact `KEY: concrete final-content evidence` entries defined in `references/audit.md`; the runtime machine-checks the criterion inventory it currently models before COMPLETE.

The final evidence must prove, not merely assert: source/evidence boundary and material supplied-source completion; omission/count/time boundaries where applicable; title/opening/H1 payoff; side focus/company-selection basis; bold skim skeleton; causal continuity; fact/inference/market-expectation separation; anti-AI and prompt-leakage cleanliness; compliance/risk; DUAL consistency; required artifact identity/readback; and every inspected render page.

For the current machine-checked formal keys, each applicable mode includes:
- `selected_title`;
- `independent_lead`;
- `opening_first_three_sentences`;
- `h1_structure`;
- `side_focus`;
- `company_selection_basis`;
- `headline_anchor`;
- `opening_payoff`;
- `bold_scan_skeleton`;
- `reasoning_continuity`;
- `compliance_risk`.

DUAL additionally requires `DUAL.cross_version_consistency`; enabled visuals add the applicable `visual_alignment` key; all tasks include `GLOBAL.evidence_boundary` and `GLOBAL.required_outputs`. Use those existing evidence keys to carry the richer checks from `references/audit.md` rather than inventing a competing checklist.

`reviewed_render_pages` must exactly list the render resource URIs actually inspected when render is required. DUAL must be checked for both independent validity and cross-version factual/evidence/conclusion-boundary consistency. Unsupported/new material facts, silently incomplete supplied sources or time-contaminated claims revise to RESEARCH rather than being silently accepted, and repair targets must point to the earliest correct legal stage.

Only after the **mandatory gate inventory itself is complete**, both knowledge decisions (`knowledge_context` and `knowledge_sync`) resolve to PASS/N_A, every other required gate resolves, criterion-level final evidence is complete, every required artifact has a recorded checksum and passes final readback/checksum verification, and final audit passes may the runtime reach `COMPLETE`. At `COMPLETE`, return artifact links/references plus the concise runtime completion checklist. Under `WORD_FILE_ONLY`, do not paste the article body.

When connected governance mirrors are available, copy final formal artifacts to the configured destination and update mirrors after Runtime completion. Mirror failure must be reported separately and must not rewrite a valid Runtime checkpoint. If claiming an external copy/upload succeeded, verify it by connected readback/metadata rather than by tool-call success alone.

## 13. Durable-rule changes and system errors
If the user changes an “以后都这样” requirement, retracts an old one, or points out that an existing rule was skipped, load `references/maintenance.md` rather than patching multiple files ad hoc. Classify the change, update one owner, clean contradictory wording and add regression coverage under a no-current-chat-memory assumption.

If a defect should have been caught by an existing rule/gate, treat it as a `SYSTEM_ERROR` candidate and repair the execution/test boundary. Do not falsely claim automated cross-task repeat-count escalation unless such a ledger is actually implemented.

## 14. Scope boundary
This Skill is for producing publishable financial content. It may use stock-picking/review knowledge as research context, but it must not activate merely because the user asks for a standalone荐股、选股、盘后复盘 or trading decision. Those are separate future workflows unless the user explicitly asks to turn the analysis into an article/post.

Do not claim deterministic support for a use case that has not been implemented and tested. Real article live-model E2E remains **unverified until an actual user-authorized run produces the final required files, every returned Word page is inspected, artifacts are re-read, and a deliberate interruption/BLOCKED recovery is demonstrated**. A mock/fixture/unit run is not a real article E2E.
