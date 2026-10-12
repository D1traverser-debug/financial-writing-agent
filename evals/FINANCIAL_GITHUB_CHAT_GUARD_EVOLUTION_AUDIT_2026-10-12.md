# Financial GitHub-chat guard evolution audit — 2026-10-12

Status: MAINTENANCE / EVOLUTION CANDIDATE UNDER VALIDATION  
Parent method: Universal Continuity v3.7 `SYSTEM_MAINTENANCE_POLICY` M0→M11 + unified self-maintenance/evolution adapter.  
Trigger: user correction that the prior repair was not sufficiently reasoned through the parent evolution system, plus Universal control signal #5 reporting stale Financial architecture validation.

## M0 — Intake / triage
The user correction is a credible system-defect hypothesis, not an implementation instruction. Re-observation confirmed the prior `d50adb...` repair changed Financial architecture while current Universal architecture validation remained pinned to `a76c83...`. The defect is therefore real and material.

## M1 — Full-system reframe
The original failed writing experiment was not primarily a prose-quality failure or merely “Python and chat lacked a bridge.” The parent-system view is:

1. **OWNER_BINDING / EXECUTION_READINESS** — the real GPT+GitHub production path could bypass the Financial owner workflow.
2. **EXECUTION-CONTROL GAP** — the first `GITHUB_CHAT` repair introduced durable state/CAS but stage order still depended on chat obeying a declaration; no deterministic transition guard or exact action-bound execution receipt existed.
3. **ARCHITECTURE-DESCRIPTION DRIFT** — `AGENT_MANIFEST.json` still described only the Python state/guard surfaces and omitted the new chat state/guard path.
4. **ASSURANCE / CLOSURE GAP** — `d50adb...` was merged while full CI never executed and architecture validation was stale. Calling the repair simply “fixed” exceeded the evidence.
5. **STALE-HARNESS ASSERTIONS** — several profile-10 tests still asserted pre-guard executor/status strings. A functioning runner would have surfaced these mismatches.

The visible stage-order failure is a downstream symptom of those control-plane defects.

## M2 — Learning / reuse scout
Reuse-before-build sources inspected:

- Universal `AGENT_ARCHITECTURE_CONTRACT.json`: durable workflow state and transition guards must live outside chat prose; harness must include contract + trajectory; freshness fails when current owner HEAD differs from validation HEAD.
- Universal `EXECUTION_READINESS_CONTRACT.json`: repository declaration is not current-session execution; HARNESS_WIRED requires a concrete executor + fail-closed state transition; material execution requires durable action-bound receipts.
- Universal `OWNER_ADAPTER_CONTRACT.json`: one parent maintenance/evolution loop, pre-patch reframe, alternative competition, strongest relevant validation, second-order review, and no self-attestation inflation.
- Novel owner architecture: existing GitHub-backed CHAT_BRIDGED mode already combines GitHub project state with deterministic guard modules rather than trusting chat prose alone.
- Current OpenAI connected-app/GitHub product model reinforces the same session-availability boundary: connected capability availability must be checked in the current execution context rather than inferred from repository declarations.

No new supervisor Agent or new root policy was justified.

## M3 — Candidate competition
### A. Add more Skill reminders
Rejected. The original bypass already happened despite explicit workflow prose. This repeats declaration-only control.

### B. Require Site/MCP deployment now
Rejected. The user explicitly operates current owners as GitHub-mounted + GPT chat. Deployment is not required to repair the present execution-control defect.

### C. Let same-chat review certify owner-native PASS
Rejected. Improves convenience by destroying the assurance boundary.

### D. Add a Financial supervisor/reviewer Agent
Rejected. It adds architecture without a distinct execution identity or stronger evidence.

### E. Deterministic owner-local GitHub-chat transition guard + action-bound receipts
Selected. Reuses current Financial business stages, Universal receipt semantics, GitHub CAS and the existing CHAT_BRIDGED owner pattern while keeping stronger semantic/independent assurance separate.

## M4/M5 — Canonical repair
Maintenance branch: `maintenance/github-chat-guard-hardening-20261012`  
PR: #13

Implemented:

- new `financial_writing_agent/github_chat_guard.py`;
- GITHUB_CHAT state schema 1.1 with exact action-bound self-attested execution receipts;
- every material transition binds the fetched prior `STATE.json` blob SHA;
- GitHub replacement must use that same SHA; stale writers fail at the provider CAS boundary;
- stage skips, wrong revision targets, missing current-stage artifacts, foreign-task artifact refs, future-stage artifact/review pre-seeding, unsupported status spoofing and chat-assurance inflation fail closed;
- only `IN_PROGRESS`, `BLOCKED`, and bounded chat terminal status are legal for GITHUB_CHAT; owner-native `COMPLETE` cannot be hand-injected;
- `REVISE` invalidates target-stage and all downstream active artifact/review refs so stale evidence cannot satisfy a replayed stage;
- material negative/corrective feedback + OPEN system-impact item share one guarded state mutation and receipt;
- `AGENT_MANIFEST.json` now models the GitHub-chat state authority and transition guard;
- profile-10 execution capabilities require the deterministic guard in the current session; missing guard blocks rather than degrading to free-form publication;
- Skill remains a thin router and explicitly forbids manual `current_stage` editing;
- stale profile-10 tests were reconciled to the canonical guarded contract rather than reverting business semantics.

