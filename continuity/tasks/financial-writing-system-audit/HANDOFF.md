# 财经写作系统全局审视与可靠性维护｜Continuity Handoff

- task_id: `financial-writing:system-audit`
- task_class: `SYSTEM_INFRA`
- domain: `FINANCIAL_WRITING_SYSTEM`
- owner: `FINANCIAL_WRITING_AGENT_ENGINEERING`
- status: `ACTIVE`
- resume_visibility: `EXPLICIT_ONLY`
- continuity_contract: `CONTINUITY_V3_7`
- current_stage: `GLOBAL_AUDIT_AND_LIVE_E2E_REPAIR`
- resume_epoch: `1`
- active_lease: `fw-eng-b8292233f43340b0912cbb20db3e227d`

## Why this task now exists

The Financial repository already contained durable system-level evidence such as:
- `evals/FINANCIAL_GLOBAL_SYSTEM_AUDIT_2026-10-12.md`;
- `evals/FINANCIAL_FULL_SYSTEM_REBUILD_2026-10-12.md`;
- `evals/FINANCIAL_LIVE_E2E_TASK_OUTPUT_CONTRACT_INCIDENT_2026-10-12.md`;
- Phase 0/1/2 closure evidence.

But the current continuity surface exposed only the ordinary USER article workspace as a resumable Financial task. In a fresh chat the user explicitly said `继承财经写作系统`, which is a Named CONTINUE under Universal v3.7, yet the system-level durable work did not have an exact Financial task manifest/checkpoint to resolve. The chat incorrectly fell back to bare USER discovery and resumed `financial-writing:main` / the ice-snow article instead.

This file normalizes the already-existing system work into an explicit resumable engineering task. It does not turn historical evals into current authority; current `main` remains engineering authority.

## Current live evidence

Latest real article trajectory: `ice-snow-economy-20261013`.

Current article state is terminal at `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN` after a full DUAL workflow and FINAL_AUDIT PASS. It therefore serves as the newest live E2E sample for the global audit.

Two canonical article identities are recorded in owner state:
- `FINANCE_DEEP_DOCX` sha256 `e863a831a1659b993ee9b46f578d9eb8c70f56ecc1de1b74f1d65a10fdb68922`;
- `FINANCE_BROAD_DOCX` sha256 `10dcfb53e46d629b669045b3f91b1f90169ed47ff4cd168745209ee17ff34895`.

However a fresh-window artifact lookup found neither article Word in current Conversation/Library. Only audit-report copies were discoverable. Therefore current terminal metadata proves artifact identity/history but does not prove current user-accessible binary availability.

## Confirmed defect FW-GA-20261013-01 — system-task continuation routing

Classification: `STARTUP_OR_ROUTING_INSTRUCTION + OWNER_BINDING / TASK_REGISTRATION`.

Evidence:
- Universal `ENTRYPOINT.md` says `Named CONTINUE → exact owner/task manifest + short checkpoint first; global discovery only if ambiguous`.
- The user's phrase `继承财经写作系统` was named, not bare.
- Financial continuity had no explicit engineering/system-audit task candidate even though system-audit durable evidence existed.
- The prior chat therefore incorrectly entered Bare CONTINUE and selected the default USER article workspace.

Repair direction:
1. keep ordinary `financial-writing:main` as the only DEFAULT USER candidate;
2. register this system audit as `SYSTEM_INFRA / EXPLICIT_ONLY` under the Financial index;
3. named phrases such as `财经写作系统`, `财经写作全局审视`, `Financial Writing system audit` must resolve here before bare discovery.

## Confirmed defect FW-GA-20261013-02 — artifact lifecycle / visible delivery recurrence

Classification: `ARTIFACT_IO / DELIVERY / EVIDENCE_OR_PROPAGATION`.
Recurrence: `RECURRED_AFTER_FIX`.

Prior incident `FINANCIAL_LIVE_E2E_TASK_OUTPUT_CONTRACT_INCIDENT_2026-10-12.md` proved a visible-delivery mismatch: default DUAL required three files but the user saw only two. The repair added exact required-output reconciliation.

The current live trajectory passes that count/hash reconciliation yet exposes a higher-layer recurrence: all three output identities exist in STATE, but the two article Word binaries are not retrievable in the new chat. Current `owner_guard._validate_delivery_artifact_metadata` validates only `kind + file_name + sha256`; tests do the same. Therefore terminalization can succeed without a fresh user-accessible artifact reference.

The repair must not be another count check. It must move up one layer to artifact lifecycle semantics:
- distinguish immutable publication source / delivered-binary identity / current-session availability;
- never treat filename/hash metadata as proof that a file can be given to the user now;
- before visible delivery or cross-chat re-delivery, perform a fresh availability handshake;
- if the prior binary is unavailable, regenerate from durable publication source, rerun mechanical/render QA, bind a new real resource reference and report any new binary hash rather than pretending old byte identity survived;
- keep GitHub control-plane state independent of Library/Drive availability; external stores are artifact vault/reference surfaces, not task-state authority.

## Global review scope still active

Continue auditing current main across:
1. entry/routing/continuity;
2. TaskContract/workflow/state/lease/CAS;
3. research recall/source traceability/universe completeness;
4. editorial architecture/title/reader funnel/prose naturalness;
5. semantic audit and assurance boundaries;
6. Word generation/mechanical/render/visible delivery/artifact lifecycle;
7. feedback/system-impact/quality promotion;
8. rule ownership/stale consumer/legacy negative space;
9. tests/static audits/hosted CI/current live E2E;
10. complexity and operator experience.

The live ice-snow Deep/Broad articles must be reviewed as actual output evidence. Prior `CHAT_SELF_REVIEW=PASS` is not accepted as independent proof of writing quality.

## Resume instruction

Future explicit continuation should use one of:
- `继承财经写作系统`
- `继续财经写作全局审视`
- `继承：financial-writing:system-audit`

Recovery must read this task manifest + HANDOFF first, show the pre-resume stage, perform takeover when it is a new chat, then continue from the current `next_action`. Do not fall back to `financial-writing:main` unless the user is actually resuming/writing an article.
