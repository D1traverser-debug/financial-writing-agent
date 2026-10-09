# ChatGPT Site deployment specification

## Goal
Host Financial Writing Agent as a Site-backed MCP plugin so the same private runtime is available from the user's ChatGPT sessions without local installation.

## v0.3 deployment boundary
v0.3 is **personal/private deployment only**. Do not enable public sharing, workspace-wide sharing, or multi-user use until the runtime has explicit per-user tenant isolation, authorization, state namespaces, artifact namespaces, and cross-user access tests.

This is a security boundary, not a product preference. The current reference store is task-keyed, not tenant-keyed.

## Runtime invariant
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Invalid transitions or failed mandatory dependencies route to `BLOCKED`; never silently fall back to free-form writing.

At `EDITORIAL_AUDIT`, the runtime must enforce three independent semantic decisions:
1. Hook Gate;
2. Human Voice Gate;
3. general editorial audit.

General editorial PASS is illegal until the first two gates PASS.

## Responsibility split
- ChatGPT/model: optional connected-knowledge reuse/writeback, live public research, synthesis, shared TopicDNA, mode-specific structures, current WeChat search-intent reconnaissance, titles, drafting, Hook judgment, Human Voice judgment and semantic audits.
- Hosted MCP runtime: TaskContract, legal transitions, mode-specific schema validation, durable checkpointing, knowledge receipts, gate status, required outputs, completion authority and downstream-QA invalidation.
- Deterministic delivery: Word construction, Chinese numbering, explicit/key-term bold preservation, zero-table checks, company-name bolding, risk/disclaimer insertion, formatting/mechanical QA, render checks and audit artifact.

Financial Writing has **no image generation, image upload, cover, section-image, avatar, visual manifest, sticker-post, or image-insertion workflow**. Image work belongs outside this runtime and must never block article completion.

No external connector is a hard dependency of the Writing Agent. If durable external knowledge is unavailable, research proceeds from current task sources/public research and knowledge writeback is explicitly recorded `N_A` with a reason.

## Editorial mode contracts
### FINANCE_DEEP
The financial/deep version is **material-complete** relative to the bounded audited research universe. It may compress repetition, textbook background and immaterial detail, but it must not omit a material event leg, transmission link, company class, counterexample, why-this/why-not branch, validation/falsification condition or material risk merely for brevity/elegance.

### FINANCE_BROAD
The broad/traffic version may select around one to three core contradictions/information gaps and compress non-essential branches, provided every retained conclusion has a complete evidence/causal chain.

`DUAL` shares one research base but does not force FINANCE_DEEP to inherit FINANCE_BROAD compression.

## Durable state
Persist complete serialized `WritingState` per `task_id`, including contract, stage, gates, structured outputs, artifacts, trace, attempts, blocked reason and timestamps. Save atomically after every material change; support load-by-id and recent-task listing.

The repository's `SQLiteStateStore` is the local/CI reference implementation only. A Site deployment must bind the runtime to a Site-supported durable structured store or another verified durable backend. **Do not silently fall back to ephemeral container/local disk for production checkpoints.** If durable persistence is unavailable, deployment is not ready.

Notion/Drive status pages are optional mirrors/governance layers, not executable checkpoint authority.

## Artifact storage and return
Production artifacts must live in persistent file/object storage or another backend whose lifetime survives fresh chats and runtime restarts. Never make a server-local path the public artifact contract.

Formal `WORD_FILE_ONLY` tasks require the applicable publication Word artifact(s) plus:
- `FINANCE_DEEP.docx` when deep mode applies;
- `FINANCE_BROAD.docx` when broad mode applies;
- `WRITING_AUDIT_REPORT.docx` always.

There is no visual/sticker artifact contract in v0.3.

The public MCP surface exposes typed artifact metadata plus Word resource links/templates. A production Site must prove those resources remain readable from a fresh ChatGPT conversation and after a runtime restart. Local `/data/...` paths are internal implementation details and must never be presented as user deliverables.

Publication article text is delivered only through Word artifacts. Final chat output supplies a concise QA checklist/list alongside the audit Word file; it does not paste the article body.

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
- `submit_hook_audit`
- `submit_style_audit`
- `submit_editorial_audit`
- `build_and_mechanically_audit_delivery`
- `record_knowledge_writeback`
- `submit_final_audit`

Every public tool must have a concrete input contract, concrete structured output schema, accurate read/write/destructive/open-world annotations, a human-readable title, and an operational description. Unknown stage-payload fields fail closed.

