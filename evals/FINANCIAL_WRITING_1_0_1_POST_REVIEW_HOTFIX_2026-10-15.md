# Financial Writing 1.0.1 Post-Review Hotfix — 2026-10-15

Owner: `DOMAIN:financial_writing`
Trigger: post-promotion Codex review of PR #35 after Financial Writing 1.0.0 reached `main`.
Disposition: `DOMAIN_CANDIDATE` -> candidate hotfix branch -> PR -> CI -> controlled promotion if green.

## Detected defects

1. P1 — persisted `quality_evidence` was only shape-checked as a mapping. A stored 1.0 state could have admitted publication fitness removed or altered after the original transition and still later reach `FINAL_AUDIT` through the lower-level owner guard.
2. P1 — `PublicationFitness.assurance=INDEPENDENT_EXECUTOR` was not bound to reviewer/author/execution provenance, so a same-session caller could overstate independence.
3. P2 — search saturation required two no-delta terminal sweeps but did not ensure the final two sweeps were materially different; repeated or cosmetically renamed searches could therefore satisfy saturation when earlier sweeps supplied source diversity.

## Root cause

The 1.0 rebuild correctly added admission-time contracts but under-specified revalidation of persisted evidence, assurance provenance, and the terminal-pair semantics of saturation. Candidate CI verified implemented invariants but did not contain adversarial regressions for these post-admission mutation and pseudo-diversity paths.

## Repairs

- `current_admission.validate_state()` is stage-aware and reparses required persisted `DecisionEnvelope`, `StoryBlueprint`, and `PublicationFitness` records.
- Each persisted quality object must match the digest from its correct admitting-stage `current_admission` receipt: RESEARCH for `DecisionEnvelope`, EDITORIAL for `StoryBlueprint`, EDITORIAL_AUDIT for `PublicationFitness`. A later unrelated receipt cannot spoof the binding.
- Any review revision route invalidates quality evidence according to the revision target, not only `EDITORIAL_AUDIT` revisions.
- `PublicationFitness` binds `AuditProvenance`; `INDEPENDENT_EXECUTOR` requires nonblank explicit reviewer/author identities, a nonblank execution reference, and reviewer != author. Otherwise assurance remains `CHAT_SELF_REVIEW`.
- `SearchSweep.source_families` rejects blank entries and duplicates after case/whitespace normalization.
- `SearchSaturation` requires the final two stable sweeps to differ in both normalized query/scope and normalized source-family set. Exact repetition cannot prove saturation, and merely renaming a query while reusing the same source mix is rejected.

## Regression targets

- missing persisted publication fitness fails validation;
- semantically valid but post-admission modified publication fitness fails receipt-digest validation;
- a later wrong-stage receipt carrying a forged matching digest cannot override the original admitting-stage digest;
- revision to `RESEARCH` removes stale admitted quality evidence;
- independent fitness without bound provenance fails;
- same reviewer/author independent provenance fails;
- blank reviewer or author identity fails independent provenance;
- explicit distinct independent provenance passes;
- blank or normalized-duplicate source families fail;
- identical final no-delta search sweeps fail even when earlier source-family diversity exists;
- differently named final sweeps over the same source-family set fail saturation.

## Version semantics

- package release: `1.0.1` candidate;
- writing kernel/state marker: remains `1.0` (no state-protocol generation change);
- capability profile: remains `18` (no new UAOS capability dependency);
- UAOS common capability minimum: remains `1.6.0`.

## Assurance boundary

Receipt-digest revalidation is an execution-governance consistency check, not a cryptographic security boundary. Repository commit/state provenance remains the stronger persistence boundary. Same-session semantic review remains `CHAT_SELF_REVIEW` unless distinct execution provenance is actually present.

## Closure condition

Do not mark repaired until the final PR head passes unit/trajectory tests, executable contract eval, static authority audits, isolated 1.0.1 wheel smoke and DOCX render smoke; the final head must also receive review with no unresolved material findings before controlled merge. After merge, reread `main` and require a successful `main` push CI. Live reader-value observation remains open after this mechanical/assurance hotfix.
