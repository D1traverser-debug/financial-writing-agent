from __future__ import annotations

import hashlib
import re
import secrets
from datetime import datetime
from typing import Any, Literal, Mapping

from pydantic import ConfigDict, Field, model_validator

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


def mint_source_id() -> str:
    """Mint an opaque source ID; the registry must still be checked for collision."""
    return "src_" + secrets.token_hex(12)


def mint_version_id(sequence: int, raw_payload: bytes | bytearray | str) -> str:
    """Mint an immutable version ID from the exact bytes that will be stored."""
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        raise ValueError("source version sequence must be a positive integer")
    if isinstance(raw_payload, str):
        payload = raw_payload.encode("utf-8")
    elif isinstance(raw_payload, (bytes, bytearray)):
        payload = bytes(raw_payload)
    else:
        raise TypeError("raw_payload must be bytes, bytearray or text")
    if not payload:
        raise ValueError("empty source payload cannot be versioned")
    return f"v{sequence:04d}-{hashlib.sha256(payload).hexdigest()[:12]}"


def source_reference(source_id: str, version_id: str) -> str:
    if _SOURCE_ID.fullmatch(source_id) is None:
        raise ValueError("source_id must be an opaque src_ identifier")
    if _VERSION_ID.fullmatch(version_id) is None:
        raise ValueError("version_id must be vNNNN-<raw_sha256_prefix>")
    return f"financial-source://{source_id}/{version_id}"


