---
name: financial-writing-agent-uaos
scope: publishable A-share financial content
---

# Financial Writing Agent — UAOS Entry

Controller/common authority: `D1traverser-debug/universal-agent-os@main`. Financial business authority: this repository on `main` after controlled promotion.

UAOS owns cross-domain governance/common capabilities. Financial Writing owns article identity/state, task requirements, product requirements, research/writing architecture, business/output contracts, domain evolution evidence and deliverables. Parent/router IDs and Financial article IDs have no equality requirement; `TaskContract` is intentionally identity-free.

## Start and authority

A fresh chat may select Financial Writing directly. Once selected, `DOMAIN:financial_writing` is the work plane; normal article turns do **not** traverse a live UAOS business proxy.

For material work read `.uaos/ADAPTER.json`, `.uaos/MANIFEST.json`, `.uaos/CAPABILITIES.json`, `config/EXECUTION_CONTRACT.json`, then only the stage references needed. Binding drift blocks the affected capability, not Financial ownership.

## Workflow, requirements and current admission

Lifecycle:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`.

New tasks use `financial_writing_agent.current_admission`, bind `writing_kernel_version=1.0`, `private_research_contract_version=1.1` and `task_requirement_contract_version=1.0`, and require:
- leaving `RESEARCH`: admitted material `DecisionEnvelope` + admitted `PrivateResearchBrief`;
- leaving `EDITORIAL`: required Deep/Broad `StoryBlueprint`;
- `EDITORIAL_AUDIT` PASS/REVISE: product-specific `PublicationFitness`.

Task-specific requirements are owner authority only after admission through `financial_writing_agent.current_admission.apply_task_requirement_change`. Chat memory, a feedback side file, or the most recent user sentence is not a substitute for the canonical active requirement set. Each admitted requirement records its scope, earliest affected stage and evidence ref; the authority carries a monotonic revision plus canonical digest. Every subsequent current-admission mutation binds that revision/digest in its execution receipt. Requirement changes invalidate only the narrowest affected stage and downstream evidence.

Use `financial_writing_agent.current_admission.requirement_context_for_scope` before material stage/product work to obtain the exact active requirements for `RESEARCH`, `PRIVATE_RESEARCH`, `FINANCE_DEEP`, `FINANCE_BROAD`, `PLATFORM_INTERACTION` or `DELIVERY`. User feedback remains high-weight evidence, not automatic Financial/global rule promotion; task requirement admission and domain evolution are separate decisions.

A side file, chat claim or naked PASS is not current quality or requirement evidence. Historical states explicitly carrying private-research 1.0 remain provenance-compatible and validate against the original 1.0 module set. Pre-requirement-authority current tasks may be upgraded by an explicit requirement-change transaction without rewriting historical receipts.

## Research invariants

For material thematic/company work, Research performs prior cognition recall, value-chain preflight, listed-company universe recall, current evidence expansion, adversarial/counterexample search, saturation, private-research synthesis, competing-thesis adjudication and Company Decision Map where applicable. Thesis selection follows value-chain coverage; late material discovery invalidates convergence.

Before Research or private-research synthesis, load the active task requirement context for the relevant scope. A task-specific coverage, granularity, market-role or evidence requirement cannot be satisfied merely because an old feedback file exists; it must be active in the requirement authority or explicitly classified as superseded.

`PrivateResearchBrief` is mandatory for new tasks and follows `references/private_research.md`. Version 1.1 requires the original comprehensive private analytical layer plus three hard jobs:
1. `material_catalyst_and_policy_ledger`: all known materially relevant event/policy catalysts under the declared scope, with chronology and tightening/easing/suspension/reduction/extension/exemption/retaliation/rollback states;
2. `driver_sustainability_operability_and_concept_map`: driver type, duration, operational expression and concept/sector mapping;
3. `cross_segment_global_selection`: after within-segment comparison, compare branch winners and market-role candidates globally under current liquidity/sentiment constraints.

The brief must retain, as applicable: economic/market universe coverage, company-level business stage and realization, total/float market cap and liquidity, catalyst freshness, benefit tiers, short-horizon role hypotheses, market structure, within-segment counterfactuals, negative/falsification cases, scenario/verification logic and publication distillation. A company list, score table or several representative names is not equivalent.

`business strongest`, `most durable` and `most likely short-horizon market core` are separate judgments. Role vocabulary is not a quota: constrained liquidity may support only one true core, and one company may combine high-board/theme-leader/middle-army roles when evidence supports it.

Prefer free or already-available authoritative tools/sources when sufficient; for policy/events prefer primary government/regulator/exchange/company sources. Paid/external crawling is justified only when it materially closes a coverage gap. Tool cost never authorizes invented evidence.

`DecisionEnvelope` requires evidence beyond user assertion, credible alternatives, challenged assumptions, counterexamples, rejected paths, rationale, saturation and verification. User feedback is high-weight evidence, not automatic rule authority.

## Research Audit and Editorial

Use `references/research.md` and `references/audit.md`. Research Audit must verify the material event/policy ledger, driver/sustainability/operability/concept analysis, within-segment comparison, cross-segment global selection, active task requirements and unresolved gaps before PASS.

Editorial uses `references/editorial.md`. Before StoryBlueprint generation, load the active `FINANCE_DEEP` and `FINANCE_BROAD` requirement contexts and bind the current requirement revision/digest through current admission. For `FINANCE_DEEP`, research completeness and publication selectivity are separate. Deep should preferentially publish decisive comparative logic — why A has stronger/weaker transmission than B, why one branch captures more of the event than another, and what would reverse the conclusion — instead of serial company mini-profiles or internal score tables. If research identifies an overall winner, Deep should explain the logic; if not, preserve the competition and resolution condition.

For event-led stories, `EVENT_TO_COMPANY` requires:
`trigger/change -> mechanism -> company exposure -> operating/financial expression -> verification/reversal condition`.
Policy-led copy must reflect the material chronology in the private catalyst ledger rather than a superseded phase.

`FINANCE_BROAD` is an independent acquisition rebuild, not shortened Deep.

## Publication and delivery

Current PublicationFitness gates: `FACT_INTEGRITY`, `RETENTION`, `COMPANY_GROUNDING`, `STRUCTURE_NUMBERING`, `ORIGINALITY`, `AUTHORIAL_STYLE`, `COMPLIANCE`, `PAYOFF`. MAJOR/CRITICAL findings block PASS. Same-session critics remain `CHAT_SELF_REVIEW`.

Originality is evidence-bound; close paraphrase/patchwriting requires revision. Natural prose remains voice/material/story first.

Load progressively: research/cognition `references/research.md`, `references/private_research.md`, `references/knowledge.md`; audit `references/audit.md`, `references/reader_value.md`; editorial/title/draft `references/editorial.md`, `references/hooks.md`, `references/style.md`; market explanation `references/market_explanation.md`; platform `references/platforms.md`; delivery `references/delivery.md`; requirement authority `docs/task_requirement_authority.md`; evolution `references/maintenance.md`, `references/proactive_resolution.md`.

Before drafting or delivery, load the current product-specific/delivery requirement context. Delivery formatting rules do not replace task requirements, and task requirements do not bypass deterministic Delivery checks.

New ordinary work defaults to `PORTFOLIO + WORD_FILE_ONLY`: `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX`, `AUDIT_DOCX`. Buy/sell, entry timing, target price, position sizing and covert equivalents remain prohibited.

## Parent cognition binding and domain problem closure

Parent cognition/search depth is owned by current UAOS `config/DELIBERATION_POLICY.json`; this Skill defines no parent cognition floor. Financial retains only domain-native evidence/root-scope/evolution/action gates.

Detected requirement drift is not solved by rereading chat or adding prose reminders. First distinguish task requirement transcription/admission failure, stage-input binding failure, stale downstream evidence and host/context drift. Repair the narrowest evidence-supported owner layer; common/host failures upcall UAOS.

## Executable proactive resolution before user escalation

`financial_writing_agent/proactive_resolution.py` owns recovery receipts and user-escalation admission. Recover from available evidence before asking the user; unresolved escalation must pass `require_user_escalation_admission`.

## Evolution and completion

Financial evolution follows `problem/evidence -> cognition -> alternatives -> DecisionEnvelope -> candidate -> regression/eval -> controlled promotion -> production reread -> live observation -> keep/repair/rollback/retire`. Common/cross-domain changes upcall UAOS.

Article identity authority is `workspaces/articles/{task_id}/STATE.json::task_id`. Completion requires current outputs, admitted task-requirement authority when enabled, admitted research decision + required private research, PublicationFitness, mechanical/render QA, state/artifact reconciliation and accurate assurance. Green mechanical tests or documentation alone are not semantic publication proof.