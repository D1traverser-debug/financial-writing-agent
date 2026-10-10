# Financial Writing Continuity Task Index

Universal protocol target: v3.7  
Owner domain: `FINANCIAL_WRITING`  
Adapter: `continuity/UNIVERSAL_PROTOCOL_ADAPTER.json`

## Default USER candidate

- `financial-writing:main` — **金融文章写作** — USER — ACTIVE — stage `READY_FOR_NEW_OR_EXPLICIT_ARTICLE` — resume `DEFAULT` — manifest: `continuity/tasks/financial-writing-main/TASK_MANIFEST.json` — checkpoint: `continuity/tasks/financial-writing-main/HANDOFF.md`

## Rules

- 裸“继承”只恢复 `financial-writing:main`。
- “写金融文章 / 金融文章写作”恢复当前 **Financial Writing Agent v0.7** 入口，不自动恢复已删除历史文章、旧 Site PoC 或旧 schema。
- GitHub `main` 是代码/规则权威；当前没有已安装的 Financial Writing Site Runtime 插件。
- 在任何 material stage / `next_action` 执行前，读取当前 `skills/financial-writing-agent/SKILL.md` 与 `continuity/EXECUTION_CAPABILITIES.json`，只对当前步骤所需能力做 session handshake；仓库声明本身不是当前聊天的执行证明。
- 新文章在当前 Site Runtime 完成生产等价验证前，只使用当前已验证的 owner runtime/standalone execution path；不得回退 legacy contract。
- 当前 task manifest / handoff 已按 Universal Continuity v3.7 原地 reconcile；同一聊天保持既有 `resume_epoch` 与 active lease。
- 新聊天 takeover 仍按当前 Universal Continuity 规则增加 `resume_epoch` 并淘汰旧 writer。
- 活跃持久任务的最终答复必须输出 v3.7 `进度提交` 回执；只有 owner authority 回读验证后才能报告 `COMMITTED`。
