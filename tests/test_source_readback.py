from datetime import datetime, timedelta, timezone
import hashlib

import pytest

from financial_writing_agent.source_lifecycle import (
    DriveObjectReference,
    SourceBindingSet,
    SourceVersion,
    bind_source_version,
    create_source_record,
    mint_version_id,
)
from financial_writing_agent.source_readback import (
    SourceReadbackError,
    build_bound_source_reader,
    verify_source_version_readback,
)


BASE = datetime(2026, 11, 19, 10, 0, tzinfo=timezone.utc)


def _binding_set(*, revision_id="rev-1"):
    payload = b"exact original source payload"
    text = "normalized source text with sufficient evidence length"
    raw_sha = hashlib.sha256(payload).hexdigest()
    text_sha = hashlib.sha256(text.encode()).hexdigest()
    version = SourceVersion(
        version_id=mint_version_id(1, payload),
        created_at=BASE + timedelta(minutes=1),
        retrieved_at=BASE,
        source_family="issuer-primary",
        storage_policy="RAW_PRESERVED",
        rights_basis="PUBLIC_PRIMARY",
        drive_object=DriveObjectReference(
            folder_id="version-folder",
            file_id="immutable-file-1",
            revision_id=revision_id,
            media_type="application/pdf",
            size_bytes=len(payload),
            raw_sha256=raw_sha,
            normalized_text_sha256=text_sha,
            extractor_name="fixture-extractor",
            extractor_version="1",
        ),
    )
    record = create_source_record(
        source_id="src_" + "a" * 24,
        source_type="PUBLIC_PRIMARY_DOCUMENT",
        title="Issuer filing",
        publisher="Issuer",
        canonical_url="https://example.com/filing.pdf",
        scope="GLOBAL_REUSABLE",
        task_id=None,
        first_version=version,
    )
    binding = bind_source_version(record, version_id=version.version_id, task_id="article-1")
    binding_set = SourceBindingSet(
        task_id="article-1",
        research_revision=1,
        decision_envelope_sha256="a" * 64,
        private_research_brief_sha256="b" * 64,
        research_package_sha256="c" * 64,
        admitted_at=BASE + timedelta(minutes=2),
        bindings=(binding,),
    )
    observed = {
        "file_id": "immutable-file-1",
        "folder_id": "version-folder",
        "revision_id": revision_id,
        "media_type": "application/pdf",
        "size_bytes": len(payload),
        "payload": payload,
        "text": text,
        "source_family": "issuer-primary",
    }
    return binding_set, version, observed, payload, text


def test_bound_reader_returns_exact_verified_research_source():
    binding_set, _, observed, payload, text = _binding_set()
    result = build_bound_source_reader(
        binding_set,
        read_drive_version=lambda file_id, revision_id: observed,
    )(binding_set.bindings[0].source_ref)
    assert result["text"] == text
    assert result["sha256"] == hashlib.sha256(text.encode()).hexdigest()
    assert result["raw_sha256"] == hashlib.sha256(payload).hexdigest()
    assert result["file_id"] == "immutable-file-1"
    assert result["revision_id"] == "rev-1"
    assert result["source_family"] == "issuer-primary"


def test_bound_reader_supports_immutable_drive_files_without_revision_ids():
    binding_set, _, observed, _, _ = _binding_set(revision_id=None)
    result = build_bound_source_reader(
        binding_set,
        read_drive_version=lambda file_id, revision_id: observed,
    )(binding_set.bindings[0].source_ref)
    assert result["revision_id"] is None
    assert result["sha256"]


@pytest.mark.parametrize(
    ("patch", "message"),
    [
        ({"file_id": "another-file"}, "FILE_ID_MISMATCH"),
        ({"folder_id": "another-folder"}, "FOLDER_ID_MISMATCH"),
        ({"revision_id": "another-revision"}, "REVISION_ID_MISMATCH"),
        ({"media_type": "text/plain"}, "MEDIA_TYPE_MISMATCH"),
        ({"size_bytes": 1}, "SIZE_MISMATCH"),
        ({"payload": b"wrong original source payload"}, "RAW_SHA256_MISMATCH"),
        ({"text": "altered normalized source text with sufficient length"}, "NORMALIZED_TEXT_SHA256_MISMATCH"),
        ({"source_family": "secondary-source"}, "FAMILY_MISMATCH"),
    ],
)
def test_bound_reader_rejects_changed_identity_or_payload(patch, message):
    binding_set, _, observed, _, _ = _binding_set()
    changed = dict(observed)
    changed.update(patch)
    with pytest.raises(SourceReadbackError, match=message):
        build_bound_source_reader(
            binding_set,
            read_drive_version=lambda file_id, revision_id: changed,
        )(binding_set.bindings[0].source_ref)


def test_bound_reader_rejects_unbound_or_non_source_refs():
    binding_set, _, _, _, _ = _binding_set()
    reader = build_bound_source_reader(
        binding_set,
        read_drive_version=lambda file_id, revision_id: None,
    )
    with pytest.raises(SourceReadbackError, match="NOT_BOUND"):
        reader("https://example.com/filing.pdf")


def test_source_version_readback_uses_exact_drive_file_and_payload_hashes():
    _, version, observed, _, _ = _binding_set()
    result = verify_source_version_readback(version, observed=observed)
    assert result["file_id"] == version.drive_object.file_id
    assert result["raw_sha256"] == version.drive_object.raw_sha256
