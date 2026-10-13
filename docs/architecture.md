# Financial Writing Agent — Architecture v0.8

## 1. Goal
Build a reliable A-share financial-writing system that keeps the business workflow durable across the user's current **GitHub-mounted + GPT-chat** operating mode, preserves the Python owner runtime as a higher-assurance executable reference/optional runtime, keeps Deep analysis materially complete, scopes market explanation explicitly, learns Writing DNA from traceable evidence, turns material quality feedback into system-impact obligations, and produces auditable Word artifacts without letting a chat caller redefine the business contract or self-certify stronger assurance than it actually has.

## 2. One owner, one business contract, two execution adapters
Financial Writing has one business owner, one canonical `TaskContract`, one canonical business sequence and two execution adapters:

1. **OWNER_NATIVE / Python** — `WorkflowController + WritingEngine + OpenAI Agents SDK/deterministic executors`. This path can produce proof-bearing owner-runtime semantic PASS when its exact runtime is session-available.
2. **CHAT_BRIDGED / GitHub** — current GPT chat performs the stage work while GitHub `main` stores per-article checkpoints and stage artifacts under `workspaces/articles/{task_id}` according to `continuity/GITHUB_CHAT_EXECUTION.json`. Normal stage transitions and feedback capture use `financial_writing_agent/github_chat_guard.py`; BLOCKED recovery and system-impact classify/close actions use `financial_writing_agent/github_chat_lifecycle.py`. This is the user's current production mode and does not require a Site/MCP deployment.

The second path is not a free-form fallback and is not a second business definition. It inherits `TaskContract` routing, delivery channel and required-output semantics from OWNER_NATIVE, uses the same business stage order/domain references, requires a session capability handshake and durable GitHub checkpoint after every material action, and keeps its weaker review/lifecycle assurance explicit.

If no platform/mode narrowing was explicitly requested, the canonical route is `DUAL`, so both article modes plus the audit Word are required. A chat executor may not silently narrow this to one mode.

