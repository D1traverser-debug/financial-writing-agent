# Financial Writing Continuity Task Index

Contract: Universal Continuity v3.3  
Owner domain: `FINANCIAL_WRITING`

## Default USER candidates

- `financial-writing:main` — **金融文章写作** — USER — ACTIVE — stage `READY_FOR_NEW_OR_EXPLICIT_ARTICLE` — resume `DEFAULT` — manifest: `continuity/tasks/financial-writing-main/TASK_MANIFEST.json` — checkpoint: `continuity/tasks/financial-writing-main/HANDOFF.md`

## Rules

- 裸“继承”只恢复 `financial-writing:main`。
- “写金融文章 / 金融文章写作”恢复当前 v0.4 写作入口，不自动恢复已删除历史文章或旧 Site PoC。
- GitHub `main` 是代码/规则权威；当前没有已安装的 Site Runtime 插件。
- 新文章在新 v0.4 Site Runtime 发布并验证前，使用当前已验证的 standalone/runtime code path，不回退任何 legacy contract。
- New-chat takeover retires the previous chat for the same task.
