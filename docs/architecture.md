# Financial Writing Agent — Architecture v0.8

## 1. Goal

Build a reliable A-share financial-writing system around the user's actual operating model: **ChatGPT is the interaction surface; current GitHub `main` is code/rule authority and the sole durable article-state authority**. The system must preserve the canonical TaskContract/workflow, fail closed on missing capabilities, learn from durable evidence, produce auditable Word artifacts and prevent retired runtime/state mechanisms from re-entering the hot path.

## 2. One owner, one execution path

Financial Writing has:

- one BUSINESS owner: `FINANCIAL_WRITING_AGENT_RUNTIME`;
- one canonical `TaskContract`;
- one canonical workflow;
- one durable article-state authority: `main/workspaces/articles/{task_id}`;
- one ChatGPT product path.

Product path:

`ChatGPT request → current GitHub main Financial owner → durable article workspace → canonical stages → Word delivery`.

There is no business/runtime selection between OWNER_NATIVE and GITHUB_CHAT. Model, web, deterministic/Python and document facilities are capabilities inside the same state trajectory. A capability may serve an exact stage, but it may not create another task-state authority, route, output contract or terminal meaning.

Canonical execution contract: `continuity/FINANCIAL_OWNER_EXECUTION.json`.

Canonical mutation guard: `financial_writing_agent/owner_guard.py`. Canonical BLOCKED recovery/system-impact lifecycle: `financial_writing_agent/owner_lifecycle.py`. Existing schema-1.2 `STATE.json.execution_mode=GITHUB_CHAT` values and old receipt labels remain compatibility data only; they must never be interpreted as route selectors or current component names.

## 3. Runtime graph

Canonical business sequence:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`

Mandatory dependency or required-output failure blocks the exact affected action. No free-form publishable fallback, silent output degradation, legacy SQLite/plugin fallback or per-article branch fallback is permitted.

A review FAIL persists a canonical repair target. BLOCKED recovery uses that persisted target, requires repair evidence and invalidates target/downstream evidence before work resumes.

## 4. Semantic review proof model

In the current ChatGPT environment, Research/Editorial/Final review artifacts are durable but carry `CHAT_SELF_REVIEW`. They may route PASS/REVISE/FAIL under the deterministic owner guard, but same-chat judgment is not provider-attested independence.

If stronger provider-attested review becomes available later, it is an optional review capability inside the same owner state trajectory. It does not create a new workflow or state store.

The historical `INDEPENDENT_EXECUTOR` payload value is legacy evidence from the retired stage-separated runtime model and must not be interpreted as provider-attested isolation.

Current normal terminal status remains `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN` unless stronger exact-action evidence actually exists.

## 5. Persistence and recovery

- GitHub `main`: current engineering/rule authority.
- `main/workspaces/articles/{task_id}/STATE.json`: sole durable article business-state authority.
- stage/review/publication refs under that workspace: durable execution evidence.
- per-article Git branches: not current business-state authority.
- historical maintenance branches/evals: evidence only.
- legacy SQLite WritingState/plugin-local task state: not current new-task or recovery authority; its second-runtime implementation is physically absent from the current tree.
- chat memory: never checkpoint authority.
- transient DOCX attachment: delivery surface only; persisted source + file hash/manifest are regeneration/identity evidence.

Every material mutation fetches the latest main state blob identity, validates the task/output contract and legal state mutation, writes with the same prior blob SHA, then rereads state and new artifact refs before durability is claimed.

Universal lease/resume_epoch fencing is an additional outer invariant. Git blob CAS prevents stale-content overwrite but must not be described as proof that the caller still owns the current Universal writer lease.

## 6. Content modes and output contract

- `FINANCE_DEEP`: `MATERIAL_COMPLETE` relative to the bounded audited research universe.
- `FINANCE_BROAD`: `SELECTIVE_TRAFFIC`, preserving evidence/uncertainty while exposing a non-niche financial stake.
- Default distribution mode without explicit narrowing: `DUAL`.
- Delivery channel: `WORD_FILE_ONLY`.
- Required outputs derive from `TaskContract`:
  - `FINANCE_DEEP` → `AUDIT_DOCX + FINANCE_DEEP_DOCX`;
  - `FINANCE_BROAD` → `AUDIT_DOCX + FINANCE_BROAD_DOCX`;
  - `DUAL` → `AUDIT_DOCX + FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX`.

`TaskContract` rejects non-empty required-output lists that do not exactly match the selected distribution mode. There is no image/sticker workflow.

## 7. Research / Market Explanation

Research builds class-accounted Universe Coverage before narrowing to familiar names. Every ResearchPackage or equivalent durable research artifact declares `market_explanation_scope = REQUIRED | NOT_MATERIAL` with a reason. A company universe alone is not activation.

When active, Market Explanation separates economic benefit from market selection, compares hypotheses, preserves `why_this / why_not`, continuation/reversal evidence and:

`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

