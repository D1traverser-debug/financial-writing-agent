# Live System-Impact Incident — execution governance, quota use, publication quality and admission drift

Date: 2026-10-15
Owner: `DOMAIN:financial_writing`
Status: `OPEN__DOMAIN_REPAIR_IN_PROGRESS__PARENT_RE_ADJUDICATION_REQUESTED`
Suggested problem id: `P-20261015-17`
Parent: `D1traverser-debug/universal-agent-os@main`

## Why this incident exists

The user explicitly required that **all problems encountered during this rebuild be reported**, not only the final technical defect. This incident therefore records the full live chain: publication-quality failure, governance/review failures, authority-admission bypasses, execution drift, tool/quota misuse and the recurrence of inherited-cognition / problem-to-action gaps.

This file is evidence only. It does not mutate UAOS authority and does not claim parent adjudication.

## 1. Original publication failure that triggered the rebuild

The delivered cross-border e-commerce article was rejected by the user for multiple simultaneous defects:

1. opening hook did not create sufficient immediate reader pull;
2. requested/expected serial numbering and internal structure were not executed well enough;
3. company analysis was insufficiently integrated into the event/industry narrative;
4. too much generic framing / stage-setting language (for example abstract “看什么/关注什么” style exposition) reduced information density;
5. de-AI / natural authorial prose objective was not achieved;
6. the result felt derivative enough to raise a plagiarism/copying concern even though the system was intended to synthesize rather than imitate;
7. reader retention / completion-rate design was not demonstrably achieved;
8. the Deep version compressed the industry too early instead of allowing complete value-chain reasoning when the topic required it.

### Diagnosis

The defect was not simply “missing more writing rules.” Existing `hooks.md`, `style.md`, `reader_value.md` and editorial rules already contained many relevant requirements. The larger failure was that generation and self-audit shared too many goals, and the audit could emit broad `PASS` labels without text-level evidence that the reader funnel, natural prose, company integration and retention geometry actually worked.

This exposed a distinction between **declared writing rules** and **effective publication fitness admission**.

## 2. Architecture problem: too many simultaneous constraints in one writing path

The old topology made one path carry research completeness, compliance, platform formatting, title quality, style, reader retention, company comparison, anti-template diagnosis and delivery constraints at once.

Observed consequence: the system could become “rule-compliant but editorially inert.” Adding more constraints risked increasing that failure rather than fixing it.

Selected redesign direction:

`cognition/research -> decision -> story architecture -> drafting -> reader-dropoff challenge -> editing -> originality/style challenge -> factual challenge -> synthesis -> delivery`

under one Financial owner, rather than a default explosion of independent Agents.

The key governance object is not “more prompts” but auditable decision/admission evidence (`DecisionEnvelope`, `StoryBlueprint`, `PublicationFitness`) plus deterministic guards where appropriate.

## 3. Self-audit false-positive problem

A major live defect was that the system's own editorial audit reported PASS while the user immediately identified obvious reader-value failures.

Failure class candidates:
- `SELF_AUDIT_FALSE_POSITIVE`
- `DECLARED_RULE_TO_TEXTUAL_EVIDENCE_GAP`
- `SAME_MODEL_SELF_CERTIFICATION_GAP`

The repair direction is to require evidence-bearing findings (location / quoted or bounded text / defect / severity / disposition) and to keep same-session critique labeled `CHAT_SELF_REVIEW`, not independent certification.

## 4. Promotion/review governance failures encountered during the rebuild

Several process failures occurred while rebuilding Financial Writing 1.0.x:

1. **CI green was at times treated too optimistically.** Later review repeatedly found material bypasses despite a green suite.
2. **Review completion was once treated as equivalent to no findings.** This was false; a completed review could still add P1/P2 findings.
3. **Stale-head evidence risk recurred.** After every candidate-head mutation, old CI/review evidence had to be invalidated. Several times the process had to correct itself and re-lock to the latest exact head.
4. **1.0.1 was merged too early.** Production CI was green, but a later completed review contained 2 P1 + 1 P2 findings. A 1.0.2 hotfix became necessary.
5. Promotion therefore requires exact-head evidence freshness, explicit finding/thread inspection and production reread. `Completed`, `green CI` or an old review cannot individually certify promotion.

