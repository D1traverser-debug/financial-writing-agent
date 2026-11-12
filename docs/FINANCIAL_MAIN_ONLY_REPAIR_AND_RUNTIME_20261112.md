# Financial Writing — 2026-11-12 main-only repair contract and truth boundary

**Repository owner:** `D1traverser-debug/financial-writing-agent` ONLY. No modification, bridge, PR, runtime invocation or Host dependency involving CAOS. **Delivery target:** one consolidated Financial `main`, not a stack of unmerged candidate branches.

## 1. Exact operational graph

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`

The only article owner remains `workspaces/articles/<task_id>/STATE.json`. Material state changes use `financial_writing_agent.standalone_runtime.admit_article_action`, actual provider SHA CAS, authenticated user permission and second readback. Rejected actions must not mutate this authority. **Business PASS does not follow from wheel install, source hashes, 8 self-scored gates or Word rendering.**

The live article `cross-border-ecommerce-20261016-v3` remains at `RESEARCH` until genuine source and current analysis evidence is generated and admitted. Its mandatory four Word outputs remain undelivered. Do not use archival v2 notes, negative cases or CI synthetic portfolio as current publication.

## 2. RESEARCH evidence contract

- Every new current-research advance through the Financial action port needs a 15-module PrivateResearchBrief v1.1 and `source_snapshot_reader` callback that **actually retrieves every reference** from external provider(s). Input: exact reference string. Output: `text` (at least 20 characters), `sha256` of the UTF-8 body, `retrieved_at` ISO-8601, `source_family` (non-empty). The current brief as-of date and snapshot retrieval must fall within seven days of actual verification, and two materially distinct source families must be observed. Archive-as-current, unread citations and fake provider digests fail closed.
- **This verifies readback, not the finance claim**. A source can be wrong or selectively quoted; fact integrity remains `NOT_VERIFIED` unless independently reviewed and checked against primary issuer/regulator records and time/metric context.
- For the v3 `full_universe_research_pool` requirement, the source artifact for `RESEARCH` must be structured `ResearchPackage` JSON, and the reader must retrieve exact bytes with the Git blob SHA. A packaged historical baseline requires all 174 originally retained **ticker IDs**; ticker duplicates, omitted names and incorrect issuer display identity block advancement. This is a **2026-10-16 frozen retained pool**. It is not a guarantee that the market universe is complete on the later publishing date.
- Requirement satisfaction evidence must refer to an actually read source snapshot or exact persisted RESEARCH artifact, not a self-asserted `SATISFIED` string with an arbitrary `audit-example://` reference. The v3 full-retained pool exception also binds the Deep article at publication scope.
- **Conservative text conflict redlines** prevent direct growth/decline inversion, period mismatch, metric direction reversal and equal-number/different-unit errors. This is *negative contradiction detection*, not general entailment. Derived arithmetic, currency transformations, claims without primary support and causal reasoning require explicit additional review.

## 3. Independent editorial proof

- Internal `CHAT_SELF_REVIEW/PASS` remains labelled self-review. It cannot certify `EDITORIAL_ACCEPTED`, general authorial quality or reader success.
- `PublicationFitness` now allows structured `INDEPENDENT_EXECUTOR` provenance only with different reviewer and author identities, actual review execution reference, reviewed **draft SHA-256** and provider attestation SHA-256. These are necessary but **not sufficient** for acceptance.
- At the Financial action port, `independent_editorial_verifier` must be a trusted externally authenticated provider callback. The current `DRAFT` artifact is fetched by `artifact_reader`, its Git SHA and content SHA-256 are checked, and the external actor identity/execution ref/provider attestation must exactly match. If no verified callback or the review is of a stale draft, the claimed independent review is **rejected**. Mock callbacks used in CI are not proof of an installed independent reviewer.
- Real reader and editorial acceptance must be collected from a genuinely different actor/system against a frozen candidate. No same-model fabricated reviewer identity.

## 4. Word product and visible-delivery contract

- Four product types must be real: `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX`, `AUDIT_DOCX`. A PrivateResearchBrief may additionally require a private research Word.
- The canonical builder records actual content SHA; `render_word_and_review_pages` produces PDF and actual PNG pages and a signed per-page receipt. Generic Word products can now be bound to this inspection; a legitimate article retains source-to-paragraph requirements separately.
- `build_visible_delivery_receipt` for a current writing-kernel article now requires `resource_binary_reader(resource_ref)` to return the **actual DOCX bytes**. It verifies the SHA-256, ZIP structure, expected Word XML and ZIP integrity, as well as the signed per-page render receipt. A hash string or `lambda True` resource ack does not substitute for real binary readback.
- CI `scripts/four_word_product_render_smoke.py` builds/opens/renders/validates all four Word kinds using plainly **synthetic claims**. It tests only the mechanical product chain and must never be published or described as a source-verified user article.

## 5. Independent acceptance and scope of remaining work

- Engineering: full tests, isolated wheel, source inventory, 15-module readback negative cases, ticker baseline, claim contradictions, independent editorial reviewer API and all four real rendered Word kinds must pass at exact candidate SHA *and* merged main SHA.
- Business: a source-verified v3 174-ticker current research package, two authored Deep/Broad products, a real platform interaction pack, audit Word, independent editor review and user-accessible download links are required separately.
- Activation: a native authenticated ChatGPT/Work Financial-only connection is **not verified by Python code or SKILL.md existing**. It requires a real user-scoped connector to be connected and used. No CAOS dependency is necessary.
- Reader quality: `GENERAL_EDITORIAL_QUALITY` and `PERSONALIZED_WRITING_DNA` remain `NOT_READY` pending real source-bound independent held-out/editor-reader evidence. CI success **cannot** change these states.

## 6. Root-cause repair and falsification

- **Rejected as sufficient:** prompt inflation, adding more AI-style word bans, blind rewording of older v2, a second duplicate business state, reintroducing CAOS, or declaring Word hashes to be fact-checks.
- **Selected:** minimal Financial-owned enforcement at the real admission and visible-delivery boundaries; old explicit user intent retained; dated historical market baseline used as a *floor* with explicit source-time warning.
- **Negative tests** cover stale research, unread/fake citations, 3-of-174 false completeness, code/name mismatch, wrong unit/direction/period, self-attested independent review, stale reviewed drafts, and missing/false Word binary/page receipts.
- **Safety constraint:** no unverified market numbers or private user materials may be committed publicly. Never mutate the current live article state to fake stage progress.
