from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
import struct
from pathlib import Path
from typing import Any, Callable, Mapping

from docx import Document

from .checks import check_docx, sha256_file
from .delivery_contract import CANONICAL_DELIVERY_PATH, FORBIDDEN_VISIBLE_CHARACTERS, TEXT_SUBSTITUTIONS
from .document import (
    ArticleDocument,
    AuditLine,
    Block,
    build_article_docx,
    build_audit_docx,
    build_interaction_pack_docx,
)
from .models import ArtifactKind
from .path_identity import require_article_path, require_word_basename
from .private_research import validate_private_research_brief
from .resources import load_packaged_policy


DELIVERY_EVIDENCE_SCHEMA_VERSION = "1.1"
BUILDER_RECEIPT_VERSION = "1.0"
RENDER_INSPECTION_RECEIPT_VERSION = "1.0"
# Process-local issuer key: visible delivery is intentionally current-session only.
# This is provenance/anti-bypass assurance, not a cryptographic trust boundary against
# a malicious caller with arbitrary in-process Python introspection.
_SESSION_ISSUER_KEY = secrets.token_bytes(32)


class CanonicalDeliveryError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CanonicalDeliveryError(message)


def _require_docx_output(output: str | Path) -> None:
    try:
        require_word_basename(Path(output).name)
    except ValueError as exc:
        raise CanonicalDeliveryError("Word output must be a canonical .docx file name") from exc


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _canonical_digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _issuer_sign(value: Mapping[str, Any]) -> str:
    return hmac.new(_SESSION_ISSUER_KEY, _canonical_json(value), hashlib.sha256).hexdigest()


def _issue_build_receipt(payload: Mapping[str, Any]) -> dict[str, Any]:
    body = {"builder_receipt_version": BUILDER_RECEIPT_VERSION, **dict(payload)}
    return {**body, "builder_attestation": _issuer_sign(body)}


