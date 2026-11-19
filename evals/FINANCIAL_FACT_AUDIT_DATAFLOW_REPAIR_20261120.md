# Financial Fact Audit Dataflow Repair — 2026-11-20

Status: `DRAFT_CANDIDATE__EXACT_CODE_HEAD_CI_PASS__INDEPENDENT_REVIEW_OPEN__NOT_MERGED`

Owner: `DOMAIN:financial_writing`

Candidate: PR #95 — `repair/fact-and-interaction-audit-dataflow-20261120`

## Executive result

The long-form fact audit and the platform-interaction branch did not receive the complete research decision context needed to verify company-to-metric attribution. The defect was in the declared pass input contracts, not merely in the wording of the audit policy.

The candidate now passes the exact code-head CI: 774 tests, 87% Python statement coverage, 81% Writing Kernel coverage, all 35 workflow steps successful. This is engineering evidence only. The PR remains Draft and is not merged.

## User outcome protected

Financial Writing must produce evidence-bounded content across different finance topics and product modes. The business workflow remains the canonical ten stages; content form, research modules and comparisons remain conditional on the user's actual task. A correct number attached to the wrong company is still a factual error.

The motivating recent writing sample contained a company-specific cash-flow direction mismatch despite the underlying company figures being available. That sample is a diagnostic trigger, not independent editorial certification or a quality-promotion case.

## Evidence and root cause

1. In `financial_writing_agent/writing_kernel.py`, the former `FACT_INTEGRITY_AUDIT` contract declared only `edited_draft`, `evidence_ledger` and `product_mode`.
2. `_invoke_pass` forwards only the pass contract's declared required inputs. Context remaining in the shared state is not automatically visible to the model callback.
3. `audited_evidence` is admitted at the Research Audit boundary; `selected_thesis`, `company_decision_map` and `change_conditions` are produced by Thesis Adjudication; `publication_distillation` is produced by Private Research Synthesis. Those values were available upstream but were not declared as Fact Audit inputs.
4. The platform-interaction adaptation and audit contracts had the same omission for the adjudicated company comparison and change conditions.
5. The production stage path builds each long-form audit branch from shared research context plus product context, and the interaction branch from shared research context plus interaction context. The missing boundary was therefore the pass contract, not a separate stage or a missing shared-state store.

Root cause: **the semantic audit's declared input boundary was narrower than the evidence and decision boundary it was responsible for checking.** The system could preserve the correct comparison upstream yet ask the audit model to certify the article without seeing that comparison.

## Competing explanations and rejected repairs

- **One-off writer typo only:** insufficient. It explains the observed sentence but not why the audit could not independently compare the sentence with the admitted company decision.
- **Add a deterministic company-name/number regex:** rejected as the primary repair. Lexical checks cannot reliably establish semantic entailment across entity, metric, period, unit, direction and comparator.
- **Add another agent or business stage:** rejected. The existing Fact Integrity and Interaction Audit responsibilities are correct; adding orchestration would increase complexity without fixing the missing evidence contract.
- **Expand the existing pass contracts and make the audit protocol explicit:** selected. This fixes the narrowest shared cause while preserving the ten-stage workflow and product boundaries.

## Implemented in the candidate

- `FACT_INTEGRITY_AUDIT` now receives `audited_evidence`, `selected_thesis`, `company_decision_map`, `change_conditions` and `publication_distillation`, in addition to its existing draft/evidence/product inputs.
- Platform-interaction adaptation and audit receive the same decision context.
- The authoritative audit reference now requires claim normalization across entity, metric, period, value/unit, direction, comparator/scope and exact evidence binding. Each company row must be checked independently; sentence order, list order and aggregate correctness cannot prove attribution.
- The Financial Skill explicitly routes both audit passes through the authoritative audit reference; the packaged runtime mirror is byte-identical.
- Execution contract and manifest dataflow declarations are synchronized.
- Regression tests verify exact `_invoke_pass` forwarding, dataflow availability, interaction context, Skill routing and contract/manifest parity.
- No new business stage, universal article template, new task classifier or second owner was introduced.

## Exact code-head verification

- PR: [#95](https://github.com/D1traverser-debug/financial-writing-agent/pull/95)
- Candidate code head: `fc64deb4562bf6851eda1e3e33847f8cb2b32be8`
- Exact-head CI: [44583877013](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/44583877013) — `success`
- Tests: 774 passed.
- Python statement coverage: 87% overall (9,051 statements; 1,207 missed).
- Module coverage: Portfolio Coordinator 87%; Standalone Runtime 89%; Writing Kernel 81%.
- Whole-tree audit: 356 tracked files, 140 Python AST parses, 55 JSON parses, 60,590 decoded text lines, zero warnings and zero errors.
- Standalone wheel build/install, DOCX render smoke, four synthetic Word product/page checks and Financial negative-case business replay passed.
- Financial Skill size: 11,985 UTF-8 bytes, within the 12,000-byte router ceiling.

## Assurance boundary and remaining OPEN items

- PR #95 remains Draft and not merged; independent technical review has not been obtained.
- The current private ChatGPT plugin remains version 0.1.4; this candidate has not been packaged into a new release or verified in a fresh native client session.
- Financial Provider Action remains `NOT_DEPLOYED`; no live provider-backed article stage was executed.
- The audit remains a model semantic judgment. This PR makes the required evidence available and makes the audit protocol explicit; it does not create a deterministic proof of semantic entailment.
- No real article was generated and independently reviewed under this candidate. Real cross-topic quality, user acceptance and post-publication performance remain OPEN.
- Existing Finance Deep, Finance Broad and Platform Interaction quality-readiness ceilings remain unchanged.

No CAOS source, runtime, host, permission or business-state file was modified.

## Next legal action

Obtain independent technical review of PR #95. If accepted, integrate it through the existing protected-main process, then package and verify the updated private Skill in a fresh session. Separately run real tasks across materially different finance topic families and requested products, with independent factual/editorial review. Do not promote article quality from CI or same-session review.


## Full PR snapshot verification

The full PR snapshot at `fc64deb4562bf6851eda1e3e33847f8cb2b32be8`, including the problem journal, evolution index and audit report, passed [exact PR snapshot CI run 44583877013](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/44583877013): 775 tests passed, 87% overall Python statement coverage, Writing Kernel 81%, all 35 workflow steps successful. Whole-tree audit: 356 tracked files, 140 Python AST parses, 55 JSON parses, 60,590 decoded text lines, zero warnings/errors. This is the full candidate snapshot check; it remains engineering evidence and does not close independent review, live-client activation or real editorial acceptance.


## Branch-history integrity correction

The initial candidate was assembled as a sequence of GitHub Contents API file commits. That did not follow this repository's required atomic candidate-write protocol. Before review, the branch is being reconstructed from the unchanged `main` base as one Git tree/commit using `create_blob → create_tree → create_commit → update_ref(expected_sha)`. The ref update is protected by the observed branch-head lease; `main` is not changed. The reconstructed exact head must pass CI again. This is a process correction, not a code-scope expansion.
