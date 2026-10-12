# Phase 0 — Financial System Authority / Flow / Duplication Map

Status: IN_PROGRESS
Branch: `maintenance/phase0-system-map-20261012`
Base: Financial `main` after full-system rebuild program initialization.

This file is evidence/diagnosis only. Phase 0 must not change Financial business behavior.

## Questions Phase 0 must answer

1. What is the single canonical owner for every material rule, state transition, artifact, review decision, learning signal and deployment surface?
2. Which files are canonical, generated mirrors, compatibility surfaces, historical audits, or shadow authorities?
3. Which business semantics are currently duplicated between OWNER_NATIVE and GITHUB_CHAT?
4. Which specialists have overlapping or ambiguous responsibility?
5. Where can a model, wrapper, adapter or stale state bypass a code-owned invariant?
6. Which current tests prove structure only, which prove trajectories, which prove persistence/provider boundaries, and which actually measure quality?
7. Which parent-Universal mechanisms govern Financial and which must remain outside the Financial business repository?
8. Which current design ideas came from user/assistant/external frameworks and have not yet survived Financial-specific falsification?

## Mandatory proposal-admission rule

Every material design proposal is treated as a hypothesis regardless of source:

- USER_PROPOSED
- ASSISTANT_PROPOSED
- EXISTING_OWNER_MECHANISM
- EXTERNAL_FRAMEWORK_OR_VENDOR
- OTHER_OWNER_PATTERN

Admission requires evidence and falsification, not source prestige. For each proposal record:

- problem/evidence it claims to address;
- smallest mechanism;
- competing alternative(s);
- counterexample/failure mode;
- expected benefit and cost/complexity;
- Financial-specific tracer/eval;
- hard-regression result;
- second-order attack;
- disposition: ADOPT / ADAPT / REJECT / DEFER / DELETE.

No external method is labelled "best practice" or "OK to use" until the relevant Financial-specific evaluation passes. Passing an external author's benchmark is evidence about their system, not proof about this owner.

## Initial known authority surfaces

To be completed by direct repo inspection:

- entry/router: `skills/financial-writing-agent/SKILL.md`
- business rule ownership registry: `config/rule_ownership.json`
- policy: `config/policy.json`
- architecture description: `docs/architecture.md`
- owner-native workflow: `financial_writing_agent/controller.py`, `engine.py`, `models.py`, `schemas.py`
- GitHub-chat workflow: `financial_writing_agent/github_chat_guard.py`, `continuity/GITHUB_CHAT_EXECUTION.json`
- execution/capability metadata: `continuity/EXECUTION_CAPABILITIES.json`, `continuity/AGENT_MANIFEST.json`
- specialist implementation: `financial_writing_agent/adapters/openai_agents.py`, deterministic adapters
- public owner-native tool surface: `plugin_server.py`, `mcp_contracts.py`, `runtime_service.py`
- delivery/artifacts: `document.py`, `rendering.py`, deterministic delivery executor
- learning/system impact: `system_impact.py`, `methodology_receipts.py`, quality regression runtime/corpus
- continuity/business task state: `continuity/tasks/financial-writing-main/*`
- owner-local maintenance: `references/maintenance.md`, `evals/*`
- future deployment: `deploy/chatgpt-site/SITE_SPEC.md`

## Initial duplication hypotheses (not yet accepted as defects)

- H1: Python and GitHub-chat implement stage/revision/invalidation semantics independently and can drift.
- H2: rule text exists in canonical `references/` plus packaged/resource/Skill mirrors; mirror classification may be incomplete or enforcement may rely on static equality rather than single-source generation.
- H3: `runtime_service` and `plugin_server` contain overlapping task-list/recovery/presentation logic that can diverge.
- H4: specialist prompts embed material domain rules already owned by canonical references, creating prompt-level shadow semantics.
- H5: continuity task metadata can lag owner execution profile and is not mechanically reconciled before normal work.
- H6: quality/evolution evidence has stronger deterministic infrastructure than live heldout coverage, creating a risk of process confidence outrunning outcome evidence.
- H7: parent multi-owner governance and Financial intra-owner specialist orchestration are conceptually similar but operationally different; importing parent patterns directly could create an unnecessary supervisor layer.

These are hypotheses only until evidence is recorded below.

## Phase 0 deliverables

- authority matrix;
- end-to-end current workflow graph for both adapters;
- specialist responsibility / input-output / forbidden-action matrix;
- duplication and shadow-authority register;
- evidence-level matrix for all test/eval surfaces;
- proposal/adoption ledger for user, assistant, external and other-owner mechanisms;
- failure matrix frozen before Phase 1 behavior changes;
- Phase 1 smallest cutover plan with deletion targets.
