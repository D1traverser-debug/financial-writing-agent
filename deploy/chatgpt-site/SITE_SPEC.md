# ChatGPT Site deployment specification — Financial Writing Agent v0.7

## Goal
Deploy the current Financial Writing Agent v0.7 as a fresh private Site-backed MCP runtime. Implement the repository contract directly; do not revive removed compatibility surfaces or older reader/style/research schemas.

## Security boundary
This is **personal/private deployment only**.

**Do not enable public sharing** or workspace-wide/multi-user use until explicit tenant isolation, authorization, task namespaces, artifact namespaces and cross-user access tests exist.

## Runtime invariant
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Invalid transitions and mandatory dependency failures fail closed to `BLOCKED`. BLOCKED must persist a recovery cursor; after the actual blocker is repaired, `resume_blocked_task` resumes that cursor. Never silently fall back to free-form writing or start a duplicate task.

At `EDITORIAL_AUDIT`, enforce three independent semantic decisions:
1. Reader Funnel / Hook Gate;
2. Natural Authorial Prose / Writing DNA Gate;
3. general editorial audit.

## Responsibility split
- ChatGPT/model: current research, synthesis, TopicDNA, optional market-explanation hypotheses, mode-specific structures, current WeChat search reconnaissance, titles, drafting and semantic audits.
- Hosted MCP runtime: TaskContract, legal transitions, BLOCKED recovery, schema validation, durable checkpoints, gate state, stale-evidence invalidation, required outputs and completion authority.
- Deterministic delivery: Word construction, numbering, exact typography, explicit bold preservation, zero-table/zero-underline/source-tail checks, inline italic risk insertion, required-file verification, rerender hygiene and mechanical QA.

Financial Writing has no image-generation, cover, section-image, avatar, sticker or image-insertion workflow.

## Editorial modes
### FINANCE_DEEP
`MATERIAL_COMPLETE` relative to the bounded audited research universe. It may compress repetition, textbook background and immaterial detail, but it must not omit a material event leg, transmission link, company class, counterexample, applicable market-explanation branch, validation/falsification condition or material risk merely for brevity.

For multi-company work, name every MATERIAL company and build an evidence-based comparison map across relevant dimensions such as order visibility, realization speed, earnings sensitivity, validated overseas exposure and technology optionality. This may produce research/evidence buckets, never executable buy/sell advice.

### FINANCE_BROAD
`SELECTIVE_TRAFFIC`. It may organize around one to three supported information gaps/core contradictions, provided retained conclusions preserve evidence strength, counterevidence and causal boundaries.

Broad packaging must pass a cold-reader finance test: a finance reader with no prior interest in the niche sector should still understand from the title/opening why the event matters to money, orders, profits, cash flow, capital expenditure, company/asset differentiation or policy transmission. Sharper truthful contrast is allowed; fabricated urgency or guaranteed-return framing is not.

## Market Explanation scope
Every ResearchPackage declares `market_explanation_scope = REQUIRED | NOT_MATERIAL` and a reason.

A company universe alone is not activation. Use `REQUIRED` only when the article materially explains market selection/price formation, leadership/limit-up/relative price reaction, continuation/reversal or another cross-sectional market-selection question.

When active, separate economic benefit/fundamental realization from market selection/price formation. Require competing mechanisms, `why_this / why_not`, continuation and reversal/exhaustion conditions, unresolved questions where material, and the confidence ladder:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

Observed price action never proves its own cause.

## Durable state
Persist complete WritingState per `task_id`, including contract, stage, gates, structured outputs, artifacts, trace, attempts, BLOCKED reason/origin/recovery cursor, timestamps and raw Writing DNA learning samples.

The repository `SQLiteStateStore` is local/CI reference only. A Site deployment must bind to a verified durable structured store. **Do not silently fall back to ephemeral container/local disk** for production checkpoints.

## Raw Writing DNA evidence
`record_writing_learning_sample` stores user edit/feedback/acceptance/rejection and post-publication performance evidence on the task. A sample is `RAW_EVIDENCE_ONLY` and must not mutate durable global writing policy automatically. Promotion remains governed by the maintenance/evidence hierarchy.

## Artifact storage and return
Production artifacts must live in persistent storage that survives fresh chats and runtime restarts. Never make a server-local filesystem path part of the public artifact contract or audit Word.

Formal tasks require applicable article Word files plus `WRITING_AUDIT_REPORT.docx`.

The only public artifact resource template is:
`writing-docx://{task_id}/{kind}`

Publication article text is delivered only through Word artifacts. Final chat output supplies a concise QA checklist and does not paste article body.

## MCP surface
There is exactly one public MCP registration surface: `financial_writing_agent/plugin_server.py`.

Expose exactly **17 tools**:
- `start_writing_task`
- `get_writing_task`
- `list_recent_writing_tasks`
- `resume_blocked_task`
- `record_writing_learning_sample`
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

Every public tool must have a concrete typed input/output contract, explicit annotations, a human-readable title and an operational description. Unknown fields/stages fail closed.

## Reader Funnel / Hook Gate
Require independent evidence for audience-promise fit, headline information value, curiosity/concreteness balance, current WeChat search discoverability, first-three-sentence retention, continuation value, completion payoff and title/opening payoff.

Cross-industry finance relevance is optional and mode-sensitive, not a universal hard rule. `FINANCE_DEEP` prioritizes qualified-reader fit and truthful payoff. `FINANCE_BROAD` instead must surface a non-niche finance stake for a cold reader. Formal title candidates record target reader, click reason, promised payoff, angle family and current search evidence; title pools must span at least five genuinely distinct supported strategy families rather than synonym-swapping one shell. Question titles are not presumed superior.

