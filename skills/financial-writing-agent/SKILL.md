---
name: financial-writing-agent
description: Create and continue publishable A-share financial articles through the persisted Financial Writing owner. Use for article creation/resume from links, PDFs, news or research; do not use for standalone stock-picking or post-close review unless the user explicitly asks to turn that work into publishable content.
---

# Financial Writing Agent v0.8

This Skill is a thin router and the single ChatGPT-facing Financial entry. Detailed business rules remain in `references/`, `config/policy.json`, the canonical workflow and executable guards.

## 1. One production path

Financial Writing has one production path for this user:

**ChatGPT executes the writing task; GitHub `main` stores the Financial code, rules, article state and durable evidence.**

Do not ask the user to choose `OWNER_NATIVE`, `GITHUB_CHAT`, Python, MCP, plugin, or any other execution mode. Python modules, controllers, plugin/MCP surfaces and deterministic executors are implementation/test components behind this one ChatGPT + GitHub workflow, not alternative user workflows.

Before material work read `continuity/EXECUTION_CAPABILITIES.json` and handshake only capabilities required by the exact next action. Repository declarations are ceilings, not current-session proof.

- Normal task transitions and material feedback capture use `financial_writing_agent/github_chat_guard.py`.
- BLOCKED review recovery and system-impact review/closure use `financial_writing_agent/github_chat_lifecycle.py`.
- Never hand-edit `current_stage`, clear a blocker, clear maintenance debt, narrow required outputs, or claim a transition happened unless the corresponding deterministic guard accepted it.
- The canonical `TaskContract` is always authoritative. Routing defaults to `DUAL` unless the user explicitly narrows it, requiring `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX`. A single-mode override requires exact user-prompt evidence in the INIT receipt.
- `main/workspaces/articles/{task_id}` is the only Financial article business-state write surface. Each material mutation binds the fetched prior state SHA, exact action/contract/input/output identities, appends an action-bound receipt, writes with the same SHA, then rereads.
- Missing hard capability blocks the affected action; it never authorizes free-form writing or a lower business SOP.
- Semantic review in the ChatGPT path is `CHAT_SELF_REVIEW`; it may force revision/failure but cannot be mislabeled as independent/provider-attested certification.
- `BLOCKED` review work resumes only through `github_chat_lifecycle.resume_blocked_state`, with explicit repair evidence and a fresh review artifact at the exact blocked stage.

GitHub `main` is engineering/rule authority and Financial article-state authority. Chat memory is never task authority.

## 2. Workflow and semantic gates

Use the owner sequence exactly:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`

Do not skip, insert, or free-form complete stages. Advancement/revision/terminalization requires `github_chat_guard`; BLOCKED recovery and system-impact lifecycle require `github_chat_lifecycle`. The production terminal status is `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN` unless separately verified independent evidence exists.

At `EDITORIAL_AUDIT`, **Reader Funnel / Hook Gate**, **Natural Authorial Prose / Writing DNA Gate**, and general editorial audit are distinct judgments. `CHAT_SELF_REVIEW` may identify defects but cannot certify independent execution.

Legacy/internal Python audit labels such as `INDEPENDENT_EXECUTOR` are implementation-test vocabulary only and must not be surfaced as a second production mode.

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

- Research uses the **Universe Coverage Ledger** with `MATERIAL / SECONDARY / REFERENCE_ONLY`; FINANCE_DEEP preserves `company_coverage_obligations` and the company comparison decision map.
- Material market explanation preserves `VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.
- `FINANCE_BROAD` keeps the domain **cold-reader test**; cross-industry appeal is not a universal hard requirement.
- Headline diversity is tracked by `angle_family`. Major H1 sections must also be **earned transitions**.
- Natural prose uses the deterministic template-cluster guard when executable; unavailable deterministic checks remain OPEN.
- Every supplied A-share company/stock name is mechanically bolded at every exact Word occurrence; this does not replace semantic skim anchors.
- Publication articles use no tables; delivery enforces zero underlines when deterministic document tooling is executable.
- Final disclaimer is one inline italic paragraph beginning `风险提示：`; semantic completeness remains required.
- Public output must never become executable buy/sell guidance.

## 5. Learning and maintenance

A material explicit user edit, feedback, rejection or acceptance that changes writing, review, or delivery must become durable owner evidence before claiming learning.

Use `github_chat_guard.attach_material_feedback` to persist material feedback. A GITHUB_CHAT OPEN system-impact item is then classified/closed only through `github_chat_lifecycle.review_system_impact_state`; any closure remains evidence-bound and self-attested at chat assurance and must not be relabeled as independent verification. Internal plugin helpers may be used in tests or future infrastructure, but they are not a second production workflow.

Systemic/non-trivial maintenance follows `references/maintenance.md` and current Universal evolution rules. Do not create another root policy or persona Agent merely to add review theatre.

## 6. Completion / delivery

Before `DELIVERY`, reconcile all article Word outputs required by the immutable task contract. Before terminalization, reconcile the full set including `AUDIT_DOCX`. Persist publication source in GitHub so Word artifacts remain reproducible.

For an active durable task, preserve owner lease/progress rules and emit the Universal progress receipt separately from quality/execution assurance.
