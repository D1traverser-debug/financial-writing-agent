# Legacy Writing System → Agent Gap Audit — Maintenance Checkpoint

> Maintenance-only task checkpoint. This file is **not** a production writing rule and must not be loaded as normal Agent behavior. Its purpose is to make this one maintenance task resumable after disconnects/new chats.

## Task identity
- Goal: compare the legacy Google Drive/Notion writing system against the current GitHub `financial-writing-agent`; add only still-valid legacy semantics that are absent or insufficiently executable in the Agent.
- Isolation rule: do **not** modify the deployment branch while Site/Agent deployment is in progress.
- Base/deployment-authoritative commit when this audit started: `1703aeadeeeb13362657e3eb6c031cf454542808`.
- Isolated working branch: `writing-system-gap-hardening`.
- Current branch head at checkpoint creation: `40d8ea106bb56b49c58383d015aae237b66f8a84`.
- Merge-base: exactly `1703aeadeeeb13362657e3eb6c031cf454542808`; branch was ahead only, behind=0 at verification.
- Surface constraint: keep the current 16-tool MCP surface unchanged unless a capability is provably impossible to express through existing contracts; prefer references + schema/harness/gates/tests.

## Migration principles already fixed
1. Do not copy legacy prose wholesale. Migrate semantics, not historical file names/pointers.
2. New Agent architecture wins where it is strictly stronger (code-owned state machine, independent judges, deterministic delivery, explicit knowledge receipts, current DUAL/runtime design).
3. Every durable semantic has one canonical owner. Mirrors must stay byte-identical where existing CI requires it.
4. High-judgment rules belong in reference + independent semantic audit; low-judgment requirements should become schema/harness/runtime assertions where feasible.
5. Documentation-only presence is not considered executable coverage.
6. `learning inheritance ≠ task inheritance`: new tasks may reuse durable cognition/rules/experience, but must not inherit prior task stage/title/outline/draft/blockers/next action/artifacts unless the user explicitly requests resume/continue.
7. Do not resurrect legacy `CURRENT_RUN`, `ACTIVE_TASK_POINTER`, or old four-stage flow inside the new Runtime; map their useful semantics onto current persisted task state/gates.

## Legacy sources read for baseline
- Google Drive `00_CONTROLLER_写作主流程`.
- `10_RESEARCH_研究与证据`.
- `20_EDITORIAL_结构与表达`.
- `30_DELIVERY_格式与发布`.
- `40_ACCEPTANCE_写作验收`.
- `50_EVAL_新对话回归测试`.
- `60_MAINTENANCE_规则演进协议`.
- `90_RECOVERY_交接与恢复`.
- `99_QA_统一质量门禁`.
- Relevant Notion writing/knowledge/system pages and current GitHub packaged Skill/Runtime.

## Completed changes on isolated branch
### Reference/owner migrations
Updated canonical/package/runtime mirrors for:
- `style.md`: restored prompt/workflow leakage ban, fake-chat/performative wording checks, reorderable-paragraph/template-switch checks, answer-delay/forced suspense checks.
- `research.md`: restored explicit task-source completion accounting, omission scan, count reconciliation, freshness/time-integrity review, fact vs inference/expectation/rumor separation, and relevant A-share durable-knowledge recall semantics without reviving legacy pointers.
- `editorial.md`: strengthened section-level promise/payoff logic, hierarchy-trigger semantics, evidence-layer clarity, closing/authorial-stance constraints without fixed templates.
- `delivery.md`: strengthened bold scan skeleton, topic-specific risk composition, compression/loss boundary, file/artifact identity/readback expectations.
- `audit.md`: mapped legacy CoverageMatrix/Omission/Time/Source-completion ideas into the existing final-audit evidence model instead of creating a second QA authority.
- `maintenance.md`: added durable rule evolution, cold-start regression, task-state contamination prevention, and system-error handling principles.
- `knowledge.md`: separated durable cognition/experience from run-local task state; retained EventBase/IndustryBase/EvidenceCache/ArticleBase/StockBase-review-queue semantics as conceptual ownership, without falsely claiming one executable shared store already exists.
- `platforms.md`: restored use of current platform/account experience when platform optimization is requested, without promoting one sample into a permanent rule.

