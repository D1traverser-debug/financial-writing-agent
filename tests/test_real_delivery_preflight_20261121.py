import json

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import RGBColor

from financial_writing_agent.checks import check_docx
from financial_writing_agent.document import ArticleDocument, Block, build_article_docx
from financial_writing_agent.resources import load_packaged_policy
from scripts.real_delivery_preflight import main, preflight


def make_article(tmp_path, name="test"):
    policy = load_packaged_policy()
    article = ArticleDocument(
        title="可核查的财经标题",
        stock_names=["国电南瑞"],
        blocks=[
            Block(kind="lead", text="国电南瑞**订单增长**，但需要核验。"),
            Block(kind="h1", text="成本与收入"),
            Block(kind="body", text="**利润变化**取决于实际结算。"),
            Block(kind="h1", text="风险提示与免责声明"),
            Block(kind="body", text="产业和经营情况有不确定性，本文不构成投资建议。"),
        ],
    )
    path = build_article_docx(article, tmp_path / (name + ".docx"), policy)
    return path, policy


def test_actual_word_checker_rejects_wrong_heading_color_even_when_size_is_correct(tmp_path):
    path, policy = make_article(tmp_path)
    doc = Document(path)
    h1 = next(p for p in doc.paragraphs if p.style.name == "Heading 1")
    for run in h1.runs:
        run.font.color.rgb = RGBColor(0x00, 0x00, 0xFF)
    doc.save(path)
    outcome = check_docx(path, stock_names=["国电南瑞"], policy=policy,
                         required_bold_anchors=["订单增长", "利润变化"])
    assert not outcome["ok"]
    assert any("H1 color drift" in e for e in outcome["errors"])


def test_actual_word_checker_rejects_non_bold_heading_and_non_centered_title(tmp_path):
    path, policy = make_article(tmp_path)
    doc = Document(path)
    doc.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    h1 = next(p for p in doc.paragraphs if p.style.name == "Heading 1")
    h1.runs[0].bold = False
    doc.save(path)
    outcome = check_docx(path, stock_names=["国电南瑞"], policy=policy,
                         required_bold_anchors=["订单增长", "利润变化"])
    assert any("title must be centered" in e for e in outcome["errors"])
    assert any("H1 must be bold" in e for e in outcome["errors"])


def test_actual_word_checker_rejects_disclaimer_not_at_end(tmp_path):
    path, policy = make_article(tmp_path)
    doc = Document(path)
    trailing = doc.add_paragraph()
    run = trailing.add_run("错误地在风险段落后面追加正文。")
    run.font.size = doc.paragraphs[1].runs[0].font.size
    doc.save(path)
    outcome = check_docx(path, stock_names=["国电南瑞"], policy=policy,
                         required_bold_anchors=["订单增长", "利润变化"])
    assert any("risk disclaimer must be the final visible paragraph" in e for e in outcome["errors"])


def test_preflight_fails_on_missing_product_and_missing_evidence(tmp_path):
    path, _ = make_article(tmp_path)
    m = {
        "task_id": "new-topic",
        "required_outputs": ["FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX", "AUDIT_DOCX"],
        "artifacts": {"FINANCE_DEEP_DOCX": str(path)},
    }
    report = preflight(m, manifest_dir=tmp_path)
    assert report["mechanical_status"] == "FAIL"
    assert "REQUIRED_ARTIFACT_SET_MISMATCH" in report["errors"]
    assert "FINANCE_DEEP_DOCX:ARTICLE_EVIDENCE_METADATA_REQUIRED" in report["errors"]


def test_preflight_positive_is_only_mechanical_not_editorial_or_owner_certification(tmp_path, capsys):
    deep, _ = make_article(tmp_path, "deep")
    broad, _ = make_article(tmp_path, "broad")
    interaction = tmp_path / "interaction.docx"
    audit = tmp_path / "audit.docx"
    Document().save(interaction)
    doc = Document()
    doc.add_paragraph("互动内容，经审阅的材料。")
    doc.save(interaction)
    doc = Document()
    doc.add_paragraph("研究底稿，来源追溯。")
    doc.save(audit)
    m = {
        "task_id": "new-topic",
        "required_outputs": ["FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX", "PLATFORM_INTERACTION_PACK_DOCX", "AUDIT_DOCX"],
        "artifacts": {
            "FINANCE_DEEP_DOCX": str(deep), "FINANCE_BROAD_DOCX": str(broad),
            "PLATFORM_INTERACTION_PACK_DOCX": str(interaction), "AUDIT_DOCX": str(audit),
        },
        "article_evidence": {
            k: {"stock_names": ["国电南瑞"], "required_bold_anchors": ["订单增长", "利润变化"]}
            for k in ("FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX")
        },
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    assert main(["--manifest", str(path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["mechanical_status"] == "PASS"
    assert result["publication_certification"] == "OPEN"
    assert result["company_universe_completeness"] == "NOT_VERIFIED_BY_THIS_GATE"
    assert result["financial_fact_entailment"] == "NOT_VERIFIED_BY_THIS_GATE"
