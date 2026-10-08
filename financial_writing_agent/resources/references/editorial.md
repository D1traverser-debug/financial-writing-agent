# Editorial module

## Principle
The research base may be broad; the article must be selective. Structure is derived from the topic's core contradiction, not from a fixed template.

Default formal output is Simplified Chinese financial prose.

For recommendation-oriented A-share articles, selection is allowed only after broad research. Editorial compression must never be used to hide shallow company work.

## TopicDNA
Before drafting, determine:
- what genuinely changed;
- the main economic transmission chain;
- the most consequential reader misjudgment;
- one to three core contradictions;
- which company-comparison dimensions matter for this topic;
- what can be omitted/compressed without breaking reasoning.

TopicDNA is shared across a DUAL task because the evidence base and factual boundary are shared.

## Mode-specific editorial plans
For every applicable output mode, build a `ModeEditorialPlan`.

### FINANCE_DEEP is the analytical master version
For a DUAL task, solve `FINANCE_DEEP` first. Generate **2–3 candidate structures** from the current TopicDNA and select the strongest structure for complete analytical expression. This version is the analytical mother article: the full causal chain, company comparison, market-position logic, `why_this / why_not`, counterevidence and current stock judgments are solved here before broad-distribution compression.

### FINANCE_BROAD is a derived adaptation
After the finance logic has been solved in FINANCE_DEEP, derive FINANCE_BROAD from that analytical master. It may reorder exposition, reduce background, merge secondary branches, sharpen the opening and use stronger hook packaging, but it must not invent a different factual thesis, stronger unsupported claim, contradictory company ranking or different stock judgment merely to manufacture novelty.

Do **not** treat DUAL as two independently invented analyses. FINANCE_BROAD exists to make the already-solved finance logic easier to enter, faster to understand and more attractive to click/read while preserving the mother version's factual identities, evidence strength, decisive causal chain and judgment boundary.

Each mode plan records its selected structure, emphasis, natural side-focus statement, one or two company-selection dimensions, section-level acceptance expectations, and any outline-fingerprint collision evidence.

Candidate structures must be generated from the current TopicDNA before recent-outline fingerprints are consulted. Fingerprints are collision checks, never structure-generation inputs or a rotation schedule. When a usable recent-outline history exists, compare against the most recent small set (normally up to the latest three relevant fingerprints) rather than searching old structures first and letting them seed the new outline.

A fixed “event → industry → stocks → market → next stage” skeleton is not a default. Market/fund flow, company comparison, policy, technical background, validation and “what next” are modules that may be integrated, demoted or omitted when they do not advance the current topic's causal logic.

## Information density and length
There is no minimum word-count target. Preserve independent facts, key numbers, causal steps, counterexamples, `why_this / why_not`, market-selection mechanism, validation/falsification conditions and risk boundaries.

For FINANCE_DEEP, completeness takes priority over arbitrary brevity. Do not cut a useful reasoning chain merely to satisfy a cosmetic target. The default hard editorial ceiling is approximately **10,000 Chinese characters** for the publishable article body unless the user explicitly requests another ceiling; this is an upper bound, not a target.

Compress repeated explanation, textbook background, synonym restatement, examples that do not change judgment and long company lists without comparison value before cutting reasoning.

FINANCE_BROAD must be materially more compressed than the completed FINANCE_DEEP mother version. Compression may remove low-value background and secondary branches, but it must retain the strongest contradiction, at least one complete core causal chain, the important company/stock conclusion and the evidence boundary that makes that conclusion defensible.

Research can be exhaustive while the article is selective, but the article must not imply that a selected subset is the whole universe. Make the chosen focus legible naturally in the lead or early prose when omission of non-focus branches could otherwise mislead the reader.

## Prose and continuity
Default to continuous report-style prose rather than fragmented notes or bullet-heavy pseudo-analysis. Lists are allowed when the content is genuinely list-like, but the article's reasoning should move through paragraphs.

Sections/paragraphs must have a visible relationship: cause, consequence, contrast, chronology, narrowing, comparison, or inference. Avoid abrupt topic jumps and stitched-block feel. Every major cross-layer move—news/event to industry, industry to company, company to market selection—should explain what the previous layer established and why the next layer is necessary.

Prefer conclusion-first openings when they reduce reader uncertainty: quickly establish what changed, why it matters and the central judgment. This is a soft editorial preference, not a mandatory identical opening formula.

