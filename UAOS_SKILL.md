---
name: financial-writing-agent-uaos
scope: publishable A-share financial articles
---

# Financial Writing Agent — UAOS Entry

Controller: `D1traverser-debug/universal-agent-os@main`.
Domain repository: `D1traverser-debug/financial-writing-agent@main`.

UAOS owns cross-domain routing, selected authority, parent-session continuity, common governance and controller action lineage. Financial Writing independently owns article identity, the article `TaskContract`, workflow, business rules, article state, review evidence and deliverable artifacts.

The two identity namespaces are deliberately distinct. A UAOS controller/router task ID is not a Financial article task ID and there is no equality requirement between them.

## Start

After UAOS routes the request to `DOMAIN:financial_writing`, read only what the current action needs, beginning with:
1. `.uaos/ADAPTER.json`;
2. `.uaos/MANIFEST.json`;
3. `.uaos/CAPABILITIES.json`;
4. `config/EXECUTION_CONTRACT.json`;
5. the exact `workspaces/articles/{task_id}/STATE.json` only when a Financial article already exists.

Before material work, confirm that declared UAOS-hosted common capabilities are available. Binding drift blocks only the affected hosted execution; it never transfers Financial business ownership to UAOS.

Never discover controller state from repository search, chat memory, historical evals or retired continuity surfaces.

## Parent/domain handoff

`financial-writing:main` is a UAOS domain router only. It never becomes an article workspace.

For a new article:
1. UAOS delegates the user brief, relevant requirements and bounded governance context to Financial Writing;
2. Financial Writing creates its own `TaskContract.task_id` and `workspaces/articles/{task_id}/STATE.json`;
3. Financial Writing executes and resumes the article using that domain-owned identity;
4. UAOS may retain an opaque reference to the returned Financial state when parent continuity needs one, but it must not manufacture, rename or require equality with the Financial task ID.

For explicit continuation, resolve the exact Financial article workspace from the user-selected or previously returned domain reference. Completed historical articles are not auto-reactivated merely because the domain matches.

## Canonical workflow

`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

Missing hard capability blocks only the affected stage. It never authorizes a weaker SOP, free-form completion or another business-state authority.

Progressively load domain references:
- research: `references/research.md`, `references/knowledge.md`;
- audit: `references/audit.md`;
- editorial/title/draft: `references/editorial.md`, `references/hooks.md`, `references/style.md`;
- platform adaptation: `references/platforms.md`;
- delivery: `references/delivery.md`;
- durable business-rule changes: `references/maintenance.md`.

## Business-state integrity

Financial article state authority is `main/workspaces/articles/{task_id}/STATE.json`, where `task_id` is a Financial-domain article identity. Material changes bind freshly read current state, use the canonical owner guard/lifecycle, persist artifacts, then reread current authority.

Default formal contract remains `DUAL` + `WORD_FILE_ONLY` with `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX` unless the user explicitly narrows it.

Semantic self-review must keep its actual assurance label. Independent review claims require distinct execution evidence.

Historical completed article receipts are immutable provenance. Old identifiers inside those receipts are evidence only and must never select current routes.

## Completion

Financial Writing determines article completion from its own workflow/state/artifacts. UAOS may consume that result to update parent progress, but the parent does not duplicate the article lifecycle or maintain a second per-article task registry.
