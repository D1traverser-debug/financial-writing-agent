# 财经写作业务全过程一致性审计（2026-11-14）

## 审计对象与验收口径

对象仅限 Financial Writing 仓库，不修改 CAOS。此审计不以 GitHub CI、GitHub Branch Protection、插件授权等系统控制面的外部验收代替写作业务。用户真正要的是：接单后自主恢复完整要求，充分取证，判断真实经济问题，形成不同读者目的的 Deep/Broad，产出自然、原创、有价值的财经文章；在各审校环节正确返工，不丢要求、不错误复用过期材料，最后交付可打开的 Word 与可追责的审计材料。

检查现行源头：docs/product_requirements.md PR-01—PR-18（含 PR-04A），真实被用户否定的海上风电与跨境电商样本，质量回归数据，Skill 与 Python 工作流、10 个 BUSINESS_STAGE 的 owner state、内部 pass DAG、功能测试、Word 生成与原始 GitHub 行为。

## 十阶段实际业务状况

| 阶段 | 当前已存在 | 不能误称已完成的业务证明 |
| --- | --- | --- |
| INTAKE | 需求来源分类、TaskRequirement 与 revision/receipt | 用户模糊表达的语义完整恢复依然依赖 LLM，非确定性 |
| RESEARCH | 全池/价值链、DecisionEnvelope、PrivateResearchBrief 1.1 和逐源字节及新鲜度读回 | 报告真实度、业务因果、投资受益排序/宏观与股票匹配仍需真正核验 |
| RESEARCH_AUDIT | 可退回 RESEARCH，结构门槛与 ref | 行业覆盖的遗漏、结论是否成立没有独立语义验证的可替代物 |
| EDITORIAL | Deep/Broad 两套 StoryBlueprint、连续标题编号、公司锚点 | 增加两产品结构差异的确定性克隆检测，仍不能保证写得有趣 |
| TITLE | 有独立 TITLE 阶段和 artifact | 标题吸引力、搜索价值、承诺兑现必须由真人/模型对照篇章判断 |
| DRAFT | 有独立 DRAFT 阶段、反重复/引述/上市公司可见性要求 | 不存在自动保证文风不 AI、结论新颖、篇章不拖沓的万能规则 |
| EDITORIAL_AUDIT | 八项带文本摘录的 PublicationFitness | 原本 CHAT_SELF_REVIEW 永远无法 PASS，只有外部独立执行器能让工作流进入 DELIVERY：**真实业务死锁** |
| DELIVERY | 四份 Word 与 source trace、DOCX binary readback | 合成 Word 的通过不等于已经实写四份真实高质量财经稿 |
| MECHANICAL_AUDIT | PDF/PNG 页图与文档数据检查 | 模拟 callback 全 PASS 不能证明排版美观 |
| FINAL_AUDIT | 四件套齐全、源和阶段 readback、可见链接验证、终态边界 | 终态仅 DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN；真实用户与独立编辑认可仍未证明 |

## 发现的内部矛盾（这不是那七项外部验收）

1. **交付死锁**：EDITORIAL_AUDIT 要求八闸全部 PASS 才能进入 DELIVERY，但同会话 CHAT_SELF_REVIEW+PASS 被 Pydantic 拒绝。这把“Word 草稿能够交付”错误绑定成“必须先拿到外部独立发表认证”。修复通过 INTERNAL_DELIVERY_READINESS 与 PUBLICATION_CERTIFICATION 分离；前者必须绑定精确 DRAFT SHA-256，且最终认证仍 OPEN。
2. **Deep/Broad 可结构复制**：此前仅检查两个 StoryBlueprint 的 product_mode，删掉 Deep 研究清单并更换 mode 字段就可把结构性相同的故事冒充 Broad。修复新增非机械化的九维结构差异最低门槛，拒绝直接和表面复制；并不宣称已证明两篇文章真的具备不同阅读价值。
3. **H1 序号跨模块冲突**：StoryBlueprint 只允许到“十五、”；publication_structure_findings 到“十、”后自动认为错误；DOCX renderer 支持更多中文数字。相同合法章节可能在策划阶段放行、文稿审校阶段拒绝。修复将中文序号生成改成一个 Financial-owned 公共函数，三个阶段共用；删除 10/15 的不一致上限。
4. **方法效果凭证实际 Git diff 漏扫**：业务变更审计支持 knowledge/actions/{action_id}.effect.json，但调用审计的 Git diff 命令仅扫描 workspaces/articles 和 METHOD_KNOWLEDGE_CATALOG.json。修复将 knowledge/actions 显式纳入 diff，防止孤立改动绕过扫描。

