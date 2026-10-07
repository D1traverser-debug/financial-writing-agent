# Audit module

## Independence
The final auditor re-evaluates the frozen final content, artifacts and current runtime state. Writer self-assessment, an earlier draft review, the mere existence of a rule, or a successful tool call is not evidence of passing.

The audit is omission-oriented as well as defect-oriented: ask not only whether present content is correct, but what applicable source, concept/company mapping, rule, section obligation, evidence boundary, risk item, artifact or knowledge action should be present and is missing. Sampling a few visible items is not equivalent to checking the applicable inventory.

## Acceptance contract first
Before FINAL PASS, read the frozen `WritingAcceptanceContract` and the final draft/artifact state. Audit every applicable mode against the contract rather than asking only whether the article feels acceptable.

The acceptance contract freezes not only the selected title/structure but also the selected headline candidate's `headline_factual_anchor`, `headline_primary_gap`, `headline_opening_payoff`, and every formal H1's section expectation: directional conclusion, reader gap, payoff requirement, logical-block plan and any required H3-bearing H2 indexes. FINAL must judge the final article against those frozen promises rather than inventing a new explanation after the fact.

For each formal mode verify with concrete final-content evidence:
- selected title is unchanged or the contract was legitimately rebuilt;
- exactly one independent lead exists before the first H1;
- the first three sentences materially pay off the **frozen** headline information gap/opening-payoff promise rather than spending the opening on generic background;
- H1 count and H1 sequence match the frozen selected structure;
- each H1 carries its frozen directional judgment and continuation gap, and the section body contains a concrete payoff location satisfying the frozen payoff requirement;
- frozen H2/H3 hierarchy is realized exactly: multi-block sections expose their frozen H2 labels/order, required H3-bearing H2 blocks have at least three third-level units, and unplanned hierarchy does not silently drift in during drafting;
- side-focus statement is actually paid off in the article rather than existing only in planning metadata;
- the company-selection basis is visible in the comparison logic;
- the **frozen** headline factual anchor is supported by the research evidence boundary and not silently substituted with a different anchor;
- the opening pays off the frozen selected headline promise rather than switching questions;
- bold emphasis forms a useful skim-reading information skeleton rather than decorative/random highlighting;
- reasoning remains continuous through sections and cross-layer transitions;
- confirmed facts, industrial/economic inference, market-traded expectations and unverified rumor/hypothesis are not silently conflated;
- published prose does not leak user prompts, hidden selection instructions, internal gate/tool names or backstage workflow language;
- risk/compliance boundaries remain satisfied.

A DUAL task additionally requires both versions to stand on their own while preserving the same factual identities, numerical facts, evidence strength, central conclusion boundary and risk boundary. Difference in structure/emphasis is expected; contradictory factual strength is not.

## Final acceptance-evidence key contract
`FinalAuditDecision.acceptance_evidence` is not a free-form summary. Every item uses exactly `KEY: concrete final-content evidence`. `KEY` is machine-checked before COMPLETE.

Every task must provide the following explicit global keys; do not collapse them into one generic “research checked” sentence:
- `GLOBAL.evidence_boundary`
- `GLOBAL.source_completion`
- `GLOBAL.omission_scan`
- `GLOBAL.count_reconciliation`
- `GLOBAL.time_integrity`
- `GLOBAL.counterexample_scan`
- `GLOBAL.required_outputs`

`GLOBAL.count_reconciliation` is still mandatory as an explicit decision. When there is no material enumerable inventory to reconcile, its evidence must say why it is genuinely N/A rather than silently omitting the check.

`GLOBAL.time_integrity` must quote the persisted task's exact `TaskContract.effective_time_boundary` (including timezone) and explain how mutable facts, market data and policy/event status were bounded to information effective on or before that cutoff. Generic phrases such as “checked freshness”, “used latest data” or “time boundary OK” do not satisfy this evidence key. For a historical cutoff, later facts must be explicitly excluded even when they are easier to retrieve today.

