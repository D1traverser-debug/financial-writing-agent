import json

from financial_writing_agent.checks import check_docx
from financial_writing_agent.document import ArticleDocument, Block, build_article_docx


def test_word_builder_uses_only_heading1_and_bolds_stocks(tmp_path):
    policy = json.loads(open("config/policy.json", encoding="utf-8").read())
    article = ArticleDocument(
        title="测试标题",
        stock_names=["国电南瑞"],
        blocks=[
            Block(kind="lead", text="这是导读，涉及国电南瑞。"),
            Block(kind="h1", text="一、第一部分"),
            Block(kind="h2", text="（1）二级标题"),
            Block(kind="body", text="国电南瑞在这里再次出现。"),
            Block(kind="h1", text="二、风险提示与免责声明"),
            Block(kind="body", text="本文仅作信息研究，不构成任何投资建议。")
        ],
    )
    path = build_article_docx(article, tmp_path / "a.docx", policy)
    result = check_docx(path, stock_names=article.stock_names, policy=policy)
    assert result["ok"], result
