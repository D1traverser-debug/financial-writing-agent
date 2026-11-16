# Financial Writing — General Writing Stability Audit

**Date:** 2026-11-16  
**Scope:** Entire Financial Writing product, all topics and all supported article products.  
**Repository:** \`D1traverser-debug/financial-writing-agent\`  
**CAOS:** No CAOS source, configuration, Skill, PR or runtime was changed.

## 1. Correct product objective

The objective is not to complete one article or optimize one topic. It is to make **every Financial Writing task reliably understand the user's goal, perform the required research and reasoning, produce a valuable article, and deliver a verified result**.

Most of the process is invariant. The specific research emphasis is conditional on material relevance and user scope. Narrative form and expression remain open and content-led.

## 2. Existing system architecture

The repository already defines one canonical ten-stage workflow:

\`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT\`.

It also defines a shared research spine, separate Deep/Broad writing branches, a separate interaction branch, evidence admission and revision invalidation. The product requirements and Style/Editorial references explicitly state that form follows content, there is no single universal story template, and sentence/paragraph geometry must not be forced.

Therefore the primary gap is **not the absence of another topic-specific workflow or more fixed prose rules**.

## 3. Historical cross-topic evidence harvested

Four existing workspaces already contain Deep/Broad outputs across different topic families:

| Existing task | Topic family | Existing outputs | Audit assurance | Owner quality evidence |
|---|---|---|---|---|
| \`fw-20261012-ai-security-6dd14859\` | Technology/security sector event | Deep + Broad | CHAT_SELF_REVIEW | Empty |
| \`huangjiu-high-end-channel-20261015\` | Consumer beverage/channel transformation | Deep + Broad | CHAT_SELF_REVIEW | Empty |
| \`ice-snow-economy-20261013\` | Consumer tourism/industry multi-company | Deep + Broad | CHAT_SELF_REVIEW | Empty |
| \`meta-muse-wonder-ai-20261013\` | Technology event/enterprise application mapping | Deep + Broad | CHAT_SELF_REVIEW | Empty |

These artifacts have been added to \`evals/quality_regression.json::diagnostic_samples\` with immutable Git blob bindings. They are useful for cross-topic diagnostics and regression review, but **none is counted as independent quality acceptance or promotion evidence**.

## 4. Verified quality-evidence gap

The promotion corpus currently has only two complete cases:
- one real user rejection case;
- one external held-out benchmark;
- only one complete held-out topic family;
- only FINANCE_DEEP represented in the complete corpus.

The existing evaluator correctly requires at least two complete held-out topic families and mode-specific evidence. FINANCE_DEEP remains diagnostic-only; FINANCE_BROAD remains unauthorized for quality promotion. The four harvested workspaces do not close this gap because their audits are same-session self-reviews and their \`quality_evidence\` is empty.

This is a system-wide evidence deficit, not a reason to keep the next work centered on one historical article.

## 5. Root causes of unstable quality assurance

1. **Task-level continuation was mistaken for system-level progress.** A single article's current state was repeatedly reported as the next objective, making one task look like the definition of the whole product.
2. **Engineering proxies were more complete than content evidence.** Stage graphs, schemas, receipts and CI can prove process integrity, but not that the research is sound, the article is valuable or the expression is effective.
3. **Self-review was mistaken for stronger quality evidence than it is.** A same-session CHAT_SELF_REVIEW can be useful for revision, but cannot independently validate itself.
4. **The corpus is too narrow for generalization.** Two complete cases and one held-out topic family cannot establish stable performance across topics or both content modes.
5. **Expression can be over-regularized.** Historical corrections already rejected fixed opening and rhetorical geometry. More quotas would create a new template rather than better writing.

## 6. Generalized operating model

### Fixed for every task
- recover the user's actual goal, reader, scope and deliverable;
- use prior knowledge as a hypothesis and revalidate material/current claims;
- acquire and normalize evidence with source provenance;
- test competing explanations and counterevidence;
- select and justify the thesis;
- preserve evidence, uncertainty and publication choices into editorial planning;
- draft, revise and audit factual integrity, originality, reader value, authorial expression and compliance;
- verify all requested outputs and report unresolved items.

### Conditional by task
Company-universe enumeration, full value-chain coverage, short-horizon market-role analysis, policy transmission, financial-statement decomposition, supply-demand modeling and other specialist modules are activated only when the task scope and evidence make them material. They do not alter the canonical workflow.

### Open by content and reader
Narrative engine, title angle, opening strategy, section order, paragraph rhythm, technical depth, length, tone and voice are chosen for the actual material and reader. A StoryBlueprint is a planning aid, not a writing mold.

## 7. Stability acceptance model

Stability means different tasks consistently meet the same substantive obligations while using different editorial choices where appropriate. It does not mean identical prose.

For every target content mode, quality promotion requires:
- a complete real-user rejection case;
- at least two complete held-out topic families;
- immutable artifact bindings;
- a semantically verified candidate change and counterexample evidence;
- blind pairwise candidate-versus-baseline reviews with position swap and exact case binding;
- zero hard-invariant regressions.

A task passes only when applicable user requirements are visibly satisfied or explicitly OPEN/BLOCKED, material claims are supported, reasoning survives counterevidence, the article's form serves its reader, semantic reviews cite actual text, and requested deliverables are verified.

## 8. Changes made in this revision

- Added the general writing stability contract to Product Requirements and the executable contract.
- Clarified in the operating Skill that system-wide stability must be assessed across topic families while keeping expression content-led.
- Harvested four historical Deep/Broad pairs into a diagnostic-only inventory with immutable Git blob bindings; incorporated the user's previously recorded cross-product editorial feedback and explicitly included the third interaction product.
- Added regression tests for topic-independent workflow, adaptive expression and non-promotion of self-reviewed samples.
- Updated system status and the problem journal to make cross-topic quality—not any one article—the next business objective.

## 9. Remaining OPEN work

- Run real, current, end-to-end writing tasks across multiple topic families and all three target products (Deep, Broad and Platform Interaction); current historical samples cover only Deep/Broad.
- Obtain independent blind editorial judgments; do not reuse same-session self-review as independent evidence.
- Add complete held-out cases until each mode meets the existing quality promotion contract.
- Verify the live model and provider-backed stage persistence path separately from deterministic CI.
- Complete independent review of PR #84 and the separate Provider Action deployment decision.

**Conclusion:** The common workflow is already defined. The missing proof is that it consistently produces strong real articles across different topics. The correct next step is cross-topic business validation and targeted root-cause repair—not another single-article-specific rebuild.


## 10. Existing user-feedback evidence now included in the general contract

The 2026-10-15 Huangjiu feedback is not a one-off article instruction. It explicitly called for system-level correction and identifies cross-product requirements that apply conditionally across the Financial Writing portfolio:

- keep source provenance in research/audit rather than narrating it in publication copy;
- remove model-like rhetorical molds and abstract staging without imposing a generic humanizer;
- optimize the long-form reader funnel from title and opening through section continuation and completion payoff;
- require explicit, evidence-bounded company comparison when multiple companies materially differ;
- bridge H1 to lower-level headings with a substantive section lead when nested headings are used;
- use meaningful numbering and information density where they improve navigation;
- treat short image-text/dynamic interaction as a third first-class publishing product.

The current repository already models \`FINANCE_DEEP\`, \`FINANCE_BROAD\` and \`PLATFORM_INTERACTION\` outputs in \`TaskContract\`. This revision makes all three explicit in the system-wide stability contract. The interaction product must derive from the same audited research package, introduce no new facts, and receive its own quality evaluation. The four historical article workspaces currently provide Deep/Broad diagnostics only; they do not provide interaction-product quality evidence.

These are quality obligations, not a fixed writing formula. Applicability depends on product and material; narrative engine and expression remain content-led.


## 11. Concrete historical failure reproduced and repaired

The Huangjiu user-rejected article contains several source-framing constructions in publication prose: a named broker's "行业深度报告", the broker "进一步指出", a "研报给出的" logic, association research framing, and an association disclosure lead-in. The previous deterministic source scanner did not cover these forms. This explains how the article could pass a same-session editorial/mechanical route while still violating the user's explicit publication-source privacy requirement.

The source scanner has now been expanded to detect:
- named broker report framing (including "深度报告");
- named broker/analyst attribution verbs;
- report/研报 verbs such as "给出、估算、提出、梳理";
- named industry-association/research attribution and disclosure framing.

A regression test reads the actual rejected Huangjiu article from the repository and asserts these failures are detected. Separate positive controls verify that ordinary company financial facts are not flagged. The scanner remains a deterministic trigger; source identity exceptions still require semantic justification. This repairs a concrete shared gate defect, not just the documentation.


## 12. Exact-head verification and integration

- Source/privacy scanner implementation head: \`8c8dc0595aae9f63c889363db6a78216b81af6fe\`.
- Exact implementation-head CI: [43833247888](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43833247888) — 727 tests passed; 88% Python statement coverage; every workflow step passed.
- PR #84 was squash-merged to \`main\` as \`7dbde945e98712856d7d6a19b8fe06b2efc500ab\`.
- Exact main merge-head CI: [43833864946](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43833864946) — 727 tests passed; 88% Python statement coverage; every workflow step passed.

The source-provenance regression is now integrated and CI-verified on main. The **overall Financial Writing quality status remains OPEN**: deterministic engineering checks do not replace independent blind article evaluation across multiple topic families and all three publishing products.

## 13. Platform Interaction quality-evaluator coverage correction

The product contract already defines `PLATFORM_INTERACTION` as a first-class, separately evaluated publishing mode. Its platform contract requires an information-bearing hook, a compact fact-to-financial-consequence chain, a natural interaction prompt, source privacy, and the same factual/uncertainty boundaries as long-form products.

**Root cause found in implementation.** `financial_writing_agent.quality_regression._MODES` accepted only `FINANCE_DEEP` and `FINANCE_BROAD`. The evaluator therefore rejected any complete Interaction rejection or held-out case as an invalid content mode. Delivery and Word-render tests covered the interaction pack, but the cross-topic quality evaluator was not tested against every product mode declared by the manifest.

**Selected correction.** Reuse the existing generic mode-scoped corpus, candidate-distillation, immutable case-binding, blind pairwise, position-swap, and hard-invariant regression machinery. Add `PLATFORM_INTERACTION` to the accepted mode set. Do not create a second evaluator or weaken the per-mode rejection and held-out requirements.

**Regression evidence.** PR #86 adds:
- a positive Interaction-mode corpus/distillation/promotion path;
- a negative test proving Deep evidence cannot satisfy Interaction's rejection and two-held-out-family requirements;
- a cross-contract test that every publishing mode declared by `FINANCIAL_MANIFEST.json` is accepted by the quality-regression schema.

**Exact-head engineering verification.** The code-only candidate commit `7d7095f3c53899752ab3ac01cbaf5a7f43435aef` passed run [43837219690](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43837219690): 730 tests passed, 88% Python statement coverage (8,178 statements; 980 missed), Portfolio Coordinator 91%, Standalone Runtime 89%, Writing Kernel 81%.

A documentation/journal follow-up at `d58038056068ee4bbe45127a9d5296a971b27b03` exposed two stale assertions that hard-coded P-04 as the latest incident (728 passed, 2 failed). The tests were corrected to validate the current latest-incident pointer/reference dynamically while retaining P-01 through P-04 as historical open items. Final candidate head `5b6aec5415c7cdce8288f29175c3724260184a45` passed exact-head run [43838436832](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43838436832): 730 tests passed; 88% statement coverage; Portfolio Coordinator 91%, Standalone Runtime 89%, Writing Kernel 81%. Whole-tree audit: 342 tracked files, 133 Python AST parses, 54 JSON parses, 55,446 decoded text lines, zero warnings/errors. DOCX render, four synthetic Word product binaries/page checks, and negative business replay passed.

**Quality status remains OPEN.** No Interaction real-user rejection or two-family held-out corpus was added. The new unit fixtures are synthetic contract tests, not editorial evidence. No blind external reader evaluation, live article production, provider-backed persistence, or user acceptance is claimed. PR #86 remains a Draft candidate pending independent review and exact-head follow-up after any further change.

---

## 14. Root cause: the invariant workflow and open editorial decisions were not bound to each execution

The product requirements already define one stable ten-stage workflow, conditional research depth and content-led expression. The runtime did not persist one prompt-bound execution profile for all semantic passes. Topic-diverse tests therefore did not prove that the same process and mandatory QA obligations were retained while editorial decisions adapted to material and reader needs.

### 14.1 Runtime correction candidate

Draft PR #88 replaces whole-task classification with:
- a typed `WritingExecutionProfile` carrying the invariant `FINANCIAL_ARTICLE_10_STAGE_V1` contract;
- exact binding of active explicit/corrective requirements and separately weighted preferences to TaskRequirementAuthority;
- locked versus open editorial decision domains and material conditional modules;
- persistence in the existing Portfolio Context and propagation to every semantic pass;
- original-prompt hash binding and mandatory profile refresh when requirements change;
- read compatibility for historical Portfolio Context 1.0.

No parallel workflow or whole-task taxonomy is introduced.

### 14.2 Acceptance boundary

Tests must verify:
- the same canonical business graph and mandatory QA obligations remain present;
- explicit/corrective requirements are neither omitted nor invented;
- preferences are not hardened into requirements;
- locked editorial decisions are preserved while open decisions remain content-led;
- specialist research modules activate only when material;
- every semantic pass receives the same prompt-bound profile;
- requirement changes refresh the profile and invalidate dependent evidence;
- historical context 1.0 remains readable.

These are engineering/dataflow checks only. They do not prove the model always interprets the request correctly or that generated articles satisfy readers. Cross-topic, per-product, independently reviewed real article evidence and actual user acceptance remain OPEN.
