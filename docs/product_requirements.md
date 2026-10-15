# Financial Writing Agent — Product Requirements

Status: `CANDIDATE_REBUILD`
Version: `1.0.0-candidate`
Date: `2026-10-15`
Owner: `DOMAIN:financial_writing`
Parent governance: `D1traverser-debug/universal-agent-os@main`

## 1. Product outcome

Financial Writing turns a finance topic, user materials and current evidence into publication-ready Chinese financial content that is:
- factually defensible and auditable;
- complete enough at research level to avoid missing material value-chain branches;
- company-grounded rather than detached industry exposition;
- structurally designed to earn reader continuation and completion;
- original in wording and construction rather than source-shaped patchwriting;
- recognizably authored rather than generic checklist prose;
- non-actionable and compliant for financial publication;
- delivered as verified Word artifacts when required;
- able to learn from prior work without treating memory, user feedback or old facts as unquestioned truth.

The governing outcome is not "satisfy the most rules". The governing outcome is **high-value, evidence-bounded writing that real readers can enter, follow, finish and use**.

## 2. Core design principles

1. User feedback is high-weight evidence, not automatic rule authority.
2. Learned knowledge is retained with provenance, scope, fit/misfit and revalidation conditions; it does not silently mutate rules.
3. Material judgments require deliberate comparison, counterexamples, external method evidence and a verification plan before execution.
4. Research completeness and publication selectivity are separate: research may be broad; publication may select.
5. The writer does not self-certify its own quality.
6. Semantic review must cite text-level evidence; naked PASS labels are insufficient.
7. Deterministic rules are used for invariants and tripwires, not as fake substitutes for semantic writing quality.
8. Multi-agent complexity is introduced only when evals and materially different responsibilities justify it.
9. Same-session critique is useful but remains `CHAT_SELF_REVIEW` unless distinct execution evidence exists.
10. Historical states/contracts remain immutable provenance.

## 3. Primary requirements

### PR-01 — Direct domain operation and ownership

A fresh session can select Financial Writing directly. Financial creates and owns article identity/state. UAOS supplies hosted common governance but is not a mandatory business proxy.

### PR-02 — Feedback classification before evolution

Any material user correction/rejection triggers problem cognition, but the system must distinguish:
- factual correction;
- user preference;
- article-specific requirement;
- recurring writing defect;
- method defect;
- architecture/control defect;
- proposed implementation idea.

The observed failure and desired outcome are evidence. A suggested fix is a candidate until compared against alternatives.

### PR-03 — Knowledge acquisition and durable reuse

Financial must retain useful learned knowledge in two families:
- topic/domain cognition;
- method/architecture/writing cognition.

Every reusable record needs provenance, category, scope, confidence/adoption state, conflicts or misfit where known and a revalidation condition. Retrieved knowledge seeds the next task but does not bypass current evidence.

### PR-04 — Value-chain-first research and broad search

For material thematic/company work, Research must:
1. recall prior relevant cognition;
2. enumerate all material value-chain classes before selecting the thesis;
3. map the relevant listed-company universe across those classes;
4. gather current evidence and chronology;
5. perform explicit disconfirming/counterexample search;
6. compare candidate causal explanations;
7. record unresolved gaps.

"Complete" means evidence-bounded coverage, not a claim that the entire internet was crawled.

For material method/architecture/thesis decisions, search may stop only after at least two consecutive materially different sweeps add no decision-changing candidate, failure mode, counterexample or changed decision. A later material discovery invalidates saturation.

### PR-05 — Decision Envelope for material judgments

Before executing a material judgment, Financial must be able to represent:
- objective;
- evidence;
- learned items/categories;
- challenged assumptions;
- at least two credible alternatives;
- candidate advantages/failure modes/fit/misfit;
- counterexamples;
- rejected paths;
- selected candidate and rationale;
- search-saturation evidence;
- verification plan;
- remaining unknowns;
- knowledge/evolution disposition.

Mechanical actions use deterministic checks and do not require full deliberation envelopes.

### PR-06 — FINANCE_DEEP is the complete finance product

