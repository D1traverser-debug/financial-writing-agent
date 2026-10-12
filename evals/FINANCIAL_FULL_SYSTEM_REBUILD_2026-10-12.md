# Financial Writing Agent — Full System Rebuild Program — 2026-10-12

Status: ACTIVE OWNER-LOCAL SYSTEM REBUILD PROGRAM
Repository authority: `D1traverser-debug/financial-writing-agent@main`
Baseline HEAD: `cf5236a8218678a85bd95bd6782442086d2d891c`
Scope owner: `FINANCIAL_WRITING_AGENT_RUNTIME`

## Authority / branch discipline

`main` is the only long-lived Financial engineering and business-rule authority.

The rebuild will NOT use a long-lived parallel architecture branch. Instead:

1. This rebuild program, diagnosis, migration map, acceptance matrix and durable decisions live on `main`.
2. Each behavioral phase uses a short-lived branch cut from the latest `main`.
3. A phase branch is never authority and may not become a dependency of later phases.
4. Before merge, the phase must rebase/reconcile against the latest `main`, run its scoped harness, second-order/fault challenge, and final-authority reread.
5. After merge, all later phases start again from the new `main`; stale phase branches are closed/deleted rather than retained as shadow authority.
6. No Financial business repair/eval/runtime file is stored in Universal. Universal may keep only shared contracts, remote observations, cross-owner methodology and non-authoritative control signals.

## Meta-method: every idea is a hypothesis

No proposal is accepted because it came from the user, the assistant, OpenAI, Anthropic, another framework, another owner, or an existing Financial file.

Every material mechanism must go through:

`claim/hypothesis → authority/evidence read → failure model → at least one credible competing mechanism → counterexample/falsification → smallest implementation → tracer/targeted eval → regression/fault challenge → second-order architecture review → adopt / revise / reject / delete`

External methods are benchmark candidates only. An external recommendation that cannot survive Financial-specific regression, cost, assurance and failure-mode checks is rejected or adapted.

## Parent-system problem statement

The target is not "make the current article workflow stricter". The target is one durable Financial writing system in which:

- one owner owns one business contract;
- one canonical workflow specification owns stage/revision/invalidation/completion truth;
- execution adapters (Python owner-native, GitHub+GPT chat, future Site/MCP) cannot redefine business semantics;
- high-judgment specialists own distinct bounded responsibilities and cannot bypass workflow/state authority;
- evidence, receipts, provenance and assurance classes are action-bound;
- recovery resumes from durable state rather than chat memory;
- quality learning does not auto-promote one-off feedback;
- system-impact/evolution changes have owner-local diagnosis, alternatives, regression and heldout evidence;
- Universal manages shared methodology/architecture contracts only and does not become a Financial shadow repository.

## Multi-agent / multi-owner distinction

Two coordination problems must remain separate:

1. **Universal multi-owner governance**: four BUSINESS owners are independent systems. Universal owns shared contracts, registry, freshness observation, control signals and cross-owner method propagation; it must not orchestrate their business stages.
2. **Financial intra-owner specialists**: Researcher, Research Auditor, Editorial Architect, Headline Engine, Writer, Reader Funnel Judge, Authorial Prose Judge, General Editorial Judge, Delivery Builder, Mechanical Auditor and Final Red Team are bounded executors inside one Financial owner. They do not own workflow state or stage existence.

A failure in one layer must not be "fixed" by inventing another supervisor unless it has a distinct execution identity, trace boundary and measurable heldout lift.

## Target architecture

### A. Thin entry / routing
- Skill remains a thin owner router and hard-boundary anchor.
- Dispatcher chooses `OWNER_NATIVE` vs `GITHUB_CHAT` from current-session capability evidence.
- Missing capability blocks the exact action; no free-form publishable fallback.

### B. Canonical workflow kernel
Create/derive one canonical machine-readable or code-owned workflow specification for:
- stage graph;
- forward transitions;
- revision routes;
- invalidation dependencies;
- required artifact classes;
- gate ownership;
- terminal states;
- blocked recovery semantics.

`controller.py` and `github_chat_guard.py` become adapters over that shared kernel, not two independent workflow definitions.

### C. State / persistence
- Owner-native store and GitHub-chat state are adapter-specific persistence implementations.
- State schema, artifact identity, revision invalidation, stale-write protection and recovery invariants are shared.
- Chat memory is never authority.

### D. Specialist execution boundaries
Each specialist receives a typed input contract and produces a typed artifact/decision. Specialists cannot:
- create/skip mandatory stages;
- self-promote assurance;
- mutate unrelated stage artifacts;
- certify their own rewritten output as independent PASS;
- silently broaden task scope.

### E. Research system
Research may use bounded parallel specialist lanes only where independence adds recall breadth (policy/event, industry/value chain, listed-company universe, counterevidence/market mechanism). A synthesis step reconciles conflicts and produces one ResearchPackage; Research Audit attacks omissions and unsupported confidence.

### F. Editorial / writing / audit
Generator and evaluator responsibilities remain distinct. Reader Funnel, Natural Prose and General Editorial are separate dimensions. Revisions route to the earliest responsible stage and invalidate downstream evidence.

