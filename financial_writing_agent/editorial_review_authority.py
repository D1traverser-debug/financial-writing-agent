"""External reviewer identity and exact article byte binding.

This module does NOT mint a reviewer or infer independence from two different
strings. A connected host must provide an authentication-backed verifier.
Without a trusted provider and a readback of exact current draft bytes,
INDEPENDENT_EXECUTOR reviews cannot become accepted business actions.
"""
from __future__ import annotations

import hashlib
import os
from collections.abc import Callable, Mapping
from typing import Any

from .provider_attestation import (
    FinancialProviderAttestationError,
    payload_sha256,
    verify_provider_attestation,
)


class IndependentEditorialEvidenceError(ValueError):
    pass


def verify_external_editorial_review(
    state: Mapping[str, Any],
    publication_fitnesses: list[Mapping[str, Any]],
    *,
    draft_reader: Callable[[str], Mapping[str, Any] | None] | None,
    provider_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None,
) -> dict[str, Any] | None:
    independent = [
        item for item in publication_fitnesses
        if item.get("assurance") == "INDEPENDENT_EXECUTOR"
    ]
    if not independent:
        return None
    if not callable(draft_reader) or not callable(provider_verifier):
        raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_TRUSTED_PROVIDER_REQUIRED")
    if len(independent) != len(publication_fitnesses):
        raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_PARTIAL_PORTFOLIO_NOT_CERTIFIED")
    draft = state.get("stage_artifacts", {}).get("DRAFT")
    if not isinstance(draft, Mapping) or not isinstance(draft.get("path"), str):
        raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_DRAFT_ARTIFACT_REQUIRED")
    try:
        observed = draft_reader(draft["path"])
    except Exception as exc:
        raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_DRAFT_READ_FAILED") from exc
    if not isinstance(observed, Mapping) or not isinstance(observed.get("content"), (str, bytes)):
        raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_DRAFT_BYTES_REQUIRED")
    from .standalone_runtime import _blob_sha

    data = observed["content"]
    binary = data.encode("utf-8") if isinstance(data, str) else data
    if _blob_sha(binary) != observed.get("blob_sha") or observed["blob_sha"] != draft.get("blob_sha"):
        raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_DRAFT_BLOB_MISMATCH")
    content_sha = hashlib.sha256(binary).hexdigest()
    admitted: list[dict[str, Any]] = []
    for fitness in independent:
        provenance = fitness.get("audit_provenance")
        if not isinstance(provenance, Mapping):
            raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_PROVENANCE_REQUIRED")
        if provenance.get("reviewed_article_sha256") != content_sha:
            raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_WRONG_ARTICLE_VERSION")
        reviewer = provenance.get("reviewer_identity")
        author = provenance.get("author_identity")
        execution_ref = provenance.get("execution_ref")
        attestation_sha = provenance.get("provider_attestation_sha256")
        if not all(isinstance(value, str) and value.strip()
                   for value in (reviewer, author, execution_ref)):
            raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_IDENTITY_OR_EXECUTION_REF_MISSING")
        if reviewer == author:
            raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_SELF_ASSESSMENT_NOT_ALLOWED")
        review_body = {
            "product_mode": fitness["product_mode"],
            "assurance": fitness["assurance"],
            "gates": fitness.get("gates"),
            "originality_checks": fitness.get("originality_checks"),
            "deterministic_findings": fitness.get("deterministic_findings", []),
            "final_status": fitness.get("final_status"),
        }
        review_sha = payload_sha256(review_body)
        request = {
            "task_id": state["task_id"],
            "product_mode": fitness["product_mode"],
            "reviewer_identity": reviewer,
            "author_identity": author,
            "execution_ref": execution_ref,
            "provider_attestation_sha256": attestation_sha,
            "reviewed_article_sha256": content_sha,
            "review_sha256": review_sha,
            "final_status": fitness.get("final_status"),
        }
        try:
            raw_attestation = provider_verifier(request)
            if not isinstance(raw_attestation, Mapping):
                raise FinancialProviderAttestationError("FINANCIAL_EDITORIAL_REVIEW_ATTESTATION_MISSING")
            if not isinstance(attestation_sha, str) or payload_sha256(raw_attestation) != attestation_sha:
                raise FinancialProviderAttestationError("FINANCIAL_EDITORIAL_REVIEW_ATTESTATION_DIGEST_MISMATCH")
            verified = verify_provider_attestation(
                raw_attestation,
                expected_type="independent_editorial_review",
                expected_actor=reviewer,
                expected_claims={
                    "approved": fitness.get("final_status") == "PASS",
                    "task_id": state["task_id"],
                    "product_mode": fitness["product_mode"],
                    "author_identity": author,
                    "execution_ref": execution_ref,
                    "reviewed_article_sha256": content_sha,
                    "review_sha256": review_sha,
                    "final_status": fitness.get("final_status"),
                },
                key_env="FINANCIAL_EDITORIAL_REVIEW_KEY",
                provider_env="FINANCIAL_EDITORIAL_REVIEW_PROVIDER_ID",
            )
            if verified["provider_id"] == os.environ.get("FINANCIAL_TRUSTED_PROVIDER_ID"):
                raise FinancialProviderAttestationError("FINANCIAL_EDITORIAL_REVIEW_PROVIDER_NOT_INDEPENDENT")
        except Exception as exc:
            raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_PROVIDER_UNVERIFIED") from exc
        admitted.append({
            "product_mode": fitness["product_mode"],
            "reviewer_identity_hash": hashlib.sha256(
                reviewer.encode("utf-8")
            ).hexdigest(),
            "execution_ref_hash": hashlib.sha256(
                execution_ref.encode("utf-8")
            ).hexdigest(),
            "provider_id": verified["provider_id"],
            "provider_attestation_sha256": attestation_sha,
            "review_sha256": review_sha,
        })
    return {
        "assurance": "AUTHENTICATED_EXTERNAL_PROVIDER_AND_EXACT_DRAFT_READBACK",
        "reviewed_draft_sha256": content_sha,
        "reviewed_modes": admitted,
        "reviewed_count": len(admitted),
        "source_authority_and_reader_outcome_verified": False,
    }


