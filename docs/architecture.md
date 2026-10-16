# Financial Writing Agent — Architecture

Version: `1.0.2-candidate`
Date: `2026-10-16`
Status: `DOMAIN_CANDIDATE`

## 1. Product boundary

Financial Writing is one domain/business owner under UAOS. UAOS owns common governance, cross-domain authority, parent continuity and shared cognition/evolution methods. Financial Writing owns article identity/state, research semantics, writing architecture, output contracts, domain knowledge/evolution evidence and delivery.

Hard invariants:
- one Financial business owner and one article state authority;
- no parent/child task-id equality requirement;
- historical state/receipts and legacy product semantics remain immutable provenance;
- historical provenance does not imply current-quality equivalence after a semantic-generation change;
- no mandatory live UAOS business proxy for normal Financial work;
- compliance, evidence integrity and owner-controlled mutation remain fail-closed.

## 2. Why 1.0.2 changes the 1.0 architecture

The 1.0 rebuild added hard cognition/story/publication-fitness admission after a rejected cross-border-ecommerce article. A later live continuation exposed a second-order defect: the same pre-kernel negative article could still be resumed at `DELIVERY` and terminalized after the rebuild without current DecisionEnvelope/StoryBlueprint/PublicationFitness evidence.

The same incident exposed a StoryBlueprint mismatch: research completeness was intended to protect thesis selection, but Deep validation could mechanically force all researched material classes into publication, encouraging a research-directory article. Named company anchors also did not guarantee event-to-company causal transmission.

1.0.2 therefore adds three bounded controls without creating another state machine:
1. post-evolution historical-resume compatibility admission;
2. explicit separation of complete research from selective publication;
3. event-to-company causal transmission for event-led stories.

Hook/style/anti-AI/numbering policy is **not** globally expanded from this one rejection; those existing gates must first be tested on a fresh current-kernel successor.

## 3. Stable lifecycle and focused internal passes

