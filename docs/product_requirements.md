# Financial Writing Agent — Product Requirements

Status: `1.1.0_STANDALONE_FINANCIAL__EDITORIAL_NOT_READY`
Version: `1.1.0-candidate`
Review date: `2026-11-12`
Owner: `DOMAIN:financial_writing`
Operating governance: Financial Writing's own Skill, DecisionEnvelope, owner state and independent QA; NO external parent.

## 1. Product outcome

Financial Writing turns a finance topic, user materials and current evidence into publication-ready Chinese financial content that is:
- factually defensible and auditable;
- complete enough at research level to avoid missing material value-chain branches;
- supported by a comprehensive private research layer before publication planning;
- editorially selective rather than a dump of the research map;
- company-grounded through causal economics rather than decorative company mentions;
- structurally designed to earn reader continuation and completion;
- original in wording and construction rather than source-shaped patchwriting;
- recognizably authored rather than generic checklist prose;
- non-actionable and compliant for financial publication;
- delivered as verified Word artifacts when required;
- able to learn from prior work without treating memory, user feedback or old facts as unquestioned truth.

The governing outcome is not “satisfy the most rules”. It is **high-value, evidence-bounded writing whose private research is deep enough to support better judgment and whose public copy is selective enough for real readers**.

## 2. Core design principles

1. User feedback is high-weight evidence, not automatic rule authority.
2. Learned knowledge retains provenance, scope, fit/misfit and revalidation conditions; it does not silently mutate rules.
3. Material judgments require deliberate comparison, current evidence, counterexamples and a verification plan; problem/architecture judgments additionally require relevant external method evidence.
4. Research completeness and publication selectivity are separate: private research may be broad and tactical; publication must choose what serves the reader thesis.
5. Historical provenance and current-quality equivalence are separate: old state may remain readable, but semantic-generation gaps require compatibility admission before current-quality continuation.
6. The writer does not self-certify its own quality.
7. Semantic review cites text-level evidence; naked PASS labels are insufficient.
8. Deterministic rules enforce invariants/tripwires, not fake semantic quality.
9. Multi-agent complexity is introduced only when evals and materially different responsibilities justify it.
10. Same-session critique remains `CHAT_SELF_REVIEW` unless distinct execution evidence exists.
11. Historical states/contracts/receipts remain immutable provenance.
12. Free or already-available authoritative tools are preferred when sufficient; paid crawling is a fallback for real evidence gaps, not a default.

## 3. Primary user journeys

### PR-01 — Direct domain operation and ownership

A fresh session selects Financial Writing directly. Financial independently owns its goal/decision/execution loops, article state, user corrections, source and writing quality, evidence and delivery. No external parent runtime or second controller may be required.

### PR-02 — Feedback classification before evolution

Any material user correction/rejection triggers problem cognition, but the system must distinguish factual correction, preference, article-specific requirement, recurring writing defect, method defect, architecture/control defect and proposed implementation idea. The failed outcome is evidence; the user’s suggested fix remains a candidate until compared against alternatives.

### PR-03 — Knowledge acquisition and durable reuse

Financial retains topic/domain cognition and method/architecture/writing cognition. Reusable records need provenance, category, scope, confidence/adoption state, known conflicts/misfit and a revalidation condition. Retrieved knowledge seeds the next task but cannot bypass current evidence.

### PR-04 — Value-chain-first research and broad search

For material thematic/company work, Research must:
1. recall prior relevant cognition;
2. enumerate material value-chain classes before selecting the thesis;
3. map the relevant listed-company universe across those classes;
4. gather current evidence and chronology;
5. perform disconfirming/counterexample search;
6. synthesize the mandatory private research brief;
7. compare candidate causal explanations;
8. record unresolved gaps.

“Complete” means evidence-bounded coverage, not exhaustive crawling. Material thesis search stops only after at least two consecutive materially different sweeps add no decision-changing candidate, failure mode, counterexample or changed decision. A later material discovery invalidates saturation.

### PR-04A — Mandatory PrivateResearchBrief before publication planning

