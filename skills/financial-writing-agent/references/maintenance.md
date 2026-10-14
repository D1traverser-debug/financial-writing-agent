# Maintenance module

## Ownership
Maintenance governs how detected problems, user feedback, reliability incidents, external methods, code changes and quality evidence become durable Financial-domain changes. It does not own cross-domain task identity or article prose rules.

Cross-domain/common-capability governance belongs to `D1traverser-debug/universal-agent-os@main`. Financial owns its product requirements, architecture, business rules and domain evolution. Financial domain bindings are `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`; current business execution contract is `config/EXECUTION_CONTRACT.json`.

## Current authority
- `UAOS_SKILL.md` — current domain entry and hosted-governance use;
- `docs/product_requirements.md` — Financial product requirements and acceptance map;
- `docs/architecture.md` — Financial architecture/boundary;
- `config/EXECUTION_CONTRACT.json` — one Financial execution contract;
- `financial_writing_agent/workflow_spec.py` — canonical stage/revision graph;
- `financial_writing_agent/owner_guard.py` — state mutation/output reconciliation;
- `financial_writing_agent/owner_lifecycle.py` — blocked recovery and system-impact lifecycle;
- `financial_writing_agent/quality_regression.py` + `evals/` — domain regression/promotion evidence;
- `workspaces/articles/{task_id}` — durable article business truth.

The repository must not contain a domain-level controller/task index/lease/resume system. `continuity/` is a retired namespace and `config/retired_runtime_paths.json` mechanically guards against its return.

## Mandatory problem-response floor
Any detected problem activates the UAOS-hosted cognition floor before a repair is selected. A problem includes a defect, failed/degraded output, user correction/rejection, contradiction, repeated repair, uncertain goal satisfaction or other evidence that current behavior is unreliable.

For every problem, retain evidence for:
1. concrete/micro diagnosis;
2. macro goal/topology/architecture alignment;
3. challenge of at least one current governing assumption, boundary or causal explanation;
4. relevant external research.

Familiarity is not a waiver. Small problems may use a lightweight pass; material/systemic problems require deeper research, counterexamples and stronger verification. Research must affect or validate the diagnosis/repair; ceremonial browsing does not satisfy this requirement.

## Change method
After the mandatory problem-response floor, for a material systemic change:
1. classify the user requirement/failure and its scope;
2. locate the unique owning rule/code/state/product-requirement surface;
3. inspect current authority and affected dependencies before editing;
4. compare at least two credible alternatives for a systemic/domain-rule change, including failure modes;
5. prefer replacement/consolidation over adding a parallel adapter/state machine/rule copy;
6. state the generalization scope and counterexamples;
7. add regression/evaluation evidence for the failure class;
8. verify business behavior, product-requirement alignment and current-tree architecture hygiene;
9. promote only evidence-backed changes; keep uncertain ideas as candidates;
10. observe post-promotion behavior and keep, rollback or retire accordingly;
11. remove superseded current mechanisms rather than leaving them in the hot path.

A first material user correction is enough to create a system-impact signal. The user's desired outcome/constraint and observed failure are evidence; a suggested implementation mechanism is a candidate until validated.

## Product review and requirement completion
A major feature family, rebuild, or failure that exposes missing/incorrect product assumptions must trigger Financial product review using the UAOS-hosted `product_requirements_and_architecture_governance` capability.

The review must reconcile at least: user outcome, functional requirements, non-functional constraints, workflow/state, failure/recovery, evidence/assurance, acceptance/evals, authority boundaries and explicit non-goals. The resulting Financial-specific requirement/architecture changes are persisted in `docs/product_requirements.md` / `docs/architecture.md`; UAOS supplies the common method but does not own the domain business specification.

## Scope and anti-overfit
One article, one feedback event or one market episode must not silently become a universal writing rule. Record the applicable scope, counterexamples and promotion evidence. Promote domain-wide rules only when evidence supports generalization.

Every problem is evaluated for learning impact, but not every problem becomes a durable rule or release.

## Parent upcall boundary
If diagnosis points to a common capability, cross-domain contract, parent continuity/governance issue or scope arbitration need, Financial emits a non-mutating parent upcall with problem/evidence/unknowns/requested outcome. UAOS decides common/cross-domain evolution; Financial does not create a second controller or directly mutate parent authority from a child context.

Financial-owned business problems remain Financial-owned and use the domain lifecycle/regression mechanisms.

## Reliability
Repeated failures are handled at the common failure class/root abstraction, not by stacking local exceptions. Any repair must check second-order effects: authority duplication, startup context growth, tool/read count, latency, state migration burden, test burden and hidden fallback paths.

## Assurance
Documentation, a role name, a configured tool or a green deterministic check is not proof of independent semantic judgment. Report the strongest assurance actually evidenced. Current same-chat semantic review remains `CHAT_SELF_REVIEW` unless a distinct execution context/provider trace exists.

Product documentation is also not proof of product correctness: requirements must map to tests, evals or explicit observable acceptance evidence.

## Historical evidence
Completed article states/receipts may contain identifiers from earlier implementations. They are immutable provenance only. Do not rewrite historical receipts to cosmetically remove old names; they have zero route/controller authority.
