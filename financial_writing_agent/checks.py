from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

from .models import ArtifactKind, TaskContract


CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def expected_artifact_kinds(contract: TaskContract) -> set[ArtifactKind]:
    return set(contract.required_outputs)


def check_required_outputs(contract: TaskContract, artifacts: dict[ArtifactKind, str]) -> list[str]:
    errors: list[str] = []
    for kind in expected_artifact_kinds(contract):
        path = artifacts.get(kind)
        if not path:
            errors.append(f"missing artifact mapping: {kind}")
        elif not Path(path).is_file():
            errors.append(f"artifact does not exist: {kind} -> {path}")
    return errors


def scan_finance_redlines(text: str, phrases: Iterable[str]) -> list[str]:
    return sorted({p for p in phrases if p in text})


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


def _has_graphic(paragraph) -> bool:
    return bool(paragraph._p.xpath(".//w:drawing | .//w:pict"))


def _all_visible_runs_bold(paragraph) -> bool:
    visible = [run for run in paragraph.runs if run.text]
    return bool(visible) and all(run.bold is True for run in visible)


def _all_visible_runs_size(paragraph, expected_pt: float) -> bool:
    visible = [run for run in paragraph.runs if run.text]
    if not visible:
        return False
    for run in visible:
        if run.font.size is None or abs(run.font.size.pt - expected_pt) > 0.2:
            return False
    return True


def _all_visible_runs_rgb(paragraph, expected_rgb: str) -> bool:
    visible = [run for run in paragraph.runs if run.text]
    if not visible:
        return False
    expected = expected_rgb.upper()
    return all(run.font.color.rgb is not None and str(run.font.color.rgb).upper() == expected for run in visible)


def _occurrence_is_bold(paragraph, token: str) -> bool:
    text = "".join(run.text for run in paragraph.runs)
    if token not in text:
        return True
    bold_mask: list[bool] = []
    for run in paragraph.runs:
        bold_mask.extend([run.bold is True] * len(run.text))
    start = 0
    while True:
        index = text.find(token, start)
        if index < 0:
            break
        if not all(bold_mask[index : index + len(token)]):
            return False
        start = index + len(token)
    return True


