# Financial Writing 1.0.1 Post-Review Hotfix — 2026-10-15

Owner: `DOMAIN:financial_writing`
Trigger: post-promotion Codex review of PR #35 after Financial Writing 1.0.0 reached `main`.
Disposition: `DOMAIN_CANDIDATE` -> candidate hotfix branch -> PR -> CI -> controlled promotion if green.

## Detected defects

1. P1 — persisted `quality_evidence` was only shape-checked as a mapping. A stored 1.0 state could have admitted publication fitness removed or altered after the original transition and still later reach `FINAL_AUDIT` through the lower-level owner guard.
2. P1 — after stage-aware validation was added to `current_admission`, the public lower-level `owner_guard.advance_state` and owner-lifecycle helpers still accepted current 1.0 states directly. This meant callers could bypass the new quality validator simply by using the lower layer.
3. P1 — `PublicationFitness.assurance=INDEPENDENT_EXECUTOR` could be asserted from caller-supplied identities/reference without trusted execution resolution, so a same-session caller could overstate independence.
4. P2 — search saturation required two no-delta terminal sweeps but did not ensure the final two sweeps were materially different; repeated, cosmetically renamed, or blank/duplicate-family searches could therefore masquerade as saturation.

## Root cause

The 1.0 rebuild correctly added admission-time contracts but initially treated current quality admission as a wrapper responsibility rather than a state invariant that every owner-level mutation must preserve. It also under-specified assurance provenance and terminal-pair search diversity. Candidate CI verified implemented invariants but did not initially include adversarial regressions for lower-layer bypass, post-admission mutation, assurance spoofing, and pseudo-diversity paths.

## Repairs

- `owner_guard` now separates base state validation from public state validation. Any state carrying `writing_kernel_version=1.0` is quality-validated at the owner boundary, regardless of whether the caller enters through `current_admission`, direct `owner_guard` APIs, or owner-lifecycle helpers.
- `current_admission` calls only owner base validation when it performs its own full quality parse, preventing recursive dispatch.
- During a legitimate current-admission transition, a process-local sentinel defers the owner callback only while the new owner receipt exists without its not-yet-attached quality digest. The sentinel is an internal sequencing mechanism, not an authorization or persistence boundary. Before returning, `current_admission` attaches the digest/path bindings and performs full current validation.
- Quality invalidation is centralized in `owner_guard._invalidate_from`: RESEARCH clears all current quality evidence; EDITORIAL clears story blueprints and publication fitness; TITLE/DRAFT clear publication fitness. Owner-lifecycle recovery therefore cannot retain stale quality evidence.
- Each persisted quality object must match the digest from its correct admitting-stage `current_admission` receipt: RESEARCH for `DecisionEnvelope`, EDITORIAL for `StoryBlueprint`, EDITORIAL_AUDIT for `PublicationFitness`. A later unrelated receipt cannot spoof the binding.
- Current Financial GITHUB_CHAT cannot independently resolve a caller-supplied execution reference against trusted independent execution evidence. Therefore `PublicationFitness.assurance=INDEPENDENT_EXECUTOR` is fail-closed and rejected in the current contract; publication fitness remains `CHAT_SELF_REVIEW` until an owner-native trusted resolver exists. Merely supplying distinct reviewer/author strings is not evidence of independence.
- `SearchSweep.source_families` rejects blank entries and duplicates after case/whitespace normalization.
- `SearchSaturation` requires the final two stable sweeps to differ in both normalized query/scope and normalized source-family set. Exact repetition cannot prove saturation, and merely renaming a query while reusing the same source mix is rejected.

## Regression targets

- a direct lower-level owner transition cannot leave RESEARCH without admitted DecisionEnvelope evidence;
- a direct lower-level DELIVERY transition rejects missing/tampered publication fitness before mutation;
- blocked owner-lifecycle recovery to RESEARCH centrally invalidates stale quality evidence and remains valid afterward;
- missing persisted publication fitness fails validation;
- semantically valid but post-admission modified publication fitness fails receipt-digest validation;
- a later wrong-stage receipt carrying a forged matching digest cannot override the original admitting-stage digest;
- review revision to `RESEARCH` removes stale admitted quality evidence;
- every current `INDEPENDENT_EXECUTOR` publication-fitness claim fails without a trusted execution resolver, including superficially plausible distinct identities/reference;
- ordinary `CHAT_SELF_REVIEW` remains valid;
- blank or normalized-duplicate source families fail;
- identical final no-delta search sweeps fail even when earlier source-family diversity exists;
- differently named final sweeps over the same source-family set fail saturation.

## Version semantics

- package release: `1.0.1` candidate;
- writing kernel/state marker: remains `1.0` (no state-protocol generation change);
- capability profile: remains `18` (no new UAOS capability dependency);
- UAOS common capability minimum: remains `1.6.0`.

## Assurance boundary

Receipt-digest revalidation is an execution-governance consistency check, not a cryptographic security boundary. Repository commit/state provenance remains the stronger persistence boundary. The internal current-admission sentinel only sequences construction of a receipt and cannot establish stronger assurance. Same-session semantic review remains `CHAT_SELF_REVIEW`; independent assurance may be claimed only after a future trusted execution resolver can prove distinct execution provenance.

## Closure condition

Do not mark repaired until the final PR head passes unit/trajectory tests, executable contract eval, static authority audits, isolated 1.0.1 wheel smoke and DOCX render smoke; the final head must also receive review with no unresolved material findings before controlled merge. After merge, reread `main` and require a successful `main` push CI. Live reader-value observation remains open after this mechanical/assurance hotfix.
