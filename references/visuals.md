# Visual planning and Word insertion

## Purpose
Visuals are a publication-delivery layer. They should increase entry appeal and section continuation without duplicating the article or weakening research standards.

## Formal article defaults
When visuals are enabled for a Word article:
- landscape 16:9;
- one hero/overall cover;
- additional section visuals at roughly one per 700 Chinese characters, prioritizing H1/semantic-block boundaries over mechanical counting;
- very short/redundant blocks do not need an image merely to meet a count;
- DEEP and BROAD versions receive publication-ready visual plans appropriate to their own structure; reuse only when semantic anchors truly match.

## Image text
Image text does not need to equal the article H1. Prefer a shorter semantic hook, contradiction, number or summary derived from the block. Keep text sparse and visually large. Avoid forcing the reader to read the same heading twice in succession.

## Avatar
Use the user's approved avatar when available. Present it as a small circular element integrated naturally into an object/environment detail; it must not dominate the image. Do not replace the avatar with another face/portrait without explicit instruction.

## Planning metadata
Every visual records target mode, role, semantic focus, source URI/path, hook text, anchor when applicable, aspect ratio and whether the approved avatar is included. Formal article targets use `FINANCE_DEEP`/`FINANCE_BROAD` with role `hero`/`section`. 微信贴图 uses target `WECHAT_STICKER_POST` and normally role `sticker` (or `hero` for a single lead image).

## Word insertion
Deterministic delivery inserts formal hero after title/before body and section images after recorded anchors. `sticker` assets are treated as image-first lead assets in the sticker Word package. Images are centered, inserted without crop and use a consistent Word width while preserving intrinsic aspect ratio.

## Generation boundary
The ChatGPT/model side owns creative planning and image generation; the deterministic runtime owns asset recording, placement and Word QA. Never fabricate an image path/URL or claim an image was embedded without a recorded asset.

## 微信贴图
Prefer a dedicated vertical composition only when current platform evidence supports it; common candidate aspects are 3:4, 4:5 or 9:16, not a permanent rule. The verified current `PlatformConstraintSnapshot` controls any numeric image count limit. The image hook, title, body and interaction prompt should complement rather than duplicate one another.
