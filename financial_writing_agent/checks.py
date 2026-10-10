from __future__ import annotations

import hashlib
import json
import math
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


def _check_run_sizes(paragraph, expected_pt: float, label: str, errors: list[str]) -> None:
    visible_runs = [run for run in paragraph.runs if run.text]
    if not visible_runs:
        return
    for run in visible_runs:
        size = run.font.size
        if size is None or not math.isclose(size.pt, expected_pt, rel_tol=0.0, abs_tol=0.01):
            actual = None if size is None else round(size.pt, 2)
            errors.append(f"{label} typography drift: expected {expected_pt}pt, got {actual}pt in {paragraph.text[:60]!r}")
            return


def _check_typography(doc: Document, policy: dict, errors: list[str]) -> None:
    word = policy.get("word", {})
    title_pt = float(word["title_pt"])
    h1_pt = float(word["h1_pt"])
    h2_pt = float(word["h2_pt"])
    h3_pt = float(word["h3_pt"])
    body_pt = float(word["body_pt"])

    nonempty = [p for p in doc.paragraphs if p.text.strip()]
    if nonempty:
        _check_run_sizes(nonempty[0], title_pt, "title", errors)

    circled = re.compile(r"^[①-⑳]")
    h2_prefix = re.compile(r"^（\d+）")
    for p in nonempty[1:]:
        if p.style and p.style.name == "Heading 1":
            _check_run_sizes(p, h1_pt, "H1", errors)
        elif h2_prefix.match(p.text.strip()):
            _check_run_sizes(p, h2_pt, "H2", errors)
        elif circled.match(p.text.strip()):
            _check_run_sizes(p, h3_pt, "H3", errors)
        else:
            _check_run_sizes(p, body_pt, "body", errors)


def check_docx(
    path: str | Path,
    *,
    stock_names: list[str],
    policy: dict,
    required_bold_anchors: list[str] | None = None,
) -> dict:
    """Run deterministic Word checks.

    `stock_names` remains in the call contract for research/QA metadata compatibility, but
    company names are no longer blanket-bold requirements. Only explicit skim anchors are
    mechanically required to be bold; entity emphasis is a semantic editorial choice.
    """
    _ = stock_names
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

    _check_typography(doc, policy, errors)

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

    for anchor in required_bold_anchors or []:
        if not _is_bold_occurrence(doc, anchor):
            errors.append(f"required skim-path anchor not bold in Word: {anchor}")

    text = "\n".join(p.text for p in doc.paragraphs)
    hits = scan_finance_redlines(text, policy["finance_compliance"]["hard_fail_phrases"])
    if hits:
        errors.append(f"actionable-finance redline phrase(s): {hits}")

    extreme_hits = scan_finance_redlines(text, policy.get("style", {}).get("hard_fail_extreme_phrases", []))
    if extreme_hits:
        errors.append(f"unsupported deterministic promotional phrase(s): {extreme_hits}")

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
