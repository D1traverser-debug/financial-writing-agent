# Audit module

## Independence
The final auditor re-evaluates the frozen final content, artifacts and current runtime state. Writer self-assessment, an earlier draft review, the mere existence of a rule, or a successful tool call is not evidence of passing.

## Acceptance contract first
Before FINAL PASS, read the frozen `WritingAcceptanceContract` and the final draft/artifact state. Audit every applicable mode against the contract rather than asking only whether the article feels acceptable.

For each formal mode verify with concrete final-content evidence:
- selected title is unchanged or the contract was legitimately rebuilt;
- exactly one independent lead exists before the first H1;
- the first three sentences materially pay off the headline/information gap rather than spending the opening on generic background;
- H1 count and H1 sequence match the frozen selected structure;
- side-focus statement is actually paid off in the article rather than existing only in planning metadata;
- the company-selection basis is visible in the comparison logic;
- the headline's factual anchor is supported by the research evidence boundary;
- the opening pays off the selected headline rather than switching questions;
- bold emphasis forms a useful skim-reading information skeleton rather than decorative/random highlighting;
- reasoning remains continuous through sections and cross-layer transitions;
- risk/compliance boundaries remain satisfied.

A DUAL task additionally requires both versions to stand on their own while preserving the same factual identities, numerical facts, evidence strength, central conclusion boundary and risk boundary. Difference in structure/emphasis is expected; contradictory factual strength is not.

## Final acceptance-evidence key contract
`FinalAuditDecision.acceptance_evidence` is not a free-form summary. Every item uses exactly `KEY: concrete final-content evidence`. `KEY` is machine-checked before COMPLETE.

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

If visuals are enabled, also provide `<MODE>.visual_alignment`.

Every formal task also provides:
- `GLOBAL.evidence_boundary`
- `GLOBAL.required_outputs`

A DUAL task additionally provides `DUAL.cross_version_consistency`.

For `WECHAT_STICKER_POST`, provide:
- `WECHAT_STICKER_POST.platform_constraints`
- `WECHAT_STICKER_POST.title_body_payoff`
- `WECHAT_STICKER_POST.useful_body`
- `WECHAT_STICKER_POST.image_copy_complement`
- `WECHAT_STICKER_POST.compliance_risk`
- `GLOBAL.evidence_boundary`
- `GLOBAL.required_outputs`
- and `WECHAT_STICKER_POST.visual_alignment` when visuals are enabled.

Evidence after the colon must point to what is actually present in the frozen final content/state. A bare PASS label, rule name, or statement such as “checked” is not acceptable evidence.

## Mechanical gates
Use deterministic code where possible for required artifacts, mandatory gate inventory, delivery channel, file identity/readback/checksum, Word styles/numbering, stock-name bolding, underlines/Markdown leakage/empty paragraphs, unambiguous actionable red-line phrases, risk/disclaimer presence/minimum substance, expected embedded image count and successful render output.

Every required artifact must have a recorded checksum before COMPLETE. A present file with no recorded checksum is an identity failure, not a PASS.

Mechanical PASS means only that those machine-checkable assertions passed. It does not prove hook quality, causal reasoning, anti-AI quality, page appearance or factual truth.

## Knowledge gates
Durable-knowledge recall and writeback are separate explicit decisions.

- `knowledge_context` must be `PASS` with real retrieved references when relevant durable knowledge was actually reused, or `N_A` with an explicit reason when no relevant/available durable source exists. It cannot remain `NOT_RUN` when RESEARCH is submitted or when the task completes.
- `knowledge_sync` must be `PASS` with real writeback receipts or `N_A` with an explicit reason before final PASS.

Do not use `N_A` merely to bypass an available, relevant connected source or writable destination.

## Render-page evidence
A successful DOCX-to-PNG render process is not visual proof of no clipping, bad pagination, orphan headings, abnormal whitespace or broken image placement.

