# Audit module

## Independence
The final auditor re-evaluates the frozen final artifact/state. Writer self-assessment is not evidence of passing.

## Dedicated semantic gates before general editorial PASS
Two independent gates are mandatory on the frozen draft.

### Reader Funnel / Hook Gate
Load `references/hooks.md`. Audit, with text-level and current-search evidence where applicable:
- audience-promise fit;
- headline information value;
- curiosity/concreteness balance;
- current WeChat search discoverability and evidence refs;
- first-three-sentence retention;
- continuation flow across H1s and paragraph transitions;
- completion payoff;
- title/opening payoff.

Do not require cross-industry finance appeal for every title. Judge `FINANCE_DEEP` on qualified-reader fit and `FINANCE_BROAD` on broader traffic value without allowing bait-and-switch.

### Natural Authorial Prose / Writing DNA Gate
Load `references/style.md`. Do not judge “humanity” by slang, typos or AI-detector scores. Audit the consolidated nine dimensions with text-level evidence:
- fidelity and responsibility;
- semantic contribution;
- argument progression;
- reader calibration;
- authorial selectivity;
- evidence specificity;
- structural/rhythm naturalness;
- template/redundancy control;
- uncertainty/rhetoric calibration.

General editorial audit cannot PASS unless both dedicated gates PASS.

## Mode-specific content audit
For `FINANCE_DEEP`, audit **material completeness**, not selective-expression elegance. Compare the final article against the research package and editorial `completeness_obligations`. A material event leg, transmission link, company class, counterexample, why-this/why-not branch, validation/falsification condition, market-explanation branch or risk cannot be omitted merely to improve brevity.

For `FINANCE_BROAD`, selective compression is legal, but every retained conclusion must still have a complete supporting causal/evidence chain.

## Market-explanation audit
Load `references/market_explanation.md` whenever `ResearchPackage.market_explanation` is present.

The final auditor must independently check:
1. **economic benefit vs market selection are not conflated**;
2. relevant concept/subtheme/company coverage is represented or explicitly bounded;
3. material companies/classes are compared on topic-specific sensitivity dimensions rather than mere concept membership;
4. `why_this / why_not` is actually answered where market selection is discussed;
5. material competing mechanisms from research are represented rather than collapsed into a hindsight single-cause story;
6. causal wording respects the research confidence ladder (`VERIFIED_FACT`, `SUPPORTED_MECHANISM`, `PLAUSIBLE_INTERPRETATION`, `UNRESOLVED`);
7. a limit-up, strong return, turnover spike, fund-flow proxy, concept label or continued advance is not used as self-proving causal evidence;
8. continuation conditions and exhaustion/reversal conditions are both considered when persistence is material;
9. unresolved questions remain visible if the evidence cannot identify a cause;
10. none of this analysis turns into executable trading advice.

A polished causal story with weak identification is a **REVISE**, not a stylistic success.

## Mechanical gates
Use deterministic code where possible for:
- required Word artifacts and file identity;
- Word styles and Chinese numbering hierarchy;
- exact policy typography where mechanically inspectable;
- **zero tables**;
- company-name bolding;
- required explicit bold skim anchors;
- unambiguous actionable red-line phrases;
- risk/disclaimer presence and minimum substance;
- successful render output.

## Semantic gates
Use independent judgment for:
- evidence support/source boundary;
- FINANCE_DEEP completeness or FINANCE_BROAD legal compression;
- market-explanation completeness and causal-confidence discipline when applicable;
- Reader Funnel / Hook Gate;
- Natural Authorial Prose / Writing DNA Gate;
- **skim-path coherence: title + H1s + bold spans must recover the article's main line**;
- platform fit;
- context-sensitive compliance;
- risk-warning information quality;
- remaining uncertainty.

A successful render process is not itself proof of no clipping or bad pagination. Claim page inspection only when rendered pages were actually made available to and viewed by the auditor.

## Audit report
Generate `WRITING_AUDIT_REPORT.docx` from final state. Include task contract/distribution, source/evidence boundary, research coverage, mode-specific coverage obligations, market-explanation audit when applicable, Reader Funnel / Hook Gate, Natural Authorial Prose / Writing DNA Gate, general editorial, bold skim path, mechanical results, defects/fixes, remaining boundaries, knowledge reuse/writeback references and final artifact identities.

A missing audit report is a completion failure under Word delivery.

## Visible chat checklist
The final chat response must include a concise list of all required QA areas and statuses, including market-explanation completeness when applicable. It accompanies the audit Word document. It must not paste the article body.

## Writing-DNA learning boundary
Audit may identify candidate style lessons, but a single article or one external skill cannot silently become durable author identity. Durable promotion follows `references/style.md` and `references/maintenance.md`: explicit user rule or repeated evidence, with provenance and regression protection.

## Fail closed
No artifact may be COMPLETE while an applicable Must-Pass item lacks evidence. Changes to facts, market-explanation confidence/mechanisms, title, opening three sentences, H1/transition structure, body logic, bold skim anchors or formatting invalidate affected checks and require re-audit.