# Financial Writing Agent — Architecture v0.6

## 1. Goal
Build a reliable A-share financial-writing system that separates deterministic workflow authority from high-judgment research/writing, keeps deep analysis materially complete, activates price-formation analysis only when it is actually material, learns Writing DNA from traceable evidence, and produces auditable Word artifacts.

## 2. Core split
The system uses a **deterministic outer runtime with model-driven inner stages**.

Deterministic Python owns TaskContract routing, legal transitions, persisted checkpoints, BLOCKED recovery cursors, downstream invalidation, required outputs, Word construction, exact typography, mechanical/render checks and completion authority.

High-judgment model stages own research synthesis, TopicDNA, optional market-explanation hypotheses, mode-specific editorial choices, Reader Funnel design, headline generation, drafting, Natural Authorial Prose judgment and final semantic red-team review.

The model cannot skip, insert, recover or complete workflow stages by itself.

## 3. Runtime graph
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Mandatory failure routes to `BLOCKED`, never ordinary free-form writing. BLOCKED state persists `blocked_from_stage`, `blocked_resume_stage` and the reason. Once the external dependency or contract defect is repaired, `resume_blocked_task` returns to that exact recovery cursor.

## 4. Content modes
Financial Writing owns `FORMAL_ARTICLE` only.

Unspecified platform defaults to `DUAL`: one audited research base with independently edited `FINANCE_DEEP` and `FINANCE_BROAD` outputs.

- `FINANCE_DEEP`: `MATERIAL_COMPLETE` relative to the bounded audited research universe.
- `FINANCE_BROAD`: `SELECTIVE_TRAFFIC`, normally organized around one to three supported information gaps/core contradictions.

Delivery is `WORD_FILE_ONLY`. There is no chat-text publication artifact or visual/sticker/image workflow.

## 5. Research and explicit Market Explanation scope
Research always covers the factual/industrial/economic problem broadly enough to support both modes. Every ResearchPackage declares:
- `market_explanation_scope = REQUIRED | NOT_MATERIAL`;
- `market_explanation_scope_reason`.

A non-empty company universe is not sufficient to activate price-formation analysis.

When `REQUIRED`, market explanation separates economic benefit/fundamental realization from market selection/price formation, uses competing mechanisms rather than a hindsight chain, and grades material explanations as:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

Observed price action proves that selection occurred, not why.

## 6. Editorial ownership boundaries
- Editorial owns material coverage and macro section prerequisites/order.
- Natural Authorial Prose owns paragraph/sentence reasoning progression, authorial selectivity and rhetoric calibration.
- Reader Funnel owns whether title/opening/H1/flow gives the intended reader sufficient truthful reason to click, continue and finish.

Do not triple-count the same defect across those gates. There is no canned `structure_patterns.md` library; structures are generated from the current TopicDNA and prior outlines may only be used for collision detection.

## 7. Reader Funnel assurance
The funnel is:
`qualified impression → click → first-screen retention → continued reading → completion → promised insight delivered`.

The dedicated gate checks audience-promise fit, headline information value, curiosity/concreteness balance, current WeChat search discoverability, first-three-sentence retention, continuation value, completion payoff and title/opening payoff.

Cross-industry finance relevance is optional and mode-sensitive, not a universal hard rule.

## 8. Natural Authorial Prose and Writing DNA
The independent prose gate checks nine dimensions:
1. fidelity and responsibility;
2. semantic contribution;
3. argument progression;
4. reader calibration;
5. authorial selectivity;
6. evidence specificity;
7. structural/rhythm naturalness;
8. template/redundancy control;
9. uncertainty/rhetoric calibration.

Writing DNA uses provenance. `record_writing_learning_sample` stores raw task-level USER_EDIT / USER_FEEDBACK / USER_ACCEPTANCE / USER_REJECTION / POST_PUBLICATION_PERFORMANCE evidence. Samples remain `RAW_EVIDENCE_ONLY`; durable promotion requires the maintenance policy rather than automatic mutation from one sample.

## 9. Delivery architecture
Only Word artifacts are public deliverables:
- `FINANCE_DEEP.docx` when applicable;
- `FINANCE_BROAD.docx` when applicable;
- `WRITING_AUDIT_REPORT.docx` always.

The only public artifact resource template is `writing-docx://{task_id}/{kind}`.

Deterministic Word rules include H1 `18pt`, H2 `15pt`, body `13.5pt`, H3 currently `12pt`, zero publication tables, Chinese numbering normalization and preservation/verification of explicit skim-path bold spans. Company names are not blanket-bolded.

Mechanical PASS requires every applicable Word artifact to exist. Rerender clears stale render pages first. Public summaries and audit Word must not expose server-local filesystem paths.

## 10. Revision invalidation
Upstream changes invalidate affected downstream gates, payloads and artifacts. Research changes invalidate factual knowledge-writeback decisions; purely rhetorical/title/layout revisions do not force a factual knowledge writeback to be repeated.

Dedicated Reader Funnel and Authorial Prose REVISE decisions route immediately to their proper upstream targets rather than leaving the task in an ambiguous audit loop.

## 11. Persistence and authority
- GitHub `main`: executable code/rule truth.
- Hosted durable store: production task/checkpoint truth when a Site runtime exists.
- SQLite: local/CI reference implementation.
- Connected Notion/Drive/etc.: optional knowledge/governance layers, not executable checkpoint authority.

## 12. Public MCP surface
`financial_writing_agent/plugin_server.py` is the only public MCP registration surface. `runtime_service.py` owns operations and registers no server.

v0.6 exposes 17 typed tools plus one Word resource template. New v0.6 capabilities include explicit `resume_blocked_task` recovery and `record_writing_learning_sample` raw evidence capture.

The old `mcp_server.py`, `CHAT_TEXT`, visual/sticker contracts and canned structure-pattern library are deleted and must not return.

## 13. Observability
The optional OpenAI Agents SDK executor uses the same deterministic state machine. SDK runs carry a workflow name, task `group_id` and stage metadata while excluding sensitive trace payloads. Repository wiring proves capability design, not that a particular ChatGPT session has the required executor/runtime; session capability handshake remains required.

## 14. Assurance classes
1. deterministic assertions: schemas, transitions, recovery, invalidation, artifacts, typography, zero tables, file identity, path privacy and render checks;
2. independent semantic judges: research completeness, optional market explanation, Reader Funnel, Natural Authorial Prose/Writing DNA, compliance;
3. trajectory/eval tests: legal stage order, revision loops, fail-closed recovery and stale-evidence invalidation.

Passing one class never substitutes for another.

## 15. Promotion rule
A future private Site must implement v0.6 directly. It must not revive v0.4/v0.5 payloads or removed compatibility surfaces. Production-ready status additionally requires durable non-ephemeral state/artifact storage, a real user-authorized article E2E, deliberate interruption/recovery, fresh-chat recovery and private-only access until tenant isolation is implemented.
