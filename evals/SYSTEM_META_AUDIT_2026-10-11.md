# Financial Writing Agent — System Meta Audit 2026-10-11

Status: `BEHAVIORAL_REPAIR_IMPLEMENTED__FINAL_CI_PENDING_AT_FIRST_WRITE`
Scope: SYSTEM/ENGINEERING only. Business task `financial-writing:main`, article state, stage, lease and resume epoch are not modified by this audit.

## Trigger
Universal SYSTEM_INFRA was explicitly challenged to stop merely identifying OPEN problems and to demonstrate self-audit by repairing Financial Writing from a fresh adversarial angle rather than waiting for another user-supplied example.

The owner was reviewed from runtime/state-machine, public MCP, quality-promotion evidence, maintenance-entry, capability and deployment perspectives rather than from the pre-existing issue list alone.

## Newly discovered failure classes

### 1. Semantic PASS side-channel
The public/documented system claimed stage-separated semantic judges, but `GateRecord` persisted only PASS/evidence/notes and `WorkflowController` advanced on PASS. Audit provenance could therefore be discarded before the authoritative transition decision. Existing trajectory tests manually set PASS and reached COMPLETE, so CI was positively blessing the bypass.

Root cause: assurance evidence existed in typed model output but was not part of the lowest authoritative state-transition invariant.

Repair:
- semantic PASS is revalidated against exact task/stage-bound persisted provenance and current owner-runtime `EXECUTOR_START/EXECUTOR_END` trajectory;
- Controller checks before leaving Research/Editorial/Final audit stages;
- `WritingEngine.complete()` rechecks before COMPLETE;
- stale PASS after re-entering an audit stage cannot be replayed.

### 2. Closing the bypass initially risked creating a production deadlock
Simply rejecting CHAT_BRIDGED PASS would have made hosted MCP unable to complete semantic audits if no owner-native audit gateway existed.

Alternatives compared:
- reject PASS only: rejected; safe but deadlocks hosted workflow;
- silently repurpose existing `submit_*audit` tools so PASS triggers hidden server rerun: rejected; tool meaning becomes surprising and migration is implicit;
- add explicit `run_semantic_audit_stage` and make it the proof-bearing owner-native certification path: accepted.

v0.8 therefore exposes an explicit server-side audit gateway. Missing SDK/model runtime becomes recoverable BLOCKED at the exact audit stage; the system does not fall back to caller self-certification.

### 3. “Independent” wording exceeded the real assurance
The historical `AuditProvenance.assurance=INDEPENDENT_EXECUTOR` label represented a stage-separated owner-runtime run, but the repository did not have provider-attested isolation evidence.

Repair: v0.8 documentation/capabilities now scope that legacy token to stage-separated owner-runtime execution only. True provider-attested isolation remains `DECLARED_ONLY/UNAVAILABLE` until a distinct provider execution identity/trace exists.

### 4. Quality corpus path existence was weaker than immutable baseline identity
A COMPLETE regression/held-out case could name artifact refs without binding the exact content version. A later changed artifact could silently alter the baseline.

Repair: COMPLETE cases require immutable artifact bindings; current real offshore-wind/rutile repository artifacts are pinned to Git blob SHA. Promotion additionally requires a case-binding verifier.

### 5. Candidate evidence ref existence did not prove the ref supported the candidate mechanism
Candidate distillation verified refs existed but did not separately verify that the change/counterexample evidence semantically supported the proposed mechanism.

Repair: candidate distillation now requires a candidate-evidence semantic verifier.

### 6. “Zero hard regressions” was caller self-report
An empty `hard_invariant_regressions` list could represent “no regression observed” without proving the regression suite ran.

Repair: promotion requires a structured hard-regression execution record bound to exact candidate/change, with execution/suite/evidence refs and semantic verification.

### 7. A verifier callback is not independent execution identity
The runtime can require verifier callbacks, but receiving a callable does not prove that callable was executed by an independent actor/provider.

Repair: code/docs call these verification contracts. Any independence claim still needs execution-control evidence outside this owner harness.

### 8. Owner-local maintenance had a shadow governance path
Financial Skill routed system changes to local `references/maintenance.md`. Although the Universal adapter bound operational_hygiene/evolution, the local change protocol did not explicitly enter current Universal Meta-Governance semantics. An owner self-audit could therefore return to the old repair-first local path.

Repair: the three maintenance mirrors now contain one explicit Universal meta-maintenance entry for systemic/non-trivial work, while retaining a reasoned lightweight path for local deterministic bugs. No new root policy or permanent meta Agent is added.

## Instruction / propagation decision

Financial repo Skill/maintenance/capability/Site instructions must change because the old owner entry and public runtime semantics were part of the defect.

No external ChatGPT account-level instruction change is justified by this owner-local repair. Account routing is not the demonstrated failure surface, and copying owner implementation doctrine into account prompt would add drift/bloat.

Universal central derived metadata should be refreshed only after final owner regression evidence exists. Financial business manifest/Handoff/lease/article state must remain untouched.

## Complexity / efficiency

Accepted cost:
- +1 narrow runtime module: `semantic_runtime.py`;
- +1 public MCP tool: `run_semantic_audit_stage`;
- public contract bump 0.7 → 0.8;
- no new root policy/registry/permanent Agent;
- no extra normal generation-stage audit; proof-bearing work occurs only at the three semantic audit stages;
- quality-promotion hardening is cold-path system evolution, not ordinary article hot-path overhead.

This is preferred over hidden tool semantic changes or permanent double-review of every generation stage.

## Second-order challenge

- Could runtime proof be self-authored? The public chat cannot create the required current owner-runtime stage trajectory through audit-submit PASS. The owner server gateway creates the trajectory around actual executor invocation.
- Does this prove provider independence? No. Stage-separated owner execution is explicitly below provider-attested isolation.
- Could old PASS survive revision? Re-entering an audit stage moves the latest STAGE_ENTER after old runtime proof, making the old proof invalid.
- Does safer enforcement deadlock production? The explicit semantic audit gateway preserves a legitimate hosted path and recoverably blocks when the required executor is unavailable.
- Did the quality gate become “more callbacks therefore more independent”? No. Callback presence is explicitly not independence proof.
- Does this prove prose quality improved? No. Current FINANCE_DEEP corpus remains NOT_READY due held-out diversity; FINANCE_BROAD and Personalized Writing DNA remain unready.
- Did the repair alter the live business task? No; SYSTEM_INFRA changes engineering/control metadata only.

## Evidence ceiling

At successful owner CI, this repair may claim at most:
- `REGRESSION_VERIFIED` runtime/control-plane hardening;
- v0.8 public contract/surface alignment;
- quality-promotion evidence-chain hardening.

It may not claim:
- provider-attested independent review;
- live Financial article quality improvement;
- Personalized Writing DNA learned;
- Site production-ready status without a real deployed owner-native semantic audit E2E.

Final validated head/run/job will be appended only after the complete current-main CI succeeds.
