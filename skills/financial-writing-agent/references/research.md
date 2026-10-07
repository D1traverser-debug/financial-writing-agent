# Research module

## Goal
Research broadly/deeply enough that editorial compression never becomes research omission. The agent should know substantially more than the final article contains.

## Cognition before selection
Before deciding what the article will emphasize, recover and/or build a market cognition map for the topic. When available, search durable StockBase/EventBase/knowledge assets and accepted prior research first, then verify time-sensitive claims against current sources.

The cognition map should cover what is material to the topic:
- catalyst/event chronology and what actually changed;
- concept map and adjacent/competing concepts;
- industry chain and economic transmission path;
- relevant A-share universe rather than a few familiar names;
- company fundamentals and business-stage differences;
- market-selection logic and `why_this / why_not`;
- when short-term market structure is relevant: leader/龙头, liquidity carrier/中军, follow-up/补涨, position/catch-up/卡位, arbitrage role,身位, crowding/抢筹, seal/order-book strength and related signals.

This cognition is not a requirement to mention every dimension in the article. It is the knowledge base from which selective writing is allowed.

## Coverage and stop condition
“全面” must be auditable rather than infinite. Run at least two independent research sweeps using materially different query/source angles. Record `ResearchPackage.coverage` with concept/company/source coverage, what was excluded, whether the search saturated or remains bounded with gaps, how many material new items appeared on the last sweep, and why research stopped.

A late sweep that still finds material concepts/companies is evidence to continue or explicitly mark the remaining gap; never declare “all” by intuition.

## Required reasoning coverage
- Establish the event, chronology, policy/industry/company facts and what changed.
- Map the relevant industry chain and economically important transmission path.
- Build the relevant A-share universe for the topic.
- For each material company, verify business relevance, business stage, customers/orders/revenue/profit/price/capacity when relevant.
- Distinguish factual exposure from narrative exposure.
- Record negative evidence, counterexamples, stale facts and unresolved gaps.
- When discussing market selection, answer both `why_this` and `why_not`.
- Separate industrial beneficiary, earnings beneficiary, sentiment leader, liquidity carrier and other market roles instead of assuming they coincide.

## Evidence ledger: evidence strength is data, not prose
Every reusable factual claim goes into `EvidenceItem`. At minimum record the claim, source, date/time when material, evidence type, confidence, source group, verification status, allowed wording where required, conflict/notes and whether the item is safe for core use.

`verification_status` has three explicit states:
- `UNRESOLVED`: not safe for headline/opening/H1/core conclusion; downgrade, verify or remove.
- `SINGLE_SOURCE_ATTRIBUTED`: one sufficiently authoritative original source exists but an independent second source does not. It may be used only with explicit `allowed_wording` and correct attribution/uncertainty.
- `INDEPENDENTLY_CROSS_CHECKED`: a second check supports the same proposition at a comparable period/definition and comes from a genuinely independent source group.

Two media rewrites of the same announcement, two tools reading the same page, Drive plus Notion copies of the same original, or multiple articles derived from one research report are not independent checks. `source_group` and `second_check_source_group` make this distinction explicit.

`core_safe=true` is legal only when the evidence is no longer `UNRESOLVED`. It means the claim may be considered for title, lead, H1 or central conclusion; it does not force editorial use.

If only one authoritative primary disclosure exists, use `SINGLE_SOURCE_ATTRIBUTED`, specify the wording boundary, and where useful cross-check calculations/notes inside that source. Never fabricate a second source merely to satisfy a quota.

## Facts requiring stronger verification
All verifiable facts in the final article must be supported. The following deserve extra scrutiny and must never rely on an unresolved evidence item:
- facts proposed for headline, independent lead/opening, H1 or bold/core conclusion;
- policy, regulation, licence, approval and legal status;
- financial/statistical comparisons where period, unit, currency, denominator or consolidation scope can change the result;
- order, customer, capacity, cooperation and equity claims where intent/sample/qualification/framework agreement can be confused with supply, production or recognized profit;
- dynamic market/fund-flow claims where date/time/market/float definition matters;
- major technology/person/event claims such as first/only/breakthrough/success/commercialization;
- disputed claims and facts that materially change `why_this / why_not`.

## StockBase and review queue
Persistent knowledge is a prior, not a verdict. For every reused knowledge item record its reference and recency; identify conflicts with new evidence. Never allow an old stock/concept label to override current business facts or current market structure.

Writing remains READ ONLY against StockBase. A stable company/concept/relation correction discovered during writing goes into `ResearchPackage.review_queue` as `StockBasePendingUpdate` with stock code, field/relation, old value if known, proposed value, source, reason, verification time and `PENDING_REVIEW`. Do not mutate StockBase directly.

Fast-changing price action,封单,抢筹,身位 and similar signals should be timestamped/treated as ephemeral rather than promoted as timeless knowledge.

## Failure and fallback receipts
Tool success is not evidence success. When a material research path fails or returns only a snippet/template/empty payload, record a `ResearchFailure` with failed action, reason, retry status, alternative source/tool, impact and whether it was resolved.

Switch sources/tools when possible; do not shrink the required universe or silently remove a verification obligation because one tool failed. A core unresolved gap blocks or weakens the claim. A non-core gap may proceed only with explicit boundary language.

## Knowledge writeback candidates
Research output should identify reusable knowledge candidates after the task: stable company/business mappings, industry-chain relationships, recurring concept definitions, source-quality notes and unresolved questions. These candidates do not authorize writeback by themselves; final writeback follows the connected-store permission boundary and explicit PASS/N_A receipt flow.

## Exit gate
RESEARCH passes only when:
- the main thesis has an evidence chain;
- the relevant company universe and concept/industry context have been considered;
- important counterevidence is represented;
- prior-knowledge conflicts are bounded;
- unresolved gaps are explicit;
- `ResearchCoverage` explains why breadth is sufficient to proceed;
- at least one publishable `core_safe` evidence item exists;
- core-safe labels have auditable verification status rather than unsupported self-certification.
