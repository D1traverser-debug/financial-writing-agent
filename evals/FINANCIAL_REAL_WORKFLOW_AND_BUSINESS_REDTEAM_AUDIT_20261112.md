# 财经写作系统真实业务回放与对抗审计（2026-11-12）

> **归属：仅 Financial Writing。** 本审计不会修改、创建 PR 或要求运行 CAOS / UAOS 仓库、服务或文件。  
> **结论：ENGINEERING PASS；财经业务产品 NOT_READY。** 本记录不能替代第三方编辑、现场登录连接、主张真实性或读者验收。

## 0. 审计范围与证据层级

- 基线：`financial-writing-agent@main` `071482ce87b1a00f62040e446aa77c88f6c944cd`，292 个跟踪文件。生产工程 CI `43003267453` SUCCESS，311 测试，Python 源码行覆盖约 86%。全文件字节/语法遍历**不等于逐行语义审查**。
- 实际场景：`workspaces/articles/cross-border-ecommerce-20261016-v3/STATE.json`，结合 v2 原始研究、反面用户反馈、`docs/product_requirements.md`、`config/EXECUTION_CONTRACT.json`、Skill、实际模块及既有回归集。
- 可重复执行：`python scripts/real_financial_workflow_redteam.py`；PR #63 的 Financial-only GitHub Actions 真实运行，输出 `audit/financial_business_redteam.json` 并上传 CI artifact。**不是模拟出一篇真实已验收文章**；反例输入是可控合成的，生产模块是真实函数。
- 事实边界：本次核验存量研究完整性、任务状态、方法学逻辑与输出门禁；没有取得 174 家企业在 2026-11-12 的完整最新披露快照，无法声称逐家实时事实复核或所有交付物可用。
- 判定术语：`STRUCTURAL_ACCEPTANCE` = 字段/一致性规则通过；`SOURCE_VERIFIED` = 外部有效来源经过实际核验；`EDITORIAL_ACCEPTED` = 独立专业/读者评价充分；`DELIVERABLE` = 真实可访问二进制产物+渲染+核验。**前者不能替代后者**。

## 1. 实际运行路径与停滞点

**用户目标**：输入财经需求与已有材料 → 全价值链与公司池 → 当前外部事实和反证 → 15 模块私有研究 → 决策 → 独立策划 Deep/Broad → 原创写作 → 事实/风格/保留率审稿 → 深度稿、泛读稿、平台互动包、审计四份 Word → 可见文件与真实用户验收、方法迭代。

**生产实际**：当前 v3 处于 `RESEARCH / IN_PROGRESS`，`quality_evidence={}`、`stage_artifacts={}`、`delivery_artifacts={}`；要求四份 Word，实际已登记 **0/4**，未发生从 RESEARCH 到用户可见交付的当前版本闭环。

任务专属两条要求：
1. `full_universe_research_pool`：全 A 股跨境电商公司研究池，去重、业务利润分层、最新来源与同分支比较。
2. `deep_complete_retained_universe`：Deep 公开完整保留公司池，弱相关公司需说明原因，不能无声省略。

原 v2 研究声称 `170 + 4 = 174` 家。检查两份 CSV：BK1115 恰有 **170 条、无重复股票代码**；BK1547 的 **8 条全部属于 BK1115**。两个概念清单来自**同一提供方东方财富**，不能把它们当成独立供应商交叉验证。原 CSV 有两家显示名称包含内部空格（`002095 生 意 宝`、`002264 新 华 都`），与旧 Deep 中规范化写法不一致；原样按名称匹配旧稿仅 172/174，去除公司名内部空格后为 174/174。额外四家公司（拉卡拉、新国都、海联金汇、米奥会展）作为经济补池有理由，但完整性仍须另取独立概念/公告/招股或定期报告源逐股验证。

## 2. 真实代码对抗用例（每条均由 Financial CI 自动执行）

