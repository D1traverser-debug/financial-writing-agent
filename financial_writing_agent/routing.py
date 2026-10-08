from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from .models import ContentMode, DeliveryChannel, DistributionMode, TaskContract
from .resources import load_packaged_policy

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


def infer_content_mode(prompt: str, platforms: Iterable[str] | None = None) -> ContentMode:
    normalized = prompt.replace(" ", "")
    platform_text = "".join(platforms or [])
    combined = normalized + platform_text
    if "微信贴图" in combined or ("微信" in combined and "贴图" in combined):
        return ContentMode.WECHAT_STICKER_POST
    return ContentMode.FORMAL_ARTICLE


def infer_delivery_channel(prompt: str) -> DeliveryChannel:
    normalized = prompt.replace(" ", "")
    lower = normalized.lower()
    explicit_chat = (
        ("聊天框" in normalized and any(x in normalized for x in ["正文", "纯文本", "直接看"]))
        or "只要纯文本" in normalized
    )
    word_forbidden = any(x in lower for x in ["不要word", "不需要word", "不用word", "不要docx", "不需要docx"])
    explicit_word = ("word" in lower or "docx" in lower) and not word_forbidden
    if explicit_chat and explicit_word:
        return DeliveryChannel.WORD_AND_CHAT
    return DeliveryChannel.CHAT_TEXT if explicit_chat else DeliveryChannel.WORD_FILE_ONLY


def infer_visuals_enabled(prompt: str, delivery_channel: DeliveryChannel) -> bool:
    if delivery_channel == DeliveryChannel.CHAT_TEXT:
        return False
    normalized = prompt.replace(" ", "")
    if any(x in normalized for x in ["不要图片", "不要配图", "不做图", "不需要配图", "纯文字即可", "纯文字就行"]):
        return False
    if any(x in normalized.lower() for x in ["word已经写好了", "word已写好", "现成word", "已有word"]):
        return False
    return True


def _default_run_constraints() -> dict[str, int]:
    defaults = load_packaged_policy()["defaults"]
    return {
        "research_max_rounds": int(defaults["research_max_rounds"]),
        "title_max_rounds": int(defaults["title_max_rounds"]),
        "draft_max_rounds": int(defaults["draft_max_rounds"]),
    }


def build_task_contract(
    *,
    prompt: str,
    source_refs: list[str] | None = None,
    target_platforms: list[str] | None = None,
    visuals_enabled: bool | None = None,
    visual_profile_ref: str | None = None,
    content_mode: ContentMode | None = None,
    effective_time_boundary: datetime | None = None,
) -> TaskContract:
    platforms = target_platforms or []
    delivery = infer_delivery_channel(prompt)
    visuals = infer_visuals_enabled(prompt, delivery) if visuals_enabled is None else visuals_enabled
    mode = content_mode or infer_content_mode(prompt, platforms)
    kwargs = {
        "prompt": prompt,
        "source_refs": source_refs or [],
        "target_platforms": platforms,
        "distribution_mode": infer_distribution_mode(platforms),
        "content_mode": mode,
        "delivery_channel": delivery,
        "visuals_enabled": visuals,
        "visual_profile_ref": visual_profile_ref,
        "run_constraints": _default_run_constraints(),
    }
    if effective_time_boundary is not None:
        kwargs["effective_time_boundary"] = effective_time_boundary
    return TaskContract(**kwargs)
