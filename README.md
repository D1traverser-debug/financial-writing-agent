# Financial Writing Agent — CAOS child

**Business authority:** `D1traverser-debug/financial-writing-agent@main`.
**Cognition parent:** `D1traverser-debug/cognition-agent-os@main`.
**Current status:** CAOS child interface with guarded, child-owned state effects; independent end-to-end editorial quality is **NOT_READY**. The former Universal Agent OS is not the parent.

## Entry and identity

- [CAOS_SKILL.md](CAOS_SKILL.md) — canonical opt-in ChatGPT/domain routing and workflow; direct Financial activation is allowed without a CAOS local Host.
- [docs/CAOS_CHILD_INTERFACE.md](docs/CAOS_CHILD_INTERFACE.md) — actual source-pinned parent boundary, supported bridge calls, grants, CAS/readback and limitations.
- `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json` — legacy **filenames only** retained because present CAOS `domain_contract.py` reads them; contents declare CAOS and one Financial business owner.
- `financial_writing_agent/caos_bridge.py` — child-native guarded write/readback API, not a second task state machine or deployed CAOS Host.
- `config/PERSISTENT_ASSET_PROFILE.json` — Financial-owned register of GitHub authority versus Notion/Drive/Library/Chat/Memory research/history/delivery surfaces; no old UAOS parent policy or second task controller.
- `financial_writing_agent/current_admission.py` — **only** current-article mutation authority; one task per `workspaces/articles/{task_id}/STATE.json`. Current task requirements and evolution live in their existing canonical locations.

## Financial product

Research goes from verified primary-source chronology and complete material economic company pool through adversarial evidence and PrivateResearchBrief 1.1 to DecisionEnvelope. Deep and Broad are independently designed articles, with story blueprints, company-specific financial transmission and source-compared originality. Same-chat checks remain non-independent.

External workflow:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`.

Default user-facing deliverables: Deep DOCX, Broad DOCX, platform interaction DOCX and audit DOCX. A current admitted private research brief may require an additional private DOCX on presentation. Actual binary existence, correct hashes, render/visual evidence and available user links are a separate acceptance level.

`workspaces/articles/cross-border-ecommerce-20261016-v3/STATE.json` remains an **IN_PROGRESS / RESEARCH** task with two admitted user requirements. Neither historical v2 Word receipts nor this repository's green CI certifies the v3 product.

## Verification

```bash
python -m pip install -e '.[dev]'
pytest -q
python scripts/eval_contracts.py
python scripts/static_audit.py
python scripts/retired_runtime_static_audit.py
```

GitHub CI also tests isolated wheel installation and DOCX render. The exact-head CI is engineering evidence only. Genuine CAOS Host attachment, parent Skill invocation, independent source adjudication, publication quality and audience outcomes need their respective actual observations. Do not claim a remote bridge grant or editorial PASS from fixture callbacks.

One codebase may be routed by CAOS but parent source code remains outside the child; no CAOS source, grant or runtime state is modified by this repository.
