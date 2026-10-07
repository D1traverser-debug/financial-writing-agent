from datetime import datetime, timedelta, timezone

import pytest

from financial_writing_agent.models import ArtifactKind, DeliveryChannel, DistributionMode
from financial_writing_agent.routing import build_task_contract, infer_distribution_mode


def test_mixed_finance_and_broad_platforms_route_dual():
    assert infer_distribution_mode(["雪球", "头条号"]) == DistributionMode.DUAL


def test_finance_only_routes_deep():
    assert infer_distribution_mode(["雪球", "韭研公社", "东方财富"]) == DistributionMode.FINANCE_DEEP


def test_broad_only_routes_finance_broad():
    assert infer_distribution_mode(["头条号", "百家号"]) == DistributionMode.FINANCE_BROAD


def test_unspecified_platform_routes_dual_and_new_word_article_enables_visuals():
    before = datetime.now(timezone.utc)
    c = build_task_contract(prompt="根据这两个链接写文章")
    after = datetime.now(timezone.utc)
    assert c.distribution_mode == DistributionMode.DUAL
    assert c.delivery_channel == DeliveryChannel.WORD_FILE_ONLY
    assert c.visuals_enabled is True
    assert ArtifactKind.AUDIT_DOCX in c.required_outputs
    assert ArtifactKind.VISUAL_MANIFEST_JSON in c.required_outputs
    assert c.effective_time_boundary.tzinfo is not None
    assert before <= c.effective_time_boundary.astimezone(timezone.utc) <= after


def test_explicit_historical_effective_time_boundary_is_preserved():
    boundary = datetime(2026, 9, 30, 15, 0, tzinfo=timezone.utc)
    c = build_task_contract(prompt="截至指定时点写文章", effective_time_boundary=boundary)
    assert c.effective_time_boundary == boundary


def test_effective_time_boundary_rejects_naive_or_future_values():
    with pytest.raises(ValueError, match="must include a timezone"):
        build_task_contract(
            prompt="历史时点文章",
            effective_time_boundary=datetime(2026, 9, 30, 15, 0),
        )

    with pytest.raises(ValueError, match="cannot be materially in the future"):
        build_task_contract(
            prompt="未来时点文章",
            effective_time_boundary=datetime.now(timezone.utc) + timedelta(days=1),
        )


def test_chat_and_existing_word_do_not_force_visuals():
    c = build_task_contract(prompt="给我直接在聊天框看正文")
    assert c.delivery_channel == DeliveryChannel.CHAT_TEXT
    assert c.visuals_enabled is False
    assert c.required_outputs == [ArtifactKind.CHAT_TEXT]

    c2 = build_task_contract(prompt="Word已经写好了，直接发我")
    assert c2.delivery_channel == DeliveryChannel.WORD_FILE_ONLY
    assert c2.visuals_enabled is False


def test_explicit_no_images_disables_visuals():
    c = build_task_contract(prompt="根据资料写一篇，不要配图")
    assert c.visuals_enabled is False
    assert ArtifactKind.VISUAL_MANIFEST_JSON not in c.required_outputs
