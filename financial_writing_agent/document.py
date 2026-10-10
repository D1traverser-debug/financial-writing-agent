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


def _format_run(run, *, size_pt: float, bold: bool = False, italic: bool = False, color: str | None = None) -> None:
    run.bold = bold
    run.italic = italic
    run.underline = False
    run.font.size = Pt(size_pt)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    _set_cn_font(run)


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


def _is_risk_heading(text: str) -> bool:
    clean = _strip_heading_prefix(text)
    return "风险" in clean and ("免责声明" in clean or "提示" in clean)


def build_article_docx(article: ArticleDocument, output: str | Path, policy: dict) -> Path:
    doc = Document()
    styles = doc.styles
    styles["Normal"].font.size = Pt(policy["word"]["body_pt"])
    styles["Normal"].font.name = "Microsoft YaHei"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run(article.title)
    _format_run(r, bold=True, size_pt=policy["word"]["title_pt"])

    h1 = h2 = h3 = 0
    risk_mode = False
    for block in article.blocks:
        render_text = block.text

        # Risk is a final inline italic paragraph, not another numbered H1.
        if block.kind == "h1" and _is_risk_heading(block.text):
            risk_mode = True
            continue
        if block.kind in {"h1", "h2", "h3"} and risk_mode:
            risk_mode = False

        if block.kind == "h1":
            h1 += 1
            h2 = h3 = 0
            render_text = _heading_label("h1", block.text, h1, h2, h3)
            p = doc.add_paragraph(style="Heading 1")
            for text, _ in _split_bold(render_text):
                run = p.add_run(text)
                _format_run(run, bold=True, size_pt=policy["word"]["h1_pt"], color=policy["word"]["h1_rgb"])
        elif block.kind == "h2":
            h2 += 1
            h3 = 0
            render_text = _heading_label("h2", block.text, h1, h2, h3)
            p = doc.add_paragraph(style="Normal")
            for text, _ in _split_bold(render_text):
                run = p.add_run(text)
                _format_run(run, bold=True, size_pt=policy["word"]["h2_pt"])
        elif block.kind == "h3":
            h3 += 1
            render_text = _heading_label("h3", block.text, h1, h2, h3)
            p = doc.add_paragraph(style="Normal")
            for text, _ in _split_bold(render_text):
                run = p.add_run(text)
                _format_run(run, bold=True, size_pt=policy["word"]["h3_pt"])
        else:
            p = doc.add_paragraph(style="Normal")
            is_risk = risk_mode or render_text.strip().startswith("风险提示：")
            if is_risk and not render_text.strip().startswith("风险提示："):
                render_text = f"风险提示：{render_text.strip()}"
            for text, bold in _split_bold(render_text):
                run = p.add_run(text)
                _format_run(run, bold=bool(bold), italic=is_risk, size_pt=policy["word"]["body_pt"])

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
    r.underline = False
    r.font.size = Pt(18)
    _set_cn_font(r)

    for summary in summary_lines or []:
        p = doc.add_paragraph(summary)
        for run in p.runs:
            run.underline = False
            _set_cn_font(run)

    for line in lines:
        p = doc.add_paragraph()
        r1 = p.add_run(f"[{line.status}] {line.area}：")
        r1.bold = True
        r1.underline = False
        _set_cn_font(r1)
        r2 = p.add_run(line.evidence)
        r2.underline = False
        _set_cn_font(r2)
        if line.notes:
            r3 = p.add_run(f"｜{line.notes}")
            r3.underline = False
            _set_cn_font(r3)

    p = doc.add_paragraph("最终文件身份：")
    for run in p.runs:
        run.underline = False
    for a in artifacts:
        p = doc.add_paragraph(a, style="List Bullet")
        for run in p.runs:
            run.underline = False

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    return output
