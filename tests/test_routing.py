from financial_writing_agent.models import ArtifactKind, DeliveryChannel, DistributionMode
from financial_writing_agent.routing import build_task_contract, infer_distribution_mode


def test_mixed_finance_and_broad_platforms_route_dual():
    assert infer_distribution_mode(["雪球", "头条号"]) == DistributionMode.DUAL


def test_finance_only_routes_deep():
    assert infer_distribution_mode(["雪球", "韭研公社", "东方财富"]) == DistributionMode.FINANCE_DEEP


def test_broad_only_routes_finance_broad():
    assert infer_distribution_mode(["头条号", "百家号"]) == DistributionMode.FINANCE_BROAD


def test_unspecified_platform_routes_dual_word_only_without_removed_artifacts():
    c = build_task_contract(prompt="根据这两个链接写文章")
    assert c.distribution_mode == DistributionMode.DUAL
    assert c.delivery_channel == DeliveryChannel.WORD_FILE_ONLY
    assert ArtifactKind.AUDIT_DOCX in c.required_outputs
    assert ArtifactKind.FINANCE_DEEP_DOCX in c.required_outputs
    assert ArtifactKind.FINANCE_BROAD_DOCX in c.required_outputs
    assert all("VISUAL" not in kind.value and kind.value != "CHAT_TEXT" for kind in c.required_outputs)


def test_even_explicit_chat_wording_keeps_publication_content_word_only():
    c = build_task_contract(prompt="给我直接在聊天框看正文")
    assert c.delivery_channel == DeliveryChannel.WORD_FILE_ONLY
    assert all(kind.value != "CHAT_TEXT" for kind in c.required_outputs)
    assert not hasattr(ArtifactKind, "CHAT_TEXT")
