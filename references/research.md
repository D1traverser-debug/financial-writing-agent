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

For an A-share topic that materially involves listed-company/concept mapping, connected StockBase/EventBase knowledge is relevant by default when it is actually accessible. Retrieve it before open-web expansion and keep StockBase READ ONLY. If the connected knowledge source is unavailable, close the knowledge-context gate explicitly rather than silently pretending the recall step was unnecessary.

## Coverage and stop condition
“全面” must be auditable rather than infinite. Run at least two independent research sweeps using materially different query/source angles. Record `ResearchPackage.coverage` with concept/company/source coverage, what was excluded, whether the search saturated or remains bounded with gaps, how many material new items appeared on the last sweep, and why research stopped.

A late sweep that still finds material concepts/companies is evidence to continue or explicitly mark the remaining gap; never declare “all” by intuition.

Coverage is omission-oriented, not only a review of what was already found. Ask explicitly what material source, concept node, listed-company mapping, counterexample, relationship, fact class or time-sensitive update should exist under the topic but is still absent. For quantity-bearing inputs or universes, reconcile known input/source totals against processed totals when a trustworthy total exists. An unexplained mismatch is a research defect or explicit boundary, never an invisible omission.

## Required reasoning coverage
- Establish the event, chronology, policy/industry/company facts and what changed.
- Map the relevant industry chain and economically important transmission path.
- Build the relevant A-share universe for the topic.
- For each material company, verify business relevance, business stage, customers/orders/revenue/profit/price/capacity when relevant.
- Distinguish factual exposure from narrative exposure.
- Record negative evidence, counterexamples, stale facts and unresolved gaps.
- When discussing market selection, answer both `why_this` and `why_not`.
- Separate industrial beneficiary, earnings beneficiary, sentiment leader, liquidity carrier and other market roles instead of assuming they coincide.
- Keep confirmed fact, evidence-bounded industrial inference, market-traded expectation and unverified rumor distinct; one layer must not silently be rewritten as another.

## Recommendation-oriented stock research depth
When the requested article recommends, compares, ranks or materially selects A-share stocks, the research obligation is **broader than the final written stock list**. Do not start from a few familiar names and then rationalize them.

Before selecting the article's final companies:
- build the material concept/company universe first, including meaningful alternatives and adjacent/competing concept mappings;
- identify one or two topic-specific comparison dimensions that actually decide the current question rather than using a fixed leader/mid-cap/follower template;
- research every material candidate deeply enough to support a relative judgment, not merely a concept-membership label;
- verify, when material, actual business/industry-chain position, customer/order exposure, revenue/profit realization, capacity/price sensitivity, business-stage differences and any other transmission variable that can change the ranking;
- record positive evidence, negative/counterevidence, `why_this`, `why_not`, and the reason a company should rank above/below meaningful alternatives on the chosen dimensions;
- distinguish industrial beneficiary, earnings beneficiary, sentiment leader, liquidity carrier,补涨/卡位/arbitrage roles and other short-term market roles instead of treating them as interchangeable;
- when short-term structure matters, timestamp the relevant role/身位/market signal and keep it inside the declared market-data capability boundary;
- preserve the current evidence-bounded company/stock judgment: what is confirmed, what remains expected, what is narrative-only, and what specific unresolved fact prevents a firmer conclusion.

A final article may omit low-value names, but omission is editorial compression **after** research. The research package must be sufficient to explain why the selected stocks were selected and why material alternatives were not. FINANCE_DEEP should be able to reconstruct that comparison; FINANCE_BROAD may later compress it but must not invent a different ranking.

## Source completion and source hierarchy
Task-provided sources are obligations, not merely hints. Every user-supplied link/PDF/report/attachment that is material to the task must be accounted for before research can honestly be called complete. A search snippet, abstract, generated summary, truncated page, table of contents or tool-success response is not equivalent to reading the relevant source content.

For every material supplied source, preserve its practical completion state in the research/evidence boundary: `FULL` when the relevant original content was actually read; `PARTIAL` when only part was accessible/read and the missing scope is stated; or `UNAVAILABLE` when it could not be read and the fallback path plus impact are stated. Do not silently drop a supplied source because another source was easier to access. If two inputs are copies/rewrites of the same original, record that equivalence rather than treating them as independent evidence.

Prefer evidence in this order when the proposition permits: original regulator/government/exchange material; company filing/official site/earnings-call or original meeting material; original paper/product/technical documentation; reliable structured market data; high-quality secondary reporting. Secondary articles, snippets and summaries are discovery aids or viewpoint comparisons, not automatic factual endpoints.

Drive/long-term knowledge may reuse stable original documents, historical reports, accepted EventBase/IndustryBase/EvidenceCache material and read-only StockBase mappings, but old articles are not current dynamic-fact evidence. Notion is a navigation/index/governance layer unless the retrieved page itself is authoritative original content; a stale summary is not upgraded into a current fact merely because it is easy to retrieve.

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