class DriveObjectReference(StrictModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    folder_id: str = Field(min_length=1)
    file_id: str = Field(min_length=1)
    revision_id: str | None = None
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
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

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
            raise ValueError("version_id digest suffix must match the exact stored Drive object")
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
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

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
    current_version_id: str
    versions: tuple[SourceVersion, ...] = Field(min_length=1)

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
        if sequences[0] != 1:
            raise ValueError("source version history must start at v0001")
        if any(right != left + 1 for left, right in zip(sequences, sequences[1:])):
            raise ValueError("source version sequence must be contiguous")
        if self.current_version_id != version_ids[-1]:
            raise ValueError("current_version_id must identify the newest immutable version")
        version_created_at = [item.created_at for item in self.versions]
        if version_created_at != sorted(version_created_at):
            raise ValueError("source version creation times must be ordered")
        drive_file_ids = [item.drive_object.file_id for item in self.versions]
        if len(drive_file_ids) != len(set(drive_file_ids)):
            raise ValueError("each immutable source version must use a new Drive file ID")
        if self.updated_at < self.versions[-1].created_at:
            raise ValueError("updated_at cannot precede the newest source version")
        current = self.versions[-1]
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
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    task_id: str = Field(min_length=1)
    source_id: str
    version_id: str
    source_ref: str
    drive_folder_id: str = Field(min_length=1)
    drive_file_id: str = Field(min_length=1)
    drive_revision_id: str | None = None
    source_type: SourceType
    scope: SourceScope
    source_task_id: str | None = None
    rights_basis: RightsBasis
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
        if self.scope == "TASK_ONLY" and self.source_task_id != self.task_id:
            raise ValueError("TASK_ONLY source binding must preserve and match its owner task_id")
        if self.scope == "GLOBAL_REUSABLE" and self.source_task_id is not None:
            raise ValueError("GLOBAL_REUSABLE source binding must not carry a source_task_id")
        for field in ("raw_sha256", "normalized_text_sha256"):
            if _SHA256.fullmatch(getattr(self, field)) is None:
                raise ValueError(f"{field} must be a lowercase SHA-256 digest")
        version_match = _VERSION_ID.fullmatch(self.version_id)
        if version_match is None or version_match.group("digest") != self.raw_sha256[:12]:
            raise ValueError("source binding version ID digest suffix must match its stored Drive payload")
        _require_aware(self.retrieved_at, "retrieved_at")
        if self.published_at is not None:
            _require_aware(self.published_at, "published_at")
        return self



class SourceBindingSet(StrictModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    task_id: str = Field(min_length=1)
    research_revision: int = Field(ge=1)
    decision_envelope_sha256: str
    private_research_brief_sha256: str
    research_package_sha256: str | None = None
    admitted_at: datetime
    bindings: tuple[SourceBinding, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_task_binding_set(self):
        _require_aware(self.admitted_at, "admitted_at")
        for field in ("decision_envelope_sha256", "private_research_brief_sha256", "research_package_sha256"):
            value = getattr(self, field)
            if value is not None and _SHA256.fullmatch(value) is None:
                raise ValueError(f"{field} must be a lowercase SHA-256 digest")
        if any(binding.task_id != self.task_id for binding in self.bindings):
            raise ValueError("every source binding must belong to the binding-set task_id")
        if any(binding.retrieved_at > self.admitted_at for binding in self.bindings):
            raise ValueError("source binding set cannot be admitted before its source retrieval")
        source_refs = [binding.source_ref for binding in self.bindings]
        if len(source_refs) != len(set(source_refs)):
            raise ValueError("source binding set cannot contain duplicate source_ref entries")
        drive_file_ids = [binding.drive_file_id for binding in self.bindings]
        if len(drive_file_ids) != len(set(drive_file_ids)):
            raise ValueError("source binding set cannot alias one Drive file across source refs")
        return self


_SOURCE_REF_LIST_FIELDS = frozenset({
    "evidence_refs",
    "source_refs",
    "recall_sources",
    "saturation_evidence_refs",
    "supporting_evidence_refs",
    "falsification_or_rejection_refs",
    "architecture_reassessment_refs",
})
_SOURCE_REF_SINGLE_FIELDS = frozenset({"source", "source_ref", "ref"})


def collect_research_source_refs(*artifacts: Mapping[str, Any]) -> list[str]:
    """Collect source-bearing refs from the complete admitted RESEARCH evidence graph.

    User intake URLs and canonical_url metadata are deliberately excluded. The
    provider passes DecisionEnvelope, PrivateResearchBrief, and ResearchPackage
    here before exact task-binding coverage is admitted.
    """
    refs: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if key in _SOURCE_REF_LIST_FIELDS:
                    if not isinstance(child, (list, tuple)):
                        raise ValueError(f"{key} must be a list of source references")
                    for item in child:
                        if not isinstance(item, str) or not item.strip():
                            raise ValueError(f"{key} contains an invalid source reference")
                        candidate = item.strip()
                        if not candidate.startswith("financial-source://"):
                            raise ValueError(f"{key} must contain exact financial-source:// references")
                        refs.add(candidate)
                elif key in _SOURCE_REF_SINGLE_FIELDS:
                    if not isinstance(child, str) or not child.strip():
                        raise ValueError(f"{key} must contain a non-empty source reference")
                    candidate = child.strip()
                    if not candidate.startswith("financial-source://"):
                        raise ValueError(f"{key} must be an exact financial-source:// reference")
                    refs.add(candidate)
                else:
                    walk(child)
        elif isinstance(value, (list, tuple)):
            for item in value:
                walk(item)

    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            raise ValueError("research source collection requires mapping artifacts")
        walk(artifact)
    return sorted(refs)


def validate_source_binding_coverage(
    binding_set: SourceBindingSet,
    *,
    task_id: str,
    evidence_refs: list[str] | tuple[str, ...],
) -> SourceBindingSet:
    """Require exact, task-scoped source bindings for every admitted research evidence ref."""
    if binding_set.task_id != task_id:
        raise ValueError("source binding set task_id does not match the current article task")
    normalized: list[str] = []
    for ref in evidence_refs:
        if not isinstance(ref, str) or not ref.strip():
            raise ValueError("research evidence source refs must be non-empty strings")
        value = ref.strip()
        if not value.startswith("financial-source://"):
            raise ValueError("raw external URLs are discovery inputs, not admitted research evidence refs")
        try:
            _, identity = value.split("://", 1)
            source_id, version_id = identity.split("/", 1)
            if "/" in version_id:
                raise ValueError("invalid source reference path")
            canonical = source_reference(source_id, version_id)
        except (ValueError, TypeError) as exc:
            raise ValueError("research evidence ref must be an exact financial-source:// reference") from exc
        if canonical != value:
            raise ValueError("research evidence ref must use its canonical exact-version form")
        normalized.append(value)
    if not normalized:
        raise ValueError("research evidence requires at least one exact source binding")
    if len(normalized) != len(set(normalized)):
        raise ValueError("research evidence refs cannot contain duplicates")
    bound = {binding.source_ref for binding in binding_set.bindings}
    required = set(normalized)
    if bound != required:
        missing = sorted(required - bound)
        unused = sorted(bound - required)
        raise ValueError(
            f"source binding coverage must be exact; missing={missing}, unused={unused}"
        )
    return binding_set


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
    if version.drive_object.file_id in {item.drive_object.file_id for item in record.versions}:
        raise ValueError("each immutable source version must use a new Drive file ID")
    if version.status != "AVAILABLE":
        raise ValueError("a new current source version must be AVAILABLE after exact Drive readback")
    match = _VERSION_ID.fullmatch(version.version_id)
    expected = max(
        int(_VERSION_ID.fullmatch(item.version_id).group("sequence"))
        for item in record.versions
    ) + 1
    if match is None or int(match.group("sequence")) != expected:
        raise ValueError("new source version must use the next contiguous sequence")
    if version.created_at < record.updated_at:
        raise ValueError("new source version cannot predate the current source record")
    updated = record.model_dump(mode="python")
    updated.update(
        {
            "versions": (*record.versions, version),
            "current_version_id": version.version_id,
            "updated_at": version.created_at,
        }
    )
    return SourceRecord.model_validate(updated)


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
        scope=record.scope,
        source_task_id=record.task_id,
        rights_basis=version.rights_basis,
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
