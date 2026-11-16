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
- Harvested four historical Deep/Broad pairs into a diagnostic-only inventory with immutable Git blob bindings.
- Added regression tests for topic-independent workflow, adaptive expression and non-promotion of self-reviewed samples.
- Updated system status and the problem journal to make cross-topic quality—not any one article—the next business objective.

## 9. Remaining OPEN work

- Run real, current, end-to-end writing tasks across multiple topic families and each target content mode.
- Obtain independent blind editorial judgments; do not reuse same-session self-review as independent evidence.
- Add complete held-out cases until each mode meets the existing quality promotion contract.
- Verify the live model and provider-backed stage persistence path separately from deterministic CI.
- Complete independent review of PR #84 and the separate Provider Action deployment decision.

**Conclusion:** The common workflow is already defined. The missing proof is that it consistently produces strong real articles across different topics. The correct next step is cross-topic business validation and targeted root-cause repair—not another single-article-specific rebuild.
