# Financial Writing Continuity Task Index

Universal protocol target: v3.7  
Owner domain: `FINANCIAL_WRITING`  
Adapter: `continuity/UNIVERSAL_PROTOCOL_ADAPTER.json`

## Default USER candidate

- `financial-writing:main` — **金融文章写作** — USER — ACTIVE — stage `READY_FOR_NEW_OR_EXPLICIT_ARTICLE` — resume `DEFAULT` — manifest: `continuity/tasks/financial-writing-main/TASK_MANIFEST.json` — checkpoint: `continuity/tasks/financial-writing-main/HANDOFF.md`

## Rules

- 裸“继承”只把 `financial-writing:main` 作为 Financial owner 的默认 USER candidate；具体文章仍必须按当前文章状态解析。
- 普通“写金融文章 / 写财经文章 / 投研文章”是 **NEW_TASK intent**：进入当前 Financial owner，但不自动恢复任何历史文章 stage / draft / next_action。
- GitHub `main` 是代码/规则权威。当前用户生产方式允许 GitHub 挂载 + GPT chat；Site/MCP 部署不是 GITHUB_CHAT 前提。
- 在任何 material action 前，读取当前 `skills/financial-writing-agent/SKILL.md`、`continuity/AGENT_MANIFEST.json` 与 `continuity/EXECUTION_CAPABILITIES.json` profile 10，只对当前步骤所需能力做 session handshake；仓库声明不是当前聊天的执行证明。
- owner-native Python/plugin 实际可用时走版本化 WritingState；不可用时，只有当前聊天同时具备模型执行、GitHub owner 读写和可执行 deterministic `github_chat_guard.py`（以及当前阶段需要的 web/document 能力）才可选择 GITHUB_CHAT。
- 缺少 deterministic guard 时必须阻塞对应 transition；不得退化成自由写作。
- GITHUB_CHAT 业务状态位于 `workspaces/articles/{task_id}`。每个 material transition 必须绑定 prior STATE blob SHA、action identity 与输出 refs，由 guard 接受后写入并回读。
- GITHUB_CHAT Research/Editorial/Final review 只能是 `CHAT_SELF_REVIEW`；可 REVISE/FAIL，不得冒充 owner-native semantic PASS、`INDEPENDENT_EXECUTOR` 或 provider-attested isolation。正常终态是 `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`。
- owner-native Hosted/MCP 路径若可用，语义 PASS 继续只通过 owner-runtime proof-bearing path；缺少其 SDK/model runtime 时不得用聊天自证替代。
- Financial task manifest / handoff 已对齐 profile 10、canonical workflow kernel 与 Phase-2 checkpoint-CAS/recovery；同一 task maintenance 保持既有 `resume_epoch` 与 active lease。
- 新聊天 takeover 仍按 Universal Continuity v3.7 增加 `resume_epoch` 并淘汰旧 writer；但普通 NEW_TASK 不需要先“继承”旧文章。
- GitHub/Library/Notion/Drive 都不是自动事件监听器。**是否能在完全全新的 ChatGPT 对话中仅凭普通财经写作请求自动发现本 repo，属于产品/账号级 routing capability，必须用真实 fresh-chat product trace 证明；不能由本索引自证。**
- 活跃持久任务最终答复输出 v3.7 `进度提交`；只有 owner authority 回读验证后才能报告 `COMMITTED`。
