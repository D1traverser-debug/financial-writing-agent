---
name: financial-writing-agent-uaos
scope: publishable A-share financial content
---

# Financial Writing Agent — UAOS Entry

Controller/common-governance authority: `D1traverser-debug/universal-agent-os@main`.
Domain business authority: `D1traverser-debug/financial-writing-agent@main` after controlled promotion; candidate maintenance uses the active candidate ref without transferring business ownership.

UAOS owns cross-domain selection/governance, parent continuity and hosted common capabilities. Financial Writing owns article identity/state, product requirements, research/writing architecture, business/output contract, domain knowledge/evolution evidence and deliverables. Parent/router IDs and Financial article IDs are distinct namespaces with **no equality requirement**. `TaskContract` remains identity-free.

## Start and authority

A fresh chat may select Financial Writing directly. Once selected, `DOMAIN:financial_writing` is the current work plane; normal article turns do **not** traverse a live UAOS business proxy.

Load only what the action needs:
1. `.uaos/ADAPTER.json`, `.uaos/MANIFEST.json`, `.uaos/CAPABILITIES.json`;
2. `config/EXECUTION_CONTRACT.json`;
3. `docs/product_requirements.md` / `docs/architecture.md` for product/architecture work;
4. exact article `STATE.json` only when an article exists;
5. progressive business references listed below.

Confirm hosted UAOS common-capability and behavior-assurance contracts before material work. Binding drift blocks the affected capability only; it never transfers Financial ownership to UAOS.

`financial-writing:main` is a selector/router entry, not an article task. Financial creates/owns its own `task_id` and `STATE.json`; UAOS may retain only an opaque returned state reference.

## Current business lifecycle

Stable external lifecycle:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

Do not expand business state into a stage for every cognitive/editorial action. Current internal work uses `financial_writing_agent/writing_kernel.py` focused passes under the same Financial owner.

### Current vs historical owner path

For **new current tasks**, create/advance state through `financial_writing_agent.current_admission`. It binds `writing_kernel_version=1.0` and fail-closes material transitions on current cognition/story/fitness evidence while delegating identity/state transition semantics to the canonical `owner_guard.py`.

Historical states without the current kernel marker remain readable/resumable through `owner_guard.py`; do not rewrite historical receipts/state merely to manufacture 1.0 evidence.

The current path requires:
- leaving `RESEARCH`: admitted material `DecisionEnvelope`;
- leaving `EDITORIAL`: required Deep/Broad `StoryBlueprint` objects;
- `EDITORIAL_AUDIT -> PASS/REVISE`: required product-specific `PublicationFitness` evidence.

A naked review file plus `review_status="PASS"` is not current 1.0 publication admission evidence.

## Progressive references

- research/cognition: `references/research.md`, `references/knowledge.md`;
- story/editorial: `references/editorial.md`, `references/hooks.md`, `references/style.md`;
- publication acceptance: `references/audit.md`, `references/reader_value.md`;
- market-specific explanation when needed: `references/market_explanation.md`;
- platform routing: `references/platforms.md`;
- delivery/Word: `references/delivery.md`;
- maintenance/evolution: `references/maintenance.md`, `references/proactive_resolution.md`, `knowledge/METHOD_KNOWLEDGE_CATALOG.json`.

Do not load all references into the writer pass. Least-context execution is part of the architecture: research rules stay in research, story rules in StoryBlueprint construction, and quality governance in downstream admission/audit.

## Research / cognition requirements

For material thematic/company work:
`knowledge recall -> value-chain preflight -> company universe -> current evidence -> adversarial/counterexample search -> search saturation -> competing thesis adjudication -> Company Decision Map -> Research Audit`.

Value-chain coverage is mandatory **before** thesis selection. A late material chain node invalidates convergence and requires thesis retest.

Broad search does not mean claiming literal exhaustive internet coverage. Material decisions preserve source-family sweeps and may stop only after two consecutive sweeps add no decision-changing candidate, failure mode, counterexample or changed decision, with remaining gaps recorded.

Material judgments use `DecisionEnvelope`: evidence beyond user assertion, at least two alternatives, assumptions challenged, counterexamples, rejected paths, selected rationale, saturation and verification. Problem-triggered or architecture/governance judgments additionally require relevant external method/architecture research.

User feedback is high-weight evidence, **not automatic rule authority**.

## Story architecture / Deep and Broad

Substantive long-form work requires a `StoryBlueprint` before prose.

