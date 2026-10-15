# Financial Writing Agent — Architecture

Version: `1.0.0-candidate`
Date: `2026-10-15`
Status: `CANDIDATE_REBUILD`

## 1. Product boundary

Financial Writing is one domain/business owner under UAOS. UAOS owns common governance, cognition/evolution method, cross-domain authority and parent continuity. Financial Writing owns article identity/state, financial research semantics, writing architecture, output contracts, domain knowledge/evolution evidence and delivery.

The rebuild keeps these invariants:
- one Financial business owner and one article state authority;
- no parent/child task-id equality requirement;
- historical article states/receipts and historical distribution-mode semantics remain immutable provenance;
- no mandatory live UAOS proxy for normal Financial work;
- compliance, evidence integrity and owner-controlled mutation remain fail-closed.

Everything else in the writing/review path is replaceable when evidence supports a better design.

## 2. Why 1.0 rebuilds the old writing kernel

The prior system accumulated many correct prose/research rules but allowed the same execution context to draft and then certify itself with broad PASS fields. A live cross-border-ecommerce article exposed the failure: weak hook execution, missing requested numbering behavior, detached company analysis, throat-clearing/generic scaffolding, suspected source-shaped phrasing, weak retention/completion design and an editorial audit that still marked every reader/style dimension PASS.

The root problem is therefore not simply missing rules. It is a topology problem:
- research completeness, story design, prose generation and quality judgment were insufficiently isolated;
- rules were richer than their admission/evidence mechanisms;
- same-context review could emit labels without text-level proof;
- style/retention/originality were treated mainly as prose guidance instead of first-class output properties;
- adding more rules increased writer context load and risked making prose more synthetic.

1.0 replaces rule stacking with an evidence-driven cognition/decision/execution/fitness architecture.

## 3. Two-level execution architecture

### 3.1 Stable business lifecycle

The external/domain business lifecycle remains compact:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

This lifecycle owns recovery, artifact identity, invalidation and completion. It is deliberately not expanded into a stage for every cognitive or editorial action.

### 3.2 Internal writing kernel

Inside those business stages, `financial_writing_agent/writing_kernel.py` defines focused passes:
1. `KNOWLEDGE_RECALL`
2. `RESEARCH_DISCOVERY`
3. `RESEARCH_ADVERSARIAL`
4. `THESIS_ADJUDICATION`
5. `STORY_ARCHITECTURE`
6. `DRAFT_GENERATION`
7. `READER_RETENTION_AUDIT`
8. `EDITORIAL_TRIM`
9. `ORIGINALITY_AUDIT`
10. `FACT_INTEGRITY_AUDIT`
11. `STYLE_AUDIT`
12. `FINAL_SYNTHESIS`

These are work passes, not independent business controllers or separate article identities. They may be executed by the same model/context or by distinct executors when available, but assurance must match evidence. Same-model passes are structured challenge evidence, never independent certification.

Each pass has a narrow purpose, declared inputs/outputs and forbidden jobs. In particular, drafting is forbidden from self-certifying quality or silently changing the governing thesis.

## 4. Six system layers

### Layer A — Cognition

The cognition layer builds the best available model of the topic before writing:
- recall prior earned knowledge;
- classify stable, operating, ephemeral, method and failure-pattern knowledge;
- map the complete material value chain before thesis selection;
- map the company universe across the chain;
- collect chronology, primary evidence and uncertainty;
- search for contradictions, missing nodes and disconfirming cases;
- separate fact, mechanism, interpretation and unresolved questions.

Prior knowledge accelerates discovery but never waives current value-chain coverage or current-fact revalidation.

### Layer B — Decision

Material judgments use `DecisionEnvelope` from `cognition_governance.py`.

A material decision cannot be admitted unless it preserves:
- objective and operation scope;
- evidence from more than user assertion alone;
- relevant external method evidence;
- challenged assumptions;
- at least two credible alternatives;
- advantages, failure modes, fit and misfit for each candidate;
- counterexamples/adversarial evidence;
- explicitly rejected paths;
- selected candidate and rationale;
- search-saturation evidence;
- verification plan;
- remaining unknowns;
- knowledge/evolution disposition.

Mechanical actions do not require a heavyweight deliberation envelope. They use deterministic checks. This prevents governance bloat while making judgment-bearing operations inspectable.

### Layer C — Execution / story construction

`StoryBlueprint` is the required bridge between audited thesis and prose. It is not an outline shell; it describes the reader journey.

A blueprint must define:
- real reader job and starting state;
- article promise and central question;
- author stance/selectivity;
- chosen narrative engine;
- a concrete opening anchor;
- the information gap opened for the reader;
- early payoff and deliberately preserved later payoff;
- explicit contiguous Chinese H1 numbering;
- section-level reader question;
- genuinely new information per section;
- named company/case anchors for material explanatory sections;
- value-chain coverage;
- section payoff and bridge/open loop to the next section;
- ending payoff;
- voice evidence.

