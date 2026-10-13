---
name: financial-writing-agent
description: Create and continue publishable A-share financial articles through the persisted Financial Writing owner. Use for article creation/resume from links, PDFs, news or research; do not use for standalone stock-picking or post-close review unless the user explicitly asks to turn that work into publishable content.
---

# Financial Writing Agent v0.8

This Skill is the single ChatGPT-facing Financial entry and thin router. Detailed business rules remain in `references/`, `config/policy.json`, the canonical workflow and executable owner guards.

## 1. Enter the one Financial owner path

Normal use has exactly one product/execution path:

`ChatGPT request → current GitHub main Financial owner → main/workspaces/articles/{task_id} durable state → canonical workflow → Word delivery`.

Do not ask the user to choose an execution mode. Do not choose between owner-native, GitHub-chat, Python or any other alternate business route. Model, web, deterministic/Python and document facilities are capabilities inside the same owner trajectory when actually available; they never create a second article-state authority.

Before material work read `continuity/FINANCIAL_OWNER_EXECUTION.json` and `continuity/EXECUTION_CAPABILITIES.json`, then handshake only capabilities required by the exact next action. Repository declarations are ceilings, not current-session proof.

- Durable article business state lives only at `main/workspaces/articles/{task_id}`.
- Create durable article state before research or drafting. Chat memory is never task authority.
- Every material transition uses `financial_writing_agent/owner_guard.py` against freshly fetched main state, binds the prior state blob SHA, writes with compare-and-swap, then rereads authoritative state and new artifact refs.
- Review FAIL/BLOCKED recovery and system-impact lifecycle use `financial_writing_agent/owner_lifecycle.py` against that same owner state; they do not create another state machine.
- Existing schema-1.2 `execution_mode=GITHUB_CHAT` and old receipt labels are compatibility data only, not route selectors.
- Missing hard capability blocks the affected stage. It never authorizes free-form writing or a lower business SOP.
- New per-article business-state branches are forbidden. Historical branches/evals are evidence only and never current authority.
- Legacy owner-native/SQLite/plugin task state is not a fallback for new or resumed Financial business work.

The canonical TaskContract defaults to `DUAL` unless the user explicitly narrows it. Default formal delivery therefore requires `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX` through `WORD_FILE_ONLY`. A single-mode override requires exact user-prompt evidence in the INIT receipt.

## 2. Workflow and semantic gates

Use the owner sequence exactly:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`.

Do not skip, insert, or free-form complete stages. Stage advancement, revision, blocked recovery, feedback mutation and terminalization require deterministic owner-state validation.

At `EDITORIAL_AUDIT`, **Reader Funnel / Hook Gate**, **Natural Authorial Prose / Writing DNA Gate**, and general editorial audit are distinct judgments. In a single GPT chat, semantic review assurance remains `CHAT_SELF_REVIEW`; it may identify PASS/REVISE/FAIL for routing, but it must not be relabeled as provider-attested independent review. If genuinely stronger provider-attested review becomes available, it is an additional capability inside the same owner state trajectory, not a new execution path.

Current bounded terminal status remains `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN` unless stronger exact-action evidence actually exists.

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

Material user edit/feedback/rejection/acceptance that changes writing, review or delivery must become durable owner evidence before claiming learning.

Persist corrective evidence in the same main article workspace and keep systemic impact OPEN until the maintenance/evolution lifecycle has evidence-backed closure. Do not fabricate runtime receipts that were not actually produced.

Systemic/non-trivial maintenance follows `references/maintenance.md` and current Universal evolution rules. Prefer consolidation/deletion over adding another execution adapter, state store or persona Agent. A superseded mechanism may remain in Git history or historical evals, but it must be removed or mechanically quarantined from current authority and hot-path routing.

## 6. Completion / delivery

Before `DELIVERY`, reconcile all article Word outputs required by the immutable task contract. Before terminalization, reconcile the full set including `AUDIT_DOCX`. Persist publication source in GitHub so Word artifacts remain reproducible.

For an active durable task, preserve Universal lease/progress rules and emit the Universal progress receipt separately from quality/execution assurance. `COMMITTED` is valid only after authoritative reread.
