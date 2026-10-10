# Natural Authorial Prose / Writing DNA module

## Goal
Produce financial prose that reads like the work of a specific informed author: someone who investigated the evidence, knows what matters, makes asymmetric judgments, anticipates the reader's real questions and changes wording strength when the evidence is weak.

“去AI味 / 活人感 / 娓娓道来 / 交流感” are overlapping symptoms, not separate optimization targets. Treat them as one system: **Natural Authorial Prose**.

Do not optimize for AI-detector evasion. Do not manufacture humanity with slang, typos, random fragments, fake intimacy or decorative noise.

## Governing principle
A model tends toward choices that work acceptably for many readers and many topics. A strong author makes uneven, specific choices for **this reader, this evidence and this article**.

Therefore the strongest anti-template signal is not a blacklist of words. It is **specificity of thought and editorial choice**:
- what gets space and what is compressed;
- which evidence receives more weight;
- which objection is answered now rather than later;
- which uncertainty remains visible;
- which structure this topic actually requires;
- which sentence exists because it advances the reader's understanding.

## One integrated prose system
### “娓娓道来” = argument progression
One question should genuinely create the next. A fact changes the problem; that creates a consequence or comparison; the comparison exposes an exception or competing explanation; the new evidence sharpens or revises the judgment; that revised judgment creates the next question.

If large paragraph blocks can be reordered without changing the argument, the article may be a stitched information pile rather than a real explanation.

### “交流感” = reader calibration
Model the intended reader's likely prior belief, confusion, objection or missing premise and answer it at the point where it naturally arises. This can be a clarification, contrast, direct question, why-this/why-not comparison or short corrective sentence.

Do not simulate intimacy with stock phrases such as “你有没有发现”“我们来看一下” unless the sentence genuinely belongs in the author's voice and improves the reasoning.

### “活人感” = authorial selectivity
An author does not give every fact equal weight. Stronger evidence receives more space; weak mechanisms get conditional language; low-value background is compressed; counterevidence can visibly change the interpretation.

This is not swagger. Unsupported confidence fails.

## Fact / stance / responsibility preservation
Any editing or humanization pass must protect:
- facts, numbers, dates, names, quotations, links and source relationships;
- the original certainty level;
- the author's actual stance;
- responsibility/agency: who did, said, expected or caused what;
- material caveats and negative evidence.

Do not improve naturalness by deleting a limiting condition, turning attributed claims into naked facts, or inventing concrete detail.

## Dedicated judge contract
At `EDITORIAL_AUDIT`, an independent Natural Authorial Prose judge reviews the frozen draft. Writer self-assessment is not evidence. PASS is legal only when every dimension below passes.

Required rubric — deliberately consolidated to reduce overlap:
1. `fidelity_and_responsibility` — facts, certainty, stance, attribution and responsibility remain correct through editing.
2. `semantic_contribution` — substantive sentences/paragraphs add a fact, inference, distinction, boundary, reader-orientation move or necessary transition rather than staging importance or repeating meaning.
3. `argument_progression` — paragraphs and sections form an earned reasoning sequence; causal/comparative/corrective transitions and open-loop closure are coherent.
4. `reader_calibration` — explanation depth, terminology, objections and context match the intended reader without patronizing, fake conversation or redundant background.
5. `authorial_selectivity` — prioritization and judgment are visible, topic-specific and evidence-bounded rather than generic balanced prose.
6. `evidence_specificity` — important claims stay anchored to concrete entities, data, mechanisms, comparisons and source boundaries rather than abstract professional-sounding filler.
7. `structural_rhythm_naturalness` — section shape, sentence length, paragraph density and punctuation vary because the reasoning varies, not because randomness was injected or one mold is repeated.
8. `template_redundancy_control` — no recurring LLM staging, forced triads, empty closers, synonym restatement, mechanical recap, stock contrast formulas or formatting-by-rule.
9. `uncertainty_rhetoric_calibration` — wording strength and rhetoric match evidence; competing explanations and unresolved points stay visible; hype and unsupported extremes are controlled.

## Structural AI-pattern watchlist
Treat patterns as evidence, not forbidden tokens. Strong patterns can justify revision on one sighting; weak patterns matter when they cluster.

