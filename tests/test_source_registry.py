from datetime import datetime, timedelta, timezone
import hashlib

import pytest

from financial_writing_agent.source_lifecycle import (
    DriveObjectReference,
    SourceVersion,
    append_source_version,
    create_source_record,
    mint_version_id,
    retire_source,
    restore_source,
)
from financial_writing_agent.source_registry import (
    EVENTS_HEADERS,
    SOURCES_HEADERS,
    VERSIONS_HEADERS,
    SourceRegistryError,
    registry_row_values,
    sheet_values_to_rows,
    source_event_row,
    source_record_from_registry_rows,
    source_records_from_registry_snapshot,
    source_registry_rows,
)


BASE = datetime(2026, 11, 19, 10, 0, tzinfo=timezone.utc)


def _version(sequence, payload, *, file_id, folder_id):
    text = payload.decode("utf-8")
    return SourceVersion(
        version_id=mint_version_id(sequence, payload),
        created_at=BASE + timedelta(minutes=sequence),
        retrieved_at=BASE + timedelta(minutes=sequence - 1),
        source_family="issuer-primary",
        storage_policy="RAW_PRESERVED",
        rights_basis="PUBLIC_PRIMARY",
        drive_object=DriveObjectReference(
            folder_id=folder_id,
            file_id=file_id,
            revision_id=None,
            media_type="text/plain",
            size_bytes=len(payload),
            raw_sha256=hashlib.sha256(payload).hexdigest(),
            normalized_text_sha256=hashlib.sha256(text.encode()).hexdigest(),
            extractor_name="utf8",
            extractor_version="1",
        ),
    )


def _event(action_id, source_id, operation, at, prior_status, resulting_status, prior_version, resulting_version, payload_sha256=None):
    return source_event_row(
        action_id=action_id,
        source_id=source_id,
        operation=operation,
        occurred_at=at,
        actor="owner",
        prior_status=prior_status,
        resulting_status=resulting_status,
        prior_version_id=prior_version,
        resulting_version_id=resulting_version,
        payload_sha256=payload_sha256,
    )


def test_registry_round_trip_tracks_append_only_versions_and_lifecycle_events():
    v1 = _version(1, b"version one", file_id="file-v1", folder_id="version-folder-v1")
    record = create_source_record(
        source_id="src_" + "a" * 24,
        source_type="PUBLIC_PRIMARY_DOCUMENT",
        title="Issuer filing",
        publisher="Issuer",
        canonical_url="https://example.com/filing",
        scope="GLOBAL_REUSABLE",
        task_id=None,
        first_version=v1,
    )
    source_row, _ = source_registry_rows(record, source_folder_id="source-folder")
    v2 = _version(2, b"version two", file_id="file-v2", folder_id="version-folder-v2")
    updated = append_source_version(record, v2)
    _, version_rows = source_registry_rows(updated, source_folder_id="source-folder")

    events = [
        _event("evt-create", record.source_id, "CREATE", record.created_at, None, "ACTIVE", None, v1.version_id, v1.drive_object.raw_sha256),
        _event("evt-version", record.source_id, "ADD_VERSION", updated.updated_at, "ACTIVE", "ACTIVE", v1.version_id, v2.version_id, v2.drive_object.raw_sha256),
    ]
    retired = retire_source(updated, at=BASE + timedelta(minutes=5))
    events.append(_event("evt-retire", record.source_id, "RETIRE", retired.updated_at, "ACTIVE", "RETIRED", v2.version_id, v2.version_id))
    restored = restore_source(retired, at=BASE + timedelta(minutes=6))
    events.append(_event("evt-restore", record.source_id, "RESTORE", restored.updated_at, "RETIRED", "ACTIVE", v2.version_id, v2.version_id))

    rebuilt = source_record_from_registry_rows(source_row, version_rows, events)
    assert rebuilt.source_id == restored.source_id
    assert rebuilt.status == "ACTIVE"
    assert rebuilt.current_version_id == v2.version_id
    assert [item.version_id for item in rebuilt.versions] == [v1.version_id, v2.version_id]
    assert rebuilt.updated_at == restored.updated_at