| ID | 输入/情景 | 实际门禁行为 | 业务判定 |
| --- | --- | --- | --- |
| R01 | 读取生产 v3 当前业务状态 | RESEARCH、0/4 交付、无质量凭证 | **正确暴露未完成** |
| R02 | 直接 `observe_article` + 实际 Git blob 字节 SHA | 只读观察，不宣称独立编辑通过 | **正确保证读态边界** |
| R03 | 尝试无需有效外部授权推进状态 | `DENIED:FINANCIAL_TRUSTED_AUTH_AND_CAS_REQUIRED` | **正确拒绝** |
| R04 | 重新验证 2026-10-16 的历史 PrivateResearchBrief | 过期 27 天仍可 `coverage_state=COMPLETE`（仅结构） | **严重时效保证缺口**，不能推断事实仍真 |
| R05 | 15 个研究模块填上 `audit-example://nonexistent` 假证据 | `validate_private_research_brief` 接受完整结构，未读取原文 | **严重来源可用性缺口** |
| R06 | 源文“2026 年收入同比**下降 20%**”，稿件改成“同比**增长 20%**” | `verify_publication_source_trace` 结构追溯通过；语义标记仍为 false | **严重内容真实度缺口**；这是追溯器明示能力上限，根因在系统级缺少强制语义复核 |
| R07 | 八项审稿 PASS，证据为未核实的“自评无问题” | `PublicationFitness` 允许 `CHAT_SELF_REVIEW / PASS` | **无法证明独立编辑质量** |
| R08 | 带不同 reviewer/author/execution_ref 的独立审稿请求 | `INDEPENDENT_EXECUTOR` 当前**被显式拒绝** | **独立验收能力无法在现有模型内闭合** |
| R09 | 内部调用者伪造 Generic AUDIT DOCX 构建凭据与两项 PASS，无真实 DOCX/PNG | `finalize_delivery_evidence` + `validate_delivery_evidence` 接受内部自签凭据 | **非任务绑定产物的审计证明弱点**。该反例使用包内私有签发函数、未通过外部资源 verifier；**不证明真实用户通道可被外部伪造** |
| R10 | 在实际 v3 全池任务下，仅提供三家合成公司并标注 `universe_coverage=COMPLETE`，稿件出现三名、弱相关理由、比较关键词 | **已接受**（只校验输入的 3 家） | **公司池外部完整性缺口**；门禁只能对比输入的结构，不会独立发现被遗漏的 171 家 |
| R11 | `full_universe_research_pool` 的满足证据写成不存在的 `audit-example://` 引用 | **已接受**（未打开任何外部证据） | **声明式满足与事实级满足尚未闭合** |
| R12 | 用 v2 实际 170 行 BK1115 CSV 逐股比对历史 Deep 草稿 | `002095 生 意 宝`、`002264 新 华 都` 与文稿中的规范化名称不同 | **来源数据身份清洗缺口**，应以 ticker 作为稳定身份 |
| R13 | 对同一篇 B2B 公司比较，只改变 `生 意 宝` / `生意宝` 的输入名称 | **已复现**：原样名称被判“公司遗漏、缺乏比较”，规范化后相同文章 `ACCEPTED:3` | **错误遗漏报警风险**，需统一标准化显示名称 |

> 执行性质：R01–R09 已在第一轮真实 CI `43144478441` 重现；R10–R11 在第二轮真实 CI `43144814292` 重现。R12–R13 已由第三轮真实 CI `43145474637` 复现。运行成功意味着**反例检查被执行**，不是所有业务门禁安全。

### 代码可追溯位置

- `financial_writing_agent/private_research.py:90-124`：验证时间字段非空、模块状态、摘要和引用非空；没有来源读取/时效或文本事实检验。
- `financial_writing_agent/claim_trace.py:51-156`：哈希、摘录及数字集合验证，保留 `semantic_fact_entailment_verified=False`，不检查上下行文、比较方向、时间/计量单位的一致性。
- `financial_writing_agent/task_publication.py:74-150` 和 `financial_writing_agent/checks.py:145-153`：Complete/公司名及比较关键词是内部结构线索，不能证明真实经济比较或市场源完整。
- `financial_writing_agent/current_admission.py:184-218`：任务满足项要求 `SATISFIED` + 非空证据引用，不读取实际材料；`current_admission.py:278-332` 确保审核材料的版本和哈希延续，却不保证语义事实。
- `financial_writing_agent/story_quality.py:187-243`：同一执行者可作 PASS，显式拒绝 `INDEPENDENT_EXECUTOR`。
- `financial_writing_agent/delivery_pipeline.py:185-271,327-520`：真实 Word 文件的机械检查较强，但 Generic Receipt 路径没有与 task-bound 长文一致的强制逐页 render receipt，且使用当前会话内部签发密钥，不代表第三方审稿。
- `financial_writing_agent/standalone_runtime.py:143-271`：状态读取/写入双次 readback 与外部认证门禁已经建立。当前应用服务/插件的实际用户授权连接尚未实测。
- `.github/workflows/ci.yml` 和 `scripts/render_smoke.py`：CI 渲染的是合成 Word 与自动 PASS 的页回调；不能证明实际四份 Word 的视觉、用户阅读体验和外部链接。

## 3. 逐阶段推演：哪里实际会断、哪里仅是形式审查

