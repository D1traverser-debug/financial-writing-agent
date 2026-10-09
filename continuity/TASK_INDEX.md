# Financial Writing Continuity Task Index

Contract: Universal Continuity v3.3  
Owner domain: `FINANCIAL_WRITING`

## Default USER candidates

- `financial-writing:main` — **金融文章写作** — USER — ACTIVE — stage `READY_FOR_NEW_OR_EXPLICIT_ARTICLE` — resume `DEFAULT` — manifest: `continuity/tasks/financial-writing-main/TASK_MANIFEST.json` — checkpoint: `continuity/tasks/financial-writing-main/HANDOFF.md`

## Non-default / historical

- `052804dc-f66a-441d-8875-c7973366b072` — **AI制药文章（历史）** — USER — ARCHIVED — resume `HIDDEN` — checkpoint `continuity/tasks/ai-pharma-writing/HANDOFF.md`
- `financial-writing-site-runtime:gate-a2` — **金融写作 Site Runtime：Gate A2** — SYSTEM_INFRA — ACTIVE — resume `EXPLICIT_ONLY` — checkpoint `continuity/tasks/site-runtime-gate-a2/HANDOFF.md`

## Rules

- 裸“继承”只能从 `Default USER candidates` 读取候选。
- “写金融文章 / 金融文章写作”恢复 `financial-writing:main`，不得自动续跑任意历史文章。
- 只有用户明确点名旧文章或 exact task_id 时，才定位历史 article task 并执行 current-contract compatibility check。
- Site Runtime Gate A2 属于系统工程维护，只有显式点名时恢复，不得污染普通业务候选。
- 具体文章 checkpoint 在 compatible Runtime 存在时服从更强 Runtime authority；否则按当前合法 Standalone/fallback 规则执行。
- New-chat takeover retires the previous chat for the same task.
