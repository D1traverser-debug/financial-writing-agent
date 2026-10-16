---
name: financial-writing-agent-uaos
scope: publishable A-share financial content
---

# Financial Writing Agent — UAOS Entry

Controller/common authority: `D1traverser-debug/universal-agent-os@main`. Financial business authority: this repository on `main` after controlled promotion.

UAOS owns cross-domain governance/common capabilities. Financial Writing owns article identity/state, product requirements, research/writing architecture, business/output contracts, domain evolution evidence and deliverables. Parent/router IDs and Financial article IDs have no equality requirement; `TaskContract` is identity-free.

## Start and authority

A fresh chat may select Financial Writing directly. Once selected, `DOMAIN:financial_writing` is the work plane; normal article turns do **not** traverse a live UAOS business proxy.

For material work read `.uaos/ADAPTER.json`, `.uaos/MANIFEST.json`, `.uaos/CAPABILITIES.json`, `config/EXECUTION_CONTRACT.json`, then only the stage references needed. Binding drift blocks the affected capability, not Financial ownership.

## Workflow and current admission

Lifecycle:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`.

New tasks use `financial_writing_agent.current_admission`, bind `writing_kernel_version=1.0` and `private_research_contract_version=1.1`, and require:
- leaving `RESEARCH`: admitted material `DecisionEnvelope` + admitted `PrivateResearchBrief`;
- leaving `EDITORIAL`: required Deep/Broad `StoryBlueprint`;
- `EDITORIAL_AUDIT` PASS/REVISE: product-specific `PublicationFitness`.

A side file, chat claim or naked PASS is not current quality evidence. Historical states explicitly carrying private-research 1.0 remain provenance-compatible and validate against the original 1.0 module set.

## Research invariants

For material thematic/company work, Research performs prior cognition recall, value-chain preflight, listed-company universe recall, current evidence expansion, adversarial/counterexample search, saturation, private-research synthesis, competing-thesis adjudication and Company Decision Map where applicable. Thesis selection follows value-chain coverage; late material discovery invalidates convergence.

`PrivateResearchBrief` is mandatory for new tasks and follows `references/private_research.md`. Version 1.1 requires the original comprehensive private analytical layer plus three hard jobs:
1. `material_catalyst_and_policy_ledger`: all known materially relevant event/policy catalysts under the declared scope, with chronology and tightening/easing/suspension/reduction/extension/exemption/retaliation/rollback states;
2. `driver_sustainability_operability_and_concept_map`: driver type, duration, operational expression and concept/sector mapping;
3. `cross_segment_global_selection`: after within-segment comparison, compare branch winners and market-role candidates globally under current liquidity/sentiment constraints.

The brief must retain, as applicable: economic/market universe coverage, company-level business stage and realization, total/float market cap and liquidity, catalyst freshness, benefit tiers, short-horizon role hypotheses, market structure, within-segment counterfactuals, negative/falsification cases, scenario/verification logic and publication distillation. A company list, score table or several representative names is not equivalent.

`business strongest`, `most durable` and `most likely short-horizon market core` are separate judgments. Role vocabulary is not a quota: constrained liquidity may support only one true core, and one company may combine high-board/theme-leader/middle-army roles when evidence supports it.

Prefer free or already-available authoritative tools/sources when sufficient; for policy/events prefer primary government/regulator/exchange/company sources. Paid/external crawling is justified only when it materially closes a coverage gap. Tool cost never authorizes invented evidence.

`DecisionEnvelope` requires evidence beyond user assertion, credible alternatives, challenged assumptions, counterexamples, rejected paths, rationale, saturation and verification. User feedback is high-weight evidence, not automatic rule authority.

## Research Audit and Editorial

Use `references/research.md` and `references/audit.md`. Research Audit must verify the material event/policy ledger, driver/sustainability/operability/concept analysis, within-segment comparison, cross-segment global selection and unresolved gaps before PASS.

Editorial uses `references/editorial.md`. For `FINANCE_DEEP`, research completeness and publication selectivity are separate. Deep should preferentially publish decisive comparative logic — why A has stronger/weaker transmission than B, why one branch captures more of the event than another, and what would reverse the conclusion — instead of serial company mini-profiles or internal score tables. If research identifies an overall winner, Deep should explain the logic; if not, preserve the competition and resolution condition.

For event-led stories, `EVENT_TO_COMPANY` requires:
`trigger/change -> mechanism -> company exposure -> operating/financial expression -> verification/reversal condition`.
Policy-led copy must reflect the material chronology in the private catalyst ledger rather than a superseded phase.

`FINANCE_BROAD` is an independent acquisition rebuild, not shortened Deep.

## Publication and delivery

Current PublicationFitness gates: `FACT_INTEGRITY`, `RETENTION`, `COMPANY_GROUNDING`, `STRUCTURE_NUMBERING`, `ORIGINALITY`, `AUTHORIAL_STYLE`, `COMPLIANCE`, `PAYOFF`. MAJOR/CRITICAL findings block PASS. Same-session critics remain `CHAT_SELF_REVIEW`.

Originality is evidence-bound; close paraphrase/patchwriting requires revision. Natural prose remains voice/material/story first.

Load progressively: research/cognition `references/research.md`, `references/private_research.md`, `references/knowledge.md`; audit `references/audit.md`, `references/reader_value.md`; editorial/title/draft `references/editorial.md`, `references/hooks.md`, `references/style.md`; market explanation `references/market_explanation.md`; platform `references/platforms.md`; delivery `references/delivery.md`; evolution `references/maintenance.md`, `references/proactive_resolution.md`.

New ordinary work defaults to `PORTFOLIO + WORD_FILE_ONLY`: `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX`, `AUDIT_DOCX`. Buy/sell, entry timing, target price, position sizing and covert equivalents remain prohibited.

## Executable proactive resolution before user escalation

`financial_writing_agent/proactive_resolution.py` owns recovery receipts and user-escalation admission. Recover from available evidence before asking the user; unresolved escalation must pass `require_user_escalation_admission`.

## Evolution and completion

Financial evolution follows `problem/evidence -> cognition -> alternatives -> DecisionEnvelope -> candidate -> regression/eval -> controlled promotion -> production reread -> live observation -> keep/repair/rollback/retire`. Common/cross-domain changes upcall UAOS.

Article identity authority is `workspaces/articles/{task_id}/STATE.json::task_id`. Completion requires current outputs, admitted research decision + required private research, PublicationFitness, mechanical/render QA, state/artifact reconciliation and accurate assurance. Green mechanical tests or documentation alone are not semantic publication proof.
