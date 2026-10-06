import binascii
import json
import struct
import zlib

from docx import Document

from financial_writing_agent.checks import check_docx
from financial_writing_agent.document import ArticleDocument, Block, DocumentImage, build_article_docx


def _write_test_png(path, width=160, height=90):
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
        )

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    row = b"\x00" + (b"\x30\x80\xC0" * width)
    raw = row * height
    path.write_bytes(signature + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def _risk_text() -> str:
    return (
        "本文仅用于公开信息研究与行业讨论，不构成任何投资建议或收益承诺。"
        "相关产业政策、需求、产品价格、订单兑现、竞争格局、公司业绩及市场交易情绪均可能变化，"
        "文中数据与判断存在时效性，投资者应自行核验最新公告与风险因素并独立决策。"
    )


def test_word_builder_normalizes_hierarchy_bolds_stocks_and_checks_risk(tmp_path):
    policy = json.loads(open("config/policy.json", encoding="utf-8").read())
    article = ArticleDocument(
        title="测试标题",
        stock_names=["国电南瑞"],
        blocks=[
            Block(kind="lead", text="这是导读，涉及国电南瑞。"),
            Block(kind="h1", text="第一部分"),
            Block(kind="h2", text="二级标题"),
            Block(kind="h3", text="三级标题"),
            Block(kind="body", text="国电南瑞在这里再次出现。"),
            Block(kind="h1", text="风险提示与免责声明"),
            Block(kind="body", text=_risk_text()),
        ],
    )
    path = build_article_docx(article, tmp_path / "a.docx", policy)
    result = check_docx(path, stock_names=article.stock_names, policy=policy, expected_images=0)
    assert result["ok"], result

    doc = Document(path)
    h1s = [p.text for p in doc.paragraphs if p.style and p.style.name == "Heading 1"]
    assert h1s[0].startswith("一、")
    assert h1s[1].startswith("二、")
    assert any(p.text.startswith("（1）") for p in doc.paragraphs)
    assert any(p.text.startswith("①") for p in doc.paragraphs)


def test_word_builder_inserts_centered_uncropped_images_at_anchors(tmp_path):
    policy = json.loads(open("config/policy.json", encoding="utf-8").read())
    image_path = tmp_path / "cover.png"
    _write_test_png(image_path)
    article = ArticleDocument(
        title="带图测试",
        blocks=[
            Block(kind="lead", text="导读。"),
            Block(kind="h1", text="正文"),
            Block(kind="body", text="正文段落。"),
            Block(kind="h1", text="风险提示与免责声明"),
            Block(kind="body", text=_risk_text()),
        ],
    )
    images = [
        DocumentImage(local_path=str(image_path), role="hero"),
        DocumentImage(local_path=str(image_path), role="section", anchor_after_block=2),
    ]
    path = build_article_docx(article, tmp_path / "visual.docx", policy, images=images)
    result = check_docx(path, stock_names=[], policy=policy, expected_images=2)
    assert result["ok"], result
    assert result["inline_images"] == 2
