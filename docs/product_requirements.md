# Financial Writing Agent — Product Requirements Baseline

Status: `CURRENT_DOMAIN_PRODUCT_REQUIREMENTS`
Version: `0.8.4`
Date: `2026-10-15`
Owner: `DOMAIN:financial_writing`
Parent common-governance method: `UAOS 2.4.5 / COMMON_CAPABILITIES 1.5.0`

## 1. Product outcome

Financial Writing turns a user brief, links/files/current-market evidence and scoped constraints into publication-ready Chinese A-share financial articles with auditable research, explicit uncertainty, non-actionable financial compliance, durable article state, review/recovery, Word delivery and evidence-bound learning.

The product must be directly usable after the user selects/inherits Financial Writing in a fresh chat. UAOS supplies hosted common capabilities and parent guidance; it is not a mandatory per-turn business proxy.

## 2. Ownership boundary

- UAOS owns cross-domain selection/governance, shared product-engineering method, hosted cognition, common/cross-domain evolution and parent continuity.
- Financial Writing owns this product requirements baseline, Financial architecture, article identity/state, business/output contract, workflow, research/editorial/style/delivery rules, domain learning/evals and deliverables.
- `workspaces/articles/{task_id}/STATE.json::task_id` is the Financial article identity authority.
- A UAOS controller/router ID is never required to equal a Financial article ID.

## 3. Primary user journeys

### PR-01 Direct start
A new chat can select Financial Writing directly and immediately operate under `DOMAIN:financial_writing`. No prior controller chat or parent-created article task is required.

### PR-02 New article
Given a brief, Financial creates its own article identity/state, derives an identity-free `TaskContract`, researches, edits, reviews, delivers and audits through the canonical workflow.

### PR-03 Exact continuation
Given an exact Financial article reference, resume from that article's current `STATE.json`; never infer or adopt a parent task ID as article identity.

### PR-04 Research and evidence
Research must maximize material-topic/company recall, maintain source/evidence quality, separate fact/mechanism/interpretation/unknowns, avoid evidence-stage escalation and revalidate time-sensitive claims.

### PR-05 Dual editorial product
Unless explicitly narrowed, produce both deep and broad finance outputs plus an audit document. Deep mode prioritizes material completeness; broad mode selectively compresses without destroying the governing contradiction/logic.

### PR-06 Publication delivery
Default delivery is `WORD_FILE_ONLY`. DOCX must satisfy mechanical and render QA, file/current-session availability, typography and policy constraints before visible completion is claimed.

### PR-07 Review and recovery
A failed review must persist a canonical repair cursor, invalidate affected downstream work and resume through the owner lifecycle rather than free-form patching.

### PR-08 User correction / detected problem
Every detected problem — including user correction/rejection, failed/degraded output, contradiction, repeated repair or unreliable goal satisfaction — must trigger the hosted problem-response floor before repair selection:
1. micro diagnosis;
2. macro goal/topology/architecture alignment;
3. governing-assumption challenge;
4. relevant external research.

Problem size changes depth, not activation. Risk may add counterexample search and independent verification.

### PR-09 Domain evolution
Every problem is evaluated for learning impact. One-off evidence may create a candidate but cannot silently become a global rule. Domain-wide changes require scope/generalization analysis plus regression/eval evidence. Common/cross-domain changes go to UAOS through parent guidance/upcall.

### PR-10 Product review / feature expansion
For a major feature family, rebuild or failure revealing missing product assumptions, use UAOS-hosted product-requirements/architecture governance to fill requirement details before implementation. The resulting Financial-specific requirements and architecture remain in this repository.

## 4. Canonical workflow

