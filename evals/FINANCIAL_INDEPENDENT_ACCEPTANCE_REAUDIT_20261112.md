# 财经写作系统 — 对抗式独立验收复审（2026-11-12）

**结论：工程模拟测试 PASS 不等于系统整体验收 PASS。实际终态仍为 NOT_READY。** 本轮仅修改 Financial Writing，CAOS 仓库代码、分支、插件、PR 和设置完全不触碰。用户此轮指令是“完整做好系统”，**不是出真实财经文章**。

## 精确的已有证据

1. 2026-11-12 原生产 `main` 为 `72cf852746a54b5f116e41f96bb8ca54b5f6838c`；CI #43191897225 报告 374 passed，测试总行覆盖 87%（4989 语句中 667 未覆盖），并非 100%。红队脚本自己报告 `product_readiness=NOT_READY`、当前 v3 为 RESEARCH 且 0/4 真实 Word 出品。
2. PR #66 已合并但没有独立 review 记录；单个维护者开发、设计模拟数据、运行测试、合并不能视为多主体独立验收。
3. 当前 GitHub 实时清点为 99 branches（含 main）、66 个 closed PR（48 merged into main，18 closed without merge）和 1 个 open PR（#67）。98 个非 main ref 中，44 个 head SHA 能与 merged-to-main PR 精确匹配，54 个没有这种精确证据；后者不等于未合并，可能是 squash merge、直接提交、过期 ref 或重复 head。PR 历史不可删除或伪造。
4. 当时 GitHub main `protected=false`，未设置 mandatory required checks；外部仓库管理权限不可通过 Financial 源码声明来获取。
5. 当时当前账户没有独立 Financial ChatGPT 插件。现已创建私有 Financial Skill 插件 `plugins_6af591b19a708191a3879e94a7ce8742`，release `pluginrel_6af591b305e88191a537446ca98fb5d3`，并经插件文件读回验证。**未经过用户显式安装、新会话激活或真实 GitHub 读写验收；该插件不托管 Python/MCP 动作 API。**

## 根因链条

原始要求 → 已认证原文及哈希 → **模型自行填写 statement、source_kind 或 retire_ids** → `CHANGE_REQUIREMENTS` 无原文与新要求语义绑定 → 可能合法 CAS 存储与用户原意相反的要求 → 后续 10 阶段在错误目标上执行 → Word 结构和 CI 均可能 PASS → 用户需求失败。

这是完整目标恢复和语义治理缺口，不能靠多加「来源哈希」补救。其他独立缺口：host/ChatGPT plugin 激活与仓库代码未真正集成；「外部 reviewer」只有注入回调，模拟实现不能替代真人或独立认证来源；主分支没有保护；PR 合并后旧分支未自动归档。

## 差异化修复

- RED：合法用户消息，试图替换为「Deep 只能保留 3 家」并上传正确 SHA；需要拒绝。模型伪造 `approved=True`、错 source/change digest、未认证 retirement，均拒绝且 STATE.json 字节不变。
- FIX：`intent_governance.verify_requirement_change_intent` 需原始用户 role/bytes、变更源文本锚定（新增 statement 必须逐字出现于原文）、独立可信 provider 对原始消息和**规范化的完整 upserts/retire_ids/old target** 计算的 exact mutation hash 给出 `OWNER_EXPLICITLY_CONFIRMED_EXACT_CHANGE`；没有这样的提供者就 **BLOCK**，而非把模型生成的 PASS 写入状态。原文不写入公开 GitHub，receipt 仅存所需摘要和经核对的身份边界。此证明仍依赖真实提供者，并不是“语义数学可判定”的虚假断言。
- 一次性仓库 branch 清理流程归档原 branch HEAD SHA 为 Git tag 后再删 ref；先 Dry Run、排除 main/protected/open-PR，遇 SHA 变化、权限和归档冲突 fail-closed；保留原 Git commit history 和标记，GitHub PR history 原封不动。需真实 Actions 权限和 provider readback。
- 私人 Financial Skill 插件是**单独域入口**，不依赖 CAOS runtime；代码明确提示其不是 Python host，不自带 GitHub 授权，使用者必须实际连接、在新会话独立验证。
- 7 门外部验收模块 `financial_writing_agent/acceptance_gates.py`：对原始意图、Article Graph/恢复、方法 CRUD+传播、真实 Git CAS、客户端激活、独立红队、main 分支治理分别要求与被验 `main` 精确绑定的外部来源回读和非拥有者认证。CI 只写 `NOT_READY` 报告，不把 PASS 数量视为产品完成。

## 退出标准及证据层级

