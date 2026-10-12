# Phase 1 — Canonical Workflow Kernel Audit — 2026-10-12

Status: CANDIDATE UNDER FINAL PHASE-1 REVIEW
Parent program: `evals/FINANCIAL_FULL_SYSTEM_REBUILD_2026-10-12.md`
Phase-0 map: `evals/PHASE0_SYSTEM_AUTHORITY_AND_FLOW_MAP_2026-10-12.md`
PR: #15
Branch: `maintenance/phase1-workflow-kernel-20261012`
Base main: `098746d07f0d9ca55574d8012457e922a612ea2a`

## 1. Trigger / problem

Phase 0 confirmed a material control-plane defect inside Financial: one intended business workflow was independently hand-maintained in owner-native engine/controller, GitHub-chat guard/contract and runtime-service invalidation/revision validators. This was not only a theoretical drift risk.

A concrete inconsistency was found before implementation:

- `controller.py` explicitly routes `DRAFT` with `draft_output=REVISE` back to `DRAFT`;
- the prior `engine.ALLOWED_TRANSITIONS[Stage.DRAFT]` did not include `Stage.DRAFT`.

Therefore a deterministic draft guard could legitimately request a rewrite that the lower engine rejected. The duplicate control truth had already produced behavior inconsistency.

## 2. Candidate competition

### A — Keep independent Python/chat graphs and add more parity tests
Rejected as primary architecture. Tests would detect some drift after it occurs but would preserve multiple machine truths. The discovered DRAFT self-loop mismatch demonstrates the cost already exists.

### B — Make Python runtime the only workflow and require every GPT chat to invoke it
Rejected for the current user operating mode. The user explicitly operates GitHub-mounted + GPT chat without a deployed owner-native plugin in every session. Forcing an unavailable runtime would either block ordinary use or recreate a free-form bypass pressure.

### C — One canonical business workflow kernel + adapter narrowing
Selected. One code-owned specification owns business-permitted stage order, PASS edges, revision targets and dependency/invalidation order. OWNER_NATIVE and GITHUB_CHAT remain separate execution/persistence/assurance adapters and may be stricter than the kernel, but may not invent broader business routes.

### D — Fully unify persistence/assurance/state representations in Phase 1
Rejected. GitHub CAS/blob identity and owner-native store/semantic-proof state are materially different evidence boundaries. Flattening them would confuse architecture convergence with evidence-model convergence and risk assurance inflation.

## 3. Implementation

New canonical surface: `financial_writing_agent/workflow_spec.py`.

It owns:

- `BUSINESS_STAGE_ORDER` / names;
- `PASS_TARGET`;
- `REVISION_TARGETS`;
- recoverable stages;
- review-stage classification;
- stage→gate dependency ownership;
- legal graph derivation;
- invalidated stage/gate derivation.

Migrated consumers:

- `engine.py` derives its legal graph/recoverable stages from the kernel;
- `controller.py` derives PASS/revision targets from the kernel;
- `github_chat_guard.py` derives stage order, forward routes, review revision targets and invalidation stages from the kernel;
- `GITHUB_CHAT_EXECUTION.json` no longer owns an independent stage list and points at kernel symbols instead;
- `AGENT_MANIFEST.json` declares the kernel in workflow transition authority.

Adapter-specific boundaries preserved:

- chat remains `CHAT_SELF_REVIEW` / self-attested action receipts;
- FINAL_AUDIT's canonical owner-native target is COMPLETE, but chat translates that into `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`;
- GitHub blob-SHA CAS is still chat-specific;
- owner-native semantic PASS proof remains Python-state specific;
- store/artifact representations are not unified in this phase.

## 4. Temporary duplicated implementation explicitly bounded

`runtime_service.py` still hand-maintains two implementation details that Phase 2 will remove when that file is already being changed for task discovery/recovery:

1. revision cleanup gate-name tuples;
2. public submit revision-target literal sets.

This duplication is not left unchecked. `tests/test_workflow_spec.py` parses the actual service source and requires both sets to equal the canonical kernel. A mismatch fails the phase regression. Adapter-specific working-key/artifact/knowledge cleanup stays local by design.

## 5. Second-order attacks and defects found

### 5.1 DRAFT revision self-loop mismatch
Confirmed pre-existing defect. Fixed by canonical `REVISION_TARGETS[Stage.DRAFT]={Stage.DRAFT}` and derived engine graph. Direct regression added.

### 5.2 Low-level COMPLETE semantic bypass
Second-order attack showed `WritingEngine.transition(state, Stage.COMPLETE)` could move a FINAL_AUDIT state to COMPLETE without `assert_can_complete()`, required artifacts or semantic proof. This was reproducibly executed before the fix.

Repair:

