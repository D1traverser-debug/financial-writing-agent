# Financial Writing Agent

A-share publishable financial-writing domain registered under Universal Agent OS (UAOS) for shared governance and cross-domain coordination, while retaining independent ownership of product requirements, article identity, workflow, business state, writing rules, domain learning/evals and deliverables.

## Current authority

Parent/common-governance authority: `D1traverser-debug/universal-agent-os@main`.

Financial business authority: `D1traverser-debug/financial-writing-agent@main`.

A fresh chat may select Financial Writing directly; normal article turns run under `DOMAIN:financial_writing` and do not require a live UAOS business proxy.

Domain entry/binding metadata:
- `UAOS_SKILL.md`
- `.uaos/MANIFEST.json`
- `.uaos/ADAPTER.json`
- `.uaos/CAPABILITIES.json`
- `config/EXECUTION_CONTRACT.json`

Product/architecture authority:
- `docs/product_requirements.md`
- `docs/architecture.md`

Article business state: `workspaces/articles/{task_id}/STATE.json`, where `task_id` is a Financial-domain article identity, not a UAOS controller task ID.

There is no domain-level cross-chat controller, parent task index, lease protocol, resume epoch or alternate business-state runtime. The retired `continuity/` namespace is physically absent from the current tree.

## Workflow

`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

Default formal contract is `DUAL` + Word delivery with `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX` unless the user explicitly narrows it.

Missing hard capability blocks only the affected stage. Same-chat semantic review stays labelled `CHAT_SELF_REVIEW`; stronger independence claims require distinct execution evidence.

## Cognition and evolution inheritance

Financial inherits the current UAOS common-capability and deliberation contracts rather than implementing a second cognition/evolution controller.

Every detected problem requires at least: micro diagnosis, macro goal/topology alignment, governing-assumption challenge and relevant external research. Small problems use a lightweight pass; material/systemic problems add deeper alternatives, counterexamples and stronger verification.

Financial owns Financial business-rule evolution. One article/user edit may create a learning candidate but cannot silently become a global rule. Systemic changes require scope/generalization analysis plus regression/eval evidence and post-promotion observation. Common/cross-domain changes are escalated to UAOS through parent guidance/upcall.

## Product review

`docs/product_requirements.md` maps the product outcome and user journeys to current owner surfaces and acceptance evidence. Major feature families, rebuilds or failures exposing missing assumptions must use the UAOS-hosted product-requirements/architecture method before implementation, while the resulting Financial requirements and architecture remain owned here.

## Business rules

Canonical rule sources live under `references/`, `config/policy.json` and the `financial_writing_agent/` deterministic implementation. Packaged reference mirrors must remain byte-equal to canonical root references.

Historical article workspaces and receipts are immutable provenance. Retired identifiers inside old receipts do not select current routes and must not be rewritten merely to make history look newer.

## Verification

Run:
```bash
pytest -q
python scripts/eval_contracts.py
python scripts/static_audit.py
python scripts/retired_runtime_static_audit.py
```
