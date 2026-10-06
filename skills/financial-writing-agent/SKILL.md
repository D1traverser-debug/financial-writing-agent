---
name: financial-writing-agent
description: Deterministic A-share financial writing workflow. Use whenever the user asks to write, rewrite, continue, audit, retitle, or produce a formal financial article from links, PDFs, news, research reports, or prior drafts. The runtime must initialize before any research or drafting; never silently fall back to free-form writing.
---

# Financial Writing Agent

## Runtime first

Before any source retrieval, web research, outlining, drafting, rewriting, title work, or delivery, call the Financial Writing Agent MCP runtime.

For a new task, call `start_writing_task`. For a continuation request, call `list_recent_writing_tasks` and then `get_writing_task` before asking the user to repeat prior context.

The runtime owns this stage order:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Never skip a stage or silently continue as ordinary free-form chat when the runtime is unavailable, blocked, or asks for revision.

## Responsibility split

- The ChatGPT model owns high-judgment work: source research, evidence synthesis, TopicDNA, structure, headline generation, drafting, and semantic red-team review.
- The MCP runtime owns legal state transitions, Pydantic validation, SQLite checkpoints, required outputs, hard gates, Word generation, mechanical/render QA, and final completion authority.
- A stage result is not accepted until it is submitted through the tool corresponding to the runtime's current stage.

## Tool choreography

Follow the `current_stage` and `next_action` returned by the runtime.

- `RESEARCH`: research broadly, build the complete `ResearchPackage`, then call `submit_research`.
- `RESEARCH_AUDIT`: independently audit evidence completeness and causal support, then call `submit_research_audit`.
- `EDITORIAL`: build TopicDNA and multiple topic-specific structures, then call `submit_editorial_plan`.
- `TITLE`: generate and judge multiple headline candidates, then call `submit_headlines`.
- `DRAFT`: create the applicable structured article payload(s), then call `submit_draft`.
- `EDITORIAL_AUDIT`: independently audit the frozen draft, then call `submit_editorial_audit`.
- `DELIVERY` or `MECHANICAL_AUDIT`: call `build_and_mechanically_audit_delivery`.
- `FINAL_AUDIT`: perform the final semantic red-team, then call `submit_final_audit`.
- `COMPLETE`: only then announce completion and deliver the recorded artifacts.

When a gate returns `REVISE`, obey the returned stage and revise there. When the runtime is `BLOCKED`, report the concrete blocker instead of bypassing it.

## Default contract

Unless the user explicitly overrides it for the current task:

- `delivery_channel = WORD_FILE_ONLY`;
- do not paste full article drafts or previews into chat;
- when targets span finance communities and broad feeds, use `DUAL`;
- `DUAL` means one complete research base plus two independently edited financial articles: `FINANCE_DEEP` and `FINANCE_BROAD`;
- Word completion requires the applicable article Word file(s) and `WRITING_AUDIT_REPORT.docx`.

## Research and editorial standard

Research broadly inside the current topic before choosing what the article emphasizes. Preserve facts and numbers that change the conclusion, chronology, the causal/transmission chain, counterevidence, unresolved gaps, company competition, `why_this / why_not`, market-selection logic, and validation/falsification conditions.

Do not use a fixed word-count target. Compress repetition, generic background, and low-value enumeration before cutting reasoning.

Build TopicDNA and several current-topic structure candidates before using historical structure fingerprints as collision checks. Do not rotate templates mechanically.

Treat the headline as a high-judgment hook stage. Generate multiple candidates and judge finance relevance, the primary contradiction, factual support, information gap, and cognitive load. `FINANCE_BROAD` must translate a sector-specific event into a finance-wide question without diluting analytical depth.

## Audit standard

Writer and semantic auditor must remain separate roles. Mechanical QA does not replace semantic review, and semantic review does not replace mechanical QA.

A run may reach `COMPLETE` only after all applicable gates pass, all required artifacts exist, Word mechanical/render checks pass, and final semantic red-team passes. Do not claim completion before the MCP runtime returns `COMPLETE`.

## Recovery

The MCP SQLite store is the executable checkpoint authority for writing tasks. In a fresh conversation, recover unfinished work with `list_recent_writing_tasks` and `get_writing_task`. External Notion/Drive pointers may mirror status for governance, but they do not override the runtime checkpoint.