`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

The workflow is owned by `financial_writing_agent/workflow_spec.py`; this document defines product intent and acceptance, not a second workflow implementation.

## 5. Functional requirement map

| Requirement | Owner surface | Acceptance evidence |
| --- | --- | --- |
| Article identity/state is domain-owned | `owner_guard.py`, article `STATE.json` | identity/state/receipt tests |
| Identity-free output contract | `models.py::TaskContract` | model + wheel smoke tests |
| Canonical stage/revision graph | `workflow_spec.py` | workflow/trajectory tests |
| Research coverage and evidence integrity | `references/research.md`, `config/policy.json` | contract evals + article audits |
| Editorial completeness and dual modes | `references/editorial.md`, `config/policy.json` | quality regression/eval fixtures |
| Title/opening/reader funnel | `references/hooks.md` | title/hook checks + semantic audit |
| Natural authorial style and anti-template controls | `references/style.md` | style/geometry/template tests |
| Compliance/non-actionability | `config/policy.json`, checks/audit refs | deterministic + semantic audit |
| Word delivery/mechanical QA | `document.py`, `checks.py`, `references/delivery.md` | DOCX tests + render smoke |
| Blocked recovery/system impact | `owner_lifecycle.py` | lifecycle tests |
| Domain learning/regression promotion | `quality_regression.py`, `references/maintenance.md` | quality regression tests/evals |
| UAOS cognition/evolution inheritance | `.uaos/CAPABILITIES.json`, `UAOS_SKILL.md`, `EXECUTION_CONTRACT.json` | inheritance architecture tests + parent binding validation |

## 6. Non-functional requirements

- Single business owner: no second Financial controller/task-index/lease/resume plane.
- No silent capability degradation: missing hard capability blocks only affected work.
- Current authority beats chat memory/search/history.
- Historical receipts remain immutable provenance.
- Same-chat self-review cannot be labelled independent.
- Material product/system changes require reproducible regression/eval evidence.
- Context loading is progressive; do not preload the whole repository for ordinary article stages.
- Parent governance cannot take over Financial business identity/workflow/state.

## 7. Failure and recovery semantics

- Review failure -> persist FAIL decision and canonical repair target -> invalidate downstream artifacts -> repair from target -> fresh review.
- Missing hard capability -> block affected stage; do not invent a weaker path.
- Binding/common-capability drift -> block the affected hosted capability and reread current parent/domain authority.
- User correction/problem -> run mandatory research/reflection floor; then decide local repair vs systemic/domain evolution vs parent upcall.
- Repeated failure -> repair common failure class/root abstraction, not stacked exceptions.

## 8. Cognition inheritance contract

Financial does not implement a second cognition controller. It consumes the current UAOS common capability and deliberation policies declared in `.uaos/CAPABILITIES.json`.

The child must preserve the four-dimensional problem-response floor and may only weaken it if the user explicitly changes the governing parent requirement. Familiarity or apparent locality is not a waiver.

## 9. Evolution inheritance contract

Financial owns business-rule evolution; UAOS owns common/cross-domain evolution. The Financial maintenance lifecycle is:

`Problem/feedback -> research+reflection -> failure/root-cause classification -> scope/generalization -> alternatives -> candidate -> regression/eval -> owner-scoped promotion -> post-promotion observation -> keep/rollback/retire`

Article-linked material feedback is tracked by `owner_lifecycle.py`. Quality-rule promotion uses domain eval/regression evidence. Parent/common changes are proposals/upcalls, not direct child mutation of UAOS.

## 10. Explicit non-goals

- No investment recommendation or covert actionability.
- No mandatory live UAOS proxy for normal article turns.
- No parent/child task-ID equality.
- No second domain controller or duplicated global requirement/evolution catalog.
- No automatic promotion of one article/user edit into a universal rule.
- No claim of independent semantic certification from same-chat self-review.

## 11. Product completion criteria

The product baseline is internally ready when:
1. parent common-capability contract contains current cognition/evolution/product-review semantics;
2. Financial declares and tests inheritance of those capabilities;
3. direct-domain activation and identity boundaries remain intact;
4. problem-response research/reflection is represented in current Financial maintenance/product authority;
5. product requirements map to executable tests/evals or explicit observable evidence;
6. full Financial CI, contract eval, static audits, isolated-wheel smoke and DOCX render smoke pass on the final candidate;
7. the promoted production tree is reread and CI-observed.

For Financial 0.8.4 these criteria are satisfied by UAOS 2.4.5 / common contract 1.5.0 production authority, Financial candidate run `38609262769` PASS, Financial release commit `6a4d6d8a1dc95444ced2a8c42f5f00d03da0ab3c`, and Financial production run `38609447053` PASS. The closure record remains the dedicated evidence narrative.
