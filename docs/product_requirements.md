# Financial Writing Agent — Product Requirements

Status: `1.0.3_CANDIDATE`
Version: `1.0.3-candidate`
Date: `2026-10-16`
Owner: `DOMAIN:financial_writing`
Parent governance: `D1traverser-debug/universal-agent-os@main`

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

A fresh session can select Financial Writing directly. Financial creates and owns article identity/state. UAOS supplies hosted common governance but is not a mandatory business proxy.

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

The brief is the private analytical workbench, not the public article. It must include every required module from `references/private_research.md`, each marked `APPLICABLE` or `NOT_MATERIAL` with explicit reasoning. For ordinary A-share thematic/company work where market behavior matters, the brief covers as applicable:
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

### PR-13 — Focused internal pass architecture

One Financial owner uses:
`KNOWLEDGE_RECALL -> RESEARCH_DISCOVERY -> RESEARCH_ADVERSARIAL -> PRIVATE_RESEARCH_SYNTHESIS -> THESIS_ADJUDICATION -> STORY_ARCHITECTURE -> DRAFT_GENERATION -> READER_RETENTION_AUDIT -> EDITORIAL_TRIM -> {ORIGINALITY_AUDIT, FACT_INTEGRITY_AUDIT, STYLE_AUDIT} -> FINAL_SYNTHESIS`.
Passes have least-context responsibilities and are not a second business state machine.

### PR-14 — Platform/output portfolio

New ordinary work defaults to `PORTFOLIO + WORD_FILE_ONLY`: `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX`, `AUDIT_DOCX`. Historical product meanings remain immutable.

The private research brief is mandatory internal quality evidence. It may also be rendered/delivered as a private document when the user requests it, but the quality contract does not depend on publication of that internal artifact.

### PR-15 — Delivery and mechanical QA

Word outputs pass formatting, artifact, render and current-resource availability checks. Mechanical success never substitutes for semantic publication fitness.

### PR-16 — Evolution and promotion

Financial-owned evolution follows:
`problem/evidence -> cognition -> candidate alternatives -> DecisionEnvelope/root-scope admission -> evolution disposition -> regression/eval -> candidate branch/PR -> controlled promotion -> production reread -> live observation -> keep/repair/rollback/retire`.
One article may create a domain candidate, not universal truth. Common/cross-domain changes go to UAOS.

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

## 6. Cognition inheritance contract

Financial inherits the UAOS problem-response floor and internal-orchestration method while keeping business decisions local. Every detected defect/unreliable outcome activates micro diagnosis, macro/topology alignment, governing-assumption challenge and external research. Material/systemic problems add competing hypotheses/counterexamples and verification proportional to risk. Declaring inheritance is not operational proof.

## 7. Evolution inheritance contract

Financial owns Financial writing promotion; UAOS owns common/cross-domain promotion. Feedback first becomes evidence, then is classified and compared with alternative diagnoses/repairs. Permanent rule/architecture changes require reproducible evaluation, owner-scoped promotion and post-promotion observation.

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