def verify_internal_editorial_delivery_readiness(
    state: Mapping[str, Any],
    publication_fitnesses: list[Mapping[str, Any]],
    *,
    draft_reader: Callable[[str], Mapping[str, Any] | None] | None,
) -> dict[str, Any] | None:
    """Permit internally reviewed Word *draft* export, never independent PASS.

    Every product must bind its self-review to the exact persisted draft bytes.
    This is an author-level revision check only: factual truth, originality and
    reader acceptance are not inferred from same-session review.
    """
    selected = [
        item for item in publication_fitnesses
        if item.get("review_scope") == "INTERNAL_DELIVERY_READINESS"
    ]
    if not selected:
        return None
    if len(selected) != len(publication_fitnesses):
        raise IndependentEditorialEvidenceError(
            "INTERNAL_READINESS_MIXED_WITH_PUBLICATION_CERTIFICATION"
        )
    if not callable(draft_reader):
        raise IndependentEditorialEvidenceError("INTERNAL_READINESS_DRAFT_READER_REQUIRED")
    draft = state.get("stage_artifacts", {}).get("DRAFT")
    if not isinstance(draft, Mapping) or not isinstance(draft.get("path"), str):
        raise IndependentEditorialEvidenceError("INTERNAL_READINESS_DRAFT_REFERENCE_MISSING")
    try:
        observed = draft_reader(draft["path"])
    except Exception as exc:
        raise IndependentEditorialEvidenceError("INTERNAL_READINESS_DRAFT_READ_FAILED") from exc
    if not isinstance(observed, Mapping) or not isinstance(observed.get("content"), (str, bytes)):
        raise IndependentEditorialEvidenceError("INTERNAL_READINESS_DRAFT_BYTES_MISSING")
    from .standalone_runtime import _blob_sha
    data = observed["content"]
    binary = data.encode("utf-8") if isinstance(data, str) else data
    if _blob_sha(binary) != draft.get("blob_sha") or observed.get("blob_sha") != draft.get("blob_sha"):
        raise IndependentEditorialEvidenceError("INTERNAL_READINESS_DRAFT_BLOB_MISMATCH")
    content_sha = hashlib.sha256(binary).hexdigest()
    modes: set[str] = set()
    for fitness in selected:
        provenance = fitness.get("audit_provenance")
        if not isinstance(provenance, Mapping):
            raise IndependentEditorialEvidenceError("INTERNAL_READINESS_PROVENANCE_REQUIRED")
        if fitness.get("assurance") != "CHAT_SELF_REVIEW" or fitness.get("final_status") != "PASS":
            raise IndependentEditorialEvidenceError("INTERNAL_READINESS_REVIEW_NOT_CLEAR")
        if provenance.get("assurance") != "CHAT_SELF_REVIEW" or provenance.get("reviewed_article_sha256") != content_sha:
            raise IndependentEditorialEvidenceError("INTERNAL_READINESS_WRONG_DRAFT_VERSION")
        mode = fitness.get("product_mode")
        if not isinstance(mode, str) or mode in modes:
            raise IndependentEditorialEvidenceError("INTERNAL_READINESS_MODES_INVALID")
        modes.add(mode)
    return {
        "status": "WORD_DRAFT_DELIVERY_READY__INDEPENDENT_CERTIFICATION_OPEN",
        "reviewed_draft_sha256": content_sha,
        "reviewed_modes": sorted(modes),
        "reviewed_count": len(modes),
        "independent_editorial_quality_verified": False,
        "factual_and_reader_outcomes_verified": False,
    }
