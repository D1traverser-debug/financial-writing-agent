# Financial Writing Agent — Current Architecture

Version: `0.9.0`
Date: `2026-10-15`

## Boundary
UAOS is the sole cross-domain parent/control plane. This repository is one Financial business domain and can run directly as the current Agent/work plane after domain selection.

UAOS owns cross-domain selection/governance, hosted common capabilities, shared product-engineering method and parent-session continuity. Financial Writing independently owns product requirements, article identity, lifecycle, workflow, business/output contract, research/editorial/style/platform/delivery rules, article state, domain learning/evals and artifacts.

The parent/controller identity namespace and Financial article identity namespace are distinct. They may be related by an opaque state reference, but their IDs are not required to match.

Normal Financial business turns do not require a live UAOS proxy.

## Current locations
- Domain entry: `UAOS_SKILL.md`
- Product requirements: `docs/product_requirements.md`
- Reader-value/current publishing rule: `references/reader_value.md`
- Platform routing: `references/platforms.md`, `financial_writing_agent/routing.py`
- Business execution contract: `config/EXECUTION_CONTRACT.json`
- Identity-free business/output contract: `financial_writing_agent/models.py::TaskContract`
- Article identity/state: `workspaces/articles/{task_id}/STATE.json::task_id`
- Canonical workflow: `financial_writing_agent/workflow_spec.py`
- Mutation/recovery guards: `owner_guard.py`, `owner_lifecycle.py`
- Quality/evolution evidence: `quality_regression.py`, `evals/`

## One research trajectory, three publication products
A topic has one Financial article identity, one audited evidence base and one workflow trajectory. The product can emit three reader products plus audit evidence:

1. `FINANCE_DEEP_DOCX` — deep finance/review long-form for 韭研公社、东方财富、微信公众号.
2. `FINANCE_BROAD_DOCX` — acquisition long-form for 微信公众号、头条号、百家号、网易号、企鹅号.
3. `PLATFORM_INTERACTION_PACK_DOCX` — independently rewritten short image-text / 微头条 / 动态 copy for 微信公众号、头条号、百家号、网易号.
4. `AUDIT_DOCX` — durable audit evidence.

These are output products, not separate agents/runtimes/states.

## Distribution-mode compatibility
New default mode is `PORTFOLIO`, producing Audit + Deep + Broad + Interaction Pack.

Broad-feed-only targeting uses `ACQUISITION`, producing Audit + Broad + Interaction Pack.

Historical contracts remain stable:
- `DUAL` retains Deep + Broad + Audit;
- `FINANCE_BROAD` retains Broad + Audit.

The owner guard validates each stored state's own immutable output contract; the release does not rewrite historical receipts or completed states.

## Research and Company Decision Map
Research first builds the evidence/universe ledger. When there are two or more `MATERIAL` companies, current Research admission requires a `CompanyDecisionMap`.

The map uses topic-specific dimensions such as business/concept purity, current scale/mix, realization speed, earnings sensitivity, evidence strength and adverse variables when relevant. It ends in a named current comparative verdict and explicit change conditions.

This is decision-useful financial analysis, not trading advice. The architecture permits evidence-bounded relative judgments (`more direct`, `faster realization`, `harder evidence`, `higher elasticity but less certain`) while compliance still blocks buy/sell, entry timing, target price, position sizing and covert equivalents.

## Reader-value publication boundary
Research/audit evidence contains source provenance. Publication products are source-private: research/source identity is removed when it exists only to signal diligence. Attribution remains only when speaker/issuer identity is part of the claim itself.

The Reader Funnel has three hard surfaces:
- selected title: concrete change + finance-wide stake + real unresolved payoff;
- first three complete sentences collectively perform hard fact/anomaly + finance-wide consequence + material unresolved payoff;
- H1s are information-bearing and create continuation value.

Natural Authorial Prose uses title/H1/body template-cluster checks plus semantic review. It targets earned argument progression and structural variation, not AI-detector evasion.

## Image-safe section-entry architecture
When an H1 has H2/H3 children, `DRAFT` must include a substantive lead paragraph between the H1 and lower-level heading. This paragraph both bridges the argument and provides the user a stable place to insert an H1-related image without placing it directly against heading styles.

The Financial runtime does not generate those images.

## Workflow
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`

Reader-value/product checks are admission conditions inside this same workflow; no second quality controller is introduced.

## Hosted cognition architecture
Financial consumes UAOS-hosted cognition through `.uaos/CAPABILITIES.json`.

Every detected problem follows:
`micro diagnosis -> macro goal/topology alignment -> governing-assumption challenge -> relevant external research -> repair selection`.

Risk may add counterexample search and genuinely independent evidence. Financial keeps domain ownership unless the cause is common/cross-domain.

## Governed evolution architecture
Financial owns domain business-rule evolution; UAOS owns common/cross-domain evolution.

Domain evolution path:
`problem/feedback -> research+reflection -> root-cause/generalization -> alternatives -> candidate -> regression/eval -> Financial promotion -> post-promotion observation -> keep/rollback/retire`.

The 2026-10-15 reader-value change originated from material user feedback attached to `huangjiu-high-end-channel-20261015` and is generalized only to the failure classes demonstrated by evidence. Huangjiu-specific facts/rankings do not become global rules.

## Product architecture review
`docs/product_requirements.md` owns current product requirements. `references/reader_value.md` owns the current publishing semantics promoted from this product review. `config/policy.json` makes mechanically/semantically enforceable requirements explicit.

Major future feature families must reconcile user outcome, functional/non-functional requirements, workflow/state, failure/recovery, evidence/assurance, acceptance/evals, ownership boundaries and non-goals before promotion.

## Capability compatibility
`.uaos/CAPABILITIES.json` declares hosted common capabilities and minimum UAOS common-capability contract. These declarations do not transfer article identity, product requirements, workflow or business-rule ownership to UAOS.

## Invariants
- one Financial business-state authority per article;
- `STATE.task_id`, receipts, workspace paths and artifact refs form one domain-owned identity chain;
- `TaskContract` is an identity-free value object;
- no parent/child ID equality requirement;
- no second Financial runtime/controller for Deep/Broad/Interaction outputs;
- direct child activation does not require a live parent proxy;
- every detected problem inherits the UAOS research/reflection floor;
- domain evolution promotes only evidence-backed Financial rules at justified scope;
- historical distribution-mode semantics and receipts remain immutable provenance;
- missing hard capability blocks only affected work.

The retired domain controller/continuation namespace `continuity/` remains forbidden.
