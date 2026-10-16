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
- leaving `RESEARCH`: admitted material `DecisionEnvelope` **and** admitted `PrivateResearchBrief`;
- leaving `EDITORIAL`: required Deep/Broad `StoryBlueprint`;
- `EDITORIAL_AUDIT` PASS/REVISE: product-specific `PublicationFitness`.
A naked review file, side research document or chat claim plus `PASS` is not current quality evidence.

Historical/current states created before the private-research marker remain valid provenance and are not retroactively rewritten. Before material continuation of a state without the current writing-kernel marker, use `financial_writing_agent.resume_compatibility.require_material_resume_admission`:
- ordinary/current-quality continuation => `CURRENT_SUCCESSOR_REQUIRED`;
- explicit historical/provenance-only continuation => `HISTORICAL_PROVENANCE_ONLY`, with no current-kernel quality claim.
Never rewrite historical receipts to manufacture current evidence.

## Business invariants

For material thematic/company work, Research performs prior cognition recall, value-chain preflight, listed-company universe recall, current evidence expansion, adversarial/counterexample search, auditable saturation, private-research synthesis, competing-thesis adjudication and Company Decision Map where applicable. Thesis selection follows value-chain coverage; late material discovery invalidates convergence.

The `PrivateResearchBrief` is mandatory for new tasks. It is the comprehensive private analytical layer and follows `references/private_research.md`. As applicable it covers:
- economic-substance and market-label universes, included/excluded/unresolved names and value-chain coverage;
- company-level business granularity, realization stage, benefit mechanism and reversal conditions;
- current total/float market cap, turnover and liquidity for material short-horizon candidates;
- catalyst strength/freshness and expectation/implementation/realization state;
- direct, first-order, second-order, weak and negative benefit tiers;
- short-horizon roles such as pioneer, sentiment high/space leader, theme leader, capacity middle-army/trend leader, branch leader, assist, card-position competitor, catch-up, follower and eliminated candidate;
- market sentiment cycle, board height/promotion structure and recent stock-character evidence;
- explicit `why A rather than B` counterfactual comparisons;
- negative/falsification pool, catalyst-specific scenario trees and next-window verification/falsification;
- publication distillation: what must inform Deep/Broad and what should remain private.

A company list, a single score or several representative names is not equivalent to the private brief. `business strongest` and `most likely short-horizon market core` are separate judgments. Role names such as leader or card-position are hypotheses requiring observable role logic, not labels applied after the fact.

Prefer free or already-available authoritative tools/sources when they are sufficient; use paid/external crawling only when it materially closes a coverage gap. Tool cost never authorizes invented evidence.

`DecisionEnvelope` requires evidence beyond user assertion, credible alternatives, challenged assumptions, counterexamples, rejected paths, selected rationale, saturation and verification. Problem/architecture decisions also require relevant external method evidence. User feedback is high-weight evidence, not automatic rule authority.

Substantive long-form work uses `StoryBlueprint`. For `FINANCE_DEEP`, research completeness and publication selectivity are separate:
- research still maps the material value chain/company universe and retains the admitted private brief;
- publication is not the research directory;
- if any researched material class is omitted from copy, `publication_scope_decisions` accounts for every researched class as `CORE`, `SUPPORT`, or `OMIT_WITH_REASON` with evidence/rationale;
- Deep retains named company/case grounding, contiguous Chinese H1 numbering and no arbitrary default word ceiling;
- private machinery such as universe bookkeeping, internal scores, ladder mechanics or tactical role maps should stay out of the article unless they materially improve the reader product.

For event-led finance stories, `EVENT_TO_COMPANY` requires each material section to bind:
`trigger/change -> mechanism -> company exposure -> operating/financial expression -> verification/reversal condition`.
A company name alone is not causal grounding.

`FINANCE_BROAD` is an independent acquisition rebuild, not shortened Deep.

Current PublicationFitness gates: `FACT_INTEGRITY`, `RETENTION`, `COMPANY_GROUNDING`, `STRUCTURE_NUMBERING`, `ORIGINALITY`, `AUTHORIAL_STYLE`, `COMPLIANCE`, `PAYOFF`. Each gate needs text evidence; MAJOR/CRITICAL findings block PASS. Same-session critics remain `CHAT_SELF_REVIEW`.

Originality is evidence-bound: source-compared `OriginalityEvidence` is required; close paraphrase/patchwriting requires revision. Same-chat intuition cannot prove zero plagiarism. Natural prose remains voice/material/story first; clustered generic scaffolding is diagnostic, not a phrase-ban or humanizer template.

## Progressive references and delivery

Load progressively: research/cognition `references/research.md`, `references/private_research.md`, `references/knowledge.md`; audit `references/audit.md`, `references/reader_value.md`; editorial/title/draft `references/editorial.md`, `references/hooks.md`, `references/style.md`; market explanation when material `references/market_explanation.md`; platform `references/platforms.md`; delivery `references/delivery.md`; evolution `references/maintenance.md`, `references/proactive_resolution.md`.

New ordinary work defaults to `PORTFOLIO + WORD_FILE_ONLY`: `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX`, `AUDIT_DOCX`. Historical product meanings remain immutable. Buy/sell, entry timing, target price, position sizing and covert equivalents remain prohibited.

## Mandatory problem response

Every detected defect, user correction/rejection, degraded outcome, contradiction, repeated repair or unreliable goal satisfaction triggers micro diagnosis, macro/topology alignment, governing-assumption challenge and relevant external research; material problems add competing hypotheses/counterexamples and stronger verification.

Do not turn user rejection directly into universal rules. Persist it as evidence, compare local/workflow/architecture/common-capability hypotheses, admit root scope, then choose `LOCAL_REPAIR`, `DOMAIN_CANDIDATE`, `PARENT_UPCALL`, or evidence-backed `NO_CHANGE`. If an owner-authorized repair is available without a required user fact/approval/safety choice, attempt it before finalizing.

## Executable proactive resolution before user escalation

`financial_writing_agent/proactive_resolution.py` owns recovery receipts and user-escalation admission. Recover from available evidence before asking the user; unresolved escalation must pass `require_user_escalation_admission`.

## Governed evolution and completion

Financial evolution follows `problem/evidence -> cognition -> alternatives -> DecisionEnvelope -> candidate -> regression/eval -> controlled promotion -> production reread -> live observation -> keep/repair/rollback/retire`. Common/cross-domain changes upcall UAOS.

Article identity authority is `workspaces/articles/{task_id}/STATE.json::task_id`. Completion requires current outputs, admitted research decision and required private research, PublicationFitness, mechanical/render QA, state/artifact reconciliation and accurate assurance. Green mechanical tests or documentation alone are not semantic publication proof.
