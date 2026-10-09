# Financial Writing Continuity v2

This reference defines cross-conversation task identity for Financial Writing Agent. It supplements the execution workflow; it does not replace stage/gate rules.

## Core rule
A chat is an execution window. A writing task is the durable object.

- New task: inherit durable writing rules, knowledge and validated learning only. Do not import another task's draft, title, stage, blockers, artifacts or `next_action`.
- Explicit continuation: recover the matching persisted task/ledger, then perform current-contract compatibility before executing the old `next_action`.
- Bare continuation discovery: only `USER + resume_eligible=true + resume_visibility=DEFAULT` may appear.
- `TEST`, `FIXTURE`, `EVAL`, `SYSTEM_INFRA`, `MIGRATION`, `EXPLICIT_ONLY` and `HIDDEN` never compete in ordinary bare inheritance.

## Runtime task metadata
Every new public Runtime writing task must persist:

- `task_id`
- `task_class = USER`
- `resume_eligible = true`
- `resume_visibility = DEFAULT`
- `contract_version`
- `runtime_version`
- `skill_version` when a stable Skill identifier is available
- `current_stage`
- exact `next_action`
- `updated_at`
- artifact/checkpoint identity through the existing Runtime state

Legacy checkpoints that predate these fields are parsed fail-closed as:

- `task_class = MIGRATION`
- `resume_eligible = false`
- `resume_visibility = EXPLICIT_ONLY`
- `contract_version = legacy-unclassified`

They remain readable by exact `task_id` for migration, audit and explicit continuation. They must not silently become ordinary USER candidates.

The existing `list_recent_writing_tasks` public tool is the Financial Writing owner-adapter for ordinary continuation during the current frozen 16-tool Site migration. It returns only safe USER/default-visible tasks. `get_writing_task(task_id)` remains the explicit diagnostic/migration path.

## Compatibility before Runtime resume
Classify the persisted task against the current Skill/runtime contract:

- `COMPATIBLE`: resume the checkpoint.
- `MIGRATABLE`: migrate the checkpoint/contract first, invalidate stale downstream receipts as required, then resume.
- `INCOMPATIBLE`: block obsolete execution semantics. Preserve only user requirements, source material, evidence and artifacts whose provenance remains valid; start a legal current control plane instead of replaying stale PASS receipts.

Tool availability alone is not compatibility. The current Skill capability/schema handshake remains mandatory.

## Standalone ShadowTaskLedger
A persisted standalone ledger uses the same continuity identity. Add these fields to the mandatory ShadowTaskLedger:

- `task_id`: stable externally persisted identifier when cross-chat continuation is claimed;
- `task_class = USER` for real user work;
- `resume_eligible`;
- `resume_visibility`;
- `contract_version`;
- `skill_version` or repository/commit reference used for the run;
- `checkpoint_ref` when the ledger is durably stored;
- `updated_at`;
- `current_stage` and exact `next_action`.

If there is no authorized durable location, keep the ledger in-session and **do not claim cross-conversation resumability**. A conversation-only ShadowTaskLedger is execution discipline, not persistence.

For explicit standalone continuation, the prior persisted ledger must be unambiguously identified and compatibility-checked. If its contract is obsolete, migrate or restart the control plane exactly as above. Never treat a prose chat summary as stronger authority than a durable ledger/artifact.

## Checkpoint events
Update the durable Runtime checkpoint or persisted ShadowTaskLedger after material state changes, including:

- task intent/output contract frozen;
- stage transition or gate verdict;
- selected title/acceptance contract frozen;
- deep mother draft or broad derivative frozen;
- revision invalidation;
- artifact creation/replacement;
- blocker/resume;
- completion;
- compatibility migration.

Do not wait until a chat is near its context limit.

## Fixture and eval discipline
Live contract/deployment validation must not pollute user continuation discovery. Internal tests/fixtures/evals must use their real non-USER task class or an isolated ephemeral data store. A production durable-store fixture may be read explicitly for diagnostics but must remain hidden from ordinary inheritance.

## Authority
Continuity metadata routes to the task. It does not duplicate writing workflow authority. The current Financial Writing Skill/code/runtime contract remains the owner of legal stages, gates, evidence and completion semantics.
