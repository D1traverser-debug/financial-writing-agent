# Delivery module

## Default channel
Unless the task explicitly requests plain chat text, deliver through `WORD_FILE_ONLY`. Under `WORD_FILE_ONLY`, chat contains artifact links/references and concise audit/checklist status only.

## Word construction
Mechanical formatting belongs to code, not the drafting model.
- Article title: dedicated centered title formatting.
- Only first-level article headings use a Word heading style.
- H1: red, bold, ~18pt.
- H2: Normal + bold, ~13.5pt.
- H3: Normal + bold, ~12pt.
- Body: ~12pt.
- Formal hierarchy is normalized deterministically to `一、二、三` → `（1）（2）（3）` → `①②③`; `·` is not a primary hierarchy marker.
- Stock/company names supplied by research state are automatically bolded on every occurrence.
- Default to prose rather than tables unless a table materially improves the task.

## Risk warning and disclaimer
Formal public financial article payloads must provide a topic-specific `risk_disclaimer` field. Delivery, not the writer, appends the final risk/disclaimer H1 and body. Risk information is mandatory. Optimize for high information density and relatively short wording; do not reduce material risks just to make the paragraph shorter. Generic boilerplate alone is insufficient.

## Visual insertion
When TaskContract enables visuals, delivery requires a validated visual package backed by real ChatGPT file parameters before Word construction. The builder embeds hero near the start, section images after semantic anchors, centers images, never crops, caps overly tall images while preserving aspect ratio, and records a visual manifest.

## Financial publishing compliance
Public-platform output must not become executable buy/sell guidance. Deterministic scanners catch unambiguous action phrases. Ambiguous words such as “买入/卖出” can also describe factual corporate transactions, so context-sensitive equivalents belong to semantic compliance audit rather than an unconditional substring ban. A disclaimer does not cure actionable instructions.

## Verification
After Word creation, run deterministic checks for heading structure/numbering, stock bolding, disclaimer presence/density, unambiguous forbidden phrases and expected image count, then render Word page by page. Render success proves files can be rendered; visual clipping/pagination/image-placement judgment remains a semantic/render review obligation and must not be falsely reported as inspected when page images were not actually viewed.

Rendered pages are internal QA artifacts unless the deployed host exposes them for inspection.

## Visible completion checklist
On COMPLETE, chat returns a concise checklist for runtime/gates, research/evidence, structure/style, Word/render, compliance/risk, visuals and knowledge synchronization where applicable. Detailed evidence remains in `WRITING_AUDIT_REPORT.docx`.
