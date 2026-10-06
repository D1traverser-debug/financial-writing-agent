# ChatGPT Site deployment specification

## Goal

Host the Financial Writing Agent as a Site-backed MCP plugin so the same runtime is available from ChatGPT web at home or work without any local installation.

## Non-negotiable workflow

The Site-hosted MCP must enforce this state machine and reject illegal stage submissions:

`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT -> COMPLETE`

A failed dependency or invalid transition must produce `BLOCKED`. There is no silent fallback to ordinary free-form writing.

## Responsibility split

- ChatGPT model: research, evidence synthesis, TopicDNA, structure, headlines, drafting, semantic audits.
- Site MCP runtime: legal transitions, schema validation, durable checkpoints, gate status, artifact identity, completion authority.
- Deterministic delivery: build article Word files and `WRITING_AUDIT_REPORT.docx`; mechanical checks must remain independent from semantic review.

## Durable state

Use the Site's supported structured persistent store for task checkpoints. One record per `task_id` must contain the complete serialized WritingState, including contract, current stage, gates, structured stage outputs, artifacts, trace, attempts, blocked reason, and updated_at.

Required operations:
- save checkpoint atomically after every material stage change;
- load by task_id;
- list most recently updated tasks;
- recover incomplete work in a fresh conversation without chat-memory dependence.

Notion and Google Drive are mirrors/governance destinations, not the executable checkpoint authority.

## Artifact storage

Use the Site's supported persistent file/object storage for generated article artifacts. Never store only an ephemeral filesystem path.

Required artifacts for WORD_FILE_ONLY:
- `FINANCE_DEEP.docx` when applicable;
- `FINANCE_BROAD.docx` when applicable;
- `WRITING_AUDIT_REPORT.docx`.

The final tool result must expose each artifact as a ChatGPT-usable file reference or supported downloadable file result, not merely a server-local path. After delivery, ChatGPT may copy formal outputs to Google Drive and update Notion governance pointers.

## MCP tools

Expose at least:
- `start_writing_task`
- `get_writing_task`
- `list_recent_writing_tasks`
- `submit_research`
- `submit_research_audit`
- `submit_editorial_plan`
- `submit_headlines`
- `submit_draft`
- `submit_editorial_audit`
- `build_and_mechanically_audit_delivery`
- `submit_final_audit`

Tool descriptions must accurately describe stage requirements and write side effects.

## Recovery behavior

For a continuation request such as `继续`, first list recent incomplete tasks. If exactly one relevant task is found, load it and continue from its persisted `current_stage`. Do not ask the user to repeat information already present in the checkpoint.

## Google Drive / Notion mirror

After task start, material stage transitions, block/pause, and completion, mirror a compact status record to Notion `CURRENT_RUN -> ACTIVE_TASK_POINTER` when the connected Notion action is available. Keep Google Drive `CURRENT_STATE` WRITING summary aligned without overwriting unrelated domains.

After COMPLETE, copy formal Word deliverables to the configured Google Drive final-artifact location when Drive write access is available. Runtime completion must not depend on Notion/Drive availability; mirror failures must be surfaced separately and must not corrupt the executable checkpoint.

## Validation before promotion

Do not call the deployment production-ready until all of these pass:
1. MCP tools discoverable from a fresh ChatGPT conversation.
2. Start task persists a checkpoint.
3. Fresh conversation can list and recover that task.
4. Illegal stage submission is rejected.
5. A revision loop returns to the correct prior stage.
6. Word artifact(s) are generated and returned as usable files.
7. Mechanical audit runs.
8. Final semantic audit gates COMPLETE.
9. Notion/Drive mirroring succeeds or reports a precise mirror-only failure.
10. One real article E2E includes a deliberate interruption and recovery.

## Canonical source

Repository: `D1traverser-debug/financial-writing-agent`
Branch: `main`
Skill: `skills/financial-writing-agent/SKILL.md`
