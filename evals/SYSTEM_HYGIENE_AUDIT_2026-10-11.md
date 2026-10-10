# Financial Writing System Hygiene Audit — 2026-10-11

Status: REGRESSION_VERIFIED__STRUCTURAL_DEBT_REMAINS
Scope: harness / Agent runtime / Skill boundaries / Continuity recovery / package hygiene / obsolete and redundant pollution sources

## Trigger
The user requested a structural audit of the Financial Writing system, explicitly including harnesses, agents, skills and obsolete/redundant pollution sources. This audit treats stale recovery metadata, test-only production payloads, obsolete execution instructions and replayable stale state as system pollution rather than article-quality defects.

## Architecture baseline
During this audit a concurrent, non-overlapping commit added `continuity/AGENT_MANIFEST.json`. It was inspected before rebasing this maintenance work. The manifest declares the same `FINANCIAL_WRITING_AGENT_RUNTIME` owner, a single Skill entrypoint, the existing hybrid runtime surfaces and the existing `WritingState + engine/controller` authority. It does not introduce a second workflow authority.

It also explicitly records that the current Skill is above the Universal thin-router target. That confirms Skill size/duplication as architecture debt, but not as safe-delete garbage. The hygiene regression now checks the Agent manifest owner/entrypoint/state-transition references against the current owner contract instead of ignoring this architecture surface.

## Confirmed pollution and repairs

### 1. Continuity recovery drift
The owner had already moved to v0.8, capability profile v8, methodology receipt contract 1.3 and proof-bearing semantic audit execution, while the active manifest/handoff still described v0.7 and receipt 1.2.

**Repair:** task manifest and handoff reconciled to v0.8 without changing `resume_epoch=2` or the active lease. Regression now cross-checks Agent manifest, pyproject, Universal adapter, capability profile, task manifest, handoff and Task Index.

### 2. Obsolete audit-stage next actions
`runtime_service._next_action` still directed audit PASS toward `submit_*audit`, even though v0.8 intentionally permits those surfaces only for conservative REVISE/FAIL and reserves PASS for `run_semantic_audit_stage`.

**Repair:** all semantic audit next actions now point PASS certification to the owner-runtime gateway; FINAL_AUDIT preserves the knowledge-writeback prerequisite.

### 3. Test-only code in the production wheel
`financial_writing_agent/adapters/mock.py` contained only runner test doubles but was shipped because setuptools includes `financial_writing_agent*`.

**Repair:** runner test doubles moved into the test file, production mock module deleted, repository regression protects the deletion, and isolated-wheel smoke asserts the module is absent after installation.

### 4. Stale semantic working payload replay surface
Gate invalidation reset semantic gates to `NOT_RUN` but could leave the same-name payload in `WritingState.working`. Runtime proof detection also accepted unordered presence of `EXECUTOR_START` and `EXECUTOR_END` after the latest stage entry.

**Repair:** any gate reset to `NOT_RUN` clears its same-name working payload; semantic execution proof now requires ordered `EXECUTOR_START → EXECUTOR_END` after the latest `STAGE_ENTER`. Regressions cover stale-payload clearing and END-before-START rejection.

### 5. Harness blind spots
Static audit already protected version/rule ownership, 18-tool inventory, known obsolete files and byte-identical reference mirrors. Wheel smoke verified installability but not test-module exclusion. Neither surface checked the active Continuity recovery state against the current Agent architecture.

**Repair:** a dedicated system-hygiene regression now checks Agent/current-owner/recovery alignment; wheel smoke rejects the removed mock adapter. Existing static audit remains the canonical rule/reference audit instead of duplicating another root policy harness.

## Inspected but deliberately retained
1. **Three reference trees** — source references, Skill references and packaged references are intentional controlled mirrors with distinct deployment roles; static audit enforces byte identity.
2. **Historical eval/audit artifacts** — system audits and rejected/held-out artifacts are provenance/regression evidence, not garbage.
3. **`runner.py` / `runtime_factory.py` versus `runtime_service.py`** — standalone/developer outer loop versus MCP service façade over the same engine/controller authority; no second state machine found.
4. **Current Site spec** — legacy Site PoC runtime files are absent; the remaining spec is a deployment contract.
5. **`network_safety.py`** — possible unused-code candidate, but dependency evidence is insufficient for safe deletion in this pass.
6. **Large Skill surface** — current `SKILL.md` remains above the Agent manifest's thin-router target and repeats meaningful stage detail also present in references. Static tests intentionally pin many of those markers. This is confirmed architecture/context debt requiring a separately evaluated compaction; deleting or collapsing it in this hygiene pass would risk behavior change.

## Harness / Agent / Skill assessment
- **Agent architecture:** one business owner, one declared Skill entrypoint and one canonical state/transition authority; no duplicate agent control plane found.
- **State machine:** one canonical `WritingEngine + WorkflowController` authority.
- **Public MCP:** one registration surface, `financial_writing_agent/plugin_server.py`.
- **Semantic audit:** proof-bearing owner-runtime gateway is structurally distinct from conservative chat-bridged submissions.
- **Skill:** current v0.8 semantics are aligned, but thin-router compaction remains open debt.
- **Quality-promotion harness:** remains separate from article runtime correctness; this cleanup does not raise the prose-quality evidence ceiling.

## Validation
Behavioral head: `dd7114beadc6741f8b998d4978c7208d45e7c16d`

GitHub Actions:
- run: `38087767904`
- job: `114317766154`
- result: PASS

Passed surfaces:
- OpenAI Agents SDK smoke;
- MCP Streamable HTTP smoke;
- unit/trajectory suite including new hygiene regressions;
- executable contract eval baseline;
- static rule-ownership/reference-bundle audit;
- isolated wheel install including test-module exclusion check;
- DOCX render smoke.

This establishes regression-verified harness/runtime/package hygiene for the covered changes. It does not establish provider-attested isolated review, better prose, or improved publication performance.

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
