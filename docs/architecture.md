# Financial Writing Agent — Current Architecture

## Boundary
UAOS is the sole cross-domain controller. This repository is one Financial business domain.

UAOS owns cross-domain routing, parent governance and parent-session continuity. Financial Writing independently owns article identity, article lifecycle, workflow, business rules, article state and artifacts.

The parent/controller identity namespace and the Financial article identity namespace are distinct. They may be related by an opaque domain state reference, but their IDs are not required to match and UAOS must not manufacture or rename a Financial article `task_id`.

## Current locations
- Domain entry: `UAOS_SKILL.md`
- UAOS adapter metadata: `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`
- Business execution contract: `config/EXECUTION_CONTRACT.json`
- Business task contract: `financial_writing_agent/models.py::TaskContract`
- Business state: `workspaces/articles/{task_id}/STATE.json`
- Canonical workflow: `financial_writing_agent/workflow_spec.py`
- Mutation guard: `financial_writing_agent/owner_guard.py`
- Recovery/system-impact lifecycle: `financial_writing_agent/owner_lifecycle.py`
- Domain rules: `references/`, `config/policy.json`

## New article and continuation
`financial-writing:main` is a UAOS domain router only; it is not an article task.

For a new article, UAOS delegates the brief and bounded governance context. Financial Writing then creates its own `TaskContract.task_id`, creates the matching domain workspace, and drives the article through the canonical workflow.

For continuation, the exact Financial article state/reference wins. UAOS may remember an opaque reference returned by the domain for parent continuity, but the child state remains authoritative for article stage and next action. Completed historical articles are never auto-resumed merely because the domain matches.

## Capability compatibility
`.uaos/CAPABILITIES.json` describes hosted integration capabilities. These declarations do not transfer article identity, workflow or business-rule ownership to UAOS.

## Invariants
- one Financial business-state authority per article;
- Financial `TaskContract.task_id`, `STATE.task_id`, receipts and workspace path are one domain-owned identity chain;
- no parent/child task-ID equality requirement;
- no route selector between multiple Financial runtimes;
- missing hard capability blocks only the affected stage;
- historical article evidence is immutable provenance and never a current route selector.

The retired domain controller/continuation namespace `continuity/` remains forbidden. Parent continuity belongs to UAOS; article continuation belongs to the exact Financial article state.
