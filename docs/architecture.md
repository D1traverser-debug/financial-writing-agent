# Financial Writing Agent — Architecture

Version: `1.0.0-candidate`
Date: `2026-10-15`
Status: `CANDIDATE_REBUILD`

## 1. Product boundary

Financial Writing is one domain/business owner under UAOS. UAOS owns common governance, cross-domain authority, parent continuity and the shared cognition/evolution method. Financial Writing owns article identity/state, research semantics, writing architecture, output contracts, domain knowledge/evolution evidence and delivery.

Hard invariants:
- one Financial business owner and one article state authority;
- no parent/child task-id equality requirement;
- historical states/receipts and legacy distribution semantics remain immutable provenance;
- no mandatory live UAOS business proxy for normal Financial work;
- compliance, evidence integrity and owner-controlled mutation remain fail-closed.

## 2. Why the writing kernel changes

The prior system accumulated many useful rules but allowed the same execution context to draft and then certify itself with broad PASS labels. The cross-border-ecommerce rejection showed that rich rules without hard admission/evidence can still produce weak reader retention, incomplete company/value-chain integration, source-shaped phrasing and an audit that says PASS without proving it.

The rebuild therefore separates cognition, decision, story construction and publication fitness while preserving one business state machine.

## 3. Stable lifecycle and focused internal passes

External lifecycle remains:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

Internal work uses `financial_writing_agent/writing_kernel.py`:
`KNOWLEDGE_RECALL -> RESEARCH_DISCOVERY -> RESEARCH_ADVERSARIAL -> THESIS_ADJUDICATION -> STORY_ARCHITECTURE -> DRAFT_GENERATION -> READER_RETENTION_AUDIT -> EDITORIAL_TRIM -> {ORIGINALITY_AUDIT, FACT_INTEGRITY_AUDIT, STYLE_AUDIT} -> FINAL_SYNTHESIS`.

These are focused passes, not independent business controllers. Same-model passes are structured challenge evidence, not independent certification.

## 4. Hosted cognition architecture

UAOS-hosted cognition supplies the problem-response method; Financial keeps business adjudication local.

For ordinary material thesis/business judgments, `DecisionEnvelope` requires:
- evidence beyond user assertion alone;
- challenged assumptions;
- at least two credible alternatives;
- candidate fit/misfit and failure modes;
- counterexamples and rejected paths;
- selected rationale;
- auditable search saturation;
- verification plan and remaining unknowns.

For a detected problem, correction/rejection or architecture/governance change, the UAOS floor additionally requires relevant external method/architecture research, macro/topology alignment and stronger verification proportional to risk. This distinction avoids turning every ordinary article decision into heavyweight architecture research.

Search convergence is bounded rather than pretending to crawl the entire internet: stop only after two consecutive materially different sweeps add no decision-changing candidate, failure mode, counterexample or changed decision. Any later material discovery invalidates saturation.

## 5. Research architecture

Normal thematic/company work follows:
`prior cognition recall -> mandatory value-chain preflight -> company universe -> current evidence -> adversarial/disconfirming search -> saturation -> thesis competition -> Company Decision Map -> Research Audit`.

Thesis selection before value-chain coverage is invalid. Prior knowledge may accelerate mapping but never waive it. Research may be broader than publication; the publication may select only after the broad cognition exists.

## 6. Story construction architecture

`StoryBlueprint` bridges audited cognition to prose. It captures reader job/start state, article promise, central question, author stance, narrative engine, concrete opening anchor, information gap, early/later payoff, numbered section plan, new information per section, company/case anchors, value-chain classes, evidence refs, bridges/open loops, ending payoff and voice evidence.

Story form follows material. Hard anomaly, company conflict, reversal, mystery, system map, consequence chain, case lead and timeline escalation are legal engines. Nut-graf, five-box and hourglass are method knowledge, not universal templates.

`FINANCE_DEEP` is the complete finance/review product: declared material value-chain classes and material companies must be represented or explicitly adjudicated out; material explanatory sections use named company/case grounding when available; H1 uses explicit contiguous Chinese numbering; there is no default word-count ceiling.

`FINANCE_BROAD` is independently rebuilt for acquisition from audited evidence, not shortened Deep.

## 7. Publication fitness architecture

