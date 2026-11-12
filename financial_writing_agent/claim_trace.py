"""Source text, numeric provenance and conservative hard-negative financial checks.

An external caller provides source reads. We recompute UTF-8 snapshot digests
and ensure a public paragraph's asserted numbers occur in retrieved excerpts.
The receipt does not certify factual entailment, source authority or reviewer
independence. Original private source bytes/URLs are never copied into it.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Callable, Mapping
from typing import Any

from .financial_fact_guard import FinancialFactConflict, reject_direct_fact_contradictions

SOURCE_TRACE_ASSURANCE = "SOURCE_TEXT_AND_NUMERALS_OBSERVED__SEMANTIC_ENTAILMENT_NOT_VERIFIED"
_NUMERIC = re.compile(r"\d+(?:[.,]\d+)*")
_SPACE = re.compile(r"\s+")


class SourceTraceError(ValueError):
    pass


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SourceTraceError(message)


def _field(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(key, default)
    return getattr(value, key, default)


def _plain(value: Any) -> str:
    """Comparison-only Unicode and whitespace normalization."""
    text = unicodedata.normalize("NFKC", str(value))
    return _SPACE.sub("", text.replace("**", "").replace("__", ""))


def _numbers(text: str) -> set[str]:
    return set(_NUMERIC.findall(_plain(text)))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_publication_source_trace(
    article: Any,
    evidence: list[Mapping[str, Any]],
    *,
    source_reader: Callable[[str], Mapping[str, Any] | None] | None,
    article_task_id: str,
) -> dict[str, Any]:
    """Trace all factual content paragraphs and numeric tokens to real snapshots.

    Rows contain claim_id, block_index (-1 for title), claim_excerpt,
    source_ref, source_excerpt. Source reader returns UTF-8 text + sha256.
    Derived statistics cannot be passed off as direct-text verified: a
    separate calculation review method must be invoked for such claims.
    """
    _require(isinstance(article_task_id, str) and bool(article_task_id.strip()), "SOURCE_TRACE_TASK_ID_REQUIRED")
    _require(callable(source_reader), "SOURCE_TRACE_SOURCE_READER_REQUIRED")
    _require(isinstance(evidence, list) and bool(evidence), "SOURCE_TRACE_EVIDENCE_LEDGER_REQUIRED")
    title = str(_field(article, "title", ""))
    blocks = _field(article, "blocks", [])
    _require(isinstance(blocks, list), "SOURCE_TRACE_ARTICLE_BLOCKS_INVALID")
    required = {
        index for index, block in enumerate(blocks)
        if _field(block, "kind") in {"lead", "body"}
        or (_field(block, "kind") in {"h1", "h2", "h3"} and _numbers(_field(block, "text", "")))
    }
    if _numbers(title):
        required.add(-1)
    _require(bool(required), "SOURCE_TRACE_NO_SUBSTANTIVE_ARTICLE_CONTENT")
    seen_claims: set[str] = set()
    covered: set[int] = set()
    observed_numbers: dict[int, set[str]] = {}
    snapshots: dict[str, dict[str, Any]] = {}
    bound_claims: list[dict[str, Any]] = []

    for row in evidence:
        _require(isinstance(row, Mapping), "SOURCE_TRACE_ROW_INVALID")
        fields = {"claim_id", "block_index", "claim_excerpt", "source_ref", "source_excerpt"}
        _require(set(row) == fields, "SOURCE_TRACE_ROW_FIELDS_MISMATCH")
        cid = row["claim_id"]
        _require(isinstance(cid, str) and bool(cid.strip()) and cid not in seen_claims,
                 "SOURCE_TRACE_CLAIM_ID_INVALID_OR_DUPLICATE")
        seen_claims.add(cid)
        index = row["block_index"]
        _require(type(index) is int and index in required, "SOURCE_TRACE_BLOCK_INDEX_INVALID")
        public_text = title if index == -1 else str(_field(blocks[index], "text", ""))
        claim = _plain(row["claim_excerpt"])
        _require(len(claim) >= 5 and claim in _plain(public_text), "SOURCE_TRACE_CLAIM_NOT_IN_PUBLIC_PARAGRAPH")
        source_ref, excerpt = row["source_ref"], row["source_excerpt"]
        _require(isinstance(source_ref, str) and bool(source_ref.strip()), "SOURCE_TRACE_SOURCE_REF_MISSING")
        _require(isinstance(excerpt, str) and len(_plain(excerpt)) >= 10,
                 "SOURCE_TRACE_SOURCE_EXCERPT_TOO_SHORT")
        if source_ref not in snapshots:
            try:
                snapshot = source_reader(source_ref)
            except Exception as exc:
                raise SourceTraceError("SOURCE_TRACE_SOURCE_READ_FAILED") from exc
            _require(isinstance(snapshot, Mapping), "SOURCE_TRACE_SOURCE_READBACK_MISSING")
            text_value, declared = snapshot.get("text"), snapshot.get("sha256")
            _require(isinstance(text_value, str) and isinstance(declared, str)
                     and re.fullmatch(r"[a-f0-9]{64}", declared) is not None,
                     "SOURCE_TRACE_SOURCE_SNAPSHOT_INVALID")
            _require(_sha256(text_value) == declared, "SOURCE_TRACE_SOURCE_SNAPSHOT_SHA_MISMATCH")
            snapshots[source_ref] = {"text": text_value, "sha256": declared}
        snapshot = snapshots[source_ref]
        _require(_plain(excerpt) in _plain(snapshot["text"]), "SOURCE_TRACE_EXCERPT_NOT_IN_SOURCE_SNAPSHOT")
        _require(
            _numbers(claim).issubset(_numbers(excerpt)),
            "SOURCE_TRACE_CLAIM_NUMBERS_ABSENT_FROM_SOURCE_EXCERPT",
        )
        try:
            reject_direct_fact_contradictions(row["claim_excerpt"], excerpt)
        except FinancialFactConflict as exc:
            raise SourceTraceError(str(exc)) from exc
        observed_numbers.setdefault(index, set()).update(_numbers(excerpt))
        covered.add(index)
        bound_claims.append({
            "claim_id": cid, "block_index": index,
            "claim_excerpt_sha256": _sha256(claim),
            "source_ref_sha256": _sha256(source_ref),
            "source_snapshot_sha256": snapshot["sha256"],
            "source_excerpt_sha256": _sha256(_plain(excerpt)),
        })
    missing = sorted(required - covered)
    _require(not missing, f"SOURCE_TRACE_UNSUPPORTED_PUBLIC_PARAGRAPHS:{missing}")
    for index in sorted(required):
        public_text = title if index == -1 else str(_field(blocks[index], "text", ""))
        unsupported = sorted(_numbers(public_text) - observed_numbers.get(index, set()))
        _require(not unsupported, f"SOURCE_TRACE_UNSUPPORTED_PUBLIC_NUMBERS:{index}:{unsupported}")
    article_binding = {
        "title": title,
        "blocks": [{"kind": _field(b, "kind"), "text": _field(b, "text")} for b in blocks],
    }
    return {
        "schema_version": "1.0",
        "task_id": article_task_id,
        "article_content_sha256": _sha256(
            json.dumps(article_binding, ensure_ascii=False, sort_keys=True)
        ),
        "traced_block_count": len(required),
        "traced_claim_count": len(bound_claims),
        "read_source_snapshot_count": len(snapshots),
        "numeric_tokens_matched": sum(len(_numbers(
            title if index == -1 else _field(blocks[index], "text", "")
        )) for index in required),
        "bindings": bound_claims,
        "assurance": SOURCE_TRACE_ASSURANCE,
        "primary_source_authority_verified": False,
        "semantic_fact_entailment_verified": False,
        "independent_journalist_review_verified": False,
    }
