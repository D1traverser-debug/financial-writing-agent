# Reader Value & Decision Utility — Current Financial Rule

Status: `CURRENT_DOMAIN_RULE`
Effective: `2026-10-15`
Revision: `0.9.1-voice-first-calibration`
Owner: `DOMAIN:financial_writing`

This reference owns the Financial Writing requirements promoted from the 2026-10-15 material user feedback on publication-source privacy, Natural Authorial Prose, title/opening/H1 reader funnel, company-decision utility, image-safe section entry and the user's three-product publishing portfolio.

When this file is more specific than an older statement in `hooks.md`, `style.md`, `editorial.md`, `platforms.md` or `delivery.md`, this file governs the listed semantics. The older modules remain authoritative for non-conflicting details.

## 1. Publication-source privacy

Research and audit keep exact source identity, URLs, dates and attribution boundaries. Publication surfaces do not expose the research trail merely to prove that research happened.

Publication copy must not use source-framing such as `XX研报指出`, `据XX报道`, `公开资料显示`, `研究报告认为` or equivalent language when the sentence can instead state the verified fact/mechanism directly with its proper certainty level.

This rule does not erase real agency. If who said/announced/forecast something is itself material to the claim — for example a listed company announces guidance, a regulator issues a rule, or a named institution's forecast is the fact being discussed — attribution may remain. The test is whether removing the speaker would change the claim, not whether naming a source makes the prose look researched.

No publication-tail source/bibliography section is added by default. Provenance remains in the research/audit evidence chain.

## 2. Natural Authorial Prose — voice/material first, AI-pattern diagnosis second

“去AI味” is not a generation style. It is a quality diagnosis applied after the article already has a real authorial position, reader, evidence base and purpose.

The governing objective is **not** to maximize irregularity, slang, short sentences, surprise, detector evasion or any other statistical opposite of AI. Corpus-level differences between human and generated text are evidence for what to inspect, not universal instructions for how every sentence must be written.

### 2.1 Before drafting: bind the article to a real voice source

The drafting pass should first resolve:
- who is speaking: the user's finance-writing account/house voice, not a generic “human writer” persona;
- who is reading: the actual product reader and platform context;
- what the article is trying to establish, dispute, compare or make useful;
- what audited facts, numbers, company differences and uncertainties are available;
- what the author deliberately treats as primary, secondary or not worth expanding.

Voice evidence priority is:
1. the user's own explicitly approved or edited writing samples for the same/similar product;
2. explicit style constraints and durable corrections supplied by the user;
3. the user's current prose signals when they materially clarify register/stance;
4. target platform and finance-genre conventions;
5. generic defaults only when stronger evidence is absent.

Never fabricate anecdotes, first-hand experience, emotion, slang or “human detail” to simulate authenticity. If the material is thin, research more, narrow the article or write shorter; do not stretch one idea into several polished paraphrases.

### 2.2 During drafting: do not write to an anti-AI checklist

The writer should use the evidence and authorial selection pressure to choose the natural structure for this topic. No sentence shell, paragraph-role sequence, punctuation quota, casual-phrase quota or rhythm target is mandatory merely because it is less common in generated text.

The following are **not generation mandates**:
- “every paragraph must perform a different named role”;
- “always vary sentence length”;
- “always avoid `不是X，而是Y`”;
- “always write `verdict -> evidence -> boundary`”;
- “always insert colloquial phrases or rhetorical questions”;
- “always make the structure asymmetrical”.

A single construction may be exactly right. The defect is unearned repetition, not the existence of the construction.

For substantial long-form work, internally compare at least two genuinely different opening/section strategies when the evidence supports multiple plausible routes. Synonym variants or the same outline with renamed headings do not count as alternatives. Use the strongest route; do not expose the tournament in publication copy.

### 2.3 After drafting: use AI-pattern signals as red flags, not verdicts

The audit examines title, H1s, paragraph openings, sentence roles and section moves for **clusters** such as:
- repeated `不是X，而是Y` / `真正的X` / `核心在于` staging;
- repeated `如果...那么/才...` conditionals that avoid making a comparison already supported by evidence;
- identical H1 grammatical molds;
- repeated `否定旧看法 -> 提出新指标 -> 宣布这才关键 -> 小结` sequences;
- noun-heavy abstraction that hides actors, causality or money/orders/profit transmission;
- paragraphs that can be reordered without changing the argument;
- platform caricature: forced口语词、情绪词、短句、互动口令 or emoji added only to look “human”.

