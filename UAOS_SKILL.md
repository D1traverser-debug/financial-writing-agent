---
name: financial-writing-agent-uaos
scope: publishable A-share financial articles
---

# Financial Writing Agent — UAOS Entry

Controller: `D1traverser-debug/universal-agent-os@main`.
Domain repository: `D1traverser-debug/financial-writing-agent@main`.

UAOS owns intent, task identity, requirements, cross-chat continuation, capability orchestration and controller action lineage. This repository owns Financial business rules, the article workflow, fine-grained article state, review evidence and deliverable artifacts.

## Start

After UAOS resolves the exact task, read only:
1. `continuity/UAOS_ADAPTER.json`;
2. `continuity/UAOS_MANIFEST.json`;
3. `continuity/EXECUTION_CAPABILITIES.json`;
4. `continuity/FINANCIAL_OWNER_EXECUTION.json`;
5. the exact article `workspaces/articles/{task_id}/STATE.json` when an article exists.

Do not discover controller state from other continuity files, historical branches, chat memory, or search results.

## Workflow

Use the canonical sequence:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`.

Missing hard capability blocks only the affected stage. Do not switch to a weaker business SOP or create a second state authority.

Progressively load domain references only when the current stage requires them:
- research: `references/research.md`, `references/knowledge.md`;
- audit: `references/audit.md`;
- editorial/title/draft: `references/editorial.md`, `references/hooks.md`, `references/style.md`;
- platform adaptation: `references/platforms.md`;
- delivery/mechanical QA: `references/delivery.md`;
- durable domain-rule changes: `references/maintenance.md`.

## Business-state integrity

Article state authority is `main/workspaces/articles/{task_id}/STATE.json`. Material Financial mutations use the domain guard against freshly fetched state, bind the prior blob identity, persist the new business artifact/state, then reread it. Domain state never replaces the UAOS task/controller state.

The default formal task contract remains DUAL unless the user explicitly narrows it. Required outputs are `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX` through Word delivery.

Semantic self-review must be labelled at its real assurance level. Do not claim provider-attested independent review without distinct execution evidence.

## Completion

Completion requires both:
- the UAOS task/action state to satisfy the current task contract; and
- the exact Financial business state, review gates and required deliverables to be verified and currently resolvable.

Do not create a parallel controller, task registry or continuation protocol inside this repository.
