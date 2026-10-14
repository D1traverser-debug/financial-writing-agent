# User Feedback System Impact — Reader Value, Decision Utility & Platform Products — 2026-10-15

Status: `CANDIDATE_RESEARCH_COMPLETE__IMPLEMENTATION_PENDING`
Scope: Financial Writing domain product/rules/runtime
Trigger article: `huangjiu-high-end-channel-20261015`
Evidence: `workspaces/articles/huangjiu-high-end-channel-20261015/FEEDBACK_2026-10-15.md`

## M0 — User outcome and observed failure

The delivered article passed the existing workflow but the user identified material publication-quality defects: source/provenance leakage in public copy, recognizable LLM rhetorical scaffolding, weak headline/H1/opening/continuation pull, low-information company comparison, abrupt H1→H2 transitions with no image-safe lead zone, insufficient information density/navigation, and a product contract that does not model the user's three-surface publishing portfolio.

The desired outcome is not covert investment advice. It is evidence-bounded decision utility: a finance reader should be able to understand which listed company has purer exposure, nearer/faster realization, stronger economic sensitivity, harder evidence, and what could change that comparison, without buy/sell/timing/target-price instructions.

## M1 — Micro diagnosis

1. `references/delivery.md` allows natural in-text source attribution when identity is material. In practice, drafting used source names to demonstrate provenance, exposing the research path in publication prose.
2. `references/style.md` and the deterministic template guard detect only obvious phrase/template clusters; they do not fully control title/H1 mold repetition, noun-heavy abstraction, or sentence/paragraph role monotony.
3. `references/hooks.md` requires title pools and early orientation but treats the first three sentences as only diagnostic. The delivered article therefore satisfied formal candidate-count/diversity requirements while still producing a weak cold-reader opening.
4. Existing company comparison rules permit comparison to be important but do not force a named, evidence-bounded comparative verdict. Generic conditional conclusions can therefore pass.
5. `check_payload_navigation` does not fail an immediate H1→H2 sequence; the user's illustration workflow needs a substantive H1 lead paragraph before lower-level headings.
6. `DistributionMode` and `ArtifactKind` model only Deep/Broad long-form plus audit. The user's standalone short interaction content is absent from the product contract.

## M2 — Macro / product-topology alignment

The Financial product is meant to convert one researched topic into publishable content with distinct reader jobs. The actual user journey has three output products sharing one audited evidence base:

- acquisition long-form: broad finance reach/follower acquisition;
- deep finance/review long-form: complete decision-useful analysis for self-review and finance communities;
- short interaction pack: standalone image-text / 微头条 / 动态 copy for engagement and follower growth.

Treating the third product as an ad-hoc post-processing request would leave product routing, acceptance, audit and delivery incomplete. This feedback therefore reveals a missing product requirement, not only a prose defect.

## M3 — Governing-assumption challenge

Assumption challenged: “If research is broad, titles have candidate diversity, and Deep names all material companies, publication quality follows.”

Counterevidence from the trigger article: the workflow had broad research, named companies, 8–12 title candidates and a formal audit, yet publication copy still leaked sourcing, repeated rhetorical molds, lacked explicit company ranking logic, and had weak section-entry continuity. Presence/completeness checks are necessary but not sufficient; reader value and decision utility require stronger acceptance semantics.

A second assumption is challenged: “Broad is merely a compressed Deep.” The user's publishing workflow assigns Broad an acquisition job and separately needs short interaction outputs. Those are distinct products and should not be represented by compression alone.

## M4 — External research used in repair design

### Headline / reader funnel
- Qiu & Golman (2024), >100,000 WeChat news articles: salient information gaps, importance and surprisingness predict consumption; more curiosity-driven clicks do not automatically improve deeper engagement. Candidate implication: optimize click + payoff integrity, not suspense alone.
- Scientific Reports registered report/meta-analysis (2025), 8,977 headline experiments: headline concreteness has a curvilinear relationship with CTR. Candidate implication: avoid both vague teaser titles and titles that completely close the information gap; combine concrete hard information with one material unresolved payoff.
- Current Toutiao creator rules explicitly penalize exaggerated, hidden-critical-information, misleading or content-mismatched titles and classify logically disjoint/repetitive prose as low quality. Candidate implication: stronger hooks must remain information-bearing and faithful.

