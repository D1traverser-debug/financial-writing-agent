# Shared cognition and knowledge layer

## Purpose
The long-term goal is one reusable cognition layer shared by writing, future stock-picking and future post-close review agents. The point is not merely archival writeback after an article; every workflow should begin with broader/deeper verified understanding before it makes a selective decision or writes selectively.

The shared layer stores **learning**, not an old task's unfinished work. A new writing task may inherit durable cognition and validated experience, but it must not inherit a previous task's stage, blocker, selected headline, selected outline, draft, artifact set, pending action, visual package or next-step pointer unless the user explicitly resumes that task.

## What the shared layer should represent
- Event/catalyst records and chronology.
- Concept definitions, overlaps and competing narratives.
- Industry-chain nodes and causal/transmission relationships.
- Listed-company business mappings and fundamental evidence.
- Company role history: industrial beneficiary, earnings beneficiary, sentiment leader, liquidity carrier/中军, follow-up/补涨,卡位/arbitrage roles when observed.
- Verification/falsification conditions and unresolved questions.
- Source-quality notes and stale/conflicting claims.
- Reusable evidence with source/date/definition/confidence boundaries.
- Platform/account experience samples and article-structure fingerprints when they are stored as experience rather than universal rules.

## Knowledge classes and writeback boundaries
When a connected durable store supports these distinctions, route reusable candidates by meaning rather than dumping everything into one generic memory bucket:
- event/catalyst chronology and event-specific facts → EventBase-like knowledge;
- stable industry structure/transmission relationships → IndustryBase-like knowledge;
- reusable factual evidence/source-quality/conflict records → EvidenceCache-like knowledge;
- article TopicDNA, accepted structural fingerprint, title/structure decision rationale, user feedback and **structured `ArticleExperienceSample` records owned by `platforms.md`** → ArticleBase-like knowledge/experience;
- company/concept/relation corrections discovered during writing → StockBase review queue only, never a direct writing-side mutation.

These are semantic target classes, not a claim that the standalone runtime owns connector credentials or that all named stores are already implemented as one executable database.

For article-performance experience, knowledge storage preserves the platform-owned sample as evidence. It does not reinterpret missing metrics, collapse the observation window, discard confounders or silently upgrade `SAMPLE_ONLY` into a durable rule. `0`, missing and unavailable remain distinct. Promotion semantics remain governed by `platforms.md` plus maintenance review.

## Stable vs ephemeral
Promote stable business/industry relationships cautiously. Timestamp ephemeral market-state observations such as price action,身位,抢筹,封单/订单簿 strength, intraday leadership or crowding; they are evidence for a dated market state, not permanent company identity.

Do not promote article-specific rhetoric, a one-off headline phrase, current-task focus, temporary ordering, a single viral/failing result or a current-task blocker into market knowledge. Experience may be retained as an experience sample, but one sample is not a durable rule.

## Read-before-research choreography
The runtime must start first. Then, when a connected knowledge store exists, the ChatGPT orchestrator uses the actual Notion/Drive/other connector to query relevant EventBase/StockBase/topic knowledge before open-web expansion. Record the returned references with `record_knowledge_context`. Treat retrieved knowledge as hypotheses/context and reverify anything current, material or contested.

For A-share company/concept writing, connected StockBase/EventBase is relevant by default when actually accessible. StockBase remains READ ONLY during writing. If unavailable, record the unavailable boundary rather than pretending the knowledge layer was consulted.

When ArticleBase/platform experience is relevant to packaging, retrieve the **current comparable samples/method state**, not merely the most memorable successful article. Preserve whether an input is `SAMPLE_ONLY`, a user-declared objective, a repeated-evidence method or an authoritative-platform mechanism. Do not treat historical performance correlation as a current platform law without re-verification.

The standalone Python runtime intentionally does **not** claim that it can directly authenticate to the user's Notion/Drive connectors. The MCP record is a receipt/boundary between connector-side retrieval and runtime state.

## Writeback choreography
Research emits `knowledge_writeback_candidates`. Before final audit, the orchestrator writes back only reusable, evidence-bounded knowledge through the connected store when available, avoiding duplicates and preserving source/date/confidence. Record resulting page/file/item references with `record_knowledge_writeback(status="PASS")`. If there is no connected destination or nothing reusable, record `N_A` with a reason. The runtime keeps this gate `NOT_RUN` until that explicit decision is recorded.

When post-publication performance is later available, a platform-owned `ArticleExperienceSample` may also be persisted into the appropriate ArticleBase-like experience store with its identity, measurement window, available metrics, baseline/context, confounders, hypothesis, confidence and current promotion status intact. This is a later learning/maintenance action, not something the writing run should fabricate before performance exists.

Article-specific rhetoric, headline wording and temporary stylistic choices are not knowledge-base facts. Contradictions are recorded rather than silently overwritten. A StockBase correction remains in the task's review queue for the authorized review workflow; generic knowledge writeback must not be used to bypass that permission boundary.

## Cold-start contamination rule
On a genuinely new task, durable knowledge may be recalled, but task-local state is not a prior. Do not search recent writing tasks merely to discover something unfinished and continue it automatically. The resume path is activated only by explicit continuation intent or an unambiguous reference to that unfinished task.

This is the operational distinction:
- **inherit:** cognition, evidence, validated source notes, structured platform experience, style lessons, regression/prevention knowledge;
- **do not inherit by default:** task_id, stage, gates, blockers, selected title/outline, draft, artifacts, pending steps, next action or visual state.

## Current implementation boundary
Writing now has an explicit connector/runtime boundary and reusable candidate/receipt contract. The repository does not yet expose an executable automatic ArticleExperienceSample-to-rule promotion workflow, and stock-picking/review agents still do not share one executable store. Never claim automatic causal learning, rule promotion or cross-agent synchronization until those paths are implemented against the same durable layer.
