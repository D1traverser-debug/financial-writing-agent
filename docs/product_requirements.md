# Financial Writing Agent — Product Requirements Baseline

Status: `CURRENT_DOMAIN_PRODUCT_REQUIREMENTS`
Version: `0.9.0`
Date: `2026-10-15`
Owner: `DOMAIN:financial_writing`
Parent common-governance method: `UAOS 2.4.5 / COMMON_CAPABILITIES 1.5.0`
Trigger evolution evidence: `evals/USER_FEEDBACK_SYSTEM_IMPACT_2026-10-15_READER_VALUE_PLATFORM_PRODUCTS.md`

## 1. Product outcome

Financial Writing turns a user brief, links/files/current-market evidence and scoped constraints into publication-ready Chinese A-share financial content with auditable research, explicit uncertainty, **evidence-bounded company decision utility**, non-actionable finance compliance, reader-value packaging, durable article state, review/recovery, Word delivery and evidence-bound learning.

The product must be directly usable after the user selects/inherits Financial Writing. UAOS supplies hosted common capabilities and parent guidance; it is not a mandatory per-turn business proxy.

## 2. Ownership boundary

- UAOS owns cross-domain selection/governance, shared product-engineering method, hosted cognition, common/cross-domain evolution and parent continuity.
- Financial Writing owns this product requirements baseline, architecture, article identity/state, business/output contract, workflow, research/editorial/style/platform/delivery rules, domain learning/evals and artifacts.
- `workspaces/articles/{task_id}/STATE.json::task_id` is the Financial article identity authority.
- A UAOS controller/router ID is never required to equal a Financial article ID.
- `references/reader_value.md` is the current domain rule for publication-source privacy, Natural Authorial Prose hardening, reader funnel, company-decision utility, image-safe section entry and the three-product publishing portfolio.

## 3. Primary user journeys

### PR-01 Direct start
A fresh chat can select Financial Writing directly and immediately operate under `DOMAIN:financial_writing`. No prior controller chat or parent-created article task is required.

### PR-02 New topic / full portfolio
When the user supplies a normal finance topic without narrowing outputs, Financial creates its own article identity/state and defaults to `PORTFOLIO`:
- `FINANCE_DEEP_DOCX`;
- `FINANCE_BROAD_DOCX`;
- `PLATFORM_INTERACTION_PACK_DOCX`;
- `AUDIT_DOCX`.

All content products share one audited research base but are independently structured for different reader jobs.

### PR-03 Exact continuation
Given an exact Financial article reference, resume from that article's current `STATE.json`; never infer or adopt a parent task ID as article identity.

### PR-04 Research and evidence
Research must maximize material topic/company recall, maintain source/evidence quality, separate fact/mechanism/interpretation/unknowns, avoid evidence-stage escalation and revalidate time-sensitive claims.

When two or more `MATERIAL` companies exist, Research must create a **Company Decision Map** using topic-specific dimensions. The map must state a current named relative verdict, its evidence and conditions that would change it.

### PR-05 Deep finance/review product
`FINANCE_DEEP_DOCX` serves 韭研公社、东方财富、微信公众号 and self-review. It must preserve material-company coverage and make economically useful distinctions explicit: business/concept purity, realization stage/speed, earnings sensitivity, evidence strength, adverse variables and other topic-specific dimensions.

It may say A is currently more direct/pure, B has faster realization, C has higher elasticity but weaker evidence, etc., when evidence supports it. It must not give buy/sell, timing, target price, position sizing or covert equivalents.

### PR-06 Acquisition long-form product
`FINANCE_BROAD_DOCX` serves 微信公众号、头条号、百家号、网易号、企鹅号 for qualified finance-domain acquisition.

Broad is not a shortened Deep article. It selects one to three strongest finance-wide information gaps and rebuilds the title, first three sentences, H1 sequence and completion payoff around them while preserving factual/uncertainty boundaries.

