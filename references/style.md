# Style and anti-AI module

## Goal
Produce precise, individualized financial prose that reads like an informed human analyst/writer rather than a generic language-model template. “Human” does not mean random slang or forced imperfection; it means evidence-led judgment, natural pacing and topic-specific choices.

## Dedicated judge contract
Anti-AI quality is a separate semantic sub-gate, not writer self-assessment. At `EDITORIAL_AUDIT`, an independent style judge returns `StyleAuditDecision` and the MCP path records it with `submit_style_audit`. The general editorial audit cannot PASS until this style gate is PASS.

The judge must provide concrete text-level evidence and a required five-part rubric: template fingerprint, transition continuity, repetition control, rhythm naturalness and extreme-language control. Overall PASS is legal only when every rubric item passes. REVISE requires concrete revision notes.

## Anti-AI review dimensions
- Avoid over-regular paragraph lengths and mechanically symmetric section structures.
- Avoid repetitive framing phrases and repeated recap of points the reader already understood.
- Avoid generic bridge sentences that add no evidence or inference.
- Avoid automatic “首先/其次/最后” scaffolding when the topic's logic is causal/competitive rather than enumerative.
- Avoid excessive “不是X，而是Y / 真正值得关注的是 / 核心在于” constructions when they become a repeated rhetorical tic.
- Treat phrases such as “我们来看一下”“那么问题来了”“回到A股”“总的来说”“值得注意的是”“这意味着” as possible fingerprints when they are repeatedly used as mechanical transitions rather than as necessary language.
- Vary sentence length and paragraph rhythm naturally while preserving readability.
- Prefer concrete entities, dates, numbers, mechanisms and comparisons over abstract motivational prose.
- Preserve the writer's judgment and prioritization; do not flatten every side into equal-weight neutral boilerplate.
- Do not repeat the headline/H1 as the first sentence of every section in slightly different words.
- Audit paragraph and section transitions for stitched-block feeling: each transition should have a real causal, comparative, chronological, narrowing or inferential job.
- Within an H1, paragraph order should normally reflect a real progression. If multiple paragraphs can be arbitrarily permuted without changing the reasoning, the section likely lacks a sufficient causal/problem/constraint/validation chain.
- When switching companies, make the changed comparison dimension, industrial handoff or market-role difference legible instead of using a repeated company-introduction template.

## Backstage/prompt leakage
Published prose must not expose orchestration or user-prompt language. Remove phrases such as “你提到”“按你的要求”“我的筛选顺序”“以后我会”, internal gate/tool names, task-routing language, hidden selection instructions, or descriptions of what the agent was told to do. The article should read as an authored research product, not a transcript of its production workflow.

The author stance is a researcher who has checked the material, is willing to prioritize and judge, and knows the evidence boundary—not a teacher positioned opposite the reader to correct them. Avoid fake-chat intimacy or classroom lecturing unless the requested genre genuinely needs it.

When evidence is already closed, state the conclusion directly. Do not manufacture suspense with “能不能/会不会/看三件事” after the answer is already known. Conditional language is appropriate when the evidence is genuinely incomplete; state what remains unresolved.

## Extreme/superlative language
Remove rhetorical superlatives and absolutes that exceed evidence strength. This includes unsupported “最…” claims and phrases such as 最强、最牛、最值得、顶级、史诗级、彻底颠覆、注定、必然、唯一机会. “最近/最后” and strictly factual ranked claims are not automatically violations; factual superlatives require explicit evidence and should be used only when materially necessary.

## Personalization without distortion
Use topic-specific judgment, ordering and emphasis. Personal voice cannot invent facts, certainty or actionable trading instructions. Accepted user articles/edits may become style samples; one successful article is an experience sample, not a permanent formula.

## Revision method
Revise the smallest affected passages. Do not “humanize” by adding slang, filler, random fragments or decorative metaphors. Remove template fingerprints and improve evidence/logic flow instead.
