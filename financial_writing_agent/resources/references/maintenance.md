# Maintenance module

## Ownership
Maintenance owns **how feedback, external methods, code changes and performance evidence become durable system changes**. It does not own article-level prose rules.

## Classify before changing
- Run-local request → current TaskContract/state only.
- Explicit durable user instruction → durable-rule change candidate with direct provenance.
- Single user edit/reaction → raw Writing DNA evidence / one-off candidate, not an automatic global rule.
- Repeated accepted edits across independent articles → eligible for personalized promotion after comparison.
- Post-publication performance → evidence sample; repeated comparable results matter more than one outlier.
- External skill/agent/article/research → benchmark candidate only; distill the underlying mechanism, not signature phrasing or an entire foreign prompt stack.
- Existing rule skipped by execution → runtime/trajectory defect; fix enforcement instead of duplicating the rule in more documents.
- Platform behavior change → reverify current evidence before policy changes.

## Learning evidence
Use `record_writing_learning_sample` (or an equivalent durable receipt) for raw user edits, feedback, acceptance/rejection and post-publication performance when a writing task exists.

For a persisted writing task, a **material explicit user edit, feedback, rejection or acceptance that changes how the system should write, review or deliver** must be captured as owner-controlled learning evidence before the turn claims durable personalized learning or closes the affected revision loop, unless equivalent evidence is already persisted. If evidence capture is unavailable, obey the user's current revision but mark personalized durable-learning persistence as unavailable; do not imply future chats have inherited the lesson.

The ledger is evidence, **not automatic self-modification**. A one-off user reaction never becomes a global style rule by itself.

A repeated material failure of the same writing responsibility is not another reminder-writing opportunity. Treat it as a runtime/trajectory reliability defect: persist failure evidence, identify the enforcement gap, add/update a regression or eval, and remove/repair the conflicting mechanism before adding unrelated writing features.

## Quality-changing system promotion
A system/prompt/method change that claims to improve writing quality must not be promoted merely because deterministic CI passes or because the changing agent writes a positive receipt.

Use `financial_writing_agent.quality_regression` for owner-local promotion evidence. Two scopes are intentionally different:

### General editorial quality
The system may improve general writing quality without waiting for the user to become its optimizer. Promotion requires:
- deterministic factual/compliance/state/artifact invariants remain an independent hard floor;
- complete real failure evidence;
- diverse complete held-out evidence spanning more than one topic family;
- blind pairwise comparison against the current baseline with the candidate evaluated in both A and B positions;
- independently verifiable judge execution evidence;
- known real failures improve, held-out cases do not regress, and at least one held-out case prefers the candidate;
- position-swapped judgments must agree or the comparison fails closed.

A user positive label is **not** required for this general scope. Independent external benchmarks and held-out scenarios may support general editorial quality, provided they do not masquerade as personalized taste.

### Personalized Writing DNA
A change that claims to encode the user's personal style or durable preference must satisfy all general-quality requirements **and** include real user acceptance/edit evidence or post-publication performance evidence. External benchmarks cannot invent personalized taste.

Partial snippets/feedback may enter the corpus immediately but cannot by themselves authorize promotion.

`evals/quality_regression.json` is owner-local eval evidence, not business task authority and not a new root policy. The real 2026-10-10 offshore-wind rejection has been recovered as a complete regression artifact under `evals/artifacts/`; general promotion is still `NOT_READY` until diverse held-out evidence exists. Personalized promotion additionally remains blocked until real positive user/performance evidence exists.

## Change protocol
1. Identify the canonical rule owner and affected runtime stages.
2. Decide whether the defect belongs in rules, schema, runtime/state machine, deterministic delivery, tests/evals or deployment—not every problem is a prompt problem.
3. Modify the canonical owner first.
4. Search for contradictory, duplicated or legacy wording/code.
5. Synchronize intentional rule mirrors byte-for-byte.
6. Align schema/runtime/MCP contracts when behavior changes.
7. Add regression tests for both success and failure paths, including revision invalidation/recovery when relevant.
8. Run SDK/MCP smoke, unit/trajectory tests, executable contract evals, static ownership/bundle/version audit, isolated wheel install and DOCX render smoke.
9. When behavior depends on live model/tool execution, run a representative real writing E2E before calling that deployment production-ready.
10. Re-read final authority files and CI state before reporting the change as committed.

## Version / cutover discipline
A breaking schema or public MCP change requires a contract version bump. `pyproject.toml`, `plugin.json`, policy contract version, README/architecture/Site spec and active Continuity metadata must not silently disagree about the current contract.

Do not preserve obsolete compatibility surfaces merely because they once existed. Keep Git history; delete unsupported runtime/schema/tool paths and protect the deletion with static regression checks.

## Runtime reliability discipline
Fail-closed must still be recoverable. A BLOCKED task needs an explicit persisted recovery cursor and a tested resume path; permanent deadlocks are not acceptable durability.

Revisions must invalidate stale downstream QA and stale generated artifacts. Re-running deterministic render/delivery steps must be idempotent so old output cannot contaminate current evidence.

## Evidence standard
A documentation edit is not proof that an Agent executes the behavior. Runtime traces, structured state, artifacts, tests and audit evidence are proof.
