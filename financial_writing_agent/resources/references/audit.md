# Audit — Evidence-Backed Publication Fitness

Status: `CURRENT_CANDIDATE_1.0`
Owner: `DOMAIN:financial_writing`

## Purpose

Audit is an adversarial admission function. Its job is not to confirm that the writer followed instructions; its job is to find evidence that the publication candidate should **not** pass.

A bare rubric of PASS labels is not acceptance evidence.

## Assurance boundary

Same-session Writer/Reader/Editor/Style or other role passes remain `CHAT_SELF_REVIEW`. Different role names do not make them independent. `INDEPENDENT_EXECUTOR` may be claimed only when distinct execution evidence/provider identity is actually bound.

Deterministic checks prove only their specific invariants. They do not prove semantic quality.

## Research Audit — PrivateResearchBrief admission

For new tasks marked with `private_research_contract_version=1.1`, RESEARCH_AUDIT must treat the admitted `quality_evidence.private_research_brief` as mandatory research evidence, not as an optional attachment. Historical states explicitly carrying `1.0` remain auditable under the original 1.0 module set.

Research Audit must REVISE to RESEARCH when any material condition below is true:
- the private brief is absent, structurally invalid or not digest-bound to the RESEARCH receipt;
- a required module for the bound contract version is missing;
- a material module is marked `NOT_MATERIAL` merely to avoid doing the work;
- the company/value-chain universe silently omits a known material branch or weak-tag/excluded names are unaccounted for;
- company comparison stops at concept-stock enumeration rather than explaining `why A rather than B`;
- material short-horizon candidates lack current total/float market cap and liquidity when market selection is part of the task;
- catalyst strength/freshness is not distinguished from old news or expectation already priced;
- for 1.1 tasks, the material event/policy ledger omits a known consequential event or a material policy phase such as announcement, implementation, suspension, reduction, extension, exemption, retaliation, expiry or rollback;
- policy research is one-sided — for example it records tariff tightening but silently drops a later negotiated reduction/suspension that materially changes the economics, or vice versa;
- driver, sustainability, market operability and concept/sector identity are collapsed into one vague score rather than separately evidenced;
- the concept label used to explain price action is not distinguished from competing/current price drivers;
- short-horizon role labels such as pioneer, leader, middle-army, branch leader, card-position or catch-up are asserted without observable role logic;
- role vocabulary is treated as a quota, forcing separate leaders/middle-armies/branch leaders when the observed market can support only one core or one stock legitimately combines roles;
- `business strongest` is collapsed into `most likely short-horizon market core` without separate evidence;
- within-segment comparisons are completed but no 1.1 cross-segment global selection is performed under current liquidity/sentiment constraints;
- the global-selection conclusion does not identify the current core hypothesis, challengers/role-switch conditions or explicitly state that no unique core is yet justified;
- market/theme liquidity capacity is ignored when deciding how many cores/branches can realistically survive;
- negative/falsification candidates are erased rather than retained;
- a broad scenario ladder is invented for a narrow catalyst without causal support;
- next-window confirmation/falsification conditions are absent where market behavior is material;
- time-sensitive fields are stale relative to the decision being made;
- publication distillation fails to separate private analytical machinery from the reader-facing article;
- Deep distillation turns material multi-company comparisons into parallel company profiles instead of preserving the causal reason why one logic/business model is stronger or weaker than another.

The audit is semantic as well as structural. A syntactically complete brief with placeholder summaries or token evidence refs is not a substantive PASS.

## Current Publication Fitness contract

For each required long-form publication product, current audit uses `financial_writing_agent.story_quality.PublicationFitness` with exactly these gates:

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

Check every material current number, policy/rule state, company claim, causal boundary and comparative statement against the audited evidence base. Distinguish observed fact from inference. For event-led work, verify chronology and current status rather than quoting one policy phase out of sequence. A fact mismatch returns to RESEARCH or DRAFT depending on cause.

### RETENTION

Read as a cold target reader. Locate where the reader is likely to stop, skip or feel the article is repeating itself. Inspect title/opening, information gain per section, timing of company examples, transitions/open loops and whether the article still has a reason to continue after early orientation.

