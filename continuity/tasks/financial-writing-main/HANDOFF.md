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
- execution capability profile: **11**

## Current architecture

Financial Writing has **one BUSINESS owner, one canonical TaskContract, one canonical workflow, one durable article-state authority and one ChatGPT product path**.

Product path:

`ChatGPT request → current GitHub main Financial owner → main/workspaces/articles/{task_id} → canonical stages → Word delivery`

There is no longer a product/runtime decision between `OWNER_NATIVE` and `GITHUB_CHAT`. Model, web, Python, document, plugin or MCP facilities are capability providers inside the same owner trajectory when actually available. They may not create an alternate article-state authority or different terminal semantics.

Canonical workflow:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`

Canonical execution contract: `continuity/FINANCIAL_OWNER_EXECUTION.json`.

The current deterministic guard implementation remains `financial_writing_agent/github_chat_guard.py` for code compatibility. The historical filename and existing `STATE.json.execution_mode=GITHUB_CHAT` token are **legacy internal identifiers only**; neither is allowed to select a route. A future rename requires explicit state migration and regression proof rather than an implicit compatibility fork.

## Business state and output contract

New and resumed Financial business state lives only at:

`main/workspaces/articles/{task_id}`

No per-article branch, chat memory, SQLite owner store, Site-local store or plugin-local store may become a fallback authority.

Default TaskContract:
- distribution mode: `DUAL`;
- delivery channel: `WORD_FILE_ONLY`;
- required outputs: `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX`.

A single-mode override requires `USER_EXPLICIT_OVERRIDE` plus an exact substring from the original user prompt in the INIT receipt.

Every material mutation must read the latest main `STATE.json`, bind its blob SHA, persist exact stage/review/publication evidence, run the deterministic owner guard, write with compare-and-swap and reread the authoritative state/artifacts before `COMMITTED`.

## Legacy quarantine

Historical `OWNER_NATIVE`, alternate SQLite `WritingState`, old plugin/MCP task-state flows, `GITHUB_CHAT` as a fallback-adapter concept, old `article/*` refs and maintenance branches are **not current business authority**.

They may remain in Git history or historical evals as evidence. They must not be loaded as startup authority, used to route a new task, used to recover a current task or activated merely because a capability is missing.

Missing capability blocks only the affected stage. It never authorizes free-form writing or an old fallback mechanism.

## Why this convergence exists

The live recurrence on 2026-10-13 proved that maintaining two internal execution adapters increased ambiguity without matching the user's actual operating model. The user consistently uses ChatGPT while the Financial system/rules/state live in GitHub. The architecture therefore converges on that real product boundary instead of maintaining parallel state machines and certification semantics.

The previous dual-adapter repair PR #20 was closed unmerged. It is historical evidence only and must not be used as implementation authority.

## New task vs continuation

A normal request such as “写一篇关于 X 的财经文章” is **NEW_TASK**. Do not auto-resume an old article.

For a new task:
1. read current main Skill / manifest / owner execution contract / capability profile;
2. create main article `STATE.json` before research or drafting;
3. handshake only the exact-stage capabilities needed now;
4. execute the canonical workflow through the same owner state trajectory;
5. preserve canonical TaskContract defaults unless exact user-prompt override evidence exists;
6. reconcile required outputs mechanically before delivery/terminal claims.

Only explicit continuation may resume an old article. Resolve the exact main article workspace; do not reconstruct stage from chat history, historical branches, evals, Notion, Drive, Library or remembered summaries.

## Assurance boundaries still OPEN

- current full GitHub-hosted owner CI: **OPEN** — Financial Actions currently creates a failed job shell with no executed steps, so current-head code is neither CI PASS nor a demonstrated code-test failure;
- final-response owner admission / physical GitHub-write interception: **OPEN at the shared Universal/product control plane**;
- non-forgeable Universal lease/resume_epoch fencing at every Financial mutation: **OPEN**;
- fresh-chat single-owner trajectory regression: **OPEN**;
- provider-attested isolated independent review: **UNAVAILABLE**.

`resume_epoch=4`; active lease remains `fw-e3dff9bf4dd547eb94fab8e15456c34f` for the current durable Financial workspace. Same-chat maintenance does not invent a new takeover epoch.