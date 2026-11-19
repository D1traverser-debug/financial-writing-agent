from datetime import datetime, timedelta, timezone
import hashlib

import pytest
from pydantic import ValidationError

from financial_writing_agent.source_lifecycle import (
    DriveObjectReference,
    SourceBindingSet,
    SourceRecord,
    SourceVersion,
    append_source_version,
    bind_source_version,
    create_source_record,
    retire_source,
    restore_source,
    validate_source_binding_coverage,
)


BASE = datetime(2026, 11, 19, 10, 0, tzinfo=timezone.utc)
SOURCE_ID = "src_" + "a" * 24


def _version(sequence, payload, *, created_at=None, source_family="official", storage_policy="RAW_PRESERVED", rights_basis="PUBLIC_PRIMARY", status="AVAILABLE"):
    created_at = created_at or BASE + timedelta(days=sequence)
    raw_sha = hashlib.sha256(payload).hexdigest()
    normalized_sha = hashlib.sha256(payload.lower()).hexdigest()
    return SourceVersion(
        version_id=f"v{sequence:04d}-{raw_sha[:12]}",
        created_at=created_at,
        retrieved_at=created_at - timedelta(seconds=1),
        source_family=source_family,
        storage_policy=storage_policy,
        rights_basis=rights_basis,
        status=status,
        drive_object=DriveObjectReference(
            folder_id="private-drive-folder",
            file_id=f"drive-file-{sequence}",
            revision_id=f"drive-revision-{sequence}",
            media_type="application/pdf",
            size_bytes=len(payload),
            raw_sha256=raw_sha,
            normalized_text_sha256=normalized_sha,
            extractor_name="pymupdf",
            extractor_version="1.26.0",
        ),
    )


def _record(*, scope="GLOBAL_REUSABLE", task_id=None, source_type="PUBLIC_PRIMARY_DOCUMENT", first=None, source_id=SOURCE_ID):
    first = first or _version(1, b"official report v1")
    return create_source_record(
        source_id=source_id,
        source_type=source_type,
        title="Official filing",
        publisher="Issuer",
        canonical_url="https://example.com/filing.pdf",
        scope=scope,
        task_id=task_id,
        first_version=first,
    )


def test_create_and_bind_pins_exact_drive_file_revision_and_hashes():
    record = _record()
    binding = bind_source_version(record, version_id=record.current_version_id, task_id="article-1")

    assert binding.source_ref == f"financial-source://{SOURCE_ID}/{record.current_version_id}"
    assert binding.drive_file_id == "drive-file-1"
    assert binding.drive_folder_id == "private-drive-folder"
    assert binding.source_type == "PUBLIC_PRIMARY_DOCUMENT"
    assert binding.scope == "GLOBAL_REUSABLE"
    assert binding.rights_basis == "PUBLIC_PRIMARY"
    assert binding.publisher == "Issuer"
    assert binding.canonical_url == "https://example.com/filing.pdf"
    assert binding.media_type == "application/pdf"
    assert binding.drive_file_size_bytes == len(b"official report v1")
    assert binding.extractor_name == "pymupdf"
    assert binding.extractor_version == "1.26.0"
    assert binding.drive_revision_id == "drive-revision-1"
    assert binding.raw_sha256 == record.versions[0].drive_object.raw_sha256
    assert binding.normalized_text_sha256 == record.versions[0].drive_object.normalized_text_sha256


def test_update_appends_new_immutable_version_and_keeps_old_binding_stable():
    record = _record()
    old_binding = bind_source_version(record, version_id=record.current_version_id, task_id="article-1")
    version2 = _version(2, b"official report v2")
    updated = append_source_version(record, version2)

    assert len(updated.versions) == 2
    assert updated.current_version_id == version2.version_id
    assert updated.versions[0] == record.versions[0]
    assert bind_source_version(updated, version_id=record.versions[0].version_id, task_id="article-1") == old_binding
    assert bind_source_version(updated, version_id=version2.version_id, task_id="article-1").drive_file_id == "drive-file-2"


