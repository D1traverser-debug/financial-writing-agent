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
- writing_contract: `Financial Writing Agent v0.5`

## Purpose
这是金融文章写作的长期 USER 工作入口，不代表任何历史文章或旧 Site PoC 正在继续。

## Resume rule
- 用户说“继承：金融文章写作 / 写金融文章 / 财经文章”等，恢复本入口。
- GitHub `main` 是当前写作代码/规则权威。
- 当前没有已安装的 Financial Writing Site Runtime 插件；需要 Site 时只能按 v0.5 当前合同重新部署并通过 compatibility handshake。
- 禁止恢复 legacy `CHAT_TEXT`、visual/sticker、旧 Site PoC、v0.4 headline schema、旧12项 Human Voice rubric 或更早 schema。

## v0.5 durable writing truth
### 1. 财经解释
- `FINANCE_DEEP` 在 bounded audited research universe 内执行 **MATERIAL_COMPLETE**，不使用“1–3个核心矛盾”选择性删减重要财经分支。
- `FINANCE_BROAD` 可围绕1–3个核心矛盾/信息差压缩，但保留结论的证据链、重要反证和不确定性边界。
- 涉及个股/题材/价格表现时启用 **Market Explanation Completeness**；区分①经济受益/基本面兑现，②市场选择/价格形成。
- 不把“催化→概念→股票→资金→连板”写死为唯一链路；至少考虑竞争/替代机制，并保留 `why_this / why_not`、延续条件、衰竭/反转条件和无法识别的部分。
- 市场解释使用 `VERIFIED_FACT / SUPPORTED_MECHANISM / PLAUSIBLE_INTERPRETATION / UNRESOLVED` 四级证据强度。价格表现是待解释事实，不是原因的自证。

### 2. Reader Funnel / Hook
把点击率、标题钩子、读者画像、前三句、一级标题/段落续读和完读率视为同一漏斗：
`qualified impression → click → first-screen retention → continued reading → completion → promised insight delivered`。

独立审计：
1. audience-promise fit；
2. headline information value；
3. curiosity/concreteness balance；
4. 当前微信搜索可发现性及证据；
5. 开头前三句留存；
6. H1 + 段落 transition 的 continuation flow；
7. completion payoff；
8. title/opening payoff。

“跨行业财经点击力”不是所有标题的硬条件。它是 `FINANCE_BROAD` 等场景可用的扩圈策略；`FINANCE_DEEP` 优先保证合格目标财经读者、真实信息价值和承诺兑现。标题优化目标是 qualified expected value，而不是凭空想象的最大CTR。

正式模式每版仍生成8–12个真实不同的候选标题。候选记录 target reader、点击理由、finance relevance、information gap、promised payoff、cognitive load、当前微信搜索词/证据；broader-finance relevance 可为空。问句标题不默认更优。

读者45岁较多、55+占比较高只作为可读性 prior，不推断金融理解能力。设备价格等线索属于弱 prior；真实账号点击/搜索/完读/反馈数据高于泛化人口学经验。

### 3. Natural Authorial Prose / Writing DNA
“去AI味 / 活人感 / 娓娓道来 / 交流感”属于重叠症状，不再作为四套并列目标。统一目标是有证据、有作者选择、有读者意识的 **Natural Authorial Prose**。

独立作者性审计收敛为9项：
1. fidelity_and_responsibility；
2. semantic_contribution；
3. argument_progression；
4. reader_calibration；
5. authorial_selectivity；
6. evidence_specificity；
7. structural_rhythm_naturalness；
8. template_redundancy_control；
9. uncertainty_rhetoric_calibration。

Humanization 不能通过口语、错别字、随机短句、假亲密、装饰性比喻或 AI-detector evasion 完成。任何改写必须保护事实、数字、日期、出处关系、作者立场、责任主体、确定性等级和重要限定条件。

### 4. Writing DNA 学习机制
持久学习按证据分级：
- `DIRECT`：用户明确的长期要求，可直接进入持久规则；
- `REPEATED_PATTERN`：多个独立文章中重复被接受的修改，可晋升持久规则候选；
- `USER_CORPUS`：足够广的用户已接受全文样本中稳定出现的模式，作为风格证据；
- `ONE_OFF_CANDIDATE`：一次修改或一篇成功文章，只记录候选，不全局写死；
- `EXTERNAL_BENCHMARK`：外部 skill / 优秀写作 / 研究只吸收底层原则，不成为 authority，不复制个人标志性表达。

优先学习 AI原稿→用户最终稿的差异：信息顺序、重点、确定性、句段形状、术语、证据处理和读者关系，而不是只统计删掉了哪些词。

### 5. 文章与Word硬规则
- 一级标题 `24px = 18pt`；二级标题 `20px = 15pt`；正文 `18px = 13.5pt`；H3 暂维持12pt。
- 正式文章禁用表格；table 是 Mechanical Hard Fail。
- 多用真实逻辑序号：`一、二、三 → （1）（2）（3） → ①②③`。
- Financial Writing 不包含做图/封面/段落图/avatar/sticker/visual-manifest。
- 关键词、关键数据、关键判断句形成粗体 skim path；`总标题 + 一级标题 + 粗体` 能复原文章主线。
- 正文只交付 Word；QA = `WRITING_AUDIT_REPORT.docx` + 聊天 checklist/list，不在聊天贴正文。
- 不提供可执行买卖建议、进出场时点、目标价、仓位、止盈止损等。
- 标题/大纲/正文/市场解释变化后，受影响的 Reader Funnel / Authorial Prose / Editorial / Word / Final PASS 自动失效并重审。

## External-skill learning policy
本轮已研究 `writing-dna-skill`、`writing-style-skill`、`humanizer-zh`、`humanizer`、`shuorenhua`、`nuwa-skill`、`distilly`、`wewrite`、`writing-agent`、`oh-story` 等代表性方法。结论不是叠加安装所有 humanizer，而是拆成能力原语：Writing DNA蒸馏、原稿→终稿差异学习、事实/立场/责任保真、结构性模板识别、读者漏斗、经验分级晋升、架构/写手/编辑分离。外部方法只作为候选知识，最终服从用户长期证据和当前文章效果。

## Legacy removal status
已执行 hard cutover：旧 Financial Writing Site插件、`mcp_server.py` compatibility shim、`CHAT_TEXT`、visual/sticker资源与旧 continuity 任务均已删除。历史Git提交本身保留，但当前 `main` 不提供这些兼容入口。

## Next action
恢复本入口后，直接按 v0.5 当前规则接收用户主题/来源并执行新文章流程。需要 Site 化时，新建/部署纯 v0.5 Site；不得修补或复活旧 PoC/v0.4 schema。
