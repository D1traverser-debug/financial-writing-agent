# Maintenance module

## Ownership
Maintenance owns **how feedback, external methods, code changes, reliability incidents and performance evidence become durable system changes**. It does not own article-level prose rules.

Financial Writing currently has one production owner path:

`ChatGPT → current GitHub main Financial owner → main/workspaces/articles/{task_id}`.

Maintenance must improve that path rather than recreate a parallel runtime, state store, adapter family or fallback authority.

## Universal meta-maintenance entry
Financial Writing does not maintain a parallel system-governance doctrine. For any **systemic, architecture-level, cross-surface, non-trivial reliability, or quality-promotion infrastructure change**, activate the current Universal `operational_hygiene@1.0 + evolution@1.0` semantics through `continuity/UNIVERSAL_PROTOCOL_ADAPTER.json`, then apply this owner-local module for Financial-specific state, writing, quality and delivery details.

A material user correction is a system-impact signal on first occurrence; do not wait for repeated reminders before asking whether the defect generalizes. Classify explicit user content into goal/constraint, failure/counterexample and proposed mechanism. The goal/constraint and real failure evidence are high-value inputs; the proposed mechanism is a candidate, not automatic architecture authority.

For systemic/non-trivial maintenance, the durable maintenance record must cover the current Universal dimensions that apply, including:
- current authority + full impact/failure model before patching;
- learning/benchmark scout when the change is systemic or architectural, with adoption/rejection rationale rather than copied doctrine;
- at least one credible alternative and an active failure-mode attack on the accepted mechanism;
- an explicit decision on whether Skill/startup/account instructions should change or remain unchanged;
- registry-derived cross-subsystem propagation/inheritance and stale override/shadow-copy review when shared semantics are affected;
- complexity/efficiency cost: authority surfaces, startup context, tool/remote reads, steady-state latency, duplicate rules and migration/test burden;
- regression/eval plus second-order attack on the accepted fix itself;
- a calibrated assurance ceiling and remaining OPEN evidence instead of a global “system has no problems” claim.

A small deterministic owner-local typo/schema/test-fixture repair may take a lightweight path when the record gives a concrete `NOT_REQUIRED_WITH_REASON` for systemic dimensions. Do not turn routine local fixes into bureaucratic full-control-plane research.

The deterministic Universal Meta-Governance Harness verifies process completeness only. It does not make Financial's diagnosis semantically correct, does not prove reviewer independence and does not replace live writing-quality evidence.

## Current authority and negative space
Current execution authority is:
- `skills/financial-writing-agent/SKILL.md` — ChatGPT-facing router;
- `continuity/FINANCIAL_OWNER_EXECUTION.json` — one execution contract;
- `financial_writing_agent/workflow_spec.py` — canonical stage/revision graph;
- `financial_writing_agent/owner_guard.py` — normal state mutation/output reconciliation;
- `financial_writing_agent/owner_lifecycle.py` — BLOCKED recovery and system-impact lifecycle;
- `main/workspaces/articles/{task_id}` — sole durable article business-state authority.

The retired owner-native/plugin/SQLite second runtime, retired dual-adapter execution contract, retired WritingState delivery wrapper and old guard component path are **physically absent from the current tree**. `config/retired_runtime_paths.json` is the canonical negative-space list. `tests/test_retired_runtime_absence.py` and `scripts/retired_runtime_static_audit.py` must fail if any listed path returns.

Git history, historical evals, closed PRs and maintenance branches may preserve those old mechanisms as evidence. Presence in history is not permission to restore them. A future architecture migration must explicitly replace the current contract, update every current consumer and pass negative-space/trajectory regression; missing capability is never enough reason to revive a retired path.

Existing schema-1.2 article states may contain `execution_mode=GITHUB_CHAT`, legacy receipt labels or old capability tokens. These are compatibility data only. They may be read by `owner_guard.py` but must not become route selectors or component discovery keys.

## Classify before changing
- Run-local request → current TaskContract/state only.
- Explicit durable user instruction → durable-rule change candidate with direct provenance.
- Single user edit/reaction → raw Writing DNA evidence / one-off candidate, not an automatic global rule.
- Repeated accepted edits across independent articles → eligible for personalized promotion after comparison.
- Post-publication performance → evidence sample; repeated comparable results matter more than one outlier.
- External skill/agent/article/research → benchmark candidate only; distill the underlying mechanism, not signature phrasing or an entire foreign prompt stack.
- Existing rule skipped by execution → runtime/trajectory defect; fix enforcement instead of duplicating the rule in more documents.
- Platform behavior change → reverify current evidence before policy changes.

## Learning and system-impact evidence
Raw user edits, feedback, acceptance/rejection and post-publication performance must be attached to the exact durable article workspace when they matter to future system behavior.

For a persisted writing task, a **material explicit user edit, feedback or rejection that may change how the system should write, review or deliver** must be captured through the current owner state mutation before the turn claims durable learning or closes the affected revision loop, unless equivalent evidence is already persisted. `owner_guard.attach_material_feedback` captures the learning evidence plus an OPEN system-impact item in one guarded mutation.

