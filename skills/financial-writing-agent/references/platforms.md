# Platform adaptation

This file owns distribution mechanics, account/platform observations and platform-specific packaging, not generic writing method.

## Default routing
If no destination/platform is specified for a normal formal article, use `DUAL` by default.

## Finance communities
Typical targets: Xueqiu, Jiuyangongshe and Eastmoney-style finance communities. Use `FINANCE_DEEP`: retain industry transmission, company-universe competition, market-selection logic and verification points.

## Broad-distribution platforms
Typical targets: Toutiao, Baijiahao, NetEase-style distribution and similar feeds. Use `FINANCE_BROAD`: remain a financial article, but frame the topic so finance readers outside the sector understand investment relevance. Lower entry cost without deleting the strongest contradiction or the core causal chain.

## Connected platform/account knowledge
When the user explicitly asks to optimize recommendation, click-through, search, retention or account-specific performance and a connected ArticleBase/platform-method store is available, retrieve the **current relevant version** as an input after Runtime start. Treat it as platform evidence/experience, not as a second copy of the generic headline/editorial rules.

Separate:
- platform/distribution mechanics that are currently evidenced;
- account-specific observed performance;
- hypotheses still being tested;
- generic article-quality/editorial method, which remains owned by editorial/style references.

One viral or failed article, one title pattern, one topic category or one short observation window is an experience sample. Do not promote it to a permanent formula without repeated, comparable evidence that controls for topic, distribution conditions, timing and obvious outliers.

## WECHAT_STICKER_POST
An explicit 微信贴图 request is a separate executable content mode, not a shortened formal article and not DUAL. Its deliverable is `WECHAT_STICKER_POST.docx` plus `VISUAL_MANIFEST.json` when visuals are enabled.

Before writing, verify the **current** publisher UI/documentation and available current platform evidence. Store this as `PlatformConstraintSnapshot` with `verified_at`, source references and any currently verifiable numeric title/body/image limits. Runtime enforces available numeric limits. The body limit applies to the publishable text package, including body, interaction prompt and risk/disclaimer text. Permanent policy intentionally keeps remembered title/body/image limits as null rather than hard-coding them.

The image is often the first visual entry point, but treat that as a current platform hypothesis to verify rather than an eternal law. When current evidence supports it, prefer dedicated vertical creative. Separate four jobs: image hook, title hook, useful body information, and interaction/comment/follow prompt. They should complement rather than repeat one another. Avoid pure clickbait with no useful information.

## Platform data discipline
Treat platform algorithms as changing external systems. Prefer current official/current UI evidence and the account's recent performance data when available. Do not infer a platform rule from low exposure, a short measurement window or CTR alone when distribution itself may be the limiting factor.

Separate distribution/recommendation signals, search/long-tail signals, article-quality signals and account-specific observed performance. Never let a platform tactic redefine the core evidence/editorial method or weaken factual/evidence/compliance boundaries.