def test_source_update_rejects_overwrite_and_skipped_version_sequence():
    record = _record()
    with pytest.raises(ValueError, match="cannot be overwritten"):
        append_source_version(record, record.versions[0])
    with pytest.raises(ValueError, match="next contiguous sequence"):
        append_source_version(record, _version(3, b"skipped version"))


def test_retire_blocks_new_bindings_and_restore_reenables_them():
    record = _record()
    retired = retire_source(record, at=BASE + timedelta(days=3))
    assert retired.status == "RETIRED"
    with pytest.raises(ValueError, match="cannot be newly bound"):
        bind_source_version(retired, version_id=retired.current_version_id, task_id="article-1")

    restored = restore_source(retired, at=BASE + timedelta(days=4))
    assert restored.status == "ACTIVE"
    assert bind_source_version(restored, version_id=restored.current_version_id, task_id="article-1")


def test_task_only_source_cannot_be_reused_by_another_article():
    record = _record(scope="TASK_ONLY", task_id="article-A")
    binding = bind_source_version(record, version_id=record.current_version_id, task_id="article-A")
    assert binding.source_task_id == "article-A"
    assert binding.scope == "TASK_ONLY"
    with pytest.raises(ValueError, match="cannot be reused by another task"):
        bind_source_version(record, version_id=record.current_version_id, task_id="article-B")


def test_source_version_rejects_bad_hash_and_unlicensed_full_news_storage():
    with pytest.raises(ValidationError, match="raw_sha256"):
        DriveObjectReference(
            folder_id="folder",
            file_id="file",
            revision_id="revision",
            media_type="text/plain",
            size_bytes=1,
            raw_sha256="not-a-sha",
            normalized_text_sha256="a" * 64,
            extractor_name="text",
            extractor_version="1",
        )

    news_version = _version(
        1,
        b"news article",
        source_family="news",
        storage_policy="RAW_PRESERVED",
        rights_basis="PUBLIC_PRIMARY",
    )
    with pytest.raises(ValidationError, match="full news-media preservation"):
        _record(source_type="NEWS_MEDIA", first=news_version)


def test_news_media_defaults_to_metadata_or_excerpt_storage_without_full_copy():
    version = _version(
        1,
        b"permitted short excerpt",
        source_family="news",
        storage_policy="METADATA_AND_EXCERPT_ONLY",
        rights_basis="METADATA_ONLY",
    )
    record = _record(source_type="NEWS_MEDIA", first=version)
    assert record.versions[0].storage_policy == "METADATA_AND_EXCERPT_ONLY"


def test_source_record_rejects_active_pointer_to_unavailable_version():
    unavailable = _version(1, b"missing original", status="MISSING")
    with pytest.raises(ValidationError, match="ACTIVE source must point to an AVAILABLE"):
        _record(first=unavailable)



def test_source_record_requires_complete_ordered_history_and_latest_pointer():
    record = _record()
    version2 = _version(2, b"official report v2")
    updated = append_source_version(record, version2)

    stale_pointer = updated.model_dump()
    stale_pointer["current_version_id"] = record.current_version_id
    with pytest.raises(ValidationError, match="newest immutable version"):
        SourceRecord.model_validate(stale_pointer)

    skipped_start = _version(2, b"first stored version cannot start at two")
    with pytest.raises(ValidationError, match="must start at v0001"):
        SourceRecord(
            source_id=SOURCE_ID,
            source_type="PUBLIC_PRIMARY_DOCUMENT",
            title="Invalid history",
            scope="GLOBAL_REUSABLE",
            task_id=None,
            created_at=skipped_start.created_at,
            updated_at=skipped_start.created_at,
            current_version_id=skipped_start.version_id,
            versions=(skipped_start,),
        )

    stale_updated_at = updated.model_dump()
    stale_updated_at["updated_at"] = record.updated_at
    with pytest.raises(ValidationError, match="cannot precede the newest source version"):
        SourceRecord.model_validate(stale_updated_at)


