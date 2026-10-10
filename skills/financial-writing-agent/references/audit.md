# Audit module

## Ownership
Audit owns independent verification of the frozen research/draft/delivery state. It does not create missing evidence or repair prose by assertion. Writer self-assessment is not PASS evidence.

## Dedicated semantic gates before general editorial PASS
Two independent gates are mandatory on the frozen draft.

### Reader Funnel / Hook Gate
Load `hooks.md` and audit with text-level/current-search evidence:
- audience-promise fit;
- headline information value;
- curiosity/concreteness balance;
- current WeChat search discoverability;
- first-three-sentence retention;
- continuation value across H1s/paragraph flow;
- completion payoff;
- title/opening payoff.

A REVISE verdict must identify whether repair belongs to `TITLE` or `DRAFT`.

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

A REVISE verdict returns to `DRAFT`. Do not use AI-detector scores, slang or superficial “humanization” as evidence.

General editorial audit cannot PASS until both dedicated gates PASS.

## Mode-specific content audit
For `FINANCE_DEEP`, compare the final article against audited research and `completeness_obligations`. A material event leg, transmission link, company class, counterexample, `why_this / why_not`, validation/falsification condition or risk cannot be omitted merely for brevity.

For `FINANCE_BROAD`, selective compression is legal, but every retained conclusion still needs its supporting facts, causal chain, counterevidence and uncertainty boundary.

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
- information density is appropriate;
- skim-path content represents the article's real thesis;
- compliance/risk boundaries are intact.

If the defect originates upstream, use the earliest correct revision target among `RESEARCH / EDITORIAL / TITLE / DRAFT`.

## Mechanical gates
Use deterministic code for:
- every applicable Word article artifact exists;
- exact policy typography;
- legal Chinese hierarchy;
- **zero tables**;
- declared explicit bold skim anchors survive as Word bold;
- required risk/disclaimer presence and minimum substance;
- unambiguous actionable-finance red-line phrases;
- renderability when render QA is required.

Do **not** require every company/stock name to be bold. Company emphasis is semantic and selective.

Repeated render must be clean/idempotent; old page images cannot count as evidence for a revised document.

## Artifact privacy
Public MCP output and the audit Word must not expose server-local filesystem paths. Artifact identity should use kind, filename, hash/resource reference and availability.

## Final audit
The final auditor rechecks the frozen state after mechanical QA. At minimum verify:
- research/evidence boundary;
- FINANCE_DEEP completeness or FINANCE_BROAD legal compression;
- Market Explanation scope and discipline when applicable;
- Reader Funnel;
- Natural Authorial Prose;
- general editorial/macro structure;
- skim-path coherence;
- platform fit;
- context-sensitive compliance and risk quality;
- remaining uncertainty;
- required Word artifacts and mechanical/render status;
- knowledge-sync decision.

A REVISE/FAIL verdict must identify the earliest correct repair target among `RESEARCH / EDITORIAL / TITLE / DRAFT / DELIVERY`.

## Recoverable fail-closed behavior
FAIL may move the task to `BLOCKED`, but BLOCKED is not a terminal deadlock. The runtime must persist a recovery cursor. After the evidenced blocker/dependency is repaired, `resume_blocked_task` resumes from that exact cursor rather than guessing a stage or starting a duplicate task.

## Audit report
Generate `WRITING_AUDIT_REPORT.docx` from final state. Include mode/source boundary, research coverage, Market Explanation scope, deep completeness obligations where applicable, Reader Funnel, Authorial Prose, general editorial, skim path, mechanical results, defects/fixes, remaining boundaries, knowledge reuse/writeback and public-safe artifact identities.

A missing audit report is a completion failure.

## Visible chat checklist
The final chat response contains a concise status list for applicable QA areas and accompanies the audit Word. It never pastes the article body.

## Writing DNA evidence boundary
Audit can identify candidate lessons, but one article or external skill cannot silently become durable author identity. Raw edits/feedback/performance can be stored through `record_writing_learning_sample`; every such record remains `RAW_EVIDENCE_ONLY` until promotion criteria in `style.md` and `maintenance.md` are met.

## Invalidation
Changes to material research facts/scope invalidate research and all dependent work. Editorial-plan changes invalidate title/draft/downstream QA. Title changes invalidate draft and downstream QA. Draft changes invalidate semantic/delivery/mechanical/final QA. Delivery changes invalidate mechanical/final QA.

Knowledge writeback is invalidated when its underlying research knowledge changes, not merely because wording/title/layout is revised.
