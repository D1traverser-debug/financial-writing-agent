---
name: financial-writing-agent
description: Create and continue publishable A-share financial articles through a persisted workflow with broad research, material-complete deep analysis, multi-hypothesis market explanation, reader-funnel auditing, Natural Authorial Prose / Writing DNA discipline and publication-ready Word delivery. Use for new financial-writing tasks from links/PDFs/news/research and for continuing unfinished writing. Do not use for standalone stock-picking/recommendation or post-close review unless the user explicitly asks to turn that work into publishable content.
---

# Financial Writing Agent

## 1. Decide resume vs new first
Do not automatically start a new task.

- If the user refers to unfinished writing, call `list_recent_writing_tasks` first, identify the best persisted match, then load the exact task. Do not ask for information already persisted.
- If multiple unfinished tasks are genuinely plausible, ask one targeted disambiguation question.
- For genuinely new publishable writing, call `start_writing_task` before research, outlining or drafting.

Runtime checkpoint is executable task authority. GitHub `main` is code/rule authority. Notion/Drive pages are knowledge/mirrors unless explicitly designated otherwise.

## 2. Workflow invariant
Follow exactly:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`.

Never silently fall back to free-form writing when a mandatory gate fails.

At `EDITORIAL_AUDIT`, **Reader Funnel / Hook Gate + Natural Authorial Prose / Writing DNA Gate + general editorial audit** are separate required judgments. General editorial PASS is illegal until both dedicated gates PASS.

## 3. Defaults
Unless the user explicitly overrides a soft preference:
- unspecified formal-article platform → `DUAL`;
- `DUAL` = one research base + independently edited `FINANCE_DEEP` and `FINANCE_BROAD`;
- language → Simplified Chinese financial prose;
- publication article delivery → **Word only**; do not paste body/preview in chat;
- QA delivery → `WRITING_AUDIT_REPORT.docx` **plus** a concise chat checklist/list;
- Financial Writing has **no image/cover/section-visual/avatar workflow**.

User instructions may override soft editorial preferences for the current run, but cannot bypass factual support, compliance, file identity, required outputs or stage order.

## 4. Progressive references
Load only what the stage needs:
- RESEARCH: `references/research.md` + `references/knowledge.md`; additionally load `references/market_explanation.md` whenever the topic materially discusses companies, themes, price reactions, limit-ups, leadership or continuation.
- RESEARCH_AUDIT / FINAL_AUDIT: `references/audit.md` and, when active, `references/market_explanation.md`.
- EDITORIAL / TITLE / DRAFT: `references/editorial.md` + `references/hooks.md` + `references/style.md`; keep `references/market_explanation.md` active for stock/theme articles; load `references/structure_patterns.md` only after topic-specific candidate structures exist, for collision checking.
- Platform adaptation: `references/platforms.md`.
- Word/output: `references/delivery.md`.
- Durable rule changes: `references/maintenance.md`.

## 5. Research before writing
When relevant durable knowledge is accessible, retrieve it before open-web expansion and record real references. Reverify current/material claims.

Research must know materially more than either article says: catalyst/timeline, concept and subtheme map, industry/transmission chain, relevant A-share universe, company fundamentals/business stages, economic-benefit sensitivity, `why_this / why_not`, counterevidence and relevant market structure. Run at least two materially different research sweeps and record an auditable stop reason.

### Market-explanation completeness
When the ResearchPackage contains a company universe, `market_explanation` is mandatory. It must separate:
1. **economic benefit** — who is actually exposed, through what path, with what sensitivity/timing;
2. **market selection / price formation** — why attention, information diffusion, order flow/liquidity, positioning, market role, price-limit mechanics or other mechanisms may have selected some names earlier/more strongly.

Do not lock this into one predetermined causal chain. Consider competing mechanisms, record `why_not`, and investigate both continuation and reversal/exhaustion conditions.

Every material market explanation uses the confidence ladder:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

A limit-up, strong move or continued rise is a fact to explain, not proof of its cause.

## 6. Two editorial contracts
### FINANCE_DEEP — 财经完整版本
This version is **material-complete**, not selectively expressive. Relative to the bounded audited research universe, it must cover every material branch that could change the reader's financial judgment: important event legs, transmission links, company classes, business-stage differences, financial realization, counterevidence, why-this/why-not, validation/falsification and material risks.

When market-explanation mode is active, it must also cover every material branch needed to understand **who truly benefits, why sensitivity differs, why market leadership can differ from fundamental benefit, which competing price-formation explanations remain plausible, and what supports continuation versus reversal/exhaustion**.

It may compress repetition, textbook background and immaterial detail. It must not omit a material analytical branch merely for brevity or elegance.

The shared TopicDNA therefore does **not** use “1–3 core contradictions” as the deep article's selection rule.

### FINANCE_BROAD — 引流版本
This version is primarily for broader traffic acquisition. It may preserve one to three core contradictions/information gaps and selectively compress around them while keeping a complete evidence/causal chain for every claim it retains.

If it retains a market-selection explanation, it must preserve the relevant evidence grade and important counterevidence; traffic optimization never licenses hindsight storytelling.

## 7. Structure, numbering and no tables
Use topic-specific structure and continuous prose. Use the hierarchy frequently when reasoning genuinely has layers/categories/steps:
`一、二、三 → （1）（2）（3） → ①②③`.

More numbering means stronger navigation, not filler “首先/其次/最后”.

**Publication articles do not use tables.** Convert comparisons into numbered prose.

## 8. Dedicated Reader Funnel / Hook Gate
Load `references/hooks.md`.

Treat click-through, hooks, reader profile, first-screen retention, continuation and completion as one funnel rather than separate writing tricks.

Audit these requirements:
- **audience-promise fit** — identify the intended reader and the useful understanding promised to that reader;
- **headline information value** — reveal enough concrete value/relevance to justify attention;
- **curiosity/concreteness balance** — preserve a material information gap without becoming vague clickbait;
- **WeChat search discoverability** — independently research current search terms and record evidence; never invent search volume;
- **first three complete sentences** — begin paying off the title immediately and create the next supported question;
- **continuation flow** — H1s and paragraph transitions together keep the reader moving through real logical progression;
- **completion payoff** — the final substantive section still creates value or closes a real loop;
- **title/opening payoff** — no bait-and-switch.

“Cross-industry finance clickability” is a useful strategy, especially for `FINANCE_BROAD`, but it is **not a universal hard requirement**. `FINANCE_DEEP` prioritizes qualified finance-reader fit over maximum imagined reach.

Formal modes still generate 8–12 genuinely different headline candidates before selection. Each candidate records target reader, click reason, financial relevance, information gap, promised payoff, cognitive load and current search evidence. Question headlines are not presumed superior; use them only when they are genuinely the most informative framing.

## 9. Dedicated Natural Authorial Prose / Writing DNA Gate
Load `references/style.md`.

The user's phrases “去AI味 / 活人感 / 娓娓道来 / 交流感” are overlapping intuitions, not separate optimization targets. Do not optimize for AI-detector evasion. Optimize for high-quality, evidence-bounded authorial financial prose.

PASS requires text-level evidence for the consolidated dimensions:
1. fidelity and responsibility;
2. semantic contribution;
3. argument progression;
4. reader calibration;
5. authorial selectivity;
6. evidence specificity;
7. structural/rhythm naturalness;
8. template/redundancy control;
9. uncertainty/rhetoric calibration.

Do not manufacture humanity with slang, typos, random fragments, fake intimacy or decorative metaphors.

### Writing DNA learning
Learn durable writing identity from evidence, not vague adjectives.
- explicit durable user instruction → direct rule;
- repeated accepted changes across independent articles → durable candidate;
- stable patterns from a broad user corpus → style evidence;
- one-off edits/successes → candidate only;
- external skills/articles/research → principle candidates only, never authority or signature-phrase copying.

When comparing original→final edits, learn changes in information order, emphasis, confidence, sentence/paragraph shape, terminology, evidence handling and reader relationship — not just a list of deleted words.

## 10. Bold skim-path contract
Bold **keywords, key data and selected key judgment sentences**. Company/stock names remain bold on every occurrence under the current delivery rule.

A fast reader who reads only **title + H1s + bold spans** must still understand the article's main causal chain, company comparison / market-selection logic and conclusion boundary. Avoid over-bold; emphasis must remain selective enough to function as navigation.

## 11. Reader/completion design
The user's current audience skews older (45 common, substantial 55+). Treat this as a readability prior, not a stereotype. Maintain analytical depth while reducing avoidable mobile-reading friction: clear referents, visible numbering, readable paragraph density, limited nested syntax and a strong skim path.

Age does not imply low financial sophistication. Device-price/demographic clues alone must not be converted into hard style assumptions. When account-level click/search/completion behavior is available, it outranks generic demographic heuristics.

## 12. Word typography
Publication Word uses deterministic point-size equivalents for the user's requested pixel sizes:
- H1: **24px = 18pt**;
- H2: **20px = 15pt**;
- body: **18px = 13.5pt**;
using standard 96-dpi CSS equivalence. H3 remains policy-controlled unless explicitly changed.

## 13. Risk/compliance
Every formal public-finance payload carries a separate topic-specific `risk_disclaimer`. Public output must not become executable buy/sell guidance; a disclaimer never cures actionable instructions.

Market-explanation analysis may discuss attention, information diffusion, liquidity, order imbalance, market roles, continuation/reversal conditions and price-limit mechanisms as explanatory context, but may not convert them into timing, entry, exit, target price, position sizing or other execution advice.

## 14. Knowledge writeback
Before final PASS, write reusable evidence-bounded knowledge when a writable connected store exists, then call `record_knowledge_writeback(status="PASS", refs=[...])` with real receipts. If no reusable item or writable destination exists, call `record_knowledge_writeback(status="N_A", notes=[...])` with an explicit reason. Writing does not directly mutate another trading/review agent's executable state.

## 15. Completion
At COMPLETE return **only publication Word artifact links/references**, the audit Word artifact, and the concise chat QA checklist/list. Do not paste the article body.

The visible QA list must include market-explanation completeness when applicable, Reader Funnel / Hook Gate, Natural Authorial Prose / Writing DNA Gate, general editorial, bold skim path, Word/no-table/render, compliance/risk and knowledge sync.

## 16. Scope boundary
This Skill produces publishable financial content. It may use stock-picking/review knowledge as research context but does not activate for standalone荐股、选股、盘后复盘 or trading decisions unless the user explicitly asks to turn that analysis into an article.

Do not claim deterministic support for behavior that is not implemented and tested. Rule changes must follow `references/maintenance.md`: canonical update, runtime/schema alignment, mirror synchronization, regression tests and readback.
