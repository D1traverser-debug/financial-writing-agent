from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from pydantic import BaseModel, Field


class Block(BaseModel):
    kind: Literal["lead", "h1", "h2", "h3", "body"]
    text: str


class ArticleDocument(BaseModel):
    title: str
    blocks: list[Block]
    stock_names: list[str] = Field(default_factory=list)


def _split_bold(text: str, stock_names: list[str]):
    parts = re.split(r"(\*\*.*?\*\*)", text)
    out: list[tuple[str, bool]] = []
    for part in parts:
        if not part:
            continue
        explicit = part.startswith("**") and part.endswith("**")
        raw = part[2:-2] if explicit else part
        if explicit:
            out.append((raw, True))
            continue
        if not stock_names:
            out.append((raw, False))
            continue
        pattern = "(" + "|".join(re.escape(x) for x in sorted(stock_names, key=len, reverse=True)) + ")"
        for token in re.split(pattern, raw):
            if token:
                out.append((token, token in stock_names))
    return out


def _set_cn_font(run, name="Microsoft YaHei"):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)


def build_article_docx(article: ArticleDocument, output: str | Path, policy: dict) -> Path:
    doc = Document()
    styles = doc.styles
    styles["Normal"].font.size = Pt(policy["word"]["body_pt"])
    styles["Normal"].font.name = "Microsoft YaHei"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run(article.title)
    r.bold = True
    r.font.size = Pt(policy["word"]["title_pt"])
    _set_cn_font(r)

    for block in article.blocks:
        if block.kind == "h1":
            p = doc.add_paragraph(style="Heading 1")
            for text, bold in _split_bold(block.text, article.stock_names):
                run = p.add_run(text)
                run.bold = True
                run.font.size = Pt(policy["word"]["h1_pt"])
                run.font.color.rgb = RGBColor.from_string(policy["word"]["h1_rgb"])
                _set_cn_font(run)
        elif block.kind in {"h2", "h3"}:
            p = doc.add_paragraph(style="Normal")
            size = policy["word"]["h2_pt"] if block.kind == "h2" else policy["word"]["h3_pt"]
            for text, _ in _split_bold(block.text, article.stock_names):
                run = p.add_run(text)
                run.bold = True
                run.font.size = Pt(size)
                _set_cn_font(run)
        else:
            p = doc.add_paragraph(style="Normal")
            for text, bold in _split_bold(block.text, article.stock_names):
                run = p.add_run(text)
                run.bold = bool(bold)
                run.font.size = Pt(policy["word"]["body_pt"])
                _set_cn_font(run)

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    return output


class AuditLine(BaseModel):
    area: str
    status: str
    evidence: str
    notes: str = ""


def build_audit_docx(title: str, lines: list[AuditLine], artifacts: list[str], output: str | Path) -> Path:
    doc = Document()
    h = doc.add_paragraph()
    r = h.add_run(title)
    r.bold = True
    r.font.size = Pt(18)
    _set_cn_font(r)

    for line in lines:
        p = doc.add_paragraph()
        r1 = p.add_run(f"[{line.status}] {line.area}：")
        r1.bold = True
        _set_cn_font(r1)
        r2 = p.add_run(line.evidence)
        _set_cn_font(r2)
        if line.notes:
            r3 = p.add_run(f"｜{line.notes}")
            _set_cn_font(r3)

    doc.add_paragraph("最终文件身份：")
    for a in artifacts:
        doc.add_paragraph(a, style="List Bullet")

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    return output