## M6/M7 — Validation performed so far
### Structural architecture replay
PASS against current Universal 1.1 manifest semantics for the maintenance branch:
- required architecture layers/fields present;
- all referenced guard/state/tool paths present;
- `contract` + `trajectory` harness suites declared;
- Skill measured 7,549 bytes, below 8,192-byte target;
- no unsupported manifest version introduced.

### Targeted deterministic trajectory/fault replay
PASS for:
- initial action-bound receipt;
- missing Research artifact rejection;
- missing review artifact rejection;
- stage route enforcement;
- same-chat assurance upgrade rejection;
- owner-native `COMPLETE` spoof rejection;
- future-stage artifact/review pre-seeding rejection;
- bounded terminalization below owner-native COMPLETE;
- paired negative-feedback/system-impact checkpoint;
- revision invalidation requiring a fresh upstream artifact;
- foreign-task artifact path rejection.

These are scoped guard/architecture checks, not full owner regression or live writing-quality evidence.

### GitHub provider-bound tracer
A synthetic tracer on isolated branch `test/github-chat-guard-tracer-20261012` exercised the production GitHub state boundary:

`STATE init → INTAKE→RESEARCH receipt → persisted Research artifact/blob SHA → RESEARCH→RESEARCH_AUDIT receipt → stale prior STATE SHA rejected with HTTP 409 → persisted RESEARCH_AUDIT REVISE artifact → REVISE→RESEARCH receipt → reread state with stage_artifacts={} and review_decisions={}`.

The synthetic workspace was then deleted from the tracer branch. Commit history remains the receipt.

This proves provider CAS + the new state/receipt/invalidation shape can compose. It does **not** prove a real article, live autonomous routing or prose quality.

### Full GitHub Actions
BLOCKED externally. PR runs again create a job with `steps=null`; no SDK smoke, MCP smoke, pytest, static audit, wheel or render command actually begins. Do not call full CI PASS or `REGRESSION_VERIFIED` on that basis.

## M8/M9 — Reliability and second-order challenge
Second-order attack found and repaired multiple defects in the first guard draft:

1. after a review routed `REVISE` upstream, old target/downstream artifact refs initially survived and could have been reused;
2. manually pre-seeded future-stage artifact/review refs were not initially rejected;
3. an unsupported status such as owner-native `COMPLETE` could initially be injected into chat state because status was not allow-listed.

The guard now invalidates downstream evidence on revision, rejects future-stage state pollution, allow-lists chat statuses and keeps bounded terminalization tied to `FINAL_AUDIT`.

Other explicit boundaries:
- a repository guard still cannot physically prevent an arbitrary LLM from printing text outside the supported execution path; it defines the only supported/certifiable Financial path and makes unsupported free-form output lack valid state/receipts;
- chat receipts are `SELF_ATTESTED_CHAT_EXECUTION_RECEIPT`, not independent/provider-attested evidence;
- current-session guard/model/GitHub/web/document capability still requires handshake;
- the existing owner-native `list_recent_writing_tasks` vs MCP unresolved-maintenance filtering shadow remains an independent OPEN defect;
- the Financial user task manifest is still profile 9 under another valid owner writer and must be reconciled by that writer on the next Financial task turn; this parent SYSTEM_INFRA maintenance does not seize that business lease.

## M10 — Propagation / cleanup
Shared method propagated here: execution-capability claims require a concrete fail-closed route and action-bound evidence; architecture changes must revalidate freshness. Financial business writing semantics remain local.

No new root Universal policy, supervisor Agent or Site deployment was added. Superseded declaration-only assumptions are being removed from Financial execution capability tests/contract surfaces; historical audits remain as history and are not rewritten to fabricate past certainty.

## M11 — Current claim ceiling
Before final merge and final-main architecture revalidation, the strongest legal claim is:

`GUARD_HARDENING_CANDIDATE__TARGETED_TRAJECTORY_AND_PROVIDER_BOUNDARY_PASS__FULL_OWNER_CI_BLOCKED__FINAL_ARCHITECTURE_FRESHNESS_OPEN__LIVE_ARTICLE_OPEN`

Do not claim:
- the Financial system is globally fixed;
- current full regression suite passed;
- a real Financial chat has autonomously executed the new path;
- prose quality improved;
- same-chat review is independent.
