# Audit — Evidence-Backed Publication Fitness

Status: `CURRENT_CANDIDATE_1.0`
Owner: `DOMAIN:financial_writing`

## Purpose

Audit is an adversarial admission function. Its job is not to confirm that the writer followed instructions; its job is to find evidence that the publication candidate should **not** pass.

A bare rubric of PASS labels is not acceptance evidence.

## Assurance boundary

Same-session Writer/Reader/Editor/Style or other role passes remain `CHAT_SELF_REVIEW`. Different role names do not make them independent. `INDEPENDENT_EXECUTOR` may be claimed only when distinct execution evidence/provider identity is actually bound.

Deterministic checks prove only their specific invariants. They do not prove semantic quality.

## Current Publication Fitness contract

For each required long-form publication product, current 1.0 audit uses `financial_writing_agent.story_quality.PublicationFitness` with exactly these gates:

1. `FACT_INTEGRITY`
2. `RETENTION`
3. `COMPANY_GROUNDING`
4. `STRUCTURE_NUMBERING`
5. `ORIGINALITY`
6. `AUTHORIAL_STYLE`
7. `COMPLIANCE`
8. `PAYOFF`

Every gate must preserve:
- status `PASS` or `REVISE`;
- concrete text location;
- excerpt;
- finding;
- severity;
- what was actually checked;
- concrete revision action when REVISE.

A `MAJOR` or `CRITICAL` finding cannot coexist with a gate PASS. Any gate REVISE makes the product fitness REVISE.

## Gate semantics

### FACT_INTEGRITY

Check every material current number, policy/rule state, company claim, causal boundary and comparative statement against the audited evidence base. Distinguish observed fact from inference. A fact mismatch returns to RESEARCH or DRAFT depending on cause.

### RETENTION

Read as a cold target reader. Locate where the reader is likely to stop, skip or feel the article is repeating itself. Inspect title/opening, information gain per section, timing of company examples, transitions/open loops and whether the article still has a reason to continue after early orientation.

Do not pass merely because the opening contains a hook-shaped sentence.

### COMPANY_GROUNDING

Check that material economic mechanisms are demonstrated with named companies/cases when evidence exists. Reject long detached industry exposition followed by a company list. For multi-company work, require meaningful distinctions rather than concept-stock enumeration.

### STRUCTURE_NUMBERING

Check explicit contiguous Chinese H1 numbering and story progression. Mechanical sequence is necessary but insufficient: headings must also be information-bearing and each section must add a distinct reader job/payoff.

### ORIGINALITY

Review suspicious/distinctive wording and source-shaped structure against material sources. Record source ref, checked passage and result:
- `NO_MATERIAL_OVERLAP`;
- `COMMON_LANGUAGE`;
- `NEEDS_REWRITE`.

`NEEDS_REWRITE` blocks publication PASS. Close paraphrase/patchwriting is a revision condition even if words were locally substituted. Same-chat review must not claim universal/zero-plagiarism assurance.

### AUTHORIAL_STYLE

Look for generic model scaffolding, throat-clearing, abstract claims without concrete evidence, repetitive section rhythm, over-explanation, register drift and prose that visibly narrates its own checklist. Diagnostic phrase hits are evidence to inspect, not automatic authorship judgments.

### COMPLIANCE

Check finance non-actionability, uncertainty, source/privacy boundary and other publication redlines. Buy/sell, timing, target price, position sizing and covert equivalents remain prohibited.

### PAYOFF

Check whether the article actually answers the promise it makes. Title/opening questions must be resolved or explicitly bounded; the ending must leave a usable model/distinction/change condition rather than generic “持续关注”. Curiosity without payoff fails.

## Deterministic tripwires

Use code checks for properties that can be encoded safely, including:
- H1 sequence continuity;
- required material-company coverage where machine-readable;
- Deep value-chain blueprint coverage;
- source-provenance leakage phrases;
- clustered generic scaffolding as a semantic-review trigger;
- finance hard-fail phrases;
- Word typography/heading/table/underline/company-bold rules;
- artifact/output completeness;
- state/receipt identity and transition integrity.

Do not turn semantic properties such as “interesting”, “human”, “good hook” or “original” into fake numeric guarantees.

## Revision routing

Use the narrowest causal upstream target:
- evidence/value-chain/thesis defect -> `RESEARCH`;
- StoryBlueprint/company progression defect -> `EDITORIAL`;
- title promise defect -> `TITLE`;
- prose/retention/originality/style defect -> `DRAFT`;
- Word/render/artifact defect -> `DELIVERY`.

When an upstream input changes materially, dependent downstream PASS evidence is invalid and must be rerun.

## Current admission

For 1.0 tasks, `financial_writing_agent.current_admission.advance_state` validates PublicationFitness before allowing `EDITORIAL_AUDIT -> DELIVERY` on PASS. Therefore a persisted review file plus the string `PASS` is no longer enough on the current path.

## Historical audit compatibility

Historical HookAudit/StyleAudit/GateDecision receipts remain immutable evidence for historical tasks. They are not proof that a current 1.0 publication satisfies PublicationFitness. Do not rewrite old audits to manufacture new assurance.

## Final audit

Final Audit reconciles:
- required outputs and delivery hashes;
- PublicationFitness PASS for required long-form outputs;
- mechanical/render QA;
- current state/artifact identity;
- unresolved system-impact/evolution items and assurance boundaries.

Completion does not imply external certification unless separately obtained.
