# Financial Writing Agent — Current Architecture

## Boundary
UAOS is the sole cross-domain controller. This repository is one Financial business domain.

## Current locations
- Domain entry: `UAOS_SKILL.md`
- UAOS binding: `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`
- Business execution contract: `config/EXECUTION_CONTRACT.json`
- Business state: `workspaces/articles/{task_id}/STATE.json`
- Canonical workflow: `financial_writing_agent/workflow_spec.py`
- Mutation guard: `financial_writing_agent/owner_guard.py`
- Recovery/system-impact lifecycle: `financial_writing_agent/owner_lifecycle.py`
- Domain rules: `references/`, `config/policy.json`

## Invariants
There is one article-state authority and no route selector between multiple runtimes. Missing hard capability blocks the affected stage. Material changes bind current state and reread written authority. Historical article evidence is immutable provenance and never a current route selector.

The retired domain controller/continuation namespace `continuity/` is forbidden from the current tree. Cross-chat identity/continuation exists only in UAOS.