When render is required, the MCP path returns `writing-render://...` resources for every rendered page. The final auditor must actually inspect every returned page and include the exact inspected resource URIs in `FinalAuditDecision.reviewed_render_pages`.

Runtime PASS requires the reviewed-page set to exactly equal the expected rendered-page set. Missing or invented page receipts are a hard failure. Do not claim page inspection on the standalone diagnostic path, which intentionally does not provide those page images to the judge.

## Semantic gates
Use an independent judge for:
- evidence support and source boundary;
- reasoning continuity and cross-layer transitions;
- counterevidence and `why_this / why_not`;
- title truthfulness, first-three-sentence payoff and opening payoff;
- H1 continuation value and structure-topic fit;
- bold skim-reading skeleton quality;
- information density and company-selection logic;
- DUAL cross-version factual/evidence/conclusion consistency;
- platform fit;
- anti-AI/template fingerprints;
- unsupported extreme language;
- context-sensitive financial-compliance risk;
- topic-specific risk-warning quality;
- visual/article semantic alignment and avatar treatment when visuals are enabled;
- remaining uncertainty and falsification conditions.

## Evidence audit
Do not trust `core_safe` labels blindly. Inspect the evidence ledger for the claims that materially support the title, lead, H1 and central conclusion.

- `UNRESOLVED` cannot support a core claim.
- `SINGLE_SOURCE_ATTRIBUTED` must respect its recorded allowed wording and attribution boundary.
- `INDEPENDENTLY_CROSS_CHECKED` must actually identify independent source groups supporting the same proposition at comparable period/definition.
- Duplicate rewrites or duplicate copies of one original source do not become independent evidence merely because multiple URLs/tools are present.

If a final text introduces a material fact that is absent from the frozen research/evidence state, revise to RESEARCH rather than silently accepting the new fact.

## Revision targeting and invalidation
Use the earliest stage that can correctly repair the defect:
- `RESEARCH` for unsupported/new/conflicting facts or material universe omissions;
- `EDITORIAL` for TopicDNA, structure-generation or company-selection-basis defects;
- `TITLE` for headline/hook defects when research/editorial remain valid;
- `DRAFT` for prose, lead, first-three-sentence payoff, bold skim skeleton, reasoning, section realization or compliance defects within a valid frozen structure;
- `DELIVERY` for Word/render/artifact-only defects.

A revision invalidates affected downstream PASS records and generated delivery artifacts. Never reuse stale QA because the change looked small.

## Audit report
Generate `WRITING_AUDIT_REPORT.docx` from the final state after the final semantic decision. It should expose enough evidence to distinguish actual verification from a generic PASS stamp, including:
- task/distribution/delivery contract and required outputs;
- acceptance-contract identity and applicable mode checks;
- source/evidence boundary and research coverage;
- stage-by-stage PASS/REVISE/FAIL/N/A;
- knowledge recall and writeback decisions/receipts;
- mechanical Word checks and render results;
- criterion-level final acceptance evidence and repaired defects/boundaries;
- visual manifest identity when applicable;
- final artifact identities/checksums, using public-safe file identity rather than server-local paths.

A missing audit report is a completion failure under `WORD_FILE_ONLY`.

## Visible checklist
The final chat response must include a concise checklist status covering runtime/gates, research/evidence, acceptance/structure/style/continuity, Word/render, compliance/risk disclaimer, visuals if applicable, and knowledge recall/writeback if applicable. Under `WORD_FILE_ONLY` this checklist must not paste the article body.

## Fail closed
No artifact may be COMPLETE while an applicable mandatory gate is absent, either knowledge decision remains `NOT_RUN`, a Must-Pass item lacks final evidence, a required output lacks a checksum, required output readback/checksum fails, or a required acceptance-evidence key is missing. Changes to facts, title, independent lead, opening, H1 structure, body logic, visual placement/assets or formatting invalidate affected checks and require re-audit.
