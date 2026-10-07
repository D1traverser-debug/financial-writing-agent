# ChatGPT Site deployment specification

## Goal
Host Financial Writing Agent as a Site-backed MCP plugin so the same private runtime is available from the user's ChatGPT sessions at home or work without local installation.

## v0.2.1 deployment boundary
v0.2.1 is **personal/private deployment only**. Do not enable public sharing, workspace-wide sharing, or multi-user use until the runtime has explicit per-user tenant isolation, authorization, state namespaces, artifact namespaces, and cross-user access tests.

This is a security boundary, not a product preference. The current reference store is task-keyed, not tenant-keyed.

**Real article live-model E2E passed is currently 0.** Unit, fixture, CI, mock-content and local diagnostic runs do not satisfy production promotion.

## Runtime invariant
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Invalid transitions or failed mandatory dependencies route to `BLOCKED`; never silently fall back to free-form writing. COMPLETE additionally requires the full mandatory-gate inventory to exist, not merely the absence of FAIL among whatever gates happen to be present.

## Responsibility split
- ChatGPT/model: optional connected-knowledge reuse/writeback when available, live public research, synthesis, TopicDNA, mode-specific structures, titles, drafting, dedicated style judgment, semantic audits, visual planning/generation, and visual inspection of returned render pages.
- Hosted MCP runtime/harness: TaskContract, legal transitions, strict schemas, evidence receipts, durable checkpointing, revision invalidation, frozen WritingAcceptanceContract, mandatory gate inventory, knowledge/visual receipts, required outputs, artifact readback/checksum and completion authority.
- Deterministic delivery: Word construction, image insertion, formatting/mechanical QA, DOCX rendering and audit-artifact construction.

No external connector is a hard dependency of the core Writing Agent. If durable external knowledge is unavailable, research proceeds from current task sources/public research and knowledge writeback is explicitly recorded `N_A` with a reason.

## Durable state
Persist complete serialized `WritingState` per `task_id`, including contract/content mode, stage, gates, acceptance contract, structured outputs, artifacts, render manifest, revision history, trace, attempts, blocked reason and timestamps. Save atomically after every material change; support load-by-id and recent-task listing.

The repository's `SQLiteStateStore` is the local/CI reference implementation only. A Site deployment must bind the runtime to a Site-supported durable structured store or another verified durable backend. **Do not silently fall back to ephemeral container/local disk for production checkpoints.** If durable persistence is unavailable, deployment is not ready.

Recovery validation must cover both process restart and fresh ChatGPT conversation. A task that survives only within one warm process is not durable.

Notion/Drive status pages are optional mirrors/governance layers, not executable checkpoint authority.

## Artifact and render storage
Production artifacts and rendered-page images must live in persistent file/object storage or another backend whose lifetime survives fresh chats and runtime restarts. Never make a server-local path the public artifact contract.

Formal `WORD_FILE_ONLY` tasks may require:
- `FINANCE_DEEP.docx`;
- `FINANCE_BROAD.docx`;
- `WRITING_AUDIT_REPORT.docx`;
- `VISUAL_MANIFEST.json` when visuals are enabled.

`WECHAT_STICKER_POST` tasks require:
- `WECHAT_STICKER_POST.docx`;
- `WRITING_AUDIT_REPORT.docx`;
- `VISUAL_MANIFEST.json` when visuals are enabled.

The public MCP surface exposes typed artifact metadata and MCP resource links/templates. It also exposes rendered Word pages through `writing-render://{task_id}/{kind}/{page}` so the final auditor can inspect actual page appearance.

A production Site must prove artifact and render resources remain readable from a fresh ChatGPT conversation and after runtime restart. Local `/data/...` paths are internal implementation details and must never be presented as user deliverables or embedded into the public audit report.

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

Required resource templates include publication artifact resources and `writing-render://{task_id}/{kind}/{page}` for page-level QA.

## Research/evidence boundary
Connected prior knowledge is a recall source, not a verdict. Time-sensitive reused facts remain subject to current re-verification.

Research evidence explicitly distinguishes unresolved claims, single authoritative source attribution and independent cross-checks. Core-safe facts may not remain unresolved. Source independence must reflect distinct original-source groups, not duplicate tools/rewrites of one source.

Writing keeps StockBase read-only. Stable corrections discovered during writing go to the run ReviewQueue rather than directly mutating StockBase.

## DUAL and acceptance contract
DUAL shares one research/evidence base but `FINANCE_DEEP` and `FINANCE_BROAD` independently generate/select their editorial structures. One outline with two emphasis labels is not sufficient.

After mode-specific structures and selected titles are frozen, the runtime creates a `WritingAcceptanceContract` before DRAFT. Formal drafts must preserve the frozen title and exact H1 sequence unless the workflow legally revises to the earlier stage and rebuilds the contract.

