# GITHUB_CHAT article-branch discovery incident — 2026-10-12

## Trigger
A genuine fresh ChatGPT conversation read only the Financial repository authority, created article task `ai-security-infrastructure-2026-10-12-7f3a91c2`, executed the canonical GITHUB_CHAT workflow through terminal `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`, and persisted the task on dedicated branch `article/ai-security-infrastructure-2026-10-12-7f3a91c2`.

## What worked
- Branch base was the then-current `main` authority head `6be076cf0cc328345d6dd5e215857f5f24b98de7`.
- Exact branch compare to terminal head `ec87c775c474f7226ac9771961d7b743e4e165d8` contained only `workspaces/articles/ai-security-infrastructure-2026-10-12-7f3a91c2/...` business artifacts.
- STATE schema 1.1, stage artifact refs, exact prior-state blob bindings, guard-accepted execution receipts, one real `EDITORIAL_AUDIT → DRAFT` revision/invalidation cycle, deterministic Word checks, render evidence, final self-review, and bounded GITHUB_CHAT terminal state were all durable.
- Delivered article SHA256 `b12132ecfe3e14272926431092b9f0745770bcdf879ae61f418bdbf721114481` matched the writing-audit report and independently inspected delivery artifact.

## Confirmed defect
The current owner authority defined the business state **path** but not its Git **ref**. `continuity/GITHUB_CHAT_EXECUTION.json`, `continuity/TASK_INDEX.md` and `docs/architecture.md` described `workspaces/articles/{task_id}` and GitHub `main` as rule authority, but did not define dedicated `article/{task_id}` refs, cold-start branch resolution, divergent main/branch conflict behavior, or a final progress receipt field for the state ref.

The live task was therefore durable but not mechanically discoverable from the declared cold-start contract. A replacement chat that only enumerated `main/workspaces/articles` could miss the completed task even though the previous chat truthfully reported `COMMITTED`.

Failure class: `DURABLE_STATE_WITHOUT_DECLARED_DISCOVERY_REF`.

## Parent-system reframe
The defect is not a workflow-stage or CAS failure. The guard bound content identity correctly. The missing identity dimension was repository ref/discovery location. Durable path + blob SHA is insufficient for cold-start continuity when state is allowed to live off `main`.

## Alternatives considered
1. **Force every article workspace back onto `main`.** Rejected: removes useful business-state isolation and recreates unnecessary whole-repository main churn; current Universal freshness logic can classify business-artifact deltas, but isolation remains valuable.
2. **Add a central mutable article-branch index on `main`.** Rejected for this repair: introduces a second cache that every task creation/terminalization would have to synchronize and creates a new stale-index failure mode.
3. **Admit deterministic `article/{task_id}` refs directly into the existing GITHUB_CHAT authority and cold-start routing contract.** Accepted: no new root authority, no duplicate business database, task id deterministically maps to ref, explicit resume can enumerate branch refs only when needed, and divergent duplicate state can fail closed.

## Repair
- `continuity/GITHUB_CHAT_EXECUTION.json` schema 1.3 defines allowed state refs, branch base/content boundaries, task-id and generic-resume resolution, divergent-state fail-closed behavior, same-ref write/reread, and branch-backed final receipt identity.
- `continuity/TASK_INDEX.md` exposes cold-start task/ref resolution without turning healthy NEW_TASK into a history scan.
- `skills/financial-writing-agent/SKILL.md` keeps only a compact hot-path state-ref anchor.
- `docs/architecture.md` documents the same persistence model.
- `tests/test_github_chat_execution.py` prevents regression to path-only continuity semantics.

## Assurance boundary
This incident proves a live cross-chat discoverability gap in declared Financial GITHUB_CHAT continuity and a structural repair to the owner contract. It does not upgrade the article's CHAT_SELF_REVIEW assurance, does not prove provider-attested independence, and does not mutate or merge the article business workspace itself.