`owner_lifecycle.review_system_impact_state` owns classification and closure of that obligation. Systemic review must:
- state problem and root-cause layer;
- define generalization scope;
- compare at least two credible mechanisms with failure modes;
- select one mechanism and justify the authority surface;
- bind regression/eval and evidence refs;
- choose `LOCAL_ONLY`, `NO_CHANGE_WITH_REASON`, or `SYSTEM_MAINTENANCE_REQUIRED`.

`SYSTEM_MAINTENANCE_REQUIRED` remains open. Closure requires the accepted diagnosis to remain immutable plus a durable `maintenance_ref`, non-empty validation refs and an assurance ceiling at least `REGRESSION_VERIFIED`. Current owner closure remains self-attested unless stronger exact-action evidence really exists.

The ledger is evidence, **not automatic self-modification**. A one-off user reaction never becomes a global style rule by itself.

A repeated material failure of the same writing responsibility is not another reminder-writing opportunity. Treat it as a reliability defect: persist failure evidence, identify the enforcement gap, add/update a regression or eval, and remove/repair the conflicting mechanism before adding unrelated writing features.

## Candidate distillation before promotion
A real failure is evidence that something is wrong, not evidence that the first proposed fix is right. Before a quality-changing candidate can enter blind promotion comparison, `financial_writing_agent.quality_regression.evaluate_candidate_distillation` must PASS.

The distillation package is process evidence, not another article-writing checklist. It must:
- bind the candidate to complete owner-local failure evidence, including at least one real user rejection;
- state the problem and root-cause hypothesis separately from the proposed mechanism;
- compare at least two credible mechanisms and record a failure mode for each;
- record the selected candidate, selection rationale and the smallest intended authority surface;
- include counterexample/failure-mode evidence and a verifiable candidate-change reference;
- independently from simple ref existence, verify that change/counterexample evidence supports this candidate package;
- state the disposition of any superseded mechanism instead of silently accumulating another parallel rule layer;
- scope the quality claim to explicit content modes.

Content-mode scope fails closed. A candidate may claim `FINANCE_DEEP` or `FINANCE_BROAD` quality improvement only when that target mode has complete real-rejection evidence **and held-out coverage spanning at least two distinct topic families**. Evidence from FINANCE_DEEP must not silently authorize a FINANCE_BROAD claim, and vice versa.

This requirement prevents two opposite failure modes: blindly adopting the user's or assistant's first idea, and endlessly adding deterministic prose rules because they are easy to test. It does **not** make the distillation package proof of better writing; blind pairwise evidence remains required afterward.

## Quality-changing system promotion
A system/prompt/method change that claims to improve writing quality must not be promoted merely because deterministic CI passes or because the changing agent writes a positive receipt.

Use `financial_writing_agent.quality_regression` for owner-local promotion evidence.

A `COMPLETE` regression/held-out case is not complete merely because a path/ref string exists. It must carry an immutable artifact identity (for example a Git blob SHA, provider immutable version or content digest), and the promotion run must verify that binding before the case can be used.

Verifier callbacks are **verification contracts**, not proof of independent execution merely because Python received a callable. When a promotion claim requires independence, the caller must separately establish verifier/judge execution identity/trace at the execution-control layer.

### General editorial quality
Promotion requires:
- deterministic factual/compliance/state/artifact invariants remain a hard floor;
- complete real failure evidence with verified immutable case bindings;
- diverse complete held-out evidence spanning **at least two topic families inside every claimed content mode**;
- a passing candidate-distillation package before the candidate is admissible;
- the quality claim is limited to content modes with complete real-failure and held-out diversity coverage;
- a real hard-invariant regression execution receipt bound to the exact candidate/change;
- blind pairwise comparison against the current baseline with candidate evaluated in both A and B positions;
- verifiable judge execution evidence;
- every judge run bound to exact candidate id and candidate-change ref;
- judge execution refs cannot be reused across distinct pairwise runs;
- evidence-ref verification and semantic judge-run verification remain separate checks;
- known real failures improve, held-out cases do not regress, and at least one held-out case prefers the candidate;
- position-swapped judgments agree or the comparison fails closed.

A user positive label is **not** required for general editorial quality. External benchmarks and held-out scenarios may support general quality, provided they do not masquerade as personalized taste.

### Personalized Writing DNA
A change that claims to encode the user's personal style or durable preference must satisfy all general-quality requirements **and** include real user acceptance/edit evidence or post-publication performance evidence. External benchmarks cannot invent personalized taste.

Partial snippets/feedback may enter the corpus immediately but cannot by themselves authorize promotion.

`evals/quality_regression.json` is owner-local eval evidence, not business task authority and not a new root policy. Historical rejection/held-out artifacts under `evals/artifacts/` remain evidence, not user-positive style exemplars.

The current corpus remains diagnostic until the documented held-out diversity and positive evidence requirements are met. Do not upgrade readiness merely because architecture tests pass.

