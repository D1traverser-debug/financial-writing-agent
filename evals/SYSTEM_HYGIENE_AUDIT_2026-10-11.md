# Financial Writing System Hygiene Audit — 2026-10-11

Status: IMPLEMENTED__REGRESSION_VALIDATION_PENDING
Scope: harness / Agent runtime / Skill boundaries / Continuity recovery / package hygiene / obsolete and redundant pollution sources

## Trigger
The user requested a structural audit of the Financial Writing system, explicitly including harnesses, agents, skills and obsolete/redundant pollution sources. This audit treats stale recovery metadata, test-only production payloads, obsolete execution instructions and replayable stale state as system pollution rather than article-quality defects.

## Architecture baseline
During this audit a concurrent, non-overlapping commit added `continuity/AGENT_MANIFEST.json`. It was inspected before rebasing this maintenance work. The manifest declares the same `FINANCIAL_WRITING_AGENT_RUNTIME` owner, a single Skill entrypoint, the existing hybrid runtime surfaces and the existing `WritingState + engine/controller` authority. It does not introduce a second workflow authority.

It also explicitly records that the current Skill is above the Universal thin-router target. That confirms Skill size/duplication as architecture debt, but not as safe-delete garbage. The hygiene regression now checks the Agent manifest owner/entrypoint/state-transition references against the current owner contract instead of ignoring this architecture surface.

## Finding 1 — Continuity recovery surface lagged behind the owner runtime
The repository authority had already moved to Financial Writing Agent v0.8, execution capability profile v8, methodology receipt contract 1.3 and the proof-bearing `run_semantic_audit_stage` gateway. However the active `financial-writing:main` task manifest and handoff still described v0.7 and receipt 1.2.

This did not break the code path, but it polluted fresh-chat recovery: a continuation reader could be routed toward an obsolete contract even while current CI was green.

### Repair
- task manifest reconciled to `FINANCIAL_WRITING_AGENT_V0_8` while preserving `resume_epoch=2` and the active lease;
- handoff reconciled to v0.8 / receipt 1.3 / capability profile v8 semantics;
- regression test now cross-checks Agent manifest, pyproject, Universal adapter, capability profile, task manifest, handoff and Task Index.

## Finding 2 — runtime next-action hints still instructed the obsolete semantic PASS path
`runtime_service._next_action` told callers at audit stages to use `submit_research_audit`, `submit_hook_audit`, `submit_style_audit`, `submit_editorial_audit` or `submit_final_audit`. In v0.8 those public submit tools are intentionally REVISE/FAIL-only; semantic PASS certification must use `run_semantic_audit_stage`.

This was an instruction/runtime contract drift: the public API correctly rejected chat-bridged PASS, but the task summary told callers to attempt it.

### Repair
Audit-stage `next_action` now points semantic PASS to `run_semantic_audit_stage`; FINAL_AUDIT still requires the explicit knowledge-writeback PASS/N_A decision before owner-runtime final certification.

## Finding 3 — test-only executors were shipped in the production wheel
`financial_writing_agent/adapters/mock.py` contained only test doubles (`PassExecutor`, `SequenceExecutor`, `ExplodingExecutor`) and was imported only by runner tests. Because setuptools includes `financial_writing_agent*`, the module was part of the published runtime package.

### Repair
- test doubles needed by `tests/test_runner.py` moved into the test file;
- production `financial_writing_agent/adapters/mock.py` removed;
- repository regression asserts the production path stays absent;
- isolated-wheel smoke now asserts `financial_writing_agent.adapters.mock` cannot be resolved after installation.

## Finding 4 — invalidated semantic gate payloads could survive as stale working-state pollution
Gate invalidation reset a gate to `NOT_RUN` but did not universally clear the same-name `WritingState.working` payload. Semantic audit payloads are stored under the gate name. Therefore old provenance material could remain after upstream revision.

Separately, runtime proof detection only checked that some `EXECUTOR_START` and some `EXECUTOR_END` existed after the latest stage entry; it did not require their order.

