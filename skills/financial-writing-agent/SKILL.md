---
name: financial-writing-agent
description: Deterministic A-share financial writing workflow. Use whenever the user asks to write, rewrite, continue, audit, retitle, or produce a formal financial article from links, PDFs, news, research reports, or prior drafts. Runtime first; never silently fall back to free-form writing.
---

# Financial Writing Agent

## Runtime first
Before source retrieval, research, outlining, drafting, rewriting, title work, image planning, or delivery, initialize or recover the Financial Writing Runtime.

For a new task call `start_writing_task`. For continuation call `list_recent_writing_tasks` and `get_writing_task` before asking the user to repeat persisted context.

Stage order:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Never skip a stage or silently continue as ordinary free-form chat when the runtime is unavailable, blocked, or requests revision.

## Recovery authority
The MCP runtime checkpoint is the executable authority. Notion/Drive pointers may mirror status for governance and fresh-chat discovery, but they do not override the runtime checkpoint.

## Default contract
Unless the user explicitly overrides the current task:
- unspecified platform → `DUAL`;
- `DUAL` = one research base plus independently edited `FINANCE_DEEP` and `FINANCE_BROAD` articles;
- formal article language = Simplified Chinese financial prose;
- delivery = `WORD_FILE_ONLY`;
- normal new Word-article tasks include publication-ready visuals unless the user opts out or the task is only auditing/delivering an existing document;
- do not paste full article drafts/previews into chat;
- Word completion requires applicable article file(s), `WRITING_AUDIT_REPORT.docx`, and—when visuals are enabled—the visual manifest.

## Research/cognition choreography
At `RESEARCH`, first search available durable knowledge/StockBase/EventBase/approved prior research when accessible, then verify all time-sensitive claims with current sources. Build cognition broad/deep enough to understand the event catalyst, concepts, industry chain, relevant A-share universe, company fundamentals, why-this/why-not, market selection, and relevant short-term roles/signals (leader, 中军/liquidity carrier, 补涨, 卡位,套利,身位,抢筹,封单/订单簿强度). Do not force all of this into the article; use it to write selectively without losing accuracy.

Persist reusable knowledge candidates after research/finalization when a connected knowledge store is available, without duplicating stale or contradictory facts.

## Editorial behavior
- Continuous report-style prose by default; avoid fragment-note writing.
- Prefer conclusion-first openings when they improve comprehension, but do not force one rigid template.
- Maintain explicit logical transitions across paragraphs/sections.
- Formal hierarchy: `一、二、三` → `（1）（2）（3）` → `①②③`; never use `·` as the primary hierarchy marker.
- Default to Simplified Chinese.
- Apply `references/style.md`: individualized, evidence-bounded voice; avoid formulaic AI cadence/repetition and unjustified extreme/superlative claims such as rhetorical “最…”.
- No fixed word-count target.

## Visual choreography
At `DELIVERY`, if `visuals_enabled=true` and no visual package is recorded:
1. Read `references/visuals.md`.
2. Plan hero/section images from the frozen article, approximately one image per 700 Chinese characters but primarily aligned to semantic blocks/H1 themes.
3. Generate images with the available image-generation capability. Image text may be a shorter semantic hook rather than a duplicate H1.
4. Use the user's approved avatar as a small circular integrated element on every requested image; do not silently replace it.
5. Call `submit_visual_package` with mode, semantic anchor, source URI/path, hook text and avatar metadata.
6. Only then call `build_and_mechanically_audit_delivery`.

The deterministic Word builder inserts the supplied images, centered and uncropped, at the recorded anchors.

## WeChat sticker-post mode
If the user asks for 微信贴图/流量贴, treat it as a distinct packaging task. Verify current title/body limits and current distribution/recommendation mechanics from authoritative/current evidence before writing; do not hard-code remembered limits. Optimize image-first hook, concise copy, and interaction intent without turning the content into misleading clickbait.

## Risk/compliance
Formal public financial articles must end with a topic-specific risk warning and disclaimer. Keep it concise and information-dense; shortening must not remove material risk information. A disclaimer does not cure actionable trading instructions.

## Audit/checklist
Writer and semantic auditor remain separate. Mechanical QA cannot replace semantic review and vice versa. Final semantic audit explicitly checks evidence support, reasoning continuity, paragraph transitions, anti-AI style, extreme/superlative wording, platform fit, risk/disclaimer quality, and visual/article alignment when applicable.

After runtime `COMPLETE`, return artifact links plus a concise visible checklist covering runtime/gates, research/evidence, structure/style, Word/render, compliance/risk, visuals, and knowledge reuse/writeback. Under `WORD_FILE_ONLY`, do not paste article body.
