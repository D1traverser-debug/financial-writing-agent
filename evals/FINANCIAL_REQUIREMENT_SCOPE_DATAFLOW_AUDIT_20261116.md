# Financial Writing — Requirement Scope and Stage Dataflow Audit

**Date:** 2026-11-16  
**Repository:** `D1traverser-debug/financial-writing-agent`  
**Candidate PR:** [#84](https://github.com/D1traverser-debug/financial-writing-agent/pull/84)  
**Candidate branch:** `repair/financial-requirement-bound-owner-stage-coordinator-20261114`  
**Exact candidate head:** `494c9c0d86a862c7bd192581389c37d8506f5d3c`  
**Exact-head CI:** [43787407518](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43787407518) — SUCCESS  
**CAOS boundary:** no CAOS repository, code, configuration, plugin, PR or runtime was modified.

## 1. Original business problem

A task requirement is not merely a sentence stored on the Article Aggregate. It must remain visible to every relevant research and production pass, become due at the correct business stage, be satisfied with evidence, and be checked consistently by the owner-state admission and the portfolio coordinator.

The failure mode under investigation was a divergence between:
- the owner aggregate's task-requirement due-stage projection;
- the portfolio coordinator's stage-requirement projection;
- the contexts injected into shared Research and product-specific passes; and
- special typed research gates that had to respect the requirement's actual scope.

This is a dataflow/authority defect, not a test-count or documentation defect.

## 2. Root cause

Two independently maintained scope projections had drifted.

1. `current_admission._requirements_due_at_stage` resolved due requirements against the task's stage and output contract.
2. `writing_kernel._requirement_scopes_for_stage` used a separate simplified rule. Shared Research previously received only ALL, RESEARCH and PRIVATE_RESEARCH. A Deep-, Broad- or platform-interaction-specific requirement affecting RESEARCH could therefore be absent from the one shared Research pass.
3. Product branches received their own contexts, but the context projection did not consistently apply the stage cutoff. A later-stage requirement could be injected too early, while a product-specific Research requirement could be missed upstream.
4. The full-universe typed ResearchPackage gate was selected by a special requirement ID without consistently checking whether that requirement applied to the task's requested outputs. A Deep-only requirement could therefore leak into a Broad-only task.
5. The older executable/static acceptance scripts still encoded the previous no-host execution model. That contradicted the already selected Financial-owned Provider Action boundary and made the architecture internally inconsistent.

The underlying problem was duplicated authority logic: owner admission and portfolio execution were not guaranteed to interpret the same requirement in the same way.

## 3. Rejected approaches

- **Tests-only repair:** rejected. It would make fixtures pass without repairing the production dataflow.
- **Add Deep/Broad scopes only to one Research callback:** rejected. It would leave owner satisfaction and portfolio due checks with separate definitions.
- **Treat every special requirement ID as globally active:** rejected. A special typed gate must be activated by the requirement's actual task scope, not by its identifier alone.
- **Revert to direct GitHub connector writes because the provider is not deployed:** rejected. Git CAS proves concurrency, not authenticated owner intent or signed effect admission.
- **Restore a CAOS-hosted parent runtime:** rejected. CAOS remains session-level governance; Financial retains its own business state and admission authority.

## 4. Selected correction

### Canonical scope authority

`financial_writing_agent.task_requirements` now owns:
- `active_task_scopes(required_outputs)`;
- `requirement_scopes_for_stage(stage, required_outputs)`;
- `requirement_applies_to_scopes` and `requirement_applies_to_task`; and
- `validate_requirement_applicability`.

Active product scopes derive from the immutable task output contract. Shared Research receives ALL, RESEARCH, PRIVATE_RESEARCH and every requested product scope. EDITORIAL/TITLE receive ALL plus requested Deep/Broad scopes. DRAFT/audit receive ALL plus requested product scopes, including interaction. DELIVERY receives ALL, DELIVERY and requested product scopes.

The owner aggregate and portfolio coordinator now use the same stage-to-scope function. New requirement mutations reject scopes that do not apply to the task's outputs and reject product scope/stage combinations that have no corresponding business pass.

### Pass-context projection

- Shared Research receives only requirements whose affected stage is RESEARCH, including product-specific research constraints for every requested product.
- Each later product branch receives ALL plus its own scope and only requirements effective by the current stage.
- The platform-interaction branch receives ALL plus PLATFORM_INTERACTION.
- The special full-universe ResearchPackage/reconciliation gate is activated only when the corresponding requirement applies to the task's actual output contract.

### Persisted stage and owner admission

The production coordinator `portfolio_coordinator.run_next_portfolio_stage` executes one task-bound stage, persists the typed stage artifact and resumable context as one artifact bundle, reads both back, cross-binds their hashes and then requests Article Aggregate admission through `standalone_runtime.py`. The owner transition binds the context reference and the stage artifact reference. This is deterministic code and test evidence; it is not evidence that a live provider endpoint exists.

### Execution boundary

The Skill-only plugin cannot call the Python admission runtime or sign canonical owner effects. Canonical owner-state and method-catalog mutations therefore require a Financial-owned hosted Provider Action over MCP/HTTPS, using authenticated owner identity, a least-privilege GitHub App, signed authorization/effect receipts, atomic CAS and exact readback. This is an adapter, not a second business controller. The endpoint remains NOT_DEPLOYED; no paid host has been provisioned.

## 5. Regression evidence

New and updated tests cover:
- equality of owner and portfolio due-requirement IDs for RESEARCH, EDITORIAL, TITLE, DRAFT and DELIVERY;
- product-scoped Research requirements reaching the shared Research pass;
- later-stage requirements not being imposed prematurely;
- Deep/Broad/interaction isolation in downstream branches;
- rejection of an unrequested product-only requirement;
- rejection of an impossible scope/stage pair;
- the full-universe gate being conditional on the requirement's actual task scope;
- typed stage/context artifact bundle persistence, exact provider readback and Article Aggregate admission;
- owner outcome/status and revision-target cross-binding;
- requirement-satisfaction evidence-set equality between persisted context and Owner Receipt;
- rejection of empty, non-string and duplicate evidence references;
- mandatory coordinator routing for new/current tasks at coordinated stages; and
- preservation of legacy owner-state transition compatibility without weakening the current-task route.

### Second-pass root-cause findings and corrections

The first pass fixed requirement-scope divergence but did not close the full execution/authority chain. A second adversarial pass found three additional defects:

1. **Stage outcome was not owner-bound.** Stage artifact and portfolio context hashes could match while their PASS / REVISE / FAIL outcome or revision target differed from the owner transition. `standalone_runtime._verify_portfolio_stage_artifact_context` now compares the exact stage result with the latest Owner Receipt's review status and revision target. A correctly hashed artifact alone is no longer sufficient.
2. **Requirement evidence could diverge at the owner boundary.** The persisted context's satisfaction set was not required to equal the evidence set admitted by the Owner Receipt. The runtime now validates nonempty unique string references, binds the exact stage-artifact path into the evidence set, and compares normalized requirement IDs, results, notes and references across both records. `current_admission` rejects invalid or duplicate evidence references before the owner transition.
3. **New tasks could bypass coordinator routing.** New tasks now bind `portfolio_execution_contract_version=1.0` into the initial Owner Receipt. The marker cannot be removed from an admitted task. For coordinated stages, direct `ADVANCE_STAGE` without a portfolio context reference is rejected. Legacy states remain distinguishable and retain historical transition behavior; the coordinator may promote a legacy task only when its first context is bound in an owner transition.

Integration fixtures now distinguish actual new/current tasks from historical pre-coordinator states. Compatibility tests no longer use a current-task fixture to simulate a legacy direct transition.

### Exact-head verification

Exact candidate head `494c9c0d86a862c7bd192581389c37d8506f5d3c`; CI run [43787407518](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43787407518) completed successfully:
- **698 tests passed**.
- Total Python statement coverage: **88%** (7,891 statements; 929 missed).
- Portfolio Coordinator: **91%** (253 statements; 22 missed).
- Standalone Runtime: **89%** (933 statements; 100 missed).
- Writing Kernel: **81%** (920 statements; 175 missed).
- Whole-tree audit: **338 tracked files**, 130 Python AST parses, 54 JSON parses, 52,710 decoded text lines, **0 warnings and 0 errors**.
- Executable contract eval, static single-owner/legacy-quarantine audit, standalone contract, wheel build and isolated install all passed.
- DOCX render smoke passed; all four synthetic Word product binaries opened, rendered and passed byte/signature/page checks.
- Real-task negative replay completed with `reproduced_weak_assurance_paths = []`. This is negative-path assurance, not a live article or factual-quality certification.

Intermediate exact-head CI attempts exposed integration defects in fixture migration, a stale helper import, a mismatched helper argument, newline serialization and readback assertion placement. Those failures were corrected before the successful run above and are not counted as passing evidence.

## 6. What this evidence does not prove

The exact-head CI is engineering evidence, not complete Financial product acceptance.

The active task `cross-border-ecommerce-20261016-v3` remains at RESEARCH / IN_PROGRESS with **0 of 4** real deliverables and no quality evidence. Its task requirement digest remains `641bfaee46fbce8b5a3c363a54cd364f1c318bca5102ebe70001d968302051dd`.

The whole-system acceptance status remains `NOT_READY__REQUIRES_SIGNED_EXTERNAL_EVIDENCE`. Seven gates remain open:
1. original goal and semantic correction;
2. legal article graph and recovery;
3. method knowledge CRUD and impact;
4. provider-authenticated runtime CAS;
5. native Financial plugin client activation;
6. independent external adversarial review; and
7. Financial main-branch hygiene.

The synthetic Word renders do not certify real article quality. The negative replay does not revalidate live news, policy, filings or company facts. The plugin package is private Skill-only release 0.1.4; actual installation/fresh-session invocation is NOT_VERIFIED. The hosted Provider Action is NOT_DEPLOYED. No independent reviewer has reviewed this exact candidate head.

## 7. Promotion decision and next legal step

PR #84 remains DRAFT and unmerged. The current `main` head remains `b2098e69367f78c452e0a595bf95d86388d6a449`; candidate head `494c9c0d86a862c7bd192581389c37d8506f5d3c` has exact-head CI success.

The next legal step is an independent review of the this exact candidate head. If that review accepts the change, merge only the Financial Writing PR and verify post-merge main CI. Do not modify CAOS. Do not provision paid infrastructure without explicit owner approval. Do not claim live owner-state execution, article completion, editorial acceptance or reader success until their separate evidence exists.