### PR-07 Interaction short-form product
`PLATFORM_INTERACTION_PACK_DOCX` serves 微信公众号贴图文字、微头条/动态、百家号动态、网易号动态.

Each item must be independently rewritten from the audited evidence base, with its own first-line hook, compact fact-to-finance consequence chain and natural interaction prompt. Truncating/copying a long-form paragraph is not accepted adaptation.

Financial Writing supplies text only; the user's later image creation/insertion remains outside the Financial image-generation workflow.

### PR-08 Publication-source privacy
Research/audit keep full provenance. Publication copy must not expose the material/research trail merely to prove sourcing (`XX研报指出`, `据XX报道`, `公开资料显示` and equivalents).

Attribution remains only when who said/announced/forecast something is itself part of the fact and removing the speaker changes the claim.

### PR-09 Natural Authorial Prose / anti-template quality
“去AI味” is defined as evidence-bounded authorial prose: varied argument roles, earned section progression, explicit selectivity, concrete actors/causality, calibrated uncertainty and control of recurring syntactic/rhetorical molds across title/H1/body.

Do not optimize for AI-detector evasion, slang or deliberate imperfections.

### PR-10 Reader funnel
The selected title should normally expose a concrete change/entity plus a finance-wide stake and leave one real unresolved payoff.

The first three complete sentences collectively must establish:
1. a hard fact/anomaly;
2. finance-wide consequence;
3. material unresolved payoff.

Order and syntax are flexible; the full answer need not be exhausted immediately.

Every H1 must be information-bearing. When lower-level headings follow an H1, a substantive lead paragraph must appear first so it both advances the reasoning and gives the user an image-safe insertion zone.

### PR-11 Review, delivery and recovery
Default channel remains `WORD_FILE_ONLY`. Required Word artifacts must pass semantic, mechanical and render QA before current-session availability is claimed.

A failed review persists a repair cursor, invalidates affected downstream work and resumes through owner lifecycle rather than free-form patching.

### PR-12 User correction / detected problem
Every detected problem — including user correction/rejection, failed/degraded output, contradiction, repeated repair or unreliable goal satisfaction — triggers the hosted problem-response floor:
1. micro diagnosis;
2. macro goal/topology/architecture alignment;
3. governing-assumption challenge;
4. relevant external research.

### PR-13 Domain evolution
One article may create an evidence candidate, but domain-wide changes require scope/generalization analysis, alternative comparison and regression/eval evidence. Common/cross-domain changes go to UAOS via parent guidance/upcall.

## 4. Canonical workflow

