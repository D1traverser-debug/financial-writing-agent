# 金融文章写作｜Continuity Handoff

- task_id: `financial-writing:main`
- display_name_zh: **金融文章写作**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: FINANCIAL_WRITING_AGENT_RUNTIME
- current_stage: `READY_FOR_NEW_OR_EXPLICIT_ARTICLE`
- continuity_contract: `CONTINUITY_V3_7`
- writing_contract: `Financial Writing Agent v0.8.1`
- writing_rule_authority: `D1traverser-debug/financial-writing-agent@main`

## Current validated / pending system state
The owner runtime remains Word-only with proof-bearing owner-runtime semantic audit certification. `RESEARCH_AUDIT`, `EDITORIAL_AUDIT` and `FINAL_AUDIT` semantic PASS still require `run_semantic_audit_stage`; the `submit_*audit` family remains conservative CHAT_BRIDGED REVISE/FAIL-only.

The prior system-hygiene baseline was regression-verified, but the new v0.8.1 material-feedback system-impact escalation path is **currently wired and awaiting fresh owner CI validation**. Do not call the new path regression-verified until the current head completes the full owner workflow.

## Confirmed defect that triggered v0.8.1
Universal and owner maintenance authority already required a first-occurrence material correction to receive a system-impact review and required existing-rule execution gaps to be treated as runtime/trajectory defects. However, the live owner action contract for `record_writing_learning_sample` previously persisted only a raw learning sample plus an evolution receipt. It did not create a durable review obligation, did not require mechanism comparison/failure-mode analysis, and `operational_hygiene` had no article-action receipt path.

Therefore the repository could be contractually correct while a real article rejection was recorded and locally revised without owner-level proof that the system-impact question had ever been reviewed. This was confirmed as a declaration-to-operation defect, not inferred from prose quality alone.

## v0.8.1 selected mechanism
Rejected mechanisms:
- another Skill/prompt reminder: still declaration-only and would re-bloat the thin router;
- automatic full maintenance for every feedback item: over-couples the article hot path to engineering control-plane mutation.

Selected mechanism: **durable owner system-impact obligation + explicit Universal handoff**.

For `USER_EDIT`, `USER_FEEDBACK` and `USER_REJECTION` recorded through the owner plugin:
1. the raw Writing-DNA evidence remains `RAW_EVIDENCE_ONLY`;
2. owner runtime creates a durable `PENDING_REVIEW` system-impact signal bound to that exact sample;
3. `review_writing_system_impact` requires a system-level problem statement, root-cause layer, generalization scope, at least two distinct mechanisms with explicit failure modes, selected mechanism/rationale, authority surface, regression/eval plan and evidence refs;
4. review may end as `REVIEWED_NO_MAINTENANCE` or `MAINTENANCE_REQUIRED`;
5. `SYSTEM_MAINTENANCE_REQUIRED` emits a non-authoritative `USER_REPORTED_SYSTEMIC_FAILURE` control signal for current Universal `operational_hygiene@1.0 + evolution@1.0` maintenance;
6. a later closure call must replay the accepted review exactly and attach durable maintenance/validation refs with assurance >= `REGRESSION_VERIFIED`;
7. `PENDING_REVIEW` cannot be silently bypassed at COMPLETE;
8. completed tasks with unresolved `MAINTENANCE_REQUIRED` remain discoverable instead of disappearing from default continuation.

The review action emits an owner action-scoped `operational_hygiene@1.0` receipt under receipt contract `1.3`. It remains `UNVERIFIED_OWNER_RECEIPT`; Universal independent exact-action, evidence-ref and semantic hook verification is still required for operational PASS.

## Evidence classes — do not collapse them
- **Repo/contract proof:** Universal + Financial maintenance authority require first-occurrence system-impact review; v0.8.1 code/capability/adapter now declare an executable owner path.
- **Reference simulation / harness proof:** unit/MCP/static/CI tests can show that negative feedback creates a signal, review requires alternatives/failure modes, COMPLETE cannot ignore pending review, and maintenance-required tasks remain discoverable. This is not a real user action.
- **Current owner action-level proof:** requires a real installed Financial Writing owner runtime invocation that persists an actual sample/signal/review/receipt. This chat currently has no installed Financial Writing Site Runtime plugin, so this evidence class remains open until such an invocation exists.
- **Live writing outcome proof:** requires a post-fix real article/user outcome. The historical offshore-wind rejection is pre-fix failure evidence, not post-fix success evidence. No claim of improved prose is permitted.

## Quality / methodology boundaries
The v0.8.1 repair changes maintenance escalation reliability, not article-quality promotion status.
- FINANCE_DEEP still lacks the second distinct complete held-out topic family required for promotion;
- FINANCE_BROAD is not quality-promotion-ready;
- Personalized Writing DNA still requires the general evidence requirements plus real acceptance/edit or performance evidence.

No blind pairwise promotion result is created by this maintenance repair, and no writing-quality improvement claim follows from CI.

## Exact next action
First, complete fresh owner CI for the v0.8.1 system-impact escalation head. If CI passes, persist the exact behavioral head/run/job into the adapter, task manifest, this handoff and the system-impact maintenance audit, then run closure-head CI and re-read authority before `COMMITTED`.

For a later normal article request, load current thin v0.8 Skill, `continuity/AGENT_MANIFEST.json`, Universal adapter and capability profile 9, complete the session handshake, then use v0.8.1. Material corrective/negative feedback recorded through the owner must not be treated as closed until the system-impact review obligation has been classified.

## Runtime / authority boundaries
- GitHub `main` is the Financial Writing code/rule authority.
- Authoritative per-article state is persisted `WritingState`; this handoff is workspace recovery metadata, not article state.
- Connected apps and chat history are reference/evidence surfaces unless explicitly promoted with stable verified receipts.
- No Financial Writing Site Runtime plugin is currently installed in this chat.
- Provider-attested isolated semantic review remains unavailable; stage-separated owner-runtime review must not be mislabeled as provider independence.

`resume_epoch=2` and active lease `fw-5636d680328b40c5ab4b5029441e3489` remain unchanged because this is same-chat maintenance, not takeover.
