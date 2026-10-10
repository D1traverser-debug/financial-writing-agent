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

## Explicit bold skim path
Bold is semantic navigation, not entity decoration.

The drafting layer explicitly marks `**...**` spans for the minimum useful set of:
- important keywords/entities when they matter to the argument;
- key numbers;
- selected key judgment sentences.

The deterministic builder preserves those spans. It **does not automatically bold every occurrence of every company/stock name**.

A fast reader who sees only **title + H1s + explicit bold spans** should still recover the topic, main transmission chain, important comparison/selection logic and conclusion boundary. Mechanical QA verifies the declared `skim_path_anchors` survived as bold; semantic audit judges whether the skim path is actually informative.

## Risk warning / disclaimer
Each formal public-finance payload provides a topic-specific `risk_disclaimer`. Delivery appends the final risk/disclaimer section deterministically so it cannot be omitted or duplicated by drafting drift.

A disclaimer never cures actionable buy/sell instructions.

## No visual workflow
Financial Writing has no image-generation, cover, section-image, avatar, sticker, visual-manifest or image-insertion step. Image work is outside this runtime.

## Mechanical verification
For every applicable article Word file, check:
- required artifact exists before mechanical PASS;
- H1/H2/H3/body typography matches policy;
- hierarchy is legal;
- zero tables;
- every required explicit skim anchor is bold;
- risk/disclaimer presence and minimum substance;
- deterministic actionable-finance red lines;
- render succeeds when render QA is required.

Repeated rendering must be idempotent: stale page images from an earlier document version must not be mixed into current render evidence.

Generic superlatives and context-sensitive promotional language belong to semantic review unless the phrase is unambiguously prohibited by policy; deterministic scanning should avoid unnecessary false positives.

## Artifact privacy / identity
Server-local filesystem paths are implementation details. Public MCP results and `WRITING_AUDIT_REPORT.docx` identify artifacts by kind/file name/hash/resource reference, not `/data/...` or other local runtime paths.

A successful render process alone is not proof of perfect pagination. Claim visual page inspection only when rendered page evidence was actually inspected.

## Visible completion checklist
On COMPLETE, chat returns a concise list covering applicable research/evidence, Market Explanation scope, Reader Funnel, Natural Authorial Prose/Writing DNA, general editorial audit, bold skim path, Word/no-table/render, compliance/risk and knowledge sync. The article body remains in Word only.
