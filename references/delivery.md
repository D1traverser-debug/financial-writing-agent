# Delivery module

## Default channel
Unless the task explicitly requests plain chat text, deliver through `WORD_FILE_ONLY`. Under `WORD_FILE_ONLY`, chat contains artifact links/references and concise audit/checklist status only.

If the user explicitly requests **both** the article body in chat and a Word file, route `WORD_AND_CHAT`. This is not equivalent to `CHAT_TEXT`: the runtime must require the chat-text artifact **and** every normal Word/audit artifact for the applicable content/distribution mode. Word construction, mechanical QA, render review, final artifact identity and `WRITING_AUDIT_REPORT.docx` remain mandatory. `CHAT_TEXT` is reserved for a request that actually excludes Word/file delivery or otherwise asks only for direct chat/plain-text output.

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
- Do not use underlining as an article-emphasis system.

Numbering clarifies structure; it must not convert the article into fragmented notes. Paragraph breaks should reflect real argument/subject shifts. Short internal line breaks or compact emphasis are acceptable only when they remain inside one logical unit rather than manufacturing a pseudo-list.

## Bold skim-reading skeleton
Bold text is not decoration. In material body paragraphs, use a concise main-idea anchor when emphasis materially helps scanning: a directional judgment, key number, causal link, contrast or compact conclusion. Avoid mechanically bolding large amounts of prose merely to increase coverage.

The final semantic audit should read the title + structural headings + body bold anchors as a separate skim layer. That layer should reconstruct the central event, causal chain, decisive data/company roles and major conclusion without pretending that every nuance belongs in bold. Mechanical Word checks can prove that intended stock names are bold and that body bold exists; only semantic audit can prove that the emphasis forms a useful information skeleton.

## Risk warning and disclaimer
Formal public financial article payloads must provide a topic-specific `risk_disclaimer` field. Delivery, not the writer, appends the final risk/disclaimer H1 and body. Risk information is mandatory. Optimize for high information density and relatively short wording; do not reduce material risks just to make the paragraph shorter. Generic boilerplate alone is insufficient.

The final risk text should, in concise topic-specific language, make the relevant boundaries clear: public information can change; analysis is evidence-bounded rather than certain; the article is for information/research discussion; it does not constitute securities investment advice or a return promise; and readers remain responsible for independent judgment. Add the topic's actual policy/technology/commercialization/order/market/data-definition uncertainties where material. A disclaimer cannot repair actionable trading guidance in the body.

## Visual insertion
When TaskContract enables visuals, delivery requires a validated visual package backed by real ChatGPT file parameters before Word construction. The builder embeds hero near the start, section images after semantic anchors, centers images, never crops, caps overly tall images while preserving aspect ratio, and records a visual manifest.

## Financial publishing compliance
Public-platform output must not become executable buy/sell guidance. Deterministic scanners catch unambiguous action phrases. Ambiguous words such as “买入/卖出” can also describe factual corporate transactions, so context-sensitive equivalents belong to semantic compliance audit rather than an unconditional substring ban. A disclaimer does not cure actionable instructions.

Compliance applies to the title, independent lead, H1s, bold anchors, ending and interaction text as well as ordinary body paragraphs. Do not move an actionable recommendation out of the body and hide it in a hook or emphasized sentence.

## Verification
After Word creation, run deterministic checks for heading structure/numbering, stock bolding, disclaimer presence/density, unambiguous forbidden phrases and expected image count, then render Word page by page. Render success proves files can be rendered; visual clipping/pagination/image-placement judgment remains a semantic/render review obligation and must not be falsely reported as inspected when page images were not actually viewed.

Rendered pages are internal QA artifacts unless the deployed host exposes them for inspection. When page resources are exposed, every page must actually be inspected before claiming layout QA; check missing glyphs, clipping, overlap, abnormal title wrapping, orphan headings, abnormal blank pages/space, broken image placement and an isolated disclaimer tail page.

Any post-audit change that can affect title/lead/headings/numbering/body structure/bold/facts/page flow invalidates the relevant mechanical/render result. Rebuild and rerender rather than reusing an old PASS because the edit looked small.

## Content metrics and compression boundary
For each final article version, preserve simple content metrics in the audit/reporting layer: total article character count, body character count, and whether compression removed any independent fact, key number, causal step, counterexample, `why_this / why_not`, market-selection mechanism, validation/falsification condition or risk boundary. Metrics are diagnostics, not target word-count quotas.

## File identity and output boundary
Intermediate draft/enhanced/de-AI/render-QA files are working artifacts, not automatically final publication assets. `COMPLETE` refers only to the required final artifacts recorded by the runtime.

Before claiming a file is the final deliverable, verify its recorded artifact kind, task identity, existence and checksum/readback state. Connected-governance copies/mirrors are secondary publication/archival actions and must not silently replace runtime artifact identity. A successful upload/copy call is not itself proof that the intended final file was stored; use the connected system's readback/metadata when claiming external persistence.

## Visible completion checklist
On COMPLETE, chat returns a concise checklist for runtime/gates, research/evidence, structure/style, Word/render, compliance/risk, visuals and knowledge synchronization where applicable. Detailed evidence remains in `WRITING_AUDIT_REPORT.docx`.
