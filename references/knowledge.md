# Shared cognition and knowledge layer

## Purpose
The long-term goal is one reusable cognition layer shared by writing, future stock-picking and future post-close review agents. The point is not merely archival writeback after an article; the point is to let every workflow begin with a broader/deeper verified understanding before it makes a selective decision or writes selectively.

## What the shared layer should represent
- Event/catalyst records and chronology.
- Concept definitions, concept overlaps and competing narratives.
- Industry-chain nodes and causal/transmission relationships.
- Listed-company business mappings and fundamental evidence.
- Company role history: industrial beneficiary, earnings beneficiary, sentiment leader, liquidity carrier/中军, follow-up/补涨,卡位/arbitrage roles when observed.
- Verification/falsification conditions and unresolved questions.
- Source-quality notes and stale/conflicting claims.

## Stable vs ephemeral
Promote stable business/industry relationships cautiously. Timestamp ephemeral market-state observations such as price action,身位,抢筹,封单/订单簿 strength, intraday leadership or crowding; they are evidence for a dated market state, not permanent company identity.

## Read-before-research behavior
When a connected knowledge store exists, query relevant EventBase/StockBase/topic knowledge before open-web expansion. Treat retrieved knowledge as hypotheses/context and re-verify anything current, material or contested.

## Writeback behavior
After a task, write back only reusable, evidence-bounded knowledge. Avoid duplicate facts and preserve source/date/confidence. Record contradictions rather than silently overwriting them. Article-specific rhetoric, headline wording and temporary stylistic choices are not knowledge-base facts.

## Current implementation boundary
Until stock-picking/review agents share the same executable store, the Writing Agent may read connected knowledge and emit/write structured reusable candidates, but must not claim cross-agent synchronization that has not been implemented.