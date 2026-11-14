# Financial Writing Agent — Architecture

Version: `1.1.0 / standalone Financial operating domain`
Reviewed: `2026-11-12`
Status: `STANDALONE_ENGINEERING_CANDIDATE__REAL_EDITORIAL_PRODUCT_NOT_READY`

## 1. Product boundary

Financial Writing is an independent business owner. It performs its own goal interpretation, source research, decision/execution/repair loops, model-assisted story creation, article state and independent checks; it has no external parent runtime, external Host or parent grant dependency. Financial Writing owns article identity/state, research semantics, writing architecture, output contracts, domain knowledge/evolution evidence and delivery.

Hard invariants:
- one Financial business owner and one article state authority;
- one article identity namespace owned by Financial (no parent task ID);
- historical state/receipts and legacy product semantics remain immutable provenance;
- historical provenance does not imply current-quality equivalence after a semantic-generation change;
- no external parent/Host runtime dependency for any Financial work;
- compliance, evidence integrity and owner-controlled mutation remain fail-closed.

## 1A. Current standalone deployment and capability boundary

Primary Skill is `skills/financial-writing-agent/SKILL.md`; current machine declarations are `config/FINANCIAL_MANIFEST.json` and `config/FINANCIAL_CAPABILITIES.json`. The independent Python action adapter `financial_writing_agent/standalone_runtime.py` uses the existing Article Aggregate with external user authorization, exact Git provider content/SHA, conditional writes, stage artifact readback and a second state read. It does not import an external parent runtime. Retired integration stubs have been removed from the current tree.

Model/web/data retrieval and document tools must actually be connected in the Financial environment; an installed Python wheel by itself does not execute LLM research or prove any native plugin connection. The real cross-border v3 task and all historic receipts remain unchanged. Full product readiness still requires independently observed financial facts, useful narrative and actual accessible Word results.

## 2. Why 1.0.3 changes the 1.0.2 architecture

The 1.0 rebuild added hard cognition/story/publication-fitness admission. The 1.0.2 repair added historical-resume compatibility, research/publication separation and event-to-company causal transmission.

A fresh current-kernel cross-border successor then exposed another control gap: broad research and publication selectivity existed, but the comprehensive private analytical workbench remained task-local rather than admission-bound. Repeated live refinement had to add full company-universe coverage, company-level business granularity, market-cap/liquidity, catalyst strength, benefit tiers, short-horizon market roles, counterfactual comparisons, negative pools, scenario trees and next-window falsification manually. Because none of that was a required quality object, the next article could legally leave RESEARCH with only a DecisionEnvelope and regress to a thinner research package.

1.0.3 therefore adds one bounded domain control without creating another state machine:
1. a mandatory digest-bound `PrivateResearchBrief` for new Financial tasks;
2. explicit Research Audit semantics for that brief;
3. publication distillation that keeps the private analytical machinery upstream while allowing Deep/Broad to remain selective reader products.

This is Financial-domain research architecture. It is not a CAOS common-rule promotion and does not retroactively rewrite historical/current pre-marker tasks.

## 3. Stable lifecycle and focused internal passes

