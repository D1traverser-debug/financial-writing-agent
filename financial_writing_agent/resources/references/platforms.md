# Platform adaptation

This file owns distribution mechanics, account/platform observations and platform-specific packaging, not generic writing method.

## Default routing
If no destination/platform is specified for a normal formal article, use `DUAL` by default.

## Finance communities
Typical targets: Xueqiu, Jiuyangongshe and Eastmoney-style finance communities. Use `FINANCE_DEEP`: retain industry transmission, company-universe competition, market-selection logic and verification points, but still prefer the shortest complete analytical expression over unnecessary length.

## Broad-distribution platforms
Typical targets: Toutiao, Baijiahao, NetEase-style distribution and similar feeds. Use `FINANCE_BROAD`: remain a financial article, but frame the topic so finance readers outside the sector understand investment relevance. Lower entry cost without deleting the strongest contradiction or the core causal chain.

For broad distribution, optimize the full funnel rather than click-through alone: **click → first-screen retention → continuation → end-of-article reach → downstream comment/engagement/monetization opportunity when the actual account/platform places those opportunities after the article**. Do not assume that every platform monetizes the same way; use this objective only when current account/platform evidence supports it.

Under the current default editorial policy, FINANCE_BROAD normally targets roughly 900–1500 Chinese characters and should not exceed 1800 without an explicit policy override. The point is not shortness for its own sake: compress background, repeated examples, secondary branches and ceremonial recap so the reader reaches the decisive payoff and article end sooner.

## Connected platform/account knowledge
When the user explicitly asks to optimize recommendation, click-through, search, retention or account-specific performance, include completion/end reach and engagement when they are part of the current account objective. If a connected ArticleBase/platform-method store is available, retrieve the **current relevant version** as an input after Runtime start. Treat it as platform evidence/experience, not as a second copy of the generic headline/editorial rules.

Separate:
- platform/distribution mechanics that are currently evidenced;
- account-specific observed performance;
- hypotheses still being tested;
- generic article-quality/editorial method, which remains owned by editorial/style/reader-value references.

One viral or failed article, one title pattern, one topic category, one reader comment about length or one short observation window is an experience sample. Do not promote it to a permanent formula without repeated, comparable evidence that controls for topic, distribution conditions, timing and obvious outliers. A user-specified business objective such as prioritizing completion for downstream monetization may still be used as an optimization target without pretending it is a universal platform law.

## Structured ArticleExperienceSample
When real post-publication/account performance is available, preserve it as a structured `ArticleExperienceSample` rather than an unqualified note such as “这个标题有效”. This is an experience/governance contract, not a claim that the current Writing Runtime automatically fetches or promotes platform analytics.

Record only fields the platform/account actually exposes, preserving unavailable values as unavailable rather than inventing zeroes. A useful sample should include when available:
- stable `article_ref` / article identity;
- platform/account context and distribution mode;
- topic/category;
- publish time and explicit observation window;
- final title/hook mechanism and article character count;
- available exposure/impression, click/read, completion/read-duration, comment, share, follow, search, conversion or monetization measurements;
- traffic-source mix;
- comparable account/topic baseline or cohort;
- material confounders such as topic heat, account growth, paid versus organic distribution, external traffic, timing, policy/event intensity or platform-feature changes;
- reader-feedback samples kept separate from behavioral metrics;
- the hypothesis the sample supports or challenges;
- confidence `LOW / MEDIUM / HIGH` with rationale;
- `promotion_status = SAMPLE_ONLY` by default.

`0`, missing and unavailable are distinct states. Do not backfill unavailable metrics with estimates merely to make samples comparable.

### Experience promotion discipline
One high- or low-performing article is not a durable method. A platform/account experience may be promoted beyond `SAMPLE_ONLY` only when at least one defensible authority exists:
1. the user explicitly declares a stable business objective/rule;
2. repeated, reasonably comparable samples support the same relationship after obvious confounders are considered; or
3. a current authoritative platform source establishes the mechanism.

Even after promotion, retain source/sample window, scope and reversibility because platform mechanics change. Reader comments are qualitative evidence; one comment is not audience-level behavioral proof. Correlation between article design and performance is not automatically causal.

The current repository does **not** implement an automatic cross-task causal-learning/promotion engine. Promotion remains maintenance/governance work unless and until an executable workflow and regression boundary are added.

## WECHAT_STICKER_POST
An explicit 微信贴图 request is a separate executable content mode, not a shortened formal article and not DUAL. Its deliverable is `WECHAT_STICKER_POST.docx` plus `VISUAL_MANIFEST.json` when visuals are enabled.

Before writing, verify the **current** publisher UI/documentation and available current platform evidence. Store this as `PlatformConstraintSnapshot` with `verified_at`, source references and any currently verifiable numeric title/body/image limits. Runtime enforces available numeric limits. The body limit applies to the publishable text package, including body, interaction prompt and risk/disclaimer text. Permanent policy intentionally keeps remembered title/body/image limits as null rather than hard-coding them.

The image is often the first visual entry point, but treat that as a current platform hypothesis to verify rather than an eternal law. When current evidence supports it, prefer dedicated vertical creative. Separate four jobs: image hook, title hook, useful body information, and interaction/comment/follow prompt. They should complement rather than repeat one another. Avoid pure clickbait with no useful information.

## Platform data discipline
Treat platform algorithms as changing external systems. Prefer current official/current UI evidence and the account's recent performance data when available. Do not infer a platform rule from low exposure, a short measurement window, one reader comment or CTR alone when distribution itself may be the limiting factor.

Separate distribution/recommendation signals, search/long-tail signals, article-quality signals and account-specific observed performance. Never let a platform tactic redefine the core evidence/editorial method or weaken factual/evidence/compliance boundaries.