Formal structural hierarchy maps to `一、二、三` → `（1）（2）（3）` → `①②③`. Mechanical numbering is owned by delivery code; the writer should not use `·` as a structural hierarchy marker. Use numbering to clarify real logical blocks, not to fragment continuous reasoning.

## Two article modes
### FINANCE_DEEP
For finance communities. This is the analytical mother version. Preserve the full reasoning path, counterevidence, company comparison, `why_this / why_not`, market-selection logic, current company/stock state and the evidence needed to explain why one stock ranks above or below another. Readers should be able to recover how the conclusion was derived.

### FINANCE_BROAD
For broad-distribution platforms while remaining a financial article. It is derived **after** the finance logic has been solved in FINANCE_DEEP. Translate that result into a lower-friction finance-wide question, compress secondary detail, improve scanability and strengthen the hook. Reader acquisition has higher packaging priority here, but hook strength never authorizes factual distortion, fake suspense or a weaker analytical boundary.

DUAL therefore uses one research/evidence base and one FINANCE_DEEP analytical mother version. FINANCE_BROAD is a controlled derivative: title, lead, section order and emphasis may change for click/read efficiency, but facts, evidence strength, entity identity, core causal chain, stock judgment, conclusion boundary and risk boundary must remain consistent.

## Hook engine
Hooks are a linked system, not merely a catchy title:
1. **Headline hook** earns the click with a truthful reason to care.
2. **Opening hook** proves the click was worth it in the first screen / first three sentences.
3. **Section hook** gives a concrete reason to continue into each H1.
4. **Company/stock hook** turns abstract industry logic into a specific comparison or judgment the reader wants resolved when stocks are material.

Before headline generation, internally answer:
- who the target reader is and why the topic matters to that reader **now**;
- the primary contradiction, consequence or anti-expectation;
- what the reader would normally assume before reading;
- the strongest verified fact that changes or sharpens that default expectation;
- the concrete stake: profit, order, price, valuation, cash flow, policy transmission, competitive position, market selection, timing or another supported consequence;
- the specific information gap deliberately left unresolved by the title;
- which company/stock comparison can make that gap concrete when relevant;
- the title's cognitive-load risk;
- exactly how the opening will pay off the title without bait-and-switch.

Formal applicable modes generate **8–12 headline candidates** from genuinely different hook mechanisms before one is selected. Candidate diversity should normally span several of the following when the evidence permits:
- contradiction / anti-expectation;
- consequence / stakes;
- verified number or scale;
- company divergence / comparison;
- market selection / 身位 difference;
- timing or policy inflection;
- causal “why” question;
- result-first framing;
- finance-wide relevance for readers outside the sector.

Do not create 8–12 superficial paraphrases of one title. Swapping punctuation, nouns or question marks is not candidate diversity.

Every `HeadlineCandidate` must record:
- the hook mechanism/angle;
- `factual_anchor`: a claim already safe enough in the research evidence ledger;
- a concrete reader stake / finance relevance;
- one primary information gap;
- `opening_payoff`: how the first screen will satisfy the click;
- cognitive load.

Do not use an unverified dramatic fact merely because it makes a stronger hook. The headline must be fully paid off by the opening. Do not make the topic unidentifiable, do not fake suspense where the answer is already known, and do not reveal the entire reasoning chain in the title.

For FINANCE_DEEP, prioritize precision, contradiction quality and analytical stakes. For FINANCE_BROAD, the hook is a first-class distribution requirement: ask why a finance reader who mainly follows another sector should care, reduce jargon cost, foreground the strongest verified contradiction/consequence, and make the article's payoff visible quickly.

## Independent lead
Every formal `ArticlePayload` contains exactly one `lead` block, and it is the first block. The first H1 follows immediately after it. A body paragraph that happens to be near the top is not an independent lead.

The opening should quickly perform three jobs without sounding formulaic: establish immediate relevance, upgrade the central contradiction, and make the reading payoff clear. These may span the first three sentences naturally. Opening facts must respect the same evidence boundary as title/H1 claims.

For FINANCE_BROAD, the opening must also convert the mother version's analysis into a low-friction entry point: the reader should understand within the first screen why this matters and what concrete judgment will be resolved.

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
After the applicable structure and selected headline are frozen, the runtime builds a `WritingAcceptanceContract` before that draft proceeds. For each formal mode it freezes at least:
- selected title;
- selected structure identity;
- expected H1 count and section sequence;
- the serialized `section_expectations` for every H1: directional conclusion, reader gap, payoff requirement, logical-block plan and any required H3-bearing H2 indexes;
- independent-lead requirement;
- side-focus statement;
- company-selection basis;
- required outputs/delivery channel and visual boundary.

