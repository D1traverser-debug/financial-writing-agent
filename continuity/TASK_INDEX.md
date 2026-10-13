# Financial Writing Continuity Task Index

Universal protocol target: v3.7  
Owner domain: `FINANCIAL_WRITING`  
Adapter: `continuity/UNIVERSAL_PROTOCOL_ADAPTER.json`  
Execution contract: `continuity/FINANCIAL_OWNER_EXECUTION.json`

## Default USER candidate

- `financial-writing:main` — **金融文章写作** — USER — ACTIVE — stage `READY_FOR_NEW_OR_EXPLICIT_ARTICLE` — resume `DEFAULT` — manifest: `continuity/tasks/financial-writing-main/TASK_MANIFEST.json` — checkpoint: `continuity/tasks/financial-writing-main/HANDOFF.md`

## Explicit-only SYSTEM candidate

- `financial-writing:system-audit` — **财经写作系统全局审视与可靠性维护** — SYSTEM_INFRA — WAITING — stage `BOUNDED_AUDIT_COMPLETE__OPEN_EXTERNAL_ASSURANCE` — resume `EXPLICIT_ONLY` — owner `FINANCIAL_WRITING_AGENT_ENGINEERING` — manifest: `continuity/tasks/financial-writing-system-audit/TASK_MANIFEST.json` — checkpoint: `continuity/tasks/financial-writing-system-audit/HANDOFF.md`

Named continuation phrases such as `继承财经写作系统`、`继续财经写作全局审视`、`继承：financial-writing:system-audit` must resolve the explicit system task before any Bare CONTINUE discovery. `SYSTEM_INFRA` remains excluded from bare/default candidate lists.

## Rules

- 裸“继承”只把 `financial-writing:main` 作为 Financial owner 的默认 USER candidate；具体文章仍必须按当前 main 文章状态解析。
- `财经写作系统 / 财经写作全局审视 / financial-writing:system-audit` 属于 Named CONTINUE，必须优先恢复 explicit-only system task；不得降格为 Bare CONTINUE 后误接普通文章 workspace。
- 当前没有 active in-progress article。最近完成的 `ice-snow-economy-20261013` 已在其 authoritative `STATE.json` 终态化为 `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`；显式恢复该文章时必须读取其最新 STATE，不得从聊天摘要重建。
- 普通“写金融文章 / 写财经文章 / 投研文章”是 **NEW_TASK intent**：进入当前 Financial owner，但不自动恢复任何历史文章 stage / draft / next_action。
- Financial 当前只有一个正式产品/执行路径：`ChatGPT → GitHub main Financial owner → main/workspaces/articles/{task_id}`。不再选择 OWNER_NATIVE / GITHUB_CHAT / Python 等平行业务模式。
- GitHub `main` 是代码/规则权威，也是唯一业务状态写入 ref。新任务不得创建 `article/{task_id}` 等文章业务分支。文章隔离依靠 `main/workspaces/articles/{task_id}`。
- 在任何 material article action 前，读取当前 `skills/financial-writing-agent/SKILL.md`、`continuity/AGENT_MANIFEST.json`、`continuity/FINANCIAL_OWNER_EXECUTION.json` 与 `continuity/EXECUTION_CAPABILITIES.json` profile 11，只对当前步骤所需能力做 session handshake；仓库声明不是当前聊天的执行证明。
- 当前 mutation guard 是 `financial_writing_agent/owner_guard.py`；BLOCKED/system-impact lifecycle 是 `financial_writing_agent/owner_lifecycle.py`。model/web/deterministic-Python/document 只能作为同一 owner trajectory 内的 capability；不得建立第二 article-state authority、第二 terminal 语义或 fallback 路径。
- schema-1.2 中旧 `execution_mode=GITHUB_CHAT` / receipt token 仅为历史状态兼容数据，不参与 routing。
- 缺少 deterministic guard、required output 或当前阶段能力时必须阻塞对应 transition；不得退化成自由写作、SQLite/plugin 备用状态、历史 branch/eval fallback 或静默少交文件。
- 默认 canonical `TaskContract` 为 `DUAL`，required outputs 为 `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX`。显式改单模式必须有用户原始 prompt 的精确子串证据。
- 每个 material mutation 必须绑定 prior STATE blob SHA、`state_ref=main`、task/output contract、action identity 与 output refs；guard 接受后写入并回读。Git SHA CAS 不是 Universal lease/epoch 所有权证明。
- `DELIVERY → MECHANICAL_AUDIT` 前必须机械核对所有适用文章 Word 输出；`FINAL_AUDIT` 终态前必须核对完整 required-output set（含 `AUDIT_DOCX`）。聊天自述“已交付”不能替代文件 manifest + hash。
- **Output identity is not current artifact availability.** Visible delivery or cross-chat re-delivery must freshly resolve a user-accessible resource for every required Word output. Filename/hash alone, a session-local path from an older chat, or a prior render claim may not be presented as a currently downloadable artifact. If the old binary cannot be resolved, regenerate from durable publication/audit source, rerun required mechanical/render checks, bind the new actual resource/hash, and disclose that byte identity changed.
- 当前 Research/Editorial/Final review 只能按真实证据报告 `CHAT_SELF_REVIEW`；可 REVISE/FAIL，不得冒充 provider-attested isolation。正常终态仍为 `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`。
- Review FAIL 必须持久化 canonical repair target；BLOCKED 恢复只能沿该 target 返回并使 target/downstream evidence 失效后重做。
- Material user correction/feedback/rejection 必须形成 durable evidence；system-impact 若进入 maintenance required，只有绑定 maintenance/validation refs 且 assurance ≥ `REGRESSION_VERIFIED` 才能关闭。
- 历史 `OWNER_NATIVE`、旧 `GITHUB_CHAT` fallback-adapter 语义、SQLite WritingState、plugin/MCP-local task state、旧 `article/*` refs、maintenance branches 与历史 evals 都不是当前 authority。它们可以作为 Git/审计证据保留，但不能参与 routing / resume / fallback。
- 同一 task maintenance 保持既有 `resume_epoch` 与 active lease；新聊天 takeover 仍按 Universal v3.7 增加 `resume_epoch` 并淘汰旧 writer。
- GitHub/Library/Notion/Drive 都不是自动事件监听器。完全全新的 ChatGPT 对话是否能仅凭普通财经写作请求自动发现本 repo，属于产品/账号级 routing capability，必须用真实 fresh-chat trace 证明，不能由本索引自证。
- 当前 system-audit scoped pass 已完成；下次显式恢复优先验证 fresh-chat Named CONTINUE 路由与 hosted CI 执行证据，不得默认重跑全局审查，除非出现新的 defect/evidence。
- 活跃持久任务最终答复输出 v3.7 `进度提交`；只有 current owner authority、stage evidence 与 required-output manifest/availability evidence appropriate to the current action 全部回读验证后才能报告 `COMMITTED`。
