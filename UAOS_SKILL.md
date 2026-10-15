---
name: financial-writing-agent-uaos
scope: publishable A-share financial content
---

# Financial Writing Agent — UAOS Entry

Controller/common-governance authority: `D1traverser-debug/universal-agent-os@main`.
Domain business authority: `D1traverser-debug/financial-writing-agent@main`.

UAOS owns cross-domain selection/governance, parent continuity and hosted common capabilities. Financial Writing owns article identity/state, product requirements, workflow, business/output contract, domain rules, review evidence and deliverables. Parent/router IDs and Financial article IDs are distinct namespaces with **no equality requirement**. `TaskContract` is intentionally identity-free.

## Start and authority

A fresh chat may select Financial Writing directly. Once selected, `DOMAIN:financial_writing` is the current work plane; normal article turns do **not** traverse a live UAOS business proxy.

Load only what the action needs:
1. `.uaos/ADAPTER.json`, `.uaos/MANIFEST.json`, `.uaos/CAPABILITIES.json`;
2. `config/EXECUTION_CONTRACT.json`;
3. `docs/product_requirements.md` / `docs/architecture.md` for product/architecture work;
4. exact article `STATE.json` only when an article exists.

Confirm both the hosted UAOS common-capability contract and common behavior-assurance contract before material work. Binding drift blocks affected capability only; it never transfers Financial ownership to UAOS.

`financial-writing:main` is a selector/router entry, not an article task. Financial creates/owns its own article `task_id` and `STATE.json`; UAOS may retain only an opaque returned state reference.

## Workflow and references

Canonical workflow:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

Missing hard capability blocks the affected stage; it does not authorize a weaker fallback.

Progressive references:
- research: `references/research.md`, `references/knowledge.md`, `references/reader_value.md`;
- audit: `references/audit.md`, `references/reader_value.md`;
- editorial/title/draft: `references/editorial.md`, `references/hooks.md`, `references/style.md`, `references/reader_value.md`;
- platform: `references/platforms.md`, `references/reader_value.md`;
- delivery: `references/delivery.md`, `references/reader_value.md`;
- maintenance: `references/maintenance.md`, `references/proactive_resolution.md`, product/architecture docs.

## Current product contract

For new ordinary work, default `PORTFOLIO + WORD_FILE_ONLY` produces:
- `FINANCE_DEEP_DOCX` — deep finance/review;
- `FINANCE_BROAD_DOCX` — acquisition long-form;
- `PLATFORM_INTERACTION_PACK_DOCX` — independently rewritten short image-text / 微头条 / 动态 copy;
- `AUDIT_DOCX`.

Broad-feed-only targets may use `ACQUISITION` (Broad + interaction pack + audit). Finance-community-only targets may use `FINANCE_DEEP`.

Historical compatibility is immutable: existing `DUAL` remains Deep + Broad + Audit and existing `FINANCE_BROAD` remains Broad + Audit. Never rewrite historical task contracts or receipts because the new default expanded.

## Reader value / company decision utility

`references/reader_value.md` owns the current promoted semantics:
- publication prose does not expose the research trail merely to prove sourcing;
- Natural Authorial Prose is **voice/material first**: bind reader, author stance, audited evidence and the strongest available user-owned voice samples before drafting;
- AI-associated phrase/structure patterns are post-draft diagnostic signals, not mandatory generation bans or quotas; one isolated signal is not a failure by itself;
- substantial long-form work compares genuinely different opening/section strategies when multiple routes are plausible rather than generating synonym variants;
- `DRAFT` writes; `EDITORIAL_AUDIT` separately rereads as Reader / Editor / Style critic. Same-session critic passes are useful challenge evidence, not independent verification;
- title/opening/H1 requirements are reader outcomes, not one-to-one sentence formulas;
- two or more `MATERIAL` companies require a Company Decision Map and a named evidence-bounded comparative judgment, but no fixed prose order is imposed;
- relative judgments such as more direct/pure, faster realization, harder evidence or higher-but-less-certain elasticity are legal when evidenced and paired with change conditions;
- buy/sell, entry timing, target price, position sizing and covert equivalents remain prohibited;
- H1 with H2/H3 children requires a substantive lead paragraph for reasoning continuity and the user's later image insertion;
- Broad is rebuilt for acquisition rather than shortened from Deep;
- interaction copy is independently rewritten from the audited evidence base and may not rely on canned “human-feel” slang/questions.

## Mandatory problem response

Financial inherits UAOS adaptive deliberation. Every detected defect, user correction/rejection, degraded outcome, contradiction, repeated repair or unreliable goal satisfaction requires at least:
1. micro diagnosis;
2. macro goal/topology alignment;
3. governing-assumption challenge;
4. relevant external research.

Familiarity is not a waiver. Material problems require alternatives/counterexamples and stronger verification. Common/cross-domain causes upcall UAOS; Financial-local causes remain Financial-owned.

After diagnosis, Financial also inherits UAOS problem-to-action closure: if an owner-authorized repair is currently available and no required user fact/approval/authorization/safety-sensitive choice blocks it, Financial must attempt the repair before ending the turn. Recommendation-only is not valid closure for a currently repairable problem.

## Executable proactive resolution before user escalation

`financial_writing_agent/proactive_resolution.py` owns the executable recovery receipt and escalation gate. Before externalizing a recoverable dependency, Financial must persist either a safe evidence-bound `RESOLVED/PROVISIONAL` result and continue, or an unsafe `UNRESOLVED` result with concrete blockers and pass `require_user_escalation_admission`. Explicit user confirmation remains legal.

A safe provisional result is not escalation-eligible. See `references/proactive_resolution.md` for evidence order, confidence/validation semantics and assurance limits. Current assurance is executable policy + trajectory evidence until live article behavior accumulates; host-level physical interception is not claimed.

## Governed evolution

Financial-owned learning follows:
`problem/feedback -> research+reflection -> root cause/scope -> alternatives -> candidate -> regression/eval -> owner promotion -> post-promotion observation -> keep/rollback/retire`.

`financial_writing_agent/owner_lifecycle.py` owns article-linked feedback/system-impact state; `financial_writing_agent/proactive_resolution.py` owns recoverable-dependency action receipts/user-escalation admission; `references/maintenance.md` owns the maintenance method. One article can create evidence but does not silently become a universal rule. Cross-domain/common-capability evolution remains UAOS-owned.

Major product changes use UAOS-hosted product-review method and persist resulting domain requirements/architecture locally. Product documentation alone is not acceptance evidence.

## State integrity and completion

Financial article identity authority is `workspaces/articles/{task_id}/STATE.json::task_id`. `TaskContract` is intentionally identity-free and only describes business/output constraints.

Material changes bind fresh owner state, use owner guard/lifecycle/proactive-resolution admission as applicable, persist evidence and reread authority. Same-chat semantic review keeps `CHAT_SELF_REVIEW`; independent claims require distinct execution evidence.

Historical completed receipts are immutable provenance and never route selectors.

Financial determines completion from its own state/artifacts. UAOS may consume the result for parent progress but does not duplicate the article lifecycle.