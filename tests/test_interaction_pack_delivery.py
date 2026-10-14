from docx import Document

from financial_writing_agent.checks import check_docx, load_policy
from financial_writing_agent.document import build_interaction_pack_docx
from financial_writing_agent.schemas import InteractionPost, PlatformInteractionPack


def _pack() -> PlatformInteractionPack:
    return PlatformInteractionPack(
        topic="渠道变化测试",
        evidence_boundary="同一已审计研究包；短内容不新增事实。",
        posts=[
            InteractionPost(
                platform_family="WECHAT_IMAGE_TEXT",
                hook="1959元只是表面，渠道利润正在先变。",
                body="甲公司兑现更快，乙公司的弹性更高但验证链更长。",
                interaction_prompt="你更看重兑现速度，还是潜在弹性？",
                stock_names=["甲公司", "乙公司"],
            ),
            InteractionPost(
                platform_family="TOUTIAO_MICRO",
                hook="同一个概念，公司的逻辑并不一样。",
                body="甲公司相关收入更直接；乙公司还需要更多渠道验证。",
                interaction_prompt="如果只看一个数据，你会先看收入还是渠道？",
                stock_names=["甲公司", "乙公司"],
            ),
            InteractionPost(
                platform_family="BAIJIAHAO_DYNAMIC",
                hook="价格抬高，不代表所有公司一起受益。",
                body="当前证据更支持甲公司的兑现确定性，乙公司保留更高弹性但边界更大。",
                interaction_prompt="你觉得确定性和弹性哪个更重要？",
                stock_names=["甲公司", "乙公司"],
            ),
        ],
    )


def test_interaction_pack_renders_as_word_without_article_risk_requirement(tmp_path):
    policy = load_policy("config/policy.json")
    path = build_interaction_pack_docx(_pack(), tmp_path / "interaction.docx", policy)
    assert path.is_file()
    text = "\n".join(p.text for p in Document(path).paragraphs)
    assert "互动短内容包" in text
    assert "甲公司" in text and "乙公司" in text

    result = check_docx(
        path,
        stock_names=["甲公司", "乙公司"],
        policy=policy,
        require_risk_disclaimer=False,
    )
    assert result["ok"], result["errors"]


def test_interaction_pack_publication_source_leak_still_fails(tmp_path):
    policy = load_policy("config/policy.json")
    pack = _pack()
    pack.posts[0].body = "某券商研报指出，甲公司兑现更快。"
    path = build_interaction_pack_docx(pack, tmp_path / "interaction-source-leak.docx", policy)
    result = check_docx(
        path,
        stock_names=["甲公司", "乙公司"],
        policy=policy,
        require_risk_disclaimer=False,
    )
    assert not result["ok"]
    assert any("source provenance" in error for error in result["errors"])


def test_reader_value_reference_mirrors_are_identical():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    refs = [
        root / "references/reader_value.md",
        root / "financial_writing_agent/resources/references/reader_value.md",
        root / "skills/financial-writing-agent/references/reader_value.md",
    ]
    assert refs[0].read_bytes() == refs[1].read_bytes() == refs[2].read_bytes()
