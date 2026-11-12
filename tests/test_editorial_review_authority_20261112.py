"""Provider-bound independent editorial review: identity strings alone are never proof."""
import hashlib

import pytest

from financial_writing_agent.editorial_review_authority import (
    IndependentEditorialEvidenceError, verify_external_editorial_review,
)
from financial_writing_agent.standalone_runtime import _blob_sha
from financial_writing_agent.schemas import AuditProvenance

RAW = b'{"draft":"actual candidate","deep":"draft","broad":"draft"}'
ARTICLE_SHA = hashlib.sha256(RAW).hexdigest()
DRAFT_PATH = "workspaces/articles/editorial-auth-fixture/stages/DRAFT.json"


def _state():
    return {
        "task_id": "editorial-auth-fixture",
        "stage_artifacts": {
            "DRAFT": {"path": DRAFT_PATH, "blob_sha": _blob_sha(RAW)},
        },
    }


def _fitness(mode, *, ref="run://real-review"):
    return {
        "product_mode": mode,
        "assurance": "INDEPENDENT_EXECUTOR",
        "audit_provenance": {
            "assurance": "INDEPENDENT_EXECUTOR",
            "reviewer_identity": "verified:external-editor",
            "author_identity": "verified:article-author",
            "execution_ref": ref,
            "reviewed_article_sha256": ARTICLE_SHA,
            "provider_attestation_sha256": "a" * 64,
        },
    }


def _draft(_):
    return {"content": RAW, "blob_sha": _blob_sha(RAW)}


def _verified(request):
    return {**request, "authenticated": True}


def test_full_editorial_modes_can_be_evidence_bound_by_an_external_provider():
    proof = verify_external_editorial_review(
        _state(), [_fitness("FINANCE_DEEP"), _fitness("FINANCE_BROAD")],
        draft_reader=_draft, provider_verifier=_verified,
    )
    assert proof["reviewed_draft_sha256"] == ARTICLE_SHA
    assert proof["reviewed_count"] == 2
    assert proof["source_authority_and_reader_outcome_verified"] is False
    assert "verified:external-editor" not in str(proof)


def test_untrusted_independent_review_must_not_be_accepted():
    kwargs = {"state": _state(), "publication_fitnesses": [_fitness("FINANCE_DEEP"), _fitness("FINANCE_BROAD")]}
    with pytest.raises(IndependentEditorialEvidenceError, match="TRUSTED_PROVIDER"):
        verify_external_editorial_review(**kwargs, draft_reader=_draft, provider_verifier=None)
    with pytest.raises(IndependentEditorialEvidenceError, match="PROVIDER_UNVERIFIED"):
        verify_external_editorial_review(**kwargs, draft_reader=_draft, provider_verifier=lambda _: {"authenticated": False})
    with pytest.raises(IndependentEditorialEvidenceError, match="ATTESTATION_MISMATCH"):
        verify_external_editorial_review(**kwargs, draft_reader=_draft, provider_verifier=lambda r: {**r, "authenticated": True, "reviewer_identity": "impostor"})


def test_review_of_stale_draft_and_partial_portfolio_fail_closed():
    fitnesses = [_fitness("FINANCE_DEEP"), _fitness("FINANCE_BROAD")]
    with pytest.raises(IndependentEditorialEvidenceError, match="WRONG_ARTICLE_VERSION"):
        bad = [dict(x) for x in fitnesses]
        bad[0]["audit_provenance"] = {**bad[0]["audit_provenance"], "reviewed_article_sha256": "f" * 64}
        verify_external_editorial_review(_state(), bad, draft_reader=_draft, provider_verifier=_verified)
    with pytest.raises(IndependentEditorialEvidenceError, match="PARTIAL_PORTFOLIO"):
        verify_external_editorial_review(
            _state(), [fitnesses[0], {"product_mode":"FINANCE_BROAD","assurance":"CHAT_SELF_REVIEW"}],
            draft_reader=_draft, provider_verifier=_verified,
        )


def test_pydantic_independent_provenance_must_carry_hash_binding():
    with pytest.raises(ValueError, match="reviewed_article_sha256"):
        AuditProvenance(assurance="INDEPENDENT_EXECUTOR", reviewer_identity="reviewer",
                        author_identity="author", execution_ref="run://review")
    model = AuditProvenance(
        assurance="INDEPENDENT_EXECUTOR", reviewer_identity="reviewer", author_identity="author",
        execution_ref="run://review", reviewed_article_sha256=ARTICLE_SHA,
        provider_attestation_sha256="a" * 64,
    )
    assert model.assurance == "INDEPENDENT_EXECUTOR"