def test_registry_requires_create_event_and_rejects_unknown_version():
    v1 = _version(1, b"version one", file_id="file-v1", folder_id="version-folder-v1")
    record = create_source_record(
        source_id="src_" + "a" * 24,
        source_type="PUBLIC_PRIMARY_DOCUMENT",
        title="Issuer filing",
        publisher="Issuer",
        canonical_url=None,
        scope="GLOBAL_REUSABLE",
        task_id=None,
        first_version=v1,
    )
    source_row, version_rows = source_registry_rows(record, source_folder_id="source-folder")
    with pytest.raises(SourceRegistryError, match="CREATE event"):
        source_record_from_registry_rows(source_row, version_rows, [])
    wrong = _event("evt-create", record.source_id, "CREATE", record.created_at, None, "ACTIVE", None, "v0001-" + "f" * 12, "f" * 64)
    with pytest.raises(SourceRegistryError, match="activate the first"):
        source_record_from_registry_rows(source_row, version_rows, [wrong])


def test_registry_rejects_out_of_order_or_invalid_lifecycle_transition():
    v1 = _version(1, b"version one", file_id="file-v1", folder_id="version-folder-v1")
    record = create_source_record(
        source_id="src_" + "a" * 24,
        source_type="PUBLIC_PRIMARY_DOCUMENT",
        title="Issuer filing",
        publisher="Issuer",
        canonical_url=None,
        scope="GLOBAL_REUSABLE",
        task_id=None,
        first_version=v1,
    )
    source_row, version_rows = source_registry_rows(record, source_folder_id="source-folder")
    create = _event("evt-create", record.source_id, "CREATE", record.created_at, None, "ACTIVE", None, v1.version_id, v1.drive_object.raw_sha256)
    invalid_retire = _event("evt-retire", record.source_id, "RETIRE", BASE + timedelta(minutes=2), "RETIRED", "RETIRED", v1.version_id, v1.version_id)
    with pytest.raises(SourceRegistryError, match="prior state"):
        source_record_from_registry_rows(source_row, version_rows, [create, invalid_retire])


def test_sheet_snapshot_requires_exact_headers_and_maps_values_by_header():
    assert len(SOURCES_HEADERS) == 14
    assert len(VERSIONS_HEADERS) == 22
    assert len(EVENTS_HEADERS) == 12
    rows = sheet_values_to_rows(
        [list(SOURCES_HEADERS), ["src_" + "a" * 24, "Title"]],
        expected_headers=SOURCES_HEADERS,
    )
    assert rows[0]["source_id"] == "src_" + "a" * 24
    assert rows[0]["title"] == "Title"
    with pytest.raises(SourceRegistryError, match="headers"):
        sheet_values_to_rows([["title", "source_id"]], expected_headers=SOURCES_HEADERS)


def test_registry_row_values_preserves_exact_header_order_and_empty_cells():
    row = {"source_id": "src_" + "a" * 24, "title": "Issuer filing", "publisher": None}
    assert registry_row_values(["source_id", "title", "publisher", "notes"], row) == [
        "src_" + "a" * 24, "Issuer filing", "", ""
    ]


def test_full_registry_snapshot_rebuilds_sources_from_three_tabs():
    v1 = _version(1, b"version one", file_id="file-v1", folder_id="version-folder-v1")
    record = create_source_record(
        source_id="src_" + "a" * 24,
        source_type="PUBLIC_PRIMARY_DOCUMENT",
        title="Issuer filing",
        publisher="Issuer",
        canonical_url=None,
        scope="GLOBAL_REUSABLE",
        task_id=None,
        first_version=v1,
    )
    source_row, version_rows = source_registry_rows(record, source_folder_id="source-folder")
    event = _event("evt-create", record.source_id, "CREATE", record.created_at, None, "ACTIVE", None, v1.version_id, v1.drive_object.raw_sha256)
    sources_values = [list(SOURCES_HEADERS), registry_row_values(SOURCES_HEADERS, source_row)]
    versions_values = [list(VERSIONS_HEADERS), *[registry_row_values(VERSIONS_HEADERS, row) for row in version_rows]]
    events_values = [list(EVENTS_HEADERS), registry_row_values(EVENTS_HEADERS, event)]
    rebuilt = source_records_from_registry_snapshot(sources_values, versions_values, events_values)
    assert len(rebuilt) == 1
    assert rebuilt[0].source_id == record.source_id
    assert rebuilt[0].current_version_id == record.current_version_id