| Gate | 验收必须满足 | 可信证据 | 本轮现有状态 |
| --- | --- | --- | --- |
| G1 用户意图忠实 | 可恢复且从未将建议或矛盾需求升格 | 实际认证原始消息 + 外部 owner-approved 变更摘要 | 代码与 mock 已有；live OPEN |
| G2 Graph/恢复 | 各阶段合法、失败恢复、重验影响范围完整 | 独立提供者状态读回、失败事务不可污染 | 模拟已覆盖；live OPEN |
| G3 方法论 CRUD | 版本、质疑、复用、退役、影响传播和回退 | 真实方法录入、影响对象读回 | 模拟已覆盖；live OPEN |
| G4 授权和写入 | 授权、CAS 冲突、拒绝与撤权可靠 | 真 Git provider 交叉权限和两次读回 | live OPEN |
| G5 唯一入口 | 新 ChatGPT 会话只连接 Financial 可完成一次原生任务 | 插件实际安装/激活与完整工具动作证据 | 私人 Skill 已创建；未安装 |
| G6 外部独立审计 | 与编码者不同的真实主体设计反例并复验 | reviewer 真实身份 + 变更及 CI SHA | OPEN |
| G7 一主分支 | 只有 main 作为活动分支且旧史可找回 | GitHub 标签、branch list、删除结果二次读回 | 一次性 Archive 候选 / OPEN |

**程序退出准则**：7 门均有外部强证明，并且精确 `main` CI PASS，才能称“系统整体验收通过”。不应利用同一模型捏造两个 reviewer 角色。此门不包括真实文章出品质量；财经内容出品将另行以现实用户样本评测。已验证的工程 PASS 与未验证的运营/客户端能力应分别保留。

## 本轮差异与约束

- 只有一个整改候选 PR #67，禁止把同一轮拆成无关的小 PR 膨胀历史。
- 用户现有独立私人 Financial 插件可打开 `https://chatgpt.com/plugins/plugins_6af591b19a708191a3879e94a7ce8742`，**但安装需要用户明确操作**；不虚构安装成功。
- 不使用 CAOS PR、文件或 Plugin Creator 项目条目来交叉编辑 Financial。
- GitHub 仓库管理员的 branch protection settings 与真正的 ChatGPT user-message provider/host API 不在 GitHub 源代码修复权限内，必须明确标记为外部权限边界。

## Candidate CI and repository hygiene update (latest exact PR head)

Candidate PR #67 head `792939bd4003a54583b3038020e934aba60692c5` ran the full CI successfully (run `43255571900`): **433 passed**, source-line coverage **87%** (5,362 statements, 695 missed). The job explicitly checked out and verified `git rev-parse HEAD == PR head SHA`, ran whole-tree byte/parse inventory (328 tracked files; 111 Python AST and 58 JSON parsed; 40,423 decoded text lines; zero warnings/errors), wheel/install, DOCX renders, synthetic negative business replay, the system acceptance report, and a **read-only** live GitHub branch cleanup dry-run.

The machine report remained `NOT_READY__REQUIRES_SIGNED_EXTERNAL_EVIDENCE` with all seven external gates open: original goal/semantic correction, legal article graph/recovery, method CRUD/impact, authenticated provider CAS, native client activation, independent external adversarial review, and main-branch hygiene. The current business replay still reports `product_readiness=NOT_READY`, article stage `RESEARCH`, **0/4 delivered outputs**, and **0 quality-evidence items**. Four Word product binaries and page renders were produced only from synthetic content; this is a renderer smoke test, not editorial acceptance.

The dry-run read **99 branch refs** and found one open PR. The updated schema-4 manifest records all 98 non-main refs, all merged-to-main PR head evidence, and exact per-ref classification: 44 refs match a merged PR head SHA; 54 have no exact merged-PR head evidence. It does not label those 54 as unmerged or safe to discard. All 98 heads receive archive tags before any deletion. Pruning refs without exact merged-PR evidence now requires the explicit workflow input `confirm_unverified_branch_archive=true`, in addition to the separate archive/prune reviewer approvals. No branch or tag was archived or deleted by the candidate CI; the dry-run remains read-only. Historical PR records remain untouched.

The real connected GitHub CAS probe succeeded on the candidate branch: valid write/readback, deliberately stale blob SHA rejected with HTTP 409, exact updated blob readback, and temporary file deletion verified by 404. This is evidence of repository file CAS only, not proof of authenticated original user-message access, real article-state provider, access revocation or native plugin activation.

Earlier intermediate candidate runs exposed test failures while the new signature-history and branch-archive guards were being tightened. They were corrected before the 428-pass exact-head CI above. Do not quote earlier failed or cancelled runs as passing.
