---
name: financial-writing-agent-uaos
scope: publishable A-share financial content
---

# Financial Writing Agent — UAOS Entry

Controller/common authority: `D1traverser-debug/universal-agent-os@main`.
Financial business authority: `D1traverser-debug/financial-writing-agent@main` after controlled promotion.

UAOS owns cross-domain governance/common capabilities. Financial Writing owns article identity/state, product requirements, research/writing architecture, business/output contracts, domain evolution evidence and deliverables. Parent/router IDs and Financial article IDs have **no equality requirement**. `TaskContract` is intentionally identity-free.

## Start and authority

A fresh chat may select Financial Writing directly. Once selected, `DOMAIN:financial_writing` is the work plane; normal article turns do **not** traverse a live UAOS business proxy.

For material work read `.uaos/ADAPTER.json`, `.uaos/MANIFEST.json`, `.uaos/CAPABILITIES.json`, `config/EXECUTION_CONTRACT.json`, then only the article state/references needed for the stage. Binding drift blocks the affected capability, not Financial ownership. `financial-writing:main` is a selector/router, not an article task.

## Workflow and admission

Lifecycle:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`.

New tasks use `financial_writing_agent.current_admission`, bind `writing_kernel_version=1.0` and `private_research_contract_version=1.0`, and require:
- leaving `RESEARCH`: admitted material `DecisionEnvelope` and admitted `PrivateResearchBrief`;
- leaving `EDITORIAL`: required Deep/Broad `StoryBlueprint`;
- `EDITORIAL_AUDIT` PASS/REVISE: product-specific `PublicationFitness`.
A naked review file, side research document or chat claim plus `PASS` is not current quality evidence.

Historical/current states created before the private-research marker remain valid provenance and are not retroactively rewritten. Before material continuation of a state without the current writing-kernel marker, use `financial_writing_agent.resume_compatibility.require_material_resume_admission`: ordinary/current-quality continuation requires a current successor; explicit provenance-only continuation cannot inherit current semantic assurance.

## Business invariants

For material thematic/company work, Research performs prior cognition recall, value-chain preflight, listed-company universe recall, current evidence expansion, adversarial/counterexample search, auditable saturation, private-research synthesis, competing-thesis adjudication and Company Decision Map where applicable. Thesis selection follows value-chain coverage; late material discovery invalidates convergence.

`PrivateResearchBrief` is mandatory for new tasks and follows `references/private_research.md`. It is the comprehensive private analytical layer, not a public article outline. It must preserve, as applicable, full economic/market universe coverage, company-level exposure and realization, valuation/liquidity context, catalyst state, benefit tiers, short-horizon role hypotheses, market-position evidence, counterfactual company comparisons, falsification/negative cases, scenario/verification logic and publication distillation. A company list, score table or several representative names is not equivalent. `business strongest` and `most likely short-horizon market core` are separate judgments.

Prefer free or already-available authoritative tools/sources when sufficient; paid/external crawling is justified only when it materially closes a coverage gap. Tool cost never authorizes invented evidence.

`DecisionEnvelope` requires evidence beyond user assertion, credible alternatives, challenged assumptions, counterexamples, rejected paths, selected rationale, saturation and verification. Problem/architecture decisions also require relevant external method evidence. User feedback is high-weight evidence, not automatic rule authority.

Substantive long-form work uses `StoryBlueprint`. For `FINANCE_DEEP`, research completeness and publication selectivity are separate:
- research maps the material value chain/company universe and retains the admitted private brief;
- publication is not the research directory;
- omitted researched classes require `CORE`, `SUPPORT`, or `OMIT_WITH_REASON` scope accounting;
- Deep retains named company/case grounding, contiguous Chinese H1 numbering and no arbitrary default word ceiling;
- private machinery such as universe bookkeeping, internal scores or tactical role maps stays out of copy unless it materially improves the reader product.

For event-led finance stories, `EVENT_TO_COMPANY` requires each material section to bind:
`trigger/change -> mechanism -> company exposure -> operating/financial expression -> verification/reversal condition`.
A company name alone is not causal grounding.

`FINANCE_BROAD` is an independent acquisition rebuild, not shortened Deep.

Current PublicationFitness gates: `FACT_INTEGRITY`, `RETENTION`, `COMPANY_GROUNDING`, `STRUCTURE_NUMBERING`, `ORIGINALITY`, `AUTHORIAL_STYLE`, `COMPLIANCE`, `PAYOFF`. Each gate needs text evidence; MAJOR/CRITICAL findings block PASS. Same-session critics remain `CHAT_SELF_REVIEW`.

Originality is evidence-bound: source-compared `OriginalityEvidence` is required; close paraphrase/patchwriting requires revision. Same-chat intuition cannot prove zero plagiarism. Natural prose remains voice/material/story first; clustered generic scaffolding is diagnostic, not a phrase-ban or humanizer template.

## Progressive references and delivery

Load progressively: research/cognition `references/research.md`, `references/private_research.md`, `references/knowledge.md`; audit `references/audit.md`, `references/reader_value.md`; editorial/title/draft `references/editorial.md`, `references/hooks.md`, `references/style.md`; market explanation when material `references/market_explanation.md`; platform `references/platforms.md`; delivery `references/delivery.md`; evolution `references/maintenance.md`, `references/proactive_resolution.md`.

New ordinary work defaults to `PORTFOLIO + WORD_FILE_ONLY`: `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX`, `AUDIT_DOCX`. Historical product meanings remain immutable. Buy/sell, entry timing, target price, position sizing and covert equivalents remain prohibited.

## Parent cognition binding and domain problem closure

Parent cognition/search depth and mandatory problem response are owned only by current UAOS `config/DELIBERATION_POLICY.json`; no parent cognition floor is copied here. Financial retains domain-native evidence/root-scope/evolution/action gates.

Do not turn user rejection directly into universal rules. Persist it as evidence, compare local/workflow/architecture/common-capability hypotheses at the depth required by the current parent policy, admit root scope, then choose `LOCAL_REPAIR`, `DOMAIN_CANDIDATE`, `PARENT_UPCALL`, or evidence-backed `NO_CHANGE`. If an owner-authorized repair is available without a required user fact/approval/safety choice, attempt it before finalizing.

## Executable proactive resolution before user escalation

`financial_writing_agent/proactive_resolution.py` owns recovery receipts and user-escalation admission. Recover from available evidence before asking the user; unresolved escalation must pass `require_user_escalation_admission`.

## Governed evolution and completion

Financial evolution follows `problem/evidence -> cognition -> alternatives -> DecisionEnvelope -> candidate -> regression/eval -> controlled promotion -> production reread -> live observation -> keep/repair/rollback/retire`. Common/cross-domain changes upcall UAOS.

Article identity authority is `workspaces/articles/{task_id}/STATE.json::task_id`. Completion requires current outputs, admitted research decision and required private research, PublicationFitness, mechanical/render QA, state/artifact reconciliation and accurate assurance. Green mechanical tests or documentation alone are not semantic publication proof.
