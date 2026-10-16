# Financial Common Behavior 1.3 Root-Scope Adoption

Status: `CANDIDATE_IMPLEMENTED__CI_PENDING`
Date: 2026-10-16
Owner: `DOMAIN:financial_writing`
Parent basis: `UAOS:FROZEN_REQUIREMENTS_v2.2 + COMMON_BEHAVIOR_ASSURANCE 1.3`
Failure class: `FC-PREMATURE-PROBLEM-FRAMING-AND-REPAIR-BEFORE-ROOT-SCOPE-001`

## Symptom

Financial already required research, alternatives, counterexamples and evolution disposition for material judgments, but the DecisionEnvelope did not separately prove the problem layer/root hypothesis before selecting a repair mechanism. A solution comparison could therefore look rigorous while still being anchored to the wrong diagnosis.

## Root-scope diagnosis

Competing hypotheses considered:

1. `LOCAL_IMPLEMENTATION`: only owner-lifecycle/system-impact code lacks fields. Rejected as the complete root because material decisions across the domain use the shared DecisionEnvelope.
2. `DOMAIN_ARCHITECTURE`: the entire writing architecture needs rebuilding. Rejected for this change because article identity, workflow ownership and publication quality architecture do not need replacement to enforce cognition ordering.
3. `COMMON_CAPABILITY / DOMAIN COGNITION BOUNDARY`: Financial needs an owner-native root-scope receipt inside its existing DecisionEnvelope before repair/no-change/evolution action. Selected.

The selected repair extends the existing cognition contract rather than adding a controller, journal, or parallel architecture advisor.

## Changes

- add explicit problem layers and root-cause hypotheses to `financial_writing_agent/cognition_governance.py`;
- keep root-cause hypotheses separate from repair alternatives;
- require an evidence-tested selected root hypothesis for every problem-triggered material judgment;
- for systemic/architecture-governance problems require cross-layer hypotheses, an upstream hypothesis, an evidence-rejected alternative and architecture reassessment evidence;
- reject direct promotion of a user/external framing to root cause;
- require a durable problem reference for domain-candidate or parent-upcall evolution dispositions;
- bump capability profile to 19 and Common Behavior minimum to 1.3.

## Rejected paths

- copy the UAOS parent kernel into Financial;
- create a second cognition controller;
- treat solution alternatives as if they were root-cause alternatives;
- rebuild the whole writing architecture because the parent failure class was architectural/control-plane level;
- change business release semantics for a behavior-profile-only upgrade.

## Verification

Primary regression: `tests/test_cognition_governance_v1.py`.

Required checks include:
- problem-triggered decisions fail without root-scope hypotheses;
- systemic problems fail when hypotheses remain in one layer;
- user/external framing cannot become root cause without falsification;
- a valid architecture decision emits a root-scope receipt and still satisfies the existing material judgment/evolution contract.

Live article outcome remains open after production promotion.
