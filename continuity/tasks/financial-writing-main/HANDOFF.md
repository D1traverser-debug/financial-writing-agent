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

Financial Writing has one owner workflow and two bounded execution adapters.

Canonical business workflow authority is `financial_writing_agent/workflow_spec.py`:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`

Adapters may be stricter than this graph but may not invent broader business routes.

### OWNER_NATIVE

Use only when the current session actually has the Python/plugin owner runtime required by the next action.

- authoritative article state: versioned `WritingState`;
- SQLite mutations use `checkpoint_version` optimistic CAS and reject stale writers;
- crash-safe revision cleanup is replayed through shared `state_recovery.py` before business use;
- read-only recovery does not secretly advance the durable checkpoint;
- semantic PASS remains proof-bearing and cannot be supplied by chat prose;
- owner-native COMPLETE is controlled by the workflow/controller and completion gates.

### GITHUB_CHAT

This is the current bounded fallback when owner-native is unavailable. It is not free-form writing.

Use only when the current session has:
- model execution;
- GitHub owner read/write;
- an executable deterministic `financial_writing_agent/github_chat_guard.py` path;
- exact-stage web/document capabilities required by the current action.

Business state lives under `workspaces/articles/{task_id}`. Every material transition must:
1. fetch current `STATE.json` and bind its blob SHA;
2. execute the exact stage action;
3. persist the stage/review/publication artifact with stable Git identity;
4. let `github_chat_guard` validate the route and emit the action-bound self-attested receipt;
5. update `STATE.json` using the same prior blob SHA;
6. reread before treating the transition as durable.

Chat cannot hand-edit the stage, self-certify owner-native PASS, or relabel its result COMPLETE. Semantic review assurance is `CHAT_SELF_REVIEW`; normal terminal state is `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`.

## New task vs continuation

### Normal new article request

A normal request such as “写一篇关于 X 的财经文章” is **NEW_TASK**, not continuation of an old article.

After the Financial owner is selected:
1. read current main Skill / manifest / profile 10;
2. handshake only capabilities needed now;
3. choose OWNER_NATIVE or GITHUB_CHAT from observed session capabilities;
4. create new durable article state **before research or drafting**;
5. execute the canonical workflow.

Do not load old article stage/draft/next_action merely because old tasks exist. Long-term validated knowledge may be retrieved as reference evidence subject to current Research rules.

### Explicit continuation

Only an explicit request to continue/recover a prior article may resume old article state. Resolve the exact article through owner-native WritingState or its GitHub article workspace. Do not reconstruct execution state from chat history, Notion, Drive, Library, or remembered summaries.

## External knowledge boundary

- GitHub `main` is Financial rule/engineering authority.
- Owner-native WritingState or guard-validated GitHub article workspace is per-article execution authority.
- Google Drive, Notion, ChatGPT Library, StockBase, ArticleBase, EvidenceCache and historical drafts are reference/bootstrap/evidence surfaces only unless the current owner contract explicitly promotes a stable ref for the current action.
- External sources may contribute research facts, prior article learning or evidence, but may not restore an old Financial Controller, task pointer, stage, gate PASS, or obsolete execution mode.

## Current completed rebuild layers

- GITHUB_CHAT is a first-class bounded owner adapter; free-form publishable fallback is forbidden.
- GitHub-chat stage transitions are guarded by deterministic code and exact Git state identity.
- Phase 1 established one canonical workflow kernel shared by execution adapters and removed duplicate route truth; it also repaired the owner-native `DRAFT → DRAFT` revision mismatch.
- Phase 2 added owner-native checkpoint CAS, shared crash recovery, paged continuation discovery, single-snapshot MCP summaries and stale-conflict fail-closed behavior.
- Material corrective/negative feedback creates durable system-impact review debt rather than disappearing into local prose revision.

## Assurance boundaries still OPEN

Do not collapse these evidence classes:

- full current GitHub-hosted owner CI: **OPEN** — recent jobs were not allocated a runner and executed no steps;
- one real post-rebuild article trajectory through the current end-to-end workflow: **OPEN**;
- post-rebuild live user acceptance/performance evidence proving better writing quality: **OPEN**;
- provider-attested isolated independent review: **UNAVAILABLE**.

Targeted/structural/fault evidence for repaired components does not prove those stronger layers.

## Fresh-chat routing boundary

Owner correctness is separate from product/account discovery. GitHub/Library files are not automatic event listeners. A completely new ChatGPT conversation can execute this system correctly **after it is routed to the Financial owner**, but zero-prompt automatic repo discovery for every generic new-chat article request requires an always-on product/account routing hook and must not be claimed from repository files alone.

`resume_epoch=3` and active lease `fw-4b398865ade44f1c896911a438f0c83b` were established by this new-chat takeover, superseding `fw-5636d680328b40c5ab4b5029441e3489`.