| Graph 阶段 | 生产控制面 | 真实业务推演/审计结果 |
| --- | --- | --- |
| INTAKE | `current_admission.build_initial_state`, task requirement digest | 原用户的两条特殊要求已留存；**通过结构连续性**。需求表述误解仍需人工核验原文。 |
| RESEARCH | source discovery, ResearchPackage, PrivateResearchBrief 1.1, DecisionEnvelope | v3 未形成新研究；15 模块可被虚构引文填满，旧 as-of 不阻挡旧结构 PASS；**当前真实研究不可验收**。 |
| RESEARCH_AUDIT | 阶段产物和 PASS/REVISE/FAIL 路由 | 有退回能力，但没有独立逐股主披露校验的实际运行证据；**OPEN**。 |
| EDITORIAL | Deep/Broad StoryBlueprint 两套方案 | Schema 能限制最低结构、事件→公司因果字段；不能证明两个结构分别服务读者；**结构层可用，语义 OPEN**。 |
| TITLE | 标题与阶段产物 | 标题多样性约束不等于真实点击率、准确性、承诺兑现；**OPEN**。 |
| DRAFT | ArticleDocument, 研究→公开范围 | 对 174 个既定公司名的可见性核对可执行，但若上游传入“三家即全部”的假池，仍有误放行可能；**来源池不可信时下游不能自救**。 |
| EDITORIAL_AUDIT | 八项 PublicationFitness；自评凭证 | R06+R07+R08 构成组合风险：数值相同、方向相反也可追溯；自评可 PASS；独立审稿被硬禁；**严重缺口**。 |
| DELIVERY | 4 类 Word Builder + SHA + render | 能实际生成 DOCX、渲染到 PNG；但用户任务 v3 没有生成；Generic audit/interaction/private 输出的自签证明独立性不足；**业务未完成**。 |
| MECHANICAL_AUDIT | DOCX/PNG/页哈希，页回调 | 页面确已渲染不等于实际审美检查。CI 的合成 reviewer 逐页无条件 PASS，仅证明回调触达页面字节；**视觉意义 OPEN**。 |
| FINAL_AUDIT | required_outputs 与状态审计、可见交付函数 | 能要求四类元数据齐全；真实二进制、用户可访问性需外部 provider verifier；用户/独立编辑认可尚未取得；**不能终结为高质量成品**。 |

`GENERAL_EDITORIAL_QUALITY` 在 `evals/quality_regression.json` 明确为 `NOT_READY__HELDOUT_DIVERSITY_INSUFFICIENT`，`PERSONALIZED_WRITING_DNA` 为 `NOT_READY`。现存负面文章不能拿历史语义冒充当前版本成功。

## 4. 共享根因：不是“再加 30 条提示词”

### H1：旧稿只是语句差，改写就能好
- **反证**：R05/R06/R07/R10 说明在文章生成之前就存在来源真实性、完整性和质量证据断层；重写无法替代上游校验。**不是充分根因。**

### H2：财经事实链把“有证据引用/哈希”误用成“陈述被证实”
- **支持**：R05 虚构 URL 仍过研究模式，R06 下降/增长反向可过文本数字追溯，任务满意度证据为字符串而非源读回。
- **归属**：Research+editorial evidence interface 的语义/时间/权限保证边界。**首要根因。**

### H3：读者质量闸门没有可执行的独立验收路径
- **支持**：R07 same-chat 任意 PASS 和 R08 schema 硬拒外部独立 PASS；历史被用户拒绝，现有 quality readiness NOT_READY。
- **归属**：PublicationFitness 与 editorial promotion。**首要根因。**

### H4：架构依赖 CAOS，连接不独立
- **反证**：当前 Financial Skill、独立 state 接口、无父依赖 manifest、R02 和 R03 能正常工作；**没有证据应重新修改或接入 CAOS**。真实本体插件尚未连接是 **Financial 的集成缺口**，不是要动 CAOS。

### H5：Word 渲染实现全部失效
- **反证**：真实 CI 可装 wheel、可 LibreOffice render，PNG 与 DOCX 的哈希读回有效。问题是 **审核和用户访问证据不足**，尤其非长文的 generic 证据路径；并非全部 Word 功能不可用。

### H6：174 个公司意味着一份全量 Deep 必须写成百科
- **反证**：用户要求“完整可见 + 分支对比”，允许弱相关集中列名；不需要 174 篇小传。**真正的风险是概念公司池缺失、错分层和利润传导虚假**。

**因果图**：上游来源真实性/时态/覆盖缺口 → 私有研究可“结构 COMPLETE” → 论证允许错误方向/公司池缩水 → same-chat 八闸自评 PASS → 自动文档与签名完整 → **产生格式可信、事实和读者质量未充分保证的 Word**。哈希不是事实验证器，Word 成功不等于文章成功。

## 5. 优先级与修复准则（尚未冒充已完成）

