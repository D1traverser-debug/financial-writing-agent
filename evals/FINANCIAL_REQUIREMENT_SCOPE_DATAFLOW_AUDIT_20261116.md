# Financial Writing — Requirement Scope and Stage Dataflow Audit

**Date:** 2026-11-16  
**Repository:** `D1traverser-debug/financial-writing-agent`  
**Candidate PR:** [#84](https://github.com/D1traverser-debug/financial-writing-agent/pull/84)  
**Candidate branch:** `repair/financial-requirement-bound-owner-stage-coordinator-20261114`  
**Verified candidate code head:** `4bf06f63fdf7e228b3153ec909a38abe8596f272`  
**Exact code-head CI:** [43819176634](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43819176634) — SUCCESS  
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

4. **Evidence-reference uniqueness was checked before canonicalization.** Raw references such as `source-A` and ` source-A ` could be treated as distinct even though they identify the same evidence. `current_admission`, `writing_kernel` and `standalone_runtime` now normalize and validate references before duplicate checks; regression coverage rejects whitespace-normalized duplicates at the owner, pass and persisted-stage boundaries.

Integration fixtures now distinguish actual new/current tasks from historical pre-coordinator states. Compatibility tests no longer use a current-task fixture to simulate a legacy direct transition.

### Verified code-head verification

Verified candidate code head 4bf06f63fdf7e228b3153ec909a38abe8596f272; exact-head CI run [43819176634](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43819176634) completed successfully:
- **720 tests passed**.
- Total Python statement coverage: **88%** (8,178 statements; 980 missed).
- Portfolio Coordinator: **91%** (255 statements; 24 missed).
- Standalone Runtime: **89%** (939 statements; 100 missed).
- Writing Kernel: **81%** (924 statements; 176 missed).
- Whole-tree audit: **340 tracked files**, 132 Python AST parses, 54 JSON parses, 54,278 decoded text lines, **0 warnings and 0 errors**.
- Executable contract eval, static single-owner/legacy-quarantine audit, standalone contract, wheel build and isolated install passed.
- DOCX render smoke passed; all four synthetic Word product binaries opened, rendered and passed byte/signature/page checks.
- Real-task negative replay completed with reproduced_weak_assurance_paths = []. This is negative-path assurance, not a live article or factual-quality certification.

The CI proves the candidate's deterministic code and synthetic artifact paths at this exact head. It does not prove that a real model callback will make sound financial judgments, that source claims entail the facts asserted, or that a human reader will accept the resulting article.
## 6. What this evidence does not prove

The exact-head CI is engineering evidence, not complete Financial product acceptance.

The active task `cross-border-ecommerce-20261016-v3` remains at RESEARCH / IN_PROGRESS with **0 of 4** real deliverables and no quality evidence. Its task requirement digest remains `641bfaee46fbce8b5a3c363a54cd364f1c318bca5102ebe70001d968302051dd`. The task record currently exposes two scoped full-universe requirements, but the original full article prompt is not independently recovered. Its V2 source references are historical fixtures (`KEEP_FIXTURE`), not current factual evidence; all material policy, company and market claims must be revalidated before a current article is written.

The whole-system acceptance status remains `NOT_READY__REQUIRES_SIGNED_EXTERNAL_EVIDENCE`. Seven gates remain open:
1. original goal and semantic correction;
2. legal article graph and recovery;
3. method knowledge CRUD and impact;
4. provider-authenticated runtime CAS;
5. native Financial plugin client activation;
6. independent external adversarial review; and
7. Financial main-branch hygiene.

The synthetic Word renders do not certify real article quality. The negative replay does not revalidate live news, policy, filings or company facts. The plugin package is private Skill-only release 0.1.4; actual installation/fresh-session invocation is NOT_VERIFIED. The hosted Provider Action is NOT_DEPLOYED. No independent reviewer has reviewed the live exact PR head.

## 7. Promotion decision and next legal step

PR #84 remains DRAFT and unmerged. The production main head remains b2098e69367f78c452e0a595bf95d86388d6a449. The current candidate code head is 4bf06f63fdf7e228b3153ec909a38abe8596f272, with exact code-head CI run 43819176634 passing 720 tests. Always re-read the live PR head and exact CI from GitHub before review or reporting.

No independent reviewer has reviewed the current live PR head. The next review step is independent review of that exact head. Provider Action deployment requires a separate host/cost decision and owner approval. Do not modify CAOS. Do not claim live owner-state execution, article completion, editorial acceptance or reader success until their separate evidence exists.
## 8. Status-evidence consistency

The second-pass audit found that status evidence had drifted across the repository and GitHub: the audit and evolution index pinned code head `494c9c0` / CI `43787407518` / 698 tests; the chronological journal's prior entry pinned `6551d3a` / CI `43780588561` / 689 tests; the PR body still reported `3b5e4b2` / CI `43781721412` / 690 tests; the live branch was at `543887a` with CI `43790509745` / 701 tests; and the Financial manifest still said the scope fix was CI-pending. The journal header/index also remained at revision 2.0 while the evolution index claimed 2.1.

The root cause was manual duplication of mutable candidate evidence without a cross-authority consistency regression. This update synchronizes the Financial-owned index, manifest, audit, problem journal and journal index, and adds regression checks that bind their code-head SHA, CI run, status and journal revision. The live PR head remains a GitHub readback fact and is refreshed separately after the final status commit; no recursive self-reference is stored in the evolution index.


---

## 9. Further root-cause closure — research provenance and editorial handoff (2026-11-16)

The follow-up did not stop at a green test run. It traced two additional failure paths through the actual execution callbacks.

### 9.1 ResearchPackage evidence was not fully covered by provider readback

The full-universe validator required company evidence references to resolve into the ResearchPackage evidence ledger, but the external source reader previously fetched only references listed by PrivateResearchBrief modules. There was no enforced binding between those two sets. A company-specific source could therefore exist in the ResearchPackage ledger without being among the sources whose bytes and freshness were actually checked.

The correction:
- every ResearchPackage evidence-ledger source must appear in at least one APPLICABLE PrivateResearchBrief module;
- every such source is then read by the external source reader, with body SHA and retrieval freshness checked;
- each declared universe-recall source family must match the actual provider-returned source_family for that exact source, not merely the aggregate family count;
- the verified research readback is persisted into the Research-stage owner receipt; delivery re-reads the same module references and rejects changed source sets, bytes or provider families.

This does not prove that the source is authoritative or that its text entails a financial claim. Those remain explicit semantic and domain-review duties.

### 9.2 Historical PrivateResearch 1.0 compatibility was inconsistent

Owner admission retained support for historical 1.0 briefs, while the source reader hard-coded 1.1 modules and delivery freshness skipped 1.0 entirely. The reader now selects the required module set from the persisted contract version, and delivery freshness rechecks both supported versions. A legacy 1.0 task is no longer silently exempt from source freshness merely because it predates 1.1.

### 9.3 Research-to-editorial handoff omitted decisive fields

PRIVATE_RESEARCH_SYNTHESIS produced publication_distillation; THESIS_ADJUDICATION produced company_decision_map and change_conditions. But STORY_ARCHITECTURE did not declare those as required inputs. Since _invoke_pass forwards only PassContract.required_inputs, those fields were not actually delivered to the Story Architecture model callback even though they remained in shared context.

The correction adds all three as required inputs to STORY_ARCHITECTURE. Missing fields now block the pass before the model callback. The editorial reference and executable contract describe the same handoff.

### 9.4 Exact-head verification

Candidate head 4bf06f63fdf7e228b3153ec909a38abe8596f272; exact-head CI run 43819176634: **720 tests passed**, 88% total statement coverage; whole-tree audit 340 tracked files, 132 Python AST parses, 54 JSON parses, 54,278 decoded text lines, zero warnings and zero errors. Wheel/install, DOCX rendering, four synthetic Word products and negative business replay passed.

### 9.5 Remaining business evidence

The active task cross-border-ecommerce-20261016-v3 remains RESEARCH / IN_PROGRESS, with **0/4** real deliverables, empty quality evidence and no persisted Research-stage artifact. Its stored prompt is only 跨境电商; its V2 source references are historical fixtures, not current factual evidence. No real research, article draft or Word deliverable has been generated by this follow-up.

PR #84 remains DRAFT and unmerged. The live Provider Action is NOT_DEPLOYED; independent current-head review, real source-provider execution, factual entailment, editorial acceptance and reader outcome remain open. No CAOS source or configuration was changed.

### 9.6 Validated company map is now the exact editorial handoff

A final consistency check found that the ResearchPackage's CompanyDecisionMap was structurally validated, while Thesis Adjudication emitted a separate top-level company_decision_map and change_conditions list for Story Architecture. Without a binding, the editorial pass could receive a different comparison from the one admitted in the evidence-bearing research package.

The new task-scoped handoff validator requires:
- the top-level company_decision_map to validate against the same strict CompanyDecisionMap schema and exactly match ResearchPackage.company_decision_map;
- the top-level change_conditions list to match the package map's admitted change conditions;
- the invariant to hold at Writing Kernel research completion, portfolio stage artifact creation, and standalone provider artifact readback.

The coordinator persists the canonical validated map and conditions, so Story Architecture receives the admitted version. A mismatch blocks the research stage before editorial work can start. Three targeted tests cover matching, divergent maps and divergent change conditions.