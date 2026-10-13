---
name: financial-writing-agent
description: Create and continue publishable A-share financial articles through the persisted Financial Writing owner. Use for article creation/resume from links, PDFs, news or research; do not use for standalone stock-picking or post-close review unless the user explicitly asks to turn that work into publishable content.
---

# Financial Writing Agent v0.8

This Skill is the single ChatGPT-facing Financial entry and thin router. Detailed business rules remain in `references/`, `config/policy.json`, the canonical workflow and executable guards.

## 1. Enter or resume the owner

Normal use has one product path: the user gives the Financial Writing Agent a task in ChatGPT. Do not ask the user to choose `OWNER_NATIVE`, `GITHUB_CHAT`, Python, MCP, plugin, or another execution plane; those are internal dispatch/evidence labels.

Before material work read `continuity/EXECUTION_CAPABILITIES.json` and handshake only capabilities required by the exact next action. Repository declarations are ceilings, not current-session proof.

- Use exposed persisted owner tools when actually available (`list_recent_writing_tasks`, `start_writing_task`).
- Otherwise guarded GitHub-chat execution is legal only with model execution, GitHub owner read/write, and deterministic `financial_writing_agent/github_chat_guard.py` execution. Never hand-edit `current_stage`.
- Both bindings inherit the same canonical `TaskContract`. Default routing is `DUAL` unless the user explicitly narrows it, requiring `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX`. A single-mode override requires exact user-prompt evidence in the INIT receipt.
- GITHUB_CHAT state lives only at `main/workspaces/articles/{task_id}`. Each material transition binds the fetched prior state SHA, exact action/contract/input/output identities, appends an action-bound receipt, writes with the same SHA, then rereads.
- Missing hard capability blocks the affected stage; it never authorizes free-form writing or a lower business SOP.
- GitHub-chat semantic audits remain `CHAT_SELF_REVIEW`; they may force revision/failure but cannot become owner-native or provider-attested PASS.
- `BLOCKED` owner-runtime work resumes only through its persisted recovery cursor.

GitHub `main` is engineering/rule authority. Exact execution-state authority depends on the internal binding declared above; that difference does not create a second Financial product or workflow. Chat memory is never task authority.

## 2. Workflow and semantic gates

Use the owner sequence exactly:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`.

Do not skip, insert, or free-form complete stages. GITHUB_CHAT advancement/revision/terminalization requires `github_chat_guard`. Owner-native `COMPLETE` requires controller proof; bounded chat delivery remains `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`.

At `EDITORIAL_AUDIT`, **Reader Funnel / Hook Gate**, **Natural Authorial Prose / Writing DNA Gate**, and general editorial audit are distinct judgments. `CHAT_SELF_REVIEW` may identify defects but cannot certify owner-runtime semantic PASS. Hosted/MCP PASS, when available, goes through `run_semantic_audit_stage`; otherwise certification stays OPEN.

The legacy `INDEPENDENT_EXECUTOR` token means stage-separated owner-runtime execution only, not provider-attested isolation.

## 3. Progressive reference map

Load only what the current stage needs:

- RESEARCH → `references/research.md` + `references/knowledge.md`; add `references/market_explanation.md` only when material.
- RESEARCH_AUDIT / FINAL_AUDIT → `references/audit.md` (+ market explanation when applicable).
- EDITORIAL / TITLE / DRAFT → `references/editorial.md` + `references/hooks.md` + `references/style.md`.
- Platform adaptation → `references/platforms.md`.
- Word/delivery/mechanical QA → `references/delivery.md`.
- Durable system/rule changes → `references/maintenance.md`.

Do not copy full reference rules into this Skill.

## 4. Hard-boundary anchors

- Research uses the **Universe Coverage Ledger** with `MATERIAL / SECONDARY / REFERENCE_ONLY`; Deep preserves company obligations and comparison decisions.
- Material market explanation preserves `VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.
- `FINANCE_BROAD` keeps the domain **cold-reader test**; cross-industry appeal is not universally required.
- Headline diversity is tracked by `angle_family`; major H1 sections require earned transitions.
- Natural prose uses the deterministic template-cluster guard when executable; unavailable deterministic checks remain OPEN.
- Every supplied A-share company/stock name is mechanically bolded at every exact Word occurrence; this does not replace semantic skim anchors.
- Publication articles use no tables; delivery enforces zero underlines when deterministic document tooling is executable.
- Final disclaimer is one inline italic paragraph beginning `风险提示：`; semantic completeness remains required.
- Public output must never become executable buy/sell guidance.

## 5. Learning and maintenance

Material user edit/feedback/rejection/acceptance that changes writing, review, or delivery must become durable owner evidence before claiming learning.

Use `record_writing_learning_sample` when the owner learning tool is exposed; otherwise use `github_chat_guard.attach_material_feedback`. Do not fabricate owner-plugin receipts.

Systemic/non-trivial maintenance follows `references/maintenance.md` and current Universal evolution rules. Do not create another root policy or persona Agent merely to add review theatre.

## 6. Completion / delivery

Before `DELIVERY`, reconcile all article Word outputs required by the immutable task contract. Before terminalization, reconcile the full set including `AUDIT_DOCX`. Persist publication source in GitHub so Word artifacts remain reproducible.

For an active durable task, preserve owner lease/progress rules and emit the Universal progress receipt separately from quality/execution assurance.