The combination created an unnecessary replay surface: stale audit payload + later generic stage trace could become more admissible than intended.

### Repair
- setting any gate to `NOT_RUN` now removes its same-name working payload;
- semantic execution proof requires an ordered `EXECUTOR_START → EXECUTOR_END` sequence after the latest `STAGE_ENTER`;
- regression tests cover stale-payload clearing and END-before-START rejection.

## Finding 5 — existing CI had hygiene blind spots
The static audit already protected v0.8 code/version alignment, 18-tool inventory, intentional reference mirrors and known obsolete files. The wheel smoke verified installability and packaged resources. Neither surface checked current Continuity recovery metadata, Agent-manifest alignment, or whether test-only package modules were excluded from the wheel.

### Repair
- new system-hygiene regression covers Agent/current-owner/recovery alignment;
- wheel smoke explicitly rejects the removed mock adapter;
- existing static audit remains the rule-ownership/reference-bundle authority instead of duplicating another root audit implementation.

## Inspected but deliberately retained
The following are not deleted in this pass:

1. **Three reference trees** — `references/*`, Skill references and packaged references are intentional byte-identical mirrors with different deployment roles. Current static audit enforces identity, so they are controlled mirrors rather than uncontrolled duplication.
2. **Historical eval/audit artifacts** — old system audits, the rejected offshore-wind artifact and held-out baselines are provenance/regression evidence. Deleting them would weaken the quality-evidence chain.
3. **`runner.py` / `runtime_factory.py` versus `runtime_service.py`** — the former is a standalone/developer outer-loop surface; the latter is the MCP service façade. Both share the same engine/controller state authority. No second state machine was found here.
4. **Current Site spec** — only the contract/spec remains; legacy Site PoC runtime files already appear removed. The spec is still needed for future deployment gates.
5. **`network_safety.py`** — currently a possible unused-code candidate, but dependency evidence is insufficient for safe deletion in this pass.
6. **Large Skill surface** — `SKILL.md` still repeats a meaningful amount of stage detail also present in references, and the new Agent manifest explicitly marks it above the thin-router target. Static tests intentionally pin many markers there. This is context/maintenance debt, but collapsing it without an eval could change behavior. It is recorded as refactor debt, not deleted as garbage.

## Harness / Agent / Skill assessment
- **Agent architecture:** one business owner, one declared Skill entrypoint and one canonical state/transition authority; no duplicate agent control plane found.
- **State-machine authority:** one canonical `WritingEngine + WorkflowController`; no second competing transition authority found.
- **Public MCP authority:** one registration surface, `financial_writing_agent/plugin_server.py`.
- **Semantic audit authority:** v0.8 owner-runtime gateway is structurally separate from conservative chat-bridged submissions.
- **Skill authority:** current v0.8 Skill is aligned with the main runtime, but its size/duplication remains a future compaction target requiring behavioral evaluation.
- **Quality-promotion harness:** remains separate from article runtime correctness; no cleanup here changes the existing evidence ceiling.

## Validation plan
Current-head CI must pass:
- OpenAI Agents SDK smoke;
- MCP Streamable HTTP smoke;
- unit/trajectory suite including the new hygiene regressions;
- executable contract evals;
- static rule-ownership/reference-bundle audit;
- isolated wheel install with test-module exclusion check;
- DOCX render smoke.

Until that current-head run is green and the authoritative manifest/handoff/audit are reread, this maintenance turn must not be reported as COMMITTED.

## Changed surfaces
- `financial_writing_agent/models.py`
- `financial_writing_agent/runtime_service.py`
- deleted `financial_writing_agent/adapters/mock.py`
- `tests/test_runner.py`
- new `tests/test_system_hygiene.py`
- `.github/workflows/ci.yml`
- `continuity/tasks/financial-writing-main/TASK_MANIFEST.json`
- `continuity/tasks/financial-writing-main/HANDOFF.md`
- this audit record

No article-level prose rule was added during this hygiene cleanup.
