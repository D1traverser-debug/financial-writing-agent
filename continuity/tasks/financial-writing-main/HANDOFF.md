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
- writing_contract: `Financial Writing Agent v0.4`

## Purpose
这是金融文章写作的长期 USER 工作入口，不代表任何历史文章或旧 Site PoC 正在继续。

## Resume rule
- 用户说“继承：金融文章写作 / 写金融文章 / 财经文章”等，恢复本入口。
- 不恢复已删除历史文章任务，不恢复旧 16-tool Site Gate A2，不读取 legacy Site checkpoint 作为执行真源。
- GitHub `main` 是当前写作代码/规则权威。
- 当前没有已安装的 Financial Writing Site Runtime 插件；新 v0.4 Site 发布并通过 compatibility handshake 前，使用当前已验证 standalone/runtime code path。
- 禁止回退到任何 legacy `CHAT_TEXT`、visual/sticker、旧8项 Human Voice 或旧 v0.3 schema。

## v0.4 durable writing truth
- `FINANCE_DEEP` 执行 bounded audited research universe 下的 **MATERIAL_COMPLETE**；不使用“1–3 个核心矛盾”选择性删减财经正文。
- 对涉及个股/题材/价格表现的文章启用 **Market Explanation Completeness**，但不把“催化→概念→股票→资金→连板”硬编码成唯一链路。
- 市场解释必须区分：①经济受益/基本面兑现；②市场选择/价格形成。产业受益者、盈利受益者、情绪领涨者、流动性载体等角色不得默认等同。
- 有公司 universe 时，ResearchPackage 必须带 `market_explanation`；至少考虑两个竞争/替代机制，并保留 `why_this / why_not`、延续条件、衰竭/反转条件和无法识别的部分。
- 市场解释使用四级证据强度：`VERIFIED_FACT / SUPPORTED_MECHANISM / PLAUSIBLE_INTERPRETATION / UNRESOLVED`。涨停、连板、成交、资金流代理、概念标签或继续上涨只是待解释事实，不得反过来证明自身原因。
- `FINANCE_BROAD` 可围绕 1–3 个核心矛盾/信息差压缩，但保留下来的市场解释必须保留证据等级和关键反证。
- 写作不得提供可执行买卖建议、进出场时点、目标价、仓位、止盈止损等。
- 风格目标为 **Natural Authorial Prose**，不优化 AI detector；独立作者性审计为12项：template fingerprint、discourse variability、semantic progression、transition continuity、repetition control、rhythm naturalness、concrete evidence density、reader modeling、narrative flow、authorial specificity、uncertainty calibration、extreme-language control。
- Word 正式文章字号固定：一级标题 `24px = 18pt`，二级标题 `20px = 15pt`，正文 `18px = 13.5pt`；H3 暂维持 12pt。字号漂移为 Mechanical Hard Fail。
- 正式文章禁用表格；table 是 Mechanical Hard Fail。
- 多用真实逻辑序号：`一、二、三 → （1）（2）（3） → ①②③`。
- Financial Writing 不包含做图/封面/段落图/avatar/sticker/visual-manifest 工作流。
- 正文只交付 Word；QA = `WRITING_AUDIT_REPORT.docx` + 聊天 checklist/list，不在聊天贴正文。
- 独立 Hook Gate：跨行业财经点击力、当前微信搜索词证据、开头前三句、一级标题续读力、段落 forward pull、标题/开头兑现。
- 关键词、关键数据、关键判断句形成粗体 skim path；`总标题 + 一级标题 + 粗体` 能复原文章主线。
- 标题/大纲/正文/市场解释一旦变化，受影响的 Hook/Authorial Prose/Editorial/Word/Final PASS 自动失效。

## Legacy removal status
2026-10-09 已执行 hard cutover：
- ChatGPT 中旧 `Financial_Writing_Agent_Runtime` 插件已卸载；
- `financial_writing_agent/mcp_server.py` compatibility shim 已删除；
- `CHAT_TEXT` legacy delivery/artifact contract 已从核心模型与公开 MCP schema 删除；
- 历史 AI 制药 continuity task 已删除；
- 旧 16-tool Site Gate A2 continuity task 已删除。

历史 Git 提交记录仍由 Git 本身保留，但当前分支不再提供这些兼容入口。

## Next action
恢复本入口后，直接按 v0.4 当前规则接收用户主题/来源并执行新文章流程。需要 Site 化时，新建/部署纯 v0.4 Site，而不是修补旧 PoC。
