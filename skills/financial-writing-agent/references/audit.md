# Audit module

## Ownership
Audit owns independent verification of the frozen research/draft/delivery state. It does not create missing evidence or repair prose by assertion. **Writer self-assessment is not PASS evidence.**

## Audit completeness principle — all applicable writing requirements are in scope
Audit is not a hand-picked subset of writing requirements. By default, **every applicable requirement owned by Research, Market Explanation, Editorial, Reader Funnel, Natural Authorial Prose, Delivery and finance-compliance policy is an audit obligation**.

A requirement may be omitted from a particular gate only when it is genuinely special to another mode/stage/surface. In that case the audit must either:
- point to the gate/surface that owns the check; or
- record an explicit `N_A` / `NOT_APPLICABLE` reason.

Silent omission is not legal. The detailed gate lists below identify ownership and high-risk checks; they do not cap the audit universe.

## Semantic-audit provenance hard gate
Every semantic audit decision carries provenance.

- `INDEPENDENT_EXECUTOR` means a separate stage-bound judge run with a distinct reviewer identity and execution reference.
- `CHAT_SELF_REVIEW` means the same chat/author is reviewing its own work without a separately evidenced judge run.

**CHAT_SELF_REVIEW can identify defects, but it cannot issue owner-native semantic PASS for Research Audit, Reader Funnel, Authorial Prose, General Editorial or Final Audit.** If the session lacks the owner runtime/independent judge capability, report the bounded assurance honestly rather than upgrading it.

A separate SDK judge run is independent for this workflow purpose, but is not the same as provider-isolated assurance. Do not overclaim isolation.

## Research audit — Universe recall and evidence-stage integrity are first-class targets
For company/theme topics, independently red-team the `Universe Coverage Ledger` before accepting “coverage complete”.

Check:
1. material economic/value-chain classes were enumerated before stock selection;
2. at least two materially different recall sources were used;
3. every universe company maps to a declared class;
4. obvious peers/material classes are included, explicitly excluded with evidence, or left as unresolved gaps;
5. `SATURATED` is not being claimed merely because repeated searches about the same familiar names found nothing new;
6. `MATERIAL / SECONDARY / REFERENCE_ONLY` labels are plausible rather than used to game Deep coverage;
7. business/financial realization stages have not been silently escalated.

The stage-integrity rule is domain-general: technology/product/capacity/order/delivery/revenue/profit/cash-flow are examples, not a permanent mandatory ladder. The audit asks whether the article inferred a later realization stage from an earlier one without evidence in the current topic.

A research package that deeply explains two familiar stocks while omitting material classes or peers is **REVISE**, not “focused research”.

## Dedicated semantic gates before general editorial PASS
Two dedicated gates are mandatory on the frozen draft. They specialize the review; they do not exempt the final audit from reconciling the complete applicable writing contract.

### Reader Funnel / Hook Gate
Load `hooks.md` and audit with text-level/current-search evidence:
- audience-promise fit;
- headline information value;
- curiosity/concreteness balance;
- **candidate-pool strategy diversity** across angle families;
- current WeChat search discoverability;
- selected opening strategy;
- early reader orientation / information scent;
- continuation value across H1s/paragraph flow;
- completion payoff;
- title-promise integrity and strategy-appropriate payoff timing.

The first three sentences are a diagnostic surface, not a universal hard checklist. An immediate-payoff lead may pass; a delayed/nut-graf, contradiction, question or scene/example lead may also pass when the delay is earned and the early opening still gives the reader sufficient orientation. Bait-and-switch or indefinite withholding fails.

Unique title strings are insufficient. A pool that mostly rewrites one mold (“真正的X不在Y”“X又动了看什么”“别只看X看Y”) fails strategy diversity.

A REVISE verdict identifies whether repair belongs to `TITLE` or `DRAFT`.

### Natural Authorial Prose / Writing DNA Gate
Load `style.md` and audit the exact nine dimensions:
- fidelity and responsibility;
- semantic contribution;
- argument progression;
- reader calibration;
- authorial selectivity;
- evidence specificity;
- structural/rhythm naturalness;
- template/redundancy control;
- uncertainty/rhetoric calibration.

