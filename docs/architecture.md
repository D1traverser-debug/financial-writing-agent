# Financial Writing Agent — Current Architecture

## Boundary
UAOS is the sole cross-domain controller. This repository is one Financial business domain.

UAOS owns durable task identity and cross-chat continuation. Financial Writing owns business workflow/rules/state/artifacts. The integration boundary is a one-to-one binding, not a duplicated controller: a UAOS Financial `task_type=article` task and its Financial `STATE.json` share the same `task_id`, and the UAOS task points to that exact state through `domain_business_authority`.

## Current locations
- Domain entry: `UAOS_SKILL.md`
- UAOS binding: `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`
- Business execution contract: `config/EXECUTION_CONTRACT.json`
- UAOS/article binding validator: `financial_writing_agent/uaos_binding.py`
- Business state: `workspaces/articles/{task_id}/STATE.json`
- Canonical workflow: `financial_writing_agent/workflow_spec.py`
- Mutation guard: `financial_writing_agent/owner_guard.py`
- Recovery/system-impact lifecycle: `financial_writing_agent/owner_lifecycle.py`
- Domain rules: `references/`, `config/policy.json`

## New article and continuation
`financial-writing:main` is a UAOS workspace router only. It must never serve as the business identity of an article.

For a new article, UAOS creates the durable per-article task first; Financial Writing creates the article state with the same ID; then the exact controller/business-state binding is reread and validated before material execution.

For continuation, an exact current UAOS article task wins. A completed historical article is never auto-resumed from domain similarity. If the user explicitly selects a historical article that predates a current UAOS per-article task, UAOS may adopt/create the exact task identity with the same historical article ID before mutation; the historical receipts remain immutable.

## Capability compatibility
`.uaos/CAPABILITIES.json` declares the UAOS common capabilities this domain requires. The active host must compare that list against current UAOS `config/COMMON_CAPABILITIES.json` during binding admission. A missing required common capability is binding drift, not permission to silently run older semantics.

## Invariants
There is one article-state authority and no route selector between multiple runtimes. Missing hard capability blocks the affected stage. Material changes bind current state and reread written authority. Historical article evidence is immutable provenance and never a current route selector.

The retired domain controller/continuation namespace `continuity/` is forbidden from the current tree. Cross-chat identity/continuation exists only in UAOS.
