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

    heading2_plus = [p.text for p in doc.paragraphs if p.style and p.style.name.startswith("Heading ") and p.style.name != "Heading 1"]
    if heading2_plus:
        errors.append(f"true Heading 2+ styles found: {heading2_plus[:5]}")

    h1s = [p.text.strip() for p in doc.paragraphs if p.style and p.style.name == "Heading 1"]
    for text in h1s:
        if text.startswith(("·", "•")):
            errors.append(f"forbidden heading hierarchy prefix: {text[:40]}")
        if not re.match(r"^[一二三四五六七八九十百]+、", text):
            errors.append(f"H1 missing Chinese sequence prefix: {text[:60]}")

    risk_idx = next(
        (i for i, p in enumerate(doc.paragraphs) if "风险" in p.text and "免责声明" in p.text),
        None,
    )
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
        warnings.append(f"document contains {len(doc.tables)} table(s); default policy prefers prose")

    for stock in stock_names:
        for p in doc.paragraphs:
            if stock not in p.text:
                continue
            for run in p.runs:
                if stock in run.text and not run.bold:
                    errors.append(f"stock name not bold: {stock} in paragraph '{p.text[:80]}'")
                    break

    text = "\n".join(p.text for p in doc.paragraphs)
    hits = scan_finance_redlines(text, policy["finance_compliance"]["hard_fail_phrases"])
    if hits:
        errors.append(f"actionable-finance redline phrase(s): {hits}")

    extreme_hits = scan_finance_redlines(text, policy.get("style", {}).get("hard_fail_extreme_phrases", []))
    if extreme_hits:
        errors.append(f"unsupported extreme-language phrase(s): {extreme_hits}")

    image_count = len(doc.inline_shapes)
    if expected_images is not None and image_count != expected_images:
        errors.append(f"embedded image count mismatch: actual={image_count}, expected={expected_images}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "paragraphs": len(doc.paragraphs),
        "inline_images": image_count,
    }


def load_policy(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
