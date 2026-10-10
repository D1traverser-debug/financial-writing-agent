# ChatGPT Site deployment specification — Financial Writing Agent v0.5

## Goal
Deploy the current Financial Writing Agent v0.5 as a fresh private Site-backed MCP runtime. The deployment must implement the current repository contract directly; it must not revive removed compatibility surfaces or obsolete v0.4 reader/style schemas.

## Security boundary
This is **personal/private deployment only**.

**Do not enable public sharing** or workspace-wide/multi-user use until explicit tenant isolation, authorization, state namespaces, artifact namespaces and cross-user access tests exist.

## Runtime invariant
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Invalid transitions or failed mandatory dependencies route to `BLOCKED`; never silently fall back to free-form writing.

At `EDITORIAL_AUDIT`, the runtime must enforce three independent semantic decisions:
1. Reader Funnel / Hook Gate;
2. Natural Authorial Prose / Writing DNA Gate;
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

## Reader Funnel / Hook Gate
Require independent evidence for:
- audience-promise fit;
- headline information value;
- curiosity/concreteness balance;
- current WeChat search discoverability with real evidence references;
- first-three-complete-sentence retention;
- continuation flow across H1s and paragraph transitions;
- completion payoff;
- title/opening payoff.

Cross-industry finance relevance is optional and mode-sensitive. It can widen `FINANCE_BROAD` when genuinely material, but it is not a universal title requirement. `FINANCE_DEEP` prioritizes qualified-reader fit and truthful payoff.

Headline candidates must record target reader, target-reader click reason, promised payoff and current search evidence. Question headlines are not presumed superior.

## Natural Authorial Prose / Writing DNA Gate
Require the consolidated nine-part rubric:
- fidelity and responsibility;
- semantic contribution;
- argument progression;
- reader calibration;
- authorial selectivity;
- evidence specificity;
- structural/rhythm naturalness;
- template/redundancy control;
- uncertainty/rhetoric calibration.

Do not optimize for detector evasion.

Writing DNA rules use provenance: explicit durable user instructions outrank repeated patterns; repeated accepted changes/corpus evidence can support promotion; one-off edits and external skill rules remain candidates until independently supported.

## Reader evidence policy
Audience demographics are readability priors, not sophistication labels. Device-price signals or generic age heuristics must not become hard writing assumptions without observed account behavior. When available, the user's account-level click/search/completion and repeated feedback data outrank generic demographic advice.

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
Any change after PASS invalidates affected downstream gates. Title changes invalidate draft and downstream QA; draft changes invalidate Reader Funnel, authorial prose, editorial, delivery, mechanical and final audit; material fact/market-explanation changes invalidate affected evidence and downstream judgments.

## Promotion validation
Do not call a new Site production-ready until all are true:
1. intended writing requests activate and unrelated standalone stock-picking/review requests do not;
2. all 15 typed v0.5 tools are discoverable from a fresh conversation;
3. only the Word resource template is exposed;
4. start persists durable state outside ephemeral process storage;
5. fresh conversation and runtime restart recover the same unfinished task;
6. illegal stages and unknown fields fail closed;
7. FINANCE_DEEP material completeness and FINANCE_BROAD selective compression are enforced;
8. market-explanation schema and causal-confidence ladder are enforced;
9. Reader Funnel Gate and nine-part Natural Authorial Prose / Writing DNA Gate independently gate editorial PASS;
10. headline schema accepts qualified sector-specific titles without forcing cross-industry relevance;
11. revisions invalidate stale downstream QA;
12. Word QA verifies exact typography, zero tables, numbering, bold skim anchors, disclaimer and renderability;
13. Word artifact resources remain readable from a fresh conversation after restart;
14. final semantic audit gates COMPLETE and returns audit Word plus visible chat checklist;
15. one user-authorized real-article E2E includes deliberate interruption/recovery;
16. public/multi-user sharing remains disabled.

## Canonical source
Repository: `D1traverser-debug/financial-writing-agent`
Branch: `main`
Skill: `skills/financial-writing-agent/SKILL.md`
