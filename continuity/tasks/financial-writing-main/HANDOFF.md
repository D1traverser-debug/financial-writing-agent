# 金融文章写作｜Continuity Handoff

- task_id: `financial-writing:main`
- display_name_zh: **金融文章写作**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: `FINANCIAL_WRITING_AGENT_RUNTIME`
- current_stage: `READY_FOR_NEW_OR_EXPLICIT_ARTICLE`
- continuity_contract: `CONTINUITY_V3_7`
- owner rule authority: `D1traverser-debug/financial-writing-agent@main`
- execution capability profile: **10**

## Current architecture

Financial Writing has **one BUSINESS owner, one canonical TaskContract, one canonical workflow kernel, and two bounded execution adapters**.

Canonical business workflow authority is `financial_writing_agent/workflow_spec.py`:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`

Adapters may be stricter in assurance/capability, but may not redefine the owner's defaults, required outputs, stage graph, revision routes, invalidation or terminal semantics.

### OWNER_NATIVE
Use only when the current session actually has the Python/plugin owner runtime required by the next action.

- authoritative article state: versioned `WritingState`;
- SQLite mutations use checkpoint CAS and reject stale writers;
- crash-safe revision cleanup is replayed through shared `state_recovery.py`;
- semantic PASS remains proof-bearing;
- `WritingEngine.complete()` rechecks required outputs before COMPLETE.

### GITHUB_CHAT
Use only when owner-native is unavailable and the current session has model execution, GitHub owner read/write, an executable deterministic `github_chat_guard.py`, and exact-stage web/document capabilities.

Current write surface is **only** `main/workspaces/articles/{task_id}`. New per-article business-state branches are forbidden.

GITHUB_CHAT inherits the same canonical TaskContract as OWNER_NATIVE:
- no explicit platform/mode narrowing → `DUAL`;
- delivery channel → `WORD_FILE_ONLY`;
- default required outputs → `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX`;
- direct single-mode override requires `USER_EXPLICIT_OVERRIDE` plus an exact substring from the original user prompt persisted as `distribution_mode_override_evidence` in the INIT receipt.

Every material mutation must fetch the current main `STATE.json` blob SHA, execute the exact stage, persist stage/review/publication evidence, let the guard build/validate the next state and receipt, replace the same main state with CAS, then reread it.

DELIVERY cannot advance unless every article Word output required by the immutable TaskContract is present. FINAL_AUDIT cannot terminalize until the complete required-output set including `AUDIT_DOCX` is reconciled. Semantic review assurance remains `CHAT_SELF_REVIEW`; normal terminal state remains `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`.

## Live fresh-chat result on 2026-10-12

A real zero-memory fresh chat successfully reconstructed the repo, selected GITHUB_CHAT, executed the stage workflow, persisted research/reviews, performed a genuine `EDITORIAL_AUDIT → DRAFT` revision, generated/rendered Word output and stopped at the correct bounded terminal assurance.

However, the visible delivery was only **2 files** (Broad + Audit). The user had not requested single-mode output. The canonical default was DUAL and should have produced **3 files** (Deep + Broad + Audit).

Therefore that live run is classified as:

`LIVE_TRAJECTORY_EXECUTED__OUTPUT_CONTRACT_FAILED_3_TO_2`

not a clean E2E PASS.

Root cause was adapter-semantic parity drift: Phase-1 had unified stage/revision semantics, but GITHUB_CHAT did not mechanically inherit/enforce the owner TaskContract's default distribution mode and required outputs. The defect crossed INTAKE routing, adapter state, DELIVERY, FINAL reconciliation and post-run audit ordering.

Durable incident record:
`evals/FINANCIAL_LIVE_E2E_TASK_OUTPUT_CONTRACT_INCIDENT_2026-10-12.md`

## Evolution / propagation lesson

The same re-audit found stale previous-rule assertions in Skill/static/eval surfaces after a prior writing-rule calibration had claimed propagation PASS. The maintenance contract now requires **consumer-complete propagation**: before closure, search all current consumers of a changed invariant (startup/Skill, policy/reference, runtime/adapter, schema, harness/evals, mirrors, continuity/deployment) and remove or explicitly justify stale/superseded assertions.

A real defect is not permission to keep adding reminder prose. Fix the canonical enforcement gap and regress it.

## Branch policy and cleanup boundary

PR #19, which proposed formalizing article-branch discovery, was closed unmerged. Adding `article/{task_id}` as another business-state authority would increase discovery/recovery/conflict/cleanup complexity and does not solve the actual output-contract defect.

Historical `article/*` refs may remain as evidence, but no new GITHUB_CHAT business mutation may use them. A legacy branch-backed task must be migrated to main before any future continuation.

Several `tmp-should-not-create*` refs were accidentally created during the maintenance tool sequence. They carry no intended authority. The current connected GitHub surface does not expose branch deletion, so physical cleanup remains OPEN with that exact tooling blocker; this does not widen current authority because guard/Skill/contract all fail closed on non-main new business-state writes.

## New task vs continuation

A normal request such as “写一篇关于 X 的财经文章” is **NEW_TASK**. Do not auto-resume an old article.

For a new task:
1. read current main Skill / manifest / capability profile;
2. handshake only capabilities needed now;
3. choose OWNER_NATIVE or guarded GITHUB_CHAT;
4. create durable article state before research/drafting;
5. preserve canonical TaskContract defaults unless exact user-prompt override evidence exists;
6. execute the canonical workflow;
7. reconcile required outputs mechanically before delivery/terminal claims.

Only explicit continuation may resume old article state. Resolve exact owner-native WritingState or main GitHub article workspace; do not reconstruct stage from chat history, Notion, Drive, Library or remembered summaries.

## Assurance boundaries still OPEN

- current full GitHub-hosted owner CI: **OPEN** — latest Financial Actions jobs continue to return a job with `steps=null`; no test step executed, so this is neither code-test failure nor CI PASS;
- fresh-chat regression under the repaired main-only/TaskContract parity path: **OPEN**;
- live user acceptance/performance proving writing quality improvement: **OPEN**;
- provider-attested isolated independent review: **UNAVAILABLE**.

The next decisive product proof is another zero-memory fresh-chat article with no explicit mode/platform narrowing. It must persist DUAL + the three required outputs on main and mechanically refuse a 2-file terminal delivery.

`resume_epoch=4` and active lease `fw-e3dff9bf4dd547eb94fab8e15456c34f` are now owned by this new-chat takeover; superseded lease: `fw-4b398865ade44f1c896911a438f0c83b`.
