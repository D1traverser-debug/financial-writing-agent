import pytest

from financial_writing_agent.delivery_availability import (
    DeliveryAvailabilityError,
    build_visible_delivery_receipt,
)


def _state():
    return {
        "task_id": "availability-task",
        "status": "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN",
        "required_outputs": ["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"],
        "delivery_artifacts": {
            "AUDIT_DOCX": {"kind": "AUDIT_DOCX", "file_name": "audit.docx", "sha256": "a" * 64},
            "FINANCE_DEEP_DOCX": {"kind": "FINANCE_DEEP_DOCX", "file_name": "deep.docx", "sha256": "b" * 64},
            "FINANCE_BROAD_DOCX": {"kind": "FINANCE_BROAD_DOCX", "file_name": "broad.docx", "sha256": "c" * 64},
        },
    }


def _canonical_resources():
    return [
        {"kind": "AUDIT_DOCX", "file_name": "audit.docx", "sha256": "a" * 64, "resource_ref": "session://audit"},
        {"kind": "FINANCE_DEEP_DOCX", "file_name": "deep.docx", "sha256": "b" * 64, "resource_ref": "session://deep"},
        {"kind": "FINANCE_BROAD_DOCX", "file_name": "broad.docx", "sha256": "c" * 64, "resource_ref": "session://broad"},
    ]


def test_visible_delivery_requires_exact_complete_current_resource_set():
    resources = _canonical_resources()[:-1]
    with pytest.raises(DeliveryAvailabilityError, match="visible delivery output mismatch"):
        build_visible_delivery_receipt(_state(), resources=resources, resource_verifier=lambda _: True)


def test_filename_and_hash_without_current_resource_ref_are_not_delivery_proof():
    resources = _canonical_resources()
    resources[1] = {"kind": "FINANCE_DEEP_DOCX", "file_name": "deep.docx", "sha256": "b" * 64}
    with pytest.raises(DeliveryAvailabilityError, match="resource_ref is required"):
        build_visible_delivery_receipt(_state(), resources=resources, resource_verifier=lambda _: True)


def test_unverified_current_resource_blocks_visible_delivery():
    with pytest.raises(DeliveryAvailabilityError, match="was not verified in the current session"):
        build_visible_delivery_receipt(_state(), resources=_canonical_resources(), resource_verifier=lambda item: item["kind"] != "FINANCE_DEEP_DOCX")


def test_non_regenerated_resource_must_match_canonical_binary_hash():
    resources = _canonical_resources()
    resources[1] = {**resources[1], "sha256": "d" * 64}
    with pytest.raises(DeliveryAvailabilityError, match="must match canonical owner state"):
        build_visible_delivery_receipt(_state(), resources=resources, resource_verifier=lambda _: True)


def test_regenerated_binary_is_a_new_instance_and_requires_source_plus_fresh_qa():
    resources = _canonical_resources()
    resources[1] = {
        "kind": "FINANCE_DEEP_DOCX",
        "file_name": "deep-redelivery.docx",
        "sha256": "d" * 64,
        "resource_ref": "session://deep-redelivery",
        "regenerated_from_durable_source": True,
        "source_ref": "workspaces/articles/availability-task/publication/FINANCE_DEEP.md",
        "source_identity": "git-blob:deep-source",
        "mechanical_qa": "PASS",
        "render_qa": "PASS",
    }
    receipt = build_visible_delivery_receipt(_state(), resources=resources, resource_verifier=lambda _: True)
    deep = receipt["presented_artifacts"]["FINANCE_DEEP_DOCX"]
    assert receipt["status"] == "VISIBLE_DELIVERY_READY"
    assert deep["sha256"] == "d" * 64
    assert deep["canonical_sha256"] == "b" * 64
    assert deep["regenerated_from_durable_source"] is True


def test_regenerated_binary_cannot_skip_fresh_render_qa():
    resources = _canonical_resources()
    resources[1] = {
        "kind": "FINANCE_DEEP_DOCX",
        "file_name": "deep-redelivery.docx",
        "sha256": "d" * 64,
        "resource_ref": "session://deep-redelivery",
        "regenerated_from_durable_source": True,
        "source_ref": "workspaces/articles/availability-task/publication/FINANCE_DEEP.md",
        "source_identity": "git-blob:deep-source",
        "mechanical_qa": "PASS",
        "render_qa": "OPEN",
    }
    with pytest.raises(DeliveryAvailabilityError, match="fresh render_qa=PASS"):
        build_visible_delivery_receipt(_state(), resources=resources, resource_verifier=lambda _: True)
