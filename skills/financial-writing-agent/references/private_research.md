# Private Research Brief — Mandatory Pre-Publication Research Layer

Status: `CURRENT_CANDIDATE_1.0`
Owner: `DOMAIN:financial_writing`

## Purpose

Every new Financial Writing task must carry a durable `PrivateResearchBrief` through Research before publication planning. The private brief is the full analytical workbench; the article is a selective reader product derived from it.

The brief exists to prevent two recurring failures:
1. a publishable narrative being chosen before the full company/value-chain/market structure is understood;
2. private decision-useful research being lost because it would be too detailed, too tactical or too process-heavy for publication copy.

The brief is not itself a buy/sell instruction. Existing Financial redlines on entry timing, target price, position sizing and covert equivalents remain in force.

## Required modules

Every brief contains every module below. A module is `APPLICABLE` or `NOT_MATERIAL`. `NOT_MATERIAL` requires an explicit reason; it is not a shortcut for omitted research. An applicable module requires evidence refs.

### 1. `company_universe_and_value_chain`

Build the broadest evidence-bounded listed-company universe relevant to the theme/event before selecting favorites. Separate, when material:
- economic-substance universe;
- market/concept-label universe;
- included / excluded / unresolved names;
- value-chain class for every retained material company;
- direct, first-order, second-order, weak and negative exposure.

Do not claim literal internet exhaustiveness. Use coverage state plus auditable saturation/gaps.

### 2. `business_granularity`

For each material company capture the decision-relevant business facts available for the topic, such as:
- revenue/profit or segment contribution;
- product/service and monetization model;
- customers, channels and geography;
- orders, shipments, paid members, transaction volume or other operating realization;
- business stage: scaled, operating/expanding, small-scale realized, trial/expansion, plan/agreement, or label-only;
- benefit mechanism and reversal/adverse variables.

High overseas revenue is not automatically high thematic purity. Export manufacturing, direct cross-border retail, B2B services, logistics, payment and marketing must not be collapsed into one bucket.

### 3. `market_cap_and_liquidity`

When listed-equity market behavior is material, timestamp and record for every short-horizon/material candidate:
- total market capitalization;
- float market capitalization;
- turnover rate;
- traded value/liquidity;
- board regime where relevant.

Private deliverables visually emphasize total and float market cap. Market cap is a market-selection variable, not evidence of business quality.

### 4. `catalyst_strength_and_freshness`

Classify each material catalyst before mapping stocks:
- sudden vs expected;
- official/primary vs rumor/secondary;
- new information vs stale/recycled information;
- expectation vs implementation vs financial realization;
- strength/coverage: systemic multi-link catalyst, focused industry catalyst, verification catalyst, or weak label/old-news catalyst.

A stronger and broader catalyst should trigger research into a wider benefit chain and possible market-role ladder; do not assume every catalyst can support a full theme.

### 5. `benefit_chain_tiering`

Map the catalyst through economics before ranking securities:
`trigger/change -> mechanism -> exposure -> operating/financial expression -> verification/reversal`.

Distinguish:
- directly helped / directly hurt;
- first-order beneficiaries;
- second-order beneficiaries;
- weak/optional exposure;
- companies whose business is real but whose profit transmission is not established.

### 6. `short_horizon_role_map`

When short-horizon A-share behavior is material, assign roles as hypotheses supported by evidence, not labels pasted after the fact:
- pioneer / first price discovery;
- sentiment high / space leader;
- theme leader;
- capacity middle-army / trend leader;
- branch leader;
- assist;
- card-position competitor;
- catch-up;
- follower / weak tag;
- eliminated / failed candidate;
- existing-height theme remapping candidate.

Role semantics:
- a high board is not automatically the theme leader;
- a pioneer may be replaced later;
- a middle-army validates capacity and industry participation rather than board height;
- card-position requires a real competing role/height and observable displacement;
- catch-up normally depends on height/attention already created elsewhere.

