# 金融文章写作｜Continuity Handoff

- task_id: `financial-writing:main`
- display_name_zh: **金融文章写作**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: FINANCIAL_WRITING_AGENT_RUNTIME
- current_stage: READY_FOR_NEW_OR_EXPLICIT_ARTICLE
- continuity_contract: CONTINUITY_V3_3
- writing_rule_authority: `D1traverser-debug/financial-writing-agent@main`
- writing_contract: `Financial Writing Agent v0.3`

## Purpose
这是金融文章写作的长期 USER 工作入口，不代表任何一篇历史文章正在继续。

## Resume rule
- 用户说“继承：金融文章写作 / 写金融文章 / 财经文章”等，应先恢复本入口。
- 若用户明确点名某篇旧文章，再定位该文章的独立 task/checkpoint 并做 compatibility check。
- 若用户没有明确点名旧文章，必须按用户当前给出的主题、来源或目标建立新的文章 task；不得自动续跑历史文章。
- GitHub `main` 是当前写作代码/规则权威。
- Site Runtime 只有在 capability/schema 与当前 v0.3 contract 兼容时才成为具体文章的执行真源；否则必须 fail closed / 使用当前合法 fallback，不得把旧 Runtime checkpoint 当成 v0.3 执行状态。

## v0.3 durable writing truth
2026-10-09 用户完成一轮持久规则升级：
- `FINANCE_DEEP` 改为 bounded research universe 下的 **MATERIAL_COMPLETE**：不再用“1–3 个核心矛盾”选择性删减财经正文；所有会 materially 改变财经判断的重要分支必须覆盖。
- `FINANCE_BROAD` 是引流/广分发版本，允许围绕 1–3 个核心矛盾/信息差选择性压缩，但保留结论所需完整证据链。
- 正式文章 **禁用表格**；table 是 mechanical Hard Fail。
- 更频繁使用 `一、二、三 → （1）（2）（3） → ①②③` 做真实逻辑分层。
- Financial Writing **删除全部做图/封面/段落图/avatar/sticker/visual-manifest 工作流**；图片任务属于独立视觉入口。
- 文章正文 **只交付 Word**；QA 同时交付 `WRITING_AUDIT_REPORT.docx` + 聊天窗口 checklist/list，不在聊天粘贴文章正文。
- 新增独立 `Hook Gate`：跨行业财经点击力、当前微信搜索词证据、开头前三句、一级标题续读力、段落 forward pull、标题/开头兑现。
- 新增独立 `Human Voice Gate`：template fingerprint、逻辑衔接、重复控制、节奏、交流感、娓娓道来、作者判断人格、极端措辞。
- 关键词、关键数据、关键判断句形成显式粗体 skim path；`总标题 + 一级标题 + 粗体` 必须能复原文章主线。
- 读者当前画像偏 45+ / 55+；在不降低分析深度的前提下加强编号、清晰指代、段落可读性和扫读骨架。
- Word 正文默认字号调整为约 13.5pt；用户后续可显式修改。
- 终段不得机械复述全文，应继续提供新信息或闭合前文问题/因果链。
- 标题/大纲/正文一旦变化，受影响的 Hook/Human Voice/Editorial/Word/Final PASS 自动失效，禁止沿用旧 QA。

## Current Runtime compatibility boundary
当前聊天实际连接到的 `Financial_Writing_Agent_Runtime` 仍是旧 Private Site compatibility PoC：
- 仍暴露 `WECHAT_STICKER_POST` / `submit_visual_package`；
- 没有独立 `submit_hook_audit`；
- 因此与 v0.3 capability/schema **不兼容**。

在该 Site 重新部署并通过 compatibility handshake 前，新 v0.3 文章不得把这个旧 Site Runtime 当作执行真源。

## Historical task boundary
旧 `AI 制药文章` 已退出默认恢复路径，不得再因旧 Runtime checkpoint 显示 `IN_PROGRESS` 而自动恢复。

## Next action
恢复本入口后：
1. 先确认可用 Runtime 是否满足 v0.3 capability/schema；
2. 若兼容，按 v0.3 Runtime 建立新文章 task；
3. 若不兼容，遵守 fail-closed/合法 fallback 边界，不得回退旧视觉/贴图/旧审计语义；
4. 接受用户当前主题/来源进入新文章流程；用户明确点名旧文时才做 exact continuation。