## 质量真问题和业务闭环：仍须验证，不能靠补一句规则解决

- 事实/因果：现行 source trace 可以抓数值、方向、财务期的明显矛盾，但 explicit semantic_fact_entailment_verified=False；“来源可读”和“文章结论成立”不是同一件事。
- 研究完整性：15 模块结构+两来源家族并不能证明真实股票池已完整、概念/直接营收的筛选正确；必须保留个股代码、来源、排除理由与当前期查证。
- 文章质量：用户拒稿中的假标题、列表式公司介绍、过长同义重复、AI 管理术语穿透正文尚未在当前真实场景盲评通过。
- 自动执行：单一状态控制器和测试可以按十阶段推进，但 LLM 研究、写作、独立审校判断仍是执行责任，非 Python schema 自动生成。CI 的全流程是合成测试，不能冒称已完成现实财经文章。
- 带条件方法学习：历史方法可以复用，但任何重用必须检索适用条件和再验证日期；审查失败后返工并失效下游内容，不接受直接把旧 PASS 复制进新稿。

## 本次代码变更对应的可执行反证

- 无独立编辑、但八闸内审完成 + 精确 DRAFT bytes：必须可以交付 Word 草稿，并明确 CERTIFICATION_OPEN；
- 内审 SHA 与真实 DRAFT bytes 不匹配：状态不得离开 EDITORIAL_AUDIT；
- Deep 改 mode 冒充 Broad：在 EDITORIAL 阶段拒绝；
- 超过 10/15 个 H1：策划、正文检查和 Word 中文编号一致；
- 孤立方法 effect.json 变动：在 Git 两版本业务审计入口被发现并拒绝；
- 原有独立认证路径、REVISE/FAIL、Word 文件实际字节/渲染约束不得退化。

## 用历史拒稿与跨主题留置样本检查质量预警

按真实存档原文（剔除元数据后）重放已有的机械检查：

- 海上风电 2026-10-10 用户拒稿，八个 H1；前四个大节的 H2 数量都是 3，构成四节相同几何结构的连续堆叠，必须触发 REVISE。文中还大量出现“不是……而是……”构式，触发模板化表达聚集预警。此检测对应用户明确反馈的“机器式组织”，**不是**仅凭词频宣判整篇好坏。
- 金红石 2026-10-06 跨主题历史基线也有八个 H1，但没有重复的 H1→H2 三层子标题结构；模板化表达警报也不应触发。这是必要的合法邻例，防止新增规则把所有长文一概判为 AI 痕迹。
- 上述两篇只是现有文本存档的回归，不能代替新的真实选题写作、取证、完整相对价值判断和用户偏好验证；目前也不能单靠章节结构检测识别海风第七、八节语义重复，必须继续用实际段落逐段比较处理。

## 是否已满足“全过程无冲突、稳定写出高水平财经稿”

**否。** 本轮修复的是已经证实的工作流死锁与跨模块合同不一致，并补齐具体回归；即使相关 CI 全部通过，也只足以证明这些机制可执行。满足完整用户目标至少还需要真正完成一篇当前时间、原始来源可验的 Deep/Broad+互动包+审计 Word，逐项人工/独立方式核查事实、观点、标题、结构、文风与读者价值，随后跨不同题材复跑，并根据失败语义迭代，而不是仅提高 Python 测试计数。
