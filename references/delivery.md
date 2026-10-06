# Delivery module

## Default channel

Unless the current task explicitly requests plain chat text, deliver through `WORD_FILE_ONLY`.

Do not paste the article body, draft or preview into chat when `WORD_FILE_ONLY` is active. Chat delivery contains artifact links and concise audit status only.

## Word construction

Mechanical formatting belongs to code, not the drafting model.

- Article title: dedicated title formatting.
- Only first-level article headings use a Word heading style.
- First-level headings: red, bold, approximately 18pt.
- Second-level headings: Normal style + bold, approximately 13.5pt.
- Third-level headings: Normal style + bold, approximately 12pt.
- Body: approximately 12pt.
- Stock/company names supplied by the research state are automatically bolded on every occurrence.
- Default to prose rather than tables unless the task explicitly benefits from a table.
- End with a topic-specific risk warning and disclaimer.

## Financial publishing compliance

Default public-platform output must not become executable buy/sell guidance. Lexical scanners catch obvious red-line phrases; semantic audit catches disguised equivalents. A disclaimer does not cure actionable trading instructions.

## Verification

After Word creation:
1. run programmatic checks;
2. render the Word document page by page;
3. inspect every page for clipping, broken pagination, missing glyphs, heading breaks and disclaimer layout;
4. modify and re-render if needed.

Rendered pages are internal QA artifacts, not article deliverables.
