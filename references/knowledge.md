# Shared cognition and knowledge layer

## Purpose
The long-term goal is one reusable cognition layer shared by writing, future stock-picking and future post-close review agents. The point is not merely archival writeback after an article; every workflow should begin with broader/deeper verified understanding before it makes a selective decision or writes selectively.

## What the shared layer should represent
- Event/catalyst records and chronology.
- Concept definitions, overlaps and competing narratives.
- Industry-chain nodes and causal/transmission relationships.
- Listed-company business mappings and fundamental evidence.
- Company role history: industrial beneficiary, earnings beneficiary, sentiment leader, liquidity carrier/中军, follow-up/补涨,卡位/arbitrage roles when observed.
- Verification/falsification conditions and unresolved questions.
- Source-quality notes and stale/conflicting claims.

## Stable vs ephemeral
Promote stable business/industry relationships cautiously. Timestamp ephemeral market-state observations such as price action,身位,抢筹,封单/订单簿 strength, intraday leadership or crowding; they are evidence for a dated market state, not permanent company identity.

## Read-before-research choreography
The runtime must start first. Then, when a connected knowledge store exists, the ChatGPT orchestrator uses the actual Notion/Drive/other connector to query relevant EventBase/StockBase/topic knowledge before open-web expansion. Record the returned references with `record_knowledge_context`. Treat retrieved knowledge as hypotheses/context and reverify anything current, material or contested.

The standalone Python runtime intentionally does **not** claim that it can directly authenticate to the user's Notion/Drive connectors. The MCP record is a receipt/boundary between connector-side retrieval and runtime state.

## Writeback choreography
Research emits `knowledge_writeback_candidates`. Before final audit, the orchestrator writes back only reusable, evidence-bounded knowledge through the connected store when available, avoiding duplicates and preserving source/date/confidence. Record resulting page/file/item references with `record_knowledge_writeback(status="PASS")`. If there is no connected destination or nothing reusable, record `N_A` with a reason. The runtime keeps this gate `NOT_RUN` until that explicit decision is recorded.

Article-specific rhetoric, headline wording and temporary stylistic choices are not knowledge-base facts. Contradictions are recorded rather than silently overwritten.

## Current implementation boundary
Writing now has an explicit connector/runtime boundary and reusable candidate/receipt contract. Stock-picking/review agents still do not share one executable store, so never claim cross-agent synchronization until those agents are implemented against the same layer.
