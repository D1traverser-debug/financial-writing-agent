# Financial Writing Agent — UAOS Cognition / Evolution / Product Audit

Date: 2026-10-15
Status: `CANDIDATE_EVALUATION`
Scope: Financial 0.8.4 candidate + UAOS 2.4.5 common-capability candidate

## Objective
Verify that Financial Writing can inherit UAOS cognition and governed-evolution capabilities without becoming a second controller, while retaining independent Financial product/business ownership. Also verify that parent product review has converted the existing feature set into a complete domain product-requirement/architecture/acceptance map.

## Initial findings
1. Financial 0.8.3 already declared `adaptive_deliberation_and_parent_guidance` and `governed_self_evolution`, but the parent `COMMON_CAPABILITIES` authority still contained pre-2.4.4 semantics: external research was conditional and protected-merge/complete-mediation wording was over-strong.
2. Financial 0.8.3 had a real business-evolution skeleton in `owner_lifecycle.py`: material feedback/system-impact records, root-cause layer, generalization scope, >=2 alternatives with failure modes, regression/eval plan, evidence refs, and maintenance closure requiring at least `REGRESSION_VERIFIED` evidence.
3. Financial maintenance guidance still said alternative comparison/research was conditional on mechanism complexity. This did not satisfy the current UAOS requirement that every detected problem receives research plus reflection.
4. `UAOS_SKILL.md`, `docs/architecture.md` and package comments still described UAOS routing/delegation in a way that could be read as a mandatory business hop, despite the corrected direct-domain session topology.
5. Financial had architecture documentation and extensive tests/evals, but no single current product requirements authority mapping user journeys/functions to owner surfaces and acceptance evidence.

## External method evidence
- Anthropic agent-evaluation guidance: evaluation-driven development forces product requirements to become concrete and helps prevent reactive production regressions.
- OpenAI evaluation guidance: variable AI behavior needs structured evals and repeatable testing during iteration.
- Google SRE incident/postmortem guidance: incidents should generate root-cause and systemic learning, not symptom-only repairs.

These sources support two borrowed properties, not wholesale framework adoption:
1. requirements -> executable/observable eval mapping;
2. problem -> root-cause/system learning loop.

## Governing assumptions challenged
- Rejected: declaring an inherited capability ID is sufficient proof that a child inherits the current semantics.
- Rejected: Financial needs its own copy of the UAOS cognition/evolution controller in order to inherit those skills.
- Rejected: every problem must become a durable writing rule.
- Rejected: parent product review means UAOS owns the Financial business specification.
- Rejected: normal Financial work must pass through a live UAOS router after the domain has been selected.

## Candidate architecture
### Parent/common layer
UAOS common capabilities own the reusable cognition/evolution/product-review method:
- every detected problem -> micro diagnosis + macro/topology alignment + governing-assumption challenge + external research;
- risk adds counterexample/independent evidence depth;
- every problem is evaluated for learning impact, but only evidence-backed scoped candidates are promoted;
- product review fills user outcome, functional/non-functional requirements, workflow/state, failure/recovery, assurance, acceptance/evals, non-goals and ownership boundaries.

### Financial domain layer
Financial owns:
- `docs/product_requirements.md` and `docs/architecture.md`;
- article identity/state/workflow/contracts;
- business rules and writing methods;
- material-feedback/system-impact lifecycle;
- domain regression/eval evidence and domain rule promotion.

Common/cross-domain changes use parent guidance/upcall. No child parent-controller/evolution catalog is introduced.

## Candidate changes
- UAOS common capability contract -> 1.5.0.
- UAOS v1.9 requirements delta for child cognition/evolution/product-governance inheritance.
- Financial capability profile -> 16 with minimum UAOS common contract 1.5.0.
- Financial version -> 0.8.4 candidate.
- Direct Financial work-plane semantics made explicit.
- Mandatory problem research/reflection floor added to Financial maintenance authority.
- `docs/product_requirements.md` added with user journeys, requirement/owner/evidence map, NFRs, failure/recovery, cognition/evolution contracts and completion criteria.
- Architecture and execution contract aligned to domain-owned product authority plus hosted common governance.
- Regression tests added to reject stale inheritance, mandatory parent proxy, parent-child identity equality and documentation-only product claims.

## Acceptance plan
Parent UAOS candidate:
- full `promotion-gate` CI PASS;
- current common contract = 1.5.0;
- v1.9 included;
- existing direct-domain/identity/anti-bloat invariants remain PASS.

Financial candidate:
- `pytest -q` PASS;
- `python scripts/eval_contracts.py` PASS;
- `python scripts/static_audit.py` PASS;
- `python scripts/retired_runtime_static_audit.py` PASS;
- isolated wheel smoke PASS;
- DOCX render smoke PASS;
- inheritance tests prove profile 16/min contract 1.5.0/problem-response floor/direct activation/domain evolution ownership/product traceability;
- no second controller/continuity namespace/parent identity code appears.

Promotion order:
1. validate both candidates;
2. promote UAOS 2.4.5 first so common contract 1.5.0 is current;
3. reread parent authority;
4. revalidate/promote Financial 0.8.4;
5. close parent assurance with Financial production evidence.

## Current assurance ceiling
Before hosted CI and production observation: `CANDIDATE_STRUCTURAL_AND_DESIGN_EVIDENCE_ONLY`.
Do not call inheritance fully verified until both repositories pass candidate and production observation in the stated order.
