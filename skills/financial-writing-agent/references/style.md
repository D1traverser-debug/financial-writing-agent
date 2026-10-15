# Style — Material, Voice and Original Expression

Status: `CURRENT_CANDIDATE_1.0`
Owner: `DOMAIN:financial_writing`

## Purpose

Style is the way a situated author selects and expresses audited material for a real reader. It is not a “humanizer”, a detector score or a bag of replacement phrases.

## Generation inputs

Before drafting bind only the writing-relevant context:
- StoryBlueprint;
- audited facts/numbers/company differences/uncertainty;
- author stance and what is primary/secondary/omitted;
- strongest available voice evidence;
- platform/product job.

The writer should not carry every governance, maintenance, CI and audit rule as prose-generation instructions. Those belong in contracts and downstream gates.

## Voice evidence priority

Use, in order when available:
1. user's explicitly approved/edited samples;
2. durable corrections/rejections that reveal voice or reader preference;
3. current prompt prose signals when materially informative;
4. target platform / genre conventions;
5. generic defaults.

Do not fabricate biography, emotion, anecdotes, slang or lived experience to simulate humanity.

## Concrete before abstract

Prefer claims that can be seen in evidence: a company, number, product, channel, margin, policy, inventory behavior, cash-flow consequence or contradiction.

Abstract finance language is legal when it compresses real material. It becomes a defect when it replaces the material itself.

For material explanatory sections, use named companies/cases early enough that the mechanism feels observed rather than lectured.

## Throat-clearing and model scaffolding

Signals such as these are review triggers when clustered or unearned:
- `值得关注/需要注意/可以看到/不难发现`;
- `这意味着/这说明/问题在于/换句话说`;
- repeated `不是X，而是Y`;
- `真正值得.../核心在于...` used as stage markers;
- generic “从这个角度看/接下来再看/未来需要关注”.

No single phrase is universally banned. The question is whether the sentence adds information or merely announces that information is about to arrive.

A clustered scaffold that creates visible model rhythm or repeats conclusions must be cut or rewritten from the underlying fact/claim.

## Paragraph economics

Each paragraph should normally do at least one real job:
- introduce a fact/scene;
- explain a mechanism;
- compare companies;
- challenge the current interpretation;
- state a boundary/uncertainty;
- deliver or open a reader payoff.

Paragraphs that only praise importance, summarize what was just said or narrate the article structure should be removed unless they perform a necessary transition.

## Rhythm

Sentence and paragraph lengths may vary naturally with content. Do not impose short-sentence quotas, punctuation hacks, forced asymmetry or slang. Strong rhythm comes from changing informational jobs: fact -> consequence -> counterexample -> comparison -> boundary, not from cosmetic randomization.

## Original expression / anti-patchwriting

Research materials are evidence, not prose templates.

Current operating method:
1. normalize sources into claims, numbers, relationships and notes;
2. set source prose aside for drafting unless direct quotation/precise actor language is necessary;
3. draft from the StoryBlueprint + normalized evidence;
4. express the reasoning in a new structure that fits the target reader;
5. compare suspicious/distinctive passages back against material sources;
6. rewrite close paraphrase/patchwriting even if individual words have changed.

If distinctive wording itself is part of the fact, quote/attribute it within legal/copyright limits. Publication-source privacy does not authorize unattributed copying.

Do not claim “zero plagiarism” from same-chat inspection alone. Current same-session review is bounded originality evidence.

## Publication source privacy

Do not write `研报指出/据报道/公开资料显示` merely to prove diligence. Research/audit keep provenance. Keep attribution when the identity of the speaker/issuer/source is itself material to the claim.

This rule removes research-process narration, not source responsibility.

## Anti-AI audit

The Style audit reads the finished candidate and cites text spans where:
- voice becomes generic/synthetic;
- scaffolding substitutes for evidence;
- paragraphs over-explain the obvious;
- section shapes repeat mechanically;
- abstract conclusions outrun company facts;
- register changes abruptly;
- source-shaped phrasing appears;
- text sounds like a compliance checklist rather than an article.

Repairs should be the minimum semantic rewrite needed. Do not run a generic whole-article humanizer that can erase evidence, stance or company distinctions.