## Impact-map closure and stale-consumer scan
An impact map is a **hypothesis about affected surfaces**, not proof that the list is complete. Systemic maintenance may not declare propagation/closure PASS merely because every file named in the initial map was edited.

Before closure, scan the repository for both the **new invariant and the superseded invariant** and reconcile every current executable/startup consumer. Minimum consumer classes, when applicable, are:
- canonical `config/policy.json`, rule ownership and canonical `references/*`;
- startup/router surfaces: Skill, Task Index, task manifest/handoff and execution contract;
- canonical `TaskContract`, routing, workflow graph, `owner_guard.py`, `owner_lifecycle.py`, schemas, document builders/checks/rendering and quality promotion code;
- `scripts/static_audit.py`, `scripts/eval_contracts.py`, `scripts/retired_runtime_static_audit.py`, current tests and CI commands;
- generated/package mirrors and deployment contracts;
- `config/retired_runtime_paths.json` negative-space contract;
- obsolete branches, closed/open PRs and historical files that still look active;
- at least one zero-memory/fresh-chat or deterministic reference trajectory when the changed invariant affects cold-start execution.

For policy-key/value changes, closure evidence should include a consumer scan for the key and distinctive text/value of the old rule. A stale executable assertion is a **CONFIRMED_DEFECT**, not documentation debt. If a machine consumer still enforces the superseded value, maintenance remains OPEN even when targeted new tests pass.

When hosted CI reports a run/job but `steps=[]` and no runner is allocated, classify hosted CI as `OPEN_RUNNER_NOT_EXECUTED`. The workflow conclusion alone is not code-test PASS/FAIL. Run whatever targeted current-session/static validation is genuinely executable and keep full hosted CI OPEN.

## Change protocol
1. For systemic/non-trivial changes, complete the Universal meta-maintenance entry before treating the first owner-local patch as accepted architecture.
2. Identify the canonical rule owner, affected runtime stages and canonical TaskContract/output semantics.
3. Build an initial impact/failure map; treat it as provisional until stale-consumer scan completes.
4. Decide whether the defect belongs in rules, schema, owner guard/lifecycle, deterministic delivery, tests/evals or deployment—not every problem is a prompt problem.
5. Modify the canonical owner first.
6. Search for contradictory, duplicated, synonymous-but-divergent, legacy and shadow wording/code, including startup Skill and harness consumers.
7. Synchronize intentional rule mirrors byte-for-byte; delete obsolete active-looking surfaces instead of leaving two authorities.
8. Do **not** restore a retired second runtime for parity. Capability providers must serve the one owner state trajectory; missing capability blocks the affected stage.
9. Add regression tests for success/failure paths, revision invalidation/recovery, output-contract failure and negative-space reintroduction when relevant.
10. Run current unit tests, executable contract evals, static ownership/bundle/version audit, retired-runtime absence audit, isolated wheel smoke and DOCX render smoke when actually executable. If hosted CI does not execute steps, record that exact boundary rather than inventing PASS.
11. When behavior depends on live model/tool execution, run a representative real writing E2E or turn an observed live failure into a durable trajectory regression before production claims.
12. Re-run stale-consumer scan after implementation and any secondary fix; the second scan is what can close propagation.
13. Re-read final authority files, business output contract, Continuity/startup surfaces and CI state before reporting the change as committed/promoted.

## Version / cutover discipline
A breaking active state schema or public business contract change requires an explicit migration/version decision. `pyproject.toml`, policy contract version, README/architecture/Site spec and active Continuity metadata must not silently disagree about the current contract.

Do not preserve obsolete compatibility surfaces merely because they once existed. Keep Git history. Delete unsupported runtime/schema/tool paths when safe and protect the deletion with deterministic negative-space regression.

Legacy schema-1.2 tokens that are still required to read existing main article state may remain **inside current state compatibility logic only**. Their survival does not justify restoring deleted runtime files.

## Runtime reliability discipline
Fail-closed must still be recoverable. A BLOCKED task needs an explicit persisted recovery cursor and tested resume path; permanent deadlocks are not acceptable durability.

Semantic review assurance is not a free status bit. Current same-chat review must remain labeled `CHAT_SELF_REVIEW`; a provider-attested claim requires distinct exact-action evidence. The historical schema label `INDEPENDENT_EXECUTOR` is compatibility/history only and is not provider-attested isolation.

The owner business contract is capability-provider-independent. Default distribution mode, delivery channel, required outputs, stage order, invalidation and terminal semantics come from the canonical TaskContract/workflow/owner guard, not from the tool substrate.

Revisions must invalidate stale downstream QA and generated artifacts. Re-running deterministic render/delivery steps must be idempotent so old output cannot contaminate current evidence.

## Evidence standard
A documentation edit is not proof that the system executes the behavior. Durable state, Git identities, file hashes, deterministic checks, tests, workflow traces and audit evidence are proof classes. A proof object still must be bound to the exact current case/candidate/action; ref existence alone is not semantic proof.