def test_each_source_version_requires_a_new_drive_file_object():
    record = _record()
    version2 = _version(2, b"official report v2")
    duplicate_drive_object = version2.drive_object.model_copy(
        update={"file_id": record.versions[0].drive_object.file_id}
    )
    duplicate_version = version2.model_copy(update={"drive_object": duplicate_drive_object})

    with pytest.raises(ValueError, match="new Drive file ID"):
        append_source_version(record, duplicate_version)


def test_source_domain_records_and_versions_are_immutable_values():
    record = _record()

    with pytest.raises(ValidationError):
        record.status = "RETIRED"
    with pytest.raises(AttributeError):
        record.versions.append(record.versions[0])
    with pytest.raises(ValidationError):
        record.versions[0].drive_object.file_id = "replacement-file"



def test_binding_set_pins_one_research_revision_and_exact_canonical_evidence_refs():
    record = _record()
    binding = bind_source_version(
        record,
        version_id=record.current_version_id,
        task_id="article-1",
    )
    binding_set = SourceBindingSet(
        task_id="article-1",
        research_revision=3,
        private_research_brief_sha256="a" * 64,
        research_package_sha256="b" * 64,
        admitted_at=BASE + timedelta(days=2),
        bindings=(binding,),
    )

    assert validate_source_binding_coverage(
        binding_set,
        task_id="article-1",
        evidence_refs=[binding.source_ref],
    ) == binding_set

    with pytest.raises(ValueError, match="raw external URLs"):
        validate_source_binding_coverage(
            binding_set,
            task_id="article-1",
            evidence_refs=["https://example.com/filing.pdf"],
        )
    with pytest.raises(ValueError, match="exact source binding"):
        validate_source_binding_coverage(
            binding_set,
            task_id="article-1",
            evidence_refs=[],
        )
    with pytest.raises(ValueError, match="must be exact"):
        validate_source_binding_coverage(
            binding_set,
            task_id="article-1",
            evidence_refs=[binding.source_ref, "financial-source://src_" + "b" * 24 + "/v0001-" + "c" * 12],
        )
    with pytest.raises(ValueError, match="does not match"):
        validate_source_binding_coverage(
            binding_set,
            task_id="article-2",
            evidence_refs=[binding.source_ref],
        )

    record2 = _record(source_id="src_" + "b" * 24)
    binding2 = bind_source_version(
        record2,
        version_id=record2.current_version_id,
        task_id="article-1",
    )
    binding_set_with_unused = SourceBindingSet(
        task_id="article-1",
        research_revision=3,
        private_research_brief_sha256="a" * 64,
        research_package_sha256="b" * 64,
        admitted_at=BASE + timedelta(days=2),
        bindings=(binding, binding2),
    )
    with pytest.raises(ValueError, match="unused"):
        validate_source_binding_coverage(
            binding_set_with_unused,
            task_id="article-1",
            evidence_refs=[binding.source_ref],
        )


def test_source_binding_rejects_version_id_digest_mismatch():
    record = _record()
    binding = bind_source_version(
        record,
        version_id=record.current_version_id,
        task_id="article-1",
    )
    raw = binding.model_dump()
    raw["version_id"] = "v0001-" + "f" * 12
    raw["source_ref"] = f"financial-source://{binding.source_id}/{raw['version_id']}"

    with pytest.raises(ValidationError, match="digest suffix must match"):
        type(binding).model_validate(raw)


def test_binding_set_rejects_cross_task_and_duplicate_bindings():
    record = _record()
    binding = bind_source_version(
        record,
        version_id=record.current_version_id,
        task_id="article-1",
    )
    with pytest.raises(ValidationError, match="belong to the binding-set task_id"):
        SourceBindingSet(
            task_id="article-2",
            research_revision=1,
            private_research_brief_sha256="a" * 64,
            admitted_at=BASE + timedelta(days=2),
            bindings=(binding,),
        )
    with pytest.raises(ValidationError, match="duplicate source_ref"):
        SourceBindingSet(
            task_id="article-1",
            research_revision=1,
            private_research_brief_sha256="a" * 64,
            admitted_at=BASE + timedelta(days=2),
            bindings=(binding, binding),
        )
