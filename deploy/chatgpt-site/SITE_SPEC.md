# ChatGPT Site deployment specification — Financial Writing Agent v0.4

## Goal
Deploy the current Financial Writing Agent v0.4 as a fresh private Site-backed MCP runtime. The deployment must implement the current repository contract directly; it must not revive removed compatibility surfaces.

## Security boundary
This is **personal/private deployment only**.

**Do not enable public sharing** or workspace-wide/multi-user use until explicit tenant isolation, authorization, state namespaces, artifact namespaces and cross-user access tests exist.

## Runtime invariant
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Invalid transitions or failed mandatory dependencies route to `BLOCKED`; never silently fall back to free-form writing.

At `EDITORIAL_AUDIT`, the runtime must enforce three independent semantic decisions:
1. Hook Gate;
2. Natural Authorial Prose Gate;
3. general editorial audit.

## Responsibility split
- ChatGPT/model: connected-knowledge reuse/writeback when available, current public research, synthesis, TopicDNA, market-explanation hypotheses, mode-specific structures, current WeChat search-intent reconnaissance, titles, drafting and semantic audits.
- Hosted MCP runtime: TaskContract, legal transitions, schema validation, durable checkpointing, gate status, required outputs, completion authority and downstream-QA invalidation.
- Deterministic delivery: Word construction, Chinese numbering, exact typography, bold preservation, zero-table checks, company-name bolding, disclaimer insertion, formatting/mechanical QA and render checks.

Financial Writing has no image-generation, cover, section-image, avatar, sticker or image-insertion workflow.

## Editorial mode contracts
### FINANCE_DEEP
Material-complete relative to the bounded audited research universe. It may compress repetition, textbook background and immaterial detail, but it must not omit a material event leg, transmission link, company class, counterexample, market-explanation branch, validation/falsification condition or material risk merely for brevity.

### FINANCE_BROAD
May select around one to three core contradictions/information gaps and compress non-essential branches, provided every retained conclusion preserves evidence strength, key counterevidence and causal boundaries.

## Market Explanation Completeness
When a task includes a company universe and materially discusses theme/price behavior, the ResearchPackage must include a multi-hypothesis market explanation that separates:
- economic benefit / fundamental realization;
- market selection / price formation.

Material explanations use:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

The runtime must require competing mechanisms, `why_this / why_not`, continuation conditions, exhaustion/reversal conditions and unresolved questions where applicable. Observed price action is never sufficient evidence of its own cause.

## Durable state
Persist complete serialized `WritingState` per `task_id`, including contract, stage, gates, structured outputs, artifacts, trace, attempts, blocked reason and timestamps. Save after every material change and support exact load plus recent-task listing.

The repository `SQLiteStateStore` is local/CI reference only. A Site deployment must bind to a Site-supported durable structured store or another verified durable backend. **Do not silently fall back to ephemeral container/local disk** for production checkpoints.

## Artifact storage and return
Production artifacts must live in persistent file/object storage or another backend whose lifetime survives fresh chats and runtime restarts. Never make a server-local path the public artifact contract.

Formal tasks require the applicable Word artifact(s) plus `WRITING_AUDIT_REPORT.docx`.

The only public artifact resource template is:
`writing-docx://{task_id}/{kind}`

Publication article text is delivered only through Word artifacts. Final chat output supplies a concise QA checklist and does not paste the article body.

## MCP surface
There is exactly one public MCP registration surface: `financial_writing_agent/plugin_server.py`.

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

## Hook Gate
Require independent evidence for:
- cross-finance title clickability;
- current WeChat search-intent consideration with real evidence references;
- first-three-complete-sentence retention;
- H1 continuation power;
- paragraph forward pull;
- title/opening payoff.

## Natural Authorial Prose Gate
Require the 12-part rubric:
- template fingerprint;
- discourse variability;
- semantic progression;
- transition continuity;
- repetition control;
- rhythm naturalness;
- concrete evidence density;
- reader modeling;
- narrative flow;
- authorial specificity;
- uncertainty calibration;
- extreme-language control.

Do not optimize for detector evasion.

## Word contract
The deterministic Word layer must enforce:
- H1 `24px = 18pt`;
- H2 `20px = 15pt`;
- body `18px = 13.5pt`;
- H3 currently `12pt`;
- Chinese hierarchy `一、二、三 → （1）（2）（3） → ①②③`;
- zero publication tables;
- company-name bolding;
- exact required bold skim anchors;
- required risk/disclaimer;
- renderability.

Typography drift is a Mechanical Hard Fail.

## QA invalidation
Any change after PASS invalidates affected downstream gates. Title changes invalidate draft and downstream QA; draft changes invalidate Hook, prose, editorial, delivery, mechanical and final audit; material fact/market-explanation changes invalidate affected evidence and downstream judgments.

## Promotion validation
Do not call a new Site production-ready until all are true:
1. intended writing requests activate and unrelated standalone stock-picking/review requests do not;
2. all 15 typed v0.4 tools are discoverable from a fresh conversation;
3. only the Word resource template is exposed;
4. start persists durable state outside ephemeral process storage;
5. fresh conversation and runtime restart recover the same unfinished task;
6. illegal stages and unknown fields fail closed;
7. FINANCE_DEEP material completeness and FINANCE_BROAD selective compression are enforced;
8. market-explanation schema and causal-confidence ladder are enforced;
9. Hook Gate and 12-part Natural Authorial Prose Gate independently gate editorial PASS;
10. revisions invalidate stale downstream QA;
11. Word QA verifies exact typography, zero tables, numbering, bold skim anchors, disclaimer and renderability;
12. Word artifact resources remain readable from a fresh conversation after restart;
13. final semantic audit gates COMPLETE and returns audit Word plus visible chat checklist;
14. one user-authorized real-article E2E includes deliberate interruption/recovery;
15. public/multi-user sharing remains disabled.

## Canonical source
Repository: `D1traverser-debug/financial-writing-agent`
Branch: `main`
Skill: `skills/financial-writing-agent/SKILL.md`
