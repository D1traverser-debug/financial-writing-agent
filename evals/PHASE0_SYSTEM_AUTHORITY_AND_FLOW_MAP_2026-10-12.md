# Phase 0 — Financial System Authority / Flow / Duplication Map

Status: COMPLETE FOR PHASE-1 ADMISSION REVIEW
Branch: `maintenance/phase0-system-map-20261012`
Base: Financial `main` after full-system rebuild-program initialization.

This file is diagnosis/evidence only. Phase 0 intentionally changes no Financial business behavior.

## 0. Method / admission rule

Every material design proposal is treated as a hypothesis regardless of source:

- `USER_PROPOSED`
- `ASSISTANT_PROPOSED`
- `EXISTING_OWNER_MECHANISM`
- `EXTERNAL_FRAMEWORK_OR_VENDOR`
- `OTHER_OWNER_PATTERN`

A proposal is not accepted because the user prefers it, the assistant invented it, an external vendor recommends it, another owner uses it, or current code already contains it.

Admission path:

`claim/hypothesis → current authority/evidence read → failure model → competing mechanism(s) → falsification/counterexample → smallest implementation → Financial-specific tracer/eval → hard regression/fault challenge → second-order architecture review → ADOPT / ADAPT / REJECT / DEFER / DELETE`

External benchmark success is evidence about the external system, not proof that the mechanism is correct for Financial Writing.

## 1. Parent-system objective

The rebuild objective is one durable Financial owner with:

- one business contract;
- one canonical workflow/revision/invalidation truth;
- execution adapters that cannot redefine business semantics;
- bounded specialist executors with typed inputs/outputs and no stage authority;
- action-bound evidence and calibrated assurance;
- durable recovery independent of chat memory;
- feedback/evolution that distinguishes raw evidence from rule promotion;
- owner-local repair/eval/migration artifacts stored in this repository;
- Universal used only for shared contracts, cross-owner methodology, remote observation and non-authoritative control signals.

The goal is not to maximize Agent count or to make every step deterministic. Code owns order/state/invalidation/evidence shape; models own high-judgment research/editorial/writing/evaluation within those bounds.

## 2. Multi-owner vs intra-owner coordination

These are two different systems and must not be conflated.

### Universal multi-owner governance

Current BUSINESS owners are independent products. Universal may own:

- membership/registry;
- shared architecture/execution/continuity contracts;
- remote architecture freshness observations;
- non-authoritative control signals;
- cross-owner maintenance/evolution method propagation.

Universal must not own Financial article stages, article state, business evidence, writing rules, repair implementation or quality corpus.

### Financial intra-owner specialists

Researcher, Research Auditor, Editorial Architect, Headline Engine, Writer, Reader Funnel Judge, Authorial Prose Judge, General Editorial Judge, Delivery/Mechanical executors and Final Auditor are bounded executors inside one owner. They do not become independent business owners and do not get authority to create/skip stages.

A supervisor/reviewer Agent is not admitted merely because coordination failed. It would require a distinct execution identity/trace boundary plus measurable heldout lift over a simpler capability/guard design.

## 3. Current authority matrix

