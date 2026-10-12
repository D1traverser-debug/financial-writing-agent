# Financial Live E2E Task / Output Contract Incident — 2026-10-12

Status: REPAIR_IMPLEMENTED_ON_MAIN__TARGETED_CONTRACT_REGRESSIONS_ADDED__HOSTED_FULL_CI_OPEN__FRESH_CHAT_RETEST_OPEN

## Trigger
A real zero-memory fresh ChatGPT conversation was explicitly pointed at `D1traverser-debug/financial-writing-agent@main`, reconstructed the Financial owner architecture, then executed a publishable article from user-supplied AI-security material.

The run produced durable stage/review evidence, a real EDITORIAL_AUDIT revision, Word/render evidence and the bounded GITHUB_CHAT terminal state. However, the visible delivery contained only two files: one `FINANCE_BROAD` Word article plus `WRITING_AUDIT_REPORT.docx`.

The canonical owner default is `DUAL`. With no explicit user platform/mode narrowing, the required output contract is three files: `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX`.

Therefore the live trajectory is **not a clean E2E PASS**. It is evidence that most workflow/state mechanics executed, but it also proves a material adapter-semantic parity defect in the task/output contract.

## Why the earlier review missed the obvious 3→2 regression
The initial post-run review prioritized:
- durable STATE / stage trajectory;
- revision invalidation;
- receipts / assurance ceiling;
- Word mechanics / render evidence;
- factual research quality;
- branch-backed task discoverability.

It did **not first reconcile the visible final deliverables against the canonical TaskContract/default output baseline**. That audit ordering was wrong. A trajectory can be internally consistent while executing the wrong initial contract.

This incident therefore changes the required review order: baseline task/output contract reconciliation precedes detailed stage-quality praise.

## Primary root cause — adapter semantic parity was incomplete
Phase-1 adapter parity centralized the canonical stage graph, PASS targets, revision routes and invalidation semantics in `workflow_spec.py`. It did not mechanically bind the GITHUB_CHAT adapter to the complete owner `TaskContract` semantics.

OWNER_NATIVE already had:
- canonical routing default `DUAL`;
- `WORD_FILE_ONLY`;
- derived `required_outputs`;
- completion-time required-output checks.

GITHUB_CHAT state previously stored only a caller-supplied `distribution_mode` string and did not persist/enforce the equivalent `required_outputs` contract. The fresh chat therefore wrote `FINANCE_BROAD` during INIT without an explicit user single-mode request, and later stages remained locally legal relative to that silently narrowed state.

Failure chain:

`canonical default DUAL` → `GITHUB_CHAT caller supplies FINANCE_BROAD` → `guard accepts narrowed mode` → `no required_outputs parity` → `DELIVERY validates only stage artifact existence` → `FINAL validates review route but not complete deliverable set` → `Broad + Audit accepted as terminal delivery`.

The defect is not owned by the Writer alone. It crossed INTAKE routing, adapter contract, DELIVERY, FINAL reconciliation and trajectory auditing.

## Secondary root cause — evolution propagation was consumer-incomplete
A preceding user-rule calibration correctly changed canonical policy/reference/runtime behavior for A-share name bolding and concise risk disclosure. Its audit claimed propagation PASS but its impact map omitted active consumers including:
- `skills/financial-writing-agent/SKILL.md`;
- `scripts/static_audit.py`;
- `scripts/eval_contracts.py`.

This left mutually contradictory old/new assertions in current main. The maintenance process therefore had the right high-level evolution doctrine but an incomplete propagation closure condition.

The maintenance contract now requires **consumer-complete propagation**: identify not only intended writers but all active startup/router, policy/reference, runtime/adapter, schema, harness/eval, mirror and continuity/deployment consumers of the changed invariant; search for stale/superseded assertions before claiming propagation PASS.