Parent-generalizable question: should UAOS define a common exact-head promotion-evidence freshness rule for governed child releases, while leaving the child's concrete CI/review topology domain-owned?

## 5. Financial 1.0.x technical admission defects found and retained as evidence

The following defects were discovered during adversarial review/self-review. They are primarily child-owned implementation failures, but the pattern is relevant to UAOS assurance claims.

### 5.1 Quality evidence / reviewer provenance
- terminal advancement did not initially revalidate persisted quality evidence strongly enough;
- `INDEPENDENT_EXECUTOR` could initially be self-attested by caller-provided identity/provenance;
- current hosted path has no owner-native independently verifiable executor, so independent assurance must fail closed to `CHAT_SELF_REVIEW` unless real external provenance exists.

### 5.2 Research saturation evidence
- saturation initially allowed repeated or semantically equivalent final sweeps;
- source-family entries could be empty/duplicated under weak normalization;
- final no-increment sweeps needed genuinely distinct search angle/query/source-family evidence rather than renamed repetition.

### 5.3 State-self-attestation and authority bypasses
- quality evidence and its receipt digest could initially be rewritten together inside the same caller-controlled state;
- current/legacy governance could be downgraded by changing/removing current markers;
- a process-local sequencing token was reachable and accepted by public APIs;
- public legacy task construction created a birth-time governance opt-out;
- caller state had to be bound to the authoritative GitHub `main` `STATE.json` blob SHA before material mutation.

### 5.4 Authoritative-state resolution defects
- GitHub Contents behavior for >1 MB state required Git Blob fallback while preserving the Contents-advertised blob SHA as authority;
- Python mapping equality collapsed JSON-distinct values such as `true` and `1`; authority comparison had to become JSON-type strict;
- task IDs with leading/trailing whitespace could alias repository paths if resolver and builder canonicalization differed.

### 5.5 Candidate mutation-isolation defects
A legal transition candidate could initially mutate unrelated state because validation checked only selected invariants.

The repair moved to immutable-by-default action ownership:
- transition-owned top-level surfaces only;
- feedback-owned surfaces only;
- unknown top-level fields immutable by default;
- exact nested delta constraints for stage artifacts, review decisions, quality evidence and delivery artifacts;
- prior execution receipt history type-strict append-only.

### 5.6 Transition semantic-closure defects
Review/self-review then found that “field exists” was not enough; action semantics also had to close:
- ordinary transition source must be `IN_PROGRESS`;
- blocked/terminal source cannot use ordinary forward transition;
- nonterminal non-FAIL routes remain `IN_PROGRESS`;
- non-review stages cannot inject review bindings;
- review decision must bind the exact admitted stage artifact;
- transition receipt path/SHA must bind the exact admitted artifact;
- duplicate `open_system_impact.signal_id` must be rejected;
- FAIL must persist an allowed canonical recovery cursor;
- feedback receipts must not carry review/recovery bindings;
- blocked recovery must trust only canonical FAIL `TRANSITION` receipts for the current stage/capability;
- REVISE provenance must bind the exact pre-invalidation reviewed artifact, not an after-state artifact that has already been invalidated.

### 5.7 Lifecycle / side-path closure
Authoritative-state preconditions had to cover not only the happy-path transition but also:
- material feedback;
- blocked recovery;
- system-impact lifecycle;
- proactive resolution.

Generalizable lesson: a strong main transition guard is insufficient if maintenance/recovery side paths can mutate the same authority object under weaker rules.

## 6. Tool / quota governance failure

The assistant repeatedly triggered GitHub `@codex review` while hardening PR #37. The user later reported that their 5-hour Codex allowance had reached zero and challenged why their Codex quota had been used.

