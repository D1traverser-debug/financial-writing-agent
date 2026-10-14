---
name: financial-writing-agent-uaos
scope: publishable A-share financial articles
---

# Financial Writing Agent — UAOS Entry

Controller/common-governance authority: `D1traverser-debug/universal-agent-os@main`.
Domain business authority: `D1traverser-debug/financial-writing-agent@main`.

UAOS owns cross-domain selection/governance, shared product-engineering method, parent-session continuity and hosted common capabilities. Financial Writing independently owns article identity, article lifecycle, product/business requirements, workflow, business/output contract, writing rules, article state, review evidence and deliverable artifacts.

The two identity namespaces are deliberately distinct. A UAOS controller/router task ID is not a Financial article ID and there is no equality requirement between them.

## Start and direct activation

A fresh chat may select Financial Writing directly. Once selected, `DOMAIN:financial_writing` is the current Agent/work plane; normal article turns do **not** traverse a live UAOS business proxy and the user does not need to first enter a UAOS controller conversation.

Read only what the current action needs, beginning with:
1. `.uaos/ADAPTER.json`;
2. `.uaos/MANIFEST.json`;
3. `.uaos/CAPABILITIES.json`;
4. `docs/product_requirements.md` and `docs/architecture.md` when product/architecture scope is material;
5. `config/EXECUTION_CONTRACT.json`;
6. the exact `workspaces/articles/{task_id}/STATE.json` only when a Financial article already exists.

Before material work, confirm that the current UAOS-hosted common-capability contract referenced by `.uaos/CAPABILITIES.json` is available. Binding drift blocks only the affected hosted capability; it never transfers Financial business ownership to UAOS.

Never discover controller state from repository search, chat memory, historical evals or retired continuity surfaces.

## New article and continuation

`financial-writing:main` is a UAOS selector/router entry only. It never becomes an article workspace and is not a prerequisite business task.

For a new article:
1. the current Financial Agent receives the user brief plus any applicable global requirements/governance context already present in the session;
2. Financial Writing chooses/creates its own article `task_id`, creates the corresponding `STATE.json`, and builds an identity-free `TaskContract` for output/business constraints;
3. Financial Writing executes and resumes the article using its own state/workspace identity;
4. UAOS may retain an opaque reference to the returned Financial state when parent continuity actually needs one, but it must not manufacture, rename or require equality with the Financial article ID.

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
- durable business-rule/product changes: `references/maintenance.md`, `docs/product_requirements.md`, `docs/architecture.md`.

## Hosted cognition — mandatory problem response

Financial Writing inherits UAOS adaptive deliberation; it does not create a second cognition controller.

Whenever a problem is detected — defect, failed/degraded output, user correction/rejection, contradiction, repeated repair, uncertain goal satisfaction or other evidence that the current behavior is unreliable — the session must perform at least:
1. concrete/micro diagnosis;
2. macro goal/topology/architecture alignment;
3. challenge of the current governing assumption/boundary/causal explanation;
4. relevant external research.

Familiarity is not a waiver. Small problems may use a lightweight pass; material/systemic problems require deeper comparison, counterexamples and stronger verification. Research must affect or validate the diagnosis/repair rather than being ceremonial browsing.

If the problem is common/cross-domain, changes parent/common capabilities, or needs scope arbitration, Financial issues a non-mutating parent upcall for UAOS guidance. Otherwise Financial retains business ownership and repairs the Financial owning surface itself.

## Governed evolution

Every detected problem is evaluated for learning impact after the cognition floor, but not every incident becomes a durable rule.

For Financial-owned learning:
1. preserve the observed problem/user feedback as evidence;
2. classify the failure/root-cause layer and generalization scope;
3. compare credible alternatives and identify the unique owning surface;
4. keep one-off observations as candidates unless evidence supports promotion;
5. add regression/eval evidence for systemic changes;
6. promote only through Financial-owned authority and verify the final tree;
7. observe post-promotion behavior and keep/rollback/retire accordingly.

`financial_writing_agent/owner_lifecycle.py` owns article-linked material-feedback/system-impact state. `references/maintenance.md` owns domain maintenance method. Cross-domain/common-capability evolution remains UAOS-owned; Financial supplies evidence and a parent upcall rather than creating another controller.

## Product review / requirements completeness

For a major feature family, rebuild, or a failure that reveals missing product assumptions, use UAOS-hosted product requirements/architecture governance before implementation. Financial persists the domain result in `docs/product_requirements.md` and `docs/architecture.md`.

The review must cover at minimum: user outcome, functional requirements, non-functional constraints, article/workflow state, failure/recovery, evidence/assurance, acceptance/evals, ownership boundaries and explicit non-goals. Product documentation is not proof by itself; requirements must map to executable tests/evals or observable acceptance evidence.

## Business-state integrity

Financial article identity authority is `STATE.task_id` inside `workspaces/articles/{task_id}/STATE.json`. The same domain-owned ID binds workspace paths, receipts and artifact references. `TaskContract` is intentionally identity-free and only describes business/output constraints.

Material changes bind freshly read current state, use the canonical owner guard/lifecycle, persist artifacts, then reread current authority.

Default formal contract remains `DUAL` + `WORD_FILE_ONLY` with `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX` unless the user explicitly narrows it.

Semantic self-review must keep its actual assurance label. Independent review claims require distinct execution evidence.

Historical completed article receipts are immutable provenance. Old identifiers inside those receipts are evidence only and must never select current routes.

## Completion

Financial Writing determines article completion from its own workflow/state/artifacts. UAOS may consume that result to update parent progress, but the parent does not duplicate the article lifecycle or maintain a second per-article task registry.