### Routing/ownership
- Updated `skills/financial-writing-agent/SKILL.md` with cold-start routing-level safeguards only; detailed method text remains in owner references.
- Updated `config/rule_ownership.json` to register the added semantics under unique owners.

### Code-level harness hardening
Modified `financial_writing_agent/harness.py`:
1. Every `TaskContract.source_ref` must be accounted for in `ResearchPackage.source_boundary` with `[FULL]`, `[PARTIAL]`, or `[UNAVAILABLE]`; silent omission now fails validation.
2. Every headline candidate `factual_anchor` must exactly match a `core_safe` claim in the frozen `ResearchPackage.evidence_ledger`; title-stage anchors can no longer be invented independently of research evidence.
3. No MCP tool was added/removed.

## Verified branch diff at checkpoint creation
Compared with base `1703ae...`: 27 commits ahead, 0 behind. Changed files are limited to rule mirrors, `SKILL.md`, `config/rule_ownership.json`, and `financial_writing_agent/harness.py`; deployment branch remains untouched.

## Current interruption point
The audit was at **Acceptance Contract structural-gap analysis** after reading `financial_writing_agent/schemas.py`.

Observed current `ModeAcceptanceContract` fields:
- selected title
- frozen headline factual anchor / primary gap / opening payoff
- selected structure name
- expected H1 count / section functions
- lead requirement
- side-focus statement
- company-selection basis

Legacy acceptance requirements still need a deliberate decision on whether/how to encode without over-constraining prose:
- per-H1 directional conclusion / reader information gap / payoff location;
- expected subordinate logical-block counts and when H2/H3 numbering should be triggered;
- explicit risk/disclaimer expectation in acceptance identity (currently guaranteed downstream, not frozen per mode);
- explicit bold/Word/compliance/knowledge-writeback acceptance obligations vs keeping those as downstream global gates;
- count-reconciliation / omission-scan proof fields vs semantic final-audit evidence only.

## Known test impact to resolve next
The new headline-anchor harness constraint will intentionally break old `tests/test_harness.py` fixtures because `_headline()` currently fabricates anchors such as `深度版标题对应的经核验公告数字`, while `_research()` contains only the core-safe claim `核心事实`, and `_state()` does not currently freeze a research package before acceptance-contract construction.

Do **not** weaken the new gate to make tests green. Update the fixtures so acceptance-contract tests include a frozen ResearchPackage and use genuine core-safe claims.

## Next exact actions
1. Update `tests/test_harness.py` fixtures to reflect the new evidence-backed headline contract and add explicit tests for:
   - missing task source accounting fails;
   - FULL/PARTIAL/UNAVAILABLE source accounting passes;
   - headline anchor absent from core-safe evidence fails;
   - valid core-safe anchor passes.
2. Decide the minimal non-conflicting extension of `ModeAcceptanceContract` for legacy section-level promise/payoff semantics. Prefer structured section acceptance objects rather than copying prose rules.
3. If schema changes are made, update `harness.py`, final-audit required evidence mapping, fixtures/evals, and mirrors as necessary.
4. Add cold-start regression scenarios specifically for:
   - new task does not inherit prior task state;
   - explicit resume does restore prior persisted task;
   - relevant durable learning can be reused without importing prior article structure/title/draft.
5. Run/inspect static ownership, mirror equality, unit/trajectory/eval contracts. Do not claim tests pass until actually executed in a runnable environment/CI.
6. Re-run base→branch diff, check that MCP tool surface remains 16 and Site deployment code is unchanged.
7. Update this checkpoint after each major group so a new chat can resume from `Next exact actions`.

## Explicit non-migrations / conflicts to preserve
- Do not restore legacy rule that every new conversation auto-recovers an active writing task. Current user requirement is learning inheritance without task inheritance; resume is explicit.
- Do not restore legacy Drive/Notion pointers as runtime authority.
- Do not replace the current code-owned stage machine with legacy START/RESEARCH/EDITORIAL/DELIVERY/ACCEPTANCE labels.
- Do not create a second QA/Acceptance authority parallel to `WritingAcceptanceContract` + runtime gates + `FinalAuditDecision`.
- Do not claim StockBase/EventBase/etc. are one executable synchronized store until that integration actually exists.

## Status
`IN_PROGRESS` — rules/reference migration partially complete; harness hardening started; Acceptance Contract schema/test work and final regression audit remain open.
