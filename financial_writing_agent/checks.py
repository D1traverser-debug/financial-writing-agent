from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

from docx import Document

from .models import ArtifactKind, TaskContract


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


def _is_bold_occurrence(doc: Document, needle: str) -> bool:
    """Return true when at least one exact occurrence is bold across every character it occupies.

    Word may split a semantic span across multiple runs. Build a character-level bold mask so
    ordinary text before/after the target does not incorrectly make a valid bold anchor fail.
    """
    if not needle:
        return False
    for paragraph in doc.paragraphs:
        full = "".join(run.text for run in paragraph.runs)
        if needle not in full:
            continue
        mask: list[bool] = []
        for run in paragraph.runs:
            mask.extend([bool(run.bold)] * len(run.text))
        start = 0
        while True:
            idx = full.find(needle, start)
            if idx < 0:
                break
            if all(mask[idx : idx + len(needle)]):
                return True
            start = idx + 1
    return False


def _all_occurrences_bold(doc: Document, needle: str) -> bool:
    """Require every exact occurrence of a company/stock name to be bold, including split runs."""
    found = False
    for paragraph in doc.paragraphs:
        full = "".join(run.text for run in paragraph.runs)
        if needle not in full:
            continue
        mask: list[bool] = []
        for run in paragraph.runs:
            mask.extend([bool(run.bold)] * len(run.text))
        start = 0
        while True:
            idx = full.find(needle, start)
            if idx < 0:
                break
            found = True
            if not all(mask[idx : idx + len(needle)]):
                return False
            start = idx + len(needle)
    return found


def check_docx(
    path: str | Path,
    *,
    stock_names: list[str],
    policy: dict,
    required_bold_anchors: list[str] | None = None,
) -> dict:
    doc = Document(path)
    errors: list[str] = []
    warnings: list[str] = []

    heading2_plus = [p.text for p in doc.paragraphs if p.style and p.style.name.startswith("Heading ") and p.style.name != "Heading 1"]
    if heading2_plus:
        errors.append(f"true Heading 2+ styles found: {heading2_plus[:5]}")

    h1s = [p.text.strip() for p in doc.paragraphs if p.style and p.style.name == "Heading 1"]
    for text in h1s:
        if text.startswith(("·", "•")):
            errors.append(f"forbidden heading hierarchy prefix: {text[:40]}")
        if not re.match(r"^[一二三四五六七八九十百]+、", text):
            errors.append(f"H1 missing Chinese sequence prefix: {text[:60]}")

    risk_idx = next((i for i, p in enumerate(doc.paragraphs) if "风险" in p.text and "免责声明" in p.text), None)
    if risk_idx is None:
        errors.append("risk/disclaimer heading not found")
    else:
        risk_body = "".join(p.text.strip() for p in doc.paragraphs[risk_idx + 1 :] if p.text.strip())
        min_chars = int(policy.get("risk_disclaimer", {}).get("min_body_chars", 0))
        if len(risk_body) < min_chars:
            errors.append(f"risk/disclaimer body too thin: {len(risk_body)} < {min_chars} chars")
        recommended_max = int(policy.get("risk_disclaimer", {}).get("recommended_max_chars", 0) or 0)
        if recommended_max and len(risk_body) > recommended_max:
            warnings.append(f"risk/disclaimer body may be verbose: {len(risk_body)} > {recommended_max} chars")

    if not policy["word"].get("allow_tables", False) and doc.tables:
        errors.append(f"publication article contains prohibited table(s): {len(doc.tables)}")

    for stock in stock_names:
        if not _all_occurrences_bold(doc, stock):
            errors.append(f"stock/company name not bold on every occurrence: {stock}")

    for anchor in required_bold_anchors or []:
        if not _is_bold_occurrence(doc, anchor):
            errors.append(f"required skim-path anchor not bold in Word: {anchor}")

    text = "\n".join(p.text for p in doc.paragraphs)
    hits = scan_finance_redlines(text, policy["finance_compliance"]["hard_fail_phrases"])
    if hits:
        errors.append(f"actionable-finance redline phrase(s): {hits}")

    extreme_hits = scan_finance_redlines(text, policy.get("style", {}).get("hard_fail_extreme_phrases", []))
    if extreme_hits:
        errors.append(f"unsupported extreme-language phrase(s): {extreme_hits}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "paragraphs": len(doc.paragraphs),
        "tables": len(doc.tables),
        "inline_images": len(doc.inline_shapes),
        "required_bold_anchors": len(required_bold_anchors or []),
    }


def load_policy(path: str | Path) -> dict:
    candidate = Path(path)
    if candidate.is_file():
        return json.loads(candidate.read_text(encoding="utf-8"))
    if candidate.name == "policy.json":
        from .resources import load_packaged_policy
        return load_packaged_policy()
    raise FileNotFoundError(candidate)
