from __future__ import annotations

import hashlib
from typing import Any, Callable, Mapping

from .source_lifecycle import SourceBindingSet, SourceVersion


class SourceReadbackError(ValueError):
    """An exact immutable Drive source version could not be verified."""


DriveVersionReader = Callable[[str, str | None], Mapping[str, Any] | None]


def _payload_bytes(value: Any) -> bytes:
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    raise SourceReadbackError("DRIVE_SOURCE_RAW_PAYLOAD_REQUIRED")


def _verify_exact_readback(
    observed: Mapping[str, Any],
    *,
    file_id: str,
    folder_id: str,
    revision_id: str | None,
    media_type: str,
    size_bytes: int,
    raw_sha256: str,
    normalized_text_sha256: str,
    source_family: str,
    retrieved_at: str,
) -> Mapping[str, Any]:
    if observed.get("file_id") != file_id:
        raise SourceReadbackError("DRIVE_SOURCE_FILE_ID_MISMATCH")
    if observed.get("folder_id") != folder_id:
        raise SourceReadbackError("DRIVE_SOURCE_FOLDER_ID_MISMATCH")
    observed_revision = observed.get("revision_id")
    if revision_id is not None and observed_revision != revision_id:
        raise SourceReadbackError("DRIVE_SOURCE_REVISION_ID_MISMATCH")
    if observed.get("media_type") != media_type:
        raise SourceReadbackError("DRIVE_SOURCE_MEDIA_TYPE_MISMATCH")

    payload = _payload_bytes(observed.get("payload"))
    if len(payload) != size_bytes:
        raise SourceReadbackError("DRIVE_SOURCE_SIZE_MISMATCH")
    actual_raw_sha = hashlib.sha256(payload).hexdigest()
    if actual_raw_sha != raw_sha256:
        raise SourceReadbackError("DRIVE_SOURCE_RAW_SHA256_MISMATCH")

    text_value = observed.get("text")
    if not isinstance(text_value, str) or not text_value.strip():
        raise SourceReadbackError("DRIVE_SOURCE_EXTRACTED_TEXT_REQUIRED")
    actual_text_sha = hashlib.sha256(text_value.encode("utf-8")).hexdigest()
    if actual_text_sha != normalized_text_sha256:
        raise SourceReadbackError("DRIVE_SOURCE_NORMALIZED_TEXT_SHA256_MISMATCH")

    actual_family = observed.get("source_family")
    if not isinstance(actual_family, str) or actual_family.strip() != source_family:
        raise SourceReadbackError("DRIVE_SOURCE_FAMILY_MISMATCH")

    return {
        "text": text_value,
        "sha256": actual_text_sha,
        "retrieved_at": retrieved_at,
        "source_family": actual_family.strip(),
        "file_id": file_id,
        "revision_id": observed_revision,
        "raw_sha256": actual_raw_sha,
        "size_bytes": len(payload),
        "media_type": media_type,
    }


def verify_source_version_readback(
    version: SourceVersion,
    *,
    observed: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    """Verify a source version against an exact Drive file readback."""
    if not isinstance(observed, Mapping):
        raise SourceReadbackError("DRIVE_SOURCE_READBACK_MISSING")
    drive = version.drive_object
    return _verify_exact_readback(
        observed,
        file_id=drive.file_id,
        folder_id=drive.folder_id,
        revision_id=drive.revision_id,
        media_type=drive.media_type,
        size_bytes=drive.size_bytes,
        raw_sha256=drive.raw_sha256,
        normalized_text_sha256=drive.normalized_text_sha256,
        source_family=version.source_family,
        retrieved_at=version.retrieved_at.isoformat(),
    )


def build_bound_source_reader(
    binding_set: SourceBindingSet,
    *,
    read_drive_version: DriveVersionReader,
) -> Callable[[str], Mapping[str, Any]]:
    """Build the source_reader callback consumed by current_research_sources.

    The callback accepts only exact financial-source:// refs already admitted in
    the binding set. It requires actual payload bytes and extracted text from the
    Drive reader, then independently verifies file identity, parent folder,
    optional revision ID, MIME type, byte size, raw SHA-256, normalized-text
    SHA-256 and source family.
    """
    if not callable(read_drive_version):
        raise SourceReadbackError("DRIVE_SOURCE_READER_REQUIRED")
    bindings = {item.source_ref: item for item in binding_set.bindings}

    def read(source_ref: str) -> Mapping[str, Any]:
        binding = bindings.get(source_ref)
        if binding is None:
            raise SourceReadbackError("SOURCE_REF_NOT_BOUND_TO_CURRENT_RESEARCH_REVISION")
        try:
            observed = read_drive_version(binding.drive_file_id, binding.drive_revision_id)
        except Exception as exc:
            raise SourceReadbackError("DRIVE_SOURCE_READ_FAILED") from exc
        if not isinstance(observed, Mapping):
            raise SourceReadbackError("DRIVE_SOURCE_READBACK_MISSING")
        return _verify_exact_readback(
            observed,
            file_id=binding.drive_file_id,
            folder_id=binding.drive_folder_id,
            revision_id=binding.drive_revision_id,
            media_type=binding.media_type,
            size_bytes=binding.drive_file_size_bytes,
            raw_sha256=binding.raw_sha256,
            normalized_text_sha256=binding.normalized_text_sha256,
            source_family=binding.source_family,
            retrieved_at=binding.retrieved_at.isoformat(),
        )

    return read