def test_registry_rejects_version_sequence_and_initial_metadata_drift():
    v1 = _version(1, b"version one", file_id="file-v1", folder_id="version-folder-v1")
    record = create_source_record(
        source_id="src_" + "a" * 24,
        source_type="PUBLIC_PRIMARY_DOCUMENT",
        title="Issuer filing",
        publisher="Issuer",
        canonical_url=None,
        scope="GLOBAL_REUSABLE",
        task_id=None,
        first_version=v1,
    )
    source_row, version_rows = source_registry_rows(record, source_folder_id="source-folder")
    event = _event("evt-create", record.source_id, "CREATE", record.created_at, None, "ACTIVE", None, v1.version_id, v1.drive_object.raw_sha256)

    wrong_sequence = [dict(version_rows[0], sequence="2")]
    with pytest.raises(SourceRegistryError, match="sequence column"):
        source_record_from_registry_rows(source_row, wrong_sequence, [event])

    wrong_rights = dict(source_row, initial_rights_basis="LICENSED")
    with pytest.raises(SourceRegistryError, match="initial_rights_basis"):
        source_record_from_registry_rows(wrong_rights, version_rows, [event])


def test_registry_rejects_missing_actor_and_event_before_version_creation():
    v1 = _version(1, b"version one", file_id="file-v1", folder_id="version-folder-v1")
    record = create_source_record(
        source_id="src_" + "a" * 24,
        source_type="PUBLIC_PRIMARY_DOCUMENT",
        title="Issuer filing",
        publisher="Issuer",
        canonical_url=None,
        scope="GLOBAL_REUSABLE",
        task_id=None,
        first_version=v1,
    )
    source_row, version_rows = source_registry_rows(record, source_folder_id="source-folder")
    missing_actor = _event("evt-create", record.source_id, "CREATE", record.created_at, None, "ACTIVE", None, v1.version_id, v1.drive_object.raw_sha256)
    missing_actor["actor"] = ""
    with pytest.raises(SourceRegistryError, match="actor"):
        source_record_from_registry_rows(source_row, version_rows, [missing_actor])

    early_create = _event("evt-create", record.source_id, "CREATE", BASE, None, "ACTIVE", None, v1.version_id, v1.drive_object.raw_sha256)
    with pytest.raises(SourceRegistryError, match="predates"):
        source_record_from_registry_rows(source_row, version_rows, [early_create])


def test_registry_snapshot_rejects_orphan_rows_and_duplicate_global_ids():
    v1 = _version(1, b"version one", file_id="file-v1", folder_id="version-folder-v1")
    record = create_source_record(
        source_id="src_" + "a" * 24,
        source_type="PUBLIC_PRIMARY_DOCUMENT",
        title="Issuer filing",
        publisher="Issuer",
        canonical_url=None,
        scope="GLOBAL_REUSABLE",
        task_id=None,
        first_version=v1,
    )
    source_row, version_rows = source_registry_rows(record, source_folder_id="source-folder")
    event = _event("evt-create", record.source_id, "CREATE", record.created_at, None, "ACTIVE", None, v1.version_id, v1.drive_object.raw_sha256)
    sources_values = [list(SOURCES_HEADERS), registry_row_values(SOURCES_HEADERS, source_row)]
    versions_values = [list(VERSIONS_HEADERS), *[registry_row_values(VERSIONS_HEADERS, row) for row in version_rows]]
    events_values = [list(EVENTS_HEADERS), registry_row_values(EVENTS_HEADERS, event)]

    orphan = dict(version_rows[0], source_id="src_" + "b" * 24)
    orphan_versions = [list(VERSIONS_HEADERS), registry_row_values(VERSIONS_HEADERS, orphan)]
    with pytest.raises(SourceRegistryError, match="orphan source_id"):
        source_records_from_registry_snapshot(sources_values, orphan_versions, events_values)

    duplicate_event = dict(event, action_id="evt-create")
    duplicate_events = [list(EVENTS_HEADERS), registry_row_values(EVENTS_HEADERS, event), registry_row_values(EVENTS_HEADERS, duplicate_event)]
    with pytest.raises(SourceRegistryError, match="duplicate action_id"):
        source_records_from_registry_snapshot(sources_values, versions_values, duplicate_events)
