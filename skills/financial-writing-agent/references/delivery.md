# Delivery module

## Default channel
Unless the task explicitly requests plain chat text, deliver through `WORD_FILE_ONLY`. Under `WORD_FILE_ONLY`, chat contains artifact links/references and concise audit/checklist status only.

If the user explicitly requests **both** the article body in chat and a Word file, route `WORD_AND_CHAT`. This is not equivalent to `CHAT_TEXT`: the runtime must require the chat-text artifact **and** every normal Word/audit artifact for the applicable content/distribution mode. Word construction, mechanical QA, render review, final artifact identity and `WRITING_AUDIT_REPORT.docx` remain mandatory. `CHAT_TEXT` is reserved for a request that actually excludes Word/file delivery or otherwise asks only for direct chat/plain-text output.

## Word construction
Mechanical formatting belongs to code, not the drafting model.
- Article title: dedicated **left-aligned** title formatting; do not center the article title.
- Only first-level article headings use a Word heading style.
- H1: red, bold, ~18pt.
- H2: Normal + bold, ~13.5pt.
- H3: Normal + bold, ~12pt.
- Body: ~12pt.
- Formal hierarchy is normalized deterministically to `一、二、三` → `（1）（2）（3）` → `①②③`; `·` is not a primary hierarchy marker.
- Use that hierarchy actively when it exposes real reasoning structure: distinct sub-arguments inside one H1 should normally become H2; an H2 with three or more explicit evidence/condition/dimension units should normally expose H3 rather than burying them in a dense paragraph.
- Do not create hierarchy for decoration, but do not hide obvious multi-level logic in a wall of text merely to keep the article visually flat.
- Stock/company names supplied by research state are automatically bolded on every occurrence.
- Default to prose rather than tables unless a table materially improves the task.
- Do not use underlining as an article-emphasis system.

Numbering clarifies structure; it must not convert the article into fragmented notes. Paragraph breaks should reflect real argument/subject shifts. Short internal line breaks or compact emphasis are acceptable only when they remain inside one logical unit rather than manufacturing a pseudo-list.

## Bold skim-reading skeleton
Bold text is not decoration. In material body paragraphs, use a concise main-idea anchor when emphasis materially helps scanning: a directional judgment, key number, causal link, contrast or compact conclusion. Avoid mechanically bolding large amounts of prose merely to increase coverage.

The final semantic audit should read the title + structural headings + body bold anchors as a separate skim layer. That layer should reconstruct the central event, causal chain, decisive data/company roles and major conclusion without pretending that every nuance belongs in bold. Mechanical Word checks can prove that intended stock names are bold and that body bold exists; only semantic audit can prove that the emphasis forms a useful information skeleton.

## Risk warning and disclaimer
Formal public financial article payloads must provide a topic-specific `risk_disclaimer` field. Delivery, not the writer, appends the final risk/disclaimer H1 and body. The default publication policy requires this boundary even when a particular publisher/account may not fall under exactly the same licensing regime as a licensed investment-consulting institution.

The objective is **minimum sufficient disclosure**, not a long legal wall. Default to roughly **60–120 Chinese characters** and hard-fail obviously bloated risk text above the configured hard cap unless policy is deliberately changed. Keep the highest-value boundaries only: the article is based on public information/research discussion; it is not securities investment advice or a return promise; relevant market/policy/company facts can change and invalidate the judgment; readers should make independent decisions and bear risk. Add at most one compact topic-specific risk clause when the actual article has a material policy/technology/commercialization/order/data-definition uncertainty that would otherwise be hidden.

A concise default formulation can follow this information shape without becoming mandatory wording: “基于公开信息研究讨论，不构成证券投资建议或收益承诺；市场、政策及公司经营均可能变化，结论可能失效，请独立判断并自担风险。”

