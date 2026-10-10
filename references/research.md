# Research module

## Ownership
Research owns **evidence breadth, source boundaries, company/concept coverage, counterevidence and the decision whether market-price explanation is materially required**. It does not decide article prose, headline packaging or Word formatting.

The research base must be materially broader than either published version so editorial choices are not forced by missing evidence.

## Cognition before expression
Before structuring an article, recover and/or build the topic cognition map. When durable knowledge is accessible, retrieve relevant EventBase/StockBase/topic knowledge first, then reverify current or material claims.

Cover what is material to the topic:
- catalyst/event chronology and what actually changed;
- concept, subtheme and adjacent/competing concept map;
- industry chain and economic transmission path;
- relevant A-share company universe rather than a few familiar names;
- company fundamentals, business stage and economic exposure;
- sensitivity dimensions such as orders, price, volume, capacity, cost, revenue, margin, cash flow, valuation/expectation gap and realization timing;
- negative evidence, stale/conflicting facts and unresolved gaps;
- current market structure only when it is material to the question being written.

A company list is part of normal financial research. It does **not** automatically mean the article needs short-term price-formation analysis.

## Coverage and stop condition
Run at least two materially different research sweeps using different source/query angles. Record `ResearchPackage.coverage` with concept/company/source coverage, exclusions, whether search saturated or remains bounded with gaps, material new items from the last sweep and the stop reason.

A late sweep that still finds a material concept, company class, contradictory fact or materially different explanation is evidence to continue or explicitly preserve the gap. “全面” must be auditable rather than asserted by intuition.

## Required research reasoning
- Establish the event, chronology and what changed relative to prior expectations.
- Map the economically relevant transmission chain.
- Build the relevant company universe and classify direct earnings/business exposure, economic linkage, second-order exposure, optionality, narrative-only association or uncertainty.
- Compare **sensitivity**, not merely concept membership.
- Record important counterexamples and `why_this / why_not` where comparison is material.
- Separate industrial beneficiary, earnings beneficiary and market role instead of assuming they coincide.
- Keep title/opening/core-conclusion facts on a stronger evidence standard than background material.

## Explicit Market Explanation scope
Every `ResearchPackage` declares:
- `market_explanation_scope = REQUIRED` or `NOT_MATERIAL`;
- `market_explanation_scope_reason` explaining the decision.

Set `REQUIRED` when the task materially asks or implies a cross-sectional **price-formation / market-selection** question, for example:
- why one stock/subtheme moved first or more strongly than economically related peers;
- limit-up/leadership/身位/continuation or reversal;
- whether observed price action reflects information diffusion, attention, order flow, liquidity, positioning, price-limit mechanics or another competing mechanism;
- an article conclusion that depends on explaining market selection rather than only economic benefit.

Set `NOT_MATERIAL` when companies are being compared only for industry exposure, fundamentals, earnings realization, policy transmission or similar economic questions and the article does not make a material claim about why prices selected one name over another.

**A non-empty company universe alone is not an activation trigger.** Do not force short-term market language into a pure industry, earnings or company-comparison article.

When scope is `REQUIRED`, load `market_explanation.md` and provide the full multi-hypothesis map. When scope is `NOT_MATERIAL`, do not submit a market-explanation map.

## Market Explanation research when REQUIRED
The map must cover, as material:
- economic-benefit dimensions;
- cross-sectional market-selection dimensions;
- at least two competing/alternative mechanisms;
- `why_this / why_not` evidence;
- continuation conditions and exhaustion/reversal conditions;
- unresolved questions where identification is weak.

Every non-`UNRESOLVED` hypothesis requires task-specific evidence references. A limit-up, strong return, turnover spike, concept label or fund-flow proxy is an observed fact, not proof of its own cause.

## Mode handoff
Research does not pre-delete material branches for editorial convenience.

For `FINANCE_DEEP`, hand off every material branch that could change financial judgment as a candidate completeness obligation. If Market Explanation is `REQUIRED`, include material economic-benefit differences, competing market-selection mechanisms, continuation/reversal conditions and falsification boundaries.

For `FINANCE_BROAD`, editorial may later select one to three central information gaps, but research still starts from the broader evidence base.

## Durable knowledge discipline
Persistent knowledge is a prior, not a verdict. Record references and recency, preserve conflicts, and never let an old concept/stock label override current business facts.

Stable company/business relationships may become reusable knowledge candidates. Fast-changing price action, positioning, attention, crowding, 封单/订单簿 and market role observations are timestamped ephemeral evidence rather than timeless company identity.

## Evidence ledger
Maintain claim, source, date when available, evidence type, confidence, whether the claim is safe for title/H1/core-conclusion use, and useful notes/boundaries.

If evidence remains unresolved, downgrade or remove the claim. Do not bridge missing evidence with confident prose.

## Exit gate
RESEARCH is ready for independent audit only when:
- the main thesis has an evidence chain;
- relevant concepts/company classes and material counterevidence are represented;
- unresolved gaps are explicit;
- the stop condition is auditable;
- Market Explanation scope has been explicitly justified;
- and, when scope is `REQUIRED`, the market-explanation map is strong enough to discuss economic benefit and market selection without hindsight storytelling.
