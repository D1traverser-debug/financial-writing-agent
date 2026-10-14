# Financial Writing Agent

A-share publishable financial-writing domain owned by Universal Agent OS (UAOS).

## Current authority

Cross-domain control: `D1traverser-debug/universal-agent-os@main`.

Domain entry/binding:
- `UAOS_SKILL.md`
- `.uaos/MANIFEST.json`
- `.uaos/ADAPTER.json`
- `.uaos/CAPABILITIES.json`
- `config/EXECUTION_CONTRACT.json`

Article business state: `workspaces/articles/{task_id}/STATE.json`.

There is no domain-level cross-chat controller, task index, lease protocol, resume epoch or alternate business-state runtime. The retired `continuity/` namespace is physically absent from the current tree.

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
