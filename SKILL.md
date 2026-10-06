---
name: financial-writing-agent
description: Deterministic A-share financial writing workflow. Use whenever the user asks to write, rewrite, continue, audit, retitle, or produce a formal financial article from links, PDFs, news, research reports, or prior drafts. Runtime first; never silently fall back to free-form writing.
---

# Financial Writing Agent

## Runtime first
Before source retrieval, research, outlining, drafting, rewriting, title work, image planning, or delivery, initialize or recover the Financial Writing Runtime.

Stage order remains:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

If a required executor/tool is unavailable or a gate fails, stop at the legal stage or `BLOCKED`. Never silently bypass the runtime.

## Recovery authority
The MCP runtime checkpoint is the executable authority for writing tasks. A fresh conversation recovers unfinished work with `list_recent_writing_tasks` and `get_writing_task` before asking the user to repeat prior context.

Notion/Drive pointers are governance mirrors and human-readable recovery aids. They must not override a newer runtime checkpoint. This repository `main` is the code/rule truth.

## Default contract
Unless the user explicitly overrides the current task:
- unspecified destination/platform → `DUAL`;
- `DUAL` = one complete research base + independently edited `FINANCE_DEEP` and `FINANCE_BROAD` articles;
- formal article language = Simplified Chinese financial prose;
- delivery = `WORD_FILE_ONLY`;
- normal new Word-article tasks are publication-ready workflows and include visuals unless the user explicitly says no images or the task is only auditing/delivering an existing document;
- do not paste article body/draft/preview into chat under `WORD_FILE_ONLY`;
- completion requires all applicable Word artifacts plus `WRITING_AUDIT_REPORT.docx`; when visuals are enabled, the visual manifest is also required.

## Cognition before selective writing
Writing, future stock-picking, and future review workflows should ultimately share one broad/deep market knowledge layer. Before selecting what to write, build or recover enough cognition to understand the catalyst, concept map, industry chain, company fundamentals, A-share universe, market-selection logic, and—when relevant—short-term market roles such as leader, liquidity carrier/中军, follow-up/补涨, position/catch-up/卡位, arbitrage role, crowding,抢筹 and order-book/seal-strength signals.

Persistent knowledge is context, not unquestioned truth. Re-verify time-sensitive facts and market-state signals with current evidence. The writer should know substantially more than the final article contains.

## Editorial behavior
- Default to continuous report-style prose, not fragmented notes.
- Use conclusion-first openings when it improves clarity: quickly establish what changed, why it matters, and the central judgment; do not force a rigid formula when the topic needs another opening.
- Paragraphs and sections must connect through causal, contrastive, chronological, or inferential transitions; avoid stitched-block feeling.
- Use Chinese hierarchy in formal articles: `一、二、三` → `（1）（2）（3）` → `①②③`; do not use `·` as a primary hierarchy marker.
- Preserve individuality and judgment while staying evidence-bounded.
- Apply the anti-AI style guide and remove unjustified superlatives/extreme phrasing, including “最…” claims when they are rhetorical rather than strictly evidenced.
- Do not use a fixed article-length target. Compress repetition/background before cutting reasoning.

## Visual workflow
When visuals are enabled, image generation is a DELIVERY sub-workflow, not a substitute for research or writing.
- Plan one 16:9 hero image plus additional images at roughly one per 700 Chinese characters, but prioritize semantic blocks/H1 themes over mechanical counting.
- Image text need not repeat the H1. Prefer a shorter, larger-font semantic hook derived from that block so the reader does not read the same heading twice.
- Use the user's approved avatar as a small circular element integrated naturally into every requested cover/section image; never silently substitute another portrait.
- After image generation, submit the visual package to the runtime. Deterministic delivery inserts images into the relevant Word document: centered, no crop, consistent width/aspect handling, hero near the start and section images after their semantic anchors.
- Each applicable Word article should be publication-ready; reuse an image across DEEP/BROAD only when the semantic anchor genuinely matches.

## WeChat sticker-post mode
微信贴图/流量贴 is a separate packaging mode, not a shortened formal article. Before execution, verify current platform/UI limits and current distribution/recommendation behavior; do not hard-code remembered title/body limits. Image is often the first-entry hook, vertical creative is commonly appropriate, copy is shorter, and interaction/comment/follow intent matters. See `references/platforms.md` and `references/visuals.md`.

## Risk/compliance
A topic-specific risk warning and disclaimer are mandatory for formal public financial articles. Keep them concise but information-dense: shorten wording, not material risk content. A disclaimer never cures actionable buy/sell guidance.

## Final visible checklist
Every formal delivery must include a concise visible checklist status in chat (without pasting the article body under `WORD_FILE_ONLY`) covering: runtime/gates, research/evidence, structure/style, Word/mechanical QA, compliance/risk disclaimer, visuals if enabled, and knowledge reuse/writeback if applicable. The audit report remains the detailed evidence artifact.

## Progressive references
Load only what the active stage needs:
- Research: `references/research.md`, `references/knowledge.md`
- Research/final audit: `references/audit.md`
- Editorial/title/draft: `references/editorial.md`, `references/style.md`, optionally `references/structure_patterns.md`
- Platform packaging: `references/platforms.md`
- Visual planning/delivery: `references/visuals.md`
- Word/output: `references/delivery.md`
- Durable changes: `references/maintenance.md`

## Canonical implementation
Repository: `D1traverser-debug/financial-writing-agent`
Canonical branch: `main`

Legacy Drive/Notion writing rule stacks are migration references only; do not reintroduce them as competing executable authorities.