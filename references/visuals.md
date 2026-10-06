# Visual planning and Word insertion

## Purpose
Visuals are a publication-delivery layer. They should increase entry appeal and section continuation without duplicating the article or weakening research standards.

## Formal article defaults
When visuals are enabled for a Word article:
- landscape 16:9;
- exactly one hero/overall cover for each applicable formal article;
- additional section visuals at roughly one per 700 Chinese characters, prioritizing H1/semantic-block boundaries over mechanical counting;
- very short/redundant blocks do not need an image merely to meet a count;
- DEEP and BROAD versions receive publication-ready visual plans appropriate to their own structure; reuse only when semantic anchors truly match.

## Image text
Image text does not need to equal the article H1. Prefer a shorter semantic hook, contradiction, number or summary derived from the block. Keep text sparse and visually large. Avoid forcing the reader to read the same heading twice in succession.

## Avatar
Use the user's approved avatar when an accessible persistent visual profile/reference exists. Present it as a small circular element integrated naturally into an object/environment detail; it must not dominate the image. Do not replace it with another portrait. If the approved avatar is genuinely inaccessible in the current environment, state that once rather than silently fabricating it.

## File contract
Creative image generation is model-side. DELIVERY passes the actual generated images through the MCP `submit_visual_package` top-level `files` parameter. Each `VisualAsset.file_id` must match one ChatGPT file parameter. Do not invent local paths or arbitrary public image URLs. The runtime copies authorized file bytes into task storage before Word construction.

## Planning metadata
Every visual records target mode, role, semantic focus, file ID, hook text, anchor when applicable, explicit aspect ratio and whether the approved avatar is included. Formal article targets use `FINANCE_DEEP`/`FINANCE_BROAD` with role `hero`/`section`. 微信贴图 uses target `WECHAT_STICKER_POST` and normally role `sticker` (or `hero` for a single lead image).

## Word insertion
Deterministic delivery inserts formal hero after title/before body and section images after recorded anchors. `sticker` assets are treated as image-first lead assets in the sticker Word package. Images are centered, inserted without crop and keep aspect ratio; very tall images are height-capped to avoid page overflow.

## 微信贴图
Prefer a dedicated vertical composition only when current platform evidence supports it; common candidate aspects are 3:4, 4:5 or 9:16, not a permanent rule. `aspect_ratio` must be explicit. The verified current `PlatformConstraintSnapshot` controls any numeric image-count limit, and runtime rejects a package that exceeds it. The image hook, title, body and interaction prompt should complement rather than duplicate one another.
