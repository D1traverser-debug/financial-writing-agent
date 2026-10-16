# Financial Writing System Handoff — 2026-10-16

Status: `SYSTEM_HANDOFF__PRIVATE_RESEARCH_1_1__CURRENT_WORK_SAVED`
Authoritative repository: `D1traverser-debug/financial-writing-agent@main`
Package version: `1.0.3`
Writing kernel: `1.0`
Private research contract for new tasks: `1.1`
Historical private research compatibility: explicit `1.0` states remain valid against the 1.0 module set.

## 1. What changed in the Financial Writing system

Every new Financial Writing task must admit a digest-bound `PrivateResearchBrief` before leaving RESEARCH. Contract 1.1 retains the original 12-module private-research layer and adds three mandatory jobs:

1. `material_catalyst_and_policy_ledger`
   - Build an evidence-bounded ledger of all known materially relevant events under the declared topic/time scope before choosing the headline catalyst.
   - Policy research is chronological and two-sided: tightening, easing, suspension, reduction, extension, exemption, retaliation, expiry/review and rollback/replacement phases must be retained when material.
   - Tariff research must check reciprocal/counter-tariff changes, de minimis rules, exemptions, suspensions, negotiated reductions and extensions when relevant.

2. `driver_sustainability_operability_and_concept_map`
   - Separate immediate driver, sustainability, A-share market operability and concept/sector identity.
   - Distinguish economic truth from price-driver identity and from optional concept labels.
   - Keep total market cap, float market cap, liquidity, turnover, board regime, current height, stock character and competing themes when material.

3. `cross_segment_global_selection`
   - After within-segment `why A rather than B` comparison, run a second all-domain selection across segment winners, high-position/sentiment candidates and capacity candidates.
   - Incorporate catalyst directness, benefit magnitude, realization, durability, scarcity, business stage, market cap/liquidity, current height/stock character, first-price-discovery advantage, concept recognition/contamination and current market/theme turnover.
   - Role vocabulary is not a quota. Low liquidity may support only one true core; one company may legitimately combine high-board/theme-leader/capacity roles. If no unique core is justified, retain challenger(s) and role-switch conditions.

The original modules remain mandatory as applicable: company/value-chain universe, business granularity, market cap/liquidity, catalyst strength/freshness, benefit tiers, short-horizon role map, market structure/positioning, within-segment counterfactual comparison, negative/falsification pool, scenario tree, next-window validation and publication distillation.

## 2. Deep publication rule added

`FINANCE_DEEP` must preferentially publish decisive causal comparisons instead of serial company mini-profiles when material multi-company/multi-branch evidence exists.

The reader-facing logic should explain:
- why A has stronger/weaker transmission than B under the same catalyst;
- why one branch captures more or less of the event/policy profit transfer than another;
- economic winner versus market-recognition winner when they differ;
- durability and reversal conditions;
- after subsegment winners are known, which business model/company has the strongest overall logic under the event, or why no unique winner is yet justified.

Internal tactical machinery such as exhaustive-universe bookkeeping, score tables, card-position mechanics and next-day trading plans remains private unless it materially improves the reader product.

## 3. Admission / audit behavior

- New tasks bind `private_research_contract_version=1.1`.
- Leaving RESEARCH requires admitted `DecisionEnvelope` + admitted `PrivateResearchBrief`.
- The private brief is persisted in `quality_evidence.private_research_brief` and SHA256-bound to the RESEARCH receipt.
- Revision back to RESEARCH invalidates stale research decision/private-research evidence.
- RESEARCH_AUDIT must reject material event/policy omissions, one-sided policy chronology, vague driver/sustainability/operability scoring, concept-attribution contamination, missing global-selection pass, forced role quotas, stale time-sensitive market fields, or Deep distillation that loses decisive comparisons.
- Historical tasks explicitly carrying private-research 1.0 remain valid under 1.0. A 1.1 task cannot submit a 1.0 brief to bypass the added jobs.

## 4. Tool/source policy

