# CAOS ↔ Financial Writing — native child interface and verification contract

**Review date:** 2026-11-11
**Parent read-only source:** `D1traverser-debug/cognition-agent-os@main` commit `9686cedeb3fd8171ecf70eab33aaea641217b04a`, `src/cognition_agent_os/domain_contract.py`.
**Financial child production base:** `main@e580cd4dfda8db47674803451c9adfff9e3cf975`.
**Candidate branch:** `rebuild/financial-integrity-r1-20261111`.

## Real parent interface (code-derived)

Current CAOS native `domain_contract.py` reads precisely `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`, then `manifest.skill.entrypoint`. It validates shared `domain_id`, controller equality, nonempty unique snake_case capability IDs, parent metadata, immutable commit-pinned source bytes and legacy parent declarations. It returns `CHILD_CONTRACT_OBSERVATION_V1`, flags `child_business_result_verified=false`, `parent_replacement_admitted=false`, and does not write child business state. This is **not** an execution, hosted model or parent grant.

We preserve the three `.uaos/` **filenames solely as the parent’s source-level read protocol**, replacing all current parent values with `D1traverser-debug/cognition-agent-os@main`. Their canonical Skill entry is now `CAOS_SKILL.md`. `UAOS_SKILL.md` is an inert historical pointer and cannot be selected as the current controller. Do not add a second Financial parent/task index.

For a real parent read-only observation, CAOS can submit its existing `domain_contract` task with:
```json
{
  "kind": "domain_contract",
  "repo": "D1traverser-debug/financial-writing-agent",
  "ref": "<exact 40-character Financial Git commit SHA>",
  "domain_id": "financial_writing"
}
```
This task must be submitted through a legitimately initialized/granted CAOS Host *if available*. A future connected Host is optional during ChatGPT interactive work; merely including the JSON here does not run the task. Avoid `state_authority_key` for dynamic per-article `{task_id}` references, since the parent validator resolves only an exact literal child-declared JSON path.

## Child-native action bridge (code-derived, not magical delegation)

`financial_writing_agent.caos_bridge` offers `observe_article(task_id, state_reader=...)` and `admit_parent_article_action(request, state_reader=..., cas_writer=..., grant_verifier=...)`. These are **ordinary Python callable contracts** that a trusted connected caller can use; the repo does not export a remote server or fabricate existing ChatGPT invocation.

The first requires a provider-resolved `workspaces/articles/<task_id>/STATE.json` containing a real provider Git blob SHA and validates the *actual* Financial current state. The result reports stage, requirement revision/digest, registered output set and explicit lack of independent editorial/user acceptance.

The second accepts `CREATE_ARTICLE`, `CHANGE_REQUIREMENTS` and `ADVANCE_STAGE` with an exact parent goal/revision/action identity, valid child slug, the current child blob SHA (or null only for create) and tightly scoped arguments. It requires:
1. An **externally authenticated grant-verifier callback**, not a caller-supplied authorization word or model claim;
2. A **trusted provider read** of the actual child article and exact version prior to mutation;
3. `current_admission.build_initial_state`, `apply_task_requirement_change` or `advance_state` with all Financial invariants, no direct `owner_guard` mutation;
4. A real GitHub compare-and-swap/create-only writer supplying the expected old blob SHA, returning the exact created Git blob SHA;
5. A **second independent provider read** whose parsed state equals the admitted candidate and whose Git blob SHA matches the new payload.

Callback missing, mismatch, stale state, denied grant or uncertain remote response yields no verified success. For an unknown provider write outcome **reconcile** the external state; do not blindly retry a non-idempotent action.

A minimally scoped request shape is:
```json
{
  "schema_version": "1.0",
  "parent_repository": "D1traverser-debug/cognition-agent-os",
  "goal_id": "actual-parent-goal-identifier",
  "goal_revision": 1,
  "action_id": "real-action-identity",
  "task_id": "financial-owned-article-slug",
  "operation": "ADVANCE_STAGE",
  "expected_state_blob_sha": "<actual 40-character child Git blob SHA>",
  "parameters": {}
}
```
Calling this shape with user-invented grant callbacks or dummy Git hashes proves nothing. The CI tests use fake callbacks **only** to test deterministic fail-closed behaviors, concurrency and readback contracts.

## Operational article and owner requirement boundary

Each article owns its own `STATE.json`, active user requirements, revision digest, exact current stage, research/blueprints/fitness evidence and delivery output hashes. Current Article Aggregate is the only state mutator. CAOS may suggest a plan but cannot silently change a requirement, overwrite historical receipts, widen provider grants, assume every article requires a market-timing ranking, or mark an outcome as accepted.

Historical cross-border v2 is `MIGRATED_HISTORY`; v3 is the current task at `RESEARCH`. Its two existing task-specific user requirements remain unmodified. A new source date or policy claim must be verified before it can be reused. The old source-to-draft, company-economics and independent reader-value gaps are still OPEN.

## Independent acceptance beyond code

- **Interface:** actual CAOS commit-pinned parent `domain_contract` observation, no old-parent declaration, real child discovery and a native ChatGPT in-scope invocation trace if the Skill is installed.
- **Effect:** user-authorized child write, actual GitHub blob compare-and-swap, direct readback, failed stale/denied/neighbor cases and rollback.
- **Finance research:** verifiable official sources, timestamped claims, company exposure, counterexample, scope-specific requirement mapping and real PrivateResearchBrief, not just 15 populated summaries.
- **Writing:** Deep/Broad separate story blueprints, company-level economics, originality comparison against actual sources, no actionable tips, independent editorial/readability result and user/reader evaluation. Historical negative Word, fixture graders and same-chat PASS are not positive baselines.
- **Delivery:** canonical real DOCX bytes, SHA-256, Word parse/format, actual visual page review, user-visible file link verified in the current session, and correct research version.
- **Learning:** real failure feedback, reconsidered root cause/method, measured recurrence and one unseen family; method cards alone are not behavior.

The complete Financial domain is `NOT_READY` until real product/owner outcomes are independently established. Repository CI is a narrower engineering gate. No CAOS source/config is modified in this candidate.
