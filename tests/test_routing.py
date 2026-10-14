from financial_writing_agent.models import ArtifactKind, DeliveryChannel, DistributionMode
from financial_writing_agent.routing import build_task_contract, infer_distribution_mode


def test_mixed_finance_and_broad_platforms_route_portfolio():
    assert infer_distribution_mode(["韭研公社", "头条号"]) == DistributionMode.PORTFOLIO


def test_wechat_alone_is_dual_role_portfolio_surface():
    assert infer_distribution_mode(["微信公众号"]) == DistributionMode.PORTFOLIO


def test_finance_only_routes_deep():
    assert infer_distribution_mode(["雪球", "韭研公社", "东方财富"]) == DistributionMode.FINANCE_DEEP


def test_broad_only_routes_acquisition():
    assert infer_distribution_mode(["头条号", "百家号", "网易号", "企鹅号"]) == DistributionMode.ACQUISITION


def test_unspecified_platform_routes_full_portfolio_word_only():
    c = build_task_contract(prompt="根据这两个链接写文章")
    assert c.distribution_mode == DistributionMode.PORTFOLIO
    assert c.delivery_channel == DeliveryChannel.WORD_FILE_ONLY
    assert c.required_outputs == [
        ArtifactKind.AUDIT_DOCX,
        ArtifactKind.FINANCE_DEEP_DOCX,
        ArtifactKind.FINANCE_BROAD_DOCX,
        ArtifactKind.PLATFORM_INTERACTION_PACK_DOCX,
    ]
    assert all("VISUAL" not in kind.value and kind.value != "CHAT_TEXT" for kind in c.required_outputs)


def test_acquisition_mode_contains_broad_and_interaction_pack():
    c = build_task_contract(prompt="写引流版", target_platforms=["头条号", "企鹅号"])
    assert c.distribution_mode == DistributionMode.ACQUISITION
    assert c.required_outputs == [
        ArtifactKind.AUDIT_DOCX,
        ArtifactKind.FINANCE_BROAD_DOCX,
        ArtifactKind.PLATFORM_INTERACTION_PACK_DOCX,
    ]


def test_even_explicit_chat_wording_keeps_publication_content_word_only():
    c = build_task_contract(prompt="给我直接在聊天框看正文")
    assert c.delivery_channel == DeliveryChannel.WORD_FILE_ONLY
    assert all(kind.value != "CHAT_TEXT" for kind in c.required_outputs)
    assert not hasattr(ArtifactKind, "CHAT_TEXT")
