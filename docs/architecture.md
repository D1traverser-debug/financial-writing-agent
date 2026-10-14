# Financial Writing Agent — Current Architecture

## Boundary
UAOS is the sole cross-domain parent/control plane. This repository is one Financial business domain and can run directly as the current Agent/work plane after domain selection.

UAOS owns cross-domain selection/governance, hosted common capabilities, shared product-engineering method and parent-session continuity. Financial Writing independently owns product requirements, article identity, article lifecycle, workflow, business/output contract, business rules, article state, domain learning/evals and artifacts.

The parent/controller identity namespace and the Financial article identity namespace are distinct. They may be related by an opaque domain state reference, but their IDs are not required to match and UAOS must not manufacture or rename a Financial article ID.

Normal Financial business turns do not require a live UAOS proxy. Parent guidance is an escalation path for common/cross-domain concerns, scope arbitration or shared-governance evolution.

## Current locations
- Domain entry: `UAOS_SKILL.md`
- Product requirements: `docs/product_requirements.md`
- UAOS adapter metadata: `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`
- Hosted common capability authority: `D1traverser-debug/universal-agent-os@main:config/COMMON_CAPABILITIES.json`
- Hosted cognition authority: `D1traverser-debug/universal-agent-os@main:config/DELIBERATION_POLICY.json`
- Business execution contract: `config/EXECUTION_CONTRACT.json`
- Identity-free business/output contract: `financial_writing_agent/models.py::TaskContract`
- Article identity/state: `workspaces/articles/{task_id}/STATE.json::task_id`
- Canonical workflow: `financial_writing_agent/workflow_spec.py`
- Mutation guard: `financial_writing_agent/owner_guard.py`
- Recovery/system-impact lifecycle: `financial_writing_agent/owner_lifecycle.py`
- Domain quality regression/evolution evidence: `financial_writing_agent/quality_regression.py`, `evals/`
- Domain maintenance method: `references/maintenance.md`
- Domain rules: `references/`, `config/policy.json`

## New article and continuation
`financial-writing:main` is a UAOS selector/router entry only; it is not an article task and is not a prerequisite runtime hop.

For a new article, the selected Financial Agent receives the brief and applicable global/governance context, chooses/creates its own article `task_id`, creates the matching domain workspace/state, derives an identity-free `TaskContract`, and drives the article through the canonical workflow.

For continuation, the exact Financial article state/reference wins. UAOS may remember an opaque reference returned by the domain for parent continuity, but the child state remains authoritative for article stage and next action. Completed historical articles are never auto-resumed merely because the domain matches.

## Hosted cognition architecture
Financial does not implement a second deliberation controller. The current session consumes UAOS-hosted cognition through `.uaos/CAPABILITIES.json`.

For every detected problem, the minimum epistemic path is:
`micro diagnosis -> macro goal/topology alignment -> governing-assumption challenge -> relevant external research -> repair selection`.

Problem size changes depth, not whether the path runs. Risk may add counterexample search, stronger evals and genuinely independent evidence. If the owning cause is common/cross-domain, the Financial Agent issues a parent upcall; otherwise it retains domain ownership and repairs its own surface.

## Governed evolution architecture
Financial owns domain business-rule evolution but not cross-domain/global evolution.

Domain evolution path:
`problem/feedback -> hosted research+reflection -> root-cause/generalization review -> alternatives -> candidate -> regression/eval -> Financial promotion -> post-promotion observation -> keep/rollback/retire`.

`owner_lifecycle.py` binds material article feedback to system-impact review. `quality_regression.py` and `evals/` provide business-quality promotion evidence. A single article/edit may generate a candidate but cannot silently become a global writing rule.

Cross-domain/common capability changes remain UAOS-owned and use parent guidance/upcall rather than a second controller inside this repository.

## Product architecture review
`docs/product_requirements.md` is the current product requirement map. It is generated/maintained using UAOS-hosted product-requirements/architecture governance but remains Financial-owned authority.

Major feature families or rebuilds must reconcile: user outcome, functional and non-functional requirements, workflow/state, failure/recovery, evidence/assurance, acceptance/evals, ownership boundaries and non-goals before implementation is considered architecturally complete.

## Capability compatibility
`.uaos/CAPABILITIES.json` describes hosted integration capabilities and the minimum UAOS common-capability contract expected by this domain. These declarations do not transfer product requirements, article identity, workflow or business-rule ownership to UAOS.

## Invariants
- one Financial business-state authority per article;
- `STATE.task_id`, receipts, workspace paths and artifact refs form one domain-owned article identity chain;
- `TaskContract` is an identity-free value object for business/output constraints;
- no parent/child ID equality requirement;
- no route selector between multiple Financial runtimes;
- direct child activation does not require a live parent business proxy;
- every detected problem inherits the UAOS research/reflection floor;
- domain evolution promotes only evidence-backed Financial rules at their justified scope;
- missing hard capability blocks only the affected stage;
- historical article evidence is immutable provenance and never a current route selector.

The retired domain controller/continuation namespace `continuity/` remains forbidden. Parent continuity belongs to UAOS; article continuation belongs to the exact Financial article state.