## 8. Editorial, Reader Funnel and prose ownership

Editorial owns material coverage, company-comparison usefulness and macro section order. Reader Funnel owns qualified click/retention/continuation/completion. Natural Authorial Prose owns reasoning progression, selectivity, specificity, natural structure/rhythm, template control and calibrated rhetoric.

Multi-company Deep work keeps MATERIAL companies/classes visible and requires a decision-useful but non-actionable comparison map. A generic monitoring checklist detached from named companies/classes fails.

## 9. Writing DNA, system impact and quality evolution

Material user edit/feedback/rejection/acceptance and performance evidence are persisted against the exact article workspace. Corrective evidence that may imply a systemic defect creates an open system-impact obligation.

System-impact review must separate local symptom from root-cause layer, compare at least two mechanisms with failure modes, choose an authority surface and bind a regression/eval plan. `SYSTEM_MAINTENANCE_REQUIRED` remains open until durable maintenance/validation refs reach at least `REGRESSION_VERIFIED`; accepted diagnosis cannot be rewritten during closure.

Quality promotion is separate from article execution. Complete cases require immutable artifact identity, real rejection evidence, held-out diversity, candidate distillation, semantic evidence verification, hard-regression execution bound to the candidate/change, blind position-swapped pairwise judging and appropriate positive/live evidence for personalized claims.

## 10. Delivery architecture

Canonical publication source is frozen before delivery. Deterministic Word rules include H1 18pt, H2 15pt, body 13.5pt, H3 12pt, zero tables, zero underlines, no tail bibliography, every supplied A-share company/stock name bolded at exact occurrences, explicit semantic skim-path bold preservation, final inline italic `风险提示：...`, required-file presence and rerender hygiene.

The owner guard enforces the immutable TaskContract at two points:

1. `DELIVERY → MECHANICAL_AUDIT`: every applicable article Word kind must exist in the structured delivery manifest with identity/hash;
2. `FINAL_AUDIT → bounded terminal`: the complete required-output set, including `AUDIT_DOCX`, must reconcile exactly.

Missing render, mechanical check or required output remains OPEN/BLOCKED; it is never silently PASS or replaced by a prose completion claim.

## 11. Capability providers

Exact-stage capability handshake determines what can execute now, not which business route is selected.

Examples:
- model runtime: research/editorial/title/draft judgment;
- web: current evidence retrieval where required;
- Python/deterministic checks: schemas, mechanical checks and guard evaluation;
- document tooling: Word generation/render inspection;
- future provider-attested reviewer: optional stronger review evidence.

The former plugin/MCP/SQLite/owner-native second runtime and WritingState delivery wrapper are physically absent from the current repository tree. Current manifests, package entrypoints, dependencies, default tests and continuity cannot activate them. Their Git history and historical evals remain evidence only.

## 12. Maintenance architecture and legacy quarantine

Financial-specific implementation/eval details live in `references/maintenance.md`. Systemic/non-trivial maintenance uses current Universal `operational_hygiene@1.0 + evolution@1.0` semantics.

A maintenance closure reconciles every current consumer of the changed invariant: Skill, execution contract, manifest, capability profile, workflow/guard/lifecycle, schemas/checks, static audit/evals, mirrors, continuity routing, current docs and stale/legacy surfaces.

Superseded mechanisms follow this rule:

- remove them from current authority/hot-path routing;
- delete current duplicate contracts/components when safe;
- retain Git history/historical evals only as evidence;
- never activate them because a current capability is missing;
- maintain `config/retired_runtime_paths.json` as the negative-space contract;
- fail unit/static CI if any listed retired runtime/discovery path reappears.

The retired dual-adapter execution contract is not current authority. The previous PR #20 is closed/unmerged historical evidence only.

## 13. Observability and assurance

Repository wiring is a capability ceiling. Current-session execution is established only by capability handshake plus action-bound evidence.

Assurance classes remain distinct:
1. declaration/contract wiring;
2. deterministic/static/regression evidence;
3. structured self-attested stage/review evidence;
4. independently/provider-attested evidence when actually available;
5. live quality/outcome evidence.

Passing one class never substitutes for another. When hosted CI does not execute workflow steps, targeted validation may provide narrower evidence but cannot be reported as full CI PASS.

## 14. Anti-bypass invariant

A publishable Financial article may not jump from user prompt to final prose. Durable main article state must exist first; each material stage must leave evidence; required outputs must reconcile; missing capability must block the affected action.

The strongest remaining shared-control-plane gaps are outside this owner-local convergence: final-response owner admission, physical GitHub write interception and non-forgeable Universal lease/epoch fencing. They remain OPEN until separately repaired and verified.