def _verify_build_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    _require(receipt.get("builder_receipt_version") == BUILDER_RECEIPT_VERSION, "build receipt version is not canonical")
    signature = str(receipt.get("builder_attestation", ""))
    _require(len(signature) == 64, "build receipt lacks builder attestation")
    body = {key: value for key, value in receipt.items() if key != "builder_attestation"}
    _require(hmac.compare_digest(signature, _issuer_sign(body)), "build receipt was not issued by the current canonical builder session")
    return body


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
    # Company names must be normalized by the same visible-text transform as article
    # prose; otherwise auto-bold/style checks can silently search for stale names.
    return ArticleDocument(
        title=normalize_delivery_text(article.title, policy),
        stock_names=[normalize_delivery_text(name, policy) for name in article.stock_names],
        blocks=[Block(kind=block.kind, text=normalize_delivery_text(block.text, policy)) for block in article.blocks],
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
    return [f"forbidden delivery character present: {token!r}" for token in _forbidden_characters(policy) if token in text]


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


def _generic_build_receipt(
    path: str | Path,
    *,
    artifact_kind: ArtifactKind,
    policy: Mapping[str, Any],
    source_quality_evidence_sha256: str | None = None,
) -> dict[str, Any]:
    # Opening the document is a minimal structural smoke check for non-article output
    # types; product-specific semantic QA remains upstream of Delivery.
    _docx_visible_text(path)
    errors = _forbidden_character_errors(path, policy)
    _require(not errors, f"canonical delivery build failed: {errors}")
    payload: dict[str, Any] = {
        "schema_version": DELIVERY_EVIDENCE_SCHEMA_VERSION,
        "canonical_delivery_path": CANONICAL_DELIVERY_PATH,
        "artifact_kind": artifact_kind.value,
        "file_name": Path(path).name,
        "sha256": sha256_file(path),
        "mechanical_qa": "PASS",
        "constraint_qa": "PASS",
    }
    if source_quality_evidence_sha256 is not None:
        payload["source_quality_evidence_sha256"] = source_quality_evidence_sha256
    return _issue_build_receipt(payload)


def build_verified_article_docx(
    article: ArticleDocument,
    output: str | Path,
    *,
    artifact_kind: ArtifactKind,
    required_bold_anchors: list[str],
    policy: dict[str, Any] | None = None,
    require_risk_disclaimer: bool = True,
    source_quality_evidence_sha256: str | None = None,
    task_state: Mapping[str, Any] | None = None,
    research: Any | None = None,
    claim_bindings: list[Mapping[str, Any]] | None = None,
    source_reader: Callable[[str], Mapping[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Build mechanically checked Word; optional state makes task-specific rules binding.

    Without task_state this receipt certifies *only* deterministic Word checks,
    never that the owner's article requirements or facts were verified.
    """
    _require_docx_output(output)
    active_policy = policy or load_packaged_policy()
    normalized = normalize_article_for_delivery(article, active_policy)
    anchor_errors = _semantic_anchor_errors(normalized, required_bold_anchors, active_policy, artifact_kind=artifact_kind)
    _require(not anchor_errors, f"delivery semantic-anchor admission failed: {anchor_errors}")

    task_scope_binding = None
    claim_trace_binding = None
    if task_state is None:
        _require(research is None, "research without task_state cannot certify publication scope")
        _require(claim_bindings is None and source_reader is None, "source trace without task state cannot certify current factual scope")
    else:
        from .task_publication import TaskPublicationError, verify_task_publication_scope

        mode = artifact_kind.value.removesuffix("_DOCX")
        _require(mode in {"FINANCE_DEEP", "FINANCE_BROAD"}, "task-bound article builder requires Deep or Broad mode")
        try:
            task_scope_binding = verify_task_publication_scope(
                task_state, normalized, research, product_mode=mode,
            )
        except ValueError as exc:
            raise CanonicalDeliveryError(f"current task publication scope failed: {exc}") from exc
        draft_ref = task_state.get("stage_artifacts", {}).get("DRAFT")
        _require(isinstance(draft_ref, Mapping), "CURRENT_TASK_DRAFT_ARTIFACT_REQUIRED")
        draft_path = draft_ref.get("path")
        draft_blob_sha = draft_ref.get("blob_sha")
        try:
            canonical_draft_path = require_article_path(draft_path, str(task_state["task_id"]))
        except (KeyError, ValueError) as exc:
            raise CanonicalDeliveryError("CURRENT_TASK_DRAFT_ARTIFACT_PATH_INVALID") from exc
        _require(
            isinstance(draft_blob_sha, str) and re.fullmatch(r"[a-f0-9]{40}", draft_blob_sha) is not None,
            "CURRENT_TASK_DRAFT_ARTIFACT_BLOB_SHA_INVALID",
        )
        task_scope_binding = {
            **dict(task_scope_binding),
            "draft_artifact_path": canonical_draft_path,
            "draft_artifact_blob_sha": draft_blob_sha,
        }
        if claim_bindings is not None:
            from .claim_trace import verify_publication_source_trace

            try:
                claim_trace_binding = verify_publication_source_trace(
                    normalized, claim_bindings, source_reader=source_reader,
                    article_task_id=str(task_state["task_id"]),
                )
            except ValueError as exc:
                raise CanonicalDeliveryError(f"current source-to-paragraph trace failed: {exc}") from exc

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

    payload: dict[str, Any] = {
        "schema_version": DELIVERY_EVIDENCE_SCHEMA_VERSION,
        "canonical_delivery_path": CANONICAL_DELIVERY_PATH,
        "artifact_kind": artifact_kind.value,
        "file_name": Path(path).name,
        "sha256": sha256_file(path),
        "mechanical_qa": "PASS",
        "constraint_qa": "PASS",
        "required_bold_anchor_count": len(required_bold_anchors),
        "task_scope_assurance": "STRUCTURAL_TASK_SCOPE_ONLY" if task_scope_binding is not None else "NOT_CHECKED",
        "source_trace_assurance": (
            claim_trace_binding["assurance"] if claim_trace_binding is not None else "NOT_CHECKED"
        ),
        "paragraphs": report.get("paragraphs"),
        "tables": report.get("tables"),
    }
    if source_quality_evidence_sha256 is not None:
        payload["source_quality_evidence_sha256"] = source_quality_evidence_sha256
    if task_scope_binding is not None:
        payload["task_scope_binding"] = task_scope_binding
    if claim_trace_binding is not None:
        payload["claim_trace_binding"] = claim_trace_binding
    return _issue_build_receipt(payload)


def build_verified_private_research_docx(
    *,
    title: str,
    blocks: list[Block],
    stock_names: list[str],
    output: str | Path,
    admitted_private_research_brief: Mapping[str, Any],
    required_bold_anchors: list[str] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Render only an admitted PrivateResearchBrief through canonical Delivery."""
    admitted = validate_private_research_brief(admitted_private_research_brief)
    article = ArticleDocument(title=title, blocks=blocks, stock_names=stock_names)
    return build_verified_article_docx(
        article,
        output,
        artifact_kind=ArtifactKind.PRIVATE_RESEARCH_DOCX,
        required_bold_anchors=list(required_bold_anchors or []),
        policy=policy,
        require_risk_disclaimer=False,
        source_quality_evidence_sha256=hashlib.sha256(
            json.dumps(admitted, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    )


def build_verified_audit_docx(
    *,
    title: str,
    lines: list[AuditLine],
    artifacts: list[str],
    output: str | Path,
    summary_lines: list[str] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _require_docx_output(output)
    active_policy = policy or load_packaged_policy()
    path = build_audit_docx(title, lines, artifacts, output, summary_lines=summary_lines)
    return _generic_build_receipt(path, artifact_kind=ArtifactKind.AUDIT_DOCX, policy=active_policy)


def build_verified_interaction_pack_docx(
    pack: Any,
    output: str | Path,
    *,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _require_docx_output(output)
    active_policy = policy or load_packaged_policy()
    path = build_interaction_pack_docx(pack, output, active_policy)
    return _generic_build_receipt(path, artifact_kind=ArtifactKind.PLATFORM_INTERACTION_PACK_DOCX, policy=active_policy)


def render_word_and_review_pages(
    build_receipt: Mapping[str, Any],
    *,
    docx_path: str | Path,
    render_dir: str | Path,
    visual_reviewer: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None,
) -> dict[str, Any]:
    """Actually render the exact issued Word bytes and inspect each produced page.

    The verifier is an externally supplied reviewer: this receipt proves a
    reviewer callback saw exact page PNG bytes; it does NOT certify that the
    reviewer is independent or that the report's editorial facts are correct.
    If no reviewer is supplied, no current-task render/visual PASS is issued.
    """
    from .rendering import render_docx_pages

    _verify_build_receipt(build_receipt)
    _require(visual_reviewer is not None, "CURRENT_WORD_VISUAL_REVIEWER_REQUIRED")
    path = Path(docx_path)
    _require(path.is_file(), "CURRENT_WORD_BINARY_NOT_FOUND")
    _require(path.name == build_receipt.get("file_name"), "CURRENT_WORD_FILE_NAME_MISMATCH")
    binary = path.read_bytes()
    actual_sha = hashlib.sha256(binary).hexdigest()
    _require(actual_sha == build_receipt.get("sha256"), "CURRENT_WORD_BINARY_HASH_MISMATCH")
    try:
        pages = render_docx_pages(path, render_dir)
    except Exception as exc:
        raise CanonicalDeliveryError("CURRENT_WORD_RENDER_EXECUTION_FAILED") from exc
    _require(isinstance(pages, list) and bool(pages), "CURRENT_WORD_RENDER_HAS_NO_PAGES")
    pdf_path = Path(render_dir).resolve() / f"{path.stem}.pdf"
    _require(pdf_path.is_file() and pdf_path.stat().st_size > 0, "CURRENT_WORD_RENDER_PDF_MISSING")
    rendered: list[dict[str, Any]] = []
    for index, page_path in enumerate(pages, start=1):
        png = Path(page_path).read_bytes()
        _require(
            len(png) >= 24 and png[:8] == b"\x89PNG\r\n\x1a\n" and png[12:16] == b"IHDR",
            f"CURRENT_WORD_PAGE_{index}_NOT_PNG",
        )
        width, height = struct.unpack(">II", png[16:24])
        _require(0 < width <= 30000 and 0 < height <= 30000, f"CURRENT_WORD_PAGE_{index}_INVALID_DIMENSIONS")
        page_sha = hashlib.sha256(png).hexdigest()
        try:
            result = visual_reviewer({
                "page_index": index, "page_count": len(pages),
                "artifact_sha256": actual_sha, "page_png_bytes": png,
                "page_sha256": page_sha, "width": width, "height": height,
            })
        except Exception as exc:
            raise CanonicalDeliveryError(f"CURRENT_WORD_PAGE_{index}_VISUAL_REVIEW_FAILED") from exc
        _require(
            isinstance(result, Mapping) and result.get("status") == "PASS"
            and isinstance(result.get("review_ref"), str) and bool(result["review_ref"].strip()),
            f"CURRENT_WORD_PAGE_{index}_VISUAL_REVIEW_NOT_ACCEPTED",
        )
        rendered.append({
            "page_index": index, "page_sha256": page_sha,
            "pixel_width": width, "pixel_height": height,
            "review_status": "PASS", "review_ref": result["review_ref"],
        })
    body = {
        "render_receipt_version": RENDER_INSPECTION_RECEIPT_VERSION,
        "artifact_sha256": actual_sha,
        "rendered_pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        "rendered_page_count": len(rendered),
        "pages": rendered,
        "review_assurance": "CALLER_SUPPLIED_REVIEW__INDEPENDENCE_NOT_ESTABLISHED",
    }
    return {**body, "session_attestation": _issuer_sign(body)}


def _verify_render_inspection_receipt(raw: Any, expected_artifact_sha256: Any) -> dict[str, Any]:
    _require(isinstance(raw, Mapping), "CURRENT_WORD_RENDER_RECEIPT_REQUIRED")
    _require(raw.get("render_receipt_version") == RENDER_INSPECTION_RECEIPT_VERSION,
             "CURRENT_WORD_RENDER_RECEIPT_VERSION_INVALID")
    signature = raw.get("session_attestation")
    _require(isinstance(signature, str) and len(signature) == 64,
             "CURRENT_WORD_RENDER_RECEIPT_UNSIGNED")
    body = {k: v for k, v in raw.items() if k != "session_attestation"}
    _require(hmac.compare_digest(signature, _issuer_sign(body)),
             "CURRENT_WORD_RENDER_RECEIPT_NOT_ISSUED_THIS_SESSION")
    _require(raw.get("artifact_sha256") == expected_artifact_sha256,
             "CURRENT_WORD_RENDER_ARTIFACT_HASH_MISMATCH")
    count, pages = raw.get("rendered_page_count"), raw.get("pages")
    _require(type(count) is int and count > 0 and isinstance(pages, list) and len(pages) == count,
             "CURRENT_WORD_RENDER_PAGE_COUNT_INVALID")
    _require([item.get("page_index") for item in pages if isinstance(item, Mapping)] == list(range(1, count + 1)),
             "CURRENT_WORD_RENDER_PAGE_SEQUENCE_INVALID")
    _require(all(
        isinstance(item, Mapping) and item.get("review_status") == "PASS"
        and isinstance(item.get("review_ref"), str) and bool(item["review_ref"].strip())
        and isinstance(item.get("page_sha256"), str) and len(item["page_sha256"]) == 64
        for item in pages
    ), "CURRENT_WORD_RENDER_PAGE_INSPECTION_INVALID")
    return dict(raw)


def finalize_delivery_evidence(
    build_receipt: Mapping[str, Any],
    *,
    source_ref: str,
    source_identity: str,
    render_qa: str,
    visual_qa: str,
    render_inspection_receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Bind an issuer-attested canonical build to current render/visual evidence."""
    unsigned_receipt = _verify_build_receipt(build_receipt)
    _require(build_receipt.get("canonical_delivery_path") == CANONICAL_DELIVERY_PATH, "build receipt is not canonical")
    _require(build_receipt.get("mechanical_qa") == "PASS", "mechanical_qa must PASS")
    _require(build_receipt.get("constraint_qa") == "PASS", "constraint_qa must PASS")
    _require(render_qa == "PASS", "render_qa must PASS")
    _require(visual_qa == "PASS", "visual_qa must PASS")
    _require(bool(str(source_ref).strip()), "source_ref is required")
    _require(bool(str(source_identity).strip()), "source_identity is required")
    binding = build_receipt.get("task_scope_binding")
    artifact_kind = str(build_receipt.get("artifact_kind", ""))
    if artifact_kind in {"FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"}:
        _require(isinstance(binding, Mapping), "CURRENT_WORD_TASK_SCOPE_BINDING_REQUIRED")
        _require(
            binding.get("mode") == artifact_kind.removesuffix("_DOCX"),
            "CURRENT_WORD_TASK_SCOPE_MODE_MISMATCH",
        )
        _require(
            isinstance(binding.get("draft_artifact_path"), str)
            and isinstance(binding.get("draft_artifact_blob_sha"), str)
            and re.fullmatch(r"[a-f0-9]{40}", str(binding.get("draft_artifact_blob_sha"))) is not None,
            "CURRENT_WORD_TASK_DRAFT_BINDING_REQUIRED",
        )
        _require(
            source_ref == binding.get("draft_artifact_path")
            and source_identity == f"git-blob:{binding.get('draft_artifact_blob_sha')}",
            "CURRENT_WORD_TASK_DRAFT_IDENTITY_MISMATCH",
        )
    # Every visible Word artifact, including generic audit/interaction outputs,
    # must have an actual current-session render/page receipt. PASS strings alone
    # cannot stand in for rendering the exact DOCX bytes.
    verified_render_inspection = _verify_render_inspection_receipt(
        render_inspection_receipt, build_receipt.get("sha256"),
    )
    if binding is not None:
        _require(isinstance(binding, Mapping), "task scope binding must be structured")
        _require(
            binding.get("observed_stage") in {"DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT"},
            "task-bound visible delivery needs admitted editorial audit and DELIVERY stage",
        )
        try:
            require_article_path(source_ref, binding.get("task_id"))
        except ValueError as exc:
            raise CanonicalDeliveryError("task-bound source_ref escapes the current article workspace") from exc
        from .claim_trace import SOURCE_TRACE_ASSURANCE

        traced = build_receipt.get("claim_trace_binding")
        _require(isinstance(traced, Mapping), "CURRENT_WORD_SOURCE_TRACE_REQUIRED")
        _require(traced.get("task_id") == binding.get("task_id"), "CURRENT_WORD_SOURCE_TRACE_TASK_MISMATCH")
        _require(traced.get("assurance") == SOURCE_TRACE_ASSURANCE,
                 "CURRENT_WORD_SOURCE_TRACE_ASSURANCE_INVALID")
        _require(type(traced.get("traced_block_count")) is int and traced["traced_block_count"] >= 1,
                 "CURRENT_WORD_SOURCE_TRACE_COVERAGE_MISSING")
        _require(type(traced.get("read_source_snapshot_count")) is int and traced["read_source_snapshot_count"] >= 1,
                 "CURRENT_WORD_SOURCE_SNAPSHOTS_NOT_OBSERVED")

    envelope: dict[str, Any] = {
        "schema_version": DELIVERY_EVIDENCE_SCHEMA_VERSION,
        "canonical_delivery_path": CANONICAL_DELIVERY_PATH,
        "artifact_kind": str(build_receipt.get("artifact_kind")),
        "artifact_sha256": str(build_receipt.get("sha256", "")).lower(),
        "build_receipt_sha256": _canonical_digest(unsigned_receipt),
        "builder_attestation": str(build_receipt.get("builder_attestation")),
        "mechanical_qa": "PASS",
        "constraint_qa": "PASS",
        "render_qa": "PASS",
        "visual_qa": "PASS",
        "source_ref": str(source_ref),
        "source_identity": str(source_identity),
    }
    if build_receipt.get("source_quality_evidence_sha256") is not None:
        envelope["source_quality_evidence_sha256"] = str(build_receipt["source_quality_evidence_sha256"])
    if verified_render_inspection is not None:
        envelope["render_inspection_receipt"] = verified_render_inspection
    if binding is not None:
        envelope["task_scope_binding"] = dict(binding)
        envelope["claim_trace_binding"] = dict(traced)
    signed = {**envelope, "session_attestation": _issuer_sign(envelope)}
    return {"delivery_evidence": signed, "delivery_evidence_sha256": _canonical_digest(signed)}


def validate_delivery_evidence(resource: Mapping[str, Any]) -> None:
    evidence = resource.get("delivery_evidence")
    _require(isinstance(evidence, Mapping), "delivery_evidence is required")
    expected_digest = resource.get("delivery_evidence_sha256")
    _require(isinstance(expected_digest, str) and len(expected_digest) == 64, "delivery_evidence_sha256 is required")
    _require(_canonical_digest(evidence) == expected_digest.lower(), "delivery_evidence digest mismatch")
    session_attestation = str(evidence.get("session_attestation", ""))
    _require(len(session_attestation) == 64, "delivery evidence lacks current-session attestation")
    unsigned = {key: value for key, value in evidence.items() if key != "session_attestation"}
    _require(hmac.compare_digest(session_attestation, _issuer_sign(unsigned)), "delivery evidence was not finalized by the current canonical Delivery session")
    _require(evidence.get("canonical_delivery_path") == CANONICAL_DELIVERY_PATH, "visible artifact bypassed canonical Delivery")
    _require(evidence.get("artifact_kind") == resource.get("kind"), "delivery evidence artifact kind mismatch")
    _require(str(evidence.get("artifact_sha256", "")).lower() == str(resource.get("sha256", "")).lower(), "delivery evidence artifact hash mismatch")
    _verify_render_inspection_receipt(
        evidence.get("render_inspection_receipt"), evidence.get("artifact_sha256"),
    )
    artifact_kind = str(evidence.get("artifact_kind", ""))
    binding = evidence.get("task_scope_binding")
    if artifact_kind in {"FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"}:
        _require(isinstance(binding, Mapping), "CURRENT_WORD_TASK_SCOPE_BINDING_REQUIRED")
        _require(
            binding.get("mode") == artifact_kind.removesuffix("_DOCX"),
            "CURRENT_WORD_TASK_SCOPE_MODE_MISMATCH",
        )
        _require(
            isinstance(binding.get("task_id"), str) and bool(binding.get("task_id"))
            and isinstance(binding.get("requirement_digest"), str)
            and re.fullmatch(r"[a-f0-9]{64}", binding["requirement_digest"]) is not None
            and type(binding.get("requirement_revision")) is int
            and binding["requirement_revision"] >= 0
            and binding.get("observed_stage") == "DELIVERY",
            "CURRENT_WORD_TASK_SCOPE_BINDING_INVALID",
        )
        _require(
            isinstance(binding.get("draft_artifact_path"), str)
            and isinstance(binding.get("draft_artifact_blob_sha"), str)
            and re.fullmatch(r"[a-f0-9]{40}", binding["draft_artifact_blob_sha"]) is not None,
            "CURRENT_WORD_TASK_DRAFT_BINDING_REQUIRED",
        )
    if binding is not None:
        trace = evidence.get("claim_trace_binding")
        from .claim_trace import SOURCE_TRACE_ASSURANCE

        _require(isinstance(trace, Mapping), "CURRENT_WORD_SOURCE_TRACE_REQUIRED")
        _require(trace.get("assurance") == SOURCE_TRACE_ASSURANCE,
                 "CURRENT_WORD_SOURCE_TRACE_ASSURANCE_INVALID")
        _require(trace.get("task_id") == binding.get("task_id"),
                 "CURRENT_WORD_SOURCE_TRACE_TASK_MISMATCH")
        _require(
            type(trace.get("traced_block_count")) is int and trace["traced_block_count"] >= 1
            and type(trace.get("read_source_snapshot_count")) is int
            and trace["read_source_snapshot_count"] >= 1,
            "CURRENT_WORD_SOURCE_TRACE_COVERAGE_MISSING",
        )
    for gate in ("mechanical_qa", "constraint_qa", "render_qa", "visual_qa"):
        _require(evidence.get(gate) == "PASS", f"delivery evidence requires {gate}=PASS")
    _require(bool(str(evidence.get("source_ref", "")).strip()), "delivery evidence source_ref is required")
    _require(bool(str(evidence.get("source_identity", "")).strip()), "delivery evidence source_identity is required")
