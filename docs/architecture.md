# Financial Writing Agent — Architecture v0.8

## 1. Goal
Build a reliable A-share financial-writing system that separates deterministic workflow authority from model-driven research/writing, keeps Deep analysis materially complete, scopes market explanation explicitly, learns Writing DNA from traceable evidence, turns material quality feedback into executable system-impact obligations, and produces auditable Word artifacts without letting a caller self-certify semantic PASS.

## 2. Core split
The system uses a **deterministic outer runtime with model-driven inner stages and proof-bearing semantic-audit gateways**.

Deterministic Python owns TaskContract routing, legal transitions, persisted checkpoints, BLOCKED recovery, downstream invalidation, required outputs, Word construction, mechanical/render checks and completion authority.

Generation stages own research synthesis, TopicDNA, editorial choices, headline generation and drafting. Semantic audit stages own Research, Reader Funnel, Authorial Prose, general Editorial and Final review, but a PASS is usable only when the owner runtime has current stage-execution evidence.

## 3. Runtime graph
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Mandatory dependency failure routes to recoverable `BLOCKED`. No free-form fallback is permitted.

## 4. Semantic audit proof model
`WritingState.semantic_gate_proof_valid()` binds semantic PASS to:
- the exact task and expected audit stage;
- a persisted audit payload/provenance;
- reviewer identity distinct from author identity;
- an execution ref bound to `{task_id}:{stage}:...`;
- current-stage owner-runtime `EXECUTOR_START` + `EXECUTOR_END` after the latest `STAGE_ENTER`.

`WorkflowController` checks this before leaving semantic-audit stages. `WritingEngine.complete()` checks it again before COMPLETE, preventing stale legacy PASS records from bypassing the runtime.

The public MCP surface does not accept CHAT_BRIDGED PASS as certification. `run_semantic_audit_stage` invokes the owner-native OpenAI Agents SDK audit stage on the server. Missing SDK/model capability fails closed to a persisted audit-stage BLOCKED cursor.

The legacy payload label `INDEPENDENT_EXECUTOR` means **stage-separated owner-runtime judge execution**, not provider-attested isolation. True provider-attested isolation remains a separate unavailable capability until a distinct execution identity/trace exists.

## 5. Content modes
- `FINANCE_DEEP`: `MATERIAL_COMPLETE` relative to the bounded audited research universe.
- `FINANCE_BROAD`: `SELECTIVE_TRAFFIC`, preserving evidence/uncertainty while exposing a non-niche financial stake.
- Delivery: `WORD_FILE_ONLY`.

There is no chat-text publication artifact or image/sticker workflow.

## 6. Research / Market Explanation
Research builds class-accounted Universe Coverage before narrowing to familiar names. Every ResearchPackage declares `market_explanation_scope = REQUIRED | NOT_MATERIAL` with a reason. A company universe alone is not activation.

When active, Market Explanation separates economic benefit from market selection, compares hypotheses, preserves `why_this / why_not`, continuation/reversal evidence and the confidence ladder:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

## 7. Editorial ownership
Editorial owns material coverage, company-comparison usefulness and macro section order. Reader Funnel owns qualified click/retention/continuation/completion. Natural Authorial Prose owns reasoning progression, selectivity, specificity, natural structure/rhythm, template control and calibrated rhetoric.

For multi-company Deep work, MATERIAL companies/classes remain visible and a decision-useful but non-actionable comparison map is required. A generic monitoring checklist detached from named companies/classes fails.

## 8. Writing DNA, system impact and quality evolution
`record_writing_learning_sample` stores raw user edit/feedback/acceptance/rejection/performance evidence. One sample never auto-promotes policy.

Material negative/corrective samples (`USER_EDIT`, `USER_FEEDBACK`, `USER_REJECTION`) also create a durable `system_impact_signals` entry in authoritative WritingState. The lifecycle is:
`PENDING_REVIEW → REVIEWED_NO_MAINTENANCE | MAINTENANCE_REQUIRED → MAINTENANCE_CLOSED`.