## Natural Authorial Prose / Writing DNA Gate
Require the nine-part rubric: fidelity/responsibility, semantic contribution, argument progression, reader calibration, authorial selectivity, evidence specificity, structural/rhythm naturalness, template/redundancy control and uncertainty/rhetoric calibration.

Argument progression includes a major-section bridge invariant: one H1 should normally create the reason for the next through cause, consequence, chronology, comparison, narrowing, correction or inference. Generic transition phrases do not satisfy that requirement.

Before semantic judgment, run the deterministic template-cluster guard. Repeated AI-like staging families can force REVISE and cannot be self-waived by the authoring executor.

Do not optimize for detector evasion. Do not recreate separate “活人感 / 娓娓道来 / 交流感” rule silos.

## Editorial ownership boundary
Editorial owns material coverage, company comparison usefulness and macro section order. Natural Authorial Prose owns reasoning progression. Reader Funnel owns continuation value. The runtime should not score one transition defect three times under three different names.

Do not ship a canned structure-pattern library. Generate topic-specific candidate structures from current TopicDNA.

For company/theme Deep articles, research must first reconcile the economically material value-chain universe, classify companies by materiality, and carry MATERIAL-company obligations into the draft. Representative-stock shortcuts are not valid completeness. Monitoring/validation/falsification sections must map signals back to named stocks or explicit value-chain classes.

A comparison map may state research order/evidence strength or “current vs later / visibility vs sensitivity” buckets. It must not use direct or euphemistic language whose practical function is to tell the reader what to buy, when to trade, what target to use, or how much to hold.

## Reader evidence policy
Audience demographics are readability priors, not sophistication labels. Device-price or generic age heuristics must not become hard writing assumptions without behavioral evidence. Account-level click/search/completion and repeated user feedback outrank generic heuristics when available.

## Word contract
The deterministic Word layer enforces:
- H1 `24px = 18pt`;
- H2 `20px = 15pt`;
- body `18px = 13.5pt`;
- H3 currently `12pt`;
- Chinese hierarchy `一、二、三 → （1）（2）（3） → ①②③`;
- zero publication tables;
- **zero underlined runs**;
- no publication-tail `资料来源 / 参考资料 / 参考来源 / 来源汇总` section; provenance remains in research/audit and material source identity is attributed naturally in prose;
- explicit selected bold skim anchors, without blanket automatic bolding of every company occurrence;
- one final fully italic inline `风险提示：...` paragraph, with no separate numbered risk H1;
- every applicable required Word artifact before Mechanical PASS;
- stale render-page cleanup before rerender;
- renderability.

For branching/long `FINANCE_DEEP` articles, visible lower-level numbered navigation is a deterministic requirement rather than a stylistic preference.

Typography, underline/source-tail/risk-format drift are Mechanical Hard Fails.

## QA invalidation
Research changes invalidate all affected downstream editorial/draft/QA/artifact state and factual knowledge-writeback decisions. Editorial-plan, title and draft changes clear their stale downstream payloads/gates/artifacts. Pure rhetoric/title/layout revisions do not by themselves invalidate already-valid factual knowledge writeback.

Dedicated Reader Funnel or Authorial Prose REVISE routes immediately to the declared upstream stage rather than waiting for a contradictory general-editorial PASS.

Semantic PASS requires independent audit provenance. A chat self-review may find defects but cannot certify semantic gates as PASS.

## Promotion validation
Do not call a Site production-ready until all are true:
1. intended writing requests activate and unrelated stock-picking/review requests do not;
2. all 17 typed v0.7 tools are discoverable from a fresh conversation;
3. only the Word resource template is exposed;
4. durable task state survives process/runtime restart;
5. Word artifacts survive fresh conversation and restart;
6. a deliberately BLOCKED task preserves a recovery cursor and successfully resumes through `resume_blocked_task` after repair;
7. illegal stages and unknown fields fail closed;
8. FINANCE_DEEP material completeness includes value-chain class accounting, MATERIAL-company reconciliation, stock-grounded validation sections and a decision-useful non-actionable company comparison map; FINANCE_BROAD selective compression remains mode-specific and passes the cold-reader finance-stake test;
9. `REQUIRED` and `NOT_MATERIAL` Market Explanation scope both validate correctly, including a non-empty company universe with legitimate `NOT_MATERIAL`;
10. Reader Funnel and nine-part Authorial Prose gates independently gate editorial completion;
11. raw Writing DNA samples persist without auto-promoting policy;
12. headline schema accepts qualified sector-specific titles, requires at least five angle families across the pool, and rejects synonym-only title pools;
13. deterministic template-cluster guard can force prose REVISE and major-section bridge defects cannot be waved through by generic transition text;
14. semantic audit PASS requires independent executor provenance; chat self-review cannot PASS;
15. revisions invalidate stale downstream state correctly;
16. Word QA verifies exact typography, zero tables, zero underlines, no end source appendix, inline italic risk, numbered Deep navigation when branching, explicit skim anchors, required-file presence and renderability;
17. public/artifact/audit outputs contain no server-local paths;
18. final semantic audit gates COMPLETE and returns audit Word plus visible checklist;
19. one user-authorized real-article E2E includes deliberate interruption/recovery and fresh-chat recovery;
20. public/multi-user sharing remains disabled.

## Canonical source
Repository: `D1traverser-debug/financial-writing-agent`
Branch: `main`
Skill: `skills/financial-writing-agent/SKILL.md`
