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


def _split_bold(text: str):
    """Parse only explicit **...** emphasis.

    Company names are not automatically bolded. Emphasis is a semantic skim-path
    decision owned by the draft rather than a blanket entity-formatting rule.
    """
    parts = re.split(r"(\*\*.*?\*\*)", text)
    out: list[tuple[str, bool]] = []
    for part in parts:
        if not part:
            continue
        explicit = part.startswith("**") and part.endswith("**")
        raw = part[2:-2] if explicit else part
        out.append((raw, explicit))
    return out


def _set_cn_font(run, name="Microsoft YaHei"):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)


def _chinese_number(n: int) -> str:
    digits = "零一二三四五六七八九"
    if n <= 0:
        return str(n)
    if n < 10:
        return digits[n]
    if n == 10:
        return "十"
    if n < 20:
        return "十" + digits[n - 10]
    if n < 100:
        tens, ones = divmod(n, 10)
        return digits[tens] + "十" + (digits[ones] if ones else "")
    return str(n)


def _strip_heading_prefix(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^[·•]\s*", "", text)
    text = re.sub(r"^[一二三四五六七八九十百]+、\s*", "", text)
    text = re.sub(r"^（\d+）\s*", "", text)
    text = re.sub(r"^[①-⑳]\s*", "", text)
    return text.strip()


def _heading_label(kind: str, text: str, h1: int, h2: int, h3: int) -> str:
    clean = _strip_heading_prefix(text)
    if kind == "h1":
        return f"{_chinese_number(h1)}、{clean}"
    if kind == "h2":
        return f"（{h2}）{clean}"
    if kind == "h3":
        circled = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
        prefix = circled[h3 - 1] if 1 <= h3 <= len(circled) else f"（{h3}）"
        return f"{prefix}{clean}"
    return clean


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

    h1 = h2 = h3 = 0
    for block in article.blocks:
        render_text = block.text
        if block.kind == "h1":
            h1 += 1
            h2 = h3 = 0
            render_text = _heading_label("h1", block.text, h1, h2, h3)
            p = doc.add_paragraph(style="Heading 1")
            for text, _ in _split_bold(render_text):
                run = p.add_run(text)
                run.bold = True
                run.font.size = Pt(policy["word"]["h1_pt"])
                run.font.color.rgb = RGBColor.from_string(policy["word"]["h1_rgb"])
                _set_cn_font(run)
        elif block.kind == "h2":
            h2 += 1
            h3 = 0
            render_text = _heading_label("h2", block.text, h1, h2, h3)
            p = doc.add_paragraph(style="Normal")
            for text, _ in _split_bold(render_text):
                run = p.add_run(text)
                run.bold = True
                run.font.size = Pt(policy["word"]["h2_pt"])
                _set_cn_font(run)
        elif block.kind == "h3":
            h3 += 1
            render_text = _heading_label("h3", block.text, h1, h2, h3)
            p = doc.add_paragraph(style="Normal")
            for text, _ in _split_bold(render_text):
                run = p.add_run(text)
                run.bold = True
                run.font.size = Pt(policy["word"]["h3_pt"])
                _set_cn_font(run)
        else:
            p = doc.add_paragraph(style="Normal")
            for text, bold in _split_bold(render_text):
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


def build_audit_docx(title: str, lines: list[AuditLine], artifacts: list[str], output: str | Path, summary_lines: list[str] | None = None) -> Path:
    doc = Document()
    h = doc.add_paragraph()
    r = h.add_run(title)
    r.bold = True
    r.font.size = Pt(18)
    _set_cn_font(r)

    for summary in summary_lines or []:
        p = doc.add_paragraph(summary)
        for run in p.runs:
            _set_cn_font(run)

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
