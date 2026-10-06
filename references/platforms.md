# Platform adaptation

This file owns distribution mechanics, not generic writing method.

## Default routing
If no destination/platform is specified for a normal formal article, use `DUAL` by default.

## Finance communities
Typical targets: Xueqiu, Jiuyangongshe and Eastmoney-style finance communities. Use `FINANCE_DEEP`: retain industry transmission, company-universe competition, market-selection logic and verification points.

## Broad-distribution platforms
Typical targets: Toutiao, Baijiahao, NetEase-style distribution and similar feeds. Use `FINANCE_BROAD`: remain a financial article, but frame the topic so finance readers outside the sector understand investment relevance.

## 微信贴图 / image-first short post
Treat 微信贴图/流量贴 as a distinct packaging mode, not a shortened formal article.
- The image is commonly the first visual entry point; vertical creative may be preferred for this format.
- Copy is shorter and may prioritize follow/comment/discussion intent, while still providing real information.
- Title/body length limits, image limits and traffic-pool/recommendation mechanics can change. Before execution, verify the current official UI/documentation and, when available, the account's own current performance data. Do not hard-code remembered limits.
- Separate image hook, title hook, body information and interaction prompt. Avoid pure clickbait with no useful information.

## Platform data discipline
Treat platform algorithms as changing external systems. Before using a platform-specific rule, prefer current official documentation and the account's recent performance data. One viral/failed article is an experience sample, not a permanent rule.

Separate distribution/recommendation signals, search/long-tail signals, article-quality signals and account-specific observed performance. Never let a platform tactic redefine the core evidence/editorial method.