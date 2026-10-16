---
name: financial-writing-agent-uaos
scope: publishable A-share financial content
---

# Financial Writing Agent — UAOS Entry

Controller/common authority: `D1traverser-debug/universal-agent-os@main`. Financial business authority: this repository on promoted `main`.

UAOS owns cross-domain governance/common capabilities. Financial owns article identity/state, task requirements, product/business rules, research/writing architecture, domain evolution evidence and deliverables. Parent/controller IDs and Financial article IDs are distinct namespaces.

## Bootstrap

A fresh chat may select Financial Writing directly. Once selected, use `DOMAIN:financial_writing` directly; normal article turns do **not** traverse a live UAOS business proxy.

Before material work read `.uaos/ADAPTER.json`, `.uaos/MANIFEST.json`, `.uaos/CAPABILITIES.json`, `config/EXECUTION_CONTRACT.json`, then only current-stage references. Binding drift blocks affected work.

Lifecycle:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`.

## Current admission and task requirements

Current tasks use `financial_writing_agent.current_admission`, bind `writing_kernel_version=1.0`, `private_research_contract_version=1.1`, and for post-promotion tasks `task_requirement_contract_version=1.0`.

Hard quality gates:
- leave `RESEARCH` only with admitted `DecisionEnvelope` + `PrivateResearchBrief`;
- leave `EDITORIAL` only with required Deep/Broad `StoryBlueprint`;
- `EDITORIAL_AUDIT` PASS/REVISE requires product-specific `PublicationFitness`.

Task-specific requirements become owner authority through `current_admission.apply_task_requirement_change`; chat memory and side feedback files are evidence, not substitutes. The requirement authority carries revision/history/digest, every later current-admission mutation binds that digest, and a material requirement change invalidates from the narrowest legal workflow target (`RESEARCH`, `EDITORIAL`, `TITLE`, `DRAFT`, or `DELIVERY`).

Before material work for a scope, call `current_admission.requirement_context_for_scope` for `RESEARCH`, `PRIVATE_RESEARCH`, `FINANCE_DEEP`, `FINANCE_BROAD`, `PLATFORM_INTERACTION`, or `DELIVERY`. Detailed semantics: `docs/task_requirement_authority.md`.

User feedback is high-weight evidence, not automatic domain/global rule authority. Requirement admission and evolution promotion are separate decisions.

## Research

Research follows `prior cognition -> value-chain preflight -> company universe -> current evidence -> adversarial/counterexample search -> saturation -> private-research synthesis -> thesis adjudication -> company comparison -> Research Audit`.

`PrivateResearchBrief` follows `references/private_research.md` and must retain, where material: full economic/market universe, company-level realization, market cap/liquidity, catalyst chronology/freshness, benefit tiers, short-horizon role hypotheses, market structure, counterfactuals, negative cases, scenario/falsification logic and publication distillation. Version 1.1 additionally requires the material catalyst/policy ledger, driver/sustainability/operability/concept map and cross-segment global selection.

`business strongest`, `most durable` and `most likely short-horizon market core` are separate judgments. Current policy/market/company facts must be timestamped and revalidated. Prefer primary government/regulator/exchange/company sources when material.

## Editorial and publication

Research completeness and public selectivity are separate. `FINANCE_DEEP` should publish decisive comparative logic rather than the private research directory unless the active task requirement explicitly says otherwise. `FINANCE_BROAD` is an independent acquisition rebuild, not shortened Deep.

For event-led explanatory sections use `EVENT_TO_COMPANY`:
`trigger/change -> mechanism -> company exposure -> operating/financial expression -> verification/reversal`.

PublicationFitness gates are exactly: `FACT_INTEGRITY`, `RETENTION`, `COMPANY_GROUNDING`, `STRUCTURE_NUMBERING`, `ORIGINALITY`, `AUTHORIAL_STYLE`, `COMPLIANCE`, `PAYOFF`. Same-session semantic review remains `CHAT_SELF_REVIEW`.

Load progressively: research `references/research.md`, `references/private_research.md`; audit `references/audit.md`, `references/reader_value.md`; editorial/draft `references/editorial.md`, `references/hooks.md`, `references/style.md`; market `references/market_explanation.md`; platform `references/platforms.md`; delivery `references/delivery.md`; evolution `references/maintenance.md`, `references/proactive_resolution.md`.

Default output is `PORTFOLIO + WORD_FILE_ONLY`: `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX`, `AUDIT_DOCX`; current admitted private research may additionally require visible `PRIVATE_RESEARCH_DOCX`. Buy/sell, timing, target price, position sizing and covert equivalents remain prohibited.

## Problem closure and evolution

Parent cognition/search depth is owned by current UAOS `config/DELIBERATION_POLICY.json`; Financial does not copy a competing parent algorithm. For requirement drift, compare requirement admission/transcription, stage binding, stale downstream evidence, host/context and other plausible causes before selecting one intervention.

### Executable proactive resolution before user escalation

`financial_writing_agent/proactive_resolution.py` owns recovery receipts and `require_user_escalation_admission`. Recover from available authority/evidence before externalizing a plausibly recoverable dependency to the user.

Financial-local evolution follows `problem/evidence -> causal comparison -> bounded intervention -> regression/eval -> controlled promotion -> production reread -> live observation`. Common/cross-domain findings upcall UAOS.

Article identity authority is `workspaces/articles/{task_id}/STATE.json::task_id`. Completion requires reconciled owner state, current active requirements when enabled, admitted research/private evidence, PublicationFitness, canonical Word/mechanical/render/visible-delivery evidence and accurate assurance.