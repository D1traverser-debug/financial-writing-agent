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
