# Financial Writing Continuity Task Index

Machine/agent discovery surface for resumable user work in this repository.

- `052804dc-f66a-441d-8875-c7973366b072` — ACTIVE — owner `FINANCIAL_WRITING_AGENT_RUNTIME` — checkpoint `continuity/tasks/ai-pharma-writing/HANDOFF.md`
- `financial-writing-site-runtime:gate-a2` — ACTIVE — owner `FINANCIAL_WRITING_AGENT_ENGINEERING` — checkpoint `continuity/tasks/site-runtime-gate-a2/HANDOFF.md`

Rules:
- These checkpoints are subordinate to compatible Runtime state where a stronger Runtime checkpoint exists.
- Resume requires current-contract compatibility before stale stages/gates are reused.
- New-chat takeover retires the previous chat for the same task.
