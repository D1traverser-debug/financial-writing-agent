from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from financial_writing_agent.checks import (
    analyze_publication_scaffolding,
    check_company_decision_utility,
    check_payload_navigation,
    scan_publication_source_leaks,
)
from financial_writing_agent.schemas import InteractionPost, PlatformInteractionPack


def block(kind: str, text: str):
    return SimpleNamespace(kind=kind, text=text)


def test_publication_source_privacy_catches_trigger_article_failure():
    text = "方正证券研报指出，黄酒高端化正在加速。公开资料显示，渠道也在变化。"
    hits = scan_publication_source_leaks(text)
    assert "research_report_attribution" in hits
    assert "public_material_framing" in hits


def test_direct_h1_to_h2_is_rejected_for_image_safe_transition():
    payload = SimpleNamespace(
        blocks=[
            block("lead", "开头。"),
            block("h1", "一、渠道为什么先变"),
            block("h2", "（1）白酒大商开始寻找新利润池"),
            block("body", "正文。"),
        ]
    )
    errors = check_payload_navigation(payload, deep=True)
    assert any("image-safe lead" in error for error in errors)


def test_substantive_h1_lead_allows_lower_heading():
    payload = SimpleNamespace(
        blocks=[
            block("lead", "开头。"),
            block("h1", "一、渠道为什么先变"),
            block("body", "真正值得拆开的，是渠道利润、客户资源和高端场景这三件事正在同时重排；下面的公司差异只有放进这条链路里才有意义。"),
            block("h2", "（1）白酒大商开始寻找新利润池"),
            block("body", "正文。"),
        ]
    )
    assert check_payload_navigation(payload, deep=True) == []


def _research(decision_map):
    return SimpleNamespace(
        universe=[
            SimpleNamespace(name="甲公司", materiality="MATERIAL"),
            SimpleNamespace(name="乙公司", materiality="MATERIAL"),
        ],
        company_decision_map=decision_map,
    )


def test_generic_company_conditional_is_not_a_decision_verdict():
    payload = SimpleNamespace(
        blocks=[
            block("body", "谁能先把高端产品卖出去，谁就更占优势。"),
            block("body", "甲公司和乙公司都在推进相关业务。"),
        ]
    )
    errors = check_company_decision_utility(payload, _research(decision_map=object()))
    assert any("named evidence-bounded comparative verdict" in error for error in errors)
    assert any("generic zero-information" in error for error in errors)


def test_named_relative_company_verdict_passes_decision_utility_gate():
    payload = SimpleNamespace(
        blocks=[
            block("body", "当前证据看，甲公司的相关业务更直接、兑现更快；乙公司的弹性更大，但收入验证链条更长，因此确定性暂时弱于甲公司。"),
        ]
    )
    assert check_company_decision_utility(payload, _research(decision_map=object())) == []


def test_title_h1_body_scaffolding_is_checked_as_one_surface():
    payload = SimpleNamespace(
        title="真正的变化不在价格，而在渠道",
        blocks=[
            block("h1", "一、真正的变化不在产品，而在渠道"),
            block("body", "真正的问题不是能不能卖，而是谁卖得更快。"),
            block("h1", "二、真正的差距不在故事，而在兑现"),
            block("body", "如果只看价格就会漏掉公司差异。"),
            block("body", "这正是需要继续验证的地方。"),
        ],
    )
    result = analyze_publication_scaffolding(payload)
    assert result["requires_revise"] is True
    assert result["surface_h1_count"] == 2


def test_interaction_pack_requires_independent_rewrite_flag_and_multiple_platform_families():
    posts = [
        InteractionPost(platform_family="WECHAT_IMAGE_TEXT", hook="一个价格信号", body="一条完整短逻辑", interaction_prompt="你更看重价格还是渠道？"),
        InteractionPost(platform_family="TOUTIAO_MICRO", hook="渠道先变了", body="另一条短逻辑", interaction_prompt="你觉得哪一步最难？"),
        InteractionPost(platform_family="BAIJIAHAO_DYNAMIC", hook="三家公司开始分化", body="第三条短逻辑", interaction_prompt="你会先验证哪项数据？"),
    ]
    pack = PlatformInteractionPack(
        topic="测试主题",
        posts=posts,
        evidence_boundary="全部来自同一已审计研究包，不新增事实。",
        independent_rewrite_from_long_form=True,
    )
    assert len(pack.posts) == 3

    with pytest.raises(ValidationError, match="independently rewritten"):
        PlatformInteractionPack(
            topic="测试主题",
            posts=posts,
            evidence_boundary="同一证据边界",
            independent_rewrite_from_long_form=False,
        )
