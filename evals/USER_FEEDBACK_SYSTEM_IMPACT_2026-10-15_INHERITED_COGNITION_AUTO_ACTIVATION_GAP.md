# User feedback system impact — inherited cognition/evolution did not auto-activate

Date: 2026-10-15
Problem ref: `P-20261015-16`
Owner of evidence: `DOMAIN:financial_writing`
Parent guidance signal: `INHERITED_COGNITION_AUTO_ACTIVATION_GAP`
Status: `OPEN__DOMAIN_REPAIR_IN_PROGRESS__PARENT_GUIDANCE_REQUIRED`

## Trigger
During a live Financial Writing task, the user selected/inherited Financial Writing through UAOS and then gave the topic `跨境电商`.

Financial initially identified and announced a likely strongest article line before first completing the whole value-chain map. The user corrected this and required value-chain coverage to be mandatory. Financial began a domain repair around pre-thesis value-chain coverage and reusable knowledge.

The user then had to remind Financial a second time that inherited UAOS cognition/evolution semantics already require assumption challenge, counterexample/rejection work, broad external research and layered alternative selection. The user explicitly identified that this should have happened automatically after inheritance rather than only after another reminder.

## Concrete failure
The child/domain successfully inherited the **declaration** of UAOS capabilities, but live business behavior did not automatically apply the relevant inherited cognition/evolution method at the point where it mattered.

Observed sequence:
1. UAOS selection correctly activated `DOMAIN:financial_writing`.
2. Financial read current domain authority and reported inherited UAOS capability compatibility.
3. Live topic research nevertheless narrowed to a preferred main line too early.
4. User correction triggered a first repair for value-chain coverage/knowledge reuse.
5. That first repair still did not automatically surface the full inherited method of governing-assumption challenge, adversarial/counterexample search and competitive/layered candidate adjudication.
6. User had to explicitly remind Financial of the parent cognition/evolution capability.

This is stronger evidence than a documentation audit: it is a live-domain behavior reproduction after successful inheritance/bootstrap.

## Micro diagnosis
The current Financial authority contains problem-response/evolution rules and inherits UAOS common capabilities, but there is still a gap between:
- capability presence/compatibility at startup;
- problem detection after an obvious defect;
- and **automatic business-action activation** of the inherited method before the user has to name the method again.

The current domain repair can encode topic-research-specific requirements, but that alone may only mask a common cross-domain failure class: inherited common cognition can remain passive until user correction explicitly invokes it.

## Macro alignment
UAOS currently states that registered domains inherit adaptive deliberation and governed self-evolution while operating directly as the business work plane. The intended model is reuse without a live parent proxy. Therefore, direct-domain execution must still behaviorally realize the inherited method when its trigger conditions appear.

If a user must remember and restate parent cognition/evolution rules after selecting a child Agent, the inheritance contract is not fully achieving its product objective even if manifests, capability versions and static tests all pass.

## Governing assumption challenged
Rejected assumption: once a domain declares compatible UAOS common capabilities and has local maintenance rules, ordinary host execution will reliably remember to instantiate the relevant inherited method at the right business moment.

New question for parent adjudication: does UAOS need a stronger common activation/admission contract or executable trajectory evidence that tests **post-selection automatic use** of inherited cognition/evolution in real domain work, rather than only capability binding and problem-response behavior after a defect is already explicitly surfaced?

## Parent evidence already relevant
Current UAOS authority says:
- problem detection is always-on after authority selection;
- every detected user correction/defect/knowledge gap activates micro diagnosis, macro/topology alignment, governing-assumption challenge and external research;
- counterexample search and independent verification add depth according to risk;
- common capabilities include competitive candidates, structured critique/revision and owner adjudication;
- governed evolution follows Problem/Incident -> Research+Reflection -> Failure Class -> Change Candidate -> Reproducible Evaluation -> Owner-Scoped Promotion -> Post-Promotion Observation -> Keep/Rollback/Retire;
- declaration-only inheritance is insufficient for operational assurance.

Relevant parent refs:
- `D1traverser-debug/universal-agent-os@main:ENTRYPOINT.md`
- `config/DELIBERATION_POLICY.json` policy 1.5.0
- `config/COMMON_CAPABILITIES.json` contract 1.6.0

## Domain-local response already underway
Financial is strengthening its own topic-research authority so that:
- value-chain coverage is a hard pre-thesis gate;
- broad multi-source recall, negative/falsification search and competing hypotheses precede final thesis selection;
- candidate theses are challenged/eliminated under explicit evidence criteria;
- prior cognition is recalled with provenance and current/material claims are revalidated.

Candidate PR: `#34 research: require value-chain preflight and provenance-aware knowledge reuse`.

This domain repair is necessary but **not sufficient evidence that the common inheritance gap is solved**.

## Parent guidance request
UAOS should evaluate this as fresh live evidence for the already-known failure families:
- `INHERITANCE_BEHAVIOR_VS_DECLARATION`;
- `DECLARATION_TO_OPERATION_GAP`;
- possibly a narrower new subtype: `INHERITED_COGNITION_AUTO_ACTIVATION_GAP`.

Requested outcome, without prescribing implementation:
1. determine whether the current common capability/behavior assurance truly requires inherited cognition/evolution to auto-activate in direct-domain business work without the user re-naming the parent method;
2. if yes, identify why the current executable/trajectory assurance did not prevent this live miss;
3. evaluate stronger common admission/trajectory/regression evidence at the smallest appropriate parent scope;
4. preserve the direct-domain architecture and avoid reintroducing a mandatory live UAOS proxy unless evidence proves it necessary;
5. use this Financial incident as a cross-domain test case, not as a reason to copy Financial-specific research rules into unrelated domains.

## Assurance boundary
This file is a non-mutating child upcall. It does not change UAOS authority and does not claim a parent fix exists yet. Parent adjudication is pending.
