# ChatGPT Site deployment specification

## Goal
Host Financial Writing Agent as a Site-backed MCP plugin so the same private runtime is available from the user's ChatGPT sessions without local installation.

## v0.4 deployment boundary
v0.4 is **personal/private deployment only**. Do not enable public sharing, workspace-wide sharing, or multi-user use until the runtime has explicit per-user tenant isolation, authorization, state namespaces, artifact namespaces, and cross-user access tests.

This is a security boundary, not a product preference. The current reference store is task-keyed, not tenant-keyed.

## Runtime invariant
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Invalid transitions or failed mandatory dependencies route to `BLOCKED`; never silently fall back to free-form writing.

At `EDITORIAL_AUDIT`, the runtime enforces three independent semantic decisions:
1. Hook Gate;
2. Natural Authorial Prose / Human Voice Gate;
3. general editorial audit.

General editorial PASS is illegal until the first two gates PASS.

## Responsibility split
- ChatGPT/model: connected-knowledge reuse/writeback when available, live public research, synthesis, market-explanation hypothesis testing, TopicDNA, mode-specific structures, current WeChat search-intent reconnaissance, titles, drafting and semantic audits.
- Hosted MCP runtime: TaskContract, legal transitions, strict stage schemas, durable checkpointing, knowledge receipts, gate status, required outputs, completion authority and downstream-QA invalidation.
- Deterministic delivery: Word construction, Chinese numbering, exact typography, explicit/key-term bold preservation, zero-table checks, company-name bolding, risk/disclaimer insertion, formatting/mechanical QA, render checks and audit artifact.

Financial Writing has **no image generation, image upload, cover, section-image, avatar, visual manifest, sticker-post, or image-insertion workflow**. Image work belongs outside this runtime and must never block article completion.

No external connector is a hard dependency of the Writing Agent. If durable external knowledge is unavailable, research proceeds from current task sources/public research and knowledge writeback is explicitly recorded `N_A` with a reason.

## Editorial mode contracts
### FINANCE_DEEP
The financial/deep version is **material-complete** relative to the bounded audited research universe. It may compress repetition, textbook background and immaterial detail, but it must not omit a material event leg, transmission link, company class, counterexample, why-this/why-not branch, validation/falsification condition, market-explanation branch or material risk merely for brevity/elegance.

### FINANCE_BROAD
The broad/traffic version may select around one to three core contradictions/information gaps and compress non-essential branches, provided every retained conclusion has a complete evidence/causal chain and any retained market explanation keeps its uncertainty/counterevidence boundary.

`DUAL` shares one research base but does not force FINANCE_DEEP to inherit FINANCE_BROAD compression.

## Market-explanation completeness
When `ResearchPackage.universe` is non-empty, v0.4 requires a `market_explanation` map.

The runtime/schema must enforce:
- separate **economic-benefit** and **market-selection / price-formation** questions;
- concept/subtheme/economic-link coverage;
- company exposure type, benefit path, sensitivity basis and realization horizon where material;
- cross-sectional `why_this / why_not`;
- at least two competing/alternative explanation hypotheses;
- continuation conditions and exhaustion/reversal conditions;
- unresolved questions where causal identification is weak.

Every material market explanation uses one of:
`VERIFIED_FACT`, `SUPPORTED_MECHANISM`, `PLAUSIBLE_INTERPRETATION`, `UNRESOLVED`.

Any non-`UNRESOLVED` hypothesis requires real task-specific evidence references. Price action, limit-ups, turnover, concept labels, fund-flow proxies or continued rises are observations to explain, not self-proving causes.

This layer explains market selection. It never becomes entry/exit timing, target price, position sizing, stop level or other trading execution advice.

## Natural Authorial Prose / Human Voice Gate
v0.4 does **not** optimize for AI-detector evasion. The deployed style gate audits actual writing quality and authorial specificity.

The strict 12-part rubric is:
1. template fingerprint;
2. discourse variability;
3. semantic progression;
4. transition continuity;
5. repetition control;
6. rhythm naturalness;
7. concrete evidence density;
8. reader modeling;
9. narrative flow;
10. authorial specificity / evidence-bounded prioritization;
11. uncertainty calibration;
12. extreme-language control.

PASS requires all 12 PASS. Slang, deliberate errors, random fragments, fake intimacy and decorative noise are not acceptable “humanization”.

## Hook Gate
A deployed v0.4 Runtime requires independent evidence for:
- cross-finance title clickability;
- current WeChat search-intent consideration with real evidence references;
- first-three-complete-sentence retention;
- H1 continuation power;
- paragraph forward pull;
- title/opening payoff.

Current search terms are task-time evidence, not a hard-coded permanent keyword list. Never fabricate exact search volume.

