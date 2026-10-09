# Financial Writing｜AI 制药文章 Continuity Handoff

- task_id: `052804dc-f66a-441d-8875-c7973366b072`
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: FINANCIAL_WRITING_AGENT_RUNTIME
- current_stage: MIGRATION_REQUIRED
- contract_version: legacy-unclassified

## Topic
AI制药进入“数据与实验验证”阶段后，A股谁真正承接增量：从干湿闭环、湿实验基础设施到BD资产兑现的分层比较。

## Source
`https://xuangutong.com.cn/ts/report/18133`

## Next action
先 exact `get_writing_task(task_id)`；对旧 checkpoint 与当前 deep-first DUAL contract 做 compatibility handshake；不得复用旧并行 DUAL 的 stage/gate PASS。

## Migration rule
旧 checkpoint 处于历史 EDITORIAL 附近，但旧 next_action 使用并行 DUAL，已与当前 `FINANCE_DEEP → BROAD_DERIVATION → FINANCE_BROAD` 冲突。只复用仍有 provenance 的 research/evidence、source refs、用户要求和原始 artifacts。