Every new Financial task created through current admission carries `private_research_contract_version=1.1`. Leaving RESEARCH requires both an admitted material `DecisionEnvelope` and a digest-bound `PrivateResearchBrief`.

The brief is the private analytical workbench, not the public article. It must include every required module from `skills/financial-writing-agent/references/private_research.md`, each marked `APPLICABLE` or `NOT_MATERIAL` with explicit reasoning. For ordinary A-share thematic/company work where market behavior matters, the brief covers as applicable:
- economic-substance and market-label company universes;
- company-level revenue/profit/business-stage/channel/customer/order detail;
- total market cap, float market cap, turnover, traded value and liquidity for material short-horizon candidates;
- catalyst strength, freshness, official/rumor status and expectation/implementation/realization stage;
- direct/first-order/second-order/weak/negative benefit tiers;
- short-horizon role hypotheses: pioneer, sentiment high/space leader, theme leader, capacity middle-army/trend leader, branch leader, assist, card-position competitor, catch-up, follower and eliminated candidate;
- market sentiment cycle, board-height/promotion structure and recent stock character;
- explicit `why A rather than B` comparisons;
- negative/falsification pool;
- catalyst-specific scenario trees and benefit ladders;
- next-session/next-catalyst confirmation and falsification conditions;
- publication distillation telling Deep/Broad which conclusions to use and which internal machinery should stay private.

`business strongest` and `most likely to become a short-horizon market core` are separate judgments. A company list, a few representative companies or one composite score cannot substitute for the brief.

### PR-05 — Decision Envelope for material judgments

Before executing a material judgment, Financial must represent objective, evidence, learned items, challenged assumptions, at least two credible alternatives, fit/misfit/failure modes, counterexamples, rejected paths, selected candidate/rationale, search saturation, verification plan, remaining unknowns and evolution disposition. Mechanical actions do not require a full envelope.

### PR-06 — FINANCE_DEEP is the complete finance product, not the complete research dump

For thematic/industry Deep work:
- Research must cover the material value-chain/company universe and admitted PrivateResearchBrief before thesis selection/publication planning.
- Publication must select the economically decisive path rather than mechanically mirror the private research directory.
- If every researched material class is genuinely needed by the selected story, full publication coverage is legal.
- If any researched material class is omitted from copy, `publication_scope_decisions` must account for every researched class as `CORE`, `SUPPORT`, or `OMIT_WITH_REASON`, with evidence and rationale.
- `OMIT_WITH_REASON` preserves research provenance but must not silently become a full publication branch.
- Selected material explanatory sections must ground mechanisms in named company/case evidence where available.
- H1 sections use explicit contiguous Chinese numbering (`一、二、三、...`).
- Company comparisons remain evidence-bounded and non-actionable.
- Internal bookkeeping, tactical role maps, exhaustive-universe narration and private scores stay out of publication copy unless they materially improve the reader product.
- **There is no default word-count ceiling.** Remove redundancy; do not add or remove material merely to hit a length target.

### PR-07 — FINANCE_BROAD is selective acquisition, not shortened Deep

Broad selects from audited evidence and private-research conclusions based on acquisition value but has its own blueprint, retention path and payoff. It may not be created by mechanically shortening Deep.

### PR-08 — Story Blueprint before prose

Substantive long-form publication requires a `StoryBlueprint` recording reader job/start state, article promise/central question, author stance, narrative engine, opening anchor, information gap, early/later payoff, numbered section plan, per-section new information, company/case anchors, selected value-chain classes, evidence refs, bridges/open loops, ending payoff and voice evidence.

For event-led finance stories whose explanatory burden is the transmission of an event/rule/change into listed-company economics, the `EVENT_TO_COMPANY` engine requires every material explanatory section to bind:
`trigger/change -> mechanism -> company exposure -> operating/financial expression -> verification/reversal condition`.
A company mention without that chain is not sufficient causal grounding.

Story form follows material. Nut-graf, five-box, hourglass and similar forms are candidate methods, not universal templates.

### PR-09 — Reader-retention outcome