| Concern | Current canonical/primary authority | Mirrors / adapters / views | Phase-0 judgment |
|---|---|---|---|
| Owner entry/routing | `skills/financial-writing-agent/SKILL.md` | `continuity/TASK_INDEX.md` | Thin router is appropriate; must not become a second workflow implementation. |
| Rule ownership | `config/rule_ownership.json` | static audit | Canonical registry; no duplicate key ownership currently accepted. |
| Policy constants | `config/policy.json` | `financial_writing_agent/resources/policy.json` | Controlled byte-identical package mirror. |
| Detailed domain semantics | `references/*.md` | Skill refs + package refs | Controlled mirrors: repository tree identity is equal and `static_audit.py` byte-compares them. Not an active shadow-authority defect. |
| Typed business payloads | `financial_writing_agent/schemas.py` | MCP typed inputs/outputs | Executable validation authority; may intentionally encode hard semantic constraints also described in references. |
| Owner-native stage identity/state | `models.Stage`, `WritingState` | MCP summary models | Canonical for Python owner-native state only. |
| Owner-native legal transitions | `engine.ALLOWED_TRANSITIONS` + `controller.WorkflowController` | runtime service actions | Code-owned, but transition/revision/invalidation semantics are duplicated elsewhere. |
| Owner-native revision invalidation | `runtime_service._cleanup_after_revision` + upstream submit invalidation | individual submission functions | Executable, but not derived from one workflow dependency specification. |
| GitHub-chat stage graph | `github_chat_guard.STAGE_ORDER/REGULAR_FORWARD/REVIEW_ROUTES` | `continuity/GITHUB_CHAT_EXECUTION.json.workflow.stage_order` | Confirmed duplicate workflow authority. |
| GitHub-chat persistence | `workspaces/articles/{task_id}/STATE.json` under guard contract | `GITHUB_CHAT_EXECUTION.json` | Valid adapter-local persistence; chat memory is not authority. |
| Owner-native persistence | `SQLiteStateStore` reference/configured owner store | public MCP wrappers | Persistence boundary also reconciles immediate negative-feedback system-impact invariant. |
| Capability wiring | `continuity/EXECUTION_CAPABILITIES.json` | `UNIVERSAL_PROTOCOL_ADAPTER.json` | Profile 10 owner wiring; repo declaration is ceiling, not session proof. |
| Public owner-native tools | `plugin_server.py` + `mcp_contracts.py` | `runtime_service.py` | MCP wrapper must delegate behavior rather than fork it; one confirmed filtering fork exists. |
| Specialist high-judgment execution | `adapters/openai_agents.py` + canonical references/schemas | current GPT chat in GITHUB_CHAT mode | Specialist identity exists; prompt overlay contains duplicated business semantics requiring Phase-3 cleanup/ownership classification. |
| Deterministic delivery/QA | `adapters/deterministic.py`, `document.py`, `checks.py`, `rendering.py` | delivery references/policy | Relatively clear deterministic ownership; no Phase-0 reason to replace it wholesale. |
| Learning evidence | owner-native `WritingState.learning_samples`; GitHub-chat article workspace evidence | MCP summaries | Raw evidence only; must not auto-promote rules. |
| System-impact lifecycle | `system_impact.py` | plugin/guard entry paths | Executable lifecycle exists; semantic local-vs-systemic classification remains a heldout-eval assurance gap. |
| Methodology receipts | `methodology_receipts.py` | MCP summary | Explicit `UNVERIFIED_OWNER_RECEIPT`; must remain below independent assurance. |
| Quality promotion gate | `quality_regression.py` + `evals/quality_regression.json` | tests | Strong deterministic admission plumbing; live corpus currently insufficient for quality-promotion claims. |
| Business continuity task | `continuity/tasks/financial-writing-main/*` under active writer rules | `TASK_INDEX.md` | Current task metadata is stale relative to profile 10; must be reconciled by correct owner writer / Phase-8 mechanism, not by arbitrary infrastructure writer seizure. |
| Architecture description | `docs/architecture.md` + `continuity/AGENT_MANIFEST.json` | README / Site spec | Description/contract surfaces only; not runtime evidence. |
| Future deployment | `deploy/chatgpt-site/SITE_SPEC.md` | none active | Optional adapter/future deployment; must never become second business authority. |
| Owner-local maintenance doctrine | `references/maintenance.md` | controlled mirrors, `evals/*` | Financial repair/evolution authority remains in this repo; Universal supplies shared method only. |

## 4. Current workflow graphs

### 4.1 Owner-native path

