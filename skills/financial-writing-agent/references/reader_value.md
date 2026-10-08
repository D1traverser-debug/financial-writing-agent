# Reader value, retention and commercial-quality contract

## Purpose
This module owns the reader-value and commercial-quality layer of a publishable financial article. It does not replace research, editorial, style, platform or audit rules. It answers one narrower question: **after the article is factually correct, what makes it worth a reader's click, attention, completion, trust and return visit?**

The optimization target is not raw click-through and not maximum length. Treat durable publication value as a chain:

`truthful acquisition → immediate information scent → sustained value density → useful perspective/judgment → completion → trust/repeat value`

Account-specific monetization, comments, follows, search traffic or downstream ad inventory may be legitimate business outcomes, but only when current platform/account evidence supports them. They never authorize misleading hooks, delayed payoff, padded length, false certainty or weaker compliance.

## Evidence basis and boundary
This module is informed by current/recent external evidence but does not turn those sources into universal platform laws:
- Reuters Institute Digital News Report 2024: across 47 markets, audiences value not only updates but education and perspective; the gap is especially large for perspective/understanding.
- Nielsen Norman Group, 2025, "Product-Specific GenAI Needs to Write for the Web": generative-AI content commonly becomes too long, hard to scan, conclusion-late and jargon-heavy; concise, scannable, inverted-pyramid and approachable writing reduces reader effort.
- Toutiao Creator Help Center, recommendation-mechanism guidance updated 2025: content is recommended in batches and later distribution depends on user/content response; title/cover deception and false content can trigger review/recommendation stops. Do not invent unpublished metric weights or thresholds.
- Xueqiu community-rule update, 2025: relevant, professional, thoughtful/logical/substantive and original content is explicitly preferred; rumors, illegal stock-touting behavior and misleading AI use are disfavored.
- Google people-first content guidance is used only as a general quality heuristic: useful, original, trustworthy, expert content should add substantial value rather than merely rewrite other sources. It is not treated as a ranking rule for Chinese content platforms.

External mechanisms change. Platform-specific claims and post-publication performance learning remain owned by `platforms.md`; durable storage/writeback boundaries remain owned by `knowledge.md`.

## Reader-value contract before structure
Before selecting structure, make the existing TopicDNA and editorial fields answer these questions explicitly in working reasoning:
- **Target reader:** who is this version for, and what baseline knowledge can reasonably be assumed?
- **Primary reader need:** is the reader mainly trying to get updated, understand a mechanism, gain perspective, compare alternatives, or reach an evidence-bounded judgment? Do not force a fixed taxonomy when another need fits better.
- **Reader starting error/question:** what would the target reader likely misunderstand, not know, or be unable to rank before reading?
- **Non-obvious delta:** what will this article add beyond the obvious headline, source summary or generic sector commentary?
- **Decision/understanding delta:** what concrete belief, comparison, priority or uncertainty should change after reading?
- **Trust reason:** what evidence, counterevidence, definition discipline or explicit boundary makes the conclusion more trustworthy than a hot take?

Do not add new parallel schema when existing fields can carry the contract. Use TopicDNA's `likely_reader_misjudgment`, `finance_wide_question`, contradictions/comparison dimensions, mode `side_focus_statement`, headline `finance_relevance/primary_gap/opening_payoff`, and H1 `reader_gap/payoff_requirement` to encode the reader-value chain.

A structure is weak when it is merely complete from the author's perspective but gives the reader no clear information gain.

## Information scent and first-screen payoff
The title creates a promise; the first screen must show the reader where the value is.

For formal articles:
- the first 1–3 sentences should identify the consequential change, contradiction or judgment quickly enough that a reader can decide whether the article is worth continuing;
- do not spend the opening on chronology/background that can be moved below the first payoff;
- do not hide the article's main answer merely to manufacture suspense;
- curiosity is useful only when the unresolved gap is real and the article can pay it off with evidence;
- every H1 should expose its directional job early rather than require several paragraphs before the reader learns why the section matters.

For FINANCE_BROAD, the entry cost must be lower still. The opening should normally deliver one meaningful fact/judgment before asking the reader to process technical background.

## Paragraph-level value density and scan path
Headings and bold anchors are necessary but not sufficient. A reader often samples the first sentence of a paragraph or scans highlighted anchors before deciding whether to read closely.

Semantic style/audit should therefore test:
- the first sentence of a material paragraph signals the paragraph's real job when feasible;
- important conclusions/numbers/comparisons are not routinely buried at paragraph ends;
- one paragraph does not carry several unrelated ideas merely because the writer wants fewer paragraph breaks;
- consecutive paragraphs form a real progression rather than interchangeable research notes;
- title + lead + headings + bold anchors + paragraph openings reconstruct a coherent scan path;
- jargon is used when it compresses expert meaning, not when it merely signals sophistication; unfamiliar terms should be explained by consequence/context rather than textbook definition dumps.

