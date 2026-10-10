# Financial Writing System Evolution Audit — 2026-10-11

Status: IMPLEMENTED__REGRESSION_VALIDATION_IN_PROGRESS_AT_RECORD_CREATION
Scope: Financial Writing quality-promotion evidence semantics and corpus-readiness calibration

## Trigger
The user explicitly requested a Universal Continuity critique/distillation/learning/evolution inspection of the Financial Writing system. The audit was treated as a system-maintenance event, not as article drafting or a subjective self-review.

## Problem 1 — pairwise evidence could be real but semantically irrelevant
The existing quality-promotion gate required blind A/B position swap and evidence refs, but a judge run only needed a non-empty `judge_identity`, non-empty `execution_ref`, and evidence refs accepted by a boolean evidence verifier. That proved existence/trust of refs, not that those refs actually supported the claimed judge run, candidate binding, blind setup, or preference conclusion.

### Failure mode
A stale, replayed, or unrelated real trace could satisfy the evidence-ref check while being semantically unrelated to the claimed candidate-vs-baseline judgment. This repeated the same reusable failure class already discovered in Universal methodology receipts: **evidence existence is not semantic proof**.

### Candidates considered
1. Add more prose fields or richer judge receipts. Rejected: more self-description does not add independent semantics.
2. Trust a populated judge identity/execution ref once the ref resolves. Rejected: identity strings are declarations, not execution proof.
3. Split reference verification from semantic judge-run verification and bind each run to the exact candidate/change. Selected: smallest change that closes the evidence-semantics gap without adding a new policy surface.

### Implemented
`financial_writing_agent.quality_regression.evaluate_quality_promotion` now requires:
- an independent evidence-ref verifier;
- a separate independent `judge_run_verifier`;
- exact `candidate_id` and `candidate_change_ref` binding on every judge run;
- independently verified execution refs;
- execution refs unique across pairwise runs;
- existing blind A/B position swap and stability checks remain mandatory.

A real evidence ref is no longer sufficient when semantic judge-run verification is missing or fails.

## Problem 2 — corpus readiness was weaker than the written maintenance contract
The maintenance authority required "diverse complete held-out evidence spanning more than one topic family". The implementation only required at least one held-out case and at least two topic families across all complete cases. Therefore one real rejection in topic family A plus one held-out in topic family B incorrectly produced `PROMOTION_READY` even though the held-out set itself had only one topic family.

### Failure mode
The triggering failure's own topic diversity was being counted as if it were held-out diversity. This overstates generalization evidence and creates a single-held-out overfit risk.

### Candidates considered
1. Keep one held-out and rely on pairwise quality judging. Rejected: a judge cannot reveal cross-topic regression on cases never represented.
2. Require an arbitrary large fixed number of held-outs. Rejected: unnecessary corpus-size ritual; topic-family diversity is the relevant invariant.
3. Require at least two distinct complete held-out topic families per claimed content mode. Selected: directly matches the existing written contract and fails closed by content mode.

### Implemented
- `evaluate_corpus_readiness` now requires at least two complete held-out topic families.
- `evaluate_candidate_distillation` applies the same requirement per target content mode.
- Current FINANCE_DEEP corpus is downgraded from promotion-ready to diagnostic/candidate-design only: one complete real rejection plus one complete held-out topic family is insufficient.
- FINANCE_BROAD remains not ready.
- Personalized Writing DNA remains not ready and additionally still requires real positive user/edit/performance evidence after general requirements pass.

## Candidate-adoption / second-order challenge
The selected fix was re-attacked before closure:
- adding headline/style/AI-phrase rules would target symptoms and increase Goodhart pressure;
- adding another root policy would duplicate existing maintenance authority;
- richer owner-generated receipts without independent semantics would preserve self-attestation;
- treating CI as proof of better prose would exceed the evidence ceiling.

The final design changes the existing owner-local promotion harness and its metadata only. It does not add article-level prose rules and does not create another permanent policy surface.

## Validation
The first post-change CI run reached 71/71 passing unit/trajectory tests plus executable contract eval PASS, but static audit failed because the intentional `references/maintenance.md` mirror had not yet been synchronized. The test was not weakened. The mirror was repaired byte-for-byte and a new CI run was triggered.

Final closure requires a green current-head CI and authoritative reread. Until that occurs, the maintenance change must not be reported as fully committed.

## Evidence ceiling after this change
This hardening can establish stronger **REGRESSION_VERIFIED gate mechanics** once CI is green. It does not establish:
- a promotion-ready FINANCE_DEEP quality corpus;
- any successful live candidate-vs-baseline quality promotion;
- independent provider-attested semantic review;
- improved article quality or publication performance.

## Exact remaining evidence needed
1. Add a second complete FINANCE_DEEP held-out article from a distinct topic family before FINANCE_DEEP can become promotion-ready again.
2. FINANCE_BROAD needs its own complete real rejection plus at least two distinct held-out topic families.
3. A concrete candidate must pass candidate distillation.
4. Live blind pairwise runs must carry independently verified execution refs and pass the independent semantic judge-run verifier with A/B position swap.
5. Personalized Writing DNA additionally needs real user acceptance/edit or post-publication performance evidence.

## Changed authority surfaces
- `financial_writing_agent/quality_regression.py`
- `tests/test_quality_regression.py`
- `skills/financial-writing-agent/references/maintenance.md`
- `references/maintenance.md`
- `evals/quality_regression.json`
- `continuity/EXECUTION_CAPABILITIES.json`
- `continuity/UNIVERSAL_PROTOCOL_ADAPTER.json`
- this audit record

No new article-level rule module was introduced.
