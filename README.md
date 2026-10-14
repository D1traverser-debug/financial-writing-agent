# Financial Writing Agent

A-share publishable financial-writing domain registered under Universal Agent OS (UAOS) for cross-domain routing and governance, while retaining independent ownership of article identity, workflow, business state, writing rules and deliverables.

## Current authority

Cross-domain controller: `D1traverser-debug/universal-agent-os@main`.

Financial business authority: `D1traverser-debug/financial-writing-agent@main`.

Domain entry/binding metadata:
- `UAOS_SKILL.md`
- `.uaos/MANIFEST.json`
- `.uaos/ADAPTER.json`
- `.uaos/CAPABILITIES.json`
- `config/EXECUTION_CONTRACT.json`

Article business state: `workspaces/articles/{task_id}/STATE.json`, where `task_id` is a Financial-domain article identity, not a UAOS controller task ID.

There is no domain-level cross-chat controller, parent task index, lease protocol, resume epoch or alternate business-state runtime. The retired `continuity/` namespace is physically absent from the current tree.

## Workflow

`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

Default formal contract is `DUAL` + Word delivery with `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX` unless the user explicitly narrows it.

Missing hard capability blocks only the affected stage. Same-chat semantic review stays labelled `CHAT_SELF_REVIEW`; stronger independence claims require distinct execution evidence.

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