### G. Delivery / artifacts
Publication source is canonical before rendering. DOCX generation and mechanical QA are deterministic when tooling is available. Delivery never upgrades semantic assurance.

### H. Learning / system impact / promotion
`feedback → raw evidence → system-impact triage → candidate mechanisms → smallest authority change → hard regression → heldout quality eval → promote/reject`.

One-off user feedback is evidence, not an automatic global rule. External methods are benchmark candidates, not authority.

## Rebuild phases

### Phase 0 — Baseline / ownership map
- enumerate every code/rule/state/eval/continuity/deploy surface;
- classify canonical vs mirror vs historical vs shadow authority;
- map current duplicate workflow and duplicated rule surfaces;
- build current-state dependency graph;
- freeze acceptance/failure matrix before behavior changes.

### Phase 1 — Canonical workflow convergence
- extract shared workflow specification;
- move Python controller/engine and GitHub-chat guard to the shared transition/invalidation truth;
- add parity tests proving both adapters accept/reject the same legal/illegal trajectories;
- delete duplicated stage-graph definitions after cutover.

### Phase 2 — Execution readiness / state / recovery
- unify action receipt schema and capability handshake semantics;
- test stale write, crash between mutations, context loss, BLOCKED resume, idempotent retry, revision invalidation and foreign-task artifact pollution;
- repair owner-native recent-task/system-impact shadow filtering.

### Phase 3 — Specialist responsibility contracts
- inventory every specialist's instruction/tool/schema/state permissions;
- eliminate overlapping ownership and hidden stage authority;
- add executor-specific contract and negative tests;
- no new specialist unless a distinct context/tool/strategy boundary produces measurable value.

### Phase 4 — Research architecture
- test sequential vs bounded parallel research on recall quality, contradiction discovery, cost and synthesis error;
- adopt parallel lanes only where heldout research cases show net lift;
- preserve one canonical synthesized ResearchPackage.

### Phase 5 — Editorial / title / prose / audit architecture
- verify each judge catches the defect class it owns and does not leak into neighboring ownership;
- add under-escalation / over-escalation cases;
- verify same-chat self-review never becomes independent PASS;
- test revision routing to earliest responsible stage.

### Phase 6 — Delivery / Word / artifact reliability
- deterministic artifact generation, privacy, idempotency, render QA, stale file cleanup, publication-source reproducibility;
- fault cases for unavailable render/document capability.

### Phase 7 — Learning / evolution / quality promotion
- reconcile owner learning ledger, system-impact lifecycle, quality regression corpus and promotion gates;
- add real-rejection, heldout and candidate-distillation coverage;
- distinguish hard-regression PASS from live quality lift;
- test proposed external/user/assistant methods against baseline before adoption.

### Phase 8 — Continuity / recovery / operator experience
- reconcile Financial task metadata to the current execution profile;
- make fresh-chat/resume behavior deterministic from Financial-owned state;
- remove stale/no-longer-supported compatibility/deployment assumptions;
- future Site/MCP remains an adapter, never a new business authority.

### Phase 9 — Full-system fault / trajectory / live E2E
Attack at least:
- direct prompt→draft bypass;
- stage skip;
- fake PASS / assurance inflation;
- stale writer;
- reused pre-revision artifacts;
- foreign task artifacts;
- partial persistence/crash;
- context loss/resume;
- research omission;
- evaluator edits then self-certifies;
- system-impact local downgrade of a systemic defect;
- over-escalation of a local defect;
- user/assistant/external first-solution bias;
- duplicate/shadow authority reintroduction;
- live article E2E and Word delivery.

## Acceptance classes

Never collapse these into one PASS:

1. STRUCTURAL_CONFORMANCE
2. DETERMINISTIC_UNIT / CONTRACT
3. TRAJECTORY / FAULT
4. PROVIDER / PERSISTENCE BOUNDARY
5. OWNER_FULL_REGRESSION
6. ACTION-LEVEL EXECUTION
7. INDEPENDENT SEMANTIC VERIFICATION
8. LIVE ARTICLE / BUSINESS QUALITY OUTCOME

A phase may merge with a narrower assurance claim only if its remaining OPEN gates are explicit and the merged change cannot silently claim a stronger class.

## Current known open defects / risks entering Phase 0

- Python and GitHub-chat currently contain overlapping workflow definitions and can drift.
- owner-native recent-task filtering differs from MCP wrapper behavior for COMPLETE tasks with open maintenance debt.
- Financial USER task metadata still describes execution profile 9 while owner architecture/capability profile is 10.
- Hosted GitHub Actions runner has repeatedly created jobs with no steps executed, so full owner regression remains unproven.
- current quality corpus is not promotion-ready for FINANCE_DEEP, FINANCE_BROAD or personalized Writing DNA.
- current post-fix guarded GitHub-chat path has no natural real-article live trajectory yet.
- external methods and internal architectural proposals need Financial-specific falsification rather than source-authority adoption.

## Immediate next action

Run Phase 0 on current `main`: produce the owner/authority/flow/duplication map and failure matrix in this repository. Do not change business behavior until that map is reviewed against actual code and tests. Then start Phase 1 from the latest `main` using a short-lived branch.
