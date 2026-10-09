# Natural authorial prose / anti-AI quality module

## Goal
Produce financial prose that reads like the work of an informed author who has actually investigated the evidence, formed priorities, revised judgments and is explaining the result to another financially literate reader.

“去AI味 / 活人感 / 娓娓道来 / 交流感” are useful intuitions, but they are **not** the optimization target themselves. The target is stronger: **authorial specificity + semantic progression + concrete evidence + calibrated uncertainty + reader awareness + controlled structural variation**.

Do **not** optimize for fooling AI detectors. Detector performance is unstable across models/domains and evasion-oriented editing can damage clarity. This gate judges writing quality and authorial specificity directly.

## Research basis behind the gate
Recent linguistic research comparing human and LLM text repeatedly finds that human writing tends to show greater structural/feature variability and more diverse semantic content, while machine text can exhibit stronger homogenization, discourse regularity or semantic redundancy. These findings are priors, not a recipe to add randomness.

Financial-communication guidance also consistently supports clear, concrete, well-organized language that preserves material information rather than burying it in boilerplate. Therefore the gate rewards meaningful variation and prioritization, not decorative irregularity.

## What “娓娓道来” means operationally
The reader should feel that one question genuinely produces the next:
- a fact changes the state of the problem;
- that change creates a consequence or comparison;
- the comparison exposes an exception, competing explanation or missing condition;
- the new evidence changes or sharpens the judgment;
- that revised judgment creates the next question.

This is **semantic progression**, not merely smooth transitions. If paragraph B can be moved before paragraph A without changing the reasoning, the prose may be a stitched information pile rather than a real argument.

## What “交流感” means operationally
Model the reader’s likely confusion, prior belief or objection, then answer it where it naturally arises.

Good reader modeling can appear as a direct question, a short corrective sentence, a comparison, a clarification or an explicit “why this / why not”. It does not require saying “你有没有发现” or “我们来看”.

Use first-person judgment only when it reveals a real analytical choice, such as which evidence deserves more weight or why an earlier interpretation was revised. Do not manufacture intimacy.

## Authorial specificity
Human-quality financial writing is not neutral data dumping. The author should make **evidence-bounded asymmetric choices**:
- stronger evidence receives more weight and space than weaker evidence;
- one mechanism can be judged more important than another, with reasons;
- uncertainty is stated where it materially affects the conclusion;
- counterevidence can force a visible change in interpretation;
- low-value background is compressed even if it would make the article look more “complete”.

Authorial specificity is not swagger. A confident unsupported opinion fails this gate.

## Concrete evidence density
Prefer specific entities, dates, quantities, relationships, mechanisms and comparisons over generic financial prose. A paragraph should normally add at least one new fact, inference, comparison, boundary or causal/mechanistic link.

Generic connective prose that merely sounds professional but advances nothing is a defect.

## Dedicated judge contract
At `EDITORIAL_AUDIT`, an independent Natural Authorial Prose / Human Voice Judge reviews the frozen draft. Writer self-assessment is not evidence. PASS is legal only when every rubric item passes.

Required rubric:
1. `template_fingerprint` — no obvious reusable LLM template or mechanically symmetric article architecture.
2. `discourse_variability` — section and paragraph shapes vary according to the topic’s real reasoning demands rather than a repeated grammar/layout mold.
3. `semantic_progression` — each substantive paragraph materially advances the argument instead of restating or merely decorating it.
4. `transition_continuity` — transitions perform actual causal, comparative, chronological, corrective, narrowing or inferential work.
5. `repetition_control` — no repeated recap, synonym restatement, duplicated claim or rhetorical tic.
6. `rhythm_naturalness` — sentence and paragraph length vary naturally without fake staccato, monotonous walls of text or theatrical fragments.
7. `concrete_evidence_density` — claims stay anchored to entities, data, mechanisms and comparisons rather than abstract boilerplate.
8. `reader_modeling` — likely reader questions/misjudgments are anticipated naturally without fake conversation.
9. `narrative_flow` — the reasoning unfolds so that later sections feel earned by earlier evidence and open questions are deliberately closed.
10. `authorial_specificity` — prioritization, weighting and judgment are visible and topic-specific rather than generic balanced prose.
11. `uncertainty_calibration` — wording strength matches evidence; competing explanations and unresolved points remain visible when material.
12. `extreme_language_control` — rhetoric does not exceed factual support.

## AI-pattern watchlist
Audit for, but do not mechanically ban, these recurring patterns:
- identical paragraph lengths or repeated section geometry;
- every section using the same “结论—三点—总结” mold;
- automatic “首先/其次/最后” when the logic is not truly enumerative;
- repeated “不是X，而是Y / 真正值得关注的是 / 核心在于 / 值得注意的是” constructions;
- generic bridges that add no evidence or inference;
- every H1 being restated in the first sentence;
- colon-heavy headings built from one repeated grammatical mold;
- section endings that recap rather than create the next analytical question;
- false balance that gives weak and strong evidence equal weight;
- over-smoothed prose in which every claim arrives with the same confidence and cadence;
- excessive semantic redundancy: multiple sentences whose meaning barely changes;
- choppy fragments, slang or typos added merely to look human;
- decorative metaphors that obscure the financial mechanism.

## Natural rhythm and older-reader usability
The audience currently skews toward readers around 45 with a substantial 55+ group. Keep analysis sophisticated while reducing avoidable reading friction:
- use clear nouns/referents instead of long pronoun chains;
- break genuinely complex reasoning into meaningful numbered layers;
- avoid deeply nested sentences when two clearer sentences preserve precision;
- avoid very dense unbroken paragraphs;
- do not fragment the article into endless one- or two-sentence blocks;
- let H1/H2/H3 numbering and selective bold carry navigation.

Larger readable type helps, but typography does not rescue opaque prose.

## Bold skim path
Bold is semantic navigation, not decoration.
- Bold important keywords, key numbers and the minimum set of key judgment sentences.
- The sequence **title → H1s → bold spans** must let a fast reader reconstruct the main causal chain, company comparison/market-selection logic and conclusion boundary.
- Do not bold whole paragraphs or so much text that emphasis loses signal.
- Company/stock names remain bold on every occurrence under the delivery rule.

## Extreme/superlative language
Remove rhetorical superlatives and absolutes that exceed evidence strength, including unsupported “最强、最牛、最值得、顶级、史诗级、彻底颠覆、注定、必然、唯一机会”. Factual ranked claims require explicit evidence and material relevance. Words such as “最近/最后” are not automatically violations.

## Revision method
Revise the smallest affected passages while preserving evidence and author judgment. Fix the reasoning defect before polishing the sentence surface. Do not “humanize” by adding filler, typos, random sentence fragments, fake emotion or decorative conversational noise.