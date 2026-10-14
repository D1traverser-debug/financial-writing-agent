---
name: financial-writing-agent-uaos
scope: publishable A-share financial content
---

# Financial Writing Agent — UAOS Entry

Controller/common-governance authority: `D1traverser-debug/universal-agent-os@main`.
Domain business authority: `D1traverser-debug/financial-writing-agent@main`.

UAOS owns cross-domain selection/governance, shared product-engineering method, parent-session continuity and hosted common capabilities. Financial Writing independently owns article identity, lifecycle, product/business requirements, workflow, business/output contract, writing rules, article state, review evidence and deliverable artifacts.

The two identity namespaces are deliberately distinct. A UAOS controller/router task ID is not a Financial article ID and there is no equality requirement between them.

## Start and direct activation

A fresh chat may select Financial Writing directly. Once selected, `DOMAIN:financial_writing` is the current Agent/work plane; normal business turns do **not** traverse a live UAOS business proxy.

Read only what the current action needs, beginning with:
1. `.uaos/ADAPTER.json`;
2. `.uaos/MANIFEST.json`;
3. `.uaos/CAPABILITIES.json`;
4. `docs/product_requirements.md` and `docs/architecture.md` when product/architecture scope is material;
5. `config/EXECUTION_CONTRACT.json`;
6. `references/reader_value.md` for current publication reader-value / company-decision / platform-product semantics;
7. the exact `workspaces/articles/{task_id}/STATE.json` only when a Financial article already exists.

Before material work, confirm the current UAOS-hosted common-capability contract. Binding drift blocks only the affected hosted capability; it never transfers Financial business ownership to UAOS.

Never discover controller state from repository search, chat memory, historical evals or retired continuity surfaces.

## New article and continuation

`financial-writing:main` is a UAOS selector/router entry only. It never becomes an article workspace.

For a new article:
1. Financial receives the user brief plus applicable scoped requirements;
2. Financial creates its own article `task_id`/`STATE.json` and an identity-free `TaskContract`;
3. Financial executes/resumes through its own state/workspace identity;
4. UAOS may retain only an opaque returned Financial state reference for parent continuity.

For explicit continuation, resolve the exact Financial article workspace. Completed historical articles are not auto-reactivated merely because the domain matches.

## Canonical workflow

`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

Missing hard capability blocks only the affected stage. It never authorizes a weaker SOP or another business-state authority.

Progressively load:
- research: `references/research.md`, `references/knowledge.md`, `references/reader_value.md` when companies/reader value are material;
- audit: `references/audit.md`, `references/reader_value.md`;
- editorial/title/draft: `references/editorial.md`, `references/hooks.md`, `references/style.md`, `references/reader_value.md`;
- platform adaptation: `references/platforms.md`, `references/reader_value.md`;
- delivery: `references/delivery.md`, `references/reader_value.md`;
- maintenance/product changes: `references/maintenance.md`, `docs/product_requirements.md`, `docs/architecture.md`.

## Current publication product contract

For **new** work, the default formal contract is `PORTFOLIO + WORD_FILE_ONLY`:
- `FINANCE_DEEP_DOCX` — deep finance/review;
- `FINANCE_BROAD_DOCX` — finance-domain acquisition long-form;
- `PLATFORM_INTERACTION_PACK_DOCX` — independently rewritten short image-text / 微头条 / 动态 copy;
- `AUDIT_DOCX`.

Broad-feed-only targeting may resolve to `ACQUISITION` (Broad + interaction pack + audit). Deep-only finance-community targeting may resolve to `FINANCE_DEEP`.

Historical compatibility is immutable: existing `DUAL` remains Deep + Broad + Audit, and existing `FINANCE_BROAD` remains Broad + Audit. Do not rewrite historical article contracts/receipts merely because the new default expanded.

## Reader value / decision utility

`references/reader_value.md` is current authority for the semantics promoted from the 2026-10-15 material feedback:
- publication copy keeps research provenance private unless attribution itself is part of the factual claim;
- Natural Authorial Prose controls repeated syntactic/rhetorical molds across title/H1/body rather than doing surface synonym swaps;
- selected title exposes concrete hard information + a finance-wide stake + one real unresolved payoff;
- the first three complete sentences collectively establish hard fact/anomaly + finance-wide consequence + material unresolved payoff;
- multiple `MATERIAL` companies require a Company Decision Map and named evidence-bounded comparative verdict;
- relative judgments such as more direct/pure, faster realization, harder evidence or greater-but-less-certain elasticity are legal when evidenced and paired with change conditions;
- executable recommendation remains prohibited: buy/sell, entry timing, target price, position sizing or covert equivalents;
- when H2/H3 follows H1, a substantive H1 lead paragraph is mandatory for reasoning continuity and the user's later image insertion workflow;
- Broad is an independent acquisition rebuild, not a shortened Deep article;
- interaction copy is independently rewritten from the audited evidence base, not truncated long-form prose.

## Hosted cognition — mandatory problem response

Financial Writing inherits UAOS adaptive deliberation; it does not create a second cognition controller.

Whenever a problem is detected — defect, failed/degraded output, user correction/rejection, contradiction, repeated repair, uncertain goal satisfaction or other evidence that behavior is unreliable — the session performs at least:
1. concrete/micro diagnosis;
2. macro goal/topology/architecture alignment;
3. challenge of the governing assumption/boundary/causal explanation;
4. relevant external research.

Familiarity is not a waiver. Material/systemic problems require deeper alternatives, counterexamples and stronger verification. If the issue is common/cross-domain, Financial issues a parent upcall; otherwise Financial retains ownership and repairs its own surface.

## Governed evolution

Every detected problem is evaluated for learning impact, but not every incident becomes a durable rule.

For Financial-owned learning:
1. preserve observed problem/user feedback as evidence;
2. classify root-cause layer and generalization scope;
3. compare credible alternatives and identify the owning surface;
4. keep one-off observations as candidates until evidence supports promotion;
5. add regression/eval evidence for systemic changes;
6. promote only through Financial-owned authority and verify final production;
7. observe post-promotion behavior and keep/rollback/retire accordingly.

`owner_lifecycle.py` owns article-linked feedback/system-impact state. `references/maintenance.md` owns maintenance method. Cross-domain/common-capability evolution remains UAOS-owned.

## Product review / requirements completeness

For a major feature family, rebuild, or a failure revealing missing product assumptions, use UAOS-hosted product requirements/architecture governance before implementation. Financial persists the result in `docs/product_requirements.md` and `docs/architecture.md`.

The review covers user outcome, functional/non-functional requirements, workflow/state, failure/recovery, evidence/assurance, acceptance/evals, ownership boundaries and explicit non-goals. Product documentation alone is not acceptance evidence.

## Business-state integrity

Financial article identity authority is `STATE.task_id` inside `workspaces/articles/{task_id}/STATE.json`. The same domain-owned ID binds workspace paths, receipts and artifact references. `TaskContract` is intentionally identity-free and only describes business/output constraints.

Material changes bind freshly read current state, use the owner guard/lifecycle, persist artifacts, then reread authority.

Semantic self-review keeps its actual assurance label. Independent review claims require distinct execution evidence.

Historical completed article receipts are immutable provenance and never current route selectors.

## Completion

Financial determines completion from its own workflow/state/artifacts. UAOS may consume that result for parent progress but does not duplicate the article lifecycle or maintain a second per-article registry.