`FINANCE_DEEP` is the complete finance/review product:
- all declared material value-chain classes represented or explicitly adjudicated out;
- material-company economics differentiated;
- material explanatory sections grounded in named company/case evidence when available;
- explicit contiguous Chinese H1 numbering (`一、二、三、...`);
- no default word-count ceiling. Remove redundancy; do not remove material coverage just to hit a length target.

`FINANCE_BROAD` is independently rebuilt for acquisition from the same audited evidence, not shortened from Deep.

Story form follows content. Hard anomaly, company conflict, reversal, mystery, system map, consequence chain, case lead and timeline escalation are candidate engines. External structures such as nut-graf/five-box/hourglass are method knowledge, not universal templates.

## Reader value / style / originality

Retention is a full-article property. Title/opening must provide a concrete reader reason, but every section must add information, company/case evidence or a consequence and earn the next section. Curiosity must be paid off.

Natural prose is material/stance/story/voice-first. Generic scaffolding or AI-associated phrases are diagnostic when clustered/unearned, not one-token bans. Do not use a generic humanizer or fabricate anecdotes/slang.

Research sources are evidence, not prose templates. Draft from normalized claims/notes + StoryBlueprint; compare suspicious/distinctive passages back against material sources. Close paraphrase/patchwriting requires revision. Same-chat inspection cannot claim zero plagiarism.

Publication copy keeps research provenance private when attribution exists only to prove diligence; retain attribution when the actor/source identity or distinctive quoted language is part of the claim.

## Publication Fitness

Current long-form publication acceptance requires exactly these evidence-backed gates:
- `FACT_INTEGRITY`
- `RETENTION`
- `COMPANY_GROUNDING`
- `STRUCTURE_NUMBERING`
- `ORIGINALITY`
- `AUTHORIAL_STYLE`
- `COMPLIANCE`
- `PAYOFF`

Each gate cites text location/excerpt/finding/severity. MAJOR/CRITICAL findings cannot PASS. REVISE requires concrete repair actions. Same-session critics remain `CHAT_SELF_REVIEW`; role labels are not independent verification.

## Current product contract

For new ordinary work, default `PORTFOLIO + WORD_FILE_ONLY` produces:
- `FINANCE_DEEP_DOCX`;
- `FINANCE_BROAD_DOCX`;
- `PLATFORM_INTERACTION_PACK_DOCX`;
- `AUDIT_DOCX`.

Broad-feed-only targets may use `ACQUISITION`. Finance-community-only targets may use `FINANCE_DEEP`.

Historical compatibility is immutable: existing `DUAL` remains Deep + Broad + Audit and existing `FINANCE_BROAD` remains Broad + Audit.

## Mandatory problem response

Financial inherits UAOS adaptive deliberation. Every detected defect, user correction/rejection, degraded outcome, contradiction, repeated repair or unreliable goal satisfaction requires at least:
1. micro diagnosis;
2. macro goal/topology alignment;
3. governing-assumption challenge;
4. relevant external research.

Material problems require alternatives/counterexamples and stronger verification proportional to risk. Familiarity is not a waiver. Common/cross-domain causes upcall UAOS; Financial-local causes remain Financial-owned.

After diagnosis, problem-to-action closure applies: if an owner-authorized repair is currently available and no required user fact/approval/authorization/safety-sensitive choice blocks it, attempt the repair before ending the turn. Recommendation-only is not a valid terminal.

## Knowledge and governed evolution

Financial retains both topic cognition and method cognition. `knowledge/METHOD_KNOWLEDGE_CATALOG.json` stores learned external/UAOS methods with source, category, fit, misfit, adoption state and revalidation condition. Cataloging is not rule promotion.

Financial-owned learning follows:
`problem/evidence -> cognition -> failure class -> alternatives -> DecisionEnvelope -> candidate -> reproducible eval -> Financial promotion -> post-promotion observation -> keep/repair/rollback/retire`.

One article/feedback event may create a candidate but does not silently become universal authority. Cross-domain/common-capability evolution remains UAOS-owned.

Multi-agent is not the default. Split specialist executors only when tools, policy/permissions, context, output contract, independence requirement or measured parallelism benefit materially differs; otherwise use the one-owner focused-pass kernel.

## State integrity and completion

Financial article identity authority is `workspaces/articles/{task_id}/STATE.json::task_id`. Material changes bind fresh owner state, use owner/current admission/lifecycle/proactive-resolution guards as applicable, persist evidence and reread authority.

Completion requires current article outputs, PublicationFitness, mechanical/render QA, state/artifact reconciliation and accurate assurance. Product documentation, configured roles or green mechanical tests alone are not semantic publication proof.

Historical completed receipts are immutable provenance and never route selectors.