These are diagnostic signals. One hit does not prove a problem and does not justify rewriting a passage that is already specific, situated, clear, evidence-bounded and voice-consistent.

Use the **minimum effective revision**: identify the exact weak span, say why it loses reader trust/voice/information, repair that span, and preserve useful roughness elsewhere.

### 2.4 Separate writer and critic jobs without pretending independence

Use the existing workflow rather than adding a new controller:
- `DRAFT`: write from evidence, reader job, author stance and voice anchors;
- `EDITORIAL_AUDIT`: reread in distinct critic passes — **Reader** (where would I stop/skip?), **Editor** (what is redundant/vague/over-structured?), **Style** (where does voice/rhythm suddenly become generic or synthetic?).

These passes may be performed in the same model/session and are useful adversarial critique, but they are **not independent verification**. Their purpose is to expose weak spans, not to manufacture a certification label.

A useful comparative paragraph may naturally follow `verdict -> evidence -> boundary/change condition`, but this is one available analytical shape, not a universal prose order.

## 3. Title + first three sentences + H1 reader funnel

The target is qualified finance-domain reach, not generic sensationalism.

### Total title
A selected title should normally make enough of the following visible for a cold finance reader to care:
- a concrete entity/event/number/change;
- a financial stake such as profit, orders, cash flow, price/volume, company differentiation or policy transmission;
- a real information gap whose payoff requires the article.

This is a reader-value test, not a title formula. A strong title may compress two jobs into one phrase or lead with a different strategy if it creates a stronger, truthful information gap. The pool must remain strategy-diverse. Different strings using the same `真正的X不在Y` shell do not count as diverse strategies.

### First three complete sentences — opening-zone outcome gate
The first three complete sentences collectively should let a cold finance reader understand:
- what concrete fact/anomaly/change has happened;
- why it matters financially or changes company differentiation;
- what useful question/payoff is still unresolved.

Do **not** map these jobs mechanically to sentence 1/2/3. One sentence may perform two jobs; a sentence may be unusually short or long; the opening may use fact, contradiction, scene, question or delayed nut-graf. The test is reader orientation after the zone, not compliance with a three-line template.

### H1s and continuation
Each H1 is an information-bearing hook, not a category label. It should expose a finding, contrast, consequence or question worth entering.

Avoid generic H1s such as `产业链梳理 / 相关公司 / 未来展望` when a topic-specific conclusion can be stated instead.

Title, H1s and paragraph transitions must not repeat one rhetorical mold. Each major section should inherit an earned reason from the previous section.

## 4. Company Decision Map — useful like stock selection research, without trading instructions

The prohibited boundary is executable recommendation — buy/sell, timing, target price, position size or covert equivalents. Evidence-bounded relative judgment is required when it improves understanding.

When a research universe contains two or more `MATERIAL` companies, Research must create a `CompanyDecisionMap`. It must use current topic-specific dimensions rather than a fixed universal scorecard. Useful dimensions include, when material:
- business/concept purity: how directly the relevant business contributes to the company's economics;
- current business scale/revenue mix;
- demand-to-revenue/profit distance;
- realization stage and speed;
- earnings/operating sensitivity;
- channel/customer/capacity/price leverage;
- certainty/evidence strength;
- adverse variable and falsification condition.

The map must culminate in a named current comparative verdict. Legal examples of the semantic form include:
- A currently has more direct/purer exposure than B because ...;
- B has the faster current realization path while C remains a later option because ...;
- A's evidence is currently harder, while B has greater elasticity but a longer evidence chain;
- the current ranking would change if X/Y evidence appears.

These are semantic examples, not mandatory sentence molds. The draft should express the comparison in whatever wording best fits the article voice.

Do not retreat to empty language such as `谁能先兑现，谁就更占优势` when current research already shows which company is ahead on the relevant dimension.

A Deep article with multiple material companies must contain at least one passage that names the compared companies and states the evidence-bounded difference. It need not be a single fixed-format paragraph. Broad may compress the map but must preserve a truthful differentiation rather than an undifferentiated basket.

