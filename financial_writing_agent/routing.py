from __future__ import annotations

from collections.abc import Iterable

from .models import ContentMode, DeliveryChannel, DistributionMode, TaskContract

FINANCE_COMMUNITIES = {"雪球", "韭研公社", "东方财富", "东方财富号"}
BROAD_FEEDS = {"今日头条", "头条号", "百家号", "网易号", "微博头条文章", "微信公众号"}


def infer_distribution_mode(platforms: Iterable[str]) -> DistributionMode:
    normalized = {p.strip() for p in platforms if p and p.strip()}
    if not normalized:
        return DistributionMode.DUAL
    has_deep = bool(normalized & FINANCE_COMMUNITIES)
    has_broad = bool(normalized & BROAD_FEEDS)
    if has_deep and has_broad:
        return DistributionMode.DUAL
    if has_deep and not has_broad:
        return DistributionMode.FINANCE_DEEP
    if has_broad and not has_deep:
        return DistributionMode.FINANCE_BROAD
    return DistributionMode.DUAL


def infer_content_mode(prompt: str, platforms: Iterable[str] | None = None) -> ContentMode:
    normalized = prompt.replace(" ", "")
    platform_text = "".join(platforms or [])
    combined = normalized + platform_text
    if "微信贴图" in combined or ("微信" in combined and "贴图" in combined):
        return ContentMode.WECHAT_STICKER_POST
    return ContentMode.FORMAL_ARTICLE


def infer_delivery_channel(prompt: str) -> DeliveryChannel:
    explicit_chat = ("聊天框" in prompt and any(x in prompt for x in ["正文", "纯文本", "直接看"])) or "只要纯文本" in prompt
    return DeliveryChannel.CHAT_TEXT if explicit_chat else DeliveryChannel.WORD_FILE_ONLY


def infer_visuals_enabled(prompt: str, delivery_channel: DeliveryChannel) -> bool:
    """Writing never owns image generation or image-asset management.

    Visual/image work is a separate workflow. Keep the field for checkpoint/schema
    compatibility, but every newly routed writing task starts with visuals disabled.
    """
    return False


def build_task_contract(
    *,
    prompt: str,
    source_refs: list[str] | None = None,
    target_platforms: list[str] | None = None,
    visuals_enabled: bool | None = None,
    visual_profile_ref: str | None = None,
    content_mode: ContentMode | None = None,
) -> TaskContract:
    platforms = target_platforms or []
    delivery = infer_delivery_channel(prompt)
    if visuals_enabled is True:
        raise ValueError(
            "Image generation/insertion is outside the Writing Agent. "
            "Run the separate visual workflow instead of enabling visuals on a writing task."
        )
    visuals = False
    mode = content_mode or infer_content_mode(prompt, platforms)
    return TaskContract(
        prompt=prompt,
        source_refs=source_refs or [],
        target_platforms=platforms,
        distribution_mode=infer_distribution_mode(platforms),
        content_mode=mode,
        delivery_channel=delivery,
        visuals_enabled=visuals,
        visual_profile_ref=visual_profile_ref,
    )
