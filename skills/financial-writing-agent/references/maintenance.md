# Maintenance — Cognition, Decision and Governed Evolution

Revision: `1.2`
Candidate extension: `2.0-candidate`
Updated: `2026-10-15`
Owner: `DOMAIN:financial_writing`

## Purpose

Maintenance governs how problems, feedback, learned methods, failed outputs and quality evidence become durable Financial changes. UAOS owns common/cross-domain governance; Financial owns Financial business/product/writing promotion.

## Core path

Do not move directly from a suggested fix to production mutation.

`signal -> cognition -> research/evidence -> assumption challenge -> alternatives -> counterexamples -> DecisionEnvelope -> candidate -> reproducible eval -> owner promotion -> production reread -> live observation -> keep/repair/rollback/retire`

User-observed failure and desired outcome are high-weight evidence. A proposed mechanism remains a candidate unless it is itself an explicit requirement.

## Authority surfaces

- `UAOS_SKILL.md`
- `docs/product_requirements.md`
- `docs/architecture.md`
- `config/EXECUTION_CONTRACT.json`
- `financial_writing_agent/writing_kernel.py`
- `financial_writing_agent/cognition_governance.py`
- `financial_writing_agent/story_quality.py`
- `financial_writing_agent/current_admission.py`
- `financial_writing_agent/owner_guard.py`
- `financial_writing_agent/owner_lifecycle.py`
- `financial_writing_agent/proactive_resolution.py`
- `references/proactive_resolution.md`
- `knowledge/METHOD_KNOWLEDGE_CATALOG.json`
- `evals/PROBLEM_EVOLUTION_JOURNAL.md`
- `financial_writing_agent/quality_regression.py`
- `workspaces/articles/{task_id}`

No second Financial controller/state machine is allowed.

## Always-on cognition

Any detected problem activates the UAOS-hosted cognition floor.

Every defect, correction/rejection, degraded outcome, contradiction, repeated repair or unreliable-goal signal requires micro diagnosis, macro/topology alignment, a governing-assumption challenge and relevant external research. Material/systemic problems add counterexamples, compare at least two credible alternatives and stronger verification. Familiarity is not a waiver.

Ordinary material business judgments require evidence, alternatives, counterexamples, saturation and verification; heavy architecture research is additionally mandatory when the problem or architecture/governance scope calls for it.

## Decision and search

Material judgments retain objective, evidence/source families, challenged assumptions, alternatives, fit/misfit, counterexamples, rejected paths, selected rationale, saturation, verification plan, unknowns and knowledge/evolution disposition.

Search across materially different source families. Stop only after two consecutive sweeps add no decision-changing candidate, failure mode, counterexample or changed decision. A later material discovery invalidates saturation. Never claim literal exhaustive internet coverage.

## Knowledge

Retain useful facts/relationships with freshness semantics, external methods with fit/misfit, rejected candidates, recurring failure patterns and eval methods. Cataloging is not promotion; unresolved conflicts block validated status.

## Candidate implementation

Material repo changes use `candidate branch -> PR -> CI/evals -> contradiction scan -> controlled merge -> production reread/checks -> live observation`.

Do not weaken an old invariant merely because a candidate fails it. Preserve valid compatibility; retire an invariant only with coherent authority, migration and eval evidence.

## Proactive resolution before asking the user

A missing ideal input is not automatically a user blocker. Recover from current state, durable context, approved samples, connected sources or public evidence when safe.

Use `record_proactive_resolution_state` to persist an evidence-bound recovery result and `require_user_escalation_admission` before escalating when applicable. Ask only when a required fact, preference, approval, authorization, safety choice or genuinely unavailable capability/evidence cannot be safely resolved.

## Problem-to-action closure

A confirmed problem ends in repair attempted/executed, a concrete blocker/required choice, or evidence-backed no-change. Recommendation-only is not terminal when an authorized repair path exists.

## Durable problem/evolution history

Every encountered problem must appear in durable history when material to system behavior or future decisions. Preserve symptom, source, diagnosis, challenged assumption, research evidence, alternatives/rejected paths, selected action, verification, result/unknowns/rollback conditions and parent-upcall status.

Do not rewrite the journal into a success-only narrative. Failures remain visible after repair.

## Promotion and Parent upcall boundary

One article or feedback event creates evidence/candidates, never silent universal authority. Domain-wide promotion needs justified scope, counterexamples, reproducible evals, no unresolved authority contradiction and owner-scoped controlled promotion. Then observe post-promotion behavior and keep, rollback or retire.

Cross-domain/common-capability changes upcall UAOS. Financial does not directly mutate parent authority from child scope.

## Assurance and anti-bloat

Configured rules are `DECLARED`; executable gates plus passing behavior tests are trajectory evidence; same-chat semantic review is `CHAT_SELF_REVIEW`; only distinct execution evidence may support independence. Green deterministic tests do not certify semantic writing quality.

Before adding a subsystem, ask whether existing owner/control/context/assurance/evolution mechanisms can be extended, what the new mechanism replaces, whether it creates a second truth source and whether benefit is measurable. The 1.0 rebuild keeps one Financial owner/state machine and adds focused passes plus admission/fitness contracts.
