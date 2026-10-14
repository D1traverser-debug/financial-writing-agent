from __future__ import annotations

from collections.abc import Iterable

from .models import ContentMode, DeliveryChannel, DistributionMode, TaskContract

# 微信公众号 is deliberately dual-role for this user: it carries both the broad
# acquisition article and the deep finance/review article. Putting it in both sets
# makes a WeChat-only target resolve to the full portfolio rather than arbitrarily
# choosing one long-form product.
FINANCE_COMMUNITIES = {"雪球", "韭研公社", "东方财富", "东方财富号", "微信公众号"}
BROAD_FEEDS = {
    "今日头条",
    "头条号",
    "百家号",
    "网易号",
    "企鹅号",
    "企鹅媒体平台",
    "微信公众号",
}


def infer_distribution_mode(platforms: Iterable[str]) -> DistributionMode:
    normalized = {p.strip() for p in platforms if p and p.strip()}
    if not normalized:
        return DistributionMode.PORTFOLIO
    has_deep = bool(normalized & FINANCE_COMMUNITIES)
    has_broad = bool(normalized & BROAD_FEEDS)
    if has_deep and has_broad:
        return DistributionMode.PORTFOLIO
    if has_deep and not has_broad:
        return DistributionMode.FINANCE_DEEP
    if has_broad and not has_deep:
        return DistributionMode.ACQUISITION
    # Unknown/unspecified distribution should not silently drop one of the user's
    # standard products. Default to the full portfolio and let explicit instructions
    # narrow it when needed.
    return DistributionMode.PORTFOLIO


def infer_content_mode(prompt: str, platforms: Iterable[str] | None = None) -> ContentMode:
    # Financial Writing owns formal finance publishing products only. Image generation
    # itself remains outside this runtime; the interaction pack supplies text/copy that
    # the user may pair with images later.
    return ContentMode.FORMAL_ARTICLE


def infer_delivery_channel(prompt: str) -> DeliveryChannel:
    # Publication content is Word-only. QA is surfaced separately as audit Word + chat checklist.
    return DeliveryChannel.WORD_FILE_ONLY


def build_task_contract(
    *,
    prompt: str,
    source_refs: list[str] | None = None,
    target_platforms: list[str] | None = None,
    content_mode: ContentMode | None = None,
) -> TaskContract:
    platforms = target_platforms or []
    return TaskContract(
        prompt=prompt,
        source_refs=source_refs or [],
        target_platforms=platforms,
        distribution_mode=infer_distribution_mode(platforms),
        content_mode=content_mode or ContentMode.FORMAL_ARTICLE,
        delivery_channel=DeliveryChannel.WORD_FILE_ONLY,
    )