`TaskContract.effective_time_boundary` is the single upper cutoff for what information the task is allowed to treat as known. The default is the task-creation time; an explicitly supplied historical cutoff may be earlier. Current-source refresh means “latest information effective on or before that boundary”, not “latest information available today regardless of the task cutoff”. No later disclosure, later market move or later platform state may be used to explain an earlier frozen decision boundary.

For mutable facts—orders, capacity, customers, executive roles, cooperation progress, policy status and similar items—refresh the latest effective disclosure **on or before `effective_time_boundary`** for each article rather than inheriting an old cache as current. Price, market cap, daily move, float, market pools and short-term market roles must carry a comparable trading date/time boundary. On a non-trading day, using the latest trading day is acceptable only when it is described as such rather than presented as same-day trading feedback.

## Market-data capability boundary
Market microstructure is an evidence-permission boundary, not a stylistic flourish. `ResearchPackage.market_data_boundary` records the actual market-data capability used for the task: `NONE`, `STANDARD` or `LEVEL2`, the data `as_of`, real source receipts, and whether order-book and/or tick data were actually available.

Standard quotes may support ordinary price/volume/market-cap or other fields the source actually returns. They do **not** authorize invented Level-2 interpretations. Claims about `封单`, order-book/queue depth, `买一/卖一` queue behavior or similar order-book structure require a declared `LEVEL2` boundary with `order_book_available=true`. `逐笔/逐单/tick` claims require declared Level-2 tick capability. `抢筹` or equivalent microstructure inference requires actual order-book or tick evidence. If the capability is unavailable, omit/downgrade the claim and record the limitation; never reverse-engineer Level-2 conclusions from ordinary quote fields.

## StockBase and review queue
Persistent knowledge is a prior, not a verdict. For every reused knowledge item record its reference and recency; identify conflicts with new evidence. Never allow an old stock/concept label to override current business facts or current market structure.

Writing remains READ ONLY against StockBase. A stable company/concept/relation correction discovered during writing goes into `ResearchPackage.review_queue` as `StockBasePendingUpdate` with stock code, field/relation, old value if known, proposed value, source, reason, verification time and `PENDING_REVIEW`. Do not mutate StockBase directly.

Fast-changing price action,封单,抢筹,身位 and similar signals should be timestamped/treated as ephemeral rather than promoted as timeless knowledge.

## Failure and fallback receipts
Tool success is not evidence success. When a material research path fails or returns only a snippet/template/empty payload, record one consolidated `ResearchFailure` per failed action/path with failed action, reason, retry count, alternative source/tool, impact and whether it was resolved.

A temporary same-path failure may receive **at most one justified retry**. A second same-path retry is not allowed by the research contract; move to an independent reliable path or keep the boundary unresolved. Known quota/permission exhaustion receives no blind probe/retry. Duplicate receipts for the same failed action must be consolidated rather than disguising repeated retries as separate failures.

Switch sources/tools when possible; do not shrink the required universe, source-completion obligation or verification obligation because one tool failed. A core unresolved gap blocks or weakens the claim. A non-core gap may proceed only with explicit boundary language. Preserve the failure/fallback receipt so “tool succeeded” can never be confused with “evidence succeeded”.

## Knowledge writeback candidates
Research output should identify reusable knowledge candidates after the task: stable company/business mappings, industry-chain relationships, recurring concept definitions, event chronology/catalyst facts, source-quality notes, reusable evidence and unresolved questions. These candidates do not authorize writeback by themselves; final writeback follows the connected-store permission boundary and explicit PASS/N_A receipt flow.

Article-specific rhetoric, headline wording, temporary emphasis and one-off stylistic choices are not market-knowledge facts. A StockBase correction remains a review-queue item rather than a writing-side direct mutation.

## Exit gate
RESEARCH passes only when:
- the main thesis has an evidence chain;
- material task-provided sources are accounted for, including partial/unavailable boundaries;
- the relevant company universe and concept/industry context have been considered;
- for recommendation-oriented/stock-comparison writing, material company research is deep enough to support explicit relative/current judgments rather than only concept labels;
- omission/count checks do not contain an unexplained material mismatch;
- important counterevidence is represented;
- prior-knowledge conflicts are bounded;
- mutable facts and market-state claims respect the frozen `effective_time_boundary` and carry a comparable explicit time boundary;
- any market-microstructure claim stays inside the declared `market_data_boundary` capability;
- failed-path retry receipts respect the single-retry/fallback boundary;
- unresolved gaps are explicit;
- `ResearchCoverage` explains why breadth is sufficient to proceed;
- at least one publishable `core_safe` evidence item exists;
- core-safe labels have auditable verification status rather than unsupported self-certification.