## Hook Gate
A deployed v0.3 Runtime must require independent evidence for:
- cross-finance title clickability;
- current WeChat search-intent consideration with real evidence references;
- first-three-complete-sentence retention;
- H1 continuation power;
- paragraph forward pull;
- title/opening payoff.

Current search terms are task-time evidence, not a hard-coded permanent keyword list. The runtime must reject headline packages whose applicable selected title lacks search terms/evidence refs. It must never fabricate exact search volume.

## Human Voice Gate
A deployed v0.3 Runtime must independently audit:
- template fingerprint;
- transition continuity;
- repetition control;
- rhythm naturalness;
- reader dialogue/交流感;
- narrative flow/娓娓道来;
- visible author judgment/persona;
- extreme-language control.

Humanization by slang, deliberate errors, random fragments or filler is not acceptable.

## Bold skim path and no-table contract
The draft schema records exact `skim_path_anchors`. Word delivery preserves their explicit bold formatting while also bolding company/stock names. Mechanical QA must verify those anchors are bold in the final Word.

The semantic audit separately verifies that **title + H1s + bold spans** reconstruct the main causal chain, comparison logic and conclusion boundary.

Publication articles must contain **zero tables**. A table is a deterministic hard failure rather than a warning.

## Reader/completion design
Current reader profile supplied by the user skews toward age ~45 with a substantial 55+ share. Preserve financial depth while favoring visible Chinese numbering, clear referents, readable paragraph density and a useful bold skim path. Do not patronize or oversimplify.

The last substantive section should still add information or close an earlier question/causal loop; recap-only mechanical endings are discouraged.

## Connected knowledge boundary
When useful connected knowledge is available, ChatGPT may retrieve it and record real references with `record_knowledge_context`. The runtime does not impersonate account connectors and does not require them to succeed. Time-sensitive reused knowledge remains subject to live re-verification.

Reusable writeback is similarly optional enrichment: actual successful writes receive `PASS` receipts; no writable target or no reusable item is an explicit `N_A`, not a task failure.

## QA invalidation
Any change after a PASS must invalidate every affected downstream gate:
- editorial-plan change → title/draft/all downstream QA stale;
- title change → draft/Hook/Human Voice/general editorial/delivery/mechanical/final stale;
- draft change → Hook/Human Voice/general editorial/delivery/mechanical/final stale;
- fact changes additionally require affected evidence verification to be rerun.

Stale PASS evidence must never be carried onto a revised artifact.

## Recovery and mirrors
A continuation request first lists/loads recent incomplete runtime tasks. Do not ask for already persisted task details. Optional Notion/Drive mirrors may be updated after material transitions/completion, but mirror failure does not corrupt or downgrade a valid Runtime checkpoint.

## Plugin mapping
Before the Site endpoint exists, do not invent or hard-code an MCP URL. After the private Site publishes a stable MCP endpoint, create/update the Site-managed MCP mapping from that real endpoint, then republish/reinstall as required by ChatGPT.

## Promotion validation
Do not call the deployment production-ready until all are true:
1. the Skill activates for intended formal writing requests and does not activate for standalone stock-picking/review or pure image requests;
2. all 15 typed v0.3 tools are discoverable from a fresh ChatGPT conversation with correct annotations/output schemas;
3. no visual/sticker tool, schema, resource template, required output or deployment contract remains active;
4. start persists a durable checkpoint outside ephemeral process state;
5. a fresh conversation can recover the same unfinished task without user repetition;
6. runtime restart preserves the same checkpoint;
7. illegal stages and unknown schema fields are rejected immediately;
8. FINANCE_DEEP material-completeness and FINANCE_BROAD selective-traffic schemas are both enforced;
9. headline packages enforce cross-finance click reason plus current WeChat search terms/evidence refs;
10. Hook Gate and Human Voice Gate are independently enforced before general editorial PASS;
11. draft/title/editorial revisions invalidate affected downstream QA and artifacts;
12. Word QA hard-fails tables and verifies numbered hierarchy, company bolding, exact bold skim anchors, disclaimer and red-line phrases;
13. Word artifact resources are readable through MCP from a fresh chat and after restart, with no local path exposed;
14. mechanical/render QA passes on returned Word artifacts;
15. final semantic audit gates COMPLETE and exposes audit Word + visible chat checklist without pasting article body;
16. optional connected knowledge/mirrors either succeed with real receipts or report precise `N_A`/failure boundaries without blocking core writing;
17. one user-authorized real article E2E includes deliberate interruption/recovery;
18. public/multi-user sharing remains disabled for v0.3.

## Canonical source
Repository: `D1traverser-debug/financial-writing-agent`
Branch: `main` once current v0.3 CI is green.
Skill: `skills/financial-writing-agent/SKILL.md`