For thematic/industry Deep work:
- declared material value-chain classes must all be represented in the publication architecture unless explicitly adjudicated non-material to publication;
- material companies must be covered sufficiently to explain distinct economics and evidence;
- material explanatory sections must use named company/case anchors when such evidence exists;
- H1 sections must use explicit contiguous Chinese numbering (`一、二、三、...`);
- mechanisms should be shown through company evidence rather than long detached scene-setting;
- company comparisons must be evidence-bounded and non-actionable;
- **there is no default word-count ceiling**. Remove redundancy; do not compress away material coverage merely to hit an arbitrary length.

### PR-07 — FINANCE_BROAD is selective acquisition, not shortened Deep

Broad can select a subset of the audited research based on reader acquisition value, but it must have its own story blueprint, retention path and payoff. It may not be generated by mechanically shortening Deep.

### PR-08 — Story Blueprint before prose

Substantive long-form publication requires a `StoryBlueprint` that records:
- reader job and starting state;
- article promise and central question;
- author stance;
- narrative engine selected from genuinely different candidate structures;
- concrete opening anchor;
- information gap, early payoff and later payoff;
- numbered section plan;
- per-section new information;
- named company/case anchors for material explanatory sections;
- value-chain classes covered;
- evidence refs;
- open loop/bridge and section payoff;
- ending payoff;
- voice evidence.

A story structure is selected to fit the material. Nut-graf, five-box, hourglass and similar forms are candidate methods, not universal templates.

### PR-09 — Reader-retention outcome

The product must evaluate retention across the entire reader journey, not just title/opening:
- stop reason at title/opening;
- promise clarity without giving away all payoff;
- new information per section;
- cadence of concrete facts/cases/companies;
- transitions that earn the next section;
- absence of repetitive thesis restatement;
- completion payoff that resolves the promised question.

Curiosity is useful only when concrete and paid off. Empty curiosity gaps or clickbait that increases clicks while reducing satisfaction fail the product objective.

### PR-10 — Originality / anti-plagiarism

Financial must not reuse another source's distinctive structure or phrasing as its own.

The required method is:
- normalize research into claims/notes/evidence before drafting;
- draft primarily from notes + blueprint, not source paragraphs;
- quote/attribute distinctive language only when legitimately necessary;
- independently rewrite information from understanding;
- compare suspicious or distinctive passages against material sources before PASS;
- treat close paraphrase/patchwriting as REVISE;
- never claim zero plagiarism solely from same-chat review.

### PR-11 — Natural authorial prose

Natural prose is produced from material, stance, concrete evidence, story architecture and voice evidence. It is not produced by slang injection, fixed sentence-length variation, phrase substitution or a generic humanizer.

Generic scaffolding (`值得关注`, `这意味着`, `问题在于`, `换句话说`, repeated `不是X而是Y`, etc.) is a diagnostic signal. A cluster that replaces new information or creates visible model rhythm requires semantic revision. Isolated legitimate use does not automatically fail.

### PR-12 — Publication Fitness gate

Every new-architecture publication candidate must pass exactly these evidence-backed gates:
- `FACT_INTEGRITY`
- `RETENTION`
- `COMPANY_GROUNDING`
- `STRUCTURE_NUMBERING`
- `ORIGINALITY`
- `AUTHORIAL_STYLE`
- `COMPLIANCE`
- `PAYOFF`

Every gate must cite text locations/excerpts and findings. MAJOR/CRITICAL findings block PASS. REVISE requires explicit repair actions. A rubric containing only labels is not acceptance evidence.

### PR-13 — Focused internal pass architecture

One Financial owner uses the internal pass DAG in `financial_writing_agent/writing_kernel.py`:
`KNOWLEDGE_RECALL -> RESEARCH_DISCOVERY -> RESEARCH_ADVERSARIAL -> THESIS_ADJUDICATION -> STORY_ARCHITECTURE -> DRAFT_GENERATION -> READER_RETENTION_AUDIT -> EDITORIAL_TRIM -> {ORIGINALITY_AUDIT, FACT_INTEGRITY_AUDIT, STYLE_AUDIT} -> FINAL_SYNTHESIS`.

Passes have least-context responsibilities and may not silently assume another pass's job. This is internal orchestration, not a second state machine.

### PR-14 — Platform/output portfolio

New ordinary work still defaults to `PORTFOLIO + WORD_FILE_ONLY`:
- `FINANCE_DEEP_DOCX`
- `FINANCE_BROAD_DOCX`
- `PLATFORM_INTERACTION_PACK_DOCX`
- `AUDIT_DOCX`