This is a semantic standard, not a fixed sentence-length or paragraph-length formula. Do not create choppy pseudo-web prose just to satisfy scanability.

## Originality and professional value
Professional depth is not measured by how many facts were collected. Publication value requires synthesis.

A strong article should contribute at least one material value layer beyond source restatement, such as:
- a non-obvious causal link;
- a definition/period/denominator correction that changes interpretation;
- a company divergence or realization-stage comparison;
- a `why_this / why_not` elimination result;
- a market-vs-fundamental mismatch;
- counterevidence that narrows a popular thesis;
- a useful perspective that connects several verified facts into a new, falsifiable judgment.

Do not manufacture novelty. If the evidence only supports a straightforward update, say so cleanly rather than inventing a contrarian angle.

For financial content, trust compounds commercially. Unsupported novelty, fake precision and exaggerated certainty may increase a single click while destroying repeat value. Prefer a smaller, defensible insight over a dramatic but weakly supported claim.

## Commercial value without quality arbitrage
Treat commercial value as **reader value that survives contact with business goals**.

When a current account/platform objective is available, identify the relevant downstream outcome (for example completion, comments, follow, search discovery or monetization opportunity) and optimize the article's packaging for that outcome without changing the evidence boundary.

Rules:
- acquisition cannot be optimized independently of opening payoff;
- completion cannot be optimized by deleting information that changes the conclusion;
- interaction prompts must ask for a specific, genuine discussion when useful, not manufacture controversy for comments;
- search/keyphrase considerations may improve discoverability but may not distort title meaning or fill prose with repeated keywords;
- a business objective does not turn one observed platform metric into a universal algorithm rule;
- repeat trust, bookmark/share value and author credibility are commercial assets, not soft extras.

## Deep vs Broad reader value
### FINANCE_DEEP
Deep earns attention through explanatory and comparative depth. It should help the reader reconstruct **why** the conclusion follows, see meaningful alternatives/counterevidence and understand what would falsify the thesis. Its commercial advantage is authority and repeat trust, not maximum word count.

### FINANCE_BROAD
Broad earns attention through fast relevance and low reader effort. It should retain the smallest set of facts, mechanism, company comparison and judgment needed to create a real information gain. Each paragraph competes with completion; background that does not change the reader's understanding should be removed or compressed.

Broad is defective when it is merely shorter. It must also be easier to enter, easier to scan and clearer about why the topic matters outside the sector.

## Final semantic audit mapping
Do not create a second final-evidence vocabulary. Prove reader value through existing keys:
- `<MODE>.hook_quality`: target reader, specific stake, truthful information gap and why the hook is worth a click;
- `<MODE>.opening_first_three_sentences` + `<MODE>.opening_payoff`: immediate information scent and first-screen value delivery;
- `<MODE>.H1_<N>.promise_payoff`: section-specific reader gap and concrete information gain;
- `<MODE>.reasoning_continuity`: paragraph/section progression, front-loading, jargon burden and whether the scan path preserves the causal chain;
- `<MODE>.bold_scan_skeleton`: whether headings/bold anchors expose the central information skeleton;
- `<MODE>.side_focus` / `<MODE>.company_selection_basis`: non-obvious editorial delta and company-comparison value;
- `DUAL.deep_master_quality`: whether Deep adds real explanatory/comparative authority beyond source restatement;
- `DUAL.broad_hook_strength`: whether Broad materially lowers entry cost while preserving information gain and trust.

A final audit that proves factual correctness but cannot explain **what the reader learns that was not obvious before reading** should revise EDITORIAL/DRAFT rather than PASS.

## Post-publication learning handoff
This module does not own the storage schema or promotion policy for article-performance experience. When real platform/account performance is available, hand it to the structured `ArticleExperienceSample` discipline in `platforms.md`; route durable storage/writeback through `knowledge.md` and maintenance governance.

Reader-value interpretation contributes the hypothesis being tested—for example whether a lower-friction opening, stronger perspective delta or tighter Broad compression improved the intended outcome—but it may not invent missing metrics or promote one successful/failed article into a causal rule.

## Failure patterns this module should catch
Revise when any of these occur:
- headline promises a large payoff but opening starts with generic background;
- article is accurate but mostly restates source material without a synthesis delta;
- Deep contains extensive information that does not change understanding/judgment;
- Broad is shorter but still jargon-heavy or slow to reveal relevance;
- important comparison appears only after several generic paragraphs;
- paragraphs are individually plausible but permutable because the logic does not progress;
- business/monetization language causes clickbait, manufactured controversy or overclaiming;
- a single performance sample is promoted as an algorithm law;
- a reader comment is treated as behavioral evidence for the whole audience.