## 3. Runtime graph
Canonical business sequence:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`

OWNER_NATIVE may then reach `COMPLETE` through the controller. GITHUB_CHAT terminates normally as `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`; it may deliver usable Word artifacts but may not relabel chat self-review as owner-native COMPLETE.

Mandatory dependency or required-output failure blocks the exact affected action. No free-form publishable fallback or silent output degradation is permitted.

## 4. Semantic audit proof model
For OWNER_NATIVE, `WritingState.semantic_gate_proof_valid()` binds semantic PASS to the exact task/stage, persisted audit provenance, distinct reviewer/author identities, an execution ref and current-stage `EXECUTOR_START/EXECUTOR_END` evidence. `WorkflowController` and `WritingEngine.complete()` revalidate it.

For GITHUB_CHAT, Research/Editorial/Final review artifacts are persisted separately but carry `CHAT_SELF_REVIEW`. They may find defects and force REVISE/FAIL; they never become Python `GateStatus.PASS`, `INDEPENDENT_EXECUTOR`, or provider-attested evidence. Missing stronger audit capability therefore leaves certification OPEN rather than encouraging a fake PASS.

The historical payload label `INDEPENDENT_EXECUTOR` means stage-separated owner-runtime judge execution only, not provider-attested isolation.

## 5. Persistence and recovery
- GitHub `main`: engineering/rule authority **and the only GITHUB_CHAT business-state write ref**.
- OWNER_NATIVE run: authoritative `WritingState` in its configured owner store; SQLite is local/CI reference.
- GITHUB_CHAT run: `main/workspaces/articles/{task_id}/STATE.json` + exact stage/review/publication refs are business execution truth.
- Per-article Git branches are not a current business-state authority and must not be created for new GITHUB_CHAT tasks.
- Chat memory: never checkpoint authority.
- A transient chat DOCX attachment: delivery artifact only; the persisted GitHub publication source + structured output manifest are the regeneration/identity authority.

Every normal material GITHUB_CHAT stage mutation fetches the current **main** state blob identity, validates the immutable task/output contract plus the stage transition through `github_chat_guard.py`, writes the intended checkpoint with the same blob SHA, and rereads it before claiming durability. Lifecycle mutations use the same fetch/CAS/reread discipline through `github_chat_lifecycle.py`.

A GITHUB_CHAT review `FAIL` blocks in place. Recovery may not hand-edit status or guess a new stage: `resume_blocked_state` requires non-empty repair evidence plus the persisted failed review artifact and FAIL decision, invalidates both, keeps the exact review stage, and requires a fresh review artifact before any later guarded advancement.

This owner-local Git blob-SHA discipline prevents stale-blob updates but does not itself prove that the caller still owns the current outer Continuity writer lease, nor does it physically intercept every direct GitHub write. Those are explicit control-plane boundaries rather than hidden assurance claims.

## 6. Content modes and output contract
- `FINANCE_DEEP`: `MATERIAL_COMPLETE` relative to the bounded audited research universe.
- `FINANCE_BROAD`: `SELECTIVE_TRAFFIC`, preserving evidence/uncertainty while exposing a non-niche financial stake.
- Default distribution mode when no platform/mode is explicitly requested: `DUAL`.
- Delivery channel: `WORD_FILE_ONLY`.
- Required outputs derive from `TaskContract` and the model rejects a non-empty required-output list inconsistent with its distribution mode:
  - `FINANCE_DEEP` → `AUDIT_DOCX + FINANCE_DEEP_DOCX`;
  - `FINANCE_BROAD` → `AUDIT_DOCX + FINANCE_BROAD_DOCX`;
  - `DUAL` → `AUDIT_DOCX + FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX`.

There is no image/sticker workflow.

## 7. Research / Market Explanation
Research builds class-accounted Universe Coverage before narrowing to familiar names. Every ResearchPackage or equivalent GITHUB_CHAT research artifact declares `market_explanation_scope = REQUIRED | NOT_MATERIAL` with a reason. A company universe alone is not activation.

When active, Market Explanation separates economic benefit from market selection, compares hypotheses, preserves `why_this / why_not`, continuation/reversal evidence and:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

## 8. Editorial, Reader Funnel and prose ownership
Editorial owns material coverage, company-comparison usefulness and macro section order. Reader Funnel owns qualified click/retention/continuation/completion. Natural Authorial Prose owns reasoning progression, selectivity, specificity, natural structure/rhythm, template control and calibrated rhetoric.

Multi-company Deep work keeps MATERIAL companies/classes visible and requires a decision-useful but non-actionable comparison map. A generic monitoring checklist detached from named companies/classes fails.

## 9. Writing DNA, system impact and quality evolution
OWNER_NATIVE `record_writing_learning_sample` stores raw edit/feedback/acceptance/rejection/performance evidence. Material corrective/negative samples create the system-impact lifecycle `PENDING_REVIEW → REVIEWED_NO_MAINTENANCE | MAINTENANCE_REQUIRED → MAINTENANCE_CLOSED`.

GITHUB_CHAT persists material user evidence inside the exact `main` article workspace. Edit/feedback/rejection that may affect system behavior creates an OPEN system-impact item in the same guarded checkpoint operation. `github_chat_lifecycle.review_system_impact_state` then reuses the canonical owner root-cause/decision constants, requires at least two mechanisms with failure modes, freezes the accepted diagnosis, and either closes it locally or emits a structurally complete non-authoritative Universal control-signal object. A `MAINTENANCE_REQUIRED` item can move to history only when the unchanged diagnosis is replayed with maintenance/validation refs and an evidence assurance label of at least `REGRESSION_VERIFIED`.

That chat closure is explicitly `SELF_ATTESTED_CHAT_EVIDENCE_BINDING`: the adapter binds refs and labels but does not independently verify those refs merely by receiving them, and it never fabricates owner-native methodology receipts.

Quality promotion is separate. Complete cases require immutable artifact identity, real rejection evidence, held-out diversity, candidate distillation, semantic evidence verification, hard-regression execution bound to the candidate/change, blind position-swapped pairwise judging and appropriate positive/live evidence for personalized claims. Current FINANCE_DEEP evidence remains diagnostic only; no current evidence proves prose quality improved.

## 10. Delivery architecture
Canonical publication source is frozen before delivery. OWNER_NATIVE deterministic Word rules include H1 18pt, H2 15pt, body 13.5pt, H3 12pt, zero tables, zero underlines, no tail bibliography, deterministic A-share-name bolding on every exact occurrence plus explicit skim-path bold preservation, final inline italic `风险提示：...`, required-file presence and rerender hygiene.

GITHUB_CHAT uses current document/Python tooling when session-available and records exactly which deterministic/render checks actually ran. Its guard additionally enforces the owner `TaskContract` at two points:
1. `DELIVERY → MECHANICAL_AUDIT`: every applicable article Word kind must exist in the structured delivery manifest with file identity/hash;
2. `FINAL_AUDIT → bounded terminal`: the complete required-output set, including `AUDIT_DOCX`, must reconcile exactly.

Missing render, mechanical check or required output remains OPEN/BLOCKED; it is never silently PASS or replaced by a prose completion claim.

## 11. Public MCP / future deployment
`financial_writing_agent/plugin_server.py` remains the single MCP registration surface and exposes the v0.8.1 owner-native tool contract. It is an optional/future execution substrate for this user's present setup, not a prerequisite for GITHUB_CHAT.

If a private Site is later deployed, it must implement the same owner business contract directly; do not revive the old v0.2.1 compatibility PoC as a second authority.

## 12. Maintenance architecture
Financial-specific implementation/eval details live in `references/maintenance.md`. Systemic/non-trivial maintenance uses current Universal `operational_hygiene@1.0 + evolution@1.0` semantics. The user goal/correction is evidence, not an automatic implementation instruction; existing rules skipped in execution are runtime/trajectory defects, not invitations to duplicate prose.

A maintenance closure must reconcile the entire consumer surface of the changed invariant, not only the files named in the first impact map. For cross-surface rule changes this includes, where applicable: canonical policy/reference, startup Skill, runtime adapters, schemas/builders/checks, static audit/eval harness, generated mirrors, architecture/continuity routing, legacy/dead paths and live fresh-chat trajectory. A local PASS cannot be promoted to “propagation complete” while stale executable assertions still encode the superseded rule.

## 13. Observability and assurance
Repository wiring is a capability ceiling. Current-session execution is established only by capability handshake plus action-bound evidence.

Assurance classes stay distinct:
1. declaration/contract wiring;
2. deterministic/static/regression evidence;
3. GITHUB_CHAT structured self-attested stage/review/lifecycle evidence;
4. stage-separated owner-runtime semantic review;
5. owner action-level methodology receipts;
6. independently verified/provider-attested execution when actually available;
7. live quality/outcome evidence.

Passing one class never substitutes for another. When hosted CI does not execute workflow steps, targeted current-session validation may provide narrower evidence but cannot be reported as full CI PASS.

## 14. Anti-bypass invariant
A publishable Financial article may not jump from user prompt to final prose. The selected execution adapter must first create/resume durable owner state, preserve the same canonical task/output contract, then leave evidence at each material stage. If the current session cannot execute the required adapter or satisfy every required output, it blocks the exact action instead of producing a pseudo-final article.

The current owner-local guards make the supported chat trajectory explicit and recoverable, but they do not physically prevent a noncompliant ChatGPT response from bypassing the owner before admission, do not provide a non-forgeable outer writer fencing token, and do not make GitHub Contents API call the owner guard. Those boundaries remain separate shared/product-control issues rather than being hidden behind stronger wording.
