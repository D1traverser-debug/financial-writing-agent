"""Provider-bound independent editorial review: identities and hashes are not proof."""
import hashlib

import pytest

from financial_writing_agent.editorial_review_authority import (
    IndependentEditorialEvidenceError, verify_external_editorial_review,
)
from financial_writing_agent.provider_attestation import payload_sha256
from financial_writing_agent.standalone_runtime import _blob_sha
from financial_writing_agent.schemas import AuditProvenance
from tests.trusted_provider_testkit import signed_attestation

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


def _fitness(mode, *, ref, reviewer="verified:external-editor"):
    fitness = {
        "product_mode": mode,
        "assurance": "INDEPENDENT_EXECUTOR",
        "gates": [{"gate": name, "status": "PASS"} for name in (
            "FACT_INTEGRITY", "RETENTION", "COMPANY_GROUNDING", "STRUCTURE_NUMBERING",
            "ORIGINALITY", "AUTHORIAL_STYLE", "COMPLIANCE", "PAYOFF",
        )],
        "originality_checks": [{
            "compared_source_ref": "source://checked",
            "checked_phrase_or_passage": "reviewed passage",
            "result": "NO_MATERIAL_OVERLAP",
            "notes": "external comparison completed",
        }],
        "deterministic_findings": [],
        "final_status": "PASS",
        "audit_provenance": {
            "assurance": "INDEPENDENT_EXECUTOR",
            "reviewer_identity": reviewer,
            "author_identity": "verified:article-author",
            "execution_ref": ref,
            "reviewed_article_sha256": ARTICLE_SHA,
            "provider_attestation_sha256": "0" * 64,
        },
    }
    review_body = {
        "product_mode": fitness["product_mode"],
        "assurance": fitness["assurance"],
        "gates": fitness["gates"],
        "originality_checks": fitness["originality_checks"],
        "deterministic_findings": fitness["deterministic_findings"],
        "final_status": fitness["final_status"],
    }
    attestation = signed_attestation(
        "independent_editorial_review", actor=reviewer,
        key_env="FINANCIAL_EDITORIAL_REVIEW_KEY",
        provider_env="FINANCIAL_EDITORIAL_REVIEW_PROVIDER_ID",
        approved=True, task_id="editorial-auth-fixture",
        product_mode=mode, author_identity="verified:article-author",
        execution_ref=ref, reviewed_article_sha256=ARTICLE_SHA,
        review_sha256=payload_sha256(review_body), final_status="PASS",
    )
    fitness["audit_provenance"]["provider_attestation_sha256"] = payload_sha256(attestation)
    return fitness, attestation


def _draft(_):
    return {"content": RAW, "blob_sha": _blob_sha(RAW)}


def _verified(attestations):
    return lambda request: attestations[request["execution_ref"]]


def test_full_editorial_modes_require_signed_review_of_exact_article_and_gate_results():
    deep, deep_attestation = _fitness("FINANCE_DEEP", ref="run://deep-review")
    broad, broad_attestation = _fitness("FINANCE_BROAD", ref="run://broad-review")
    proof = verify_external_editorial_review(
        _state(), [deep, broad],
        draft_reader=_draft,
        provider_verifier=_verified({
            "run://deep-review": deep_attestation,
            "run://broad-review": broad_attestation,
        }),
    )
    assert proof["reviewed_draft_sha256"] == ARTICLE_SHA
    assert proof["reviewed_count"] == 2
    assert proof["source_authority_and_reader_outcome_verified"] is False
    assert "verified:external-editor" not in str(proof)
    assert all(item["provider_id"] == "synthetic-editorial-review-provider"
               for item in proof["reviewed_modes"])


def test_unsigned_boolean_or_wrong_actor_review_cannot_be_accepted():
    deep, deep_attestation = _fitness("FINANCE_DEEP", ref="run://deep-review")
    broad, broad_attestation = _fitness("FINANCE_BROAD", ref="run://broad-review")
    kwargs = {"state": _state(), "publication_fitnesses": [deep, broad]}
    with pytest.raises(IndependentEditorialEvidenceError, match="TRUSTED_PROVIDER"):
        verify_external_editorial_review(**kwargs, draft_reader=_draft, provider_verifier=None)
    with pytest.raises(IndependentEditorialEvidenceError, match="PROVIDER_UNVERIFIED"):
        verify_external_editorial_review(
            **kwargs, draft_reader=_draft,
            provider_verifier=lambda _: {"authenticated": True},
        )
    impostor = dict(deep_attestation)
    impostor["authenticated_actor"] = "impostor"
    with pytest.raises(IndependentEditorialEvidenceError, match="PROVIDER_UNVERIFIED"):
        verify_external_editorial_review(
            **kwargs, draft_reader=_draft,
            provider_verifier=_verified({
                "run://deep-review": impostor,
                "run://broad-review": broad_attestation,
            }),
        )


def test_review_of_stale_draft_and_partial_portfolio_fail_closed():
    deep, deep_attestation = _fitness("FINANCE_DEEP", ref="run://deep-review")
    broad, broad_attestation = _fitness("FINANCE_BROAD", ref="run://broad-review")
    provider = _verified({
        "run://deep-review": deep_attestation,
        "run://broad-review": broad_attestation,
    })
    bad = [dict(deep), dict(broad)]
    bad[0]["audit_provenance"] = {
        **bad[0]["audit_provenance"], "reviewed_article_sha256": "f" * 64,
    }
    with pytest.raises(IndependentEditorialEvidenceError, match="WRONG_ARTICLE_VERSION"):
        verify_external_editorial_review(
            _state(), bad, draft_reader=_draft, provider_verifier=provider,
        )
    with pytest.raises(IndependentEditorialEvidenceError, match="PARTIAL_PORTFOLIO"):
        verify_external_editorial_review(
            _state(), [deep, {"product_mode": "FINANCE_BROAD", "assurance": "CHAT_SELF_REVIEW"}],
            draft_reader=_draft, provider_verifier=provider,
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
