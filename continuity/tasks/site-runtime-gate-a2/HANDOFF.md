# Financial Writing Agent Site Runtime｜Gate A2 Continuity Handoff

- task_id: `financial-writing-site-runtime:gate-a2`
- display_name_zh: **金融写作 Site Runtime：Gate A2**
- task_class: SYSTEM_INFRA
- status: ACTIVE
- resume_visibility: EXPLICIT_ONLY
- owner: FINANCIAL_WRITING_AGENT_ENGINEERING
- current_stage: GATE_A2_BUSINESS_EXECUTION_WIRING
- contract_version: SITE_POC_GATE_A2

## Goal
把当前 16-tool contract-hosting PoC 变成真正可执行的 Site Runtime，同时继续以 Python Runtime 为唯一 behavioral oracle。

## Continuity classification
这是 Financial Writing Agent 的系统工程维护任务，不是“写金融文章”的默认 USER 工作入口。
因此它不得进入裸“继承”默认候选；只有用户明确说继续 Site Runtime / Gate A2 / 对应 task_id 时才恢复。

## Hard boundaries
- Gate A2 完成前不进入 Gate B durability test；
- 不跑真实文章 live-model E2E；
- 不做 production-ready 宣告；
- Site 可部署/工具存在不等于与当前 Skill contract 兼容。

## Next action
从当前 integrated HEAD 重新做 capability/schema preflight，继续 16-tool business execution wiring 与实际 Site 环境验证；修复以唯一 owner + regression/CI 方式进入。
