# Natural Authorial Prose / Writing DNA module

## Ownership
This module owns **how the argument is expressed and how durable authorial preferences are learned**. It does not own research breadth, headline/search packaging, platform tactics or Word mechanics.

The user's phrases “去AI味 / 活人感 / 娓娓道来 / 交流感” are overlapping intuitions, not separate optimization targets. The target is evidence-bounded **Natural Authorial Prose**: a specific informed author making real choices for this evidence, this reader and this article.

Do not optimize for AI-detector evasion. Do not manufacture humanity with slang, typos, random fragments, fake intimacy or decorative noise.

## Boundary with Editorial and Reader Funnel
- **Editorial** owns macro section order, material coverage, company-universe coverage and whether multi-branch reasoning needs visible numbered structure.
- **Authorial Prose** owns whether sentences/paragraphs genuinely advance the reasoning and whether the author's priorities are visible.
- **Reader Funnel** owns whether the resulting title/opening/H1/paragraph flow gives the target reader enough value and forward pull to continue.

Do not duplicate one defect under three different names.

## Governing principle
A generic model tends toward choices acceptable across many topics. Strong authorial prose makes uneven, topic-specific choices:
- what gets space and what gets compressed;
- which evidence receives more weight;
- which objection is answered now;
- which uncertainty stays visible;
- which comparison changes the judgment;
- which sentence exists because it advances understanding rather than stages importance.

## “娓娓道来” = earned argument progression
A fact should alter the question; that creates a consequence/comparison; the comparison exposes an exception or competing explanation; new evidence sharpens or revises the judgment; the revised judgment creates the next question.

If large paragraph blocks can be reordered without affecting the argument, the article may be a stitched information pile rather than an explanation.

### Major-section bridge hard gate
A correct section order is not enough if the prose still feels like separate research cards pasted together. Before every new H1, the preceding substantive paragraph should normally create an **earned bridge** into the next analytical job through at least one real relation: cause, consequence, chronology, comparison, narrowing, correction, unresolved question or inference.

Do not add empty bridge phrases such as “接下来我们来看”“说完A再看B”. The bridge must tell the reader *why B follows from A*. If the next H1 could be moved elsewhere with no loss of reasoning, revisit the transition or the macro structure.

The final paragraph of a section need not announce the next heading mechanically. A good bridge can be a conclusion whose consequence naturally makes the next section necessary.

## “交流感” = reader calibration
Model the intended reader's likely prior belief, confusion, objection or missing premise and answer it where it naturally arises. Use clarification, contrast, a genuine question, `why_this / why_not`, or a short corrective sentence when useful.

Do not simulate intimacy with stock phrases such as “你有没有发现”“我们来看一下” unless they genuinely improve the reasoning and fit the author's voice.

## “活人感” = authorial selectivity
Do not give every fact equal weight. Stronger evidence gets more space; weak mechanisms get conditional wording; low-value background is compressed; counterevidence can visibly change the interpretation.

This is judgment, not swagger. Unsupported confidence fails.

## Fidelity / stance / responsibility preservation
Any editing pass must preserve:
- facts, numbers, dates, names, quotations, links and source relationships;
- certainty level;
- the author's actual stance;
- responsibility/agency: who did, said, expected or caused what;
- material caveats and negative evidence.

Naturalness never justifies deleting a limiting condition, converting an attributed claim into a naked fact or inventing concrete detail.

A topic's business-realization ladder must also remain intact. Do not rewrite an earlier evidence stage as a later one merely for narrative force—for example, technology/product progress does not itself prove orders; orders do not themselves prove recognized revenue; revenue does not itself prove profit or cash-flow realization. The actual stages vary by topic, so this is a **general evidence-stage rule**, not a permanent vocabulary tied to one industry.

## Dedicated nine-part judge
At `EDITORIAL_AUDIT`, an independent judge reviews the frozen draft. PASS requires text-level evidence for all nine dimensions:
1. `fidelity_and_responsibility` — facts, certainty, stance, attribution and agency remain correct.
2. `semantic_contribution` — substantive units add fact, inference, distinction, boundary, reader orientation or necessary connective work rather than restating importance.
3. `argument_progression` — paragraphs form an earned reasoning sequence, major sections are causally/comparatively bridged and open loops close coherently.
4. `reader_calibration` — explanation depth, terminology and objections fit the intended reader without patronizing or fake conversation.
5. `authorial_selectivity` — prioritization is visible, topic-specific and evidence-bounded.
6. `evidence_specificity` — important claims stay anchored to concrete entities, data, mechanisms, comparisons and source boundaries.
7. `structural_rhythm_naturalness` — sentence/paragraph/section rhythm varies because reasoning varies, not because randomness was injected.
8. `template_redundancy_control` — no recurring LLM staging, forced triads, generic bridges, synonym restatement, mechanical recap or formatting-by-rule.
9. `uncertainty_rhetoric_calibration` — wording strength matches evidence and unresolved/competing explanations remain visible.

## Deterministic template-cluster guard
The semantic judge is not allowed to wave away a visible template cluster with “整体自然”. Before Authorial Prose judgment, the runtime computes a structural signal report over the frozen article.

