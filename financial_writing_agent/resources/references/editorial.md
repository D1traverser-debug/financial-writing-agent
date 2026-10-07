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

TopicDNA is shared across a DUAL task because the evidence base and factual boundary are shared. The actual article architecture is not shared automatically.

## Mode-specific editorial plans
For every applicable output mode, build a separate `ModeEditorialPlan`.

- `FINANCE_DEEP` and `FINANCE_BROAD` in a DUAL task each generate **2–3 independent candidate structures** and select one independently.
- Do not generate one outline and merely change emphasis labels for two versions.
- Each mode plan records its selected structure, emphasis, natural side-focus statement, one or two company-selection dimensions, and any outline-fingerprint collision evidence.
- Candidate structures must be generated from the current TopicDNA before recent-outline fingerprints are consulted. Fingerprints are collision checks, never structure-generation inputs or a rotation schedule.
- A mode may arrive at a structurally similar outline only when the current TopicDNA genuinely justifies it; record why the collision is acceptable rather than assuming DUAL means artificial difference.

## Information density
No default word-count target. Preserve independent facts, key numbers, causal steps, counterexamples, why-this/why-not, market-selection mechanism, validation/falsification conditions and risk boundaries.

Compress repeated explanation, textbook background, synonym restatement, examples that do not change judgment and long company lists without comparison value before cutting reasoning.

## Prose and continuity
Default to continuous report-style prose rather than fragmented notes or bullet-heavy pseudo-analysis. Lists are allowed when the content is genuinely list-like, but the article's reasoning should move through paragraphs.

Sections/paragraphs must have a visible relationship: cause, consequence, contrast, chronology, narrowing, comparison, or inference. Avoid abrupt topic jumps and stitched-block feel.

Prefer conclusion-first openings when they reduce reader uncertainty: quickly establish what changed, why it matters and the central judgment. This is a soft editorial preference, not a mandatory identical opening formula.

Formal structural hierarchy maps to `一、二、三` → `（1）（2）（3）` → `①②③`. Mechanical numbering is owned by delivery code; the writer should not use `·` as a structural hierarchy marker.

## Two article modes
### FINANCE_DEEP
For finance communities. Preserve the full reasoning path, counterevidence, company comparison, `why_this / why_not`, and market-selection logic. Readers should see how the conclusion was derived.

### FINANCE_BROAD
For broad-distribution platforms while remaining a financial article. Translate a sector-specific event into a finance-wide investment question; reduce entry cost, not analytical depth. Preserve at least one complete core causal chain.

DUAL shares one research/evidence base but independently edits title, independent lead, structure, emphasis and length. Facts, evidence strength, entity identity, conclusion boundary and risk boundary must remain consistent across versions.

## Hook engine
Hooks are a three-layer system:
1. Headline earns the click.
2. Independent lead/opening proves the click was worth it quickly.
3. H1 sections create reasons to continue.

Before headline generation, internally answer: why the target finance reader should care, the one primary contradiction, default expectation, strongest verified counter-expectation fact, credible anchor, real information gap, cognitive-load risk, and how the opening will pay off the title.

Formal applicable modes generate 8–12 headline candidates from genuinely different logical angles before one is selected. Every `HeadlineCandidate` must record:
- `factual_anchor`: a claim already safe enough in the research evidence ledger;
- one primary information gap;
- `opening_payoff`: how the first screen will satisfy the click;
- finance relevance and cognitive load.

Do not use an unverified dramatic fact merely because it makes a stronger hook. Headline must be fully paid off by the opening. Do not make the topic unidentifiable, and do not reveal the entire reasoning chain in the headline.

For FINANCE_BROAD ask why a finance reader who mainly follows another sector should care, using profit, valuation, pricing power, orders, cash flow, policy transmission, market selection or another supported cross-sector question.

## Independent lead
Every formal `ArticlePayload` contains exactly one `lead` block, and it is the first block. The first H1 follows immediately after it. A body paragraph that happens to be near the top is not an independent lead.

The lead should establish immediate relevance, upgrade the contradiction and state the reading payoff without mechanically restating the headline. The opening facts must respect the same evidence boundary as title/H1 claims.

## Acceptance contract
After mode-specific structures and selected headlines are frozen, the runtime builds a `WritingAcceptanceContract` before drafting proceeds. For each formal mode it freezes at least:
- selected title;
- selected structure identity;
- expected H1 count and section functions;
- independent-lead requirement;
- side-focus statement;
- company-selection basis;
- required outputs/delivery channel and visual boundary.

Drafting is constrained by this contract. If later revision changes title/structure or upstream facts, the relevant contract/gates are invalidated and must be rebuilt rather than silently reusing stale PASS results.

## Company selection
Do not prescribe a fixed number of stocks or a fixed leader/mid-cap/follower template. Before deep company writing, establish one or two topic-specific selection dimensions such as industrial position, realization stage, budget entry, customer/order exposure, market role or another relevant contradiction.

The article must make the selection logic understandable. Research breadth may be much larger than the number of companies deeply written about.

## Risk section
The writer returns a separate `risk_disclaimer` field for each formal article. Do not place a risk/disclaimer H1 inside article blocks. Deterministic delivery appends the final section so it cannot be omitted or duplicated by formatting drift.

## Style
Load `references/style.md` for anti-AI, individuality and extreme-language rules. Style must never override evidence accuracy.

## Editorial judge
Judge title/opening/structure separately from the writer. Use PASS/REVISE/FAIL with concrete evidence. Revision feedback identifies the first point where reasoning, transition, information density, reader motivation, acceptance-contract fidelity or evidence-bounded style breaks.