`TaskContract → WritingEngine.start → WorkflowController → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Key authority pieces:

- `models.Stage` enumerates stages;
- `engine.ALLOWED_TRANSITIONS` accepts legal edges;
- `controller.WorkflowController` applies gate-dependent routes;
- `runtime_service` validates submissions and separately performs downstream invalidation/cleanup;
- semantic PASS additionally requires exact task/stage provenance plus current-stage `EXECUTOR_START/EXECUTOR_END` evidence;
- completion checks pending system-impact review, unresolved gates, semantic proof and required artifacts.

### 4.2 GitHub-chat path

`build_initial_state → INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`

Key authority pieces:

- `github_chat_guard.STAGE_ORDER` enumerates stages;
- `REGULAR_FORWARD` and `REVIEW_ROUTES` implement legal routing;
- `_invalidate_from` implements revision invalidation;
- action receipts bind prior GitHub state blob SHA and exact task/stage/capability/action;
- provider CAS rejects stale writers;
- `GITHUB_CHAT_EXECUTION.json` separately repeats stage order/evidence descriptions;
- chat semantic review remains `CHAT_SELF_REVIEW` and cannot become owner-native COMPLETE/PASS.

### 4.3 Core convergence defect

The two adapters are supposed to implement one business sequence, but the sequence/revision/dependency truth is hand-maintained in multiple places. A future stage/revision change can legally pass tests for one adapter while silently diverging from the other unless parity is explicitly tested.

Therefore Phase 1 must converge workflow semantics before adding more specialists or features.

## 5. Specialist responsibility matrix

| Specialist/capability | Inputs it may consume | Output / owned judgment | Tools/context | Forbidden authority |
|---|---|---|---|---|
| Researcher | TaskContract, sources, research/knowledge/market-explanation semantics | `ResearchPackage` | live web when current facts needed | Cannot draft final article, certify research audit, change stage graph. |
| Research Auditor | frozen ResearchPackage + audit/research semantics | `GateDecision` for Research | stage-separated model execution in owner-native; self-review artifact in chat | Cannot silently repair Research then certify its own repaired output; cannot route anywhere except allowed Research revise/pass route. |
| Editorial Architect | frozen research + editorial/hooks/style context | `EditorialPlan` / TopicDNA / mode structure & coverage obligations | model | Cannot change research facts/universe or draft body as authority. |
| Headline Engine | research/editorial plan + current search evidence | `HeadlinePackage` | web/search + model | Cannot alter research/evidence to justify a title; cannot skip title evidence. |
| Writer | frozen research/editorial/title | `DraftPackage` | model | Cannot redefine required MATERIAL coverage, research confidence, stage order or self-certify editorial quality. |
| Reader Funnel Judge | frozen title pool + draft | Hook/reader-funnel decision | model; current search evidence where required | Owns reader promise/click/continuation dimension only; cannot substitute for prose/general editorial/research audit. |
| Authorial Prose Judge | frozen draft + deterministic template report | Style/prose decision | model + deterministic template signal | Cannot certify research completeness, rewrite then self-certify independent PASS, or create stage transitions. |
| General Editorial Judge | frozen research/editorial/title/draft + prior dedicated audit results | overall editorial decision/revision target | model | Cannot erase dedicated Reader Funnel/Prose failures; must route earliest responsible stage. |
| Delivery Executor | frozen DraftPackage + delivery policy | Word artifacts + hashes | deterministic Python/docx | Cannot upgrade semantic assurance. |
| Mechanical Auditor | Word artifacts + frozen expected payload | mechanical/render evidence | deterministic checks/render | Cannot decide article thesis/editorial quality. |
| Final Auditor | frozen publication content + recorded gates/mechanical evidence | final red-team decision | stage-separated model / chat self-review class | Cannot upgrade chat assurance; upstream defects must route to earliest responsible stage. |
| Persistence/store | WritingState or GitHub state | durable state bytes | SQLite/GitHub CAS | Cannot decide business quality. |
| System-impact reviewer | persisted material feedback signal | local/systemic/no-change classification + alternatives | owner/maintenance reasoning | Cannot treat the first user/assistant/vendor mechanism as automatic fix; semantic classification needs evaluation evidence. |
| Quality-promotion harness | immutable cases + candidate package + verified runs | promote/block/fail | deterministic harness + external judge/verifier contracts | Cannot infer live quality from deterministic plumbing or synthetic verifier callbacks alone. |

## 6. Duplication / shadow-authority register

### H1 — duplicate workflow truth
**CONFIRMED MATERIAL DEFECT.**

Observed workflow truth appears in at least:

1. `models.Stage`;
2. `engine.ALLOWED_TRANSITIONS` + `controller.py`;
3. `github_chat_guard.STAGE_ORDER/REGULAR_FORWARD/REVIEW_ROUTES`;
4. `continuity/GITHUB_CHAT_EXECUTION.json.workflow.stage_order`;
5. invalidation dependencies are additionally hand-written in `runtime_service._cleanup_after_revision` and individual submit functions.

Failure mode: adapter drift, stale revision route, inconsistent invalidation, tests validating separate local truths.

Phase-1 target: one code-owned canonical workflow specification consumed by both adapters; descriptive docs may render/validate against it but may not define another independent machine truth.

### H2 — reference/policy mirrors
**NO_DEFECT at current evidence level.**

`references/`, Skill references and packaged references are tree-identical; source/package policy blobs are identical; `static_audit.py` fails byte drift.

Decision: keep as explicit generated/distribution mirrors until packaging design is changed. Do not spend rebuild complexity deleting a currently controlled mirror merely because duplication looks aesthetically undesirable.

### H3 — task-list maintenance-debt filtering fork
**CONFIRMED DEFECT.**

`runtime_service.list_recent_writing_tasks(include_complete=False)` hides every COMPLETE task. `plugin_server.list_recent_writing_tasks` directly uses the store and retains COMPLETE tasks with open system-impact obligations.

Failure mode: different callers receive different continuation truth; unresolved maintenance debt can disappear through one path.

Phase-2 target: move filtering to one runtime function and make MCP a presentation wrapper only.

### H4 — specialist prompt overlay duplicates domain semantics
**CONFIRMED ARCHITECTURAL RISK; NOT YET A DELETE-ALL DEFECT.**

`openai_agents.py` loads canonical references, then appends material rules such as Universe recall breadth, MATERIAL-company obligations, headline-count/diversity requirements, Deep coverage and prose-template constraints. Many are also represented in references/policy/schema/checks.

Some overlay is legitimate stage execution instruction; some is shadow business semantics.

Phase-3 rule: classify each overlay sentence as:
- EXECUTION_CONTEXT_ONLY;
- SCHEMA/DETERMINISTIC_CONSTRAINT_EXPLANATION;
- DOMAIN_SEMANTIC_DUPLICATE;
- TEMPORARY_COMPATIBILITY.

Delete/rewrite only after tests show the specialist still receives all necessary execution context from canonical surfaces.

### H5 — continuity task metadata stale against execution profile
**CONFIRMED DEFECT/DRIFT.**

Owner adapter/capabilities are profile 10, while `continuity/tasks/financial-writing-main/TASK_MANIFEST.json` still instructs profile 9 behavior. Current hygiene tests load this manifest but do not assert the profile match, so the drift escaped regression.

Phase-8 target: owner-writer-safe automatic reconciliation check before material work; add regression so task metadata cannot silently lag capability profile.

### H6 — quality process confidence exceeds live evidence
**CONFIRMED ASSURANCE GAP, NOT A QUALITY-RUNTIME DEFECT BY ITSELF.**

`quality_regression.py` has strong fail-closed admission mechanics, but most unit tests use synthetic cases/verifiers. The real seed corpus is explicitly NOT_READY: insufficient heldout diversity and no positive personalized anchor.

Decision: preserve harness; do not claim prose improvement. Phase 7 must add real, immutable heldout/live cases before changing writing-quality policy based on promotion results.

### H7 — parent multi-owner pattern imported as child multi-agent pattern
**CONFIRMED TRANSFER RISK; NO DIRECT MECHANISM ADOPTED.**

Universal orchestrates independent owners; Financial specialists cooperate inside one owner/state machine. Shared execution/readiness/evidence invariants may transfer, but orchestration topology does not automatically transfer.

Decision: no Financial supervisor/manager Agent is added during Phase 0. Specialist count/topology changes require Financial-specific experiments.

### H8 — system-impact review is structurally forced but semantic classification is not independently proven
**CONFIRMED ASSURANCE GAP.**

`system_impact.py` forces diagnosis, alternatives/failure modes and immutable accepted review, but an executor can still choose `LOCAL_ONLY` / `NO_CHANGE_WITH_REASON` on a truly systemic case or over-escalate a local case.

Phase-7 target: under-escalation / over-escalation / bad-user-mechanism / insufficient-evidence heldout trajectories. Do not solve by adding a supervisor by default.

### H9 — dynamic parent execution-registry prose can become stale
**CONFIRMED PARENT CONTROL-PLANE DEFECT; OUTSIDE FINANCIAL REPAIR OWNERSHIP.**

Universal `OWNER_EXECUTION_REGISTRY.json` is documented as a rebuildable pointer/cache, yet its Financial summary still states current owner regression passed while current full Financial CI is runner-blocked/open. This can mislead operators even if the file is non-authoritative.

Disposition: repair in Universal only after consumer/impact review. Financial must not copy that registry or its dynamic summary into this repository.

## 7. Evidence-level matrix

| Surface | What it currently proves | What it does NOT prove |
|---|---|---|
| `static_audit.py` | mirror equality, version/rule ownership/static invariant presence, MCP inventory | runtime path actually executed; semantic quality |
| schemas/unit tests | typed shapes and local validation | model will produce good/correct content |
| `tests/test_trajectory.py` | deterministic owner-native stage route, semantic-proof shape, blocked resume | provider isolation; real article quality; GitHub-chat parity |
| GitHub-chat guard tests | chat state guard, artifacts, revision invalidation, assurance ceiling | actual current chat invokes guard; prose quality |
| real GitHub CAS tracer | provider write/read/CAS composition | full article E2E or independent audit |
| `tests/test_system_impact_escalation.py` | structural obligation/alternatives/closure invariants | semantic correctness of LOCAL vs SYSTEMIC classification |
| methodology receipt tests | receipt shape/action binding/self-attestation boundary | independent hook correctness |
| quality-regression unit tests | promotion gate mechanics and fail-closed verifier contracts | real corpus readiness or real quality lift |
| real quality corpus | one real rejection + one heldout baseline for diagnosis | production promotion readiness |
| architecture validator | layer/refs/manifest structural conformance and freshness | session execution, live quality, full CI |
| GitHub Actions workflow definition | intended full suite composition | latest suite actually ran; current hosted jobs repeatedly had no steps |
| live article trajectory | currently OPEN post-fix | all future cases or provider-independent review |

Acceptance classes remain separate:
`STRUCTURAL → UNIT/CONTRACT → TRAJECTORY/FAULT → PROVIDER/PERSISTENCE → FULL OWNER REGRESSION → ACTION EXECUTION → INDEPENDENT SEMANTIC → LIVE QUALITY/OUTCOME`.

## 8. Proposal/adoption ledger

### P1 — “Just strengthen the Skill/SOP reminders”
Source: possible user/assistant/local repair instinct.
Decision: **REJECT**.
Evidence: prior real bypass occurred despite explicit SOP prose. A prompt declaration cannot substitute for transition enforcement.

### P2 — “Deploy Site/MCP now to solve everything”
Source: infrastructure option.
Decision: **REJECT FOR CURRENT REBUILD REQUIREMENT / DEFER AS FUTURE ADAPTER**.
Reason: current user operating mode is GitHub+GPT; deployment does not fix duplicated business workflow authority and would risk another implementation of the same semantics.

### P3 — “Use one canonical workflow kernel with adapters”
Source: assistant/system diagnosis, compatible with external workflow practice.
Decision: **CANDIDATE FOR PHASE 1, NOT YET PROMOTED**.
Competing alternative A: keep two independent state machines + parity tests.
Competing alternative B: make Python owner-native the only workflow and force chat to invoke it.
Failure modes: over-generalized kernel obscures adapter-specific assurance/state needs; migration can break existing paths.
Required Phase-1 proof: parity corpus before/after, negative trajectory equivalence, adapter-specific terminal/assurance preserved, deletion of duplicate graph only after parity PASS.

### P4 — “Add more specialist Agents / supervisor”
Source: common multi-agent design instinct / external examples.
Decision: **REJECT BY DEFAULT**.
Admission only when a distinct tool/context/strategy boundary plus heldout measurable lift outweighs coordination/cost/error surface.

### P5 — “Parallelize Financial research”
Source: external multi-agent research patterns and assistant hypothesis.
Decision: **DEFER TO PHASE 4 EXPERIMENT**.
Competing baseline: one Researcher with structured multi-sweep recall.
Candidate: bounded independent research lanes + one synthesis step.
Measure: material-universe recall, counterevidence discovery, contradiction resolution, synthesis error, latency/cost, duplicate/noise rate.
Adopt only if heldout Financial topics show net lift without breaking one canonical ResearchPackage.

### P6 — “Planner / generator / evaluator separation”
Source: existing Financial design plus external agent-harness patterns.
Decision: **PARTIALLY ALREADY ADOPTED, MUST BE OWNER-LOCALLY REVALIDATED**.
Current evidence: Editorial→Writer→dedicated judges exists; stage-separated owner-native audits exist.
Open challenge: evaluator responsibility overlap, prompt shadow semantics, same-chat assurance boundaries, under/over-escalation.

### P7 — “External/vendor best practice is safe after citation”
Decision: **REJECT AS A METHOD**.
Replacement rule: external source only creates a benchmark candidate. Financial-specific regression/falsification is required before adoption.

### P8 — “User’s proposed fix should be implemented because it comes from the user”
Decision: **REJECT AS A METHOD**.
User goals/constraints/failure evidence are high-value evidence; the proposed mechanism competes with alternatives like every other candidate.

### P9 — “Assistant’s first architecture diagnosis gets priority”
Decision: **REJECT**.
This rebuild exists partly because the earlier assistant diagnosis (“Python↔chat bridge”) was too shallow and closure was too early. Prepatch parent reframe and second-order attack are mandatory.

## 9. Frozen failure matrix for subsequent phases

No later phase may be called complete unless relevant cases cover both success and failure paths.

### Workflow / state
- prompt directly to final draft;
- illegal stage skip;
- invalid revision target;
- revision leaves stale target/downstream evidence;
- adapter parity mismatch;
- stage added/removed in one adapter only;
- manual COMPLETE / assurance inflation;
- future-stage state pollution.

### Persistence / recovery
- stale GitHub writer;
- crash between related writes;
- context loss and resume;
- BLOCKED without valid recovery cursor;
- idempotent retry producing duplicate/contradictory evidence;
- foreign-task artifact/reference;
- artifact hash/path mismatch;
- COMPLETE task with open maintenance debt hidden from discovery.

### Specialist ownership
- Researcher drafts publication prose as final authority;
- Writer changes research universe/facts to fit narrative;
- judge edits output then certifies its own edit as independent;
- Reader Funnel substitutes for Prose/Editorial;
- general editor bypasses a failed dedicated judge;
- specialist mutates unrelated stage state;
- duplicate specialist adds no measurable value.

### Research quality
- familiar-name tunnel vision;
- omitted material value-chain class;
- unsupported causal confidence;
- missing counterevidence;
- parallel lanes increase noise/synthesis mistakes without recall lift.

### Editorial / prose / title
- one rhetorical title mold with synonyms;
- title promise not paid off;
- template scaffolding persists;
- Deep material companies disappear;
- generic validation checklist detached from stocks/classes;
- Broad compression leaks into Deep completeness.

### Audit / assurance
- chat self-review relabeled independent;
- stale audit replay after revision;
- real but irrelevant receipt reused;
- provider/reference existence mistaken for semantic proof.

### Learning / evolution
- one-off feedback auto-promoted;
- systemic defect classified local;
- local issue escalated to heavy system maintenance;
- user/assistant/vendor first mechanism adopted without competition;
- regression PASS incorrectly promoted to live-quality PASS;
- superseded mechanism left as shadow authority.

### Delivery
- stale DOCX after upstream revision;
- source and DOCX mismatch;
- prohibited tables/underlines/risk formatting;
- missing render capability silently passed;
- transient attachment treated as durable business authority.

## 10. Phase-1 cutover plan

Phase 1 is intentionally narrow: converge workflow truth before touching specialist topology or article-quality semantics.

### Candidate canonical surface
Create a code-owned workflow specification/kernel that contains at minimum:

- canonical ordered business stages;
- legal forward transitions;
- review stages and legal revision targets;
- dependency/invalidation start points;
- stage class (generation/review/delivery/mechanical/final);
- adapter-neutral completion semantics while allowing adapter-specific terminal assurance/status.

### Consumers to migrate

- `engine.py` legal transitions;
- `controller.py` routing assertions;
- `runtime_service.py` invalidation dependency selection;
- `github_chat_guard.py` stage/route/invalidation tables;
- contract/static tests;
- `GITHUB_CHAT_EXECUTION.json` should validate/render from canonical values or be guarded against drift rather than remain an unchecked independent truth.

### Deletion targets after parity PASS

- duplicate hand-maintained `STAGE_ORDER`/`REGULAR_FORWARD`/`REVIEW_ROUTES` tables in the chat adapter where the canonical kernel can supply them;
- duplicated invalidation target lists in runtime service where dependency policy can be derived safely;
- any test that merely checks one duplicated copy against a hard-coded list while failing to compare adapters to the canonical source.

### Must remain adapter-specific

- GitHub CAS/blob-SHA receipt binding;
- owner-native SQLite/store semantics;
- owner-native semantic PASS proof model;
- chat terminal status `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`;
- provider/session capability handshake details;
- adapter-specific artifact representations.

### Phase-1 required evidence

1. pre-cutover legal/illegal trajectory corpus captured from both current adapters;
2. canonical kernel unit tests;
3. both adapters pass the same route/revision/invalidation cases after migration;
4. chat assurance terminal remains bounded and native COMPLETE semantics remain unchanged;
5. fault cases for revision, stale evidence, fake assurance and blocked state;
6. architecture/static checks updated without weakening old invariants;
7. second-order attack specifically searching for a new shadow workflow definition;
8. full CI if runner executes; otherwise exact-code scoped regression plus explicit full-CI OPEN boundary;
9. final main authority reread after merge.

## 11. Phase-0 conclusion

The system should NOT be rebuilt as a free-form swarm of Agents. Current evidence supports one Financial owner with a code-owned workflow kernel, adapter-specific persistence/execution, and bounded high-judgment specialists.

The first rebuild priority is not adding intelligence; it is removing duplicated control truth so every future improvement has one enforceable path.

Phase 1 is admitted only for workflow convergence. Research multi-agent topology, evaluator redesign and quality-policy changes remain separate hypotheses until their own Financial-specific heldout/regression evidence exists.