External lifecycle remains:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`.

Internal work remains:
`KNOWLEDGE_RECALL -> RESEARCH_DISCOVERY -> RESEARCH_ADVERSARIAL -> THESIS_ADJUDICATION -> STORY_ARCHITECTURE -> DRAFT_GENERATION -> READER_RETENTION_AUDIT -> EDITORIAL_TRIM -> {ORIGINALITY_AUDIT, FACT_INTEGRITY_AUDIT, STYLE_AUDIT} -> FINAL_SYNTHESIS`.

These are focused passes, not independent controllers. Same-model passes are structured challenge evidence, not independent certification.

## 4. Hosted cognition and problem-action architecture

UAOS-hosted cognition supplies the problem-response method; Financial keeps business adjudication local.

Material judgments use `DecisionEnvelope`: evidence beyond user assertion, challenged assumptions, credible alternatives, failure/fit/misfit conditions, counterexamples/rejected paths, selected rationale, search saturation, verification and remaining unknowns.

Detected problems additionally require micro diagnosis, macro/topology alignment, governing-assumption challenge and external method/architecture research. Systemic signals compare local/workflow/domain-architecture/common-capability hypotheses before repair. Evolution disposition precedes terminal repair/no-change, and owner-authorized repair cannot end as recommendation-only when it is executable now.

User feedback is failure evidence, not root-cause authority.

## 5. Research architecture

Normal thematic/company work follows:
`prior cognition recall -> value-chain preflight -> company universe -> current evidence -> adversarial/disconfirming search -> saturation -> thesis competition -> Company Decision Map -> Research Audit`.

Thesis selection before value-chain coverage is invalid. Prior knowledge accelerates mapping but never waives it. Search saturation is bounded: at least two materially different no-delta sweeps; any later material discovery invalidates convergence.

**Research completeness is an epistemic safety property, not a publication-outline mandate.**

## 6. Story construction and publication-scope architecture

`StoryBlueprint` bridges audited cognition to prose. It captures reader job/start state, article promise, central question, author stance, narrative engine, opening anchor/gap/payoff, numbered section plan, new information, company/case anchors, selected value-chain classes, evidence refs, bridges/open loops, ending payoff and voice evidence.

Story form follows material. Legal engines include hard anomaly, company conflict, reversal, mystery, system map, consequence chain, event-to-company, case lead and timeline escalation.

### FINANCE_DEEP

Deep is the complete finance/review **product**, not a complete dump of research.

- Research first maps the material value chain/company universe.
- If the final story genuinely needs every researched class, full coverage is legal.
- If any researched class is left out of copy, `ValueChainScopeDecision` must account for every researched class as `CORE`, `SUPPORT`, or `OMIT_WITH_REASON`, with evidence/rationale.
- CORE/SUPPORT classes must appear in the blueprint; OMIT classes preserve research provenance but must not silently appear as article branches.
- No default word ceiling exists; length follows selected material, not the size of the research map.

### Event-led stories

When the explanatory burden is an event/rule/change flowing into listed-company economics, `NarrativeEngine.EVENT_TO_COMPANY` requires each material section to carry `CausalTransmission`:
`trigger/change -> mechanism -> company exposure -> operating/financial expression -> verification/reversal condition`.

This avoids decorative company mentions. The engine is conditional, not a universal template.

`FINANCE_BROAD` remains independently rebuilt for acquisition from audited evidence, not shortened Deep.

## 7. Publication fitness architecture

Every current long-form product supplies exactly these evidence-backed gates:
- `FACT_INTEGRITY`
- `RETENTION`
- `COMPANY_GROUNDING`
- `STRUCTURE_NUMBERING`
- `ORIGINALITY`
- `AUTHORIAL_STYLE`
- `COMPLIANCE`
- `PAYOFF`

Each semantic gate records text location, excerpt, finding and severity. MAJOR/CRITICAL findings block PASS; REVISE requires concrete repair actions.

Originality is source-compared evidence, not a self-assertion. Research is normalized to claims/notes before drafting; suspicious/distinctive passages are checked against material sources; close paraphrase/patchwriting forces revision. Same-chat review cannot claim zero plagiarism.

Natural prose is material/stance/story/voice first. Generic scaffolding is diagnostic when clustered/unearned, not a phrase blacklist or humanizer generator.

## 8. Current admission and post-evolution resume compatibility

New tasks use `financial_writing_agent.current_admission` and carry `writing_kernel_version=1.0` plus `quality_evidence`. Current admission fail-closes:
- RESEARCH forward without admitted `DecisionEnvelope`;
- EDITORIAL forward without required StoryBlueprints;
- EDITORIAL_AUDIT PASS/REVISE without PublicationFitness.

Historical state remains readable provenance. Before **materially** continuing a state without the current kernel marker, `financial_writing_agent.resume_compatibility.require_material_resume_admission` classifies intent:
- `CURRENT_STATE`: already current;
- `HISTORICAL_PROVENANCE_ONLY`: explicit historical-semantics continuation, no current-quality claim;
- `CURRENT_SUCCESSOR_REQUIRED`: ordinary/current-quality continuation must create a fresh current-kernel successor/replay.

This guard does not rewrite the old state and does not transfer ownership to UAOS. It separates continuity from assurance.

## 9. Knowledge architecture

Financial retains topic/domain knowledge and method/failure-pattern knowledge with source, scope, fit/misfit, adoption/confidence and revalidation semantics. `knowledge/METHOD_KNOWLEDGE_CATALOG.json` is a durable catalog, not rule authority.

Use flow: `recall -> revalidate -> use as evidence/candidate -> observe -> write back`.
Promotion flow: `evidence -> DecisionEnvelope/root scope -> candidate -> regression/eval -> owner promotion -> production observation`.

## 10. Governed evolution and parent upcall

Financial-owned evolution follows:
`problem/feedback -> causal diagnosis -> alternatives/counterexamples -> root-scope admission -> evolution disposition -> candidate -> reproducible eval -> owner promotion -> production reread -> live observation -> keep/repair/rollback/retire`.

One article may create a domain candidate but cannot silently become universal truth. Financial-local business/writing rules remain Financial-owned. A credible common/cross-domain failure class is raised as a non-authoritative child upcall; UAOS decides whether a common outcome-level rule belongs in parent governance.

The cross-border incident therefore creates:
- a Financial domain candidate for resume compatibility/publication scope/event-company causality;
- a UAOS parent-upcall candidate asking whether `cross_chat_continuity_and_recovery` should require owner-defined compatibility admission after material child semantic upgrades.

UAOS must not copy Financial’s schema/markers into other domains.

## 11. Product architecture review

A major change reconciles user/product outcome, identity/state ownership, functional/non-functional requirements, cognition/story/audit topology, recovery/invalidation, evidence/assurance boundaries, historical compatibility, acceptance/held-out evals and explicit non-goals.

Documentation alone is not evidence. Multi-agent complexity is introduced only when tools/data, permissions, context, output contract, independence or measured parallelism materially justify it.

## 12. Fitness functions and recovery

Executable invariants include:
- material decisions cannot omit alternatives/counterexamples/saturation;
- conflicted knowledge cannot be validated;
- pre-current-kernel material resume cannot silently inherit current-quality assurance;
- Deep has no default word ceiling;
- selective Deep omission requires complete publication-scope accounting;
- EVENT_TO_COMPANY material sections require full causal transmission;
- material sections need company/case grounding;
- H1 labels are explicit/contiguous;
- publication PASS requires all eight evidence-backed gates;
- MAJOR/CRITICAL or originality-rewrite findings block PASS;
- writing-kernel dependencies remain acyclic/complete.

Recovery routes to the narrowest upstream cause: historical semantic generation gap -> successor/replay; fact/coverage -> RESEARCH; story/scope/company causality/retention -> EDITORIAL/TITLE; prose/originality/style -> DRAFT; Word/render -> DELIVERY. Material upstream change invalidates dependent downstream PASS evidence.

## 13. Completion and assurance

A current article is complete only when research is complete/bounded, material decisions are admitted, required StoryBlueprints exist, publication candidates pass evidence-backed fitness, delivery/mechanical/render checks pass, state/artifact identities reconcile, evolution impact is classified and assurance is accurate.

A historical article delivered under historical semantics is not evidence that current 1.0.x semantic gates were executed. Same-chat semantic review remains `CHAT_SELF_REVIEW`; role labels do not create independence. Green CI/documentation/mechanical checks never certify live reader quality.