The runtime's deterministic `template_signal_report` is mandatory evidence. When it reports `requires_revise=true`, `template_redundancy_control` cannot PASS until the repeated rhetorical scaffolding is rewritten.

The judge also checks that prose editing did not upgrade an earlier business-realization stage into a later one without evidence.

A REVISE verdict returns to `DRAFT`. Do not use AI-detector scores, slang or superficial “humanization” as evidence.

General editorial audit cannot PASS until both dedicated gates PASS at the assurance level available to the execution mode.

## Mode-specific content audit
For `FINANCE_DEEP`, compare the final article against audited research, `completeness_obligations`, `company_coverage_obligations`, and the Universe Coverage Ledger.

Hard requirements:
- every `MATERIAL` company appears in the Deep article;
- material value-chain classes are not silently omitted;
- `SECONDARY` companies may be grouped only when the grouping preserves the relevant distinction;
- the article cannot substitute “two representative stocks” for universe completeness;
- if the universe is `BOUNDED_WITH_GAPS`, the article preserves that boundary;
- validation/monitoring/realization sections that introduce material signals map those signals back to named stocks or clearly identified company classes;
- when company differentiation is a material reader question, the article performs a real evidence-bounded comparison rather than merely listing company cards.

Comparison may be a **major analytical focus** and may explicitly distinguish stronger/weaker evidence, faster/slower realization, higher/lower operating sensitivity or current/later validation. The prohibited boundary is executable trading instruction, not comparative emphasis.

A generic final checklist such as “看招标、看交付、看收入” after stock discussion fails if the reader cannot tell which stocks/classes each signal changes.

For `FINANCE_BROAD`, selective compression is legal, but every retained conclusion still needs its supporting facts, causal chain, counterevidence and uncertainty boundary.

## Numbered-navigation audit
Numbering is semantic navigation, not decoration, and FINANCE_DEEP should use it **generously when real branching exists**.

For FINANCE_DEEP, when the article contains several company classes, multiple realization stages, three or more comparison dimensions, or multiple causal branches, visible lower-level hierarchy `（1）（2）（3）/①②③` is required. A Deep article that hides these branches inside long continuous prose fails navigability even if it remains technically readable.

Do not require every H1 to have exactly three children. The number of subpoints follows the actual logic. Sequential reasoning may remain prose; real parallel structure should normally be visible.

## Market Explanation scope / audit
First verify the research scope declaration.

- `market_explanation_scope = REQUIRED`: a `market_explanation` map must exist and the final article must preserve the material branches needed by its mode.
- `market_explanation_scope = NOT_MATERIAL`: no market-explanation map should be present, and the article should not be forced to invent short-term price-selection analysis merely because companies are discussed.

When scope is `REQUIRED`, independently check:
1. economic benefit and market selection are not conflated;
2. material company/subtheme coverage is represented or explicitly bounded;
3. sensitivity comparisons are topic-specific rather than concept-membership lists;
4. `why_this / why_not` is answered where selection is discussed;
5. material competing mechanisms remain visible;
6. causal wording respects `VERIFIED_FACT / SUPPORTED_MECHANISM / PLAUSIBLE_INTERPRETATION / UNRESOLVED`;
7. price action, turnover, fund-flow proxies, concept labels or continuation are not self-proving causal evidence;
8. continuation and exhaustion/reversal evidence are both considered when persistence is material;
9. unresolved questions remain unresolved when identification is weak;
10. analysis never becomes executable trading advice.

A polished hindsight story with weak identification is REVISE.

## Macro editorial audit
General editorial audit owns section-level coherence and mode contract, not sentence-level style or reader-funnel duplication. Check:
- premises precede dependent conclusions;
- comparison dimensions precede ranking/selection claims;
- counterevidence is positioned where it can affect interpretation;
- major sections have distinct analytical jobs;
- company coverage remains traceable from research into Deep;
- stock-grounded validation/monitoring is present when applicable;
- numbered navigation is adequate and sufficiently used for branch complexity;
- information density is appropriate;
- skim-path content represents the article's real thesis beyond automatic stock-name emphasis;
- compliance/risk boundaries are intact.