### Natural authorial prose / LLM residue
- Shaib et al., EMNLP 2024: generated text uses syntactic templates at a higher rate than human-reference text. Candidate implication: anti-template audit must operate beyond banned phrases and look for repeated sentence/section moves.
- Related linguistic work on LLM writing reports lower structural variation and frequent noun-heavy/nominalized or coordination-heavy constructions. Candidate implication: “去AI味” should mean evidence-bounded authorial selectivity, varied argument roles and earned progression—not slang, errors or detector gaming.

### Company comparison
- CFA company/industry/financial analysis methods distinguish industry-wide from company-specific drivers and compare business model, revenue drivers, pricing power, margins, operating leverage/sensitivity and peer position. Candidate implication: material-company coverage should culminate in topic-specific comparison across exposure/purity, realization stage/speed, sensitivity, evidence certainty and adverse variables, while remaining non-actionable.

### Platform product design
- Toutiao and Baijiahao content rules penalize clickbait, title-body mismatch, low-information titles and low-quality stitched/repetitive content. The short interaction product should therefore be independently rewritten from the same evidence base rather than copied as a truncated long-form excerpt.

## M5 — Alternatives

### Alternative A — Local article rewrite only
Mechanism: revise this one Huangjiu article and keep current rules/product contract.
Failure mode: same defects remain admissible on future topics; the workflow may again report PASS despite poor decision utility/source privacy/platform fit.

### Alternative B — Add rigid banned phrases and a fixed headline/opening formula
Mechanism: ban common LLM phrases and force one first-three-sentence template.
Failure mode: creates a new recognizable template, overfits one complaint, and suppresses topic-specific authorial choices. It can also incentivize surface synonym replacement without better reasoning.

### Alternative C — Layered acceptance contract (selected)
Mechanism:
1. publication-source privacy with provenance retained only in research/audit;
2. research-backed anti-template/authorial-progression gate across title/H1/body;
3. qualified-click funnel requiring the opening three sentences collectively to establish hard fact/anomaly, finance-wide consequence, and a real unresolved payoff (flexible order/wording);
4. named company decision map with evidence-bounded comparative verdict and change conditions;
5. mandatory substantive H1 lead/bridge before H2/H3, creating an image-safe insertion zone;
6. stronger information-density/numbered-navigation audit;
7. three-product platform contract including a standalone interaction pack;
8. deterministic/regression checks for mechanically testable parts and semantic audit for judgment.

Failure mode: added contract complexity and more acceptance work. Mitigation: reuse the existing single workflow/evidence base, add one companion output rather than a second runtime/controller, and keep semantic dimensions topic-specific rather than fixed scoring weights.

Selected: Alternative C.

## M6 — Generalization scope and counterexamples

Generalize domain-wide:
- source-provenance privacy in publication surfaces;
- anti-template/argument-progression requirements;
- reader-funnel information value;
- evidence-bounded comparative company decision utility when multiple material companies exist;
- H1 lead/image-safe bridge when lower-level headings follow;
- platform product routing/packaging.

Do not generalize:
- Huangjiu-specific companies, metrics or ranking dimensions;
- mandatory stock comparison for topics with no material listed-company differentiation;
- one fixed headline syntax or one fixed three-sentence wording;
- requirement that every article contain H2/H3 when reasoning is genuinely sequential.

## M7 — Acceptance / regression targets

Candidate implementation must prove at least:
1. source-leak scanner rejects publication framing such as “XX研报指出/据XX报道/公开资料显示” while research/audit may retain exact provenance;
2. title/H1/body template guard catches repeated rhetorical molds without banning isolated normal phrases;
3. an H1 immediately followed by H2/H3 fails; H1→substantive lead/body→H2 passes;
4. multi-company Deep audit requires a named evidence-bounded comparative verdict, not only generic “whoever achieves X…” statements;
5. routing maps 微信公众号 to dual-role long-form, 企鹅号 to broad acquisition, 韭研公社/东方财富 to Deep;
6. Broad and DUAL required outputs include a standalone platform interaction pack; Deep-only does not;
7. short interaction pack is an independent rewrite from the audited evidence base and not a copied long-form excerpt;
8. product requirements/architecture/rule ownership/audit/delivery references all agree on the three-product contract;
9. existing owner identity/state/single-controller invariants remain unchanged.

## Assurance boundary

External research validates repair direction but is not authority by itself. This record is a candidate until implementation, regression evidence, owner-appropriate CI/promotion, production reread and later live-user observation support KEEP. Same-chat evaluation remains self-attested and is not independent certification.
