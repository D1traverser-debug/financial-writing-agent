# Financial Writing Continuity Task Index

Universal protocol target: v3.7  
Owner domain: `FINANCIAL_WRITING`  
Adapter: `continuity/UNIVERSAL_PROTOCOL_ADAPTER.json`

## Default USER candidate

- `financial-writing:main` — **金融文章写作** — USER — ACTIVE — stage `READY_FOR_NEW_OR_EXPLICIT_ARTICLE` — resume `DEFAULT` — manifest: `continuity/tasks/financial-writing-main/TASK_MANIFEST.json` — checkpoint: `continuity/tasks/financial-writing-main/HANDOFF.md`

## Rules

- 裸“继承”只恢复 `financial-writing:main`。
- “写金融文章 / 金融文章写作”恢复当前 **Financial Writing Agent v0.8** 入口，不自动恢复已删除历史文章、旧 Site PoC 或旧 schema。
- GitHub `main` 是代码/规则权威。当前用户生产方式是 GitHub 挂载 + GPT chat；Site/MCP 部署不是当前使用前提。
- 在任何 material stage / `next_action` 执行前，读取当前 `skills/financial-writing-agent/SKILL.md` 与 `continuity/EXECUTION_CAPABILITIES.json`，只对当前步骤所需能力做 session handshake；仓库声明本身不是当前聊天的执行证明。
- owner-native Python/plugin 可用时走其状态机。不可用但当前聊天具备模型 + GitHub owner 读写时，必须显式选择 `continuity/GITHUB_CHAT_EXECUTION.json` 的 CHAT_BRIDGED 路径；不得退化为自由写作。
- GITHUB_CHAT 的业务状态位于 `workspaces/articles/{task_id}`，每个 material stage 必须写 GitHub checkpoint 并回读。聊天记忆不是业务状态权威。
- GITHUB_CHAT 的 Research/Editorial/Final review 只能记为 `CHAT_SELF_REVIEW`；可以 REVISE/FAIL，但不得冒充 owner-native semantic PASS、`INDEPENDENT_EXECUTOR` 或 provider-attested isolation。正常终态是 `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`。
- owner-native Hosted/MCP 路径若未来启用，语义 PASS 继续只通过 `run_semantic_audit_stage`；缺少其 SDK/model runtime 时，不得用聊天自证替代 owner-native PASS。
- 当前 task manifest / handoff 已按 Universal Continuity v3.7 原地 reconcile；同一聊天保持既有 `resume_epoch` 与 active lease。
- 新聊天 takeover 仍按当前 Universal Continuity 规则增加 `resume_epoch` 并淘汰旧 writer。
- 活跃持久任务的最终答复必须输出 v3.7 `进度提交` 回执；只有 owner authority 回读验证后才能报告 `COMMITTED`。
