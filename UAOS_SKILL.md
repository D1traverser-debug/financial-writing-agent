---
name: financial-writing-agent-uaos
scope: publishable A-share financial articles
---

# Financial Writing Agent — Current UAOS Entry

Controller: `D1traverser-debug/universal-agent-os@main`.
Domain repository: `D1traverser-debug/financial-writing-agent@main`.

UAOS owns intent, durable task identity, requirements, cross-chat continuation, capability orchestration and controller action lineage. This repository owns Financial business rules, the canonical article workflow, fine-grained article state, review evidence and deliverable artifacts.

## Start

After UAOS resolves the exact task, read only what the current action needs, beginning with:
1. `.uaos/ADAPTER.json`;
2. `.uaos/MANIFEST.json`;
3. `.uaos/CAPABILITIES.json`;
4. `config/EXECUTION_CONTRACT.json`;
5. the exact `workspaces/articles/{task_id}/STATE.json` when an article exists.

Before material work, confirm that every `required_uaos_common_capabilities` entry in `.uaos/CAPABILITIES.json` exists in the current UAOS `config/COMMON_CAPABILITIES.json`. Binding or capability drift blocks the affected execution; never silently substitute an older parent semantic.

Never discover controller state from repository search, chat memory, historical evals or old continuity surfaces.

## UAOS ↔ article identity binding

`financial-writing:main` is a router, not an article workspace.

For a normal new article request:
1. UAOS creates one durable Financial `task_type=article` task;
2. create the Financial article state using exactly the same `task_id`;
3. the UAOS task's `domain_business_authority` must equal `D1traverser-debug/financial-writing-agent@main:workspaces/articles/{task_id}/STATE.json`;
4. reread both authorities and apply `financial_writing_agent.uaos_binding.validate_uaos_article_binding` before material article execution.

For continuation, resolve an exact current UAOS article task. The router never auto-reactivates a completed historical article merely because the domain matches. When the user explicitly names a historical article that predates a current UAOS per-article task, create/adopt the exact UAOS article task with the same historical `task_id` before any material mutation; do not rewrite historical receipts or pretend the router itself is the article task.

This binding is a join between two authorities, not a second registry: UAOS remains task authority and `workspaces/articles/{task_id}/STATE.json` remains Financial business-state authority.

## Canonical workflow

`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

Missing hard capability blocks only the affected stage. It never authorizes a weaker SOP, free-form completion or another state authority.

Progressively load domain references:
- research: `references/research.md`, `references/knowledge.md`;
- audit: `references/audit.md`;
- editorial/title/draft: `references/editorial.md`, `references/hooks.md`, `references/style.md`;
- platform adaptation: `references/platforms.md`;
- delivery: `references/delivery.md`;
- durable rule changes: `references/maintenance.md`.

## Business-state integrity

Article state authority is `main/workspaces/articles/{task_id}/STATE.json`. Material changes bind freshly read current state, use the canonical owner guard/lifecycle, persist artifacts, then reread current authority. Domain state never replaces UAOS controller state.

Default formal contract remains `DUAL` + `WORD_FILE_ONLY` with `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX` unless the user explicitly narrows it.

Semantic self-review must keep its actual assurance label. Independent review claims require distinct execution evidence.

Historical completed article receipts are immutable provenance. Old identifiers inside those receipts are evidence only and must never select current routes.

## Completion

Completion requires both UAOS task/action satisfaction and verified current Financial business state/artifacts. Do not create a parallel controller, task registry, continuation protocol, lease or resume mechanism in this repository.