Keep `business strongest` separate from `most likely to become a short-horizon limit-up/sentiment core`.

### 7. `market_structure_and_positioning`

When market behavior is material, timestamp the relevant environment:
- sentiment cycle: launch, expansion, divergence, repair, retreat;
- current maximum board height and important height tiers;
- 1->2, 2->3 or other promotion/attrition where available;
- limit-up, broken-board, strong-stock and prior-limit-up pools when available;
- recent stock character: limit-up count, maximum consecutive limits, reason/driver, failed boards, reversal, A-kill or rebound memory;
- whether the theme has isolated boards, branch breadth, a leader, a capacity confirmation and a credible ladder.

Use market structure to explain selection pressure; do not infer business truth from price action.

### 8. `counterfactual_company_comparison`

For every serious candidate set, answer:
**Why would the market/economics select A rather than B under this exact catalyst?**

Compare topic-specific variables such as business purity, realization, scarcity, catalyst fit, market cap, board regime, liquidity, current height, recent stock character, competing themes and negative evidence.

A company list without this counterfactual comparison is not a finished private research brief.

### 9. `negative_and_falsification_pool`

Preserve companies/facts that weaken the preferred story:
- false/weak thematic labels;
- old news repeatedly recycled;
- zero-revenue/planning-only exposure;
- current price move driven by another theme;
- business growth without profit realization;
- high-position or failed-promotion risk;
- policy direction that helps one branch while hurting another.

Rejected or failed candidates remain evidence; do not delete them after a winner is selected.

### 10. `scenario_tree`

Build scenario-dependent role maps before the event happens. Different catalysts should produce different expected winners.

For a broad, high-strength catalyst, test whether a plausible ladder can form:
`pioneer -> theme/space leader -> capacity middle-army -> branch leaders -> assists -> low-position catch-up -> elimination`.

For a narrow catalyst, explicitly resist inventing a broad ladder when only one branch has causal exposure.

### 11. `next_window_validation`

State what observable next-session/next-catalyst evidence would:
- confirm theme formation;
- confirm a leader or branch leader;
- prove real card-position displacement;
- confirm capacity participation;
- distinguish an isolated stock move from sector formation;
- falsify the preferred thesis or role map.

This is a verification plan, not an entry-price instruction.

### 12. `publication_distillation`

The private brief and the published article have different jobs.

Record explicitly:
- the private conclusions that must inform `FINANCE_DEEP`;
- the narrower acquisition/payoff model for `FINANCE_BROAD`;
- material research that should stay private because it is process-heavy, tactical or distracting;
- which company comparisons/causal chains are essential to the article;
- which internal vocabulary (for example exhaustive-universe bookkeeping, scoring tables, ladder mechanics) should not be narrated unless it improves the reader product.

A publication may be selective. The research brief may not silently become selective just because the article is.

## Coverage and freshness

`coverage_state` is `COMPLETE` only when no known material research gap remains under the declared scope. `BOUNDED_WITH_GAPS` requires explicit unresolved gaps.

Time-sensitive fields — market cap, float cap, turnover, board height, promotion rates, policy state, orders and current business data — must carry an `as_of` boundary and be refreshed when material to the next decision.

## Source/tool priority

Prefer free or already-available authoritative sources/tools when they can supply the required evidence reliably. Use paid/external crawling only when it materially improves coverage or a needed source cannot be obtained through the free/primary path. Tool cost never justifies inventing missing evidence.

## Admission boundary

For marker-enabled new tasks, `financial_writing_agent.current_admission` persists the validated brief in `quality_evidence.private_research_brief` and binds its digest in the RESEARCH execution receipt. A side file or chat statement is not equivalent.

Revision back to RESEARCH invalidates the admitted brief together with downstream research quality evidence. A materially changed catalyst, company universe, market structure or new counterexample requires the affected private-research modules to be refreshed before re-admission.
