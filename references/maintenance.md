# Maintenance — Cognition, Decision and Governed Evolution

Revision: `2.0-candidate`
Updated: `2026-10-15`
Owner: `DOMAIN:financial_writing`

## Purpose

Maintenance governs how problems, user feedback, learned methods, failed outputs, code changes and quality evidence become durable Financial changes. It does not own article prose or parent/common authority.

UAOS owns common/cross-domain governance and the shared cognition/evolution method. Financial owns its business/product/writing rules and domain promotion.

## Core principle

**Do not move directly from “someone suggested a fix” to production mutation.**

For material problems/changes, the path is:
`signal -> cognition -> evidence/research -> assumption challenge -> candidate alternatives -> counterexamples -> DecisionEnvelope -> candidate implementation -> reproducible evaluation -> owner promotion -> production reread -> live observation -> keep/repair/rollback/retire`.

The user's observed failure and desired outcome are high-weight evidence. The user's proposed mechanism is a candidate unless explicit authorization/requirement makes it itself the required behavior.

## Current authority surfaces

- `UAOS_SKILL.md` — domain entry/current execution guidance;
- `docs/product_requirements.md` — user/product requirements;
- `docs/architecture.md` — Financial architecture;
- `config/EXECUTION_CONTRACT.json` — current product/execution contract;
- `financial_writing_agent/workflow_spec.py` — stable business stage graph;
- `financial_writing_agent/writing_kernel.py` — focused internal pass DAG;
- `financial_writing_agent/cognition_governance.py` — DecisionEnvelope, saturation and knowledge contracts;
- `financial_writing_agent/story_quality.py` — StoryBlueprint and PublicationFitness;
- `financial_writing_agent/current_admission.py` — current 1.0 admission wrapper over the canonical owner state machine;
- `financial_writing_agent/owner_guard.py` — canonical/historical business state transitions;
- `financial_writing_agent/owner_lifecycle.py` — recovery/system-impact lifecycle;
- `financial_writing_agent/proactive_resolution.py` — recoverable dependency resolution/user-escalation gate;
- `knowledge/METHOD_KNOWLEDGE_CATALOG.json` — durable method knowledge;
- `evals/PROBLEM_EVOLUTION_JOURNAL.md` — causal problem/evolution index;
- `financial_writing_agent/quality_regression.py` + `evals/` — promotion/regression evidence;
- `workspaces/articles/{task_id}` — article business truth.

No second Financial controller/task index/lease/resume system is allowed.

## Always-on problem detection and cognition

Every detected defect, user correction/rejection, degraded result, contradiction, repeated repair, knowledge gap or unreliable-goal signal activates the UAOS problem-response floor:
1. micro diagnosis;
2. macro goal/topology alignment;
3. challenge at least one governing assumption/boundary/causal explanation;
4. relevant external method/architecture research.

Material/systemic problems add counterexample search and stronger verification proportional to risk. Familiarity is not a waiver.

Ordinary material business judgments still require evidence, alternatives, counterexamples and verification, but they do not automatically require heavy architecture research unless a problem or architecture/governance change triggered it.

## Decision Envelope

For a material judgment, retain:
- objective and operation;
- evidence/source families;
- learned items/categories;
- assumptions challenged;
- at least two credible alternatives;
- advantages/failure modes/fit/misfit;
- counterexamples;
- rejected paths;
- selected candidate/rationale;
- search-saturation evidence;
- verification plan;
- remaining unknowns;
- knowledge/evolution disposition.

Mechanical actions use deterministic admission/verification instead of fake deliberation records.

## Broad search and saturation

Do not stop after the first plausible method or repair. Search materially different source families and explicitly search for alternatives/counterexamples.

For material decisions, preserve sweep results. Convergence is admissible only after two consecutive sweeps produce no decision-changing candidate, failure mode, counterexample or changed decision. A later material discovery invalidates saturation.

This is an auditable approximation to broad traversal; never claim literal exhaustive internet coverage.

## Knowledge retention

Learned knowledge should survive the current task even when it is not adopted.

Retain:
- useful domain facts/relationships with freshness semantics;
- external methods with source, fit and misfit;
- rejected architecture/writing candidates and why they failed;
- repeatable failure patterns;
- verification/eval methods.

Knowledge cataloging is not production promotion. A conflicting record cannot be marked validated until conflict is resolved/bounded.

## Candidate implementation

Material repo changes use:
`candidate branch -> draft/normal PR -> owner-appropriate CI/evals -> contradiction scan -> controlled merge -> production reread -> production checks -> live observation`.

Do not patch `main` directly for convenience. Do not weaken tests simply because a candidate fails an old invariant; first decide whether that invariant remains valid. If valid, preserve compatibility. If intentionally retired, update authority + migration/eval evidence coherently.

## Product/architecture rebuild

A major rebuild must reconcile:
- user outcome;
- functional requirements;
- non-functional constraints;
- business workflow/state;
- internal execution topology;
- failure/recovery;
- evidence/assurance;
- acceptance/evals;
- ownership boundaries;
- migration/historical compatibility;
- explicit non-goals.

Documentation alone is not evidence that the rebuild works.

## Proactive resolution before asking the user

If missing information may be recoverable from current state, durable context, approved samples, connected sources or public evidence, attempt proportionate recovery first and use `proactive_resolution.py` for owner-native receipt/admission when applicable.

Ask the user only when the missing item is a fact/preference/approval/authorization that cannot safely be inferred, alternatives materially change the result with no defensible default, capability/evidence is genuinely unavailable, safety/permission requires explicit choice, or the user requested confirmation.

## Problem-to-action closure

A confirmed problem must end in:
- repair attempted/executed;
- concrete blocker/required choice;
- evidence-backed no-change.

Recommendation-only is not a valid terminal when Financial currently has an authorized repair path.

## Durable problem/evolution history

Every evolution-relevant/material problem must preserve enough causal history to explain future decisions:
- symptom/impact;
- detection source;
- micro diagnosis;
- macro/topology alignment;
- challenged assumption;
- research/method evidence;
- alternatives/rejected/failed paths;
- selected action;
- verification/eval evidence;
- result/remaining unknowns/rollback conditions;
- parent-upcall status if applicable.

Do not rewrite failures into a success-only history after the repair lands.

## Promotion rules

One article or one feedback event may create a candidate, never silent universal authority.

Domain-wide promotion requires:
- justified generalization scope;
- relevant counterexamples;
- reproducible regressions/evals;
- no unresolved authority contradiction;
- owner-scoped controlled promotion;
- post-promotion observation.

Cross-domain/common-capability changes are sent to UAOS as parent guidance/upcall. Financial must not directly mutate parent authority from child scope.

## Assurance

Report only what evidence proves:
- configured rule/document: `DECLARED`;
- executable gate + passing behavior tests: executable/trajectory evidence;
- same-chat semantic review: `CHAT_SELF_REVIEW`;
- distinct executor/provider trace: potentially independent evidence;
- live user/article outcome: outcome evidence.

A green deterministic test cannot certify semantic writing quality, and a role label cannot certify independence.

## Anti-bloat

Before adding a subsystem ask:
- can the current owner/control/context/assurance/evolution mechanisms be extended instead?
- what mechanism does this replace or retire?
- does it create a second truth source or state machine?
- is its benefit measurable in regression/live evidence?

The 1.0 rebuild therefore keeps one Financial business owner and one state machine while adding focused internal passes and admission/fitness contracts.
