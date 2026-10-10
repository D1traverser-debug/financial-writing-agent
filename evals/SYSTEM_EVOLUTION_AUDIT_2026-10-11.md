# Financial Writing System Evolution Audit — 2026-10-11

Status: IMPLEMENTED_AND_OWNER_REGRESSION_PASS__LIVE_QUALITY_EVIDENCE_PENDING
Scope: Financial Writing quality-promotion evidence semantics and corpus-readiness calibration

## Trigger
The user explicitly requested a Universal Continuity critique/distillation/learning/evolution inspection of the Financial Writing system. The audit was treated as a system-maintenance event, not article drafting or subjective self-review.

## Findings and root causes

### 1. Pairwise evidence could be real but semantically irrelevant
The previous promotion gate required blind A/B position swap and verified evidence refs, but only checked that `judge_identity` and `execution_ref` were populated and that evidence refs resolved. It did not independently establish that those refs actually supported this exact judge run, candidate binding, blind setup or preference conclusion.

This is the reusable failure class **evidence existence is not semantic proof**. A stale, replayed or unrelated real trace could otherwise look admissible.

Candidates considered:
1. richer owner-generated prose/receipts — rejected because self-description is not independent semantics;
2. trust populated judge identity/execution refs once they resolve — rejected because identity strings are declarations, not execution proof;
3. split reference verification from semantic judge-run verification and bind every run to the exact candidate/change — selected as the smallest testable repair.

Implemented in `financial_writing_agent.quality_regression.evaluate_quality_promotion`:
- independent evidence-ref verifier;
- separate independent `judge_run_verifier`;
- exact `candidate_id` and `candidate_change_ref` binding on every judge run;
- independently verified execution refs;
- execution refs unique across pairwise runs;
- blind A/B position swap and stability checks remain mandatory.

### 2. Corpus readiness was weaker than the written maintenance contract
The maintenance authority required diverse complete held-out evidence spanning more than one topic family. The old implementation required one held-out case plus two topic families across all complete cases. One rejection in family A plus one held-out in family B therefore incorrectly produced promotion readiness even though the held-out set itself contained only one family.

Candidates considered:
1. keep one held-out and rely on pairwise judging — rejected because unseen cross-topic regression cannot be detected;
2. require a large arbitrary fixed corpus — rejected as ritual rather than an invariant;
3. require at least two distinct complete held-out topic families per claimed content mode — selected because it matches the existing authority and fails closed by mode.

Implemented:
- `evaluate_corpus_readiness` requires at least two complete held-out topic families;
- `evaluate_candidate_distillation` enforces the same requirement per target content mode;
- current FINANCE_DEEP evidence is diagnostic/candidate-design only, not promotion-ready;
- FINANCE_BROAD remains not ready;
- Personalized Writing DNA remains not ready and additionally requires real user acceptance/edit or post-publication performance evidence after general requirements pass.

## Second-order challenge
The accepted fix was re-attacked before closure. Adding title/style/AI-phrase rules would target symptoms and increase Goodhart pressure. Adding another root policy would duplicate existing maintenance authority. Richer self-receipts would preserve self-attestation. Treating CI as proof of better prose would exceed the evidence ceiling. The final repair therefore changes the existing owner-local promotion harness and its metadata only; no new article-level prose-rule module was introduced.

## Validation history
1. Initial hardened-gate run `38069467849` reached 71/71 unit/trajectory PASS and executable contract eval PASS, then static audit correctly failed on stale `maintenance.md` mirror drift. The mirror was repaired rather than weakening the audit.
2. Run `38069792883` then exposed one stale regression assertion expecting execution capability profile v5 after the intentional v6 contract hardening. The test was upgraded to assert v6 **and** the new semantic-verifier / held-out-diversity / candidate-binding invariants.
3. Final behavioral head `38ab669d91816291c5575c93d8be27ed4a336cbc`, GitHub Actions run `38069902882`, job `114265021061`: PASS across OpenAI Agents SDK surface smoke, MCP Streamable HTTP smoke, unit/trajectory suite, executable contract eval baseline, static rule ownership/bundle audit, isolated wheel install and DOCX render smoke.

This establishes **REGRESSION_VERIFIED gate mechanics** for the covered hardening. It does not establish better prose quality.

## Evidence ceiling / remaining open gates
The audit does **not** prove:
- a promotion-ready FINANCE_DEEP corpus;
- a successful live candidate-vs-baseline quality promotion;
- provider-attested isolated semantic review;
- improved article quality or publication performance.

Exact remaining evidence:
1. a second complete FINANCE_DEEP held-out article from a distinct topic family;
2. for FINANCE_BROAD, its own complete real rejection plus at least two distinct held-out topic families;
3. a concrete candidate-distillation PASS;
4. live blind pairwise runs with independently verified execution refs and independent semantic judge-run verification, with A/B position swap;
5. for Personalized Writing DNA, real user acceptance/edit or post-publication performance evidence in addition to all general requirements.

## Changed authority surfaces
- `financial_writing_agent/quality_regression.py`
- `tests/test_quality_regression.py`
- `tests/test_execution_capability_entrypoint.py`
- `skills/financial-writing-agent/references/maintenance.md`
- `references/maintenance.md`
- `financial_writing_agent/resources/references/maintenance.md`
- `evals/quality_regression.json`
- `continuity/EXECUTION_CAPABILITIES.json`
- `continuity/UNIVERSAL_PROTOCOL_ADAPTER.json`
- this audit record

No article-level writing rule was added merely to satisfy the triggering failure.
