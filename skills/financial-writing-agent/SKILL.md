---
name: financial-writing-agent
description: Create and continue publishable A-share financial articles through the persisted Financial Writing owner. Use for article creation/resume from links, PDFs, news or research; do not use for standalone stock-picking or post-close review unless the user explicitly asks to turn that work into publishable content.
---

# Financial Writing Agent v0.8

This Skill is a thin router. Runtime/workflow/guards are executable authority; detailed domain rules live in `references/` and `config/policy.json`.

## 1. Enter or resume through an explicit owner execution mode

Before material execution read `continuity/EXECUTION_CAPABILITIES.json` and handshake only the capabilities needed by the exact next action. Repository declarations are ceilings, not current-session proof.

- If the Python owner runtime/plugin is actually available, use the persisted owner runtime: existing work via `list_recent_writing_tasks`; new article via `start_writing_task` before research or drafting.
- If owner-native runtime is unavailable, GITHUB_CHAT is legal only when this session has GPT/model execution, GitHub owner read/write **and** a deterministic way to execute `financial_writing_agent/github_chat_guard.py`. Create/resume state through that guard; do not hand-edit `current_stage`.
- Every GITHUB_CHAT material transition must bind the fetched prior `STATE.json` blob SHA, the exact task/stage/capability/action, executor identity, subject/input bindings and output refs in one new self-attested execution receipt. Resolve the durable state ref first (`main` or `article/{task_id}` per `continuity/GITHUB_CHAT_EXECUTION.json`), then write and reread on that same ref; a branch-backed final receipt must identify `state_ref`.
- If the deterministic guard cannot execute, block the stage transition. Missing owner runtime is never permission to free-form a publishable article.
- In GitHub-chat mode, semantic audits are `CHAT_SELF_REVIEW`: they may detect defects and force revision/failure but never become owner-native `PASS`, `INDEPENDENT_EXECUTOR`, or provider-attested evidence. Normal terminal state is `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`.
- `BLOCKED` owner-runtime work resumes only from its persisted recovery cursor through `resume_blocked_task`; never reconstruct execution stage from chat memory.

GitHub `main` is engineering/rule authority. Owner-native `WritingState` is execution truth for Python/plugin runs; guard-validated GitHub article checkpoints are execution truth for explicit GITHUB_CHAT runs. Chat memory is never task authority.

## 2. Workflow and semantic gates

Use the owner sequence exactly:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`.

Owner-native runs may then reach `COMPLETE` only through the controller. GitHub-chat runs may deliver at their bounded chat assurance but may not relabel that result as owner-native COMPLETE.

Do not free-form skip, insert or complete stages. In GITHUB_CHAT, stage advancement/revision/terminalization is accepted only by `github_chat_guard`; a fluent model answer or manually edited `STATE.json` is not workflow proof.

At `EDITORIAL_AUDIT`, **Reader Funnel / Hook Gate**, **Natural Authorial Prose / Writing DNA Gate**, and general editorial audit are distinct required judgments.

For owner-native execution, semantic PASS is proof-bearing. `CHAT_SELF_REVIEW` / `CHAT_BRIDGED` may find defects or request revision but may not certify Research Audit, Reader Funnel, Authorial Prose, General Editorial or Final Audit as owner-runtime PASS. Hosted/MCP PASS certification goes through `run_semantic_audit_stage`; if its required runtime is unavailable, keep that certification OPEN rather than self-certifying.

The legacy `INDEPENDENT_EXECUTOR` token means stage-separated owner-runtime execution only; it is not provider-attested isolation.

## 3. Progressive reference map

Load only what the current stage needs:

- RESEARCH → `references/research.md` + `references/knowledge.md`; use `references/market_explanation.md` only when deciding or applying material market-explanation scope.
- RESEARCH_AUDIT / FINAL_AUDIT → `references/audit.md` (+ market explanation reference only when applicable).
- EDITORIAL / TITLE / DRAFT → `references/editorial.md` + `references/hooks.md` + `references/style.md`.
- Platform adaptation → `references/platforms.md`.
- Word/delivery/mechanical QA → `references/delivery.md`.
- Durable system/rule changes → `references/maintenance.md`.

`references/*` are canonical domain semantics. Do not copy their full rules back into this Skill.

## 4. Hard-boundary contract anchors

These anchors stay hot because crossing them changes product behavior:

- Research breadth uses the **Universe Coverage Ledger** with `MATERIAL / SECONDARY / REFERENCE_ONLY`; Deep preserves `company_coverage_obligations` and a company comparison decision map.
- When market explanation is material, preserve `VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.
- `FINANCE_BROAD` keeps the domain **cold-reader test**; cross-industry finance appeal is **not a universal hard requirement**.
- Headline diversity is tracked by `angle_family` rather than synonym-only shells.
- Major H1 sections must also be **earned transitions**.
- Natural prose uses the deterministic **template-cluster guard** before semantic judgment when that guard is executable; GitHub-chat self-review must still apply the same pattern semantics and mark unavailable deterministic checks OPEN.
- Do not automatically bold every company/stock-name occurrence.
- Publication articles do not use tables; delivery enforces **zero underlines** when the deterministic document path is executable.
- Final disclaimer remains one inline italic paragraph beginning `风险提示：`.
- Public output must never become executable buy/sell guidance. A disclaimer does not cure actionable instructions.

## 5. Learning and maintenance

Any **material explicit user edit, feedback, rejection or acceptance that changes how the system should write, review or deliver** must become durable owner evidence before claiming learning or closing that revision loop.

- Owner-native mode: use `record_writing_learning_sample` and its system-impact path.
- GITHUB_CHAT mode: use `github_chat_guard.attach_material_feedback` so material edit/feedback/rejection and its OPEN system-impact item enter the same guard-validated state mutation and action-bound receipt. Do not fabricate owner-plugin receipts when that runtime is unavailable.

Systemic/non-trivial maintenance enters `references/maintenance.md` and the current Universal `operational_hygiene` / `evolution` path. Local deterministic bugs may use the lighter path defined there. Do not create another root policy or persona Agent merely to add review theatre.

## 6. Completion / delivery

Owner-native `COMPLETE` remains controlled by the owner workflow/controller and requires its proof-bearing gates and artifacts.

GITHUB_CHAT may deliver a Word artifact only after the full guard-enforced GitHub workflow, current-session mechanical checks, and final self-review complete. Report its bounded state as `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN` and list unavailable independent/owner-native checks as OPEN. Persist the publication source in GitHub so the Word file is reproducible even if the chat attachment is transient.

For an active durable task, preserve owner lease/progress rules and emit the Universal progress receipt separately from quality/execution assurance.