Important evidence boundary: this child cannot prove which individual review call consumed how much quota. It **can** prove that repeated Codex review requests were initiated in this workflow, and that the workflow had turned Codex review into a de facto mandatory promotion gate without first establishing a quota/consent policy.

Failure classes:
- `USER_RESOURCE_BUDGET_UNGOVERNED`
- `OPTIONAL_EXTERNAL_REVIEWER_BECAME_REQUIRED_GATE`
- `TOOL_SELECTION_SIDE_EFFECT_NOT_SURFACED`

Required child repair:
- Codex review is optional supplementary evidence, not a required Financial promotion gate;
- Financial must have a no-Codex path using repository diff inspection, deterministic/adversarial regression, GitHub Actions CI, static audits, isolated wheel/package smoke, render smoke and explicit self-review assurance labeling;
- do not use quota-bearing external review as a default without a clear need and appropriate user/resource governance.

Parent question: should UAOS common tool governance require Agents to classify user-scoped paid/limited external tools as budget-bearing side effects and avoid making them hidden mandatory gates when a non-quota execution path exists?

## 7. Execution drift after the quota issue

After the user asked whether Codex had consumed their quota and whether another method was possible, the assistant answered by explaining alternatives instead of immediately continuing the already-authorized repair. The next user message correctly identified that the Agent had drifted again: execution should have continued automatically, and the response also omitted the required `Agent Progress` block.

Failure classes:
- `PROBLEM_TO_ACTION_CLOSURE_GAP__RECURRENCE`
- `EXPLANATION_SUBSTITUTED_FOR_AUTHORIZED_EXECUTION`
- `REQUIRED_PROGRESS_REPORT_OMISSION`

This is new live evidence that P-20261015-15's executable repair-or-block contract and P-20261015-16's inherited cognition auto-activation gap are not fully solved at the natural-language host/action-orchestration layer.

The user then explicitly required: **all encountered problems must be reported.** This incident is the direct durable response.

Parent question: how should UAOS mechanically ensure that a child does not regress from “repair-now” into explanation-only after a tool/policy surprise, and that mandatory progress/status reporting survives long maintenance sequences and connection interruptions?

## 8. Connection interruption / resumability observation

The conversation experienced repeated connection interruptions during a long maintenance sequence. Durable GitHub branch/PR/CI state allowed work to resume, which is positive evidence for externalized continuity.

However, repeated re-entry increased the risk of:
- using stale head/review evidence;
- re-explaining instead of executing;
- omitting required progress state.

No claim is made that connection interruption itself is a Financial defect. It is evidence that exact-head re-lock + durable progress reporting are important recovery invariants.

## 9. Child vs parent ownership

### Financial-owned repairs
Financial may and should repair:
- publication fitness gates;
- writing-pass architecture;
- exact-head promotion evidence inside its release process;
- authoritative state admission;
- candidate/lifecycle mutation isolation;
- no-Codex fallback promotion path;
- local regression/eval coverage.

### Parent-relevant / parent-adjudication requested
Financial requests UAOS re-adjudication/generalization for:
1. `INHERITED_COGNITION_AUTO_ACTIVATION_GAP` recurrence;
2. `PROBLEM_TO_ACTION_CLOSURE_GAP` recurrence after an unexpected tool/quota issue;
3. exact-head / stale-evidence promotion semantics as a possible common assurance primitive;
4. user-resource-budget / quota-bearing-tool governance;
5. external reviewer optionality / degraded-mode execution when user quota is exhausted;
6. mandatory progress/status continuity during long autonomous maintenance and interruption recovery.

Financial must not directly promote these child observations into UAOS authority.

## 10. Current disposition

- Financial 1.0.2 hotfix remains on PR #37 and is not production yet.
- The most recent exact candidate at the time of this incident must be re-read before any promotion claim; prior head CI/review evidence becomes stale after this incident/reporting commit.
- Codex review is no longer treated as a required promotion gate.
- Remaining promotion should use Financial-owned evidence and explicit assurance boundaries.
- All new material problems from this sequence must continue to be appended to the owner problem/evolution history and parent handoff, not left only in chat.
