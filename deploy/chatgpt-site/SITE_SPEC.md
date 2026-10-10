# ChatGPT Site deployment specification — Financial Writing Agent v0.8

## Goal
Deploy Financial Writing Agent v0.8 as a fresh **personal/private deployment only** Site-backed MCP runtime. Implement current `main` directly; do not revive removed compatibility surfaces or older schemas.

## Security boundary
Do not enable public/workspace/multi-user sharing until tenant isolation, authorization, task/artifact namespaces and cross-user access tests exist.

## Runtime invariant
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Mandatory dependency failures fail closed to recoverable `BLOCKED` with an exact cursor. Do not silently fall back to ephemeral container/local disk, free-form writing or duplicate tasks.

## Semantic PASS authority
Semantic `PASS` is not accepted from a CHAT_BRIDGED caller merely because a typed audit payload contains `PASS` or `INDEPENDENT_EXECUTOR`.

For `RESEARCH_AUDIT`, `EDITORIAL_AUDIT` and `FINAL_AUDIT`, PASS certification must go through `run_semantic_audit_stage`. The Site runtime must have the OpenAI Agents SDK/model runtime required by `financial_writing_agent.adapters.openai_agents.OpenAIStageExecutor` for this tool. The server executes the owner-native audit stage, records current-stage `EXECUTOR_START/EXECUTOR_END` trajectory and persisted audit provenance, then the deterministic controller decides whether the stage advances.

At `EDITORIAL_AUDIT`, the owner-native stage performs three distinct judgments:
1. Reader Funnel / Hook Gate;
2. Natural Authorial Prose / Writing DNA Gate;
3. general editorial audit.

If the owner-native semantic runtime is unavailable, preserve the task as recoverably BLOCKED at the audit cursor. Do not downgrade to caller self-certification.

The historical payload value `INDEPENDENT_EXECUTOR` means stage-separated owner-runtime execution in v0.8; it is **not provider-attested isolation**. A true independent/provider-attested claim requires a distinct provider execution identity/trace and remains a separate capability.

## Responsibility split
- ChatGPT/model generation path: research, synthesis, TopicDNA, optional market-explanation hypotheses, mode-specific structures, current WeChat search reconnaissance, titles and drafting.
- Owner-native semantic runtime: proof-bearing Research/Editorial/Final audit execution.
- Hosted MCP runtime: TaskContract, legal transitions, BLOCKED recovery, schemas, durable checkpoints, stale-evidence invalidation, required outputs and completion authority.
- Deterministic delivery: Word construction, numbering, typography, explicit bold preservation, zero-table/zero-underline/source-tail checks, inline italic risk insertion, required-file verification, rerender hygiene and mechanical QA.

Financial Writing has no image-generation, cover, section-image, avatar, sticker or image-insertion workflow.

## Durable state and artifacts
Persist complete WritingState per `task_id`, including stage, gates, structured outputs, artifacts, trace, attempts, blocker/recovery cursor, timestamps, learning samples and methodology receipts.

SQLite is local/CI reference only. Production state and Word artifacts must survive runtime restart and fresh chats. Public outputs must not expose server-local paths.

The only public artifact resource template is:
`writing-docx://{task_id}/{kind}`

Required Word outputs remain applicable article files plus `WRITING_AUDIT_REPORT.docx`. Article body is not pasted into chat.

## MCP surface
There is exactly one registration surface: `financial_writing_agent/plugin_server.py`.

Expose exactly **18 tools**:
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
- `run_semantic_audit_stage`
- `build_and_mechanically_audit_delivery`
- `record_knowledge_writeback`
- `submit_final_audit`

The five `submit_*audit` tools may persist conservative REVISE/FAIL evidence where their schemas permit it, but they cannot certify semantic PASS from CHAT_BRIDGED input. `run_semantic_audit_stage` is the public proof-bearing PASS gateway.

Every tool needs typed input/output, explicit annotations, human-readable title and operational description. Unknown fields/stages fail closed.

## Research/editorial invariants
- FINANCE_DEEP is `MATERIAL_COMPLETE` relative to the bounded audited research universe.
- FINANCE_BROAD is `SELECTIVE_TRAFFIC` but must expose a truthful non-niche financial stake to a cold finance reader.
- Universe Coverage is class-accounted; representative-stock shortcuts do not satisfy Deep completeness.
- Multi-company Deep work carries MATERIAL companies forward and leaves a decision-useful but non-actionable comparison map.
- Market Explanation is explicitly scoped `REQUIRED | NOT_MATERIAL`; a company universe alone does not activate it.
- When active, separate economic benefit from market selection, compare mechanisms, preserve `why_this/why_not`, continuation/reversal conditions and causal-confidence boundaries.

## Reader Funnel / Authorial Prose
Reader Funnel covers audience-promise fit, information value, curiosity/concreteness balance, current WeChat search evidence, first-screen retention, continuation, completion payoff and title/opening payoff. Title pools need genuine strategy diversity, not synonym variants.

Natural Authorial Prose uses the nine-part rubric for fidelity/responsibility, semantic contribution, argument progression, reader calibration, authorial selectivity, evidence specificity, structural/rhythm naturalness, template/redundancy control and uncertainty/rhetoric calibration. Template-cluster guards may force REVISE.

Do not optimize for detector evasion or recreate overlapping “活人感” silos.

## Writing DNA and quality evolution
`record_writing_learning_sample` stores raw task-level user edit/feedback/acceptance/rejection/performance evidence. A sample never auto-promotes policy.

Quality-promotion evidence is separate from article execution. Promotion requires immutable regression/held-out case identities, semantic candidate evidence verification, real hard-regression execution bound to the exact candidate/change, blind A/B position-swapped pairwise judging, and separate reference/semantic verification. A callback named “verifier” is not proof of independent execution identity.

Current FINANCE_DEEP evidence remains diagnostic only until a second held-out topic family exists. FINANCE_BROAD and Personalized Writing DNA remain not ready under their documented evidence requirements.

## Word contract
Deterministic Word enforces H1 `18pt`, H2 `15pt`, body `13.5pt`, H3 currently `12pt`, Chinese hierarchy, zero publication tables, zero underlines, no tail source appendix, explicit skim-anchor bolding without blanket company bold, one final italic inline `风险提示：...`, required-file presence, stale-render cleanup and renderability.

## Promotion validation
Do not call a Site production-ready until all are true:
1. activation routing is correct;
2. all **18 typed v0.8 tools** and only the Word resource template are discoverable;
3. owner-native `run_semantic_audit_stage` can really execute with the deployed SDK/model runtime;
4. direct CHAT_BRIDGED semantic PASS is rejected;
5. semantic-runtime unavailability produces recoverable BLOCKED rather than self-review fallback;
6. durable state/artifacts survive restart and fresh chat;
7. legal stage/revision/invalidation/recovery paths pass;
8. Deep/Broad research/editorial invariants pass;
9. semantic audit gates require current owner-runtime proof and COMPLETE rechecks it;
10. deterministic Word QA and path privacy pass;
11. one user-authorized real article E2E includes deliberate interruption/recovery and fresh-chat recovery;
12. public/multi-user sharing remains disabled.

## Canonical source
Repository: `D1traverser-debug/financial-writing-agent`
Branch: `main`
Skill: `skills/financial-writing-agent/SKILL.md`