## 5. H1 lead / image-safe transition zone

When an H1 is followed by H2/H3 branches, it must not jump directly into the lower-level heading.

Insert a substantive section-lead paragraph after H1. The paragraph must:
- connect the prior section to this section's analytical job;
- explain why the following branches/comparisons matter;
- add actual information rather than `下面来看` staging;
- be substantive enough to remain readable if the user inserts an H1-related image between this lead and the first H2.

This is both an argument-progression requirement and a publishing-layout requirement. Do not force the lead to a fixed sentence count or rhetorical structure.

## 6. Information density and numbering

High information density means each paragraph changes the reader's model through a fact, causal relation, comparison, boundary, counterexample or validation condition. Rephrasing importance without new information is a defect.

Use `一、二、三 -> （1）（2）（3） -> ①②③` readily when real branches exist. In Deep, parallel companies, realization stages, mechanisms, comparison dimensions or validation paths should normally be visibly numbered. Do not force symmetric subpoints where no real branch exists.

## 7. Three publishing products from one audited evidence base

One topic may produce three separate products. They share research facts and evidence boundaries but have different reader jobs.

### A. Deep finance/review long-form
Platforms: `韭研公社 / 东方财富 / 微信公众号`.
Output: `FINANCE_DEEP_DOCX`.
Job: complete self-review/finance-community analysis, material-company coverage, Company Decision Map and falsification/monitoring logic.

### B. Acquisition long-form
Platforms: `微信公众号 / 头条号 / 百家号 / 网易号 / 企鹅号`.
Output: `FINANCE_BROAD_DOCX`.
Job: attract cold finance readers, earn continuation/completion and convert attention to follows. It is not a shortened Deep article. It selects the strongest one-to-three finance-wide information gaps and rebuilds title/opening/structure around them while preserving evidence boundaries.

### C. Interaction short-form pack
Platforms: `微信公众号 / 头条号 / 百家号 / 网易号`.
Output: `PLATFORM_INTERACTION_PACK_DOCX`.
Formats include `贴图文字 / 微头条 / 动态`.
Job: standalone interaction and follower acquisition.

The short pack must be independently rewritten from the audited evidence base. Copying/truncating long-form paragraphs is not legal adaptation. Each item needs its own first-line reason to stop, compact fact/judgment chain and a context-appropriate interaction move when interaction is genuinely useful. Do not append a canned question merely to satisfy an engagement template.

Financial Writing supplies text only. User-added images remain outside the Financial image-generation workflow.

## 8. Default/new-mode semantics and historical compatibility

New no-target tasks default to `PORTFOLIO`:
`AUDIT_DOCX + FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + PLATFORM_INTERACTION_PACK_DOCX`.

Broad acquisition-only target platforms use `ACQUISITION`:
`AUDIT_DOCX + FINANCE_BROAD_DOCX + PLATFORM_INTERACTION_PACK_DOCX`.

Historical `DUAL` remains the legacy Deep+Broad+Audit contract. Historical `FINANCE_BROAD` remains Broad+Audit. Their meaning is not retroactively changed.

## 9. Audit admission

An applicable final article cannot PASS if any of these remain:
- publication research/source trail exposed;
- clustered title/H1/body rhetorical scaffolding that materially harms voice/reader progression;
- opening zone leaves the cold finance reader unable to tell what changed, why it matters, or what useful payoff remains;
- H1 jumps directly to H2/H3 without a substantive lead;
- multi-MATERIAL-company Deep lacks Company Decision Map or named comparative judgment;
- generic company-selection conditional substitutes for available research;
- Broad is merely a compressed Deep rather than a rebuilt acquisition product;
- required interaction pack is missing or is copied/truncated from long-form prose;
- anti-AI revision has flattened a working passage into generic 'humanized' prose or inserted fabricated experience/platform caricature.

A deterministic template-cluster hit is a **review trigger**, not proof that every matched sentence must be removed. Semantic audit decides whether the cluster is actually unearned.

Same-chat PASS remains `CHAT_SELF_REVIEW`; separate Reader/Editor/Style passes inside the same session do not upgrade assurance provenance.