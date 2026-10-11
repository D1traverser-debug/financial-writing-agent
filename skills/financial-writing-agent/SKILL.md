---
name: financial-writing-agent
description: Create and continue publishable A-share financial articles through the persisted Financial Writing runtime. Use for article creation/resume from links, PDFs, news or research; do not use for standalone stock-picking or post-close review unless the user explicitly asks to turn that work into publishable content.
---

# Financial Writing Agent v0.8

This Skill is a thin router. Runtime/workflow/guards are executable authority; detailed domain rules live in `references/` and `config/policy.json`.

## 1. Enter or resume through the owner runtime

- Existing/unfinished work: call `list_recent_writing_tasks`, select the persisted task, then load it. Never reconstruct stage from chat memory.
- `BLOCKED`: inspect the persisted blocker/recovery cursor and use `resume_blocked_task` only after the dependency/contract defect is repaired.
- New publishable article: call `start_writing_task` before research, outlining or drafting.
- GitHub `main` is engineering/rule authority; persisted `WritingState` is article execution truth. External stores are inputs/mirrors unless explicitly promoted by the owner contract.

Before material execution read `continuity/EXECUTION_CAPABILITIES.json` and perform the current-session capability handshake only for the exact next action. A declaration is a ceiling, not session proof.

## 2. Workflow and semantic gates

Use the owner state machine exactly:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`.

Do not free-form skip, insert or complete stages.

At `EDITORIAL_AUDIT`, **Reader Funnel / Hook Gate**, **Natural Authorial Prose / Writing DNA Gate**, and general editorial audit are distinct required judgments.

Semantic PASS is proof-bearing. `CHAT_SELF_REVIEW` / `CHAT_BRIDGED` may find defects or request revision but may not certify Research Audit, Reader Funnel, Authorial Prose, General Editorial or Final Audit as PASS. Hosted/MCP PASS certification goes through `run_semantic_audit_stage`; if the required owner-native SDK/model runtime is unavailable, the exact audit stage stays recoverably BLOCKED.

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

These anchors stay hot because crossing them would change product behavior; their detailed logic still belongs in references/policy/runtime:

- Research breadth is governed by the **Universe Coverage Ledger** with `MATERIAL / SECONDARY / REFERENCE_ONLY`; Deep preserves `company_coverage_obligations` and a company comparison decision map.
- When market explanation is material, preserve `VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.
- `FINANCE_BROAD` keeps the domain **cold-reader test**; cross-industry finance appeal is **not a universal hard requirement**.
- Headline diversity is tracked by `angle_family` rather than synonym-only shells.
- Major H1 sections must also be **earned transitions**; detailed structure semantics live in `references/editorial.md`.
- Natural prose uses the deterministic **template-cluster guard** before semantic judgment.
- Do not automatically bold every company/stock-name occurrence.
- Publication articles do not use tables; deterministic delivery enforces **zero underlines**.
- Final disclaimer remains one inline italic paragraph beginning `风险提示：`.
- Public output must never become executable buy/sell guidance. A disclaimer does not cure actionable instructions.

## 5. Learning and maintenance

Any **material explicit user edit, feedback, rejection or acceptance that changes how the system should write, review or deliver** must be captured through `record_writing_learning_sample` (or equivalent durable owner evidence) before claiming durable learning or closing that learning loop. If the learning-evidence executor is unavailable, obey the current revision but state that **durable learning was not persisted**.

Systemic/non-trivial maintenance enters `references/maintenance.md` and the current Universal `operational_hygiene` / `evolution` meta-maintenance path. Local deterministic bugs may use the lighter path defined there. Do not create another root policy or persona Agent merely to add review theatre.

## 6. Completion

Only the owner workflow/controller may advance stages or COMPLETE. Required artifacts, semantic gates, mechanical QA, exact file identity and applicable methodology/action receipts must be satisfied at their real assurance level.

For an active durable task, preserve owner lease/progress rules and emit the Universal progress receipt separately from quality/execution assurance.