External lifecycle remains:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`.

No extra external stage is introduced. The private brief is an admitted quality object owned by RESEARCH.

Internal work becomes:
`KNOWLEDGE_RECALL -> RESEARCH_DISCOVERY -> RESEARCH_ADVERSARIAL -> PRIVATE_RESEARCH_SYNTHESIS -> THESIS_ADJUDICATION -> STORY_ARCHITECTURE -> DRAFT_GENERATION -> READER_RETENTION_AUDIT -> EDITORIAL_TRIM -> {ORIGINALITY_AUDIT, FACT_INTEGRITY_AUDIT, STYLE_AUDIT} -> FINAL_SYNTHESIS`.

These are focused passes, not independent controllers. Same-model passes are structured challenge evidence, not independent certification.

## 4. Financial-owned cognition and decision architecture

Financial natively applies its decision and execution methods. DecisionEnvelope and evidence-grounded causal challenges are Financial-owned, with no external controller or parent authorization.

Material judgments use `DecisionEnvelope`: evidence beyond user assertion, challenged assumptions, credible alternatives, failure/fit/misfit conditions, counterexamples/rejected paths, selected rationale, search saturation, verification and remaining unknowns.

Detected problems additionally require micro diagnosis, macro/topology alignment, governing-assumption challenge and external method/architecture research. Systemic signals compare local/workflow/domain-architecture/common-capability hypotheses before repair. Evolution disposition precedes terminal repair/no-change, and owner-authorized repair cannot end as recommendation-only when it is executable now.

User feedback is failure evidence, not root-cause authority. The private-research requirement is promoted here because repeated live failures plus an observable admission gap supported a domain-workflow cause; it is not promoted solely because a user requested a preferred implementation.

## 5. Research architecture

Normal thematic/company work follows:
`prior cognition recall -> value-chain preflight -> company universe -> current evidence -> adversarial/disconfirming search -> saturation -> private research synthesis -> thesis competition -> Company Decision Map -> Research Audit`.

Thesis selection before value-chain coverage/private-research synthesis is invalid. Prior knowledge accelerates mapping but never waives current verification. Search saturation is bounded: at least two materially different no-delta sweeps; any later material discovery invalidates convergence.

**Research completeness is an epistemic safety property, not a publication-outline mandate.**

### 5.1 PrivateResearchBrief

New states created through `financial_writing_agent.current_admission.build_initial_state` bind `private_research_contract_version=1.1` with fifteen required modules; historical 1.0 evidence remains parseable only where explicitly marked.

`financial_writing_agent.private_research` defines the required modules and validates structural admission. `financial_writing_agent.current_admission.advance_state` persists the validated object under `quality_evidence.private_research_brief`, computes a canonical digest and binds it to the RESEARCH execution receipt.

Required modules are:
- `company_universe_and_value_chain`;
- `business_granularity`;
- `market_cap_and_liquidity`;
- `catalyst_strength_and_freshness`;
- `benefit_chain_tiering`;
- `short_horizon_role_map`;
- `market_structure_and_positioning`;
- `counterfactual_company_comparison`;
- `negative_and_falsification_pool`;
- `scenario_tree`;
- `next_window_validation`;
- `publication_distillation`;
- `material_catalyst_and_policy_ledger` (contract 1.1): all materially relevant events and policy phases, including changes, suspensions, reductions, exemptions, retaliation, expiry and rollback;
- `driver_sustainability_operability_and_concept_map` (contract 1.1): independently evidence the immediate driver, durability, market operability and concept/sector identity;
- `cross_segment_global_selection` (contract 1.1): compare segment winners and role candidates again across the whole market under current catalyst, liquidity and sentiment constraints.

Every module is `APPLICABLE` or `NOT_MATERIAL`; applicable modules require evidence refs and `NOT_MATERIAL` requires an explicit reason. The validator deliberately proves contract completeness, not semantic excellence. Research Audit remains responsible for detecting placeholder evidence, stale facts and unjustified role labels.

For short-horizon A-share work, market roles are hypotheses, not taxonomy pasted after price moves. A high board is not automatically a theme leader; a pioneer may be replaced; a capacity middle-army validates participation rather than height; card-position requires an observable competitor/role displacement; catch-up usually depends on height/attention already created elsewhere. `Business strongest` and `most likely short-horizon market core` remain separate judgments.

Time-sensitive market cap, float cap, turnover, board height, promotion rate, catalyst state and operating data require an `as_of` boundary. Private deliverables may display these fully; publication does not have to narrate them all.

### 5.2 Backward compatibility

The private-research requirement is marker-gated. Existing states without `private_research_contract_version` remain valid and are not retroactively invalidated. If a pre-marker task is materially replayed as a new current-quality task, normal resume-compatibility semantics determine whether a successor is required; a newly created successor receives the marker automatically.

A revision to RESEARCH invalidates all quality evidence, including the admitted private brief and research decision. Editorial/Draft revisions do not erase still-valid upstream research.

## 6. Story construction and publication-scope architecture

`StoryBlueprint` bridges audited cognition to prose. It captures reader job/start state, article promise, central question, author stance, narrative engine, opening anchor/gap/payoff, numbered section plan, new information, company/case anchors, selected value-chain classes, evidence refs, bridges/open loops, ending payoff and voice evidence.

Story form follows material. Legal engines include hard anomaly, company conflict, reversal, mystery, system map, consequence chain, event-to-company, case lead and timeline escalation.

### FINANCE_DEEP

Deep is the complete finance/review **product**, not a complete dump of research.

- Research first maps the material value chain/company universe and admits the private brief.
- `publication_distillation` records which private conclusions must inform Deep/Broad and which internal machinery should remain private.
- If the final story genuinely needs every researched class, full coverage is legal.
- If any researched class is left out of copy, `ValueChainScopeDecision` must account for every researched class as `CORE`, `SUPPORT`, or `OMIT_WITH_REASON`, with evidence/rationale.
- CORE/SUPPORT classes must appear in the blueprint; OMIT classes preserve research provenance but must not silently appear as article branches.
- No default word ceiling exists; length follows selected material, not the size of the research map.
- Universe bookkeeping, internal scores, tactical role ladders and research-process narration do not leak into copy unless they materially improve reader understanding.

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

Research Audit separately checks the private brief semantically: coverage, company granularity, current market data where material, catalyst/benefit-tier logic, role semantics, counterfactual comparison, negative pool, scenario tree, next-window falsification and publication distillation.

Originality is source-compared evidence, not a self-assertion. Research is normalized to claims/notes before drafting; suspicious/distinctive passages are checked against material sources; close paraphrase/patchwriting forces revision. Same-chat review cannot claim zero plagiarism.

Natural prose is material/stance/story/voice first. Generic scaffolding is diagnostic when clustered/unearned, not a phrase blacklist or humanizer generator.

## 8. Current admission and post-evolution resume compatibility

New tasks use `financial_writing_agent.current_admission` and carry `writing_kernel_version=1.0`, `private_research_contract_version=1.1` plus `quality_evidence`. Current admission fail-closes:
- RESEARCH forward without admitted `DecisionEnvelope`;
- marker-enabled RESEARCH forward without valid `PrivateResearchBrief`;
- downstream validation when either admitted research object is missing, tampered or no longer matches its RESEARCH receipt digest;
- EDITORIAL forward without required StoryBlueprints;
- EDITORIAL_AUDIT PASS/REVISE without PublicationFitness.

Historical state remains readable provenance. Before **materially** continuing a state without the current kernel marker, `financial_writing_agent.resume_compatibility.require_material_resume_admission` classifies intent:
- `CURRENT_STATE`: already current;
- `HISTORICAL_PROVENANCE_ONLY`: explicit historical-semantics continuation, no current-quality claim;
- `CURRENT_SUCCESSOR_REQUIRED`: ordinary/current-quality continuation must create a fresh current-kernel successor/replay.

The private-research marker is intentionally separate from the writing-kernel marker so already-created 1.0/1.0.2 states are not silently invalidated by the 1.0.3 domain upgrade.

This guard does not rewrite the old state or transfer ownership outside Financial. It separates continuity from assurance.

## 9. Knowledge architecture

Financial retains topic/domain knowledge and method/failure-pattern knowledge with source, scope, fit/misfit, adoption/confidence and revalidation semantics. `knowledge/METHOD_KNOWLEDGE_CATALOG.json` is a durable catalog, not rule authority.

Use flow: `recall -> revalidate -> use as evidence/candidate -> observe -> write back`.
Promotion flow: `evidence -> DecisionEnvelope/root scope -> candidate -> regression/eval -> owner promotion -> production observation`.

## 10. Governed evolution architecture

Financial-owned evolution follows:
`problem/feedback -> causal diagnosis -> alternatives/counterexamples -> root-scope admission -> evolution disposition -> candidate -> reproducible eval -> owner promotion -> production reread -> live observation -> keep/repair/rollback/retire`.

One article may create a domain candidate but cannot silently become universal truth. Financial-specific business/writing rules and generalizable methods used inside Financial remain Financial-owned. Reusable methods are evaluated and promoted only with Financial-local negative/positive evidence, current Financial operations reject parent upcalls; external methods may inform local choices but cannot delegate ownership.

The 1.0.3 private-research admission is Financial-local. It governs how A-share financial writing research is represented before publication and never requires another agent to adopt its domain-specific taxonomy.

## 11. Product architecture review

A major change reconciles user/product outcome, identity/state ownership, functional/non-functional requirements, cognition/story/audit topology, recovery/invalidation, evidence/assurance boundaries, historical compatibility, acceptance/held-out evals and explicit non-goals.

Documentation alone is not evidence. Multi-agent complexity is introduced only when tools/data, permissions, context, output contract, independence or measured parallelism materially justify it.

## 12. Fitness functions and recovery

Executable invariants include:
- material decisions cannot omit alternatives/counterexamples/saturation;
- new marker-enabled research cannot advance without PrivateResearchBrief;
- admitted private research is digest-bound and tamper-detected;
- required private-research modules cannot be omitted;
- APPLICABLE modules need evidence refs and NOT_MATERIAL modules need reasons;
- COMPLETE coverage cannot retain unresolved gaps and BOUNDED_WITH_GAPS cannot hide them;
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

Recovery routes to the narrowest upstream cause: historical semantic generation gap -> successor/replay; private-research/fact/coverage -> RESEARCH; story/scope/company causality/retention -> EDITORIAL/TITLE; prose/originality/style -> DRAFT; Word/render -> DELIVERY. Material upstream change invalidates dependent downstream PASS evidence.

## 13. Completion and assurance

A current 1.0.3 article is complete only when research is complete/bounded, material decisions and required PrivateResearchBrief are admitted, required StoryBlueprints exist, publication candidates pass evidence-backed fitness, delivery/mechanical/render checks pass, state/artifact identities reconcile, evolution impact is classified and assurance is accurate.

A historical or pre-private-marker article is not evidence that 1.0.3 private-research semantics were executed. Same-chat semantic review remains `CHAT_SELF_REVIEW`; role labels do not create independence. Green CI/documentation/mechanical checks verify executable invariants but never certify live reader quality.

## Owner intent, requirements, methodology CRUD and recursive dependency control (2026-11-12)

The evidence-first governance method is **implemented as Financial-owned behavior**, not a new parent/Host/runtime dependency. The current Financial Skill remains the sole domain operating entry. Source authority: actual user message/correction → authenticated owner-intent evidence → typed requirement classification; task requirements and stage invalidations stay in one Article Aggregate. Nonbinding ideas remain visible in the article's `intent_history` without acquiring hard-goal authority. `USER_EXPLICIT` is never an inferred default.

Decision and execution are distinct loops with recursive re-entry. The decision loop challenges source, task interpretation, alternative mechanisms, chosen methodology, and its verifier; the execution loop performs an authorized action, independently reads back actual source/effect, follows downstream invalidation and may reopen an upstream hypothesis. The ten-stage business state graph is unchanged; problem/recovery and feedback governance remain owner-native.

The existing method catalog is the **only method knowledge authority**. It carries a versioned, append-only change history, pending revisions that cannot silently replace current methods, explicit candidate/adopted/challenged/retired states, non-destructive retirement and verified promotion/impact closures. Existing legacy method labels remain LEGACY_DECLARED; they are not automatic proof of an independently validated method. The dedicated method-scope action in the same `standalone_runtime` uses user-authenticated exact Git CAS/readback but is **not a second task state or workflow controller**. A changed method records affected stages and OPEN revalidation rather than silently approving old dependent tasks.

Assurance boundary: synthetic CI verifies deterministic admission and state replay; native Financial plugin activation, real original-message provider, semantic intent classification and cross-article live impact verification remain separate evidence requirements. See `evals/FINANCIAL_GOAL_METHOD_GOVERNANCE_AUDIT_20261112.md`.

### Method-version→Article dependency edge (verified synthetic path)

When a current research DecisionEnvelope explicitly names a method ID, the Financial provider action gateway binds its effective ACTIVE record hash, method revision and catalog revision into the existing RESEARCH receipt. Each following stage reads the method catalog and compares effective fingerprints. A pending revision that has **not** been promoted leaves active evidence unchanged; a revised, challenged or retired method fails closed with `METHOD_DEPENDENCY_STALE`. The authorized `REOPEN_METHOD_DEPENDENCY` action derives the earliest affected stage from signed/provider-read catalog change-event history, archives invalidated evidence, reuses `owner_guard._invalidate_from`, preserves original task requirements, and appends a canonical owner receipt under Git CAS/readback. An unrelated method change does not create false invalidation. This is a dependency edge in existing Financial state and method catalog, not a second Graph or shadow history.

Coverage is scoped to **explicit method IDs used in an admitted research decision**. It does not heuristically infer every LLM method influence or automatically crawl all historical articles. Unverifiable provenance remains OPEN; a real connected client must supply the actual method reader.


## 14. Active ChatGPT-native execution runtime

The current user-facing runtime is the ChatGPT model following the single Financial Skill, with the user's already-connected GitHub connector as the persistent provider and current web/document/Python tools for research and production. The Skill-only plugin is an instruction package; it neither grants GitHub access nor hosts Python/MCP. This design therefore requires no custom hosted service, local daemon or paid API.

All persistent task state and artifacts remain in the existing Financial repository. Single-file writes use the current blob SHA and exact readback. Multi-file writes use Git blobs, a tree based on the current main tree, a commit parented to the exact current main head, and update_ref with expected_sha and force=false; every changed path is then read back at the resulting commit SHA. Binary Word artifacts use base64 blobs. Stale writes stop for reread and recomputation. Explicit owner confirmation in the current conversation authorizes binding requirement changes; the full source message and confirmation are preserved in the existing article intent history.

The Python standalone_runtime module remains a reference implementation and CI test target for a separately hosted integration. It is not directly invoked by a Skill-only chat and is not a prerequisite for the active ChatGPT path. Its HMAC/provider gates remain applicable only when that optional adapter is actually deployed and called. System release acceptance, independent editorial acceptance and real article quality remain separate from basic native execution.

## 15. Article action effect binding

The article aggregate's execution receipt and the provider's effect receipt are separate, linked evidence. Authorization alone binds intent to the prior state; the effect receipt binds the authenticated action to the exact resulting Git blob. The canonical state remains workspaces/articles/<task_id>/STATE.json; each action's immutable effect evidence is stored under that same article at actions/<action_id>.effect.json. No second business-state ledger is introduced.

For each new article mutation, the runtime requires a fresh provider-signed action authorization and a provider-signed action_effect receipt with the same actor/provider. The signed claims bind action ID, task ID, operation, previous and resulting state blob SHAs, request SHA-256, authorization-attestation SHA-256, effect contract version and the canonical admission runtime. Both files are committed atomically with one conditional Git update, then reread by exact blob identity. The next action's previous-state SHA must equal the preceding effect's resulting-state SHA; the latest effect must equal the current state blob. This closes the gap between a valid authorization and an independently verifiable persisted effect.

Legacy signed authorization v1.0 records remain immutable and are reported as effect-unbound history. They are not silently rewritten or treated as effect proof. New writes use authorization v1.1 plus effect receipt v1.0, and history cannot roll back to v1.0 after an effect-bound action. The optional Python adapter is still not the active ChatGPT Skill runtime; the native client cannot manufacture the provider signature. Missing live signer/CAS capability therefore remains fail-closed and keeps the external provider gate OPEN.

## 16. Method-catalog effect binding and operation replay

The existing METHOD_KNOWLEDGE_CATALOG remains the sole method authority. A new method event references a detached provider-signed effect receipt under knowledge/actions/<action_id>.effect.json. The receipt binds the exact prior and resulting catalog Git blob SHAs, action/task scope, operation, knowledge ID, canonical request digest, exact authorization-attestation digest and admission runtime. Authorization and effect use the same authenticated actor/provider. Catalog and receipt are committed atomically and read back by exact blob identity.

The two-revision audit verifies the prior catalog SHA against the base bytes, verifies the detached effect signature and resulting catalog SHA against candidate bytes, and replays the signed operation against the prior catalog. It compares the full resulting catalog except non-business clock fields. This closes both the stale-prior-SHA gap and the ability to alter a candidate record or lifecycle status while keeping a valid authorization event. Historical method events remain effect-unbound; after the first effect-bound event, history cannot roll back. Effect binding does not replace independent promotion review or impact revalidation.

## 17. Writing-business operational consistency (2026-11-14)

The ten-stage Article Aggregate is the only business cursor; internal writing passes are a DAG inside the relevant stage, not a second controller. The article's default PORTFOLIO requires two **distinct** editorial blueprints and four verifiable Word outputs. Deep/Broad must differ materially in reader job, article promise, opening, narrative path and payoff; the deterministic clone detector can reject cosmetic Deep-to-Broad copies but cannot prove reader value.

EDITORIAL_AUDIT has two honest outcomes:

- PUBLICATION_CERTIFICATION: the existing eight-gate PublicationFitness PASS requires independent editorial provenance and a trusted authenticated review verifier of the exact draft.
- INTERNAL_DELIVERY_READINESS: same-chat review can mark eight internal gates PASS for Word draft export only after the current persisted DRAFT artifact bytes are reread and the reviewer-declared content SHA-256 matches. The final owner state remains DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN, and independent editorial quality/readership outcomes remain false.

A missing/changed draft, REVISE gate, cloned Broad blueprint, or stale source prevents progression. This removes an operational deadlock without converting chat self-review into independent editorial acceptance. A complete writing-business outcome still requires real-source fact/quality work; synthetic transport CI only verifies the mechanism. The Git repository exact-diff audit now includes knowledge/actions detached method-effect receipt paths, preventing orphaned evidence changes from bypassing GitHub changed-path selection.

## 19. User-outcome-first replay and executable pass contracts (2026-11-14)

The user-facing goal is not completion of 10 stage names or existence of 13 pass definitions. Prior synthetic tests could create arbitrary stage files, then simulated Word and review artifacts, without executing actual writing passes. A real user goal needs each instruction traced from exact intake provenance through evidence, thesis, title, independently architected Deep/Broad prose, factual/retention/style review, revision, and Word output.

**Pass graph:** RESEARCH_DISCOVERY now produces discovery_package/source_evidence_ledger for downstream consumers; RESEARCH_ADVERSARIAL produces adversarial_package. THESIS_ADJUDICATION produces decision_envelope instead of needing it before adjudication. The executable contract adapter checks producer/consumer names, missing external inputs, missing outputs and Research Audit boundary before story architecture. Callback outputs are execution traces only, NOT factual/editorial certification. The existing Article Aggregate remains the only persisted state owner.

**User instructions:** TaskRequirement Authority admits arbitrary owner-authored requirement IDs, but a historical hard-coded Word gate used to reject everything except one Deep requirement and any Broad requirement. The corrected publication scope permits structurally admitted generic requirements on both Deep/Broad, reports semantic status as unverified and preserves strict Deep full-universe checks. DELIVERY-stage requirements may remain pending during Word build, but the owner state transition still requires exact satisfaction evidence and source readback. Requirements not yet due prevent premature publication; a mis-scoped Deep-only full-universe requirement in Broad is rejected.

**Open business outcome:** a connected host has yet to demonstrate that it actually invokes every pass, persists the meaningful outputs, matches the final prose to the instructions and earns a real source-backed editorial/reader assessment across topics. Such claims remain OPEN even if synthetic CI passes.
