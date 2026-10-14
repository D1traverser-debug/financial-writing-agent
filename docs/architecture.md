# Financial Writing Agent — Current Architecture

## Boundary
UAOS is the sole cross-domain controller. This repository is one Financial business domain.

UAOS owns cross-domain routing, parent governance and parent-session continuity. Financial Writing independently owns article identity, article lifecycle, workflow, business/output contract, business rules, article state and artifacts.

The parent/controller identity namespace and the Financial article identity namespace are distinct. They may be related by an opaque domain state reference, but their IDs are not required to match and UAOS must not manufacture or rename a Financial article ID.

## Current locations
- Domain entry: `UAOS_SKILL.md`
- UAOS adapter metadata: `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`
- Business execution contract: `config/EXECUTION_CONTRACT.json`
- Identity-free business/output contract: `financial_writing_agent/models.py::TaskContract`
- Article identity/state: `workspaces/articles/{task_id}/STATE.json::task_id`
- Canonical workflow: `financial_writing_agent/workflow_spec.py`
- Mutation guard: `financial_writing_agent/owner_guard.py`
- Recovery/system-impact lifecycle: `financial_writing_agent/owner_lifecycle.py`
- Domain rules: `references/`, `config/policy.json`

## New article and continuation
`financial-writing:main` is a UAOS domain router only; it is not an article task.

For a new article, UAOS delegates the brief and bounded governance context. Financial Writing chooses/creates its own article `task_id`, creates the matching domain workspace/state, derives an identity-free `TaskContract`, and drives the article through the canonical workflow.

For continuation, the exact Financial article state/reference wins. UAOS may remember an opaque reference returned by the domain for parent continuity, but the child state remains authoritative for article stage and next action. Completed historical articles are never auto-resumed merely because the domain matches.

## Capability compatibility
`.uaos/CAPABILITIES.json` describes hosted integration capabilities. These declarations do not transfer article identity, workflow or business-rule ownership to UAOS.

## Invariants
- one Financial business-state authority per article;
- `STATE.task_id`, receipts, workspace paths and artifact refs form one domain-owned article identity chain;
- `TaskContract` is an identity-free value object for business/output constraints;
- no parent/child ID equality requirement;
- no route selector between multiple Financial runtimes;
- missing hard capability blocks only the affected stage;
- historical article evidence is immutable provenance and never a current route selector.

The retired domain controller/continuation namespace `continuity/` remains forbidden. Parent continuity belongs to UAOS; article continuation belongs to the exact Financial article state.
