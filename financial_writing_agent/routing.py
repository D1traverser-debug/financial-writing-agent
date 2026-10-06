from __future__ import annotations

from collections.abc import Iterable

from .models import DeliveryChannel, DistributionMode, TaskContract

FINANCE_COMMUNITIES = {"雪球", "韭研公社", "东方财富", "东方财富号"}
BROAD_FEEDS = {"今日头条", "头条号", "百家号", "网易号", "微博头条文章"}


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


def infer_delivery_channel(prompt: str) -> DeliveryChannel:
    explicit_chat = ("聊天框" in prompt and any(x in prompt for x in ["正文", "纯文本", "直接看"])) or "只要纯文本" in prompt
    return DeliveryChannel.CHAT_TEXT if explicit_chat else DeliveryChannel.WORD_FILE_ONLY


def build_task_contract(
    *,
    prompt: str,
    source_refs: list[str] | None = None,
    target_platforms: list[str] | None = None,
) -> TaskContract:
    platforms = target_platforms or []
    return TaskContract(
        prompt=prompt,
        source_refs=source_refs or [],
        target_platforms=platforms,
        distribution_mode=infer_distribution_mode(platforms),
        delivery_channel=infer_delivery_channel(prompt),
    )
