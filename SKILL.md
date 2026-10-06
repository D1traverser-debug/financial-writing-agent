---
name: financial-writing-agent
description: Deterministic A-share financial writing workflow. Use whenever the user asks to write, rewrite, continue, audit, retitle, or produce a formal financial article from links, PDFs, news, research reports, or prior drafts. The runtime must initialize before any research or drafting; never silently fall back to free-form writing.
---

# Financial Writing Agent

## Runtime first

Do not begin web research, source extraction, outlining, drafting, or delivery until the Financial Writing Runtime has initialized a TaskContract and checkpoint.

The executable runtime owns stage order:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

If the runtime or a required stage executor is unavailable, stop at `BLOCKED`. Do not continue as ordinary free-form chat.

## Responsibility split

- Code owns routing, stage transitions, checkpoint/resume, required outputs and hard gates.
- High-judgment model stages own research synthesis, TopicDNA, structure, headline generation, drafting and semantic review.
- Deterministic scripts own Word generation, document-format checks, required artifact checks and visible audit packaging.
- References are loaded progressively by the stage that needs them.

## Cross-conversation handoff

SQLite is the per-run execution checkpoint. It is not, by itself, the ChatGPT cross-conversation recovery layer.

For writing tasks, the chat-level recovery pointer is Notion `CURRENT_RUN｜当前写作断点与交付门禁` → `ACTIVE_TASK_POINTER`. The global Drive `CURRENT_STATE` keeps only the compact WRITING-domain summary.

At task start, after every material stage transition, on pause/block, and on completion:
- sync `task_id`, `status`, `current_stage`, `completed_steps`, `pending_steps`, `blockers`, `artifacts`, `distribution_mode`, `delivery_channel`, `next_exact_action`, and `updated_at` to `ACTIVE_TASK_POINTER`;
- keep the Drive `CURRENT_STATE` WRITING line aligned with the active writing-system state without overwriting unrelated business domains;
- read back the persisted pointer before claiming that the task is recoverable from a fresh conversation.

If the pointer cannot be persisted or read back, do not claim cross-conversation recovery is ready. Record the persistence failure explicitly and keep the task in a non-complete state.

When a fresh conversation receives “继续/接着来/继续昨天那篇”, recover the writing pointer first, then load the matching runtime checkpoint/task state. Do not ask the user to restate information already present in the persisted pointer.

## Default contract

Unless the current user request explicitly says otherwise:
- `delivery_channel = WORD_FILE_ONLY`
- do not paste article body, draft or preview into chat;
- when the destinations span finance communities and broad feeds, use `DUAL`;
- `DUAL` means one complete research base plus two independently edited financial articles: `FINANCE_DEEP` and `FINANCE_BROAD`;
- completion requires the applicable article Word file(s) plus `WRITING_AUDIT_REPORT.docx`.

## Progressive references

Load only the reference owned by the active stage:
- Research and research audit: `references/research.md` and `references/audit.md`
- TopicDNA, structure, hooks and drafting: `references/editorial.md`; structure selection may additionally use `references/structure_patterns.md`
- Platform adaptation when relevant: `references/platforms.md`
- Word/output work: `references/delivery.md`
- Semantic/mechanical/final audit: `references/audit.md`
- Durable system changes: `references/maintenance.md`

## Editorial principles

Research broadly inside the current topic, then write selectively. Preserve the causal chain, important facts and numbers, counterevidence, company competition, why-this/why-not, market-selection mechanism, and validation/falsification conditions. Compress repetition, generic background and low-value lists before cutting reasoning.

Do not use a fixed article-length target.

Build TopicDNA and multiple candidate structures before reading recent outline fingerprints. Fingerprints are collision checks, not generation templates. Structure patterns may be used as design patterns after TopicDNA, never as a rotation schedule.

Treat the headline as a high-judgment hook. Generate multiple candidates and judge finance relevance, primary contradiction, factual anchor, information gap and cognitive load. For broad-feed financial writing, frame the sector-specific event as a finance-wide question that can interest finance readers outside that sector without diluting the analysis.

## Audit

Writer and semantic auditor are separate stages. Mechanical checks do not substitute for semantic review, and semantic review does not substitute for mechanical checks.

A run may reach `COMPLETE` only when every applicable gate has evidence and all required artifacts exist. The visible audit report must record gate status, evidence, remaining boundaries and artifact identity.

## Canonical implementation

Repository: `D1traverser-debug/financial-writing-agent`
Canonical branch: `main`

The old Drive/Notion writing rule stack remains migration reference only until a real article regression validates this runtime. Do not delete legacy material during validation unless explicitly authorized.
