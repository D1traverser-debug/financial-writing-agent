# Delivery module

## Ownership
Delivery owns **Word construction, deterministic typography, hierarchy normalization, explicit emphasis preservation, file identity, mechanical checks and renderability**. It does not decide what evidence is true, what argument should be made or whether a headline is persuasive.

## Default channel
Formal publication content is delivered **only as Word**. Do not paste the article body or preview into chat.

Completion has two QA surfaces:
1. `WRITING_AUDIT_REPORT.docx` — durable detailed QA evidence;
2. a concise chat checklist/list — visible status for required gates.

## Word construction
Mechanical formatting belongs to code, not the drafting model.
- Article title: centered, current policy controls exact size.
- H1: red + bold, **24px equivalent = 18pt**.
- H2: Normal + bold, **20px equivalent = 15pt**.
- H3: Normal + bold, current policy 12pt unless changed.
- Body: **18px equivalent = 13.5pt**.
- px→pt uses standard CSS/96-dpi equivalence `1px = 0.75pt` because Word stores point sizes.
- Hierarchy is normalized to `一、二、三 → （1）（2）（3） → ①②③`.
- Publication tables are prohibited.
- **Underlines are prohibited everywhere in publication Word**, including title, headings, body, risk text and generated audit text. Emphasis uses hierarchy, bold or italics only when semantically justified.

## Source presentation
Do **not** append a publication-tail bibliography or a `资料来源 / 参考资料 / 参考来源 / 来源汇总` section to the article by default.

Evidence provenance still matters. Keep source IDs/URLs and research attribution in the ResearchPackage and audit evidence, and use natural in-text attribution when the source identity is material to the claim (for example, “公司公告显示” or “监管文件提出”). Removing the end source appendix never licenses uncited invention or loss of evidence traceability.

## Explicit bold skim path
Bold is semantic navigation, not entity decoration.

The drafting layer explicitly marks `**...**` spans for the minimum useful set of:
- important keywords/entities when they matter to the argument;
- key numbers;
- selected key judgment sentences.

The deterministic builder preserves those spans. It **does not automatically bold every occurrence of every company/stock name**.

A fast reader who sees only **title + H1s + explicit bold spans** should still recover the topic, main transmission chain, important comparison/selection logic and conclusion boundary. Mechanical QA verifies the declared `skim_path_anchors` survived as bold; semantic audit judges whether the skim path is actually informative.

## Risk warning / disclaimer
Each formal public-finance payload provides a topic-specific `risk_disclaimer`. Delivery appends it deterministically so it cannot be omitted or duplicated by drafting drift.

The publication surface uses **one final inline paragraph beginning `风险提示：`**, with the complete risk paragraph in *italics*. Do not render a separate numbered `风险提示与免责声明` H1. A disclaimer never cures actionable buy/sell instructions.

## No visual workflow
Financial Writing has no image-generation, cover, section-image, avatar, sticker, visual-manifest or image-insertion step. Image work is outside this runtime.

## Mechanical verification
For every applicable article Word file, check:
- required artifact exists before mechanical PASS;
- H1/H2/H3/body typography matches policy;
- hierarchy is legal;
- zero tables;
- zero underlined runs;
- no publication-tail source/bibliography section;
- every required explicit skim anchor is bold;
- exactly one inline `风险提示：...` paragraph is present, substantive and fully italic;
- deterministic actionable-finance red lines;
- render succeeds when render QA is required.

Repeated rendering must be idempotent: stale page images from an earlier document version must not be mixed into current render evidence.

Generic superlatives and context-sensitive promotional language belong to semantic review unless the phrase is unambiguously prohibited by policy; deterministic scanning should avoid unnecessary false positives.

## Artifact privacy / identity
Server-local filesystem paths are implementation details. Public MCP results and `WRITING_AUDIT_REPORT.docx` identify artifacts by kind/file name/hash/resource reference, not `/data/...` or other local runtime paths.

A successful render process alone is not proof of perfect pagination. Claim visual page inspection only when rendered page evidence was actually inspected.

## Visible completion checklist
On COMPLETE, chat returns a concise list covering applicable research/evidence, Market Explanation scope, Reader Funnel, Natural Authorial Prose/Writing DNA, general editorial audit, bold skim path, Word/no-table/no-underline/source-tail/risk-italic/render, compliance/risk and knowledge sync. The article body remains in Word only.