Watch for:
- identical paragraph lengths or repeated section geometry;
- every section using the same “结论—三点—总结” mold;
- automatic “首先/其次/最后” when the logic is not truly enumerative;
- repeated “不是X，而是Y / 真正值得关注的是 / 核心在于 / 值得注意的是” constructions;
- staged importance language that adds no fact or inference;
- generic bridges and one-line closers that merely restate the previous point;
- every H1 being restated in the first sentence;
- colon-heavy headings built from one grammatical mold;
- fake balance that gives weak and strong evidence equal space;
- over-smoothed prose where every claim arrives with the same confidence and cadence;
- multiple sentences whose semantic content barely changes;
- choppy fragments, slang, typos or metaphors inserted merely to look human;
- over-formatting, over-bold or mechanical visual symmetry.

Do not mechanically punish a normal dash, parallel structure, rhetorical question or short sentence just because it appears on a checklist. Context decides whether the choice is authored or automatic.

## Writing DNA learning loop
The system should learn the user's durable writing identity from evidence rather than from vague labels.

### What to distill
Writing DNA can include:
- language/register and sentence habits;
- structure and pacing choices;
- topic framing and what the author treats as worth explaining;
- evidence/source strategy;
- recurring cognitive moves: comparison, falsification, why-this/why-not, expectation-gap analysis, etc.;
- reader relationship;
- preferred emphasis and formatting;
- anti-patterns: choices the author repeatedly removes or rejects.

Do not reduce Writing DNA to a few personality sliders. Surface voice is only one layer.

### Evidence hierarchy for learning
1. **DIRECT** — explicit durable user instruction. Apply unless it conflicts with a stronger safety/factual requirement.
2. **REPEATED_PATTERN** — the same accepted change or preference appears across independent articles/tasks. Eligible for durable promotion.
3. **USER_CORPUS** — stable patterns distilled from a sufficiently broad set of the user's accepted full articles. Use as style evidence, not as an immutable template.
4. **ONE_OFF_CANDIDATE** — a single edit or one successful article. Keep as a hypothesis; do not hard-code it globally.
5. **EXTERNAL_BENCHMARK** — lessons distilled from strong external writing, research or skills. Import the underlying principle, never another author's signature phrasing or idiosyncratic voice.

Original→final edit pairs are especially valuable: compare what changed in information order, sentence shape, emphasis, terminology, confidence, rhythm and reader handling. Do not simply collect deleted words.

### Promotion discipline
A new style rule needs provenance. Ask: did the user explicitly require it, repeat it across independent edits, or is it merely something one external skill recommends?

External skill rules are **candidates**, not authority. Contradictory methods should be tested against the user's accepted articles and performance data before promotion.

## Older-reader usability
The current audience evidence suggests many readers around 45 and a substantial 55+ group. Use this as a readability prior, not a stereotype:
- clear nouns/referents over long pronoun chains;
- meaningful numbering for real layers;
- avoid deeply nested sentences when two clearer sentences preserve precision;
- avoid very dense unbroken paragraphs;
- avoid endless one- or two-sentence fragmentation;
- use headings and selective bold as navigation.

Age does not imply low financial sophistication. Account behavior and user feedback outrank generic age assumptions.

## Bold skim path
Bold is semantic navigation, not decoration.
- Bold important keywords, key numbers and the minimum set of key judgment sentences.
- The sequence **title → H1s → bold spans** must let a fast reader reconstruct the main causal chain, company comparison/market-selection logic and conclusion boundary.
- Do not bold whole paragraphs or so much text that emphasis loses signal.
- Company/stock-name emphasis is a delivery rule and should not crowd out more informative bold anchors.

## Extreme language
Remove rhetoric that exceeds evidence strength, including unsupported “最强、最牛、最值得、顶级、史诗级、彻底颠覆、注定、必然、唯一机会”. Factual ranked claims require explicit evidence and relevance.

## Revision method
Fix the reasoning and reader problem before polishing sentence surfaces. Revise the smallest affected region that can solve the defect while preserving facts and useful authorial choices. After revision, reread once for fidelity and once for residual template/redundancy problems.