Publication acceptance uses evidence-backed fitness gates rather than unsupported PASS labels. Every current long-form product must supply exactly:
- `FACT_INTEGRITY`
- `RETENTION`
- `COMPANY_GROUNDING`
- `STRUCTURE_NUMBERING`
- `ORIGINALITY`
- `AUTHORIAL_STYLE`
- `COMPLIANCE`
- `PAYOFF`

Every semantic gate records text location, excerpt, finding and severity. MAJOR/CRITICAL findings block PASS; REVISE requires concrete repair actions. Deterministic checks remain tripwires for invariants, not substitutes for semantic reading.

Natural prose is generated from material, stance, story architecture and voice evidence. Generic scaffolding is diagnostic when clustered/unearned, not a phrase blacklist. Sources supply evidence rather than reusable prose; close paraphrase/patchwriting is a revision condition.

## 8. Current admission and historical compatibility

New tasks use `financial_writing_agent.current_admission` and carry `writing_kernel_version=1.0` plus `quality_evidence`. The wrapper delegates identity/state semantics to `owner_guard.py` but fail-closes:
- RESEARCH forward transition without an admitted `DecisionEnvelope`;
- EDITORIAL forward transition without required Deep/Broad `StoryBlueprint` objects;
- EDITORIAL_AUDIT PASS/REVISE without required `PublicationFitness` evidence.

Historical states without the marker remain readable/resumable through the legacy/low-level owner guard. Historical receipts are not rewritten to manufacture new evidence.

## 9. Knowledge architecture

Financial retains two families:
1. topic/domain knowledge with freshness/revalidation semantics;
2. method/failure-pattern knowledge with source, fit, misfit, adoption state and revalidation trigger.

`knowledge/METHOD_KNOWLEDGE_CATALOG.json` is a durable catalog, not rule authority. Knowledge can accumulate broadly; production authority stays small and coherent.

Flow:
`recall -> revalidate -> use as evidence/candidate -> observe -> write back`.

Promotion is separate:
`evidence -> DecisionEnvelope -> candidate -> regression/eval -> owner promotion -> production observation`.

## 10. Governed evolution architecture

Financial-owned evolution follows:
`problem/feedback -> cognition -> failure class -> alternatives/counterexamples -> candidate -> reproducible evaluation -> owner-scoped promotion -> production reread -> live observation -> keep/repair/rollback/retire`.

User feedback is high-weight evidence, not automatic rule authority. One article may create a candidate but cannot silently become universal truth. Common/cross-domain changes upcall UAOS; Financial-local business/writing rules remain Financial-owned.

Material repository evolution uses candidate branch -> PR -> CI/evals -> contradiction scan -> controlled merge -> production reread/checks -> live observation.

## 11. Product architecture review

A major architecture change is admissible only when it reconciles:
- user/product outcome;
- workflow and identity/state ownership;
- functional and non-functional requirements;
- cognition/decision/story/audit topology;
- recovery and invalidation;
- evidence and assurance boundaries;
- historical compatibility/migration;
- acceptance and held-out evals;
- explicit non-goals.

Documentation alone is not acceptance evidence. Multi-agent complexity is introduced only when tools/data, permissions, context, output contract, independence or measured parallelism materially justify it; otherwise the one-owner focused-pass kernel is preferred.

## 12. Fitness functions and recovery

Executable invariants include:
- material decisions cannot omit alternatives/counterexamples/saturation;
- conflicted knowledge cannot be validated;
- Deep cannot carry a default word ceiling or omit declared material value-chain classes;
- material explanatory sections need company/case anchors;
- H1 sequence labels must be explicit/contiguous;
- publication PASS requires all eight gates with text evidence;
- MAJOR/CRITICAL or originality-rewrite findings block PASS;
- writing-kernel dependencies remain acyclic/complete.

REVISE/FAIL routes to the narrowest upstream cause: fact/coverage -> RESEARCH; story/retention -> EDITORIAL/TITLE; prose/originality/style -> DRAFT; Word/render -> DELIVERY. Material upstream changes invalidate dependent downstream PASS evidence.

## 13. Completion and assurance

A current article is complete only when research is complete or explicitly bounded, material decisions are admitted, required StoryBlueprints exist, all publication candidates pass evidence-backed fitness, delivery/mechanical/render checks pass, state/artifact identities reconcile, learning/evolution impact is classified and assurance is accurately reported.

Same-chat semantic review remains `CHAT_SELF_REVIEW`; role labels do not create independence. Green documentation or mechanical tests alone never certify semantic publication quality.
