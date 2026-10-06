from financial_writing_agent.models import ArtifactKind, DeliveryChannel, DistributionMode
from financial_writing_agent.routing import build_task_contract, infer_distribution_mode


def test_mixed_finance_and_broad_platforms_route_dual():
    assert infer_distribution_mode(["雪球", "头条号"]) == DistributionMode.DUAL


def test_finance_only_routes_deep():
    assert infer_distribution_mode(["雪球", "韭研公社", "东方财富"]) == DistributionMode.FINANCE_DEEP


def test_broad_only_routes_finance_broad():
    assert infer_distribution_mode(["头条号", "百家号"]) == DistributionMode.FINANCE_BROAD


def test_default_delivery_is_word_and_chat_requires_explicit_request():
    c = build_task_contract(prompt="根据这两个链接写文章")
    assert c.delivery_channel == DeliveryChannel.WORD_FILE_ONLY
    assert ArtifactKind.AUDIT_DOCX in c.required_outputs

    c2 = build_task_contract(prompt="给我直接在聊天框看正文")
    assert c2.delivery_channel == DeliveryChannel.CHAT_TEXT
    assert c2.required_outputs == [ArtifactKind.CHAT_TEXT]
