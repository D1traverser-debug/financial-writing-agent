---
name: financial-writing-agent-uaos
scope: publishable A-share financial content
---

# Financial Writing Agent — UAOS Entry

Controller/common-governance authority: `D1traverser-debug/universal-agent-os@main`.
Domain business authority: `D1traverser-debug/financial-writing-agent@main` after controlled promotion; candidate maintenance uses the active candidate ref without transferring ownership.

UAOS owns cross-domain selection/governance and hosted common capabilities. Financial Writing owns article identity/state, product requirements, research/writing architecture, business/output contracts, domain knowledge/evolution evidence and deliverables. Parent/router IDs and Financial article IDs are distinct namespaces with **no equality requirement**. `TaskContract` is intentionally identity-free.

## Start and authority

A fresh chat may select Financial Writing directly. Once selected, `DOMAIN:financial_writing` is the current work plane; normal article turns do **not** traverse a live UAOS business proxy.

Load only what the action needs:
1. `.uaos/ADAPTER.json`, `.uaos/MANIFEST.json`, `.uaos/CAPABILITIES.json`;
2. `config/EXECUTION_CONTRACT.json`;
3. `docs/product_requirements.md` / `docs/architecture.md` for product or architecture work;
4. exact article `STATE.json` only when an article exists;
5. the progressive references relevant to the current stage;
6. `evals/EVOLUTION_INDEX.json` when a detected problem is material/evolution-relevant or needs parent guidance.

Confirm hosted UAOS capability/behavior-assurance bindings before material work. Binding drift blocks the affected capability; it does not transfer Financial ownership to UAOS.

`financial-writing:main` is a selector/router entry, not an article task. Financial creates and owns its own `task_id` and `STATE.json`.

## Workflow and current admission

Stable external lifecycle:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

New current tasks use `financial_writing_agent.current_admission`, which binds `writing_kernel_version=1.0` and delegates state-transition semantics to `owner_guard.py` while adding fail-closed quality admission. Historical states without the marker remain readable/resumable through `owner_guard.py`; do not rewrite historical receipts to manufacture 1.0 evidence.

Current hard admissions:
- leaving `RESEARCH`: admitted material `DecisionEnvelope`;
- leaving `EDITORIAL`: required Deep/Broad `StoryBlueprint` objects;
- `EDITORIAL_AUDIT` PASS/REVISE: product-specific `PublicationFitness` evidence.

A naked review file plus `PASS` is not current publication evidence.

## Progressive references

- research/cognition: `references/research.md`, `references/knowledge.md`;
- research audit/publication acceptance: `references/audit.md`, `references/reader_value.md`;
- editorial/title/draft: `references/editorial.md`, `references/hooks.md`, `references/style.md`;
- market explanation when material: `references/market_explanation.md`;
- platform routing: `references/platforms.md`;
- Word delivery: `references/delivery.md`;
- maintenance/evolution: `references/maintenance.md`, `references/proactive_resolution.md`, `knowledge/METHOD_KNOWLEDGE_CATALOG.json`, `evals/EVOLUTION_INDEX.json`.

Do not load every reference into the writer pass. Research, story construction and audit use least-context responsibilities under the one Financial owner and `financial_writing_agent/writing_kernel.py`.

## Business invariants

For material thematic/company work, Research performs prior cognition recall, mandatory value-chain preflight, listed-company universe recall, current evidence expansion, adversarial/counterexample search, auditable saturation, competing-thesis adjudication and Company Decision Map when applicable. Thesis selection occurs only after value-chain coverage exists; a late material node invalidates convergence.

`DecisionEnvelope` requires evidence beyond user assertion, credible alternatives, challenged assumptions, counterexamples, rejected paths, selected rationale, saturation and verification. Problem-triggered or architecture/governance decisions additionally require relevant external method/architecture research. User feedback is high-weight evidence, not automatic rule authority.

Substantive long-form work uses `StoryBlueprint`. `FINANCE_DEEP` preserves material value-chain/company coverage, uses named company/case grounding where available, explicit contiguous Chinese H1 numbering and no default word ceiling. `FINANCE_BROAD` is independently rebuilt for acquisition, not shortened Deep.