If the defect originates upstream, use the earliest correct revision target among `RESEARCH / EDITORIAL / TITLE / DRAFT`.

## Mechanical gates
Use deterministic code for:
- every applicable Word article artifact exists;
- exact policy typography;
- legal Chinese hierarchy;
- **zero tables**;
- zero underlines;
- no publication-tail source section;
- **every exact occurrence of every supplied A-share company/stock name is bold**;
- declared explicit semantic skim anchors survive as Word bold;
- Deep lower-level numbered navigation is preserved when the article's branching requires it;
- exactly one non-empty inline italic risk/disclaimer paragraph;
- unambiguous actionable-finance red-line phrases;
- renderability when render QA is required.

Do not use a fixed risk-character minimum as a substitute for semantic review. The semantic audit checks whether the risk paragraph is topic-specific and information-complete while remaining concise.

Repeated render must be clean/idempotent; old page images cannot count as evidence for a revised document.

## Artifact privacy
Public MCP output and the audit Word must not expose server-local filesystem paths. Artifact identity should use kind, filename, hash/resource reference and availability.

## Final audit — complete contract reconciliation
The final auditor rechecks the frozen state after mechanical QA and reconciles **all applicable writing requirements**, not only the high-level categories named below. At minimum verify:
- research/evidence boundary, evidence-stage integrity and Universe Coverage Ledger;
- FINANCE_DEEP material/company completeness or FINANCE_BROAD legal compression;
- stock-grounded validation/monitoring sections;
- company-comparison quality and non-actionable boundary;
- Market Explanation scope and discipline when applicable;
- Reader Funnel including title-strategy diversity, opening strategy, early orientation and promise integrity;
- Natural Authorial Prose including deterministic template-cluster status;
- numbered navigation and whether real lower-level branches were surfaced;
- general editorial/macro structure;
- A-share company-name bolding plus semantic skim-path coherence;
- platform fit;
- context-sensitive compliance and concise-complete risk quality;
- remaining uncertainty;
- required Word artifacts and mechanical/render status;
- knowledge-sync decision;
- explicit `N_A` reasons for any owner requirement that genuinely does not apply to the current mode/topic/surface.

A REVISE/FAIL verdict identifies the earliest correct repair target among `RESEARCH / EDITORIAL / TITLE / DRAFT / DELIVERY`.

## Recoverable fail-closed behavior
FAIL may move the task to `BLOCKED`, but BLOCKED is not a terminal deadlock. The runtime persists a recovery cursor. After the evidenced blocker/dependency is repaired, `resume_blocked_task` resumes from that exact cursor rather than guessing a stage or starting a duplicate task.

## Audit report
Generate `WRITING_AUDIT_REPORT.docx` from final state. Include mode/source boundary, research coverage, **Universe Coverage Ledger**, Market Explanation scope, deep completeness/company obligations, Reader Funnel, Authorial Prose/template guard, numbered navigation, general editorial, company comparison, A-share bolding plus semantic skim path, mechanical results, defects/fixes, remaining boundaries, knowledge reuse/writeback, audit provenance, explicit N/A dispositions and public-safe artifact identities.

A missing audit report is a completion failure.

## Visible chat checklist
The final chat response contains a concise status list for applicable QA areas and accompanies the audit Word. It never pastes the article body.

## Writing DNA evidence boundary
Audit can identify candidate lessons, but one article or external skill cannot silently become durable author identity. Raw edits/feedback/performance can be stored through `record_writing_learning_sample`; every such record remains `RAW_EVIDENCE_ONLY` until promotion criteria in `style.md` and `maintenance.md` are met.

## Invalidation
Changes to material research facts/scope/universe coverage invalidate research and all dependent work. Editorial-plan changes invalidate title/draft/downstream QA. Title changes invalidate draft and downstream QA when the title change alters the article promise or packaging assumptions. Draft changes invalidate semantic/delivery/mechanical/final QA. Delivery changes invalidate mechanical/final QA.

Knowledge writeback is invalidated when its underlying research knowledge changes, not merely because wording/title/layout is revised.
