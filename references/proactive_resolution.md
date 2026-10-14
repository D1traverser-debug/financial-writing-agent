# Proactive Resolution & Evidence Recovery

Status: `CURRENT_DOMAIN_MAINTENANCE_RULE`
Revision: `1.0`
Effective: `2026-10-15`
Owner: `DOMAIN:financial_writing`
Parent-review status: `UPCALL_RECOMMENDED_FOR_COMMON_CAPABILITY_GENERALIZATION`

## Purpose

Financial Writing already inherits the UAOS problem-response floor: detected problem -> micro diagnosis -> macro alignment -> governing-assumption challenge -> external research. This rule closes a separate execution gap discovered on 2026-10-15: a session may correctly notice missing evidence, preference or voice information yet still behave passively by treating the missing item as a future user dependency.

The default behavior is now **recover, infer provisionally, test, and only then escalate**. Missing highest-tier evidence is not automatically a blocker.

## Trigger

Activate this rule when any of the following is true:
- a preferred voice/style sample is not immediately present;
- a user preference or prior correction appears relevant but is not fully in the current turn;
- a completed or prior article may contain reusable accepted/edited evidence;
- an uncertainty can plausibly be reduced by current repository state, prior durable artifacts, available conversation context, connected-source retrieval or external method research;
- the assistant is about to say or imply `以后如果你提供...`, `等你给...`, `需要你再...`, or equivalent dependency language for something it may be able to recover itself.

This is not permission to fabricate facts, preferences, personal history or approval.

## Mandatory proactive recovery order

Before treating the user as the next dependency, inspect the strongest legally available evidence in this order, stopping only when the decision is sufficiently supported:

1. exact current article/project authority and durable state/artifacts;
2. user-approved or user-edited writing samples already present in Financial durable evidence;
3. explicit durable user corrections, rejections, constraints and accepted outcomes from prior work;
4. recent same-product outputs with positive acceptance or post-publication performance evidence;
5. current conversation/context signals that materially clarify the decision;
6. target-platform and finance-genre conventions;
7. external practitioner/Agent/Skill/research evidence, used as candidate guidance rather than user-voice truth.

When prior personal/context evidence is required and available through the host, retrieve it rather than asking the user to repeat it.

## Provisional candidate rule

If the strongest evidence is incomplete but the work can continue safely, create an internal provisional candidate rather than blocking. The candidate must identify:
- `target`: what is being inferred/resolved;
- `evidence_refs`: what supports it;
- `scope`: where it may be used;
- `confidence`: high / medium / low;
- `contradictions_or_unknowns`;
- `validation_plan`: what future article/user response/performance evidence would confirm, refine or reject it.

For writing voice, absence of a perfect approved sample does **not** mean falling back to a generic humanizer. Derive only traits supported by existing corrections/output evidence, keep uncertain traits provisional, and test them on real Financial work.

## Escalation boundary

Ask the user only when:
- the unresolved choice materially changes the requested outcome;
- available evidence produces genuinely competing interpretations with no defensible default;
- proceeding would invent a fact, approval, identity, preference or risky assumption;
- the user explicitly requested a choice/confirmation.

Do not ask merely because the best evidence is imperfect.

## Problem-response integration

A recovered candidate does not bypass the existing UAOS cognition floor. When the underlying gap is itself a defect or repeated failure, continue through:
`recover evidence -> micro diagnosis -> macro alignment -> challenge assumption -> external research -> alternatives -> repair -> verify -> observe`.

The important change is that evidence recovery is an **active step**, not a future-user placeholder.

## Logging requirement

Every encountered problem must be represented in `evals/PROBLEM_EVOLUTION_JOURNAL.md`.

Small/local problems may use a compact ledger entry. Material, repeated, architectural, user-rejected or cross-domain problems require the full chronology: symptom, detection, diagnosis, assumptions challenged, research, alternatives, actions, verification, result, system impact, remaining unknowns and parent-upcall status.

The journal is an evidence index, not a replacement for detailed incident/eval files. Link detailed evidence rather than duplicating every artifact.

## Parent/common-capability upcall

This rule is Financial-owned because the triggering incident occurred in Financial writing and directly affects Financial evidence/voice resolution. However, the underlying failure class—`inherited cognition exists but the agent externalizes a recoverable dependency to the user`—is plausibly cross-domain.

Record this as a parent guidance item. UAOS should decide whether a common future contract should require registered children to attempt available-context recovery before user escalation. Financial must not directly rewrite parent common authority from the child domain.
