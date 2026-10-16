# Financial -> UAOS Parent Guidance Handoff — stale child resume after domain evolution

Status: `NON_MUTATING_CHILD_UPCALL__PARENT_ADJUDICATION_REQUESTED`
Date: 2026-10-16
Child owner: `DOMAIN:financial_writing`
Parent authority: `D1traverser-debug/universal-agent-os@main`

## Trigger

A historical Financial article created before the Financial Writing 1.0 semantic-quality kernel was resumed at `DELIVERY` after the rebuild and terminalized without current DecisionEnvelope / StoryBlueprint / PublicationFitness evidence. The same cross-border article was already a known negative rebuild replay case. A live user rejected the delivered result.

## Child diagnosis

Financial has selected a domain-workflow repair: explicit post-evolution resume compatibility admission. Historical state remains immutable provenance, but a legacy state cannot silently inherit current-quality claims. Current-quality continuation requires a current-kernel successor/replay; explicit historical-only continuation remains bounded to historical semantics.

Child evidence:
- `workspaces/articles/cross-border-ecommerce-20261015/feedback/USER_REJECTION_20261016.md`
- `workspaces/articles/cross-border-ecommerce-20261015/feedback/SYSTEM_IMPACT_20261016.json`
- `evals/FINANCIAL_CROSS_BORDER_POST_REBUILD_REJECTION_20261016.md`
- candidate implementation: `financial_writing_agent/resume_compatibility.py`

## Parent question

Please adjudicate whether UAOS `cross_chat_continuity_and_recovery` should promote a common outcome-level invariant:

> After a material child-domain architecture/quality-contract upgrade, resuming an older child business state under current-quality claims requires an owner-defined compatibility admission. Historical provenance may remain readable/resumable under explicitly historical semantics, but parent continuity must not imply quality-equivalence across semantic generations.

This proposed common rule must remain outcome-level. UAOS should not copy Financial's state schema, kernel marker, or successor implementation into other domains.

## Why this may be common scope

The failure was enabled at the intersection of cross-chat continuation and child evolution. The general risk can exist in any registered domain whose historical business state survives a material contract upgrade. The exact compatibility logic is domain-owned, but the requirement to distinguish historical provenance from current-contract assurance may belong to parent continuity governance.

## Alternatives considered

1. Financial-only fix, no parent learning: sufficient for immediate article repair but risks repeating the class in other domains.
2. Parent forces migration/rewrite of all old child states: rejected; destroys provenance and violates child ownership.
3. Parent becomes live proxy on every continuation: rejected; unnecessary centralization and microscheduling.
4. Outcome-level compatibility admission + domain-owned implementation: selected candidate.

## Requested parent evidence

- test whether this class is already prevented by current UAOS continuity semantics;
- compare at least one non-Financial child evolution/resume path before promoting a common rule;
- if promoted, keep implementation domain-owned and avoid exact-version freezes;
- add parent-level regression only for the common outcome, not Financial-specific fields.

This file is a non-authoritative child upcall. It does not mutate UAOS.
