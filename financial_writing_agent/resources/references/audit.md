# Audit module

## Independence
The final auditor re-evaluates the frozen final content, artifacts and current runtime state. Writer self-assessment, an earlier draft review, the mere existence of a rule, or a successful tool call is not evidence of passing.

## Acceptance contract first
Before FINAL PASS, read the frozen `WritingAcceptanceContract` and the final draft/artifact state. Audit every applicable mode against the contract rather than asking only whether the article feels acceptable.

For each formal mode verify with concrete final-content evidence:
- selected title is unchanged or the contract was legitimately rebuilt;
- exactly one independent lead exists before the first H1;
- H1 count and H1 sequence match the frozen selected structure;
- side-focus statement is actually paid off in the article rather than existing only in planning metadata;
- the company-selection basis is visible in the comparison logic;
- the headline's factual anchor is supported by the research evidence boundary;
- the opening pays off the selected headline rather than switching questions;
- risk/disclaimer and required output boundaries remain satisfied.

A DUAL task additionally requires both versions to stand on their own while preserving the same factual identities, numerical facts, evidence strength, central conclusion boundary and risk boundary. Difference in structure/emphasis is expected; contradictory factual strength is not.

## Mechanical gates
Use deterministic code where possible for required artifacts, delivery channel, file identity/readback/checksum, Word styles/numbering, stock-name bolding, unambiguous actionable red-line phrases, risk/disclaimer presence/minimum substance, expected embedded image count and successful render output.

Mechanical PASS means only that those machine-checkable assertions passed. It does not prove hook quality, causal reasoning, anti-AI quality, page appearance or factual truth.

## Render-page evidence
A successful DOCX-to-PNG render process is not visual proof of no clipping, bad pagination, orphan headings, abnormal whitespace or broken image placement.

When render is required, the MCP path returns `writing-render://...` resources for every rendered page. The final auditor must actually inspect every returned page and include the exact inspected resource URIs in `FinalAuditDecision.reviewed_render_pages`.

Runtime PASS requires the reviewed-page set to exactly equal the expected rendered-page set. Missing or invented page receipts are a hard failure. Do not claim page inspection on the standalone diagnostic path, which intentionally does not provide those page images to the judge.

## Semantic gates
Use an independent judge for:
- evidence support and source boundary;
- reasoning continuity and cross-layer transitions;
- counterevidence and `why_this / why_not`;
- title truthfulness and opening payoff;
- H1 continuation value and structure-topic fit;
- information density and company-selection logic;
- DUAL cross-version factual/evidence/conclusion consistency;
- platform fit;
- anti-AI/template fingerprints;
- unsupported extreme language;
- context-sensitive financial-compliance risk;
- topic-specific risk-warning quality;
- visual/article semantic alignment and avatar treatment when visuals are enabled;
- remaining uncertainty and falsification conditions.

A PASS `FinalAuditDecision` must include concrete `acceptance_evidence` from the frozen final content. Generic statements such as “checked all rules” are insufficient.

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
- `DRAFT` for prose, lead, reasoning, section realization or compliance defects within a valid frozen structure;
- `DELIVERY` for Word/render/artifact-only defects.

A revision invalidates affected downstream PASS records and generated delivery artifacts. Never reuse stale QA because the change looked small.

## Audit report
Generate `WRITING_AUDIT_REPORT.docx` from the final state after the final semantic decision. It should expose enough evidence to distinguish actual verification from a generic PASS stamp, including:
- task/distribution/delivery contract and required outputs;
- acceptance-contract identity and applicable mode checks;
- source/evidence boundary and research coverage;
- stage-by-stage PASS/REVISE/FAIL/N/A;
- mechanical Word checks and render results;
- final semantic/red-team evidence and repaired defects/boundaries;
- knowledge reuse/writeback receipts when available;
- visual manifest identity when applicable;
- final artifact identities/checksums.

A missing audit report is a completion failure under `WORD_FILE_ONLY`.

## Visible checklist
The final chat response must include a concise checklist status covering runtime/gates, research/evidence, acceptance/structure/style/continuity, Word/render, compliance/risk disclaimer, visuals if applicable, and knowledge reuse/writeback if applicable. Under `WORD_FILE_ONLY` this checklist must not paste the article body.

## Fail closed
No artifact may be COMPLETE while an applicable Must-Pass item lacks final evidence. Changes to facts, title, independent lead, H1 structure, body logic, visual placement/assets or formatting invalidate affected checks and require re-audit.
