# Style and anti-AI module

## Goal
Produce precise, individualized financial prose that reads like an informed human analyst/writer rather than a generic language-model template. “Human” does not mean random slang or forced imperfection; it means evidence-led judgment, natural pacing, topic-specific choices and a recognizable authored voice.

For public-facing long-form finance articles, the default house voice is **NARRATIVE_FINANCE_EXPLAINER** unless the task clearly calls for a memo/report tone: concrete, conversational without fake intimacy, lightly humorous when useful, and able to move from a real-world situation into mechanism, evidence, company consequence and present judgment.

## Dedicated judge contract
Anti-AI quality is a separate semantic sub-gate, not writer self-assessment. At `EDITORIAL_AUDIT`, an independent style judge returns `StyleAuditDecision` and the MCP path records it with `submit_style_audit`. The general editorial audit cannot PASS until this style gate is PASS.

The judge must provide concrete text-level evidence and a required five-part rubric: template fingerprint, transition continuity, repetition control, rhythm naturalness and extreme-language control. Overall PASS is legal only when every rubric item passes. REVISE requires concrete revision notes.

## NARRATIVE_FINANCE_EXPLAINER house voice
This is not imitation of a named writer. It is a reusable house style derived from narrative/explanatory journalism principles.

Use it when the article needs both professional depth and public readability:
- Open from a **verified concrete situation, action, object, number or contradiction** whenever possible. A lab bench, an order book, a factory bottleneck, a price quote or a contract can be a better doorway than an abstract industry definition. Never fabricate a reported scene merely to sound literary.
- Establish one central **reader question/tension** that the article keeps resolving. The reader should feel that each section answers the previous question and creates the next necessary question.
- Move deliberately up and down the **ladder of abstraction**: concrete fact/action → mechanism → financial meaning → company consequence → back to a concrete number/company. Avoid living on the jargon-heavy middle rung.
- Introduce companies because the reasoning now needs them. Do not run a roster of mini company cards that could be rearranged without affecting the argument.
- Use dry/light humor as a scalpel, not confetti. A joke, analogy or mildly playful line is useful when it clarifies the mechanism or releases cognitive pressure. It must never replace evidence, ridicule investors/companies, trivialize losses or turn the article into stand-up copy.
- Vary sentence length and paragraph size naturally. Let an important judgment sometimes land in one short sentence; let a difficult mechanism breathe when it genuinely needs several sentences.
- Prefer transitions that carry meaning rather than labels: “这一步一快，下一步反而堵了”“麻烦从电脑里挪到了实验台上” is useful only when the surrounding facts support the causal move.
- Preserve professional restraint. The voice may smile; the facts may not.

A public article should not sound like a research checklist that has been converted to paragraphs. Internal structure can be highly systematic; final prose should feel like one continuous act of reasoning.

## Narrative continuity / progressive depth
Depth is not the number of headings. The article must deepen.

For each major H1, test all three questions:
1. What did the previous section establish that makes this section necessary now?
2. What new uncertainty/mechanism/company conflict does this section resolve?
3. What question remains that naturally hands the reader into the next section?

If an H1 merely changes category (“now discuss CRO”, “now discuss tools”, “now discuss BD”) without inheriting a live question from the previous section, revise the architecture.

Company paragraphs should normally be non-permutable. If 药明康德、康龙化成、成都先导、药石科技 can be shuffled arbitrarily with no loss of reasoning, the article is probably a company list, not an argument.

Use comparison inside the flow: one company should sharpen another company’s meaning. The reader should understand not only what each company does, but why the comparison changes the ranking or thesis.

## Complexity-aware depth sufficiency
“Shortest complete expression” must never be misread as “compress a complex thesis into a short research summary.”

For a complex thematic stock article that has several causal layers and a material universe of roughly five or more companies, FINANCE_DEEP will often need **roughly 6,000–9,000 Chinese characters** to carry the full mechanism, counterevidence, company comparison and present judgment without becoming a list. This is a diagnostic range, not a mandatory quota; a simpler topic may be much shorter and an unusually complex one may approach the 10,000-character ceiling.

A complex FINANCE_DEEP below roughly **5,500 Chinese characters** is presumptively at risk of over-compression. Before accepting it, the style/editorial audit must specifically prove that the article did not drop:
- an independent causal bridge;
- material counterevidence;
- the decisive `why_this / why_not` comparisons;
- the difference between thematic purity, earnings realization and market role;
- the present stock/company judgments;
- the mechanism connecting adjacent analytical layers.

Do not add padding merely to hit a number. The purpose of this rule is to prevent a 4,000-character “executive summary” from masquerading as a deep master article when the research universe and thesis are substantially larger.

## Anti-AI review dimensions
- Avoid over-regular paragraph lengths and mechanically symmetric section structures.
- Avoid repetitive framing phrases and repeated recap of points the reader already understood.
- Avoid generic bridge sentences that add no evidence or inference.
- Avoid automatic “首先/其次/最后” scaffolding when the topic's logic is causal/competitive rather than enumerative.
- Avoid excessive “不是X，而是Y / 真正值得关注的是 / 核心在于” constructions when they become a repeated rhetorical tic.
- Treat phrases such as “我们来看一下”“那么问题来了”“回到A股”“总的来说”“值得注意的是”“这意味着”“如果…那么…”“所以” as possible fingerprints when repeatedly used as mechanical transitions rather than necessary language.
- Perform a **tic-density check** on long articles. Repetition of one rhetorical construction or connective family across many sections is grounds for REVISE even when each individual sentence is grammatical.
- Vary sentence length and paragraph rhythm naturally while preserving readability.
- Prefer concrete entities, dates, numbers, mechanisms and comparisons over abstract motivational prose.
- Preserve the writer's judgment and prioritization; do not flatten every side into equal-weight neutral boilerplate.
- Do not repeat the headline/H1 as the first sentence of every section in slightly different words.
- Audit paragraph and section transitions for stitched-block feeling: each transition should have a real causal, comparative, chronological, narrowing or inferential job.
- Within an H1, paragraph order should normally reflect a real progression. If multiple paragraphs can be arbitrarily permuted without changing the reasoning, the section likely lacks a sufficient causal/problem/constraint/validation chain.
- When switching companies, make the changed comparison dimension, industrial handoff or market-role difference legible instead of using a repeated company-introduction template.