The architecture deliberately catalogs multiple story forms rather than promoting one universal template: hard anomaly, company conflict, reversal, mystery, system map, consequence chain, character/case and timeline escalation are legal engines. WSJ/nut-graf, five-box and hourglass are method knowledge and candidate patterns, not mandatory shells.

### Layer D — Verification / publication fitness

Publication quality is governed by fitness gates rather than unsupported PASS labels.

Every publication candidate must produce text-level evidence for exactly these gates:
- `FACT_INTEGRITY`
- `RETENTION`
- `COMPANY_GROUNDING`
- `STRUCTURE_NUMBERING`
- `ORIGINALITY`
- `AUTHORIAL_STYLE`
- `COMPLIANCE`
- `PAYOFF`

Each gate records location, excerpt, finding and severity. MAJOR/CRITICAL findings mechanically block PASS. REVISE decisions require concrete repair actions.

Deterministic checks remain tripwires, not substitutes for semantic reading. Examples: numbered heading continuity, prohibited finance-action phrases, Word layout, repeated generic scaffolding clusters and source-provenance leakage.

### Layer E — Knowledge

Financial maintains two different reusable knowledge families:

1. Domain/topic knowledge: industry/value-chain structures, business relationships, company roles, policies/financials with freshness semantics.
2. Method knowledge: writing forms, research methods, architecture patterns, failure modes and evaluation methods learned from UAOS and external sources.

`knowledge/METHOD_KNOWLEDGE_CATALOG.json` records method knowledge with source, fit, misfit, adoption status and revalidation trigger. Cataloging is not promotion.

Knowledge flows:
`recall -> revalidate -> use as evidence/candidate -> observe outcome -> write back with provenance`.

Rules and architecture flow separately:
`evidence -> decision envelope -> candidate -> regression/eval -> owner promotion -> observation`.

This prevents knowledge acquisition from silently mutating governance.

### Layer F — Evolution and governance

Financial inherits UAOS governed evolution:
`problem/feedback -> research+reflection -> failure class -> candidate -> reproducible evaluation -> owner-scoped promotion -> production observation -> keep/rollback/retire`.

User feedback is high-weight evidence, not automatic truth. A user's desired outcome/observed failure may trigger a candidate immediately; the user's proposed implementation is evaluated alongside alternatives.

Cross-domain/common capability changes are upcalled to UAOS. Financial-owned research/writing/product rules remain Financial-owned.

## 5. Search breadth and saturation

"Search everything" is implemented as bounded, auditable saturation rather than an unverifiable claim of crawling the entire internet.

For material architecture/method/thesis decisions:
- search across materially different source families;
- include direct/supporting evidence and explicit counterexample/adversarial search;
- preserve each sweep and what new candidate/failure mode/counterexample it produced;
- do not stop on the first plausible answer;
- stop only after at least two consecutive sweeps produce no decision-changing candidate, failure mode, counterexample or changed decision, with remaining gaps recorded.

A new material discovery after convergence invalidates saturation and requires re-adjudication.

## 6. Research architecture

Research remains value-chain first.

Required order for normal thematic/company work:
`knowledge recall -> value-chain preflight -> universe recall -> evidence expansion -> adversarial search -> search saturation -> thesis competition -> company decision map -> research audit`.

Thesis selection before value-chain preflight is invalid. A late material value-chain node forces thesis retest.

Research may be much broader than the final publication. The publication can select; the research layer cannot claim completeness while silently excluding a material economic branch.

## 7. Deep vs Broad products

### FINANCE_DEEP

Deep is the complete finance/review product. For a thematic/industry article:
- all material value-chain classes must be represented in the story blueprint or explicitly resolved as non-material to publication;
- all material companies must be covered at the level needed to distinguish their economics;
- mechanisms should be grounded with named companies/cases instead of long detached industry exposition;
- company comparison must be evidence-bounded and non-actionable;
- there is **no default word-count ceiling**. Length follows materiality and reader progression. Compression requires explicit user/product need or evidence that material is redundant.

Deep may be long. Its control is information density and progression, not arbitrary character count.

### FINANCE_BROAD

Broad is a separate acquisition product, not a shortened Deep. It can select a smaller subset of the audited evidence but still requires a real story architecture, company grounding, retention/payoff and originality gates.

### Interaction pack

Short posts remain independent rewrites from audited evidence. They are not paragraph truncations or slang-added versions of long-form copy.

## 8. Reader retention architecture

Retention is treated as a sequence of reader decisions, not a title score.

