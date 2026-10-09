# Research module

## Goal
Research broadly/deeply enough that neither article mode is constrained by research omission. The agent should know substantially more than the traffic-oriented version contains, while FINANCE_DEEP must later express every material branch that could change the financial judgment.

For stock/theme-related topics, “全面” now includes **market-explanation completeness**: not only which companies are related, but why economic benefit differs, why market selection differs from economic benefit, what mechanisms could explain price leadership, and what evidence could support continuation versus temporary price pressure/reversal.

Load `references/market_explanation.md` whenever the task materially discusses A-share companies, themes, price reactions, limit-ups, leadership or continuation.

## Cognition before expression
Before deciding article structure, recover and/or build a market cognition map for the topic. When available, search durable StockBase/EventBase/knowledge assets and accepted prior research first, then verify time-sensitive claims against current sources.

The cognition map should cover what is material to the topic:
- catalyst/event chronology and what actually changed;
- concept map and adjacent/competing concepts;
- industry chain and economic transmission path;
- relevant A-share universe rather than a few familiar names;
- company fundamentals and business-stage differences;
- market-selection logic and `why_this / why_not`;
- when relevant, short-term market structure such as leader, liquidity carrier, follow-up/position roles, crowding, seal/order-book strength and related signals;
- when companies/price action are central, the separate **economic-benefit** and **market-selection** explanations required by `market_explanation.md`.

This is the bounded evidence base from which mode-specific writing proceeds.

## Coverage and stop condition
“全面” must be auditable rather than infinite. Run at least two independent research sweeps using materially different query/source angles. Record `ResearchPackage.coverage` with concept/company/source coverage, exclusions, whether search saturated or remains bounded with gaps, material new items found on the last sweep and the reason research stopped.

A late sweep that still finds material concepts/companies or a materially different explanation of market selection is evidence to continue or explicitly mark the remaining gap. Never declare “all” by intuition.

## Required reasoning coverage
- Establish event, chronology, policy/industry/company facts and what changed.
- Map the relevant industry chain and economically important transmission path.
- Build the relevant A-share universe for the topic.
- For each material company/class, verify business relevance, business stage, customers/orders/revenue/profit/price/capacity when relevant.
- Distinguish direct earnings/business exposure, economic linkage, second-order exposure, optionality and narrative-only association.
- Compare sensitivity, not merely concept membership: exposure purity, revenue/profit share, earnings elasticity, capacity/order visibility, timing, valuation/expectation gap and other topic-specific dimensions.
- Record negative evidence, counterexamples, stale facts and unresolved gaps.
- When discussing market selection, answer both `why_this` and `why_not`.
- Separate industrial beneficiary, earnings beneficiary, sentiment leader, liquidity carrier and other market roles instead of assuming they coincide.
- Where price leadership/limit-up/continuation is material, consider multiple price-formation mechanisms and grade them using the causal-confidence ladder in `market_explanation.md`.
- Explicitly investigate both persistence and exhaustion/reversal evidence; a strong move is not itself evidence that the underlying explanation is correct.

## Market-explanation activation rule
If `ResearchPackage.universe` is non-empty, the research package must include `market_explanation`.

That map must contain:
- concept/subtheme/economic-link coverage;
- economic-benefit comparison dimensions;
- cross-sectional market-selection dimensions;
- at least two competing or alternative explanation hypotheses;
- `why_not` evidence;
- continuation conditions;
- reversal/exhaustion conditions;
- unresolved questions when identification is weak.

Non-`UNRESOLVED` hypotheses require task-specific evidence references. The map is not permission to fabricate causality; it is a structure for making uncertainty explicit.

## Mode handoff
Research does not pre-delete material branches for editorial convenience.

For `FINANCE_DEEP`, the editorial handoff must identify **completeness obligations** covering every material branch in the bounded research universe. When market-explanation mode is active, those obligations must also cover material economic-benefit differences, market-selection mechanisms, competing explanations, continuation/reversal conditions and falsification boundaries.

Low-materiality detail and repetition can be compressed, but material facts/branches cannot be silently dropped.

For `FINANCE_BROAD`, editorial may choose one to three central contradictions/information gaps and compress non-essential branches, provided retained claims remain fully supported and any retained market explanation keeps its evidence grade/counterevidence.

## Durable knowledge discipline
Persistent knowledge is a prior, not a verdict. For every reused knowledge item record its reference and recency; identify conflicts with new evidence. Never allow an old stock/concept label to override current business facts or current market structure.

Research output should identify reusable knowledge candidates: stable company/business mappings, industry-chain relationships, recurring concept definitions, source-quality notes and unresolved questions. Fast-changing price action, positioning, order flow and attention signals should be timestamped/treated as ephemeral rather than promoted as timeless knowledge.

## Evidence discipline
Maintain an evidence ledger with claim, source, date, evidence type, confidence and whether the claim is safe for title/H1/core-conclusion use.

Facts used in headline, opening, H1 or central conclusion require stronger verification than background facts. If evidence remains unresolved, downgrade/remove the claim; do not bridge the gap with confident prose.

For market explanations, distinguish:
- directly verified facts;
- supported mechanisms;
- plausible interpretations;
- unresolved competing explanations.

Do not infer a unique cause of a stock move merely from co-movement, concept membership, fund-flow proxies, a limit-up, a leaderboard position or subsequent continuation.

## Scope
Research is global **within the current topic**. It may use market-wide knowledge, but does not rerun unrelated ranking unless that competition is needed to explain the article.

## Exit gate
RESEARCH passes only when the main thesis has an evidence chain, relevant company universe and concept/industry context have been considered, important counterevidence is represented, prior-knowledge conflicts are bounded, unresolved gaps are explicit, and `ResearchCoverage` explains why breadth is sufficient.

For stock/theme articles, exit additionally requires a market-explanation map strong enough for FINANCE_DEEP to explain both economic exposure and cross-sectional market selection without hindsight storytelling.