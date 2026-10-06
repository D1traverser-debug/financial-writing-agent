# ChatGPT Site deployment specification

## Goal
Host Financial Writing Agent as a Site-backed MCP plugin so the same runtime is available from ChatGPT at home or work without local installation.

## Runtime invariant
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Invalid transitions or failed mandatory dependencies route to `BLOCKED`; never silently fall back to free-form writing.

## Responsibility split
- ChatGPT/model: connector-side knowledge retrieval/writeback, live web research, synthesis, TopicDNA, structure, titles, drafting, dedicated style judgment, semantic audits, visual planning/generation.
- Hosted MCP runtime: TaskContract, legal transitions, schema validation, durable checkpointing, knowledge/visual receipts, gate status, required outputs, completion authority.
- Deterministic delivery: Word construction, image insertion, formatting/mechanical QA, render checks, audit artifact.

## Durable state
Persist complete serialized `WritingState` per `task_id`, including contract/content mode, stage, gates, structured outputs, artifacts, trace, attempts, blocked reason and timestamps. Save after every material change; support load-by-id and recent-task listing.

Notion/Drive status pages are mirrors/governance layers, not the executable checkpoint authority.

## Artifact storage
The production Site must use persistent object/file storage. Never expose only ephemeral server paths.

Formal `WORD_FILE_ONLY` tasks may require:
- `FINANCE_DEEP.docx`;
- `FINANCE_BROAD.docx`;
- `WRITING_AUDIT_REPORT.docx`;
- `VISUAL_MANIFEST.json` when visuals are enabled.

`WECHAT_STICKER_POST` tasks require:
- `WECHAT_STICKER_POST.docx`;
- `WRITING_AUDIT_REPORT.docx`;
- `VISUAL_MANIFEST.json` when visuals are enabled.

Final tool results must expose ChatGPT-usable file references/downloads, not server-local paths.

## MCP tools
Expose and preserve stage semantics for:
- `start_writing_task`
- `get_writing_task`
- `list_recent_writing_tasks`
- `record_knowledge_context`
- `submit_research`
- `submit_research_audit`
- `submit_editorial_plan`
- `submit_headlines`
- `submit_draft`
- `submit_style_audit`
- `submit_editorial_audit`
- `submit_visual_package`
- `build_and_mechanically_audit_delivery`
- `record_knowledge_writeback`
- `submit_final_audit`

## Connected knowledge boundary
ChatGPT uses actual Notion/Drive/other connected tools, then records references/receipts into MCP state. Hosted runtime does not falsely claim those account connectors. Time-sensitive reused knowledge remains subject to live re-verification.

## Visual workflow
Creative image generation remains ChatGPT/model-side. Runtime records only real submitted asset references, embeds them deterministically, verifies expected image counts and fails closed when visuals are required but assets are absent.

## WeChat sticker-post mode
Explicit 微信贴图 requests use `WECHAT_STICKER_POST`. Current publisher limits/mechanics must be researched at execution time and captured in `PlatformConstraintSnapshot`; remembered limits are not permanent deployment constants.

## Recovery and mirrors
A continuation request first lists/loads recent incomplete runtime tasks. Do not ask for already persisted task details. Mirror material task status to configured Notion/Drive governance layers when those connectors are available, but mirror failure does not corrupt the runtime checkpoint.

## Promotion validation
Do not call production-ready until all are true:
1. tools are discoverable from a fresh ChatGPT conversation;
2. start persists a durable checkpoint;
3. a fresh conversation can recover it;
4. illegal stages are rejected;
5. revision loops return correctly;
6. dedicated style audit gate is enforced;
7. formal and sticker contracts route to correct required outputs;
8. visual submission and Word image insertion work with real assets;
9. Word files are returned as usable files and pass render/mechanical QA;
10. final semantic audit gates COMPLETE and exposes completion checklist;
11. connected knowledge/mirror work either succeeds with receipts or reports precise N/A/failure boundaries;
12. one user-authorized real article E2E includes deliberate interruption/recovery.

## Canonical source
Repository: `D1traverser-debug/financial-writing-agent`
Branch: `main`
Skill: `skills/financial-writing-agent/SKILL.md`
