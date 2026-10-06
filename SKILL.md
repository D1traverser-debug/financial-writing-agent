---
name: financial-writing-agent
description: Deterministic A-share financial writing workflow for formal articles and image-first WeChat sticker posts. Use for writing, rewriting, continuation, audit, retitling, publication-ready Word delivery, or short financial sticker-post packaging. Runtime first; never silently fall back to free-form writing.
---

# Financial Writing Agent

## Runtime first
Before source retrieval, research, outlining, drafting, rewriting, title work, image planning, or delivery, initialize or recover the Financial Writing Runtime.

Stage order remains:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

If a required executor/tool is unavailable or a gate fails, stop at the legal stage or `BLOCKED`. Never silently bypass the runtime.

## Recovery authority
The MCP runtime checkpoint is the executable authority for writing tasks. A fresh conversation recovers unfinished work with `list_recent_writing_tasks` and `get_writing_task` before asking the user to repeat prior context. Notion/Drive pointers are governance mirrors and human-readable recovery aids; they do not override a newer runtime checkpoint. Repository `main` is the code/rule truth.

## Default contract
Unless the user explicitly overrides the current task:
- unspecified destination/platform → `DUAL`;
- normal formal content mode → `FORMAL_ARTICLE`;
- `DUAL` = one complete research base + independently edited `FINANCE_DEEP` and `FINANCE_BROAD` articles;
- formal article language = Simplified Chinese financial prose;
- delivery = `WORD_FILE_ONLY`;
- normal new Word-article tasks include publication-ready visuals unless the user explicitly opts out or the task is only auditing/delivering an existing document;
- do not paste article body/draft/preview into chat under `WORD_FILE_ONLY`;
- completion requires all applicable Word artifacts plus `WRITING_AUDIT_REPORT.docx`; when visuals are enabled, `VISUAL_MANIFEST.json` is also required.

## Cognition before selective writing
Writing, future stock-picking, and future review workflows should ultimately share one broad/deep market knowledge layer. Before selecting what to write, build or recover enough cognition to understand catalyst, concept map, industry chain, company fundamentals, A-share universe, market-selection logic, and—when relevant—leader/中军/补涨/卡位/套利/身位/抢筹/封单等 short-term roles/signals.

When connected Notion/Drive/StockBase/EventBase knowledge is available, ChatGPT retrieves it with the appropriate connector **after runtime start but before open-web expansion**, then records the recovered references with `record_knowledge_context`. The standalone Python runtime does not pretend to own those connector credentials. Current/material claims must still be reverified.

Research emits `knowledge_writeback_candidates`. Before final audit, write reusable evidence-bounded items back through the connected store when available and call `record_knowledge_writeback` with receipts; use `N_A` with an explicit reason when no connected write target exists. Do not claim cross-agent synchronization that has not been implemented.

## Editorial behavior
- Default to continuous report-style prose, not fragmented notes.
- Use conclusion-first openings when useful, not as a rigid template.
- Paragraphs and sections must connect through causal, contrastive, chronological, comparative, narrowing, or inferential transitions.
- Formal hierarchy: `一、二、三` → `（1）（2）（3）` → `①②③`; never use `·` as a primary hierarchy marker.
- Preserve individualized judgment while remaining evidence-bounded.
- Remove unjustified superlatives/extreme phrasing, including rhetorical “最…” claims; factual ranking claims require evidence.
- No fixed article-length target; compress repetition/background before cutting reasoning.

## Dedicated anti-AI/style judge
Anti-AI quality is not a writer self-check and not only a banned-word scan. At `EDITORIAL_AUDIT`, run a separate style judge first and call `submit_style_audit`. It audits template fingerprints, repetitive rhetorical constructions, over-regular pacing, empty bridges, abrupt transitions and unsupported extreme language. General editorial audit cannot PASS until the style gate passes.

## Formal visual workflow
When visuals are enabled, image generation is a DELIVERY sub-workflow, not a substitute for research/writing.
- one 16:9 hero + additional images at roughly one per 700 Chinese characters, prioritizing H1/semantic blocks over mechanical counting;
- image text may be a shorter semantic hook rather than a duplicate H1;
- use the user's approved avatar as a small circular integrated element; never silently substitute another portrait;
- after generation call `submit_visual_package`; deterministic delivery inserts images centered, uncropped, at recorded anchors.

## WeChat sticker-post mode
An explicit 微信贴图 request routes to `WECHAT_STICKER_POST`, not to a shortened DUAL article. The runtime requires a separate `WECHAT_STICKER_POST.docx` artifact. Before drafting, verify current title/body/image limits and relevant distribution/recommendation mechanics using current evidence. Draft output contains a `PlatformConstraintSnapshot` with verification time and source references; remembered limits are never hard-coded. Runtime validates title/body against the verified snapshot when numeric limits are available.

Sticker creative is image-first: use one or more dedicated vertical images when current platform evidence supports it; image hook, title, body and interaction prompt should complement rather than repeat one another. Keep copy concise but useful, suitable for attention/comment/follow intent without empty clickbait. Sticker visual assets use `article_mode=WECHAT_STICKER_POST` and role `sticker`/`hero`, then are embedded into the Word package.

## Risk/compliance
A topic-specific risk warning and disclaimer are mandatory for public financial content. Keep them concise but information-dense: shorten wording, not material risk content. A disclaimer never cures actionable buy/sell guidance.

## Final visible checklist
After runtime `COMPLETE`, the MCP summary includes `completion_checklist`. Return it concisely in chat together with artifact links, covering runtime/gates, research/evidence, structure/style/continuity, Word/render, compliance/risk, visuals, and knowledge reuse/writeback. Under `WORD_FILE_ONLY`, do not paste the article body.

## Progressive references
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
