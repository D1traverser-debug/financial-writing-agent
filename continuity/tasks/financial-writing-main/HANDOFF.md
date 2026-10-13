# 金融文章写作｜Continuity Handoff

- task_id: `financial-writing:main`
- display_name_zh: **金融文章写作**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: `FINANCIAL_WRITING_AGENT_RUNTIME`
- current_stage: `ACTIVE_ARTICLE_FINAL_AUDIT`
- continuity_contract: `CONTINUITY_V3_7`
- owner rule authority: `D1traverser-debug/financial-writing-agent@main`
- execution capability profile: **11**

## Active article checkpoint — 2026-10-13

当前正在执行的具体文章不是“等待新任务”，而是：

- article task_id: `ice-snow-economy-20261013`
- topic: **冰雪经济**
- authoritative state: `main/workspaces/articles/ice-snow-economy-20261013/STATE.json`
- article status: `IN_PROGRESS`
- current article stage: `FINAL_AUDIT`
- distribution mode: `DUAL`
- delivery channel: `WORD_FILE_ONLY`
- review assurance: `CHAT_SELF_REVIEW`

已经持久化并通过的阶段：

`RESEARCH → RESEARCH_AUDIT(PASS) → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT(PASS) → DELIVERY → MECHANICAL_AUDIT(PASS) → FINAL_AUDIT(current)`

当前 canonical 两份文章 Word 已经在 article STATE 的 `delivery_artifacts` 中登记，恢复时必须按这些身份对账，不能用新窗口里的临时重建件替代：

- `FINANCE_DEEP_DOCX` — file_name `ice_snow_economy_deep.docx` — SHA-256 `e863a831a1659b993ee9b46f578d9eb8c70f56ecc1de1b74f1d65a10fdb68922`
- `FINANCE_BROAD_DOCX` — file_name `ice_snow_economy_broad.docx` — SHA-256 `10dcfb53e46d629b669045b3f91b1f90169ed47ff4cd168745209ee17ff34895`

机械审计已经 PASS，durable refs：

- `stages/DELIVERY.md` blob `e92543eb28eb12844339fe4938cde3af34388687`
- `reviews/MECHANICAL_AUDIT.md` blob `d2e42d6cd760c99b2caeb8817942120456fe6477`

**尚未完成的唯一业务闭环：**

1. 在 `FINAL_AUDIT` 生成或重新生成 `AUDIT_DOCX`；
2. 对 AUDIT_DOCX 做机械/渲染验证；
3. 持久化 `reviews/FINAL_AUDIT.md`；
4. 用当前 `financial_writing_agent/owner_guard.py` 对 `AUDIT_DOCX + FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX` 做完整三输出 reconciliation；
5. FINAL_AUDIT 以真实 `CHAT_SELF_REVIEW=PASS` 终态化为 `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`；
6. 回读 `STATE.json` 与 final audit 后才能报告 `COMMITTED`。

上一个聊天中曾生成并渲染过审计 Word 的瞬时本地副本，但它**没有成为 durable authority**。新窗口不得凭聊天记忆、旧容器路径或旧本地文件认定 AUDIT_DOCX 已完成；应从上述 authoritative FINAL_AUDIT 状态重新验证/生成。

## Exact resume procedure for a new chat

用户下一次在新窗口说“继承”时：

1. Universal v3.7 Bare CONTINUE discovery 选择 `financial-writing:main` 后，先读本 manifest + 本 HANDOFF；
2. 报告“继承前进度”：active article=`ice-snow-economy-20261013`，stage=`FINAL_AUDIT`，只剩审计 Word 和终态闭环；
3. 因为是**新聊天 takeover**，先按 Universal adapter 增加 `resume_epoch`（当前为 5，因此下一 writer 应成为 6）并签发新 lease，supersede `fw-fbadb6dbc3544d048325c9778cd0df6a`；
4. 回读 `main/workspaces/articles/ice-snow-economy-20261013/STATE.json`，以它而不是本 HANDOFF 的复制信息作为具体业务 authority；
5. 如果 article STATE 已被其他 writer 推进，服从更新后的 article STATE，不要回退到这里；
6. 仅加载 FINAL_AUDIT 所需 Skill / owner execution / capability profile / audit+delivery rules，继续真实 next_action；
7. 不重新研究、不重新写正文、不创建重复 article task，除非 authoritative state 明确要求 revision。

## Current architecture

Financial Writing has **one BUSINESS owner, one canonical TaskContract, one canonical workflow, one durable article-state authority and one ChatGPT product path**.

`ChatGPT request → current GitHub main Financial owner → main/workspaces/articles/{task_id} → canonical stages → Word delivery`

Canonical workflow:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`

Canonical mutation guard: `financial_writing_agent/owner_guard.py`.  
Canonical BLOCKED/system-impact lifecycle: `financial_writing_agent/owner_lifecycle.py`.

New and resumed business state lives only at `main/workspaces/articles/{task_id}`. No per-article branch, chat memory, SQLite owner store, plugin-local store, historical branch or eval artifact may become fallback authority.

Default TaskContract is `DUAL + WORD_FILE_ONLY + FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX`. A single-mode override requires exact original user-prompt evidence.

## Assurance boundaries still OPEN

- GitHub-hosted full owner CI: `OPEN_RUNNER_NOT_EXECUTED`;
- fresh-chat single-owner live trajectory regression: `OPEN`;
- final-response owner admission / physical GitHub-write interception: `OPEN at shared Universal/product control plane`;
- non-forgeable Universal lease/resume_epoch fencing at every Financial mutation: `OPEN`;
- provider-attested isolated independent review: `UNAVAILABLE`.

Current `resume_epoch=5`; active lease=`fw-fbadb6dbc3544d048325c9778cd0df6a`. Same-chat checkpointing does not invent a new epoch. The next fresh-chat takeover must advance the epoch and replace this lease before any article mutation.