Final acceptance evidence uses machine-checked `KEY: concrete evidence` entries for every applicable criterion. DUAL additionally requires explicit cross-version consistency evidence. A generic “checked/pass” string cannot satisfy completion.

## Mechanical and visual QA
Creative image generation remains ChatGPT/model-side. `submit_visual_package` accepts authorized ChatGPT file parameters, not arbitrary server paths. Runtime copies only validated image inputs into task storage, embeds them deterministically, verifies expected image counts and fails closed when visuals are required but assets are absent.

Production hosting must restrict egress/file retrieval to authorized file-param traffic and reject non-HTTPS, private-network, loopback, link-local or otherwise unsafe targets, including unsafe redirect destinations.

Mechanical Word QA must validate machine-checkable publication requirements such as H1 sequence/style/color/size, H2/H3 style/sequence, stock-name bold spans across Word runs, Markdown leakage, underlines, abnormal empty paragraphs, risk section, red-line phrases and image count.

Successful DOCX-to-PNG conversion is not visual-page PASS. When render is required, every returned render-page resource must be inspected and the final decision must list exactly those inspected resource URIs. Missing or invented render receipts prevent PASS.

## Agents SDK diagnostic path
The optional standalone Agents SDK path is a developer diagnostic path, not a replacement for the production MCP/ChatGPT visual workflow. It may disable visual generation and page-image inspection explicitly rather than pretending those model-side capabilities exist locally.

High-judgment SDK runs should use task-grouped traces (`workflow_name`, `group_id=task_id`, stage metadata) and avoid tracing sensitive prompt/output content by default. CI should include deterministic `ScriptedModel` workflow testing in addition to structural import smoke.

## WeChat sticker-post mode
Explicit 微信贴图 requests use `WECHAT_STICKER_POST`. Current publisher limits/mechanics must be researched at execution time and captured in `PlatformConstraintSnapshot`; remembered limits are not permanent deployment constants. A stale snapshot must be reverified rather than reused.

## Recovery and mirrors
A continuation request first lists/loads recent incomplete runtime tasks. Do not ask for already persisted task details. A revision or recovery must preserve already-valid upstream work but must not preserve downstream PASS state invalidated by the changed content.

Optional Notion/Drive mirrors may be updated after material transitions/completion, but mirror failure does not corrupt or downgrade a valid Runtime checkpoint.

## Plugin mapping
Before the Site endpoint exists, do not invent or hard-code an MCP URL. After the private Site publishes a stable MCP endpoint, create/update the Site-managed MCP mapping (and portable `mcp.json` if the chosen packaging path requires it) from that real endpoint, then republish/reinstall as required by ChatGPT.

## Promotion validation
Do not call the deployment production-ready until all are true:
1. the Skill activates for intended writing requests and does not activate for standalone stock-picking/review requests;
2. all 15 typed tools and required artifact/render resource templates are discoverable from a fresh ChatGPT conversation with correct contracts;
3. start persists a durable checkpoint outside ephemeral process state;
4. a fresh conversation can recover the same unfinished task without user repetition;
5. runtime restart preserves the same checkpoint;
6. illegal stages, unknown schema fields and absent mandatory gates are rejected immediately;
7. revision loops return to the earliest correct legal stage and stale downstream PASS/artifacts are invalidated;
8. evidence verification/source-group rules and the dedicated style audit gate are enforced;
9. DUAL uses independent mode-specific structures and a frozen acceptance contract before drafting;
10. formal DUAL and sticker contracts route to correct required outputs;
11. visual submission accepts real authorized image files, rejects unsafe/invalid/redirect targets, and Word image insertion works with real assets;
12. Word/artifact resources are readable through MCP from a fresh chat and after restart, with no local path exposed;
13. deterministic mechanical QA passes on the returned Word artifacts;
14. every rendered Word page is readable and actually inspected before final PASS;
15. final semantic audit provides the full criterion-level evidence inventory, required render-page receipts and DUAL cross-version consistency where applicable;
16. final artifact identity is re-read and checksum-verified before COMPLETE;
17. `WRITING_AUDIT_REPORT.docx` contains acceptance/evidence/render/artifact identity results without server-local paths;
18. optional connected knowledge/mirrors either succeed with real receipts or report precise `N_A`/failure boundaries without blocking core writing;
19. one user-authorized real article live-model E2E deliberately interrupts mid-run and successfully resumes without repeating passed stages;
20. the same E2E returns/downloads the actual final Word file(s) and audit report and verifies them after recovery;
21. public/multi-user sharing remains disabled for v0.2.1.

## Canonical source
Repository: `D1traverser-debug/financial-writing-agent`
Stable branch: `main`
Hardening branch until promotion: `v0.2.1-runtime-rule-hardening`
Skill: `skills/financial-writing-agent/SKILL.md`