Every formal applicable mode (`FINANCE_DEEP` and/or `FINANCE_BROAD`) must provide all of:
- `<MODE>.selected_title`
- `<MODE>.independent_lead`
- `<MODE>.opening_first_three_sentences`
- `<MODE>.h1_structure`
- `<MODE>.side_focus`
- `<MODE>.company_selection_basis`
- `<MODE>.headline_anchor`
- `<MODE>.opening_payoff`
- `<MODE>.bold_scan_skeleton`
- `<MODE>.reasoning_continuity`
- `<MODE>.compliance_risk`

For every frozen `section_expectations` item in that mode, FINAL also supplies a dynamic key:
- `<MODE>.H1_<N>.promise_payoff`

The H1 evidence value must identify the final H1, show the frozen directional conclusion is actually expressed, identify the still-open reader gap/continuation reason, and point to the concrete paragraph/portion where the body pays off the frozen requirement. A restatement of planning metadata is not evidence.

`headline_anchor` evidence must explicitly tie the final title/opening to the frozen `headline_factual_anchor`. `opening_first_three_sentences` and `opening_payoff` evidence must explicitly compare the final opening with the frozen `headline_primary_gap` and `headline_opening_payoff`.

Use the existing keys as evidence containers rather than inventing a second checklist vocabulary:
- `<MODE>.h1_structure` identifies the final H1 sequence and confirms frozen H2/H3 hierarchy realization; per-H1 semantic direction/gap/payoff evidence belongs in the dynamic `H1_<N>.promise_payoff` key.
- `<MODE>.reasoning_continuity` covers causal/cross-layer transitions, fact-vs-inference-vs-market-expectation separation, falsification awareness, natural ending and whether compression preserved the core reasoning chain.
- `<MODE>.bold_scan_skeleton` states whether title + headings + body bold anchors reconstruct the article's central information skeleton without excessive decorative bold.
- `<MODE>.compliance_risk` covers title/lead/H1/bold/ending as well as ordinary body text and confirms the risk section is topic-specific rather than generic boilerplate.
- `GLOBAL.evidence_boundary` summarizes final claim/evidence boundaries, unresolved gaps, source-group independence and StockBase read-only/review-queue discipline.
- `GLOBAL.source_completion` accounts for every user-supplied `TaskContract.source_ref` using the recorded FULL/PARTIAL/UNAVAILABLE boundary and explains the impact of any PARTIAL/UNAVAILABLE source.
- `GLOBAL.omission_scan` states what should have been present by rule/topic/universe but was specifically checked for absence.
- `GLOBAL.count_reconciliation` reconciles material enumerable inventories—sources, company universe, selected companies, H1/required outputs/knowledge items where relevant—or explicitly justifies N/A.
- `GLOBAL.time_integrity` quotes the exact frozen `effective_time_boundary`, identifies the effective dates/times used for mutable evidence, and proves no post-cutoff information contaminated the article.
- `GLOBAL.counterexample_scan` points to counterevidence, excluded peers, falsification conditions or other evidence that could have overturned the main thesis.
- `GLOBAL.required_outputs` covers required artifact identity/checksum/readback plus the audit report itself; when a connected external copy is claimed as saved/uploaded, external readback/metadata evidence is required separately from runtime artifact existence.

If visuals are enabled, also provide `<MODE>.visual_alignment`.

A DUAL task additionally provides `DUAL.cross_version_consistency`.

For `WECHAT_STICKER_POST`, provide:
- `WECHAT_STICKER_POST.platform_constraints`
- `WECHAT_STICKER_POST.title_body_payoff`
- `WECHAT_STICKER_POST.useful_body`
- `WECHAT_STICKER_POST.image_copy_complement`
- `WECHAT_STICKER_POST.compliance_risk`
- the full global key set above;
- and `WECHAT_STICKER_POST.visual_alignment` when visuals are enabled.

Evidence after the colon must point to what is actually present in the frozen final content/state. A bare PASS label, rule name, or statement such as “checked” is not acceptable evidence.

