from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Mapping, Sequence

from .source_lifecycle import DriveObjectReference, SourceRecord, SourceVersion


SOURCES_HEADERS = (
    "source_id", "title", "publisher", "canonical_url", "source_type", "scope",
    "task_id", "created_at", "source_folder_id", "initial_rights_basis",
    "initial_storage_policy", "description", "tags", "notes",
)
VERSIONS_HEADERS = (
    "source_id", "version_id", "sequence", "drive_file_id", "drive_revision_id",
    "file_name", "mime_type", "size_bytes", "stored_payload_sha256",
    "retained_text_sha256", "source_family", "published_at", "retrieved_at",
    "storage_policy", "rights_basis", "extractor_name", "extractor_version",
    "status", "drive_url", "change_note", "created_at", "drive_folder_id",
)
EVENTS_HEADERS = (
    "action_id", "source_id", "operation", "occurred_at", "actor", "prior_status",
    "resulting_status", "prior_version_id", "resulting_version_id",
    "payload_sha256", "reason", "related_task_id",
)
_VERSION_PATTERN = re.compile(r"^v(?P<sequence>[0-9]{4,})-(?P<digest>[a-f0-9]{12})$")


class SourceRegistryError(ValueError):
    """A Drive registry snapshot is incomplete, inconsistent or malformed."""


def _text(row: Mapping[str, Any], key: str, *, required: bool = True) -> str | None:
    value = row.get(key)
    if value is None or not str(value).strip():
        if required:
            raise SourceRegistryError(f"registry field {key} is required")
        return None
    return str(value).strip()


def _integer(row: Mapping[str, Any], key: str) -> int:
    value = row.get(key)
    if isinstance(value, bool):
        raise SourceRegistryError(f"registry field {key} must be an integer")
    try:
        if isinstance(value, int):
            number = value
        elif isinstance(value, float):
            if not value.is_integer():
                raise ValueError
            number = int(value)
        else:
            number = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise SourceRegistryError(f"registry field {key} must be an integer") from exc
    if number < 1:
        raise SourceRegistryError(f"registry field {key} must be positive")
    return number


