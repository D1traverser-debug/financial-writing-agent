# 金融文章写作｜Continuity Handoff

- task_id: `financial-writing:main`
- display_name_zh: **金融文章写作**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: FINANCIAL_WRITING_AGENT_RUNTIME
- current_stage: READY_FOR_NEW_OR_EXPLICIT_ARTICLE
- contract_version: CONTINUITY_V3_3

## Purpose
这是金融文章写作的长期 USER 工作入口，不代表任何一篇历史文章正在继续。

## Resume rule
- 用户说“继承：金融文章写作 / 写金融文章 / 财经文章”等，应先恢复本入口。
- 若用户明确点名某篇旧文章，再定位该文章的独立 task/checkpoint 并做 compatibility check。
- 若用户没有明确点名旧文章，必须按用户当前给出的主题、来源或目标建立新的文章 task；不得自动续跑历史文章。
- Runtime 只有在当前 capability/schema 兼容时才成为具体文章的执行真源；否则遵守当前 Financial Writing Agent 的合法 fallback/Standalone 规则。

## Current truth
旧 `AI 制药文章` 已退出默认恢复路径，不得再因旧 checkpoint 存在而自动恢复。

## Next action
恢复本入口后，直接接受用户当前的金融文章主题/来源并进入当前 Writing Agent 流程；如果用户明确点名旧文，再做 exact continuation。
