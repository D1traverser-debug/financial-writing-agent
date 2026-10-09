import json

from docx import Document

from financial_writing_agent.checks import check_docx
from financial_writing_agent.document import ArticleDocument, Block, build_article_docx


def _risk_text() -> str:
    return (
        "本文仅用于公开信息研究与行业讨论，不构成任何投资建议或收益承诺。"
        "相关产业政策、需求、产品价格、订单兑现、竞争格局、公司业绩及市场交易情绪均可能变化，"
        "文中数据与判断存在时效性，投资者应自行核验最新公告与风险因素并独立决策。"
    )


def test_word_builder_normalizes_hierarchy_and_preserves_bold_skim_path(tmp_path):
    policy = json.loads(open("config/policy.json", encoding="utf-8").read())
    article = ArticleDocument(
        title="测试标题",
        stock_names=["国电南瑞"],
        blocks=[
            Block(kind="lead", text="这是导读，涉及国电南瑞，并且**利润开始兑现**。"),
            Block(kind="h1", text="第一部分"),
            Block(kind="h2", text="二级标题"),
            Block(kind="h3", text="三级标题"),
            Block(kind="body", text="国电南瑞在这里再次出现，**订单增长20%**。"),
            Block(kind="h1", text="风险提示与免责声明"),
            Block(kind="body", text=_risk_text()),
        ],
    )
    path = build_article_docx(article, tmp_path / "a.docx", policy)
    result = check_docx(
        path,
        stock_names=article.stock_names,
        policy=policy,
        required_bold_anchors=["利润开始兑现", "订单增长20%"],
    )
    assert result["ok"], result

    doc = Document(path)
    h1s = [p.text for p in doc.paragraphs if p.style and p.style.name == "Heading 1"]
    assert h1s[0].startswith("一、")
    assert h1s[1].startswith("二、")
    assert any(p.text.startswith("（1）") for p in doc.paragraphs)
    assert any(p.text.startswith("①") for p in doc.paragraphs)


def test_tables_are_hard_fail(tmp_path):
    policy = json.loads(open("config/policy.json", encoding="utf-8").read())
    article = ArticleDocument(
        title="无表格测试",
        blocks=[
            Block(kind="lead", text="**关键事实**。"),
            Block(kind="h1", text="正文"),
            Block(kind="body", text="正文**关键判断**。"),
            Block(kind="h1", text="风险提示与免责声明"),
            Block(kind="body", text=_risk_text()),
        ],
    )
    path = build_article_docx(article, tmp_path / "table.docx", policy)
    doc = Document(path)
    doc.add_table(rows=1, cols=2)
    doc.save(path)
    result = check_docx(path, stock_names=[], policy=policy, required_bold_anchors=["关键事实", "关键判断"])
    assert not result["ok"]
    assert any("prohibited table" in error for error in result["errors"])