Prefer free or already-available authoritative tools/sources when sufficient. For policy/events prefer primary government/regulator/exchange/company sources before secondary summaries. Paid/external crawling should be used only when it materially closes a real coverage gap. Tool cost never authorizes invented evidence.

## 5. Current cross-border-ecommerce task state

Task: `cross-border-ecommerce-20261016-v2`
Authoritative state file: `workspaces/articles/cross-border-ecommerce-20261016-v2/STATE.json`
Current owner state at handoff:
- `status`: `IN_PROGRESS`
- `current_stage`: `EDITORIAL_AUDIT`
- `next_action`: `execute and persist EDITORIAL_AUDIT`

Important compatibility note: this task was created before the current private-research marker. Its authoritative state does **not** contain `private_research_contract_version=1.1`, and its original RESEARCH artifact predates the user's later full-universe/private-research requirements. Therefore do not resume it by simply accepting the old EDITORIAL_AUDIT as current-quality evidence.

Existing later research assets and locally generated V5 Word files are evidence/sample material only, not an admitted PrivateResearchBrief 1.1 state. Relevant repo assets include the full-universe feedback and later classification/research files under the task workspace. Local prior deliverables included:
- `CROSS_BORDER_RESEARCH_REPORT_V5.docx`
- `cross_border_ecommerce_FINANCE_DEEP_V5.docx`
- `cross_border_ecommerce_FINANCE_BROAD_V5.docx`

These do not supersede owner state.

## 6. Required next-chat continuation for the cross-border task

When a new chat says to inherit the Financial Writing system and continue the cross-border task:

1. Read current `UAOS_SKILL.md`, `.uaos/ADAPTER.json`, `.uaos/MANIFEST.json`, `.uaos/CAPABILITIES.json`, `config/EXECUTION_CONTRACT.json`.
2. Read `references/private_research.md`, `references/research.md`, `references/audit.md`, `references/editorial.md`.
3. Read `workspaces/articles/cross-border-ecommerce-20261016-v2/STATE.json` and the later research/feedback assets.
4. Apply resume-compatibility admission because the task predates the private-research 1.1 marker; do not inherit current semantic assurance from old artifacts.
5. Re-open/rebuild RESEARCH as required and admit a real PrivateResearchBrief 1.1, including:
   - full material company/value-chain universe;
   - complete materially relevant event/policy ledger, including tightening and easing/reduction/suspension/extension phases (for example US/China reciprocal tariff chronology, de minimis changes, EU low-value package rules, and other material policy reversals/extensions within scope);
   - company business stage/financial realization;
   - total/float market cap and liquidity for material short-horizon candidates;
   - driver/sustainability/operability/concept map;
   - within-segment comparisons;
   - cross-segment global selection under current liquidity/sentiment constraints;
   - short-horizon role hypotheses, challengers and role-switch conditions;
   - negative/falsification pool, scenario tree and next-window validation.
6. Rebuild StoryBlueprint(s) from the re-admitted research. Deep must emphasize causal comparison and overall logic selection; Broad remains an independent rebuild.
7. Continue the canonical workflow through PublicationFitness, Word delivery, mechanical audit, render QA and final audit.

## 7. User-specific default interpretation now encoded

For every Financial Writing task, “private research brief” means the complete internal analytical workbench, not a representative-company summary. It must be detailed enough to support both industry/business judgment and short-horizon A-share market-selection reasoning when that behavior is material.

The published article is a separate product. It should absorb the strongest comparative and causal conclusions without narrating the entire internal research process.

## 8. Verification checkpoint

At this checkpoint:
- package remains `1.0.3`;
- writing kernel remains `1.0`;
- new tasks bind private-research contract `1.1`;
- unit/trajectory tests and executable-contract evaluation have already passed during the upgrade sequence;
- the remaining reconciliation being finalized is mirrored-reference/static-audit consistency, followed by isolated wheel and DOCX render smoke.

Do not claim full production verification from this checkpoint alone. In a new chat, inspect the latest `main` GitHub Actions run. If the latest full chain is green, treat this handoff as production-verified; otherwise fix the concrete failure before continuing semantic work.
