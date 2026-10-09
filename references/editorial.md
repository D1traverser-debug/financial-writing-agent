# Editorial module

## Principle
Research is broad for every formal article. **FINANCE_DEEP and FINANCE_BROAD now have different expression contracts.**

- `FINANCE_DEEP` is the comprehensive financial version. It must express every **material** branch that could change a financially literate reader's judgment. It may compress low-materiality repetition, but it must not omit a material event leg, transmission link, company class, counterexample, `why_this/why_not`, validation condition or risk merely to make the article shorter or cleaner.
- `FINANCE_BROAD` is the traffic-oriented broad-distribution version. It may select and compress around one to three core contradictions/information gaps so long as the retained chain remains factually complete enough to support its conclusions.

“Comprehensive” is bounded by the audited ResearchPackage, not by an impossible infinite universe. The deep article is material-complete relative to the bounded research universe.

Default formal output is Simplified Chinese financial prose.

## Shared TopicDNA
Before mode-specific structuring, determine:
- what genuinely changed;
- the main economic transmission chain;
- the most consequential reader misjudgment;
- which company-comparison dimensions matter for this topic;
- the finance-wide question that makes the topic relevant beyond its immediate sector.

**Do not use a shared `core_contradictions` or shared `compression_candidates` field to govern FINANCE_DEEP.** Those selection devices belong only to the broad/traffic version.

## FINANCE_DEEP plan
The deep plan must declare explicit `completeness_obligations`: the material dimensions/branches that the final article must cover. Typical obligations may include event chronology, industrial/economic transmission, relevant company categories, business-stage differences, financial realization, market-selection logic, counterevidence, validation/falsification and risks. The exact list is topic-specific.

The deep version may prioritize and sequence, but not selectively hide a material branch. If a material item is intentionally excluded, it must be named as an explicit research boundary rather than silently omitted.

## FINANCE_BROAD plan
The broad/traffic version may identify one to three `core_contradictions` and `compression_candidates`. It should lower entry cost and maximize completion while preserving factual support and the causal chain needed for its conclusions.

Broad does **not** mean shallow, generic or inaccurate. It means a more selective route through the same evidence base.

## Information density
No default word-count target. Preserve independent facts, key numbers, causal steps, counterexamples, why-this/why-not, market-selection mechanism, validation/falsification conditions and risk boundaries according to the applicable mode contract.

For FINANCE_DEEP, compression may remove only repetition, textbook background, synonym restatement and immaterial detail. It must not remove material analytical branches.

For FINANCE_BROAD, additional selective compression is allowed when the retained article still fully supports its claims.

## Prose, numbering and continuity
Use continuous report-style prose, but use the formal hierarchy **frequently when the reasoning genuinely contains layers, steps, comparisons or categories**:
`一、二、三` → `（1）（2）（3）` → `①②③`.

“More numbering” means clearer visible structure, not mechanical “首先/其次/最后” filler. Paragraph transitions must still follow the actual causal/comparative/chronological/inferential logic.

Tables are not used in publication articles. Convert comparison material into numbered prose with explicit dimensions and conclusions.

Sections/paragraphs must have a visible relationship: cause, consequence, contrast, chronology, narrowing, comparison, correction or inference. Avoid abrupt topic jumps and stitched-block feel.

## Two article modes
### FINANCE_DEEP
For finance communities and readers seeking full financial analysis. Preserve the full bounded reasoning path and all material coverage obligations. Readers should be able to audit how the conclusion was derived and what could invalidate it.

### FINANCE_BROAD
For broad-distribution / traffic acquisition while remaining a financial article. Translate a sector event into a finance-wide reason to care, reduce first-read cognitive cost and selectively emphasize the strongest supported route through the evidence.

`DUAL` shares one research base but independently edits title, opening, structure and emphasis for each mode. It does **not** force the deep version to adopt the broad version's compression.

## Hook engine
Load `references/hooks.md`. Hooks are independently audited after the draft is frozen. Title, first three sentences, H1s and paragraph transitions form a single completion funnel, but their criteria are checked separately from human-voice/style.

Formal applicable modes generate 8–12 headline candidates from genuinely different logical angles. The selected title must satisfy both cross-finance clickability and current WeChat search-intent consideration; these are separate requirements.

## Bold skim path
Load `references/style.md`. Keywords, key numbers and selected key judgment sentences should be bold so that **title + H1s + bold spans** reconstruct the article's main line for a fast reader. Do not over-bold.

## Risk section
The writer returns a separate `risk_disclaimer` field for each formal article. Do not place a risk/disclaimer H1 inside article blocks. Deterministic delivery appends the final section so it cannot be omitted or duplicated by formatting drift.

## Editorial judge
General editorial audit is independent from both the Hook Gate and Human Voice Gate. It checks evidence, mode-specific coverage/compression legality, reasoning continuity, information density, reader motivation and compliance. PASS is illegal until both dedicated gates PASS.