Signals include recurring families such as:
- “真正的X不是/不在Y，而是/而在Z”；
- “如果只看……”；
- “这正是……”；
- “最值得关注/写清楚的是……”；
- repeated “核心在于/问题在于/值得注意的是/换句话说” staging.

These are **not banned phrases**. One well-earned occurrence is normal Chinese prose. The deterministic guard requires REVISE only when a family repeats heavily or several families cluster at meaningful density. When `requires_revise=true`, `template_redundancy_control` cannot PASS until those sections are rewritten.

This protects against the specific failure mode where every section uses the same move:
`先否定旧指标 → 提出新指标 → 再说“这正是/真正值得看” → 小结`.

## Pattern watchlist
Treat patterns as evidence, not forbidden tokens. Watch for clusters such as:
- identical paragraph lengths or repeated section geometry;
- every section using the same “结论—三点—总结” mold;
- automatic “首先/其次/最后” without real enumeration;
- repeated “不是X，而是Y / 真正值得关注的是 / 核心在于 / 值得注意的是” staging;
- generic bridges or one-line closers that add no information;
- abrupt H1 changes where the previous section never creates a reason for the next one;
- H1 restated immediately in the first sentence;
- colon-heavy headings built from one grammatical mold;
- fake balance between weak and strong evidence;
- multiple sentences with little semantic change;
- slang/fragments/metaphors inserted only to look human;
- over-formatting or mechanical visual symmetry.

A normal dash, parallel structure, question or short sentence is not an error by itself.

## Numbering and prose naturalness
Visible numbering is not “AI format” when it reflects real analytical branches. For a Deep article with several stock classes, stages, dimensions or causal branches, `（1）（2）（3）/①②③` should be used **readily and often** when it makes the reasoning easier to scan and compare. Do not reserve lower-level numbering only for extreme paragraph density.

The error is mechanical symmetry: do not force every H1 to contain exactly three subpoints. Use as many numbered subpoints, and as much hierarchy, as the actual logic earns.

## Writing DNA: what to learn
Writing DNA can include:
- register and sentence habits;
- structure and pacing choices;
- topic framing and what the author treats as worth explaining;
- evidence/source strategy;
- recurring cognitive moves such as comparison, falsification, expectation-gap analysis and `why_this / why_not`;
- reader relationship;
- preferred emphasis/formatting;
- anti-patterns the author repeatedly removes.

Do not reduce Writing DNA to personality sliders or a list of banned words.

## Evidence hierarchy
1. **DIRECT** — explicit durable user instruction.
2. **REPEATED_PATTERN** — the same accepted change appears across independent articles/tasks.
3. **USER_CORPUS** — stable patterns from a sufficiently broad set of accepted full articles.
4. **ONE_OFF_CANDIDATE** — one edit or one successful article; hypothesis only.
5. **EXTERNAL_BENCHMARK** — external writing, skills, agents or research; import principles, never signature phrasing or foreign authority.

Original→final edit pairs are especially valuable because they show changes in information order, emphasis, confidence, sentence/paragraph shape, terminology, evidence handling and reader relationship.

## Raw learning-sample ledger
Use `record_writing_learning_sample` to retain task-level evidence such as:
- `USER_EDIT` — original→revised text or durable refs;
- `USER_FEEDBACK` / `USER_ACCEPTANCE` / `USER_REJECTION`;
- `POST_PUBLICATION_PERFORMANCE` — observed metrics/analytics refs.

Each stored sample is `RAW_EVIDENCE_ONLY`. Recording it does **not** promote it into a permanent rule. Promotion follows the evidence hierarchy and `maintenance.md`.

## Older-reader usability
The currently known audience suggests many readers around 45 and a substantial 55+ group. Treat this as a readability prior, not a sophistication label:
- clear nouns/referents over long pronoun chains;
- meaningful numbering for real layers;
- avoid unnecessarily deep sentence nesting;
- avoid dense unbroken walls and endless one-sentence fragmentation;
- use headings and deliberate bold as navigation.

Account behavior and user feedback outrank generic demographic assumptions.

## Bold skim path
Every A-share company name supplied to the publication document is a deterministic bold entity marker. **That does not satisfy the skim-path requirement by itself.**

Explicitly emphasize additional key facts, numbers, mechanisms and selected judgment sentences so **title → H1s → all bold spans** reconstruct the main line. The reader should be able to recover not only *which companies are present* but also *what changed, how the logic transmits, which comparison matters and where the conclusion is bounded*.

Do not respond to automatic company-name bolding by removing semantic bold anchors. The fixed entity layer and the selective reasoning layer serve different functions.

## Extreme language
Unambiguous promises such as “注定暴涨”“必然上涨”“唯一机会” can be deterministic hard fails. Generic superlatives such as “最强”“顶级” require semantic context: unsupported hype fails, while a genuinely sourced ranked claim can be legal if the wording and relevance are precise.

## Revision method
Fix reasoning/reader defects before polishing surfaces. Revise the smallest region that solves the defect while preserving facts and useful authorial choices. Then reread once for fidelity, once for **major-section progression**, once for evidence-stage integrity and once for residual template/redundancy problems.
