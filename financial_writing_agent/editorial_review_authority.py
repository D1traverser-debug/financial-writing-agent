"""External reviewer identity and exact article byte binding.

This module does NOT mint a reviewer or infer independence from two different
strings. A connected host must provide an authentication-backed verifier.
Without a trusted provider and a readback of exact current draft bytes,
INDEPENDENT_EXECUTOR reviews cannot become accepted business actions.
"""
from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from typing import Any


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
        request = {
            "task_id": state["task_id"],
            "product_mode": fitness["product_mode"],
            "reviewer_identity": provenance["reviewer_identity"],
            "author_identity": provenance["author_identity"],
            "execution_ref": provenance["execution_ref"],
            "provider_attestation_sha256": provenance["provider_attestation_sha256"],
            "reviewed_article_sha256": content_sha,
        }
        try:
            verified = provider_verifier(request)
        except Exception as exc:
            raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_PROVIDER_UNVERIFIED") from exc
        if not isinstance(verified, Mapping) or verified.get("authenticated") is not True:
            raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_PROVIDER_UNVERIFIED")
        if any(verified.get(key) != value for key, value in request.items()):
            raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_PROVIDER_ATTESTATION_MISMATCH")
        if request["reviewer_identity"] == request["author_identity"]:
            raise IndependentEditorialEvidenceError("INDEPENDENT_REVIEW_SELF_ASSESSMENT_NOT_ALLOWED")
        admitted.append({
            "product_mode": fitness["product_mode"],
            "reviewer_identity_hash": hashlib.sha256(
                request["reviewer_identity"].encode("utf-8")
            ).hexdigest(),
            "execution_ref_hash": hashlib.sha256(
                request["execution_ref"].encode("utf-8")
            ).hexdigest(),
            "provider_attestation_sha256": provenance["provider_attestation_sha256"],
        })
    return {
        "assurance": "AUTHENTICATED_EXTERNAL_PROVIDER_AND_EXACT_DRAFT_READBACK",
        "reviewed_draft_sha256": content_sha,
        "reviewed_modes": admitted,
        "reviewed_count": len(admitted),
        "source_authority_and_reader_outcome_verified": False,
    }