The product evaluates retention across the reader journey: stop reason at title/opening, promise clarity without exhausting payoff, new information per section, cadence of concrete facts/cases/companies, transitions that earn the next section, absence of repetitive restatement, and completion payoff. Curiosity must be concrete and paid off.

### PR-10 — Originality / anti-plagiarism

Financial must not reuse another source’s distinctive structure or phrasing as its own. Required method:
- normalize research into claims/notes/evidence before drafting;
- draft primarily from notes + blueprint, not source paragraphs;
- quote/attribute distinctive language when legitimately necessary;
- independently reconstruct information from understanding;
- compare suspicious/distinctive passages against material sources before PASS;
- treat close paraphrase/patchwriting as REVISE;
- never claim zero plagiarism solely from same-chat review.

### PR-11 — Natural authorial prose

Natural prose comes from material, stance, concrete evidence, story architecture and voice evidence—not slang injection, fixed sentence-length variation, phrase substitution, AI-detector optimization or a generic humanizer. Generic scaffolding is a diagnostic signal only when clustered/unearned and replacing new information.

### PR-12 — Publication Fitness gate

Every current-architecture long-form candidate passes exactly:
`FACT_INTEGRITY`, `RETENTION`, `COMPANY_GROUNDING`, `STRUCTURE_NUMBERING`, `ORIGINALITY`, `AUTHORIAL_STYLE`, `COMPLIANCE`, `PAYOFF`.

Each gate cites text location/excerpt/finding. MAJOR/CRITICAL findings block PASS. REVISE needs explicit repair actions. Originality requires source-compared `OriginalityEvidence`; a same-chat impression is not evidence of zero overlap.

Research Audit separately validates the admitted private brief semantically; syntactic module completion with placeholder evidence is not enough.

The writing workflow distinguishes INTERNAL_DELIVERY_READINESS from PUBLICATION_CERTIFICATION. A same-chat reviewer may mark all eight internal text-evidence gates PASS for draft Word export only when the exact persisted DRAFT bytes were reread and bound by SHA-256; the resulting delivery is explicitly uncertified and must retain independent editorial quality OPEN. Without this explicit scope, CHAT_SELF_REVIEW remains forbidden from issuing a publication PASS. Independent publication certification still requires a separate authenticated reviewer of exact draft bytes. A failed gate must REVISE or FAIL, never be waived to finish the workflow.

### PR-13 — Focused internal pass architecture and portfolio orchestration

One Financial owner uses one internal pass graph and one existing 10-stage Article Graph. Internal passes are work responsibilities, not a second business state machine.