def check_docx(
    path: str | Path,
    *,
    stock_names: list[str],
    policy: dict,
    expected_images: int | None = None,
) -> dict:
    doc = Document(path)
    errors: list[str] = []
    warnings: list[str] = []

    word_policy = policy["word"]
    h1_pt = float(word_policy["h1_pt"])
    h2_pt = float(word_policy["h2_pt"])
    h3_pt = float(word_policy["h3_pt"])
    h1_rgb = str(word_policy["h1_rgb"])

    if not doc.paragraphs:
        errors.append("document has no paragraphs")
    else:
        title_paragraph = doc.paragraphs[0]
        expected_alignment = str(word_policy.get("title_alignment", "left")).lower()
        if expected_alignment == "left" and title_paragraph.alignment != WD_ALIGN_PARAGRAPH.LEFT:
            errors.append("article title must be left-aligned")

    heading2_plus = [
        p.text for p in doc.paragraphs
        if p.style and p.style.name.startswith("Heading ") and p.style.name != "Heading 1"
    ]
    if heading2_plus:
        errors.append(f"true Heading 2+ styles found: {heading2_plus[:5]}")

    h1_paragraphs = [p for p in doc.paragraphs if p.style and p.style.name == "Heading 1"]
    h1_texts = [p.text.strip() for p in h1_paragraphs]
    if len(h1_texts) != len(set(h1_texts)):
        errors.append("duplicate H1 heading text found")

    for index, paragraph in enumerate(h1_paragraphs, start=1):
        text = paragraph.text.strip()
        expected_prefix = f"{_chinese_number(index)}、"
        if text.startswith(("·", "•")):
            errors.append(f"forbidden heading hierarchy prefix: {text[:40]}")
        if not text.startswith(expected_prefix):
            errors.append(f"H1 sequence mismatch: expected '{expected_prefix}', got '{text[:60]}'")
        if not _all_visible_runs_bold(paragraph):
            errors.append(f"H1 not fully bold: {text[:60]}")
        if not _all_visible_runs_rgb(paragraph, h1_rgb):
            errors.append(f"H1 color mismatch: {text[:60]}")
        if not _all_visible_runs_size(paragraph, h1_pt):
            errors.append(f"H1 size mismatch: {text[:60]}")

    current_h2 = 0
    current_h3 = 0
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if paragraph.style and paragraph.style.name == "Heading 1":
            current_h2 = 0
            current_h3 = 0
            continue
        h2_match = re.match(r"^（(\d+)）", text)
        if h2_match:
            current_h2 += 1
            current_h3 = 0
            actual = int(h2_match.group(1))
            if actual != current_h2:
                errors.append(f"H2 sequence mismatch: expected （{current_h2}）, got {text[:60]}")
            if not paragraph.style or paragraph.style.name != "Normal":
                errors.append(f"H2 must use Normal style: {text[:60]}")
            if not _all_visible_runs_bold(paragraph):
                errors.append(f"H2 not fully bold: {text[:60]}")
            if not _all_visible_runs_size(paragraph, h2_pt):
                errors.append(f"H2 size mismatch: {text[:60]}")
            continue
        if text and text[0] in CIRCLED:
            current_h3 += 1
            expected = CIRCLED[current_h3 - 1] if current_h3 <= len(CIRCLED) else None
            if expected is not None and not text.startswith(expected):
                errors.append(f"H3 sequence mismatch: expected {expected}, got {text[:60]}")
            if current_h2 == 0:
                errors.append(f"H3 appears before any H2 in current H1: {text[:60]}")
            if not paragraph.style or paragraph.style.name != "Normal":
                errors.append(f"H3 must use Normal style: {text[:60]}")
            if not _all_visible_runs_bold(paragraph):
                errors.append(f"H3 not fully bold: {text[:60]}")
            if not _all_visible_runs_size(paragraph, h3_pt):
                errors.append(f"H3 size mismatch: {text[:60]}")

    empty_paragraphs: list[int] = []
    underlined: list[str] = []
    for index, paragraph in enumerate(doc.paragraphs, start=1):
        if not paragraph.text.strip() and not _has_graphic(paragraph):
            empty_paragraphs.append(index)
        for run in paragraph.runs:
            if run.underline is True:
                underlined.append(paragraph.text[:60])
                break
    if empty_paragraphs:
        errors.append(f"empty paragraph(s) found: {empty_paragraphs[:10]}")
    if underlined:
        errors.append(f"underlined text found: {underlined[:5]}")

    risk_idx = next(
        (i for i, p in enumerate(doc.paragraphs) if "风险" in p.text and "免责声明" in p.text),
        None,
    )
    article_content_chars = 0
    if risk_idx is None:
        errors.append("risk/disclaimer heading not found")
        article_content_chars = sum(len(p.text.strip()) for p in doc.paragraphs[1:] if p.text.strip())
    else:
        risk_heading = doc.paragraphs[risk_idx]
        if not risk_heading.style or risk_heading.style.name != "Heading 1":
            errors.append("risk/disclaimer heading must be Heading 1")
        risk_body = "".join(p.text.strip() for p in doc.paragraphs[risk_idx + 1 :] if p.text.strip())
        min_chars = int(policy.get("risk_disclaimer", {}).get("min_body_chars", 0))
        if len(risk_body) < min_chars:
            errors.append(f"risk/disclaimer body too thin: {len(risk_body)} < {min_chars} chars")
        recommended_max = int(policy.get("risk_disclaimer", {}).get("recommended_max_chars", 0) or 0)
        hard_max = int(policy.get("risk_disclaimer", {}).get("hard_max_chars", 0) or 0)
        if hard_max and len(risk_body) > hard_max:
            errors.append(f"risk/disclaimer body too verbose: {len(risk_body)} > {hard_max} chars")
        elif recommended_max and len(risk_body) > recommended_max:
            warnings.append(f"risk/disclaimer body may be verbose: {len(risk_body)} > {recommended_max} chars")
        article_content_chars = sum(
            len(p.text.strip())
            for p in doc.paragraphs[1:risk_idx]
            if p.text.strip()
        )

    filename = Path(path).name.upper()
    editorial_policy = policy.get("editorial", {})
    if "FINANCE_BROAD" in filename:
        preferred_max = int(editorial_policy.get("finance_broad_preferred_max_chars", 0) or 0)
        hard_max = int(editorial_policy.get("finance_broad_hard_max_chars", 0) or 0)
        if hard_max and article_content_chars > hard_max:
            errors.append(
                f"FINANCE_BROAD exceeds default completion-oriented hard cap: {article_content_chars} > {hard_max} chars"
            )
        elif preferred_max and article_content_chars > preferred_max:
            warnings.append(
                f"FINANCE_BROAD exceeds preferred distribution range: {article_content_chars} > {preferred_max} chars"
            )
    elif "FINANCE_DEEP" in filename:
        density_review = int(editorial_policy.get("finance_deep_density_review_chars", 0) or 0)
        hard_max = int(editorial_policy.get("finance_deep_max_chars", 0) or 0)
        if hard_max and article_content_chars > hard_max:
            errors.append(f"FINANCE_DEEP exceeds hard editorial ceiling: {article_content_chars} > {hard_max} chars")
        elif density_review and article_content_chars > density_review:
            warnings.append(
                f"FINANCE_DEEP exceeds density-review threshold: {article_content_chars} > {density_review} chars; verify that every retained section changes the judgment"
            )

    if not word_policy.get("allow_tables", False) and doc.tables:
        warnings.append(f"document contains {len(doc.tables)} table(s); default policy prefers prose")

    for stock in sorted(set(stock_names), key=len, reverse=True):
        for paragraph in doc.paragraphs:
            if stock in paragraph.text and not _occurrence_is_bold(paragraph, stock):
                errors.append(f"stock name not fully bold across runs: {stock} in paragraph '{paragraph.text[:80]}'")

    text = "\n".join(p.text for p in doc.paragraphs)
    markdown_hits = sorted(set(re.findall(r"\*\*|__", text)))
    if markdown_hits:
        errors.append(f"Markdown bold marker(s) leaked into Word: {markdown_hits}")

    hits = scan_finance_redlines(text, policy["finance_compliance"]["hard_fail_phrases"])
    if hits:
        errors.append(f"actionable-finance redline phrase(s): {hits}")

    extreme_hits = scan_finance_redlines(text, policy.get("style", {}).get("hard_fail_extreme_phrases", []))
    if extreme_hits:
        errors.append(f"unsupported extreme-language phrase(s): {extreme_hits}")

    non_heading_text_paragraphs = [
        p for p in doc.paragraphs
        if p.text.strip() and not (p.style and p.style.name == "Heading 1")
        and not re.match(r"^（\d+）", p.text.strip())
        and not (p.text.strip() and p.text.strip()[0] in CIRCLED)
    ]
    body_with_bold = sum(any(run.bold is True and run.text.strip() for run in p.runs) for p in non_heading_text_paragraphs)
    if non_heading_text_paragraphs and body_with_bold == 0:
        warnings.append("no body-level bold anchors detected; semantic bold-skeleton audit still required")

    image_count = len(doc.inline_shapes)
    if expected_images is not None and image_count != expected_images:
        errors.append(f"embedded image count mismatch: actual={image_count}, expected={expected_images}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "paragraphs": len(doc.paragraphs),
        "h1_count": len(h1_paragraphs),
        "empty_paragraphs": empty_paragraphs,
        "body_bold_anchor_paragraphs": body_with_bold,
        "article_content_chars": article_content_chars,
        "inline_images": image_count,
    }


def load_policy(path: str | Path) -> dict:
    candidate = Path(path)
    if candidate.is_file():
        return json.loads(candidate.read_text(encoding="utf-8"))
    if candidate.name == "policy.json":
        from .resources import load_packaged_policy
        return load_packaged_policy()
    raise FileNotFoundError(candidate)
