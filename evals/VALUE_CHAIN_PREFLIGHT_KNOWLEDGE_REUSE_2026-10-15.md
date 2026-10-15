# Value-chain preflight and knowledge reuse — evolution evaluation

Date: 2026-10-15
Owner: `DOMAIN:financial_writing`
Trigger: user correction during cross-border e-commerce topic research.

## Symptom
Research selected a likely article main line (low-value parcel economics shifting toward overseas warehousing/local fulfilment/branding/compliance) before first completing an explicit whole-value-chain cognition map.

## User consequence
The selected angle could be locally plausible while still missing an economically material upstream/downstream/enabling branch. The user also identified a second-order risk: valuable industry/company cognition learned during one article could be relearned from zero or forgotten in later work.

## Micro diagnosis
`references/research.md` already required material value-chain classes for company/theme universe coverage, but the obligation was coupled too closely to company recall and did not state an unambiguous **pre-thesis** ordering constraint. `references/knowledge.md` described reusable cognition, but repository/connected reuse remained optional enough that a new task could still ignore earned prior cognition.

## Macro alignment
The product goal is not only to write a correct article. Financial Writing should maintain a cumulative, evidence-bounded cognition advantage: know the whole economically relevant map first, select the article angle second, and carry stable knowledge forward without carrying stale facts forward.

## Governing assumption challenged
Rejected assumption: a sufficiently strong early catalyst can safely define the research frame, with value-chain expansion happening later as a completeness check.

Replacement: value-chain coverage is a mandatory **frame-construction step**. Thesis competition begins only after the map is complete or explicitly bounded with gaps.

## External method evidence
Current agent/data architecture guidance supports retrieval-grounded reasoning and graph-like relationship representation for complex multi-hop questions rather than relying only on flat semantic recall. It also distinguishes persistent long-term knowledge, short-term context and durable transactional/audit evidence. This supports keeping reusable structural cognition with provenance while revalidating current facts rather than treating memory as authority.

Relevant external evidence used in this diagnosis:
- Google Cloud, `Core concepts of AI agents`: RAG as grounding; GraphRAG for explicit relationships; hybrid retrieval; persistent storage for long-term knowledge plus separate audit ledgers.
- Google Cloud, `Optimizing RAG retrieval`: retrieval quality requires evaluation because silent retrieval failures damage trust.
- Recent provenance-aware agent-memory research: long-term memories are more reliable when origin/timestamp/evidence pointers remain attached and retrieval targets complete supporting evidence rather than isolated fragments.

## Alternatives considered
1. **Keep current rules and rely on stronger operator discipline.** Rejected: repeats the declaration-to-operation failure class and does not make ordering explicit.
2. **Force every article to publish the entire value chain.** Rejected: confuses research cognition breadth with publication scope; Broad/Deep still need editorial selection.
3. **Make value-chain mapping mandatory before thesis selection, then allow focused publication.** Selected.
4. **Create a new autonomous knowledge controller/store immediately.** Rejected for this repair: would create unnecessary architecture/authority surface. Existing article artifacts and connected knowledge can first serve as provenanced recall inputs.
5. **Reuse prior cognition with stability classes + mandatory revalidation triggers.** Selected.

## Candidate repair
- `references/research.md`: hard pre-thesis Value-Chain Coverage Map; late-discovered material classes force thesis re-test; research cannot claim a strongest/main line before coverage.
- `references/knowledge.md`: mandatory recall-before-expansion when relevant prior cognition exists; stable/semi-stable/ephemeral classes; provenance/time/confidence; revalidation and writeback loop; prior knowledge cannot waive current value-chain coverage.
- regression checks: protect the ordering and reuse semantics from silent drift.

## Acceptance targets
- A topic research run cannot legitimately finalize its main angle before the value-chain map is COMPLETE or BOUNDED_WITH_GAPS (or defensibly NOT_APPLICABLE).
- Final publication may remain selective; Research retains the omitted material branches in cognition/evidence.
- Later related research first recalls relevant prior Financial artifacts/connected knowledge, then revalidates current/material claims.
- Reused knowledge never loses provenance, time/confidence or freshness boundary.
- Ephemeral market/policy/financial state never becomes timeless company identity.

## Assurance boundary
This candidate strengthens current GitHub-chat business authority and adds regression protection against semantic drift. It does not claim host-level physical interception of every natural-language research turn. Live article observation remains required to confirm that the new ordering is consistently followed and that knowledge reuse reduces repeated work without introducing stale-fact carryover.
