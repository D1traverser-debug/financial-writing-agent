# Financial Writing 1.0.1 Post-Review Hotfix — 2026-10-15

Owner: `DOMAIN:financial_writing`
Trigger: post-promotion Codex review of PR #35 after Financial Writing 1.0.0 reached `main`.
Disposition: `DOMAIN_CANDIDATE` -> candidate hotfix branch -> PR -> CI -> controlled promotion if green.

## Detected defects

1. P1 — persisted `quality_evidence` was only shape-checked as a mapping. A stored 1.0 state could have admitted publication fitness removed or altered after the original transition and still later reach `FINAL_AUDIT` through the lower-level owner guard.
2. P1 — `PublicationFitness.assurance=INDEPENDENT_EXECUTOR` was not bound to reviewer/author/execution provenance, so a same-session caller could overstate independence.
3. P2 — search saturation required two no-delta terminal sweeps but did not ensure the final two sweeps were materially different; repeated identical searches could therefore satisfy saturation when earlier sweeps supplied source diversity.

## Root cause

The 1.0 rebuild correctly added admission-time contracts but under-specified revalidation of persisted evidence, assurance provenance, and the terminal-pair semantics of saturation. Candidate CI verified implemented invariants but did not contain adversarial regressions for these three post-admission mutation paths.

## Repairs

- `current_admission.validate_state()` becomes stage-aware and reparses required persisted `DecisionEnvelope`, `StoryBlueprint`, and `PublicationFitness` records. Each required record must match the most recent corresponding SHA-256 binding in execution receipts.
- Any review revision route now invalidates quality evidence according to the revision target, not only `EDITORIAL_AUDIT` revisions.
- `PublicationFitness` binds `AuditProvenance`; `INDEPENDENT_EXECUTOR` requires explicit distinct reviewer/author identities and an execution reference. Otherwise assurance remains `CHAT_SELF_REVIEW`.
- `SearchSaturation` requires the final two stable sweeps to differ in normalized scope or source-family set; exact repetition cannot prove saturation.

## Regression targets

- missing persisted publication fitness fails validation;
- semantically valid but post-admission modified publication fitness fails receipt-digest validation;
- revision to `RESEARCH` removes stale admitted quality evidence;
- independent fitness without bound provenance fails;
- same reviewer/author independent provenance fails;
- explicit distinct independent provenance passes;
- identical final no-delta search sweeps fail even when earlier source-family diversity exists.

## Version semantics

- package release: `1.0.1` candidate;
- writing kernel/state marker: remains `1.0` (no state-protocol generation change);
- capability profile: remains `18` (no new UAOS capability dependency);
- UAOS common capability minimum: remains `1.6.0`.

## Closure condition

Do not mark repaired until PR CI passes unit/trajectory tests, executable contract eval, static authority audits, isolated 1.0.1 wheel smoke and DOCX render smoke, followed by merge to `main`, production reread and successful `main` push CI. Live reader-value observation remains open after this mechanical/assurance hotfix.