For DUAL, the FINANCE_DEEP acceptance contract is the analytical mother contract. FINANCE_BROAD is later frozen as a derivative contract whose thesis/stock judgment boundary must remain compatible with the completed FINANCE_DEEP mother version.

Formal acceptance freezing fails closed when an applicable mode lacks section expectations. Drafting is checked mechanically against the frozen H1/H2/H3 hierarchy. Semantic truth is not inferred from heading counts: FINAL separately supplies concrete frozen-final evidence for each H1's direction/gap/payoff contract.

Risk/disclaimer substance, Word/render status, artifact identity and knowledge-writeback status remain downstream schema/gate responsibilities rather than duplicated per-mode contract state.

If later revision changes title/structure/section contract or upstream facts, the relevant contract/gates are invalidated and must be rebuilt rather than silently reusing stale PASS results.

## Company selection and stock-judgment discipline
Do not prescribe a fixed number of stocks or a fixed leader/mid-cap/follower template. Before deep company writing, establish one or two topic-specific selection dimensions such as industrial position, realization stage, budget entry, customer/order exposure, market role or another relevant contradiction.

Any stock/company actually mentioned as part of the article's recommendation/comparison logic should be deeply researched before publication rather than added from familiarity or concept labels. The research should make clear, when material:
- what the company actually does and where it sits in the industry chain;
- factual exposure versus narrative exposure;
- order/customer/revenue/profit/capacity/price evidence that matters for this topic;
- business/earnings realization stage;
- industrial beneficiary role versus sentiment/market role;
- current short-term market role, 身位 and liquidity role when relevant;
- positive evidence and negative/counterevidence;
- `why_this` and `why_not` versus meaningful alternatives;
- the current evidence-bounded judgment on the stock/company **now**, not only a list of variables to watch.

The article must make the selection logic understandable. Industrial authenticity, earnings benefit, sentiment leadership and liquidity role can diverge; do not collapse them into a single ranking merely because one stock is prominent.

### No empty hedge endings
When evidence is sufficient, state the present judgment directly and connect it to the stock/company: what is already confirmed, what is still only expected, which stock is currently stronger/weaker/ahead/behind on the relevant dimensions, and why.

Avoid empty endings such as “接下来还要看A、再看B”, “后续需要继续观察”, “能否走出来还要看市场”, or equivalent language that merely postpones judgment. Such wording is acceptable only when the evidence genuinely cannot support a stronger conclusion. In that case, name the **specific unresolved variable**, why it is unresolved, the concrete verification trigger/threshold, and how each possible outcome would change the stock judgment. Uncertainty must be informative, not evasive.

Do not turn this rule into direct trading instructions. The goal is a clear analytical state judgment, not imperatives about buying/selling/position size.

## Fact / inference / market layer
Keep four layers legible in the prose and editing logic:
- confirmed facts;
- industrial/economic inference built from those facts;
- expectations currently being traded by the market;
- unverified rumor or hypothesis.

Industry logic answers who may benefit and how profit transmits. Market logic answers whom the market is choosing, which name carries liquidity and which names are dropping out. They may corroborate one another but cannot impersonate one another. Market/fund-flow material belongs in the article when it explains the topic.

## Ending and falsification
Do not force a universal “next stage / what to watch next / summary” ending. Close where the topic naturally closes: return to the opening contradiction, the decisive company difference, the present stock judgment, a policy/price/order/technology validation point, or a live disagreement.

If the topic is recommendation/comparison-oriented and the evidence is adequate, the ending should leave the reader with a concrete current-state conclusion rather than a generic watchlist. Preserve falsification awareness, but it need not be a dedicated section and must not be used as an excuse to avoid a supported judgment.

## Risk section
The writer returns a separate `risk_disclaimer` field for each formal article. Do not place a risk/disclaimer H1 inside article blocks. Deterministic delivery appends the final section so it cannot be omitted or duplicated by formatting drift.

## Style
Load `references/style.md` for anti-AI, individuality, backstage/prompt-leakage, judgment-specificity and extreme-language rules. Style must never override evidence accuracy.

## Editorial judge
Judge title/opening/structure separately from the writer. Use PASS/REVISE/FAIL with concrete evidence. Revision feedback identifies the first point where reasoning, transition, information density, reader motivation, H1 continuation promise, stock-judgment specificity, mother-to-derivative consistency, acceptance-contract fidelity or evidence-bounded style breaks.
