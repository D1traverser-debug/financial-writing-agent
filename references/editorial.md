# Editorial module

## Principle
The research base may be broad; the article must be selective. Structure is derived from the topic's core contradiction, not from a fixed template.

Default formal output is Simplified Chinese financial prose.

## TopicDNA
Before drafting, determine:
- what genuinely changed;
- the main economic transmission chain;
- the most consequential reader misjudgment;
- one to three core contradictions;
- which company-comparison dimensions matter for this topic;
- what can be omitted/compressed without breaking reasoning.

Generate at least two candidate structures before reading recent outline fingerprints. `selected_structure` must be one of those candidates. Use fingerprints only as collision checks after the current topic produces its own candidates. `references/structure_patterns.md` is a design-pattern library, never a rotation schedule.

## Information density
No default word-count target. Preserve independent facts, key numbers, causal steps, counterexamples, why-this/why-not, market-selection mechanism, validation/falsification conditions and risk boundaries.

Compress repeated explanation, textbook background, synonym restatement, examples that do not change judgment and long company lists without comparison value before cutting reasoning.

## Prose and continuity
Default to continuous report-style prose rather than fragmented notes or bullet-heavy pseudo-analysis. Lists are allowed when the content is genuinely list-like, but the article's reasoning should move through paragraphs.

Sections/paragraphs must have a visible relationship: cause, consequence, contrast, chronology, narrowing, comparison, or inference. Avoid abrupt topic jumps and stitched-block feel.

Prefer conclusion-first openings when they reduce reader uncertainty: quickly establish what changed, why it matters and the central judgment. This is a soft editorial preference, not a mandatory identical opening formula.

Formal structural hierarchy should map to `一、二、三` → `（1）（2）（3）` → `①②③`. Mechanical numbering is owned by delivery code; the writer should not use `·` as a structural hierarchy marker.

## Two article modes
### FINANCE_DEEP
For finance communities. Preserve the full reasoning path and competitive logic among mapped companies. Readers should see how the conclusion was derived.

### FINANCE_BROAD
For broad-distribution platforms while remaining a financial article. Translate a sector-specific event into a finance-wide investment question; reduce entry cost, not analytical depth.

DUAL shares one research base but independently edits title, opening, structure and emphasis for each mode.

## Hook engine
Hooks are a three-layer system:
1. Headline earns the click.
2. Opening/lead proves the click was worth it quickly.
3. H1 sections create reasons to continue.

Formal applicable modes generate 8-12 headline candidates from different logical angles before one is selected; runtime validates candidate count and membership. Evaluate finance relevance, one primary contradiction/question, credible factual anchor when available, real information gap and cognitive load. Do not turn this into a fixed formula.

For FINANCE_BROAD ask why a finance reader who mainly follows another sector should care, using profit, valuation, pricing power, orders, cash flow, policy transmission, market selection or another supported cross-sector question.

Headline must be fully paid off by the opening. Do not make the topic unidentifiable, and do not reveal the entire reasoning chain in the headline.

## Risk section
The writer returns a separate `risk_disclaimer` field for each formal article. Do not place a risk/disclaimer H1 inside article blocks. Deterministic delivery appends the final section so it cannot be omitted or duplicated by formatting drift.

## Style
Load `references/style.md` for anti-AI, individuality and extreme-language rules. Style must never override evidence accuracy.

## Editorial judge
Judge title/opening/structure separately from the writer. Use PASS/REVISE/FAIL with evidence. Revision feedback identifies the first point where reasoning, transition, information density, reader motivation or evidence-bounded style breaks.