def _datetime(row: Mapping[str, Any], key: str) -> datetime:
    value = _text(row, key)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SourceRegistryError(f"registry field {key} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SourceRegistryError(f"registry field {key} must include a timezone")
    return parsed


def _optional_datetime(row: Mapping[str, Any], key: str) -> datetime | None:
    if not _text(row, key, required=False):
        return None
    return _datetime(row, key)


def _version_sequence(version_id: str) -> int:
    match = _VERSION_PATTERN.fullmatch(version_id)
    if match is None:
        raise SourceRegistryError("invalid source version ID")
    return int(match.group("sequence"))


def sheet_values_to_rows(
    values: Sequence[Sequence[Any]],
    *,
    expected_headers: Sequence[str],
) -> list[dict[str, str]]:
    """Convert a bounded Google Sheets values response into header-bound rows."""
    if not values:
        raise SourceRegistryError("registry sheet is missing its header row")
    headers = tuple(str(item).strip() for item in values[0])
    if headers != tuple(expected_headers):
        raise SourceRegistryError("registry sheet headers do not match the source-library contract")
    rows: list[dict[str, str]] = []
    for row_number, raw_row in enumerate(values[1:], start=2):
        if len(raw_row) > len(headers):
            raise SourceRegistryError(f"registry row {row_number} has more cells than its header")
        cells = ["" if value is None else str(value) for value in raw_row]
        cells.extend([""] * (len(headers) - len(cells)))
        if not any(cell.strip() for cell in cells):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def _version_from_row(row: Mapping[str, Any]) -> SourceVersion:
    version_id = _text(row, "version_id")
    if _integer(row, "sequence") != _version_sequence(version_id):
        raise SourceRegistryError("source version sequence column does not match version_id")
    revision_id = _text(row, "drive_revision_id", required=False)
    drive_object = DriveObjectReference(
        folder_id=_text(row, "drive_folder_id"),
        file_id=_text(row, "drive_file_id"),
        revision_id=revision_id,
        media_type=_text(row, "mime_type"),
        size_bytes=_integer(row, "size_bytes"),
        raw_sha256=_text(row, "stored_payload_sha256"),
        normalized_text_sha256=_text(row, "retained_text_sha256"),
        extractor_name=_text(row, "extractor_name"),
        extractor_version=_text(row, "extractor_version"),
    )
    return SourceVersion(
        version_id=version_id,
        created_at=_datetime(row, "created_at"),
        published_at=_optional_datetime(row, "published_at"),
        retrieved_at=_datetime(row, "retrieved_at"),
        source_family=_text(row, "source_family"),
        storage_policy=_text(row, "storage_policy"),
        rights_basis=_text(row, "rights_basis"),
        status=_text(row, "status"),
        drive_object=drive_object,
    )


def source_record_from_registry_rows(
    source_row: Mapping[str, Any],
    version_rows: Sequence[Mapping[str, Any]],
    event_rows: Sequence[Mapping[str, Any]],
) -> SourceRecord:
    """Rebuild one source from Sources, Versions and Events rows in sheet order."""
    source_id = _text(source_row, "source_id")
    versions = [
        _version_from_row(row)
        for row in version_rows
        if _text(row, "source_id") == source_id
    ]
    versions.sort(key=lambda item: _version_sequence(item.version_id))
    if not versions:
        raise SourceRegistryError("source has no available version history")
    if _text(source_row, "initial_rights_basis") != versions[0].rights_basis:
        raise SourceRegistryError("Sources initial_rights_basis disagrees with the first version")
    if _text(source_row, "initial_storage_policy") != versions[0].storage_policy:
        raise SourceRegistryError("Sources initial_storage_policy disagrees with the first version")
    sequences = [_version_sequence(item.version_id) for item in versions]
    if sequences != list(range(1, len(sequences) + 1)):
        raise SourceRegistryError("source version history must be contiguous from v0001")

    events = [row for row in event_rows if _text(row, "source_id") == source_id]
    if not events:
        raise SourceRegistryError("source lifecycle must begin with a CREATE event")

    status = "ACTIVE"
    current_version_id = versions[0].version_id
    updated_at = _datetime(source_row, "created_at")
    known_versions = {item.version_id: item for item in versions}
    seen_actions: set[str] = set()

    for index, event in enumerate(events):
        action_id = _text(event, "action_id")
        _text(event, "actor")
        if action_id in seen_actions:
            raise SourceRegistryError("source lifecycle action_id must be unique")
        seen_actions.add(action_id)
        operation = _text(event, "operation")
        prior_status = _text(event, "prior_status", required=False)
        resulting_status = _text(event, "resulting_status")
        prior_version_id = _text(event, "prior_version_id", required=False)
        resulting_version_id = _text(event, "resulting_version_id")
        occurred_at = _datetime(event, "occurred_at")
        if index == 0 and occurred_at < versions[0].created_at:
            raise SourceRegistryError("CREATE event predates the first source version")
        if occurred_at < updated_at:
            raise SourceRegistryError("source lifecycle event time moved backwards")

        if index == 0:
            if operation != "CREATE":
                raise SourceRegistryError("source lifecycle must begin with a CREATE event")
            if prior_status is not None or prior_version_id is not None:
                raise SourceRegistryError("CREATE cannot have a prior status or version")
            if resulting_status != "ACTIVE" or resulting_version_id != versions[0].version_id:
                raise SourceRegistryError("CREATE must activate the first source version")
        else:
            if prior_status != status or prior_version_id != current_version_id:
                raise SourceRegistryError("source lifecycle prior state does not match the previous event")
            if operation == "ADD_VERSION":
                if status != "ACTIVE" or resulting_status != "ACTIVE":
                    raise SourceRegistryError("ADD_VERSION requires ACTIVE to ACTIVE")
                if resulting_version_id not in known_versions:
                    raise SourceRegistryError("ADD_VERSION points to an unknown source version")
                if _version_sequence(resulting_version_id) != _version_sequence(current_version_id) + 1:
                    raise SourceRegistryError("ADD_VERSION must append the next contiguous version")
                if occurred_at < known_versions[resulting_version_id].created_at:
                    raise SourceRegistryError("ADD_VERSION event predates its source version")
            elif operation == "RETIRE":
                if status != "ACTIVE" or resulting_status != "RETIRED" or resulting_version_id != current_version_id:
                    raise SourceRegistryError("RETIRE requires ACTIVE to RETIRED without changing the current version")
            elif operation == "RESTORE":
                if status != "RETIRED" or resulting_status != "ACTIVE" or resulting_version_id != current_version_id:
                    raise SourceRegistryError("RESTORE requires RETIRED to ACTIVE without changing the current version")
            elif operation == "BLOCK":
                if status != "ACTIVE" or resulting_status != "BLOCKED" or resulting_version_id != current_version_id:
                    raise SourceRegistryError("BLOCK requires ACTIVE to BLOCKED without changing the current version")
            else:
                raise SourceRegistryError(f"unsupported source lifecycle operation: {operation}")

        if operation in {"CREATE", "ADD_VERSION"}:
            payload_sha = _text(event, "payload_sha256")
            if payload_sha != known_versions[resulting_version_id].drive_object.raw_sha256:
                raise SourceRegistryError("source lifecycle payload digest does not match the admitted version")
        status = resulting_status
        current_version_id = resulting_version_id
        updated_at = occurred_at

    if current_version_id != versions[-1].version_id:
        raise SourceRegistryError("source lifecycle must admit the newest stored version")

    return SourceRecord(
        source_id=source_id,
        source_type=_text(source_row, "source_type"),
        title=_text(source_row, "title"),
        publisher=_text(source_row, "publisher", required=False) or "",
        canonical_url=_text(source_row, "canonical_url", required=False),
        scope=_text(source_row, "scope"),
        task_id=_text(source_row, "task_id", required=False),
        status=status,
        created_at=_datetime(source_row, "created_at"),
        updated_at=updated_at,
        current_version_id=current_version_id,
        versions=tuple(versions),
    )


def source_records_from_registry_snapshot(
    sources_values: Sequence[Sequence[Any]],
    versions_values: Sequence[Sequence[Any]],
    events_values: Sequence[Sequence[Any]],
) -> tuple[SourceRecord, ...]:
    sources = sheet_values_to_rows(sources_values, expected_headers=SOURCES_HEADERS)
    versions = sheet_values_to_rows(versions_values, expected_headers=VERSIONS_HEADERS)
    events = sheet_values_to_rows(events_values, expected_headers=EVENTS_HEADERS)
    source_ids = [_text(row, "source_id") for row in sources]
    if len(source_ids) != len(set(source_ids)):
        raise SourceRegistryError("Sources contains duplicate source_id rows")
    source_id_set = set(source_ids)
    version_source_ids = {_text(row, "source_id") for row in versions}
    event_source_ids = {_text(row, "source_id") for row in events}
    if not version_source_ids.issubset(source_id_set):
        raise SourceRegistryError("Versions contains orphan source_id rows")
    if not event_source_ids.issubset(source_id_set):
        raise SourceRegistryError("Events contains orphan source_id rows")
    version_keys = [(_text(row, "source_id"), _text(row, "version_id")) for row in versions]
    if len(version_keys) != len(set(version_keys)):
        raise SourceRegistryError("Versions contains duplicate source/version rows")
    file_ids = [_text(row, "drive_file_id") for row in versions]
    if len(file_ids) != len(set(file_ids)):
        raise SourceRegistryError("Drive file IDs must be unique across source versions")
    action_ids = [_text(row, "action_id") for row in events]
    if len(action_ids) != len(set(action_ids)):
        raise SourceRegistryError("Events contains duplicate action_id rows")
    return tuple(
        source_record_from_registry_rows(source_row, versions, events)
        for source_row in sources
    )


def source_registry_rows(
    record: SourceRecord,
    *,
    source_folder_id: str,
    description: str = "",
    tags: str = "",
    notes: str = "",
    version_annotations: Mapping[str, Mapping[str, str]] | None = None,
) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Serialize one source identity row and its append-only immutable version rows."""
    annotations = version_annotations or {}
    source_row = {
        "source_id": record.source_id,
        "title": record.title,
        "publisher": record.publisher,
        "canonical_url": record.canonical_url or "",
        "source_type": record.source_type,
        "scope": record.scope,
        "task_id": record.task_id or "",
        "created_at": record.created_at.isoformat(),
        "source_folder_id": source_folder_id,
        "initial_rights_basis": record.versions[0].rights_basis,
        "initial_storage_policy": record.versions[0].storage_policy,
        "description": description,
        "tags": tags,
        "notes": notes,
    }
    version_rows: list[dict[str, str]] = []
    for version in record.versions:
        drive = version.drive_object
        annotation = annotations.get(version.version_id, {})
        version_rows.append({
            "source_id": record.source_id,
            "version_id": version.version_id,
            "sequence": str(_version_sequence(version.version_id)),
            "drive_file_id": drive.file_id,
            "drive_revision_id": drive.revision_id or "",
            "file_name": annotation.get("file_name", ""),
            "mime_type": drive.media_type,
            "size_bytes": str(drive.size_bytes),
            "stored_payload_sha256": drive.raw_sha256,
            "retained_text_sha256": drive.normalized_text_sha256,
            "source_family": version.source_family,
            "published_at": version.published_at.isoformat() if version.published_at else "",
            "retrieved_at": version.retrieved_at.isoformat(),
            "storage_policy": version.storage_policy,
            "rights_basis": version.rights_basis,
            "extractor_name": drive.extractor_name,
            "extractor_version": drive.extractor_version,
            "status": version.status,
            "drive_url": annotation.get("drive_url", ""),
            "change_note": annotation.get("change_note", ""),
            "created_at": version.created_at.isoformat(),
            "drive_folder_id": drive.folder_id,
        })
    return source_row, version_rows


def source_event_row(
    *,
    action_id: str,
    source_id: str,
    operation: str,
    occurred_at: datetime,
    actor: str,
    prior_status: str | None,
    resulting_status: str,
    prior_version_id: str | None,
    resulting_version_id: str,
    payload_sha256: str | None = None,
    reason: str = "",
    related_task_id: str | None = None,
) -> dict[str, str]:
    if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
        raise SourceRegistryError("source event time must include a timezone")
    if operation not in {"CREATE", "ADD_VERSION", "RETIRE", "RESTORE", "BLOCK"}:
        raise SourceRegistryError("unsupported source lifecycle operation")
    if not action_id.strip() or not source_id.strip() or not actor.strip():
        raise SourceRegistryError("source event action_id, source_id and actor are required")
    return {
        "action_id": action_id,
        "source_id": source_id,
        "operation": operation,
        "occurred_at": occurred_at.isoformat(),
        "actor": actor,
        "prior_status": prior_status or "",
        "resulting_status": resulting_status,
        "prior_version_id": prior_version_id or "",
        "resulting_version_id": resulting_version_id,
        "payload_sha256": payload_sha256 or "",
        "reason": reason,
        "related_task_id": related_task_id or "",
    }


def registry_row_values(headers: Sequence[str], row: Mapping[str, Any]) -> list[str]:
    """Return values in the exact current Google Sheets header order."""
    if len(headers) != len(set(headers)):
        raise SourceRegistryError("registry headers must be unique")
    return ["" if row.get(header) is None else str(row[header]) for header in headers]
