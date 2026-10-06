# Platform adaptation

This file owns distribution mechanics, not generic writing method.

## Default routing
If no destination/platform is specified for a normal formal article, use `DUAL` by default.

## Finance communities
Typical targets: Xueqiu, Jiuyangongshe and Eastmoney-style finance communities. Use `FINANCE_DEEP`: retain industry transmission, company-universe competition, market-selection logic and verification points.

## Broad-distribution platforms
Typical targets: Toutiao, Baijiahao, NetEase-style distribution and similar feeds. Use `FINANCE_BROAD`: remain a financial article, but frame the topic so finance readers outside the sector understand investment relevance.

## WECHAT_STICKER_POST
An explicit 微信贴图 request is a separate executable content mode, not a shortened formal article and not DUAL. Its deliverable is `WECHAT_STICKER_POST.docx` plus `VISUAL_MANIFEST.json` when visuals are enabled.

Before writing, verify the **current** publisher UI/documentation and available current platform evidence. Store this as `PlatformConstraintSnapshot` with `verified_at`, source references and any currently verifiable numeric title/body/image limits. Runtime may enforce numeric limits from that snapshot. Permanent policy intentionally keeps remembered title/body/image limits as null rather than hard-coding them.

The image is often the first visual entry point, but treat that as a current platform hypothesis to verify rather than an eternal law. When current evidence supports it, prefer dedicated vertical creative. Separate four jobs: image hook, title hook, useful body information, and interaction/comment/follow prompt. They should complement rather than repeat one another. Avoid pure clickbait with no useful information.

## Platform data discipline
Treat platform algorithms as changing external systems. Prefer current official/current UI evidence and the account's recent performance data when available. One viral/failed article is an experience sample, not a permanent rule.

Separate distribution/recommendation signals, search/long-tail signals, article-quality signals and account-specific observed performance. Never let a platform tactic redefine the core evidence/editorial method.
