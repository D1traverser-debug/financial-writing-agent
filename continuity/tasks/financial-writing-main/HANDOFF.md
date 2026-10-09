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
这是金融文章写作的长期 USER 工作入口，不代表任何一篇历史文章正在继续。

## Resume rule
- 用户说“继承：金融文章写作 / 写金融文章 / 财经文章”等，应先恢复本入口。
- 若用户明确点名某篇旧文章，再定位该文章的独立 task/checkpoint 并做 compatibility check。
- 若用户没有明确点名旧文章，必须按用户当前给出的主题、来源或目标建立新的文章 task；不得自动续跑历史文章。
- GitHub `main` 是当前写作代码/规则权威。
- Site Runtime 只有在 capability/schema 与当前 v0.4 contract 兼容时才成为具体文章的执行真源；否则 fail closed，不得把旧 Runtime checkpoint 当成 v0.4 执行状态。

## v0.4 durable writing truth
2026-10-09 在 v0.3 基础上继续完成一轮研究驱动升级：
- `FINANCE_DEEP` 继续执行 bounded audited research universe 下的 **MATERIAL_COMPLETE**；不使用“1–3 个核心矛盾”选择性删减财经正文。
- 对涉及个股/题材/价格表现的文章，完整性新增 **Market Explanation Completeness**，但不把用户经验中的“催化→概念→股票→资金→连板”硬编码成唯一链路。
- 市场解释必须区分：①经济受益/基本面兑现；②市场选择/价格形成。产业受益者、盈利受益者、情绪领涨者、流动性载体等角色不得默认等同。
- 有公司 universe 时，ResearchPackage 必须带 `market_explanation`；至少考虑两个竞争/替代机制，并保留 `why_this / why_not`、延续条件、衰竭/反转条件和无法识别的部分。
- 市场解释使用四级证据强度：`VERIFIED_FACT / SUPPORTED_MECHANISM / PLAUSIBLE_INTERPRETATION / UNRESOLVED`。涨停、连板、成交、资金流代理、概念标签或继续上涨只是待解释事实，不得反过来证明自身原因。
- `FINANCE_BROAD` 可围绕 1–3 个核心矛盾/信息差压缩，但保留下来的市场解释必须保留证据等级和关键反证。
- 写作仍不得提供可执行买卖建议、进出场时点、目标价、仓位、止盈止损等。
- “去AI味/活人感/娓娓道来/交流感”不再作为模糊目标；升级为 **Natural Authorial Prose**：不优化 AI detector，而审计真实写作质量。
- 独立作者性审计从8项升级到12项：template fingerprint、discourse variability、semantic progression、transition continuity、repetition control、rhythm naturalness、concrete evidence density、reader modeling、narrative flow、authorial specificity、uncertainty calibration、extreme-language control。
- Word 正式文章字号固定为用户指定像素的 Word 等价值：一级标题 `24px = 18pt`，二级标题 `20px = 15pt`，正文 `18px = 13.5pt`；H3 暂维持 12pt。字号漂移为 Mechanical Hard Fail。

## v0.3 rules still active
- 正式文章禁用表格；table 是 mechanical Hard Fail。
- 多用真实逻辑序号：`一、二、三 → （1）（2）（3） → ①②③`，不以“首先/其次/最后”冒充逻辑。
- Financial Writing 删除全部做图/封面/段落图/avatar/sticker/visual-manifest 工作流。
- 正文只交付 Word；QA = `WRITING_AUDIT_REPORT.docx` + 聊天 checklist/list，不在聊天贴正文。
- 独立 Hook Gate：跨行业财经点击力、当前微信搜索词证据、开头前三句、一级标题续读力、段落 forward pull、标题/开头兑现。
- 关键词、关键数据、关键判断句形成粗体 skim path；`总标题 + 一级标题 + 粗体` 能复原文章主线。
- 读者画像偏 45+/55+；在不降低分析深度前提下加强编号、清晰指代、段落可读性和扫读骨架。
- 终段不做机械复述，仍需提供新信息、验证/证伪条件或闭合问题链。
- 标题/大纲/正文/市场解释一旦变化，受影响的 Hook/Authorial Prose/Editorial/Word/Final PASS 自动失效。

## Current Runtime compatibility boundary
当前聊天实际连接到的 `Financial_Writing_Agent_Runtime` 仍是旧 Private Site compatibility PoC：
- 仍暴露 `WECHAT_STICKER_POST` / `submit_visual_package`；
- 没有当前独立 `submit_hook_audit` capability；
- 更没有 v0.4 `MarketExplanationMap`、四级 causal-confidence schema、12项 Authorial Prose rubric 和精确字号合同；
- 因此与 v0.4 capability/schema **INCOMPATIBLE**。

在 Site 重新部署并通过 v0.4 compatibility handshake 前，新文章不得把该旧 Site Runtime 当执行真源。

## Historical task boundary
旧 `AI 制药文章` 已退出默认恢复路径，不得因旧 Runtime checkpoint 显示 `IN_PROGRESS` 而自动恢复。

## Next action
恢复本入口后：
1. 先检查可用 Runtime 是否满足 v0.4 capability/schema；
2. 若兼容，按 v0.4 Runtime 建立新文章 task；
3. 若不兼容，遵守 fail-closed/当前合法 fallback，不得回退旧视觉、旧市场解释或旧8项风格审计；
4. 接受用户当前主题/来源进入新文章流程；用户明确点名旧文时才做 exact continuation。