`review_writing_system_impact` requires a system-level problem statement, root-cause layer, generalization scope, at least two alternative mechanisms with explicit failure modes, one selected mechanism, authority surface, regression/eval plan and evidence refs. A `SYSTEM_MAINTENANCE_REQUIRED` decision emits a non-authoritative Universal control signal and leaves the obligation open. A later closure call must replay the accepted review exactly and attach durable maintenance/validation refs with an assurance ceiling of at least `REGRESSION_VERIFIED`. Pending reviews block COMPLETE; a reviewed maintenance requirement does not block article delivery but remains discoverable even on completed tasks.

The system-impact bridge emits owner-self-attested `operational_hygiene@1.0` receipts with exact action binding. Those receipts still require Universal independent evidence/ref and semantic hook verification; they are not self-certifying.

Quality promotion is a separate evidence path. Complete regression/held-out cases require immutable artifact identity. Candidate-change/counterexample evidence must semantically support the candidate. Zero hard regressions requires a real regression run bound to the exact candidate/change. Blind pairwise runs bind the exact candidate/change and require unique verified execution refs plus separate semantic verification.

A verifier callback is only a verification contract; callback presence is not independent execution attestation.

Current FINANCE_DEEP quality evidence remains diagnostic only because held-out diversity is insufficient. No current evidence proves prose quality improved.

## 9. Delivery architecture
Public deliverables are applicable article DOCX files plus `WRITING_AUDIT_REPORT.docx`; only `writing-docx://{task_id}/{kind}` is exposed as an artifact template.

Deterministic Word rules include H1 18pt, H2 15pt, body 13.5pt, H3 12pt, zero tables, zero underlines, no publication-tail source appendix, explicit skim-path bold preservation, final inline italic `风险提示：...`, required-file presence and rerender hygiene.

## 10. Persistence and authority
- GitHub `main`: executable code/rule truth.
- Hosted durable store: production task/checkpoint truth when deployed.
- SQLite: local/CI reference implementation.
- Connected apps: optional knowledge/evidence inputs unless explicitly promoted; never implicit checkpoint authority.

## 11. Public MCP surface
`financial_writing_agent/plugin_server.py` is the only registration surface. v0.8.1 exposes **19 typed tools** plus one Word resource template.

Generation may use an explicitly permitted CHAT_BRIDGED degraded path. Semantic PASS may not. The dedicated `run_semantic_audit_stage` is the public proof-bearing owner-native audit gateway. `review_writing_system_impact` is the feedback-to-maintenance bridge; it classifies owner-local system impact but does not itself mutate GitHub policy/code or claim Universal verification.

## 12. Maintenance architecture
Owner-local `references/maintenance.md` handles Financial-specific implementation/eval/deployment details. Systemic/non-trivial maintenance first activates current Universal `operational_hygiene@1.0 + evolution@1.0` meta-maintenance semantics. This avoids a shadow owner governance path without copying a second root policy into the repo.

The owner action path now makes that declaration executable: material feedback creates a durable review obligation, the review either closes with reason or emits a control signal, and the Universal loop remains responsible for cross-authority maintenance, external scouting when required, regression validation, cleanup and calibrated closure.

## 13. Observability and assurance
OpenAI Agents SDK runs carry workflow/task/stage metadata while excluding sensitive trace payloads. Repository wiring is only a capability ceiling; live session/tool availability still needs handshake.

Assurance classes remain distinct:
1. deterministic assertions and state-machine proof;
2. stage-separated owner-runtime semantic review;
3. owner action-level self-attested methodology receipts;
4. independently verified owner action evidence;
5. true provider-attested/independent execution, currently not claimed by the owner;
6. quality/live-outcome evidence, separately gated.

Passing one class never substitutes for another.

## 14. Promotion rule
A future private Site must implement v0.8.1 directly. Production-ready status requires durable non-ephemeral state/artifact storage, all 19 tools including a functioning owner-native semantic-audit gateway and system-impact review action, rejection of direct chat PASS, interruption/recovery, a real user-authorized article E2E, fresh-chat recovery and private-only access until tenant isolation exists.
