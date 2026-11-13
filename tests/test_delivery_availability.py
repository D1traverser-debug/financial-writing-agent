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
    render_body = {
        "render_receipt_version": delivery_pipeline.RENDER_INSPECTION_RECEIPT_VERSION,
        "artifact_sha256": digest,
        "rendered_pdf_sha256": hashlib.sha256(b"%PDF synthetic fixture").hexdigest(),
        "rendered_page_count": 1,
        "pages": [{
            "page_index": 1, "page_sha256": "d" * 64,
            "pixel_width": 1200, "pixel_height": 1600,
            "review_status": "PASS", "review_ref": "synthetic://page-review/1",
        }],
        "review_assurance": "CALLER_SUPPLIED_REVIEW__INDEPENDENCE_NOT_ESTABLISHED",
    }
    render_receipt = {
        **render_body,
        "session_attestation": delivery_pipeline._issuer_sign(render_body),
    }
    return finalize_delivery_evidence(
        build,
        source_ref=f"workspaces/articles/availability-task/source/{kind}.json",
        source_identity=f"git-blob:{kind.lower()}",
        render_qa="PASS",
        visual_qa="PASS",
        render_inspection_receipt=render_receipt,
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


def test_current_visible_delivery_requires_genuine_provider_docx_bytes_not_boolean_ack():
    from io import BytesIO
    from docx import Document

    state = _state(with_private=False)
    state["writing_kernel_version"] = "1.0"
    resources = _canonical_resources()
    with pytest.raises(DeliveryAvailabilityError, match="CURRENT_FINANCIAL_BINARY_READER_REQUIRED"):
        build_visible_delivery_receipt(state, resources=resources, resource_verifier=lambda _: True)

    with pytest.raises(DeliveryAvailabilityError, match="current DOCX bytes not available"):
        build_visible_delivery_receipt(
            state, resources=resources, resource_verifier=lambda _: True,
            resource_binary_reader=lambda _: None,
        )

    stream = BytesIO()
    d = Document()
    d.add_paragraph("当前财经文章 Word 页面必须可真实读取。")
    d.save(stream)
    blob = stream.getvalue()
    with pytest.raises(DeliveryAvailabilityError, match="actual DOCX bytes differ from declared hash"):
        build_visible_delivery_receipt(
            state, resources=resources, resource_verifier=lambda _: True,
            resource_binary_reader=lambda _: {"content": blob},
        )

    # A correct real DOCX and hash can get through *binary* verification.
    # Other independent editorial and source gates remain separate.
    digest = hashlib.sha256(blob).hexdigest()
    for kind in state["delivery_artifacts"]:
        state["delivery_artifacts"][kind]["sha256"] = digest
    resources = [
        _resource(kind, item["file_name"], digest)
        for kind, item in state["delivery_artifacts"].items()
    ]
    # Correct binary alone is not an accepted current deliverable. Remove
    # the page receipt and re-sign the envelope to model an otherwise valid
    # same-session build with no render/readback evidence.
    for resource in resources:
        evidence = resource["delivery_evidence"]
        unsigned = {key: value for key, value in evidence.items() if key != "session_attestation"}
        unsigned.pop("render_inspection_receipt", None)
        signed = {
            **unsigned,
            "session_attestation": delivery_pipeline._issuer_sign(unsigned),
        }
        resource["delivery_evidence"] = signed
        resource["delivery_evidence_sha256"] = delivery_pipeline._canonical_digest(signed)
    with pytest.raises(DeliveryAvailabilityError, match="CURRENT_WORD_RENDER_RECEIPT_REQUIRED"):
        build_visible_delivery_receipt(
            state, resources=resources, resource_verifier=lambda _: True,
            resource_binary_reader=lambda _: {"content": blob},
        )
