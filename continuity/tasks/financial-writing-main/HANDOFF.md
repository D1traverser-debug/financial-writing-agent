# 金融文章写作｜Continuity Handoff

- task_id: `financial-writing:main`
- display_name_zh: **金融文章写作**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: FINANCIAL_WRITING_AGENT_RUNTIME
- current_stage: `READY_FOR_NEW_OR_EXPLICIT_ARTICLE`
- continuity_contract: `CONTINUITY_V3_7`
- writing_contract: `Financial Writing Agent v0.8`
- writing_rule_authority: `D1traverser-debug/financial-writing-agent@main`

## Current system state
The owner runtime is v0.8 with 18 typed MCP tools, Word-only delivery and proof-bearing owner-runtime semantic audit certification. `RESEARCH_AUDIT`, `EDITORIAL_AUDIT` and `FINAL_AUDIT` semantic PASS must use `run_semantic_audit_stage`; the `submit_*audit` family is conservative CHAT_BRIDGED REVISE/FAIL-only and cannot self-certify PASS.

The prior v0.7 recovery wording in this handoff/manifest was stale relative to the current Skill, Universal adapter and execution-capability profile. The 2026-10-11 system-hygiene audit reconciles that recovery surface to v0.8 and adds regression coverage so version/capability drift is no longer invisible to CI.

## Harness / pollution hardening in this maintenance turn
Implemented, pending current-head CI closure:
- semantic gate invalidation clears same-name working payloads, so an invalidated old audit payload cannot survive as stale proof material;
- semantic runtime proof requires an ordered `EXECUTOR_START → EXECUTOR_END` pair after the latest stage entry;
- runtime `next_action` now routes semantic PASS through `run_semantic_audit_stage` instead of stale `submit_*audit` instructions;
- test-only `financial_writing_agent/adapters/mock.py` is removed from the production package; runner-test doubles live only in tests;
- wheel smoke now fails if the test-only mock adapter reappears;
- continuity recovery metadata is regression-checked against current owner contract v0.8 and capability profile v8.

## Deliberately retained surfaces
These were inspected and are not treated as garbage:
- `references/*`, `skills/financial-writing-agent/references/*`, and packaged `financial_writing_agent/resources/references/*` are intentional byte-identical mirrors serving source authority, Skill bundling and installed-wheel resources;
- historical `evals/` audits and rejected/held-out artifacts remain provenance/regression evidence;
- `runner.py` / `runtime_factory.py` remain the developer/standalone outer-loop path, while `runtime_service.py` + `plugin_server.py` remain the MCP service path over the same engine/controller authority;
- `deploy/chatgpt-site/SITE_SPEC.md` remains the deployment contract even though no Site Runtime plugin is currently installed.

`network_safety.py` and Skill-size/duplication were inspected as possible debt but are not deleted without stronger dependency/evaluation evidence.

## Quality / methodology boundaries
Methodology owner receipts use receipt contract `1.3` with exact action binding and remain `UNVERIFIED_OWNER_RECEIPT`; they do not self-certify operational conformance.

Quality-promotion status is unchanged:
- FINANCE_DEEP is diagnostic/candidate-design only until a second complete held-out case from a distinct topic family exists;
- FINANCE_BROAD is not quality-promotion-ready;
- Personalized Writing DNA additionally requires real user acceptance/edit or post-publication performance evidence after the general requirements pass.

No harness cleanup or CI result by itself proves prose quality improved.

## Exact next action
For a normal article request, load the current v0.8 Skill, Universal adapter and capability profile, complete the current-session capability handshake, then run the existing v0.8 state machine. Semantic audit PASS uses `run_semantic_audit_stage` only.

For this system-hygiene maintenance turn, finish current-head full CI, then write the verified behavioral head/run/job back into this handoff, the task manifest and `evals/SYSTEM_HYGIENE_AUDIT_2026-10-11.md` before reporting COMMITTED.

## Runtime / authority boundaries
- GitHub `main` is the Financial Writing code/rule authority.
- Authoritative per-article state is persisted `WritingState`; this handoff is workspace recovery metadata, not article state.
- Connected apps and chat history are reference/evidence surfaces unless explicitly promoted with stable verified receipts.
- No Financial Writing Site Runtime plugin is currently installed.
- Provider-attested isolated semantic review remains unavailable; stage-separated owner-runtime review must not be mislabeled as provider independence.

`resume_epoch=2` and the active lease are unchanged because this is same-chat maintenance, not takeover.