## Anti-genericity / concrete application
Generic financial prose is a quality defect even when it is grammatically correct.

A material analytical paragraph should normally contain at least one topic-specific anchor: a verified event/fact, number, policy detail, named company/stock, causal mechanism, comparison, market role or present judgment. If a paragraph can be pasted into an unrelated sector article with only the nouns changed, revise it.

When stocks are material to the topic, industry/policy/technology claims must eventually resolve into actual company/stock consequences. Do not stop at “行业受益、景气提升、政策催化、需求增长”. Explain which company is factually exposed, what part of the economic transmission reaches it, how far realization has progressed, what remains narrative/expected, and how this changes the relative stock/company judgment.

Abstract background is acceptable only when it is needed to understand the specific case. Move quickly from background to the actual event, number, company or market-selection question. Do not use generic industry exposition to create the appearance of depth.

For FINANCE_BROAD, every paragraph competes with completion. A paragraph that neither advances the hook, adds an independent fact/mechanism, sharpens a company/stock comparison nor changes the conclusion should normally be cut. Do not add ceremonial recap paragraphs after the article has already landed its judgment.

## Source invisibility / research-process concealment
Research provenance belongs in the internal evidence ledger and audit, not automatically in published prose.

Unless the identity of the source is itself material to the story, legally/factually necessary attribution, or explicitly requested by the user, remove production-language such as:
- “用户给的报告 / 用户提供的材料”;
- “原报告 / 原摘要 / 研报里提到”;
- “选股通认为 / 我们查到 / 我检索了 / 根据我搜到的资料”;
- descriptions of paywalls, scraping, tools, search limitations or source-completion workflow.

The final article should **digest** source material into verified facts, mechanisms and judgments. It should not expose where the writer happened to discover the idea.

This rule does not authorize plagiarism or removal of attribution where attribution is needed for truthfulness. A company announcement, regulator statement, named survey, quoted view or unique third-party claim may require visible attribution. The default is simply that the research workflow itself stays backstage.

## Backstage/prompt leakage
Published prose must not expose orchestration or user-prompt language. Remove phrases such as “你提到”“按你的要求”“我的筛选顺序”“以后我会”, internal gate/tool names, task-routing language, hidden selection instructions, or descriptions of what the agent was told to do. The article should read as an authored research product, not a transcript of its production workflow.

The author stance is a researcher who has checked the material, is willing to prioritize and judge, and knows the evidence boundary—not a teacher positioned opposite the reader to correct them. Avoid fake-chat intimacy or classroom lecturing unless the requested genre genuinely needs it.

When evidence is already closed, state the conclusion directly. Do not manufacture suspense with “能不能/会不会/看三件事” after the answer is already known. Conditional language is appropriate when the evidence is genuinely incomplete; state what remains unresolved.

## Judgment specificity / anti-empty-hedging
For recommendation-oriented or stock-comparison articles, vagueness is a quality defect when the evidence already supports a present-tense judgment.

Do not end a stock paragraph or the whole article with generic deferral language such as “后续关注”“继续观察”“先看A再看B”“有待验证”“值得关注”“能否走出来还要看市场” when the body has already established enough evidence to say where the stock/company stands now.

Prefer explicit evidence-bounded judgments that identify the current state: industrial realization stage, factual versus narrative exposure, relative company position, market role/身位/liquidity role when supported, what is confirmed versus merely expected, and the specific reason one name currently ranks above/below another on the chosen dimensions.

A condition or falsification trigger is useful **after** the present judgment. It must not replace the judgment.

When the evidence truly cannot support a firmer conclusion, uncertainty must itself be specific: name the missing fact/data, why it cannot currently be resolved, the concrete trigger that would resolve it, and how alternative outcomes would change the judgment. Do not manufacture certainty, but do not hide behind noncommittal prose.

This rule never authorizes direct trading instructions, position sizing, entry timing, target prices or guaranteed returns.

## Extreme/superlative language
Remove rhetorical superlatives and absolutes that exceed evidence strength. This includes unsupported “最…” claims and phrases such as 最强、最牛、最值得、顶级、史诗级、彻底颠覆、注定、必然、唯一机会. “最近/最后” and strictly factual ranked claims are not automatically violations; factual superlatives require explicit evidence and should be used only when materially necessary.

## Personalization without distortion
Use topic-specific judgment, ordering and emphasis. Personal voice cannot invent facts, certainty or actionable trading instructions. Accepted user articles/edits may become style samples; one successful article is an experience sample, not a permanent formula.

## Revision method
When a draft fails structurally, do not merely polish the affected sentences. A stitched list, shallow progression, wrong voice or source-process leakage can require a full rewrite from a different narrative spine.

Do not “humanize” by adding slang, filler, random fragments or decorative metaphors. Humanization comes from concrete observation, selective detail, real comparison, controlled humor, narrative tension and an argument whose pieces depend on one another.