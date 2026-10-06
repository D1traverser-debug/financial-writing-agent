# ChatGPT Site deployment specification

## Goal
Host Financial Writing Agent as a Site-backed MCP plugin so the same private runtime is available from the user's ChatGPT sessions at home or work without local installation.

## v0.2 deployment boundary
v0.2 is **personal/private deployment only**. Do not enable public sharing, workspace-wide sharing, or multi-user use until the runtime has explicit per-user tenant isolation, authorization, state namespaces, artifact namespaces, and cross-user access tests.

This is a security boundary, not a product preference. The current reference store is task-keyed, not tenant-keyed.

## Runtime invariant
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Invalid transitions or failed mandatory dependencies route to `BLOCKED`; never silently fall back to free-form writing.

## Responsibility split
- ChatGPT/model: optional connected-knowledge reuse/writeback when available, live public research, synthesis, TopicDNA, structure, titles, drafting, dedicated style judgment, semantic audits, visual planning/generation.
- Hosted MCP runtime: TaskContract, legal transitions, schema validation, durable checkpointing, knowledge/visual receipts, gate status, required outputs, completion authority.
- Deterministic delivery: Word construction, image insertion, formatting/mechanical QA, render checks, audit artifact.

No external connector is a hard dependency of the Writing Agent. If durable external knowledge is unavailable, research proceeds from current task sources/public research and knowledge writeback is explicitly recorded `N_A` with a reason.

## Durable state
Persist complete serialized `WritingState` per `task_id`, including contract/content mode, stage, gates, structured outputs, artifacts, trace, attempts, blocked reason and timestamps. Save atomically after every material change; support load-by-id and recent-task listing.

The repository's `SQLiteStateStore` is the local/CI reference implementation only. A Site deployment must bind the runtime to a Site-supported durable structured store or another verified durable backend. **Do not silently fall back to ephemeral container/local disk for production checkpoints.** If durable persistence is unavailable, deployment is not ready.

Notion/Drive status pages are optional mirrors/governance layers, not executable checkpoint authority.

## Artifact storage and return
Production artifacts must live in persistent file/object storage or another backend whose lifetime survives fresh chats and runtime restarts. Never make a server-local path the public artifact contract.

Formal `WORD_FILE_ONLY` tasks may require:
- `FINANCE_DEEP.docx`;
- `FINANCE_BROAD.docx`;
- `WRITING_AUDIT_REPORT.docx`;
- `VISUAL_MANIFEST.json` when visuals are enabled.

`WECHAT_STICKER_POST` tasks require:
- `WECHAT_STICKER_POST.docx`;
- `WRITING_AUDIT_REPORT.docx`;
- `VISUAL_MANIFEST.json` when visuals are enabled.

The public MCP surface exposes typed artifact metadata plus MCP resource links/templates. A production Site must prove those resources remain readable from a fresh ChatGPT conversation and after a runtime restart. Local `/data/...` paths are internal implementation details and must never be presented as user deliverables.

## MCP surface
There is exactly one public MCP registration surface: `financial_writing_agent/plugin_server.py`. `runtime_service.py` contains business/runtime operations only. `mcp_server.py` is a thin compatibility shim and must not register a second tool set.

Expose exactly these 15 tools:
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

Every public tool must have a concrete input contract, concrete structured output schema, accurate read/write/destructive/open-world annotations, a human-readable title, and an operational description. Unknown stage-payload fields fail closed.

## Connected knowledge boundary
When useful connected knowledge is available in the current ChatGPT environment, ChatGPT may retrieve it and record real references with `record_knowledge_context`. The runtime does not impersonate Notion/Drive/other account connectors and does not require them to succeed. Time-sensitive reused knowledge remains subject to live re-verification.

Reusable writeback is similarly optional enrichment: actual successful writes receive `PASS` receipts; no writable target or no reusable item is an explicit `N_A`, not a task failure.

## Visual workflow
Creative image generation remains ChatGPT/model-side. `submit_visual_package` accepts authorized ChatGPT file parameters, not arbitrary server paths. Runtime copies only validated image inputs into task storage, embeds them deterministically, verifies expected image counts and fails closed when visuals are required but assets are absent.

Production hosting should restrict egress/file retrieval to authorized file-param traffic and reject non-HTTPS, private-network, loopback, link-local, or otherwise unsafe download targets.

## WeChat sticker-post mode
Explicit 微信贴图 requests use `WECHAT_STICKER_POST`. Current publisher limits/mechanics must be researched at execution time and captured in `PlatformConstraintSnapshot`; remembered limits are not permanent deployment constants. A stale snapshot must be reverified rather than reused.

## Recovery and mirrors
A continuation request first lists/loads recent incomplete runtime tasks. Do not ask for already persisted task details. Optional Notion/Drive mirrors may be updated after material transitions/completion, but mirror failure does not corrupt or downgrade a valid Runtime checkpoint.

## Plugin mapping
Before the Site endpoint exists, do not invent or hard-code an MCP URL. After the private Site publishes a stable MCP endpoint, create/update the Site-managed MCP mapping (and portable `mcp.json` if the chosen packaging path requires it) from that real endpoint, then republish/reinstall as required by ChatGPT.

## Promotion validation
Do not call the deployment production-ready until all are true:
1. the Skill activates for intended writing requests and does not activate for standalone stock-picking/review requests;
2. all 15 typed tools are discoverable from a fresh ChatGPT conversation with correct annotations/output schemas;
3. start persists a durable checkpoint outside ephemeral process state;
4. a fresh conversation can recover the same unfinished task without user repetition;
5. runtime restart preserves the same checkpoint;
6. illegal stages and unknown schema fields are rejected immediately;
7. revision loops return to the correct legal stage;
8. dedicated style audit gate is enforced;
9. formal DUAL and sticker contracts route to correct required outputs;
10. visual submission accepts real authorized image files, rejects unsafe/invalid inputs, and Word image insertion works with real assets;
11. Word/artifact resources are readable through MCP from a fresh chat and after restart, with no local path exposed;
12. mechanical/render QA passes on the returned Word artifacts;
13. final semantic audit gates COMPLETE and exposes the visible completion checklist;
14. optional connected knowledge/mirrors either succeed with real receipts or report precise `N_A`/failure boundaries without blocking core writing;
15. one user-authorized real article E2E includes deliberate interruption/recovery;
16. public/multi-user sharing remains disabled for v0.2.

## Canonical source
Repository: `D1traverser-debug/financial-writing-agent`
Branch: `main` after the pre-deployment hardening PR is merged and `main` CI is green.
Skill: `skills/financial-writing-agent/SKILL.md`
