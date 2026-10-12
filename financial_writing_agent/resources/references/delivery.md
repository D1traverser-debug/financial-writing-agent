# Delivery module

## Ownership
Delivery owns **Word construction, deterministic typography, hierarchy normalization, fixed A-share entity emphasis, explicit reasoning-emphasis preservation, file identity, mechanical checks and renderability**. It does not decide what evidence is true, what argument should be made or whether a headline is persuasive.

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

## Two-layer bold contract
Publication bold has two distinct jobs and both are required.

### 1. Deterministic A-share company emphasis
Every A-share company/stock name supplied in `ArticleDocument.stock_names` is bolded at **every exact occurrence** in the Word article. This is a durable user formatting preference and is mechanical rather than editorial.

Do not infer additional stock names inside Delivery. The drafting/research path supplies the authoritative A-share name list for the article; overseas companies or other entities are not automatically bold unless they are explicitly emphasized for semantic reasons.

### 2. Explicit semantic skim-path emphasis
The drafting layer separately marks `**...**` spans for important:
- facts / mechanisms;
- key numbers;
- selected judgment sentences;
- other words or phrases needed to reconstruct the argument.

Automatic company bolding **does not replace** these explicit anchors. The deterministic builder preserves both layers.

A fast reader who sees only **title + H1s + all bold spans** should still recover the topic, main transmission chain, important comparison/selection logic and conclusion boundary—not merely a list of A-share names. Mechanical QA verifies both the fixed company-name layer and declared semantic anchors; semantic audit judges whether the resulting skim path is informative.

## Risk warning / disclaimer
Each formal public-finance payload provides a topic-specific `risk_disclaimer`. Delivery appends it deterministically so it cannot be omitted or duplicated by drafting drift.

The publication surface uses **one final inline paragraph beginning `风险提示：`**, with the complete risk paragraph in *italics*. Do not render a separate numbered `风险提示与免责声明` H1. A disclaimer never cures actionable buy/sell instructions.

Risk wording should be **as concise as possible without deleting material risk information**. A fixed minimum character count is not a quality target and must not force boilerplate. Mechanical QA requires a non-empty single italic risk paragraph; semantic audit checks whether it is topic-specific and information-complete.

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
- **every exact occurrence of every supplied A-share company/stock name is bold**;
- every required explicit skim anchor is bold;
- exactly one inline `风险提示：...` paragraph is present, non-empty and fully italic;
- deterministic actionable-finance red lines;
- render succeeds when render QA is required.

Risk paragraph completeness is semantic, not a character-count quota. Deep lower-level hierarchy remains semantically driven, but when Editorial/Audit declares real branching, delivery must preserve the supplied H2/H3 structure rather than flattening it.

Repeated rendering must be idempotent: stale page images from an earlier document version must not be mixed into current render evidence.

Generic superlatives and context-sensitive promotional language belong to semantic review unless the phrase is unambiguously prohibited by policy; deterministic scanning should avoid unnecessary false positives.

## Artifact privacy / identity
Server-local filesystem paths are implementation details. Public MCP results and `WRITING_AUDIT_REPORT.docx` identify artifacts by kind/file name/hash/resource reference, not `/data/...` or other local runtime paths.

A successful render process alone is not proof of perfect pagination. Claim visual page inspection only when rendered page evidence was actually inspected.

## Visible completion checklist
On COMPLETE, chat returns a concise list covering applicable research/evidence, Market Explanation scope, Reader Funnel, Natural Authorial Prose/Writing DNA, general editorial audit, numbered navigation where applicable, **A-share name bolding plus semantic skim path**, Word/no-table/no-underline/source-tail/risk-italic/render, compliance/risk and knowledge sync. The article body remains in Word only.
