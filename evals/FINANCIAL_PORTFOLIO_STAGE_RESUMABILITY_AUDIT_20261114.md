# Financial Portfolio Stage Resumability — 2026-11-14

## Scope and decision

This is a Financial Writing subsystem repair only. CAOS source, configuration, PRs and runtime were not modified.

The previous portfolio helper executed all writing passes in one in-memory call. It could not be treated as a durable, resumable business workflow. PR #83 introduced a stage-at-a-time execution foundation and was merged to `main`.

- PR: https://github.com/D1traverser-debug/financial-writing-agent/pull/83
- Candidate branch: `repair/financial-resumable-portfolio-stages-20261114`
- Candidate head: `bb244744c8f41debf9ace9072a67ee5336963d6c`
- Merge/main SHA: `cdb67a2a40fdce07124242eaa47c814b739ec9d4`
- Exact-head PR CI: run `43593808379`, success
- Post-merge main CI: run `43594019716`, success

## Root cause addressed

The 16 internal passes were previously exposed through one portfolio call that ran the research callback, research-audit callback and every product branch in memory. That obscured the boundary between business stages and did not provide a reliable restart point after interruption.

The new API is:
- `start_portfolio_context`: creates a task- and requirement-digest-bound serializable context.
- `execute_portfolio_stage`: executes exactly one current business stage and returns a context with hash-linked pass and stage receipts.
- `validate_portfolio_context`: verifies stage position, receipt chains, task/requirement binding and payload integrity.
- `execute_portfolio_writing`: retained as an in-memory replay/test helper only; it is explicitly not the production persistence route.

The internal sequence is RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT. RESEARCH_AUDIT is now an explicit stage. The active pass DAG validation and Deep/Broad clone rejection remain enforced.

## Verification evidence

Both exact-head PR CI and post-merge main CI completed successfully.

- 620 tests passed.
- Measured source line coverage: 89% (6,963 statements; 778 missed).
- Whole-tree audit: 322 tracked files, 123 Python AST parses, 53 JSON parses, 47,348 decoded text lines, zero warnings and zero errors.
- Owner-obligation and two-revision mutation admission tests passed.
- Live branch inventory / zero-mutation archive dry-run passed.
- Executable contract evaluation, static single-owner audit and standalone Financial runtime checks passed.
- Wheel build and isolated install passed.
- Four Word product binaries were generated, opened and rendered with page/signature checks. Their content was synthetic; this is not evidence of real article quality.
- Financial real-task and negative-case business replay passed within the test harness. This is not independent editorial acceptance.

## Assurance boundary — still OPEN

The new receipts are deterministic hash-bound integrity checks. They are not provider signatures, semantic proof, or owner acceptance.

The stage executor itself does not persist provider artifacts or advance the Article Aggregate. Its caller must persist the stage result, reread exact provider bytes, and complete the authenticated standalone owner admission before resuming. A successful in-memory replay is not proof that those effects occurred.

The current implementation also binds the requirement digest but does not yet inject fresh, scoped requirement contexts into every pass or collect stage-specific requirement-satisfaction evidence. The canonical `current_admission.requirement_context_for_scope` API exists but is not yet wired into the portfolio stage executor.

Stage-result artifacts and resumable portfolio-context artifacts must remain distinct. In particular, the existing RESEARCH artifact admission may require a typed `ResearchPackage`; the full portfolio context must not be substituted for that stage artifact.

No current user-like finance article was produced or independently evaluated in this repair. No claim is made that personalized voice, editorial quality, native client activation, live provider persistence or external reader outcomes are complete.

## Next legal engineering phase

1. Re-read current Article Aggregate state and requirement authority before every stage; inject the exact scoped requirements and digest into every applicable pass.
2. Require stage-specific satisfaction evidence for newly due requirements and bind it to the current stage artifact; owner admission must independently revalidate it.
3. Separate and persist (a) the typed business-stage artifact and (b) the resumable portfolio context; provider-read both back by exact bytes.
4. Add one authenticated coordinator that calls the existing standalone Financial owner admission and verifies the resulting Article Aggregate state before allowing the next stage.
5. Test interruption/restart, stale requirement digest, wrong artifact type, changed provider bytes, concurrent state changes, failed review, REVISE invalidation and legitimate neighboring tasks.
6. Only then run a current first-party-sourced, user-like finance topic through all products and evaluate the actual writing outcome.

Do not change CAOS. Do not label the Financial system complete while these boundaries remain open.
