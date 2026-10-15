# Financial Writing Kernel Rebuild — Replay Evidence

Date: `2026-10-15`
Candidate: `evolution/writing-execution-architecture-20261015`
Assurance: `REPOSITORY_REPLAY + CHAT_SELF_REVIEW`; no independent semantic certification claimed.

## Trigger

A cross-border-ecommerce task passed the historical editorial audit but was rejected as a writing outcome. The rebuild therefore treats the incident as an architecture/admission failure, not merely a request for more prose rules.

## Negative replay — cross-border ecommerce

Historical artifacts:
- `workspaces/articles/cross-border-ecommerce-20261015/stages/RESEARCH.md`
- `workspaces/articles/cross-border-ecommerce-20261015/stages/DRAFT.md`
- `workspaces/articles/cross-border-ecommerce-20261015/reviews/EDITORIAL_AUDIT.md`

Observed replay findings:
1. Historical audit declares `Decision: PASS` and `PASS -> DELIVERY`.
2. The audit is dominated by PASS labels and summary statements; it does not implement the current eight named PublicationFitness gates with bound `location / excerpt / finding / severity` evidence.
3. The research did build a broad value-chain cognition map, but the publication/audit path did not have a first-class StoryBlueprint contract proving how declared material classes were represented, grouped or explicitly adjudicated out.
4. The task dated `2026-10-15` contains a November 1 requirement in a way that can be read as already effective. This is a temporal-boundary example for the new `FACT_INTEGRITY` gate: future effective dates must be described as future until they actually take effect.
5. Because current admission now requires DecisionEnvelope, StoryBlueprint and PublicationFitness evidence, the same historical naked PASS artifact is not sufficient to advance a new 1.0 task.

Replay verdict: `NEGATIVE_CASE_CAUGHT_BY_NEW_ADMISSION`.

## Held-out replay — ice/snow economy

Held-out artifact:
- `workspaces/articles/ice-snow-economy-20261013/publication/FINANCE_DEEP.md`

Why held out:
- different industry and causal structure;
- not part of the cross-border rejection;
- already uses a different narrative engine: three economically distinct ways companies make money (destination traffic, engineering/equipment, brand/consumer).

Observed findings:
1. The article uses explicit numbered H1 progression.
2. Material explanatory sections are grounded in named companies such as 长白山、天府文旅、冰山冷热、雪人集团、三夫户外.
3. A valid `SYSTEM_MAP` StoryBlueprint can represent this article with material classes `destination / equipment / brand`, showing that the contract is not hard-coded to cross-border categories or the `COMPANY_CONFLICT` engine.
4. The rebuild therefore constrains required reader/evidence properties while allowing different topic-specific story geometry.

Held-out verdict: `ARCHITECTURE_GENERALIZES_TO_DIFFERENT_TOPIC_GEOMETRY`.

## What this replay proves — and does not prove

Supported:
- the old self-PASS artifact is not admissible under the current quality-evidence contract;
- current contracts can represent at least two materially different topic/story geometries;
- temporal fact boundaries now have an explicit acceptance gate;
- the rebuild is not merely a phrase blacklist or cross-border-specific template.

Not yet supported:
- independent semantic certification;
- guaranteed reader retention on future live articles;
- zero plagiarism;
- production outcome superiority before live post-promotion observation.

## Promotion implication

Promotion remains conditional on full candidate CI, authority/mirror/version reconciliation, contradiction scan, controlled merge, production reread/checks and subsequent live article observation. The correct post-promotion state is trajectory-verified with live observation still open, not “quality solved forever”.
