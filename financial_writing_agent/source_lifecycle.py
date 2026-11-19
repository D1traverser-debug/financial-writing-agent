from __future__ import annotations

import re
from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator

from .schemas import StrictModel


SourceType = Literal[
    "USER_UPLOAD",
    "PUBLIC_PRIMARY_DOCUMENT",
    "NEWS_MEDIA",
    "DATASET",
    "OTHER",
]
SourceStatus = Literal["ACTIVE", "RETIRED", "BLOCKED"]
SourceScope = Literal["GLOBAL_REUSABLE", "TASK_ONLY"]
VersionStatus = Literal["AVAILABLE", "QUARANTINED", "MISSING"]
StoragePolicy = Literal["RAW_PRESERVED", "METADATA_AND_EXCERPT_ONLY", "LINK_ONLY"]
RightsBasis = Literal["USER_PROVIDED", "PUBLIC_PRIMARY", "LICENSED", "METADATA_ONLY", "UNKNOWN"]

_SOURCE_ID = re.compile(r"^src_[a-f0-9]{24}$")
_VERSION_ID = re.compile(r"^v(?P<sequence>[0-9]{4,})-(?P<digest>[a-f0-9]{12})$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


def _require_aware(value: datetime, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")


def source_reference(source_id: str, version_id: str) -> str:
    if _SOURCE_ID.fullmatch(source_id) is None:
        raise ValueError("source_id must be an opaque src_ identifier")
    if _VERSION_ID.fullmatch(version_id) is None:
        raise ValueError("version_id must be vNNNN-<raw_sha256_prefix>")
    return f"financial-source://{source_id}/{version_id}"


class DriveObjectReference(StrictModel):
    folder_id: str = Field(min_length=1)
    file_id: str = Field(min_length=1)
    revision_id: str = Field(min_length=1)
    media_type: str = Field(min_length=1)
    size_bytes: int = Field(gt=0)
    raw_sha256: str
    normalized_text_sha256: str
    extractor_name: str = Field(min_length=1)
    extractor_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_digests(self):
        for field in ("raw_sha256", "normalized_text_sha256"):
            if _SHA256.fullmatch(getattr(self, field)) is None:
                raise ValueError(f"{field} must be a lowercase SHA-256 digest")
        return self


class SourceVersion(StrictModel):
    version_id: str
    created_at: datetime
    published_at: datetime | None = None
    retrieved_at: datetime
    source_family: str = Field(min_length=1)
    storage_policy: StoragePolicy
    rights_basis: RightsBasis
    status: VersionStatus = "AVAILABLE"
    drive_object: DriveObjectReference

    @model_validator(mode="after")
    def validate_version_identity_and_rights(self):
        match = _VERSION_ID.fullmatch(self.version_id)
        if match is None:
            raise ValueError("version_id must be vNNNN-<raw_sha256_prefix>")
        if match.group("digest") != self.drive_object.raw_sha256[:12]:
            raise ValueError("version_id digest suffix must match the original Drive object")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.retrieved_at, "retrieved_at")
        if self.published_at is not None:
            _require_aware(self.published_at, "published_at")
        if self.created_at < self.retrieved_at:
            raise ValueError("version creation cannot precede source retrieval")
        if (
            self.storage_policy == "RAW_PRESERVED"
            and self.rights_basis not in {"USER_PROVIDED", "PUBLIC_PRIMARY", "LICENSED"}
        ):
            raise ValueError("RAW_PRESERVED requires user-provided, public-primary, or licensed rights")
        return self


class SourceRecord(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    domain_id: Literal["financial_writing"] = "financial_writing"
    source_id: str
    source_type: SourceType
    title: str = Field(min_length=1)
    publisher: str = ""
    canonical_url: str | None = None
    scope: SourceScope
    task_id: str | None = None
    status: SourceStatus = "ACTIVE"
    created_at: datetime
    updated_at: datetime
    current_version_id: str | None = None
    versions: list[SourceVersion] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_source_record(self):
        if _SOURCE_ID.fullmatch(self.source_id) is None:
            raise ValueError("source_id must be an opaque src_ identifier")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.updated_at, "updated_at")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot precede created_at")
        if self.scope == "TASK_ONLY" and not self.task_id:
            raise ValueError("TASK_ONLY source requires task_id")
        if self.scope == "GLOBAL_REUSABLE" and self.task_id is not None:
            raise ValueError("GLOBAL_REUSABLE source must not bind to one task_id")

        version_ids = [item.version_id for item in self.versions]
        if len(version_ids) != len(set(version_ids)):
            raise ValueError("source version IDs must be unique")
        sequences = [
            int(_VERSION_ID.fullmatch(item.version_id).group("sequence"))
            for item in self.versions
        ]
        if sequences != sorted(sequences):
            raise ValueError("source versions must be ordered by ascending sequence")
        if any(right != left + 1 for left, right in zip(sequences, sequences[1:])):
            raise ValueError("source version sequence must be contiguous")
        if self.current_version_id not in version_ids:
            raise ValueError("current_version_id must identify an existing immutable version")
        current = next(item for item in self.versions if item.version_id == self.current_version_id)
        if self.status == "ACTIVE" and current.status != "AVAILABLE":
            raise ValueError("ACTIVE source must point to an AVAILABLE current version")
        if self.source_type == "NEWS_MEDIA":
            if any(
                item.storage_policy == "RAW_PRESERVED"
                and item.rights_basis not in {"USER_PROVIDED", "LICENSED"}
                for item in self.versions
            ):
                raise ValueError("full news-media preservation requires user-provided or licensed rights")
        return self


class SourceBinding(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    task_id: str = Field(min_length=1)
    source_id: str
    version_id: str
    source_ref: str
    drive_folder_id: str = Field(min_length=1)
    drive_file_id: str = Field(min_length=1)
    drive_revision_id: str = Field(min_length=1)
    source_type: SourceType
    publisher: str = ""
    canonical_url: str | None = None
    raw_sha256: str
    normalized_text_sha256: str
    source_family: str = Field(min_length=1)
    retrieved_at: datetime
    published_at: datetime | None = None
    media_type: str = Field(min_length=1)
    storage_policy: StoragePolicy
    drive_file_size_bytes: int = Field(gt=0)
    extractor_name: str = Field(min_length=1)
    extractor_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_exact_binding(self):
        if self.source_ref != source_reference(self.source_id, self.version_id):
            raise ValueError("source_ref must bind the exact source_id and version_id")
        for field in ("raw_sha256", "normalized_text_sha256"):
            if _SHA256.fullmatch(getattr(self, field)) is None:
                raise ValueError(f"{field} must be a lowercase SHA-256 digest")
        _require_aware(self.retrieved_at, "retrieved_at")
        if self.published_at is not None:
            _require_aware(self.published_at, "published_at")
        return self


def create_source_record(
    *,
    source_id: str,
    source_type: SourceType,
    title: str,
    publisher: str,
    canonical_url: str | None,
    scope: SourceScope,
    task_id: str | None,
    first_version: SourceVersion,
) -> SourceRecord:
    match = _VERSION_ID.fullmatch(first_version.version_id)
    if match is None or int(match.group("sequence")) != 1:
        raise ValueError("first source version must use sequence v0001")
    return SourceRecord(
        source_id=source_id,
        source_type=source_type,
        title=title,
        publisher=publisher,
        canonical_url=canonical_url,
        scope=scope,
        task_id=task_id,
        status="ACTIVE",
        created_at=first_version.created_at,
        updated_at=first_version.created_at,
        current_version_id=first_version.version_id,
        versions=[first_version],
    )


def append_source_version(record: SourceRecord, version: SourceVersion) -> SourceRecord:
    if record.status != "ACTIVE":
        raise ValueError("only ACTIVE sources can receive a new version")
    if version.version_id in {item.version_id for item in record.versions}:
        raise ValueError("source versions are immutable and cannot be overwritten")
    match = _VERSION_ID.fullmatch(version.version_id)
    expected = max(
        int(_VERSION_ID.fullmatch(item.version_id).group("sequence"))
        for item in record.versions
    ) + 1
    if match is None or int(match.group("sequence")) != expected:
        raise ValueError("new source version must use the next contiguous sequence")
    if version.created_at < record.updated_at:
        raise ValueError("new source version cannot predate the current source record")
    return record.model_copy(
        update={
            "versions": [*record.versions, version],
            "current_version_id": version.version_id,
            "updated_at": version.created_at,
        }
    )


def retire_source(record: SourceRecord, *, at: datetime) -> SourceRecord:
    if record.status != "ACTIVE":
        raise ValueError("only ACTIVE sources can be retired")
    _require_aware(at, "at")
    if at < record.updated_at:
        raise ValueError("retirement time cannot precede the current source record")
    return record.model_copy(update={"status": "RETIRED", "updated_at": at})


def restore_source(record: SourceRecord, *, at: datetime) -> SourceRecord:
    if record.status != "RETIRED":
        raise ValueError("only RETIRED sources can be restored")
    _require_aware(at, "at")
    if at < record.updated_at:
        raise ValueError("restore time cannot precede the current source record")
    current = next(item for item in record.versions if item.version_id == record.current_version_id)
    if current.status != "AVAILABLE":
        raise ValueError("source cannot be restored while its current Drive version is unavailable")
    return record.model_copy(update={"status": "ACTIVE", "updated_at": at})


def bind_source_version(record: SourceRecord, *, version_id: str, task_id: str) -> SourceBinding:
    if record.status != "ACTIVE":
        raise ValueError("retired or blocked sources cannot be newly bound")
    if record.scope == "TASK_ONLY" and task_id != record.task_id:
        raise ValueError("TASK_ONLY source cannot be reused by another task")
    version = next((item for item in record.versions if item.version_id == version_id), None)
    if version is None:
        raise ValueError("requested source version does not exist")
    if version.status != "AVAILABLE":
        raise ValueError("unavailable source versions cannot be newly bound")
    return SourceBinding(
        task_id=task_id,
        source_id=record.source_id,
        version_id=version.version_id,
        source_ref=source_reference(record.source_id, version.version_id),
        drive_folder_id=version.drive_object.folder_id,
        drive_file_id=version.drive_object.file_id,
        drive_revision_id=version.drive_object.revision_id,
        source_type=record.source_type,
        publisher=record.publisher,
        canonical_url=record.canonical_url,
        raw_sha256=version.drive_object.raw_sha256,
        normalized_text_sha256=version.drive_object.normalized_text_sha256,
        source_family=version.source_family,
        retrieved_at=version.retrieved_at,
        published_at=version.published_at,
        media_type=version.drive_object.media_type,
        storage_policy=version.storage_policy,
        drive_file_size_bytes=version.drive_object.size_bytes,
        extractor_name=version.drive_object.extractor_name,
        extractor_version=version.drive_object.extractor_version,
    )
