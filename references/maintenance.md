# Maintenance module

## Ownership
Maintenance governs how user feedback, reliability incidents, external methods, code changes and quality evidence become durable Financial-domain changes. It does not own cross-domain task identity or article prose rules.

Cross-domain/systemic governance belongs to `D1traverser-debug/universal-agent-os@main`. Financial domain bindings are `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`; current business execution contract is `config/EXECUTION_CONTRACT.json`.

## Current authority
- `UAOS_SKILL.md` — current domain entry;
- `config/EXECUTION_CONTRACT.json` — one Financial execution contract;
- `financial_writing_agent/workflow_spec.py` — canonical stage/revision graph;
- `financial_writing_agent/owner_guard.py` — state mutation/output reconciliation;
- `financial_writing_agent/owner_lifecycle.py` — blocked recovery and system-impact lifecycle;
- `workspaces/articles/{task_id}` — durable article business truth.

The repository must not contain a domain-level controller/task index/lease/resume system. `continuity/` is a retired namespace and `config/retired_runtime_paths.json` mechanically guards against its return.

## Change method
For a material systemic change:
1. classify the user requirement/failure and its scope;
2. locate the unique owning rule/code/state surface;
3. inspect current authority and affected dependencies before editing;
4. compare credible alternatives when the mechanism is non-trivial;
5. prefer replacement/consolidation over adding a parallel adapter/state machine/rule copy;
6. add regression/evaluation evidence for the failure class;
7. verify business behavior and current-tree architecture hygiene;
8. promote only evidence-backed changes; keep uncertain ideas as candidates;
9. remove superseded current mechanisms rather than leaving them in the hot path.

A first material user correction is enough to create a system-impact signal. The user's desired outcome/constraint and observed failure are evidence; a suggested implementation mechanism is a candidate until validated.

## Scope and anti-overfit
One article, one feedback event or one market episode must not silently become a universal writing rule. Record the applicable scope, counterexamples and promotion evidence. Promote global rules only when evidence supports generalization.

## Reliability
Repeated failures are handled at the common failure class/root abstraction, not by stacking local exceptions. Any repair must check second-order effects: authority duplication, startup context growth, tool/read count, latency, state migration burden, test burden and hidden fallback paths.

## Assurance
Documentation, a role name, a configured tool or a green deterministic check is not proof of independent semantic judgment. Report the strongest assurance actually evidenced. Current same-chat semantic review remains `CHAT_SELF_REVIEW` unless a distinct execution context/provider trace exists.

## Historical evidence
Completed article states/receipts may contain identifiers from earlier implementations. They are immutable provenance only. Do not rewrite historical receipts to cosmetically remove old names; they have zero route/controller authority.