- private `_apply_transition()` owns raw graph application;
- public `transition()` refuses COMPLETE;
- only `complete()` calls `_apply_transition(... COMPLETE)` after `assert_can_complete()`.

### 5.3 Low-level BLOCKED/recovery bypass
The same raw transition API could enter BLOCKED without reason/recovery cursor, or leave BLOCKED without clearing recovery metadata.

Repair:

- public `transition()` refuses direct entry to BLOCKED;
- public `transition()` refuses any departure while current stage is BLOCKED;
- `block()` / `resume_blocked()` own those semantic transitions;
- tests cover entry, exit and metadata clearing.

### 5.4 Private primitive future bypass
Because Python privacy is conventional, a regression scans package modules and requires `_apply_transition(` to remain engine-local. Adding a direct caller elsewhere fails tests.

### 5.5 Stale harness enforcing shadow authority
`tests/test_github_chat_execution.py` still required `GITHUB_CHAT_EXECUTION.json.workflow.stage_order`, which would force preservation of the duplicate stage list Phase 1 is deleting.

The test was reconciled to canonical `BUSINESS_STAGE_NAMES`; evidence, assurance and fail-closed assertions were preserved. This is harness cleanup, not weakening business semantics.

## 6. Validation performed

### 6.1 Exact-code targeted owner-native execution
PASS in isolated Python execution using current branch workflow/engine/controller semantics:

- kernel graph contains legal DRAFT→DRAFT revision;
- engine compatibility transition surface equals canonical graph;
- controller DRAFT REVISE returns to DRAFT;
- illegal DRAFT→TITLE is rejected;
- invalidation gate order derives as expected.

### 6.2 Exact GitHub-chat guard blob execution
The branch guard source was reconstructed byte-for-byte and Git blob SHA independently matched:

`080cdfe722b93c256327055f3bb9767ca55ef648`.

PASS:

- full guarded path from INTAKE through FINAL_AUDIT;
- 11 action-bound receipts including initialization;
- terminal status remains `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`, never COMPLETE;
- direct COMPLETE status pollution is rejected;
- EDITORIAL_AUDIT REVISE→RESEARCH invalidates all target/downstream active stage artifacts and review decisions.

### 6.3 Package-composition harness
PASS with current Pydantic WritingState/model behavior, SQLite store semantics, kernel, engine/controller and exact chat guard:

- owner-native DRAFT self-revision works;
- chat full path remains bounded terminal;
- no adapter-assurance flattening observed in the exercised path.

### 6.4 Special-transition fault harness after second-order repair
PASS:

- raw FINAL_AUDIT→COMPLETE rejected;
- raw stage→BLOCKED rejected;
- raw BLOCKED→recovery-stage rejected;
- block()/resume_blocked() succeeds and clears recovery metadata.

### 6.5 Runtime-service parity
PASS for all current revision cleanup targets:

- RESEARCH;
- EDITORIAL;
- TITLE;
- DRAFT;
- DELIVERY.

The current service gate lists equal `workflow_spec.invalidated_gate_names_from(...)`.

Public Research/Editorial/Final submit revision sets are also guarded to match `workflow_spec.revision_targets(...)`.

### 6.6 Hosted full CI
OPEN / externally blocked. PR run `38196512322`, job `114640264451` ended with `runner_id=0`, `steps=[]`; no checkout/install/test command executed. This is not a code-test failure and is not a full-regression PASS.

## 7. Assurance ceiling

Strongest current phase claim before final branch architecture/diff review and merge:

`WORKFLOW_KERNEL_SCOPED_EXACT_CODE_AND_FAULT_PASS__FULL_OWNER_CI_RUNNER_NOT_EXECUTED__LIVE_ARTICLE_OPEN`

Do not claim:

- full owner regression PASS;
- live article quality improvement;
- independent semantic review;
- all workflow duplication removed (runtime-service implementation duplication is guarded but scheduled for Phase 2 deletion);
- Financial full-system rebuild complete.

## 8. Remaining Phase-1 acceptance checks

- current Universal architecture validator against final branch manifest/ref set;
- full PR diff review for unrelated behavior drift;
- search/attack for a new independent workflow table outside the canonical kernel;
- final exact-code harness after any late test/audit changes;
- merge to main only with scoped assurance explicitly recorded;
- reread final main authority after merge.

## 9. Phase-2 handoff if Phase 1 merges

Phase 2 owns execution readiness/state/recovery convergence. It must:

- edit `runtime_service.py` once for both task-discovery maintenance-debt filtering and removal of the temporary revision/gate-list implementation duplicates now guarded by parity tests;
- preserve the canonical workflow kernel rather than introducing another route table;
- test stale writes/partial persistence/context loss/BLOCKED recovery/idempotent retry/foreign-task artifact pollution;
- keep owner-native vs GitHub persistence and assurance differences explicit.
