# ChatGPT Site deployment specification — Financial Writing Agent v0.8

## Goal

If a private Site/MCP deployment is used in the future, it must act only as a **capability transport inside the existing single Financial owner trajectory**. It must not create a second business-state authority, alternate workflow, alternate terminal semantics or fallback runtime.

Current product path remains:

`ChatGPT request → Financial owner on GitHub main → main/workspaces/articles/{task_id} → canonical workflow → Word delivery`.

Canonical execution contract: `continuity/FINANCIAL_OWNER_EXECUTION.json`.

## Security boundary

Do not enable public/workspace/multi-user sharing until tenant isolation, authorization, task/artifact namespaces and cross-user access tests exist.

## Runtime invariant

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`

Mandatory dependency failures fail closed at the exact affected owner state. Do not silently fall back to ephemeral local disk, free-form writing, duplicate tasks, legacy SQLite WritingState or an alternate plugin task store.

## State authority

A Site/MCP deployment must read and mutate the same durable owner state under:

`main/workspaces/articles/{task_id}`

It may not treat local SQLite, process memory, server-local files or a separate database as authoritative Financial task state unless a future contract explicitly replaces the GitHub-main authority with a migration that updates every current consumer and regression test. Historical Git code/evals are not such a migration.

Every material mutation must preserve task/output invariants, bind the latest main state identity, perform conflict-safe write semantics and reread authoritative state/artifacts before COMMITTED.

## Responsibility split

- ChatGPT/model capability: research, synthesis, TopicDNA, structures, current search reconnaissance, titles and drafting.
- Web capability: current public evidence when the stage requires it.
- Deterministic/Python capability: schema/guard checks, output reconciliation and mechanical QA.
- Document capability: Word generation/render inspection.
- Optional provider-attested review capability: stronger review evidence only when real provider identity/trace exists.
- Site/MCP: transport/invocation convenience for those capabilities; **not a business-state owner**.
- Universal maintenance/evolution control plane: consumes escalated non-authoritative owner signals for shared/systemic defects.

Financial Writing has no image-generation, cover, section-image, avatar, sticker or image-insertion workflow.

## Semantic review authority

A Site may host a stronger reviewer capability, but a semantic PASS claim is valid only when the exact review action has the promised provider/runtime evidence. Typed payloads, tool names or the legacy token `INDEPENDENT_EXECUTOR` are not proof by themselves.

If stronger review is unavailable, the same owner trajectory remains at `CHAT_SELF_REVIEW` assurance and current bounded terminal semantics. Missing stronger review must not select another workflow or state store.

## Task/output contract

Default distribution mode is `DUAL` unless the user explicitly narrows it with exact prompt evidence. Default delivery is `WORD_FILE_ONLY` and requires:

`FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX`

`TaskContract.required_outputs` must exactly match distribution mode; no Site tool may silently narrow the output set.

## Recovery and system impact

A review FAIL persists a canonical repair target. Recovery uses that persisted cursor, requires repair evidence and invalidates stale target/downstream evidence.

Material `USER_EDIT`, `USER_FEEDBACK` and `USER_REJECTION` create durable owner evidence and, where applicable, an open system-impact obligation. Systemic closure requires accepted diagnosis plus maintenance/validation evidence at least `REGRESSION_VERIFIED`. Site-local success is not enough to close a shared-control-plane defect.

## Research/editorial invariants

- FINANCE_DEEP is `MATERIAL_COMPLETE` relative to the bounded audited research universe.
- FINANCE_BROAD is `SELECTIVE_TRAFFIC` but must expose a truthful non-niche financial stake to a cold finance reader.
- Universe Coverage is class-accounted; representative-stock shortcuts do not satisfy Deep completeness.
- Multi-company Deep work carries MATERIAL companies forward and leaves a decision-useful but non-actionable comparison map.
- Market Explanation is explicitly scoped `REQUIRED | NOT_MATERIAL`; a company universe alone does not activate it.
- When active, separate economic benefit from market selection, compare mechanisms, preserve `why_this/why_not`, continuation/reversal conditions and causal-confidence boundaries.

## Reader Funnel / Authorial Prose

Reader Funnel covers audience-promise fit, information value, curiosity/concreteness balance, current search evidence, first-screen retention, continuation, completion payoff and title/opening payoff. Title pools need genuine strategy diversity, not synonym variants.

Natural Authorial Prose uses the current rubric for fidelity/responsibility, semantic contribution, argument progression, reader calibration, authorial selectivity, evidence specificity, structural/rhythm naturalness, template/redundancy control and uncertainty/rhetoric calibration. Template-cluster guards may force REVISE.

## Word contract

Deterministic Word enforces H1 `18pt`, H2 `15pt`, body `13.5pt`, H3 currently `12pt`, Chinese hierarchy, zero publication tables, zero underlines, no tail source appendix, every supplied A-share company/stock name bolded at exact occurrences, explicit semantic skim-anchor bolding, one final italic inline `风险提示：...`, required-file presence, stale-render cleanup and renderability.

## Promotion validation

Do not call a Site integration production-ready until all are true:
1. it enters the existing single Financial owner path rather than creating a Site-local task;
2. durable state/artifacts remain on the canonical main article workspace and survive restart/fresh chat;
3. legal stage/revision/invalidation/BLOCKED recovery paths pass;
4. default DUAL three-output contract cannot be narrowed without exact user override evidence;
5. semantic assurance claims match actual provider evidence;
6. material corrective feedback creates and exposes durable system-impact obligations;
7. deterministic Word QA and path privacy pass;
8. one user-authorized real article E2E includes interruption/recovery and fresh-chat recovery;
9. public/multi-user sharing remains disabled.

## Legacy quarantine

The former owner-native/plugin/SQLite second runtime has been **physically removed from the current repository tree**. Its Git history and historical evals may remain as evidence only. Reintroducing any retired runtime/discovery path listed in `config/retired_runtime_paths.json` is a regression and must fail current CI. A future Site integration must extend the single owner trajectory rather than restore those deleted task-state mechanisms.

## Canonical source

Repository: `D1traverser-debug/financial-writing-agent`  
Branch: `main`  
Skill: `skills/financial-writing-agent/SKILL.md`  
Execution contract: `continuity/FINANCIAL_OWNER_EXECUTION.json`