## Mechanical gates
Use deterministic code where possible for required artifacts, mandatory gate inventory, delivery channel, file identity/readback/checksum, Word styles/numbering, stock-name bolding, underlines/Markdown leakage/empty paragraphs, unambiguous actionable red-line phrases, risk/disclaimer presence/minimum substance, expected embedded image count and successful render output.

Every required artifact must have a recorded checksum before COMPLETE. A present file with no recorded checksum is an identity failure, not a PASS.

Mechanical PASS means only that those machine-checkable assertions passed. It does not prove hook quality, causal reasoning, anti-AI quality, page appearance, source completion or factual truth.

## Research completeness and time integrity
Research PASS is not established merely because the final article has citations. The auditor should trace the final thesis back through the ResearchPackage and verify:
- material user-provided sources were actually accounted for; snippets/truncated reads are not silently treated as complete originals;
- the relevant concept/company universe was broad enough for the topic and any known count mismatch is explained;
- the omission scan asked what should have been present but was missing, not only what was already processed;
- counterevidence/negative evidence was actively represented;
- mutable company/policy/order/customer/capacity facts were refreshed to the latest state effective on or before the persisted `TaskContract.effective_time_boundary`;
- market-price/market-cap/float/fund-flow/role claims use a stated comparable trading date/time at or before that cutoff and do not use later information to explain an earlier decision boundary;
- every verifiable fact that survived into the final article is supported, with stronger checks for title/lead/H1/bold/core-conclusion claims.

A tool reporting success, a search result existing, or a source being listed in notes does not prove its relevant content was read or that the claim was verified.

## Knowledge gates
Durable-knowledge recall and writeback are separate explicit decisions.

- `knowledge_context` must be `PASS` with real retrieved references when relevant durable knowledge was actually retrieved, or `N_A` with an explicit reason when no relevant/available durable source exists. It cannot remain `NOT_RUN` when RESEARCH is submitted or when the task completes.
- For A-share company/concept writing, connected StockBase/EventBase is relevant by default when actually accessible; do not use `N_A` merely as a convenience bypass.
- If `knowledge_context=N_A`, `ResearchPackage.cognition.prior_knowledge_refs` must be empty. If `knowledge_context=PASS`, any `prior_knowledge_refs` claimed by ResearchPackage must be a subset of the refs actually recorded by the recall gate; the research payload cannot invent durable references.
- `knowledge_sync` must be `PASS` with real writeback receipts or `N_A` with an explicit reason before final PASS.

Do not use `N_A` merely to bypass an available, relevant connected source or writable destination. StockBase corrections remain review-queue items; a writing run must not use generic knowledge writeback as a back door to mutate StockBase.

## Render-page evidence
A successful DOCX-to-PNG render process is not visual proof of no clipping, bad pagination, orphan headings, abnormal whitespace or broken image placement.

When render is required, the MCP path returns `writing-render://...` resources for every rendered page. The final auditor must actually inspect every returned page and include the exact inspected resource URIs in `FinalAuditDecision.reviewed_render_pages`.

Runtime PASS requires the reviewed-page set to exactly equal the expected rendered-page set. Missing or invented page receipts are a hard failure. Do not claim page inspection on the standalone diagnostic path, which intentionally does not provide those page images to the judge.

## Semantic gates
Use an independent judge for:
- evidence support, material source completion and source boundary;
- omission scan, material inventory reconciliation and time integrity;
- reasoning continuity and cross-layer transitions;
- counterevidence and `why_this / why_not`;
- title truthfulness, frozen-anchor fidelity, first-three-sentence payoff and opening-payoff fidelity;
- every frozen H1's directional conclusion, continuation gap and payoff location;
- H1/H2/H3 hierarchy need and structure-topic fit;
- bold skim-reading skeleton quality;
- information density, compression loss and company-selection logic;
- fact/inference/market-expectation/rumor separation;
- DUAL cross-version factual/evidence/conclusion consistency;
- platform fit;
- anti-AI/template fingerprints and backstage/prompt leakage;
- unsupported extreme language;
- context-sensitive financial-compliance risk;
- topic-specific risk-warning quality;
- visual/article semantic alignment and avatar treatment when visuals are enabled;
- remaining uncertainty and falsification conditions.

