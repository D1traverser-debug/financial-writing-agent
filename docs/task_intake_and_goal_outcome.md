# Goal-first Intake and User-goal Outcome Closure

Owner: Financial Writing only. Contract: goal-first intake v1.0 and independent final outcome review v1.0.

This change closes two connected failures in the existing Financial Article Aggregate. It does not create another controller, task registry, state machine or CAOS dependency.

## 1. Root cause

The current task-requirement authority could be created empty and populated after the first Portfolio Context had already been built. This allowed research to start before the original user request had been fully decomposed and bound to the execution context.

The final workflow also had strong stage receipts, editorial fitness, Word binary checks and visible-delivery checks, but those controls did not independently prove that every user requirement and every declared success criterion was satisfied by the actual delivered article text.

## 2. Goal-first intake

New tasks created through the standalone Financial runtime bind \`task_intake_contract_version=1.0\`. Legacy tasks without the marker retain historical compatibility and are not retroactively certified.

Before leaving INTAKE, the task must admit a \`TaskIntakeManifest\` containing:

- exact task ID and original prompt SHA-256;
- instruction units classified as goal, requirement, correction, preference, suggestion, issue, question, approval or context;
- exact source excerpts and links from each binding requirement or preference to its source units;
- nonbinding ideas and unresolved questions kept separate from authoritative requirements;
- the immutable requested output set;
- success criteria that cover every active requirement;
- the prompt-bound WritingExecutionProfile;
- required/optional/not-required knowledge and capability routes;
- material assumptions and blocking questions.

A separate trusted reviewer signs \`task_intake_review\` against the exact prompt, manifest digest, requirement IDs, instruction-unit IDs, output contract, success criteria, execution profile and route coverage. The reviewer must differ from the owner and the Financial action provider.

The coordinator validates the manifest and review, derives revision 1 of the existing TaskRequirementAuthority, computes all active scope projections and binds the resulting digest plus manifest digest/profile into the first Portfolio Context. The owner transition independently repeats validation and admits the same requirement authority. The persisted owner state keeps the manifest and signed review; the context does not create a second authority.

A goal-first task cannot leave INTAKE without this evidence. Resume must match the admitted manifest digest and recompute the scoped requirement projection from the owner state. Requirement changes continue through the existing requirement-change transaction and downstream invalidation graph.

## 3. Independent user-goal outcome review

At FINAL_AUDIT, the host reads the exact current Word binaries, extracts their actual text, and constructs \`goal_outcome.build_goal_outcome_challenge\`. The challenge binds the original prompt, admitted manifest, current TaskRequirementAuthority revision/digest, every active requirement, every success criterion, current research/draft references, exact deliverable metadata and binary hashes, extracted text, and visible-delivery evidence.

A separate trusted provider signs \`independent_goal_outcome_review\`. It must return:

- one SATISFIED or NOT_SATISFIED result for every active requirement;
- one SATISFIED or NOT_SATISFIED result for every manifest success criterion;
- evidence references for every result;
- exact result digests and unmet-ID lists;
- no uncovered material requirements;
- a substantive review summary;
- PASS, REVISE or FAIL.

PASS is valid only when every requirement and criterion is satisfied and no revision target is supplied. REVISE requires at least one unmet item and an allowed signed revision target. FAIL requires at least one unmet item, has no revision target and blocks the task in place. The owner state preserves every signed review in its receipt-bound history; only the latest current PASS can support terminal delivery status.

The independent review does not assert user acceptance. It asserts only that a separate reviewer evaluated the delivered content against the admitted goal. Exact visible-delivery readback remains a separate runtime gate after owner admission and before the state/effect bundle is committed.

## 4. Failure behavior

- Missing, stale, malformed or unsigned intake evidence: INTAKE cannot advance.
- Prompt, output contract, scope, profile or requirement projection mismatch: reject before owner mutation.
- Resume with a different manifest digest: reject rather than silently rebuild.
- Missing or stale Word binary/text: final challenge cannot be constructed.
- Incomplete requirement or success-criterion result set: reject.
- False PASS with unmet items: reject.
- REVISE: route through the existing owner revision graph and invalidate downstream evidence.
- FAIL: block in place; recovery requires the existing explicit owner recovery action.
- Legacy task without the marker: preserve legacy behavior; do not infer semantic certification.

## 5. Assurance boundary

Synthetic tests prove schema, digest, signature, binding, state-transition and tamper-rejection contracts only. They do not prove that a live independent reviewer provider is deployed, that a hosted Financial Provider Action is available, that production secrets are configured, that a real Word artifact was reviewed, or that the user accepted the article. Those remain external evidence gates and must not be reported as complete without observation.
