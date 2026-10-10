# Financial Writing Continuity Task Index

Universal protocol target: v3.7  
Owner domain: `FINANCIAL_WRITING`  
Adapter: `continuity/UNIVERSAL_PROTOCOL_ADAPTER.json`

## Default USER candidates

- `financial-writing:main` — **金融文章写作** — USER — ACTIVE — stage `READY_FOR_NEW_OR_EXPLICIT_ARTICLE` — resume `DEFAULT` — manifest: `continuity/tasks/financial-writing-main/TASK_MANIFEST.json` — checkpoint: `continuity/tasks/financial-writing-main/HANDOFF.md`

## Rules

- 裸“继承”只恢复 `financial-writing:main`。
- “写金融文章 / 金融文章写作”恢复当前 v0.4 写作入口，不自动恢复已删除历史文章或旧 Site PoC。
- GitHub `main` 是代码/规则权威；当前没有已安装的 Site Runtime 插件。
- 新文章在新 v0.4 Site Runtime 发布并验证前，使用当前已验证的 standalone/runtime code path，不回退任何 legacy contract。
- 旧聊天/旧 task manifest 若仍记录 Universal Continuity v3.3，不要求用户迁移；由当前有效 task writer 在下一次 durable write 前按 `UNIVERSAL_PROTOCOL_ADAPTER.json` 原地 reconcile 到 v3.7，保持业务状态、resume_epoch 与 active lease 不变。
- 新聊天 takeover 仍按当前 Universal Continuity 规则增加 `resume_epoch` 并淘汰旧 writer。
- 活跃持久任务的每次最终答复必须输出当前 v3.7 `进度提交` 回执；只有 owner authority 回读验证后才能报告 `COMMITTED`。
