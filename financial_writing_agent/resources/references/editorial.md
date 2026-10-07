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
- Each mode plan records its selected structure, emphasis, natural side-focus statement, one or two company-selection dimensions, section-level acceptance expectations, and any outline-fingerprint collision evidence.
- Candidate structures must be generated from the current TopicDNA before recent-outline fingerprints are consulted. Fingerprints are collision checks, never structure-generation inputs or a rotation schedule.
- When a usable recent-outline history exists, compare against the most recent small set (normally up to the latest three relevant fingerprints) rather than searching old structures first and letting them seed the new outline.
- A mode may arrive at a structurally similar outline only when the current TopicDNA genuinely justifies it; record why the collision is acceptable rather than assuming DUAL means artificial difference.

A fixed “event → industry → stocks → market → next stage” skeleton is not a default. Market/fund flow, company comparison, policy, technical background, validation and “what next” are modules that may be integrated, demoted or omitted when they do not advance the current topic's causal logic.

## Information density
No default word-count target. Preserve independent facts, key numbers, causal steps, counterexamples, why-this/why-not, market-selection mechanism, validation/falsification conditions and risk boundaries.

Compress repeated explanation, textbook background, synonym restatement, examples that do not change judgment and long company lists without comparison value before cutting reasoning.

Research can be exhaustive while the article is selective, but the article must not imply that a selected subset is the whole universe. Make the chosen focus legible naturally in the lead or early prose when omission of non-focus branches could otherwise mislead the reader.

## Prose and continuity
Default to continuous report-style prose rather than fragmented notes or bullet-heavy pseudo-analysis. Lists are allowed when the content is genuinely list-like, but the article's reasoning should move through paragraphs.

Sections/paragraphs must have a visible relationship: cause, consequence, contrast, chronology, narrowing, comparison, or inference. Avoid abrupt topic jumps and stitched-block feel. Every major cross-layer move—news/event to industry, industry to company, company to market selection—should explain what the previous layer established and why the next layer is necessary.

Prefer conclusion-first openings when they reduce reader uncertainty: quickly establish what changed, why it matters and the central judgment. This is a soft editorial preference, not a mandatory identical opening formula.

Formal structural hierarchy maps to `一、二、三` → `（1）（2）（3）` → `①②③`. Mechanical numbering is owned by delivery code; the writer should not use `·` as a structural hierarchy marker. Use numbering to clarify real logical blocks, not to fragment continuous reasoning.

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

The opening should quickly perform three jobs without sounding formulaic: establish immediate relevance, upgrade the central contradiction, and make the reading payoff clear. These may span the first three sentences in a natural way. Opening facts must respect the same evidence boundary as title/H1 claims.

## H1 continuation contract
Every H1 is more than a directory label. Before drafting a selected structure, define for each H1:
- `directional_conclusion`: the directional conclusion or judgment the heading carries;
- `reader_gap`: the real information gap, mechanism, contrast, cost, benefit or unresolved quantity that remains worth reading for;
- `payoff_requirement`: what the section body must actually establish to pay off that gap;
- `logical_blocks`: the section's major semantic blocks, in order;
- `h3_required_h2_indexes`: only those second-level blocks that truly contain at least three explicit evidence/condition/dimension units and therefore need a third-level hierarchy.

`logical_blocks` has a dual role. A one-item list means the section remains one continuous H1-level reasoning block and should not invent H2 headings. A list with two or more items freezes the expected H2 labels/order. If an H2 later develops a real three-or-more-unit internal structure, mark its 1-based index in `h3_required_h2_indexes`; do not create H3 merely for decoration.

An H1 that only summarizes a topic, reports a number, names a category, or gives away the entire section without a continuation reason is weak. Hierarchy is a semantic structure decision first and a delivery-format check second—do not create headings merely to satisfy a count.

The final auditor must be able to map each H1 to its frozen directional judgment, continuation gap and concrete payoff location in the final prose. If that mapping cannot be made, the section design was not actually fulfilled.

## Acceptance contract
After mode-specific structures and selected headlines are frozen, the runtime builds a `WritingAcceptanceContract` before drafting proceeds. For each formal mode it freezes at least:
- selected title;
- selected structure identity;
- expected H1 count and section sequence;
- the serialized `section_expectations` for every H1: directional conclusion, reader gap, payoff requirement, logical-block plan and any required H3-bearing H2 indexes;
- independent-lead requirement;
- side-focus statement;
- company-selection basis;
- required outputs/delivery channel and visual boundary.

Formal acceptance freezing fails closed when an applicable mode lacks section expectations. The draft is then checked mechanically against the frozen H1/H2/H3 hierarchy. Semantic truth is not inferred from heading counts: FINAL separately supplies concrete frozen-final evidence for each H1's direction/gap/payoff contract.

Risk/disclaimer substance, Word/render status, artifact identity and knowledge-writeback status remain downstream schema/gate responsibilities rather than duplicated per-mode contract state. This prevents two competing sources of truth while preserving their mandatory completion gates.

Drafting is constrained by this contract. If later revision changes title/structure/section contract or upstream facts, the relevant contract/gates are invalidated and must be rebuilt rather than silently reusing stale PASS results.

## Company selection
Do not prescribe a fixed number of stocks or a fixed leader/mid-cap/follower template. Before deep company writing, establish one or two topic-specific selection dimensions such as industrial position, realization stage, budget entry, customer/order exposure, market role or another relevant contradiction.

The article must make the selection logic understandable. Research breadth may be much larger than the number of companies deeply written about. Industrial authenticity, earnings benefit, sentiment leadership and liquidity role can diverge; do not collapse them into a single ranking merely because one stock is prominent.

## Fact / inference / market layer
Keep four layers legible in the prose and editing logic:
- confirmed facts;
- industrial/economic inference built from those facts;
- expectations currently being traded by the market;
- unverified rumor or hypothesis.

Industry logic answers who may benefit and how profit transmits. Market logic answers whom the market is choosing, which name carries liquidity and which names are dropping out. They may corroborate one another but cannot impersonate one another. Market/fund-flow material belongs in the article only when it explains the topic.

## Ending and falsification
Do not force a universal “next stage / what to watch next / summary” ending. Close where the topic naturally closes: return to the opening contradiction, the decisive company difference, a policy/price/order/technology validation point, or a live disagreement. Preserve falsification awareness, but it need not be a dedicated section.

## Risk section
The writer returns a separate `risk_disclaimer` field for each formal article. Do not place a risk/disclaimer H1 inside article blocks. Deterministic delivery appends the final section so it cannot be omitted or duplicated by formatting drift.

## Style
Load `references/style.md` for anti-AI, individuality, backstage/prompt-leakage and extreme-language rules. Style must never override evidence accuracy.

## Editorial judge
Judge title/opening/structure separately from the writer. Use PASS/REVISE/FAIL with concrete evidence. Revision feedback identifies the first point where reasoning, transition, information density, reader motivation, H1 continuation promise, acceptance-contract fidelity or evidence-bounded style breaks.