Do not misuse the disclaimer as a compliance shield. Chinese securities regulation and current enforcement distinguish public financial commentary from licensed securities investment-consulting activity; a disclaimer does **not** legalize unlicensed paid/benefit-linked investment advice, public buy/sell/hold recommendations, guaranteed-return language or other conduct that crosses the applicable regulatory boundary. The body, title, hook and ending must remain compliant on their own.

## Visual insertion
When TaskContract enables visuals, delivery requires a validated visual package backed by real ChatGPT file parameters before Word construction. The builder embeds hero near the start, section images after semantic anchors, centers images, never crops, caps overly tall images while preserving aspect ratio, and records a visual manifest.

## Financial publishing compliance
Public-platform output must not become executable buy/sell guidance. Deterministic scanners catch unambiguous action phrases. Ambiguous words such as “买入/卖出” can also describe factual corporate transactions, so context-sensitive equivalents belong to semantic compliance audit rather than an unconditional substring ban. A disclaimer does not cure actionable instructions.

Compliance applies to the title, independent lead, H1s, bold anchors, ending and interaction text as well as ordinary body paragraphs. Do not move an actionable recommendation out of the body and hide it in a hook or emphasized sentence.

## Verification
After Word creation, run deterministic checks for title alignment, heading structure/numbering, stock bolding, disclaimer presence/density/compactness, unambiguous forbidden phrases, content-length guardrails and expected image count, then render Word page by page. Render success proves files can be rendered; visual clipping/pagination/image-placement judgment remains a semantic/render review obligation and must not be falsely reported as inspected when page images were not actually viewed.

Rendered pages are internal QA artifacts unless the deployed host exposes them for inspection. When page resources are exposed, every page must actually be inspected before claiming layout QA; check missing glyphs, clipping, overlap, abnormal title wrapping, orphan headings, abnormal blank pages/space, broken image placement and an isolated disclaimer tail page.

Any post-audit change that can affect title/lead/headings/numbering/body structure/bold/facts/page flow invalidates the relevant mechanical/render result. Rebuild and rerender rather than reusing an old PASS because the edit looked small.

## Content metrics and compression boundary
For each final article version, preserve simple content metrics in the audit/reporting layer: total article character count, body character count, and whether compression removed any independent fact, key number, causal step, counterexample, `why_this / why_not`, market-selection mechanism, validation/falsification condition or risk boundary.

For `FINANCE_DEEP`, research depth does not authorize prose bloat. The default policy triggers a density review above roughly 6,000 Chinese characters and keeps approximately 10,000 as a hard ceiling. Crossing the density-review threshold is not automatically wrong, but every retained section should materially change the reader's judgment rather than repeat background or explanation.

For `FINANCE_BROAD`, completion/end-of-article reach is a first-class distribution objective. The preferred default range is roughly **900–1500 Chinese characters**; the default hard cap is **1800**. Shorter is acceptable when the hook, one complete causal chain, decisive company/stock judgment and evidence/risk boundary are still intact. Broad should not carry long background, repeated examples or secondary company lists merely because Deep researched them.

Metrics are editorial controls, not excuses to delete information that changes the conclusion. Compress redundancy and low-value explanation before removing independent information.

## File identity and output boundary
Intermediate draft/enhanced/de-AI/render-QA files are working artifacts, not automatically final publication assets. `COMPLETE` refers only to the required final artifacts recorded by the runtime.

Before claiming a file is the final deliverable, verify its recorded artifact kind, task identity, existence and checksum/readback state. Connected-governance copies/mirrors are secondary publication/archival actions and must not silently replace runtime artifact identity. A successful upload/copy call is not itself proof that the intended final file was stored; use the connected system's readback/metadata when claiming external persistence.

## Visible completion checklist
On COMPLETE, chat returns a concise checklist for runtime/gates, research/evidence, structure/style, Word/render, compliance/risk, visuals and knowledge synchronization where applicable. Detailed evidence remains in `WRITING_AUDIT_REPORT.docx`.
