# Delivery module

## Default channel
Unless the task explicitly requests plain chat text, deliver through `WORD_FILE_ONLY`. Under `WORD_FILE_ONLY`, chat contains artifact links and concise audit/checklist status only.

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
Formal public financial articles must end with a topic-specific risk warning and disclaimer. Risk information is mandatory. Optimize for high information density and relatively short wording; do not reduce material risks just to make the paragraph shorter. Generic boilerplate alone is insufficient.

## Visual insertion
When the TaskContract enables visuals, delivery requires a validated visual package before building Word. The builder:
- embeds the hero near the start;
- embeds section images after recorded semantic anchors;
- centers images;
- does not crop;
- keeps a consistent display width while preserving intrinsic aspect ratio;
- records a visual manifest used by audit.

Creative generation remains model-side; deterministic delivery never invents missing image assets.

## Financial publishing compliance
Public-platform output must not become executable buy/sell guidance. Lexical scanners catch obvious red-line phrases; semantic audit catches disguised equivalents. A disclaimer does not cure actionable instructions.

## Verification
After Word creation:
1. run programmatic checks (heading structure/numbering, stock bolding, disclaimer presence/density floor, forbidden phrases, expected image count);
2. render Word page by page;
3. inspect clipping, broken pagination, missing glyphs, heading breaks, image placement and disclaimer layout;
4. modify/re-render if needed.

Rendered pages are internal QA artifacts.

## Visible completion checklist
On COMPLETE, chat returns a concise checklist for runtime/gates, research/evidence, structure/style, Word/render, compliance/risk, visuals and knowledge synchronization where applicable. Detailed evidence remains in `WRITING_AUDIT_REPORT.docx`.