## Evidence audit
Do not trust `core_safe` labels blindly. Inspect the evidence ledger for the claims that materially support the title, lead, H1, bold core statements and central conclusion.

- `UNRESOLVED` cannot support a core claim.
- `SINGLE_SOURCE_ATTRIBUTED` must respect its recorded allowed wording and attribution boundary.
- `INDEPENDENTLY_CROSS_CHECKED` must actually identify independent source groups supporting the same proposition at comparable period/definition.
- Duplicate rewrites or duplicate copies of one original source do not become independent evidence merely because multiple URLs/tools are present.

If a final text introduces a material fact that is absent from the frozen research/evidence state, revise to RESEARCH rather than silently accepting the new fact.

## Revision targeting and invalidation
Use the earliest stage that can correctly repair the defect:
- `RESEARCH` for unsupported/new/conflicting facts, material source-completion defects, stale/time contamination or material universe omissions;
- `EDITORIAL` for TopicDNA, structure-generation, section-acceptance design, H1 continuation design or company-selection-basis defects;
- `TITLE` for headline/hook/frozen-headline-promise defects when research/editorial remain valid;
- `DRAFT` for prose, lead, first-three-sentence payoff, prompt leakage, bold skim skeleton, reasoning, section realization or compliance defects within a valid frozen title/structure/section contract;
- `DELIVERY` for Word/render/artifact-only defects.

A revision invalidates affected downstream PASS records and generated delivery artifacts. Never reuse stale QA because the change looked small.

## Audit report
Generate `WRITING_AUDIT_REPORT.docx` from the final state after the final semantic decision. It should expose enough evidence to distinguish actual verification from a generic PASS stamp, including:
- task/distribution/delivery contract, exact `effective_time_boundary` and required outputs;
- acceptance-contract identity, frozen headline promises, section expectations and applicable mode checks;
- source/evidence boundary and explicit supplied-source completion;
- omission scan, count reconciliation, time-integrity and counterexample evidence;
- stage-by-stage PASS/REVISE/FAIL/N/A;
- knowledge recall and writeback decisions/receipts;
- mechanical Word checks and render results;
- per-version total/body character metrics and a compression-loss judgment as diagnostics rather than length targets;
- criterion-level final acceptance evidence and repaired defects/boundaries;
- visual manifest identity when applicable;
- final artifact identities/checksums, using public-safe file identity rather than server-local paths.

A missing audit report is a completion failure under `WORD_FILE_ONLY`.

## System-error learning
When final audit discovers a defect that an already-existing rule/gate should have prevented, do not solve it by copying the same rule into more files. Treat it as a `SYSTEM_ERROR` candidate: record the symptom/root cause/where detected/why the earlier gate missed it in the audit or maintenance record, repair the canonical owner/runtime/test boundary, and add a regression case before claiming the system has learned from the failure. Until a cross-task recurrence ledger is implemented, do not falsely claim automatic global repeat-count escalation merely because this task recorded the defect.

## Visible checklist
The final chat response must include a concise checklist status covering runtime/gates, research/evidence, acceptance/structure/style/continuity, Word/render, compliance/risk disclaimer, visuals if applicable, and knowledge recall/writeback if applicable. Under `WORD_FILE_ONLY` this checklist must not paste the article body.

## Fail closed
No artifact may be COMPLETE while an applicable mandatory gate is absent, either knowledge decision remains `NOT_RUN`, a Must-Pass item lacks final evidence, a material supplied source is silently unaccounted for, the omission/count/time/counterexample decision is missing, a required output lacks a checksum, required output readback/checksum fails, a required per-mode/per-H1 acceptance-evidence key is missing, or a material source/evidence boundary remains unresolved without an explicit boundary. Changes to facts, title, headline promise, section acceptance contract, independent lead, opening, H1 structure, body logic, visual placement/assets or formatting invalidate affected checks and require re-audit.