| 优先级 | 必须整改的 Financial-only 事项 | 可独立判断的验收 |
| --- | --- | --- |
| P0 | 当前业务 RESEARCH 加来源时效闸门；正式发布前重新查询到期法规/政策和近期财报，区分已实施/待实施/废止 | 同一 October snapshot 在 November 发布时强制 OPEN，真实更新源验证后才解除；不破坏历史原稿 |
| P0 | 为关键数值建立 `ClaimLedger`：主体、指标、会计期、单位、方向、同比/环比、一次性项、来源类型和快照，另写独立语义/算术审查入口 | 用“下降20% → 增长20%”“2026H1→2026Q3”“元↔万元”“净利↔收入”四类负样本均不得被标成 `SEMANTIC_FACT_VERIFIED` |
| P0 | 研究完整性不得仅因 `coverage_state=COMPLETE` 或 15 模块非空而成立；逐股代码去重、多家来源比较、issuer 披露核验、缺口列表必须绑定实际 source readback | 伪造 `audit-example://` / 三家伪全池失败关闭；恢复真实 174 pool 的逐股 inclusion/exclusion ledger 与有效期 |
| P0 | PublicationFitness 的 same-chat PASS 不能成为独立文章最终验收；支持独立 reviewer 身份、原稿/反馈/盲读与强审计 provenance，缺失时标记 OPEN | 同作者自评永远不能晋级 `EDITORIAL_ACCEPTED`；独立真实读者样本可关联到稿件修订 |
| P1 | 所有 Word 类型通过同一真实 DOCX blob readback / render page manifest / visual evidence 与资源签名；generic 路径不能仅靠 PASS 字符串声称 render | 无 DOCX 的审计/互动包不得形成“已验证真实文件”陈述；真实四份可打开且可访问 |
| P1 | 外部用户授权的 Financial-only GitHub provider CAS / ChatGPT 插件、会话权限和现有 STATE 数据持久化现场集成 | 一个**经用户真实授权**的 Financial-only 任务 action 成功，冲突/撤权/跨文章输入拒绝；不假装 mock 等于安装 |
| P1 | Real-article E2E：在 v3 新研究上实际产生 Deep/Broad/interaction/audit Word，页面逐页验收，不用 v2 旧稿直接封装 | 4/4 Word + 来源/研究/稿件修订 + provider readback + 外部编辑/读者反馈 |
| P2 | 写作风格和多场景盲评，受众留存与原创性测试，并形成独立 held-out corpus | 至少两种不同议题的真实双版本文章，盲评相对基线改进；不过拟合跨境专题 |
| P2 | 复用知识只能保留“来源/时间/适用条件/反例/再验证条件”，优先减少重复扫描耗时 | 历史资料在旧时间触发质疑，而非被自动认作最新事实 |

**首选修复路线**：适配现有 Financial 自有 Article Aggregate 和各 gate，新增“事实主张级+时态+来源验证”的阻断证明以及“真实独立编辑”的证明，不创建第二套业务状态或父级运行系统。备选“加关键词黑名单”只可作报警，不可当事实判断；备选“复制/调用 CAOS”明确排除；备选“重做全部多 Agent”在业务改善证据不足之前不采用。

## 6. 外部政策的真实反例：历史资料不能直接视为当前事实

历史 `stages/DRAFT_V2_20261016.md` 将欧盟 11 月 1 日小包处理费写为“当时尚未定价的未来事项”，符合**旧文时间标签**；2026-11-12 再执行，必须主动核实 11/1 后实施状态及费率，而不能把相对时间原样继承。外部政策参考：欧盟/成员国后续公告与中国商务部当期信息；用户可见审计解释已提供政策变更来源。

**风险不在历史文本存档，而在**：下游 `validate_private_research_brief` 仍接受其 `COMPLETE` 结构且无法判断“旧证据对今天的发布是否仍有效”。若文章为 2026-10-16 历史回顾，时间冻结可以保留，但出版时应明确历史口径；若为 2026-11-12 当期稿，政策/个股核心数据必须刷新。

## 7. 当前验收声明

1. `ENGINEERING`: 可由 GitHub Actions 的精确 head、步骤、输出复核；本审计增加的所有代码和文档仅位于 Financial 仓库。
2. `DOMAIN_SCHEMA`: 部分缺陷以**真实生产 Python 函数及对抗输入**重现，详见脚本+CI JSON。
3. `EDITORIAL`: **NOT_READY**；没有独立事实核验和认可，更不存在可声明的泛化读者提升。
4. `LIVE_FINANCIAL_APP`: **NOT_VERIFIED**；GitHub repo 自述不等于已连接/部署的 ChatGPT Plugin。
5. `LIVE_ARTICLE`: **NOT_READY**；v3 没有跳阶段，也没有伪造新来源、假“研究完成”或旧稿重新包装。
6. `CAOS`: **NO WRITES / NO PR ACTIONS / NO DEPENDENCY**，本审计从始至终只执行 Financial 仓库内操作。

后续任何改动，仍只允许对 `D1traverser-debug/financial-writing-agent` 开展；真实用户验收不能由同一执行器写一个 PASS 字符串代替。
