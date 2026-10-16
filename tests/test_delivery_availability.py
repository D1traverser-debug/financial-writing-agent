import hashlib
import json

import pytest

from financial_writing_agent import delivery_pipeline
from financial_writing_agent.delivery_availability import (
    DeliveryAvailabilityError,
    build_visible_delivery_receipt,
)
from financial_writing_agent.delivery_pipeline import finalize_delivery_evidence
from financial_writing_agent.private_research import REQUIRED_MODULES, validate_private_research_brief


def _brief():
    return {
        "contract_version": "1.1",
        "as_of": "2026-10-16T15:00:00+08:00",
        "coverage_state": "COMPLETE",
        "modules": {
            name: {
                "status": "APPLICABLE",
                "summary": f"{name} complete",
                "evidence_refs": [f"evidence://{name}"],
            }
            for name in REQUIRED_MODULES
        },
        "unresolved_gaps": [],
    }


def _brief_digest(brief):
    admitted = validate_private_research_brief(brief)
    payload = json.dumps(admitted, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _state(*, with_private=False):
    state = {
        "task_id": "availability-task",
        "status": "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN",
        "required_outputs": ["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"],
        "delivery_artifacts": {
            "AUDIT_DOCX": {"kind": "AUDIT_DOCX", "file_name": "audit.docx", "sha256": "a" * 64},
            "FINANCE_DEEP_DOCX": {"kind": "FINANCE_DEEP_DOCX", "file_name": "deep.docx", "sha256": "b" * 64},
            "FINANCE_BROAD_DOCX": {"kind": "FINANCE_BROAD_DOCX", "file_name": "broad.docx", "sha256": "c" * 64},
        },
    }
    if with_private:
        brief = _brief()
        state["private_research_contract_version"] = "1.1"
        state["quality_evidence"] = {"private_research_brief": brief}
    return state


def _delivery_evidence(kind, digest, *, source_quality_evidence_sha256=None):
    payload = {
        "schema_version": "1.1",
        "canonical_delivery_path": "financial_writing_agent.delivery_pipeline",
        "artifact_kind": kind,
        "file_name": f"{kind}.docx",
        "sha256": digest,
        "mechanical_qa": "PASS",
        "constraint_qa": "PASS",
    }
    if source_quality_evidence_sha256 is not None:
        payload["source_quality_evidence_sha256"] = source_quality_evidence_sha256
    build = delivery_pipeline._issue_build_receipt(payload)
    return finalize_delivery_evidence(
        build,
        source_ref=f"workspaces/articles/availability-task/source/{kind}.json",
        source_identity=f"git-blob:{kind.lower()}",
        render_qa="PASS",
        visual_qa="PASS",
    )


def _resource(kind, file_name, digest, *, regenerated=False, source_quality_evidence_sha256=None):
    resource = {
        "kind": kind,
        "file_name": file_name,
        "sha256": digest,
        "resource_ref": f"session://{kind.lower()}",
        **_delivery_evidence(kind, digest, source_quality_evidence_sha256=source_quality_evidence_sha256),
    }
    if regenerated:
        resource.update(
            {
                "regenerated_from_durable_source": True,
                "source_ref": f"workspaces/articles/availability-task/source/{kind}.json",
                "source_identity": f"git-blob:{kind.lower()}",
            }
        )
    return resource


def _canonical_resources():
    return [
        _resource("AUDIT_DOCX", "audit.docx", "a" * 64),
        _resource("FINANCE_DEEP_DOCX", "deep.docx", "b" * 64),
        _resource("FINANCE_BROAD_DOCX", "broad.docx", "c" * 64),
    ]


def _private_resource(state, *, digest_override=None):
    digest = digest_override or _brief_digest(state["quality_evidence"]["private_research_brief"])
    return _resource(
        "PRIVATE_RESEARCH_DOCX",
        "private.docx",
        "e" * 64,
        regenerated=True,
        source_quality_evidence_sha256=digest,
    )


def test_visible_delivery_requires_exact_complete_current_resource_set():
    resources = _canonical_resources()[:-1]
    with pytest.raises(DeliveryAvailabilityError, match="visible delivery output mismatch"):
        build_visible_delivery_receipt(_state(), resources=resources, resource_verifier=lambda _: True)


def test_filename_and_hash_without_current_resource_ref_are_not_delivery_proof():
    resources = _canonical_resources()
    resources[1] = {key: value for key, value in resources[1].items() if key != "resource_ref"}
    with pytest.raises(DeliveryAvailabilityError, match="resource_ref is required"):
        build_visible_delivery_receipt(_state(), resources=resources, resource_verifier=lambda _: True)


def test_unverified_current_resource_blocks_visible_delivery():
    with pytest.raises(DeliveryAvailabilityError, match="was not verified in the current session"):
        build_visible_delivery_receipt(
            _state(),
            resources=_canonical_resources(),
            resource_verifier=lambda item: item["kind"] != "FINANCE_DEEP_DOCX",
        )


def test_non_regenerated_resource_must_match_canonical_binary_hash():
    resources = _canonical_resources()
    resources[1] = _resource("FINANCE_DEEP_DOCX", "deep.docx", "d" * 64)
    with pytest.raises(DeliveryAvailabilityError, match="must match canonical owner state"):
        build_visible_delivery_receipt(_state(), resources=resources, resource_verifier=lambda _: True)


def test_regenerated_binary_is_a_new_instance_and_requires_canonical_delivery_evidence():
    resources = _canonical_resources()
    resources[1] = _resource("FINANCE_DEEP_DOCX", "deep-redelivery.docx", "d" * 64, regenerated=True)
    receipt = build_visible_delivery_receipt(_state(), resources=resources, resource_verifier=lambda _: True)
    deep = receipt["presented_artifacts"]["FINANCE_DEEP_DOCX"]
    assert receipt["status"] == "VISIBLE_DELIVERY_READY"
    assert deep["sha256"] == "d" * 64
    assert deep["canonical_sha256"] == "b" * 64
    assert deep["regenerated_from_durable_source"] is True
    assert deep["canonical_delivery_path"] == "financial_writing_agent.delivery_pipeline"
    assert deep["visual_qa"] == "PASS"


def test_missing_delivery_evidence_blocks_even_hash_matching_canonical_resource():
    resources = _canonical_resources()
    resources[0].pop("delivery_evidence")
    resources[0].pop("delivery_evidence_sha256")
    with pytest.raises(DeliveryAvailabilityError, match="canonical delivery evidence failed"):
        build_visible_delivery_receipt(_state(), resources=resources, resource_verifier=lambda _: True)


def test_current_private_research_state_requires_private_word_supplement_bound_to_owner_brief():
    state = _state(with_private=True)
    with pytest.raises(DeliveryAvailabilityError, match="PRIVATE_RESEARCH_DOCX"):
        build_visible_delivery_receipt(
            state,
            resources=_canonical_resources(),
            resource_verifier=lambda _: True,
        )

    receipt = build_visible_delivery_receipt(
        state,
        resources=[*_canonical_resources(), _private_resource(state)],
        resource_verifier=lambda _: True,
    )
    assert receipt["supplemental_required_outputs"] == ["PRIVATE_RESEARCH_DOCX"]
    assert receipt["presented_artifacts"]["PRIVATE_RESEARCH_DOCX"]["supplemental"] is True
    assert receipt["presented_artifacts"]["PRIVATE_RESEARCH_DOCX"]["visual_qa"] == "PASS"
    assert receipt["presented_artifacts"]["PRIVATE_RESEARCH_DOCX"]["source_quality_evidence_sha256"] == _brief_digest(state["quality_evidence"]["private_research_brief"])


def test_private_research_resource_bound_to_wrong_brief_is_rejected():
    state = _state(with_private=True)
    with pytest.raises(DeliveryAvailabilityError, match="not bound to the admitted owner"):
        build_visible_delivery_receipt(
            state,
            resources=[*_canonical_resources(), _private_resource(state, digest_override="f" * 64)],
            resource_verifier=lambda _: True,
        )


def test_historical_state_without_private_marker_does_not_retroactively_require_private_word():
    receipt = build_visible_delivery_receipt(
        _state(with_private=False),
        resources=_canonical_resources(),
        resource_verifier=lambda _: True,
    )
    assert receipt["supplemental_required_outputs"] == []