Current publication fitness gates are `FACT_INTEGRITY`, `RETENTION`, `COMPANY_GROUNDING`, `STRUCTURE_NUMBERING`, `ORIGINALITY`, `AUTHORIAL_STYLE`, `COMPLIANCE`, `PAYOFF`. Each semantic gate needs text-location/excerpt/finding evidence; MAJOR/CRITICAL findings cannot PASS. Same-session critics remain `CHAT_SELF_REVIEW`.

Natural prose is voice/material/story first. Generic scaffolding is diagnostic when clustered/unearned, not a one-token ban. Research sources are evidence, not prose templates; close paraphrase/patchwriting requires revision.

## Current product contract

New ordinary work defaults to `PORTFOLIO + WORD_FILE_ONLY`:
- `FINANCE_DEEP_DOCX`;
- `FINANCE_BROAD_DOCX`;
- `PLATFORM_INTERACTION_PACK_DOCX`;
- `AUDIT_DOCX`.

Historical `DUAL` and `FINANCE_BROAD` meanings remain immutable. Buy/sell, entry timing, target price, position sizing and covert equivalents remain prohibited.

## Mandatory problem response — Common Behavior 1.3

Every detected defect, user correction/rejection, degraded outcome, contradiction, repeated repair or unreliable goal satisfaction triggers micro diagnosis, macro goal/topology alignment, governing-assumption challenge and relevant external research. Material problems add alternatives/counterexamples and stronger verification. Familiarity is not a waiver.

Financial does not replace its existing cognition system for Common Behavior 1.3. `financial_writing_agent.cognition_governance.DecisionEnvelope` remains the evidence/research/alternatives/counterexample/search-saturation authority. `financial_writing_agent.problem_action_admission` adds the missing causal bridge: an admitted DecisionEnvelope must be converted into an evidence-grounded `RootScopeReceipt` before repair or evidence-backed no-change.

User framing, an external Skill/method, and the first repairable symptom are evidence, not root-cause authority. A material/systemic problem must compare hypotheses across causal layers, preserve at least one evidence-rejected alternative, test an architecture/upstream explanation and bind architecture reassessment evidence. Hypotheses must reference evidence actually present in the admitted DecisionEnvelope; invented support refs fail admission.

The owner-native problem transaction is:
`DETECT -> RECOVER WHEN APPLICABLE -> DECISION_ENVELOPE -> ROOT_SCOPE_ADMISSION -> TYPED_EVOLUTION_DISPOSITION -> REPAIR / NO_CHANGE / BLOCK / PARENT_UPCALL -> VERIFY`.

Material/evolution-relevant problems require a durable causal reference discoverable through `evals/EVOLUTION_INDEX.json`; a `PARENT_UPCALL` evolution disposition additionally requires a structured parent-upcall reference. A genuine required user fact/approval/authorization/safety choice may block without fabricating root-cause certainty.

If an admitted owner-authorized repair is currently available and no required user fact/approval/authorization/safety choice blocks it, attempt and verify the repair before ending the turn. Recommendation-only is not valid closure for a repairable problem.

## Executable proactive resolution before user escalation

`financial_writing_agent/proactive_resolution.py` owns the recovery receipt and escalation gate. Recover safely from available evidence before asking the user; unresolved escalation must pass `require_user_escalation_admission`. See `references/proactive_resolution.md` for evidence order and assurance limits.

## Governed evolution and completion

Financial retains topic cognition and method cognition. Cataloging knowledge is not rule promotion. Financial-owned evolution follows `problem/evidence -> cognition -> alternatives -> DecisionEnvelope -> root-scope -> typed evolution disposition -> candidate/action -> regression/eval -> controlled promotion -> production reread -> live observation -> keep/repair/rollback/retire`. Cross-domain/common-capability changes upcall UAOS.

Financial article identity authority is `workspaces/articles/{task_id}/STATE.json::task_id`. Completion requires current outputs, PublicationFitness, mechanical/render QA, state/artifact reconciliation and accurate assurance. Product docs, role labels or green mechanical tests alone are not semantic publication proof. Historical receipts remain immutable provenance.
