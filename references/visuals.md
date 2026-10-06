# Visual planning and Word insertion

## Purpose
Visuals are a publication-delivery layer. They should increase entry appeal and section continuation without duplicating the article or weakening research standards.

## Formal article defaults
When visuals are enabled for a Word article:
- use landscape 16:9;
- create one hero/overall cover;
- create additional section visuals at roughly one per 700 Chinese characters, but prioritize H1/semantic-block boundaries over mechanical counting;
- very short/redundant blocks do not need an image merely to meet a count;
- DEEP and BROAD versions receive publication-ready visual plans appropriate to their own structure; reuse is allowed only when semantic anchors truly match.

## Image text
Image text does not need to equal the article H1. Prefer a shorter semantic hook, contradiction, number or summary derived from the block. Keep text sparse and visually large. Avoid forcing the reader to read the same heading twice in succession.

## Avatar
Use the user's approved avatar when available. Present it as a small circular element integrated naturally into an object/environment detail; it must not dominate the image. Do not replace the avatar with another face/portrait without explicit instruction.

## Planning metadata
Every image asset records:
- article mode (`FINANCE_DEEP` or `FINANCE_BROAD`);
- role (`hero` or `section`);
- semantic focus;
- short hook text if any;
- anchor block index for section images;
- source URI/path;
- whether the approved avatar is included.

## Word insertion
Deterministic delivery inserts the hero after the article title/before the body and section images after recorded block anchors. Images are centered, inserted without crop and use a consistent Word width while preserving their intrinsic aspect ratio.

## Generation boundary
The ChatGPT/model side owns creative planning and image generation; the deterministic runtime owns asset recording, placement and Word QA. Never fabricate an image path/URL or claim an image was embedded without a recorded asset.

## 微信贴图
For image-first 微信贴图 mode, prefer a dedicated vertical composition when current platform evidence supports it. Because platform limits/mechanics change, verify current title/body/image constraints before generating the package. The image hook, title and body should complement rather than duplicate one another.