`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

The workflow remains single-owner. The three products are outputs on the same Financial article trajectory, not separate runtimes/controllers.

## 5. Distribution modes and compatibility

- `PORTFOLIO` — new default: Audit + Deep + Broad + Interaction Pack.
- `ACQUISITION` — broad-feed targets: Audit + Broad + Interaction Pack.
- `FINANCE_DEEP` — Deep + Audit.
- historical/explicit `DUAL` — Deep + Broad + Audit; semantics remain immutable for prior states.
- historical/explicit `FINANCE_BROAD` — Broad + Audit; semantics remain immutable for prior states.

微信公众号 is dual-role for this user and therefore resolves to `PORTFOLIO` when it is the sole target.

## 6. Functional requirement map

| Requirement | Owner surface | Acceptance evidence |
| --- | --- | --- |
| Article identity/state domain-owned | `owner_guard.py`, article `STATE.json` | identity/state/receipt tests |
| Identity-free output contract | `models.py::TaskContract` | contract/routing tests |
| Canonical stage/revision graph | `workflow_spec.py` | workflow/trajectory tests |
| Research coverage/evidence integrity | `references/research.md`, policy | research audits/evals |
| Company Decision Map / named verdict | `schemas.py`, `checks.py`, `references/reader_value.md` | company-decision regressions |
| Publication-source privacy | `checks.py`, `references/reader_value.md` | source-leak regression |
| Title/opening/H1 reader funnel | `references/hooks.md`, `references/reader_value.md`, policy | hook regressions + semantic audit |
| Natural authorial prose | `references/style.md`, `references/reader_value.md`, checks | template/geometry regressions |
| Image-safe H1 lead | `checks.py`, `references/reader_value.md` | navigation regression |
| Three product routing | `models.py`, `routing.py`, `references/platforms.md` | routing/output-contract tests |
| Interaction short-form pack | `schemas.py`, platform/delivery rules | schema + delivery tests |
| Compliance/non-actionability | policy, checks/audit | deterministic + semantic audit |
| Word delivery/mechanical QA | `document.py`, `checks.py`, delivery refs | DOCX tests + render smoke |
| Blocked recovery/system impact | `owner_lifecycle.py` | lifecycle tests |
| Domain learning/promotion | `quality_regression.py`, maintenance | regression tests/evals |
| UAOS cognition/evolution inheritance | `.uaos/CAPABILITIES.json`, `UAOS_SKILL.md` | binding/architecture tests |

## 7. Cognition inheritance contract

Financial consumes the UAOS-hosted problem-response method and does not create a second cognition controller. Every detected defect, user rejection, contradiction, degraded result or uncertain goal satisfaction activates micro diagnosis, macro goal/topology alignment, governing-assumption challenge and relevant external research. Risk may require counterexample search or stronger independent verification. Parent guidance may advise common/cross-domain scope without taking over the Financial article identity, workflow or state.

## 8. Evolution inheritance contract

Financial owns promotion of Financial-specific business/writing rules; UAOS owns common/cross-domain evolution. User feedback first becomes evidence and a system-impact signal, then must pass root-cause/generalization analysis, alternative comparison, reproducible regression/eval evidence, owner-scoped promotion and post-promotion observation. One article or one edit never silently becomes a permanent universal rule.

## 9. Non-functional requirements

- Single business owner; no second Financial controller/task-index/resume plane.
- No silent capability degradation.
- Current authority beats chat memory/search/history.
- Historical receipts remain immutable provenance.
- Same-chat self-review cannot be labelled independent.
- Material product/system changes require reproducible regression/eval evidence.
- Reader-value rules must not become rigid fixed title/paragraph templates.
- Historical distribution-mode meanings cannot be retroactively changed.

## 10. Failure and recovery semantics

- Missing Company Decision Map for multiple material companies -> RESEARCH/EDITORIAL cannot pass.
- Publication source leak -> DRAFT/DELIVERY revision required.
- Weak first-three-sentence jobs or title/H1 promise -> TITLE/DRAFT revision.
- H1 directly enters H2/H3 without substantive lead -> DRAFT revision.
- Required interaction pack absent/copied from long-form -> DRAFT/DELIVERY revision.
- Review failure -> persist FAIL/REVISE target -> invalidate downstream -> repair and re-audit.

## 11. Explicit non-goals

- No investment recommendation or covert actionability.
- No fixed cross-topic stock-score formula.
- No single mandatory title/opening sentence syntax.
- No AI-detector optimization.
- No user-image generation inside Financial Writing.
- No mandatory live UAOS proxy.
- No parent/child task-ID equality.
- No automatic promotion of one article edit into a universal rule.

## 12. Product completion criteria

The 0.9.0 candidate is promotion-ready only when:
1. domain rule/product/architecture/execution-contract surfaces agree on the new portfolio and reader-value requirements;
2. legacy `DUAL` / `FINANCE_BROAD` state contracts remain valid;
3. regressions prove source privacy, H1 image-safe lead, Company Decision Map/named verdict, routing/output sets and interaction-pack schema;
4. full Financial CI, contract eval, static audits, isolated-wheel smoke and DOCX render smoke pass;
5. the candidate is promoted through the owner-appropriate GitHub path;
6. production authority is reread and production CI observed;
7. post-promotion live article/user observation determines KEEP / further repair / rollback.

Documentation alone is not Acceptance evidence.