Do not pass merely because the opening contains a hook-shaped sentence.

### COMPANY_GROUNDING

Check that material economic mechanisms are demonstrated with named companies/cases when evidence exists. Reject long detached industry exposition followed by a company list. For multi-company work, require meaningful distinctions rather than concept-stock enumeration.

For marker-enabled tasks, compare the publication against the private brief's `publication_distillation`: the article may omit private machinery, but it must not contradict or silently discard a material causal distinction that the admitted research says is necessary to the reader payoff.

For `FINANCE_DEEP`, when the private brief identifies material alternatives or cross-segment competition, verify that the prose explains the decisive comparison — for example why A has stronger transmission, realization or durability than B under the same event. A sequence of isolated company mini-profiles does not satisfy this requirement merely because every company is named.

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

Private research vocabulary such as universe bookkeeping, internal scores, ladder mechanics or audit process should not leak into the article merely because it existed upstream. It belongs in copy only when it materially improves reader understanding.

### COMPLIANCE

Check finance non-actionability, uncertainty, source/privacy boundary and other publication redlines. Buy/sell, timing, target price, position sizing and covert equivalents remain prohibited.

### PAYOFF

Check whether the article actually answers the promise it makes. Title/opening questions must be resolved or explicitly bounded; the ending must leave a usable model/distinction/change condition rather than generic “持续关注”. Curiosity without payoff fails.

## Deterministic tripwires

Use code checks for properties that can be encoded safely, including:
- H1 sequence continuity;
- required material-company coverage where machine-readable;
- PrivateResearchBrief contract presence/digest binding on marker-enabled tasks;
- required 1.1 private-research module presence;
- Deep value-chain blueprint coverage;
- source-provenance leakage phrases;
- clustered generic scaffolding as a semantic-review trigger;
- finance hard-fail phrases;
- Word typography/heading/table/underline/company-bold rules;
- artifact/output completeness;
- state/receipt identity and transition integrity.

Do not turn semantic properties such as “interesting”, “human”, “good hook”, “true leader”, “sustainable”, “operable” or “original” into fake numeric guarantees.

## Revision routing

Use the narrowest causal upstream target:
- evidence/value-chain/private-research/event-ledger/global-selection/thesis defect -> `RESEARCH`;
- StoryBlueprint/company progression/comparative-logic defect -> `EDITORIAL`;
- title promise defect -> `TITLE`;
- prose/retention/originality/style defect -> `DRAFT`;
- Word/render/artifact defect -> `DELIVERY`.

When an upstream input changes materially, dependent downstream PASS evidence is invalid and must be rerun.

## Current admission

For marker-enabled new tasks, `financial_writing_agent.current_admission.advance_state` validates both the material DecisionEnvelope and PrivateResearchBrief before allowing `RESEARCH -> RESEARCH_AUDIT`, then digest-binds both to the RESEARCH receipt.

New tasks bind private-research contract `1.1`; historical states explicitly bound to `1.0` remain readable and are validated against the original 1.0 module set. A brief version must match the state marker.

The same admission layer validates PublicationFitness before allowing `EDITORIAL_AUDIT -> DELIVERY` on PASS. Therefore a persisted review file plus the string `PASS` is no longer enough on the current path.

Historical/current states created before the private-research marker remain valid provenance and are not retroactively rewritten. New tasks created through current admission are marker-enabled by default.

## Historical audit compatibility

Historical HookAudit/StyleAudit/GateDecision receipts remain immutable evidence for historical tasks. They are not proof that a current publication satisfies PublicationFitness. Do not rewrite old audits to manufacture new assurance.

## Final audit

Final Audit reconciles:
- required outputs and delivery hashes;
- admitted research decision and, when marker-enabled, PrivateResearchBrief;
- PublicationFitness PASS for required long-form outputs;
- mechanical/render QA;
- current state/artifact identity;
- unresolved system-impact/evolution items and assurance boundaries.

Completion does not imply external certification unless separately obtained.