Historical `DUAL` and `FINANCE_BROAD` meanings remain immutable.

### PR-15 — Delivery and mechanical QA

Word outputs must pass formatting, artifact, render and availability checks. Mechanical success never substitutes for semantic publication fitness.

### PR-16 — Evolution and promotion

Financial-owned evolution follows:
`problem/evidence -> cognition -> candidate alternatives -> DecisionEnvelope -> regression/eval -> candidate branch/PR -> controlled promotion -> production reread -> live observation -> keep/repair/rollback/retire`.

One article may create a domain candidate, not universal truth. Cross-domain/common changes go to UAOS.

### PR-17 — Multi-agent is conditional, not default

Separate agents/executors are justified only when tool access, permissions, context, output contract, independence requirement or measured parallelism benefit materially differs. Otherwise the default is one Financial owner with focused passes.

## 4. Acceptance map

| Requirement | Executable/evidence surface |
| --- | --- |
| Material decision rigor | `cognition_governance.py::DecisionEnvelope`, tests |
| Search saturation | `SearchSaturation`, tests |
| Knowledge conflict discipline | `KnowledgeRecord`, `knowledge/METHOD_KNOWLEDGE_CATALOG.json` |
| Value-chain-first research | current ResearchPackage coverage map + research rules/evals |
| Story architecture | `story_quality.py::StoryBlueprint`, tests |
| Deep no default word ceiling | StoryBlueprint validator + regression |
| H1 numbering | StoryBlueprint + publication structure tripwire |
| Company-grounded sections | SectionBlueprint validator + live replay |
| Retention/payoff | PublicationFitness text-evidence gates + live/user observation |
| Originality | OriginalityEvidence + source-overlap review + replay |
| Style/anti-AI | diagnostic scaffold tripwire + evidence-backed style critic |
| Internal pass isolation | `writing_kernel.py`, DAG tests |
| Financial compliance | existing deterministic/semantic finance checks |
| Word delivery | existing DOCX/render/mechanical tests |
| Evolution | existing owner lifecycle/quality regression + new decision/eval evidence |

## 5. Failure/recovery semantics

- missing material value-chain coverage -> return to RESEARCH;
- thesis selected before coverage/adversarial search -> RESEARCH;
- DecisionEnvelope admission failure -> do not execute the material decision;
- story blueprint fails numbering/company/value-chain obligations -> EDITORIAL;
- hook/retention/payoff failure -> EDITORIAL/TITLE/DRAFT as narrowest repair;
- suspicious source overlap/patchwriting -> DRAFT;
- current fact/causal boundary failure -> RESEARCH/DRAFT depending cause;
- generic scaffolding cluster -> semantic STYLE review, not automatic authorship verdict;
- semantic audit without excerpt/location evidence -> audit invalid;
- mechanical Word failure -> DELIVERY;
- any upstream material change invalidates dependent downstream PASS evidence.

## 6. Explicit non-goals

- no buy/sell/timing/target/position guidance;
- no promise that the entire internet can be exhaustively crawled;
- no automatic promotion of user suggestions into rules;
- no universal story template;
- no universal stock-scoring formula;
- no generic-draft-then-humanizer architecture;
- no AI-detector optimization;
- no claim that same-model critics are independent;
- no cosmetic multi-agent role multiplication;
- no default Deep word-count ceiling;
- no rewriting historical states/receipts to fit the new architecture.

## 7. Candidate completion criteria

The rebuild is promotion-eligible only when:
1. architecture, product requirements, execution contract, skill/reference surfaces and packaged mirrors agree;
2. cognition decision, story blueprint, pass-DAG and publication-fitness unit tests pass;
3. existing historical compatibility, owner, routing, delivery and compliance tests remain green;
4. the rejected cross-border-ecommerce article is replayed as a negative case and the old defects cannot receive an unqualified PASS;
5. at least one held-out long-form case demonstrates the new design does not merely overfit cross-border ecommerce;
6. candidate CI passes;
7. authority-wide contradiction scan passes;
8. controlled promotion occurs through owner-appropriate GitHub workflow;
9. production authority and production CI are reread;
10. subsequent live user/article observation determines KEEP / further repair / rollback.
