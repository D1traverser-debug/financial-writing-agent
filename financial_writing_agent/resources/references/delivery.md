# Delivery module

## Default channel
Formal writing delivers **publication content only as Word**. Do not paste the article body or preview into chat.

Completion has two QA surfaces:
1. `WRITING_AUDIT_REPORT.docx` — durable detailed QA evidence;
2. a concise **chat checklist/list** — visible status for every required gate.

Therefore “Word only” describes article-content delivery, not silent QA. The chat checklist must never substitute for the audit Word file, and the audit Word file must never suppress the chat checklist.

## Word construction
Mechanical formatting belongs to code, not the drafting model.
- Article title: dedicated centered title formatting; current policy owns its exact size.
- Only first-level article headings use a Word heading style.
- H1: red + bold, **24px equivalent = 18pt**.
- H2: Normal + bold, **20px equivalent = 15pt**.
- H3: Normal + bold, current policy 12pt unless the user explicitly changes it.
- Body: **18px equivalent = 13.5pt**.
- The px→pt mapping uses the standard CSS/96-dpi equivalence `1px = 0.75pt`; Word stores point sizes, so the deterministic builder uses the pt values above.
- Formal hierarchy is normalized deterministically to `一、二、三` → `（1）（2）（3）` → `①②③`.
- Use numbered H2/H3 levels frequently when the reasoning genuinely has layers/steps/categories; do not add empty levels merely to increase numbering.
- Company/stock names supplied by research state are automatically bolded on every occurrence.
- Explicit `**...**` spans are preserved as Word bold for key terms, key numbers and key judgment sentences.
- **Tables are prohibited in publication articles.** Convert comparisons into numbered prose.

## Bold skim-path contract
The final article must contain a deliberate emphasis skeleton. A fast reader who sees only:
**title + H1s + bold spans**
should still recover the topic, main economic transmission, major comparison/selection logic and conclusion boundary.

Mechanical QA verifies required explicit bold anchors and company-name bolding. Semantic audit verifies that the resulting skim path actually makes sense. Do not bold whole paragraphs or large percentages of the article.

## Risk warning and disclaimer
Formal public financial article payloads must provide a topic-specific `risk_disclaimer` field. Delivery, not the writer, appends the final risk/disclaimer H1 and body. Risk information is mandatory, concise and materially complete. Generic boilerplate alone is insufficient. A disclaimer never cures actionable buy/sell guidance.

## No visual workflow
Financial Writing has no image-generation, cover, section-image, avatar or visual-asset step. Image work belongs outside this writing runtime and must not block or alter article completion.

## Financial publishing compliance
Public-platform output must not become executable buy/sell guidance. Deterministic scanners catch unambiguous action phrases. Context-sensitive equivalents belong to semantic compliance audit. A disclaimer does not cure actionable instructions.

## Verification
After Word creation, run deterministic checks for heading structure/numbering, exact policy typography, **absence of tables**, company-name and explicit-key-point bolding, disclaimer presence/density, unambiguous forbidden phrases and successful render. Then inspect rendered pages when page evidence is actually available; render success alone is not visual proof of good pagination.

## Visible completion checklist
On COMPLETE, chat returns a concise list covering at least:
- runtime/stage gates;
- research/evidence and FINANCE_DEEP material-completeness where applicable;
- market-explanation completeness where applicable;
- Reader Funnel / Hook Gate;
- Natural Authorial Prose / Writing DNA Gate;
- general editorial audit;
- bold skim path;
- Word/no-table/render;
- compliance/risk;
- knowledge reuse/writeback.

Detailed evidence remains in `WRITING_AUDIT_REPORT.docx`. No article body is pasted into chat.