## Typography, skim path and no-table contract
Publication Word uses the user's requested sizes mapped to Word points with standard 96-dpi CSS equivalence:
- H1: `24px = 18pt`;
- H2: `20px = 15pt`;
- body: `18px = 13.5pt`.

H3 remains policy-controlled at 12pt unless explicitly changed. Mechanical QA hard-fails typography drift.

The draft schema records exact `skim_path_anchors`. Word delivery preserves their bold formatting while also bolding company/stock names. Semantic audit verifies that **title + H1s + bold spans** reconstruct the event, economic transmission, company comparison/market-selection logic and conclusion boundary.

Publication articles contain **zero tables**. A table is a deterministic hard failure.

## Reader/completion design
Current reader profile supplied by the user skews toward age ~45 with a substantial 55+ share. Preserve analytical depth while favoring visible Chinese numbering, clear referents, readable paragraph density and a useful bold skim path. Do not patronize or oversimplify.

The last substantive section must still add information, test an interpretation, or close an earlier question/causal loop; recap-only mechanical endings are not sufficient.

## Durable state
Persist complete serialized `WritingState` per `task_id`, including contract, stage, gates, structured outputs, artifacts, trace, attempts, blocked reason and timestamps. Save atomically after every material change; support load-by-id and recent-task listing.

The repository's `SQLiteStateStore` is the local/CI reference implementation only. A Site deployment must bind the runtime to a Site-supported durable structured store or another verified durable backend. **Do not silently fall back to ephemeral container/local disk for production checkpoints.** If durable persistence is unavailable, deployment is not ready.

Notion/Drive status pages are optional mirrors/governance layers, not executable checkpoint authority.

## Artifact storage and return
Production artifacts must survive fresh chats and runtime restarts. Never make a server-local path the public artifact contract.

Formal `WORD_FILE_ONLY` tasks require the applicable publication Word artifact(s) plus `WRITING_AUDIT_REPORT.docx`. There is no visual/sticker artifact contract.

Publication article text is delivered only through Word artifacts. Final chat output supplies a concise QA checklist/list alongside the audit Word file; it does not paste the article body.

## MCP surface
There is exactly one public MCP registration surface: `financial_writing_agent/plugin_server.py`. `runtime_service.py` contains business/runtime operations only. `mcp_server.py` is a thin compatibility shim.

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

Every public tool must have a concrete input contract, concrete structured output schema, accurate annotations, a human-readable title and an operational description. Unknown stage-payload fields fail closed.

## QA invalidation
Any change after a PASS invalidates every affected downstream gate. In particular, changes to facts or market-explanation hypotheses/confidence invalidate affected research/editorial/final evidence; title and draft changes invalidate Hook/authorial-prose/general-editorial/delivery/mechanical/final checks. Stale PASS evidence must never be carried onto a revised artifact.

## Connected knowledge and recovery
When useful connected knowledge is available, ChatGPT may retrieve it and record real references with `record_knowledge_context`. Time-sensitive reused knowledge remains subject to live re-verification. Writeback is optional enrichment: real writes receive `PASS` receipts; no writable target or no reusable item is explicit `N_A`.

A continuation request first lists/loads recent incomplete runtime tasks. Do not ask for already persisted task details. Optional mirrors may fail without corrupting a valid Runtime checkpoint.

## Promotion validation
Do not call the deployment production-ready until all are true:
1. intended writing activation works and standalone stock-picking/review or image requests do not accidentally activate it;
2. all 15 typed v0.4 tools are discoverable with correct schemas/annotations;
3. no visual/sticker contract remains active;
4. durable checkpoints survive fresh chat and runtime restart;
5. illegal stages/unknown fields fail closed;
6. FINANCE_DEEP material completeness and FINANCE_BROAD selective compression are enforced;
7. stock/theme ResearchPackages require multi-hypothesis market-explanation maps and causal-confidence discipline;
8. Hook Gate and the 12-part Natural Authorial Prose gate are independently enforced before general editorial PASS;
9. exact Word typography `24px/20px/18px` equivalents, hierarchy, no-table, bold anchors, disclaimer and red lines are mechanically verified;
10. revisions correctly invalidate downstream QA/artifacts;
11. artifact resources remain readable from fresh chat/restart with no local path exposed;
12. mechanical/render QA passes;
13. final semantic audit checks market-explanation completeness where applicable and returns audit Word + visible chat checklist without article body;
14. optional knowledge/mirrors produce real receipts or precise `N_A` boundaries;
15. one user-authorized real article E2E includes deliberate interruption/recovery;
16. public/multi-user sharing remains disabled for v0.4.

## Canonical source
Repository: `D1traverser-debug/financial-writing-agent`
Branch: `main` once current v0.4 CI is green.
Skill: `skills/financial-writing-agent/SKILL.md`
