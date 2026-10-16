from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

from docx import Document

from .checks import check_docx, sha256_file
from .delivery_contract import CANONICAL_DELIVERY_PATH, FORBIDDEN_VISIBLE_CHARACTERS, TEXT_SUBSTITUTIONS
from .document import ArticleDocument, Block, build_article_docx
from .models import ArtifactKind
from .resources import load_packaged_policy


DELIVERY_EVIDENCE_SCHEMA_VERSION = "1.0"


class CanonicalDeliveryError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CanonicalDeliveryError(message)


def _canonical_digest(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _word_policy(policy: Mapping[str, Any]) -> Mapping[str, Any]:
    word = policy.get("word", {})
    return word if isinstance(word, Mapping) else {}


def _text_substitutions(policy: Mapping[str, Any]) -> dict[str, str]:
    merged = dict(TEXT_SUBSTITUTIONS)
    configured = _word_policy(policy).get("text_substitutions", {})
    if isinstance(configured, Mapping):
        merged.update({str(source): str(target) for source, target in configured.items() if str(source)})
    return merged


def _forbidden_characters(policy: Mapping[str, Any]) -> tuple[str, ...]:
    values = list(FORBIDDEN_VISIBLE_CHARACTERS)
    configured = _word_policy(policy).get("forbidden_characters", [])
    if isinstance(configured, list):
        values.extend(str(item) for item in configured if str(item))
    return tuple(dict.fromkeys(values))


def normalize_delivery_text(text: str, policy: Mapping[str, Any]) -> str:
    """Apply deterministic user-owned presentation substitutions before Word construction."""
    normalized = str(text)
    for source, target in _text_substitutions(policy).items():
        normalized = normalized.replace(source, target)
    return normalized


def normalize_article_for_delivery(article: ArticleDocument, policy: Mapping[str, Any]) -> ArticleDocument:
    return ArticleDocument(
        title=normalize_delivery_text(article.title, policy),
        stock_names=list(article.stock_names),
        blocks=[
            Block(kind=block.kind, text=normalize_delivery_text(block.text, policy))
            for block in article.blocks
        ],
    )


def _docx_visible_text(path: str | Path) -> str:
    doc = Document(path)
    parts = [paragraph.text for paragraph in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.append(cell.text)
    return "\n".join(parts)


def _forbidden_character_errors(path: str | Path, policy: Mapping[str, Any]) -> list[str]:
    text = _docx_visible_text(path)
    return [
        f"forbidden delivery character present: {token!r}"
        for token in _forbidden_characters(policy)
        if token in text
    ]


def _semantic_anchor_errors(
    article: ArticleDocument,
    required_bold_anchors: list[str],
    policy: Mapping[str, Any],
    *,
    artifact_kind: ArtifactKind,
) -> list[str]:
    if artifact_kind not in {ArtifactKind.FINANCE_DEEP_DOCX, ArtifactKind.FINANCE_BROAD_DOCX}:
        return []
    style = policy.get("style", {})
    if not isinstance(style, Mapping) or not style.get("bold_skim_path_required", False):
        return []
    errors: list[str] = []
    anchors = [str(anchor).strip() for anchor in required_bold_anchors if str(anchor).strip()]
    if not anchors:
        errors.append("public long-form delivery requires explicit semantic bold anchors")
        return errors
    visible = "\n".join([article.title, *[block.text for block in article.blocks]])
    numeric_material = bool(re.search(r"\d(?:[\d,.]*)(?:%|％|亿元|万元|万亿元|美元|欧元|元|家|个|倍|年|月|日)", visible))
    if numeric_material and not any(re.search(r"\d", anchor) for anchor in anchors):
        errors.append("public long-form with material numeric facts requires at least one numeric bold anchor")
    return errors


def build_verified_article_docx(
    article: ArticleDocument,
    output: str | Path,
    *,
    artifact_kind: ArtifactKind,
    required_bold_anchors: list[str],
    policy: dict[str, Any] | None = None,
    require_risk_disclaimer: bool = True,
) -> dict[str, Any]:
    """Canonical owner-native path for a user-visible long-form/private Word build.

    The path normalizes durable presentation constraints, uses the Financial Word
    renderer, then fail-closes on deterministic Word and whole-document constraint
    checks. Ad-hoc DOCX construction cannot produce a valid canonical build receipt.
    """
    active_policy = policy or load_packaged_policy()
    normalized = normalize_article_for_delivery(article, active_policy)
    anchor_errors = _semantic_anchor_errors(
        normalized,
        required_bold_anchors,
        active_policy,
        artifact_kind=artifact_kind,
    )
    _require(not anchor_errors, f"delivery semantic-anchor admission failed: {anchor_errors}")

    path = build_article_docx(normalized, output, active_policy)
    report = check_docx(
        path,
        stock_names=list(normalized.stock_names),
        policy=active_policy,
        required_bold_anchors=list(required_bold_anchors),
        require_deep_navigation=artifact_kind == ArtifactKind.FINANCE_DEEP_DOCX,
        require_risk_disclaimer=require_risk_disclaimer,
    )
    errors = list(report.get("errors", [])) + _forbidden_character_errors(path, active_policy)
    _require(not errors, f"canonical delivery build failed: {errors}")

    return {
        "schema_version": DELIVERY_EVIDENCE_SCHEMA_VERSION,
        "canonical_delivery_path": CANONICAL_DELIVERY_PATH,
        "artifact_kind": artifact_kind.value,
        "file_name": Path(path).name,
        "sha256": sha256_file(path),
        "mechanical_qa": "PASS",
        "constraint_qa": "PASS",
        "required_bold_anchor_count": len(required_bold_anchors),
        "paragraphs": report.get("paragraphs"),
        "tables": report.get("tables"),
    }


def build_verified_private_research_docx(
    *,
    title: str,
    blocks: list[Block],
    stock_names: list[str],
    output: str | Path,
    required_bold_anchors: list[str] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Render admitted private research through the same deterministic Word surface."""
    article = ArticleDocument(title=title, blocks=blocks, stock_names=stock_names)
    return build_verified_article_docx(
        article,
        output,
        artifact_kind=ArtifactKind.PRIVATE_RESEARCH_DOCX,
        required_bold_anchors=list(required_bold_anchors or []),
        policy=policy,
        require_risk_disclaimer=False,
    )


def finalize_delivery_evidence(
    build_receipt: Mapping[str, Any],
    *,
    source_ref: str,
    source_identity: str,
    render_qa: str,
    visual_qa: str,
) -> dict[str, Any]:
    """Bind canonical build/check evidence to render and actual visual-inspection evidence."""
    _require(build_receipt.get("canonical_delivery_path") == CANONICAL_DELIVERY_PATH, "build receipt is not canonical")
    _require(build_receipt.get("mechanical_qa") == "PASS", "mechanical_qa must PASS")
    _require(build_receipt.get("constraint_qa") == "PASS", "constraint_qa must PASS")
    _require(render_qa == "PASS", "render_qa must PASS")
    _require(visual_qa == "PASS", "visual_qa must PASS")
    _require(bool(str(source_ref).strip()), "source_ref is required")
    _require(bool(str(source_identity).strip()), "source_identity is required")

    envelope = {
        "schema_version": DELIVERY_EVIDENCE_SCHEMA_VERSION,
        "canonical_delivery_path": CANONICAL_DELIVERY_PATH,
        "artifact_kind": str(build_receipt.get("artifact_kind")),
        "artifact_sha256": str(build_receipt.get("sha256", "")).lower(),
        "mechanical_qa": "PASS",
        "constraint_qa": "PASS",
        "render_qa": "PASS",
        "visual_qa": "PASS",
        "source_ref": str(source_ref),
        "source_identity": str(source_identity),
    }
    return {"delivery_evidence": envelope, "delivery_evidence_sha256": _canonical_digest(envelope)}


def validate_delivery_evidence(resource: Mapping[str, Any]) -> None:
    evidence = resource.get("delivery_evidence")
    _require(isinstance(evidence, Mapping), "delivery_evidence is required")
    expected_digest = resource.get("delivery_evidence_sha256")
    _require(isinstance(expected_digest, str) and len(expected_digest) == 64, "delivery_evidence_sha256 is required")
    _require(_canonical_digest(evidence) == expected_digest.lower(), "delivery_evidence digest mismatch")
    _require(evidence.get("canonical_delivery_path") == CANONICAL_DELIVERY_PATH, "visible artifact bypassed canonical Delivery")
    _require(evidence.get("artifact_kind") == resource.get("kind"), "delivery evidence artifact kind mismatch")
    _require(str(evidence.get("artifact_sha256", "")).lower() == str(resource.get("sha256", "")).lower(), "delivery evidence artifact hash mismatch")
    for gate in ("mechanical_qa", "constraint_qa", "render_qa", "visual_qa"):
        _require(evidence.get(gate) == "PASS", f"delivery evidence requires {gate}=PASS")
    _require(bool(str(evidence.get("source_ref", "")).strip()), "delivery evidence source_ref is required")
    _require(bool(str(evidence.get("source_identity", "")).strip()), "delivery evidence source_identity is required")