The system evaluates:
- why a cold reader stops at the title/opening;
- what concrete question remains unresolved;
- whether early context gives enough value without giving away the whole article;
- where each section adds new information rather than repeating the thesis;
- whether technical explanation is periodically grounded by a company, case, contradiction, number or consequence;
- whether each section earns the next section through a bridge/open loop;
- whether the ending closes the article's promised question and yields a usable mental model.

Curiosity gaps are legal only when the article pays them off. Empty clickbait and withholding basic orientation fail the PAYOFF/RETENTION gates.

## 9. Company-grounded explanation

For material explanatory sections, the default unit is:
`economic change -> named company/case -> observable number/behavior -> mechanism -> contrast/counterexample -> implication/boundary`.

This is not a mandatory sentence order. It is a grounding obligation. A long abstract explanation with companies bolted on later is a review defect when company evidence exists and materially clarifies the mechanism.

## 10. Natural prose / anti-AI design

The system does not create a universal "humanizer" stage and does not optimize for AI detectors.

Natural prose comes from:
- material-specific author stance;
- concrete evidence;
- strong story architecture;
- selective omission;
- user-owned voice evidence when available;
- post-draft removal of unearned scaffolding and repetitive abstractions.

Patterns such as `不是X而是Y`, `值得关注`, `这意味着`, `问题在于`, `换句话说` are diagnostic signals. Isolated use is legal. Clusters that substitute for new information trigger semantic review.

The writer pass does not see every governance rule as generation instructions; governance is shifted into inputs, contracts and downstream fitness gates.

## 11. Originality / anti-plagiarism

Publication-source privacy never licenses plagiarism.

The operating method is:
1. research captures claims/evidence, not reusable source prose;
2. writer works primarily from normalized notes/evidence and story blueprint rather than source paragraphs;
3. distinctive source language is quoted/attributed when legitimately needed, otherwise rewritten from understanding;
4. originality audit compares suspicious/distinctive phrases or passages against material sources;
5. close paraphrase/patchwriting is a REVISE condition even when individual words were substituted;
6. the system never claims "zero plagiarism" without appropriate external evidence. Current same-chat checks are bounded originality review.

## 12. Assurance model

Assurance labels must not exceed evidence:
- deterministic code/test -> deterministic invariant evidence;
- same-chat semantic critic -> `CHAT_SELF_REVIEW`;
- distinct executor/provider with bound trace -> eligible for stronger independent evidence;
- user acceptance/performance -> live outcome evidence.

A configured reviewer role, prompt name or second pass is not independent merely because it has a different label.

## 13. Evolutionary fitness functions

Architecture invariants are protected with executable tests where possible:
- material decisions cannot omit alternatives/counterexamples/search saturation;
- knowledge with unresolved conflicts cannot be promoted as validated;
- Deep cannot carry a default word ceiling;
- Deep story blueprint cannot omit declared material value-chain classes;
- material explanatory sections need company/case anchors;
- H1 sequence labels must be explicit and contiguous;
- publication PASS requires all fitness gates with text evidence;
- MAJOR/CRITICAL findings block PASS;
- suspicious originality findings block PASS;
- writing-kernel dependencies must remain acyclic and complete.

Semantic properties that cannot be reduced safely to deterministic metrics remain evidence-backed critic gates rather than fake numerical formulas.

## 14. Multi-agent policy

Multi-agent is not the default architecture.

A specialist executor is justified only when one or more materially differ:
- tools/data access;
- policy/permissions;
- context required;
- output contract;
- assurance/independence requirement;
- parallelism produces measured value.

Otherwise use the single-owner multi-pass kernel. Any move to multi-agent must be eval-driven and preserve a single Financial business owner/adjudicator.

## 15. Recovery

Any REVISE/FAIL finding points to the narrowest upstream invalidation target:
- fact/evidence defect -> RESEARCH;
- thesis/coverage defect -> RESEARCH/EDITORIAL;
- story architecture/retention defect -> EDITORIAL/TITLE;
- prose/originality/style defect -> DRAFT;
- Word/render defect -> DELIVERY.

Repair must re-run all downstream affected fitness gates. A previous PASS is invalid once its input artifact changes materially.

## 16. Completion definition

A new-architecture article is complete only when:
- value-chain-first research and adversarial search are complete or explicitly bounded;
- material decisions have admitted Decision Envelopes;
- story blueprint satisfies product-mode obligations;
- required publication artifacts exist;
- every publication candidate passes all eight evidence-backed fitness gates;
- deterministic/mechanical/Word checks pass;
- state/artifact identities reconcile;
- reusable knowledge candidates and evolution impact are classified;
- assurance is reported accurately.

Green documentation alone is never completion evidence.