The shared research spine executes once:
\`KNOWLEDGE_RECALL -> RESEARCH_DISCOVERY -> RESEARCH_ADVERSARIAL -> PRIVATE_RESEARCH_SYNTHESIS -> THESIS_ADJUDICATION\`.
The Research Audit boundary must then admit actual evidence before any publication branch begins.

Every requested long-form product executes its own branch:
\`STORY_ARCHITECTURE -> HEADLINE_ADJUDICATION -> DRAFT_GENERATION -> READER_RETENTION_AUDIT -> EDITORIAL_TRIM -> {ORIGINALITY_AUDIT, FACT_INTEGRITY_AUDIT, STYLE_AUDIT} -> FINAL_SYNTHESIS\`.
Deep and Broad must receive separate product-scoped inputs, story blueprints, headline decisions, drafts, reviews and final candidates. Broad is not produced by shortening Deep.

When the output contract includes the interaction pack, it receives a separate branch:
\`PLATFORM_INTERACTION_ADAPTATION -> PLATFORM_INTERACTION_AUDIT\`.
It is rewritten from the shared audited evidence and platform context, not copied or truncated from either long-form product.

The 16 pass contracts, dependencies, scope partition and mapping to existing business stages are owned by \`financial_writing_agent.writing_kernel\`. The native ChatGPT model remains the active LLM orchestrator. Python callback adapters make the contract testable but do not prove that a live model executed the passes or that their content is correct.

Pass names, a valid DAG, callback outputs and synthetic tests are not execution evidence. A real run must produce and reread each required product-scoped work artifact, bind it to the correct existing stage, stop on missing dependencies, and route failed work to the earliest affected stage. Research Audit must precede every publication branch.

User-authored requirements must cross every applicable product scope. Do not reject an admitted free-text requirement merely because its ID is absent from a hard-coded whitelist. Check stage satisfaction receipts and requirement digest; unknown semantics remain UNVERIFIED, not auto-PASS. A requirement first due at DELIVERY may be pending while Word is built, but final stage transition still requires satisfaction and source readback.

### PR-14 — Platform/output portfolio

New ordinary work defaults to \`PORTFOLIO + WORD_FILE_ONLY\`: \`FINANCE_DEEP_DOCX\`, \`FINANCE_BROAD_DOCX\`, \`PLATFORM_INTERACTION_PACK_DOCX\`, \`AUDIT_DOCX\`. Historical product meanings remain immutable.

Portfolio execution reuses one audited research spine while preserving separate reader promises, story architecture, title, draft and review for each requested product. An output not present in the canonical task contract must not be fabricated; a required output must not be silently omitted.

The private research brief is mandatory internal quality evidence. It may also be rendered/delivered as a private document when the user requests it, but the quality contract does not depend on publication of that internal artifact.

### PR-15 — Delivery and mechanical QA

Word outputs pass formatting, artifact, render and current-resource availability checks. Mechanical success never substitutes for semantic publication fitness.

### PR-16 — Evolution and promotion

Financial-owned evolution follows:
`problem/evidence -> cognition -> candidate alternatives -> DecisionEnvelope/root-scope admission -> evolution disposition -> regression/eval -> candidate branch/PR -> controlled promotion -> production reread -> live observation -> keep/repair/rollback/retire`.
One article may create a domain candidate, not universal truth. Cross-topic reusable method changes are evaluated and versioned within Financial's existing maintenance authority; no upstream parent action is required.

### PR-17 — Multi-agent is conditional, not default

Separate executors are justified only when tool access, permissions, context, output contract, independence requirement or measured parallelism benefit materially differs. Otherwise use one Financial owner with focused passes.

### PR-18 — Post-evolution historical resume compatibility

Before materially continuing an article state that predates the current semantic quality generation:
- apply the owner-native resume compatibility admission;
- ordinary continuation intended to satisfy current quality must create a current-kernel successor/replay (`CURRENT_SUCCESSOR_REQUIRED`);
- explicit historical/provenance-only continuation may preserve historical semantics (`HISTORICAL_PROVENANCE_ONLY`) but cannot inherit current DecisionEnvelope/StoryBlueprint/PublicationFitness assurance;
- do not retroactively require the private-research marker on already-created states; new tasks receive it by default;
- never rewrite old receipts/state to simulate current evidence.

This requirement preserves both continuity and provenance without silently equating semantic generations.

## 4. Acceptance evidence — Functional requirement map

| Requirement | Executable/evidence surface |
| --- | --- |
| Material decision rigor | `cognition_governance.py::DecisionEnvelope`, tests |
| Mandatory private research | `private_research.py`, `current_admission.py`, private-research tests/reference/eval |
| Search saturation | `SearchSaturation`, tests |
| Knowledge conflict discipline | `KnowledgeRecord`, `knowledge/METHOD_KNOWLEDGE_CATALOG.json` |
| Value-chain-first research | ResearchPackage coverage map + research rules/evals |
| Historical resume compatibility | `resume_compatibility.py`, trajectory regression |
| Story architecture | `story_quality.py::StoryBlueprint`, tests |
| Research/publication separation | `ValueChainScopeDecision`, PrivateResearchBrief publication-distillation, held-out replay |
| Event→company transmission | `CausalTransmission`, EVENT_TO_COMPANY regression |
| Deep no default word ceiling | StoryBlueprint validator + regression |
| H1 numbering | StoryBlueprint + structure tripwire |
| Company-grounded sections | SectionBlueprint/CausalTransmission + live replay |
| Retention/payoff | PublicationFitness text-evidence gates + live/user observation |
| Originality | OriginalityEvidence + source-overlap review + replay |
| Style/anti-AI | scaffold tripwire + evidence-backed style critic |
| Internal pass isolation | `writing_kernel.py`, DAG tests |
| Financial compliance | deterministic/semantic finance checks |
| Word delivery | DOCX/render/mechanical tests |
| Evolution | owner lifecycle/problem-action admission/evolution index |

## 5. Failure and recovery semantics

- historical pre-current-kernel material resume under current-quality intent -> create current-kernel successor/replay;
- missing/invalid/digest-mismatched PrivateResearchBrief on marker-enabled task -> RESEARCH cannot advance / RESEARCH_AUDIT revises;
- missing material research coverage -> RESEARCH;
- thesis selected before coverage/adversarial/private-research synthesis -> RESEARCH;
- stale material market-cap/role/catalyst data -> RESEARCH;
- DecisionEnvelope admission failure -> do not execute the material decision;
- Deep selective omission without full scope accounting -> EDITORIAL;
- EVENT_TO_COMPANY section without full causal transmission -> EDITORIAL;
- story numbering/company grounding failure -> EDITORIAL;
- hook/retention/payoff failure -> EDITORIAL/TITLE/DRAFT as narrowest repair;
- suspicious source overlap/patchwriting -> DRAFT;
- current fact/causal boundary failure -> RESEARCH/DRAFT depending cause;
- generic scaffolding cluster -> semantic STYLE review, not automatic authorship verdict;
- semantic audit without excerpt/location evidence -> audit invalid;
- mechanical Word failure -> DELIVERY;
- upstream material change invalidates dependent downstream PASS evidence.

## 6. Financial-native cognition and decision contract

Financial owns and executes the complete goal-recovery, decision, failure-diagnosis, counterexample, method-comparison, execution and verification procedure itself. No external controller or Host is invoked or consulted for operating authority. Material problems require micro diagnosis, macro goal/topology alignment, governing-assumption challenge and external research proportional to risk. Systemic problems compare root layers and falsifiers before a lawful repair. Same-model decisions are not independent product proof.

## 7. Financial-owned evolution contract

Financial owns finance-specific and reusable method promotion for its own system. A correction is evidence, not authority to copy the proposed fix. Reusable changes require causal comparison, negative tests, exact-head candidate validation and production/product readback. No external parent upcall is an allowed operating path.

## 8. Explicit non-goals

- no buy/sell/timing/target/position guidance;
- no claim of literal exhaustive internet crawling;
- no automatic promotion of user suggestions into rules;
- no universal story template or stock-scoring formula;
- no research-directory-as-article mandate;
- no generic-draft-then-humanizer architecture or AI-detector optimization;
- no claim same-model critics are independent;
- no cosmetic multi-agent role multiplication;
- no default Deep word-count ceiling;
- no rewriting historical state/receipts to fit the current architecture.

## Current authoritative runtime vs quality evidence (2026-10-18 review)

Current `main` contains the Financial Writing 1.0.3 business implementation and CI #1414 succeeded at `f261367eb480c884880890513752afc77d1ef916`. Historical research briefs explicitly bound to contract 1.0 remain valid under their own task markers; every **new** current-admission task uses PrivateResearchBrief 1.1.

This is a source/contract implementation fact, **not** a general editorial-quality or audience-value certification. `evals/quality_regression.json` currently marks GENERAL_EDITORIAL_QUALITY as `NOT_READY__HELDOUT_DIVERSITY_INSUFFICIENT` and PERSONALIZED_WRITING_DNA as `NOT_READY`; the v3 cross-border successor remains at RESEARCH. The full product-quality assurance level is tracked in `evals/FINANCIAL_WHOLE_SYSTEM_OWNER_REVIEW_20261018.md` and will advance only with actual heldout/current article evidence.

## 9. Product completion criteria

The 1.0.3 candidate is promotion-eligible only when:
1. product requirements, architecture, execution contract, Skill/bindings and code agree;
2. new tasks bind `private_research_contract_version=1.1` by default;
3. RESEARCH cannot advance without both DecisionEnvelope and valid PrivateResearchBrief;
4. private research is digest-bound, tamper-detected and invalidated on revision to RESEARCH;
5. private-research structural tests cover required modules, evidence refs, NOT_MATERIAL reasoning and coverage gaps;
6. existing cognition, StoryBlueprint, selective-scope, event-company, resume-compatibility and PublicationFitness tests remain green;
7. wheel smoke verifies packaged private-research runtime/reference availability;
8. existing owner/routing/delivery/compliance and held-out tests remain green;
9. production CI and contradiction scan pass;
10. live Financial tasks observe whether the mandatory private layer improves company coverage, catalyst/market-role reasoning and article distillation without turning the public article into a research dump.

## 10. Standalone Financial connection and independent acceptance (2026-11-11)

Current operating Skill: `skills/financial-writing-agent/SKILL.md`; manifest `config/FINANCIAL_MANIFEST.json`; Financial-only provider entry `financial_writing_agent/standalone_runtime.py`. It requires externally verified user authorization, actual Git state and artifact bytes, provider CAS and second readback. This is an adapter, not an assertion that a native ChatGPT plugin is installed. Retired integration stubs are removed from the current Financial tree; only Financial-owned runtime assets remain.

Full product readiness still needs genuine source-to-claim and requirement-to-paragraph evidence, a current article's PrivateResearchBrief, separate Deep/Broad/interaction/audit production, live DOCX readback and independently assessed reader/owner result. `GENERAL_EDITORIAL_QUALITY` and `PERSONALIZED_WRITING_DNA` remain NOT_READY until observed, regardless of CI.

## Financial system-governance acceptance addendum (owner scope: 2026-11-12)

This addendum evaluates intrinsic Financial goal/workflow/method governance, **not real article content production**.

- Original user demand and latest corrections control a task's active requirements. Active `TaskRequirement.source_kind` must be explicit; no model/default promotion to USER_EXPLICIT. At the connected action port, the user role, original text, quote and source digest must be independently read from a trusted provider. User suggestion, implementation idea, issue report, model inference and UNKNOWN do not become requirements by mere mention.
- Nonbinding intents remain actionable, visible, task-owned evidence. They must not mutate the authoritative requirement digest or stage graph unless separately adjudicated as a binding user correction.
- Existing requirements allow CREATE/REPLACE/RETIRE with source, revision, immutable historical events and earliest-affected-stage replay; ambiguous simultaneous retire-and-upsert of one ID fails closed.
- Existing Financial method knowledge supports query, candidate add, revision staging, discard, evidence-grounded promotion, challenge, retirement, restore-as-candidate and independently verified impact closure. A method change cannot erase the previous record, silently assume legacy adoption labels are proof, or close without observing all affected stage-evidence refs.
- Systemic diagnoses and method choices are revisited when counterexamples defeat them. Decisions and executions share one Financial owner and explicit independent assurance levels; native client activation and real editorial acceptance remain distinct from machine test results.

The corresponding architecture/evidence source is `evals/FINANCIAL_GOAL_METHOD_GOVERNANCE_AUDIT_20261112.md`.

## Financial system acceptance correction (2026-11-12)

The engineering test suite is a necessary but **insufficient** acceptance gate. A valid original user source hash does not prove that an LLM-derived requirement matches the actual user's intent. Requirement mutations are blocked unless their exact change digest is confirmed through a provider-attested owner semantic decision; nonbinding ideas stay nonbinding. The independent Financial client, real user-message provider, real GitHub CAS, independent reviewer and one-main branch hygiene are external release gates; their absence means NOT_READY, even with 100% engineering tests. See `evals/FINANCIAL_INDEPENDENT_ACCEPTANCE_REAUDIT_20261112.md` and `financial_writing_agent/acceptance_gates.py`. Current private ChatGPT Skill creation is not proof of actual plugin installation.

Before claiming completion or asking the user whether a requirement was remembered, `standalone_runtime.observe_article` must expose the current per-requirement progress projection from the single owner state. It includes the original user instruction, stage due, admitted evidence, pending stage work and missing Word outputs. It never promotes an execution receipt or mock review into semantic/user acceptance.