## Rejected alternative — branch discovery as a new authority dimension
An initial repair candidate (PR #19) attempted to formalize `article/{task_id}` branch discovery because the real fresh-chat task had been executed on such a branch.

That direction was rejected and PR #19 was closed unmerged. It would have added a second business-state ref dimension and therefore more discovery, recovery, conflict, cleanup and audit complexity without solving the actual 3→2 output-contract failure.

Current design decision:
- `GitHub main` remains engineering/rule authority;
- new GITHUB_CHAT business mutations use `main/workspaces/articles/{task_id}` only;
- per-article branches are not a current business-state write authority;
- a legacy branch-backed task is historical evidence only until explicitly migrated to main before any future continuation.

## Implemented repair on main
### Task-contract parity
`financial_writing_agent/github_chat_guard.py` now:
- derives default routing from the same canonical `build_task_contract` / `TaskContract` semantics as OWNER_NATIVE;
- defaults to `DUAL` when the user did not explicitly narrow platform/mode;
- persists `state_ref`, `target_platforms`, `distribution_mode_source`, `delivery_channel`, `required_outputs`, and `delivery_artifacts`;
- makes those task-contract fields immutable across transitions;
- accepts new business state only on `main`;
- requires any direct single-mode override to carry `USER_EXPLICIT_OVERRIDE` **and** `distribution_mode_override_evidence` that is an exact substring of the original user prompt in the INIT receipt.

### Delivery / terminal reconciliation
For default DUAL:
- DELIVERY cannot advance with only Broad or only Deep;
- MECHANICAL_AUDIT PASS rechecks the required article output set;
- FINAL_AUDIT PASS requires `AUDIT_DOCX` and exact reconciliation of the complete `required_outputs` set;
- revision invalidation that reaches DELIVERY clears stale `delivery_artifacts`.

### Regression coverage
`tests/test_github_chat_guard.py` now covers:
- canonical default DUAL / main state / exact three required outputs;
- silent mode narrowing rejection;
- missing or mismatched override evidence rejection;
- exact user-prompt override evidence acceptance;
- missing Deep/Broad rejection at DELIVERY;
- missing Audit rejection at FINAL;
- Deep + Broad + Audit bounded terminal success;
- delivery artifact invalidation on upstream revision.

`scripts/eval_contracts.py` now asserts that an unspecified-platform task routes to DUAL with exactly the three required output kinds. The stale fixed-risk-minimum assertion was removed.

`scripts/static_audit.py` was aligned to the current bolding/risk/output contract and its branch-authority stale-term check was narrowed so the correct sentence “Do not create per-article business-state branches” is not itself falsely rejected.

### Startup / capability / contract propagation
The main Skill, `continuity/GITHUB_CHAT_EXECUTION.json`, `continuity/EXECUTION_CAPABILITIES.json`, `continuity/TASK_INDEX.md`, architecture documentation and owner maintenance reference now state one task contract / main-only GITHUB_CHAT write surface / required-output reconciliation semantics.

## Branch hygiene
The repository still contains historical and experimental branches, including old `article/*` experiments. The completed fresh-chat task branch is retained as historical evidence because it currently contains the only durable state for that exact task and must not be destroyed merely to make branch counts look clean.

Several `tmp-should-not-create*` branches were accidentally created during this maintenance while selecting the wrong GitHub connector action. They are not authority and contain no unique intended business state. The currently connected GitHub surface does not expose a delete-ref action, and no authenticated browser profile is available for safe physical deletion. Their removal is therefore **OPEN cleanup debt with an exact tooling blocker**, not falsely reported as completed.

Correctness does not depend on deleting those refs because current contracts fail closed on non-main new business-state writes. Physical branch cleanup remains desirable hygiene.

## Assurance / validation boundary
Confirmed durable evidence:
- root-cause analysis is bound to a real live trajectory;
- repairs and regressions are committed on current Financial main;
- current authority surfaces have been reread after mutation;
- PR #19 branch-discovery direction is closed unmerged.

Not yet proven:
- current full hosted CI PASS. Recent Financial GitHub Actions jobs continue to end with job `steps=null`, so they are runner/infrastructure non-execution, not code-test evidence;
- a new fresh-chat product trajectory under the repaired contract;
- provider-attested independent semantic review;
- improved prose quality from this repair.

The next decisive live proof is a new zero-memory Financial article request with no explicit mode/platform narrowing. It must create state on main, persist canonical DUAL + three required outputs, and refuse terminalization if any of Deep/Broad/Audit is absent.

## System lesson
A workflow graph is only one slice of business semantics. Adapter parity must cover **input/default contract + workflow + invalidation + output contract + terminal semantics**, and end-of-run review must reconcile visible outputs against the initial immutable contract before praising internal trajectory quality.
