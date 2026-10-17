from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


ARTIFACT_STATUS_CONTRACT_VERSION = "1.0"
ALLOWED_WORKSPACE_LIFECYCLES = {"CURRENT", "MIGRATED_HISTORY", "ARCHIVE"}
ALLOWED_ARTIFACT_STATUSES = {
    "KEEP_CURRENT",
    "KEEP_FIXTURE",
    "ARCHIVE_PROVENANCE",
    "DELETE_UNREFERENCED",
}


class ArtifactHygieneError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactHygieneError(message)


def validate_artifact_status_manifest(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one task workspace's current-vs-history namespace contract.

    Filenames are not authority. A workspace manifest must make current ownership explicit,
    and migrated/history workspaces cannot retain any artifact that still claims current
    status. This preserves provenance without allowing stale PASS/draft/delivery files to
    be consumed as current merely because they remain searchable.
    """

    _require(isinstance(raw, Mapping), "artifact status manifest must be an object")
    manifest = deepcopy(dict(raw))
    _require(
        manifest.get("schema_version") == ARTIFACT_STATUS_CONTRACT_VERSION,
        f"artifact status schema_version must be {ARTIFACT_STATUS_CONTRACT_VERSION}",
    )
    lifecycle = manifest.get("workspace_lifecycle")
    _require(lifecycle in ALLOWED_WORKSPACE_LIFECYCLES, f"unsupported workspace_lifecycle: {lifecycle}")
    task_id = manifest.get("task_id")
    _require(isinstance(task_id, str) and bool(task_id.strip()), "artifact status manifest requires task_id")
    statuses = manifest.get("statuses")
    _require(isinstance(statuses, Mapping) and bool(statuses), "artifact status manifest requires statuses")

    normalized_statuses: dict[str, str] = {}
    for path, status in statuses.items():
        _require(isinstance(path, str) and bool(path.strip()), "artifact status path must be non-empty")
        _require(status in ALLOWED_ARTIFACT_STATUSES, f"unsupported artifact status for {path}: {status}")
        normalized_statuses[path] = str(status)
    manifest["statuses"] = normalized_statuses

    current_paths = sorted(path for path, status in normalized_statuses.items() if status == "KEEP_CURRENT")
    if lifecycle == "CURRENT":
        current_authority = manifest.get("current_authority")
        _require(isinstance(current_authority, str) and bool(current_authority.strip()), "CURRENT workspace requires current_authority")
        relative_authority = current_authority
        prefix = f"workspaces/articles/{task_id}/"
        if relative_authority.startswith(prefix):
            relative_authority = relative_authority[len(prefix):]
        _require(current_paths == [relative_authority], "CURRENT workspace must have exactly one KEEP_CURRENT artifact matching current_authority")
    elif lifecycle == "MIGRATED_HISTORY":
        _require(not current_paths, "MIGRATED_HISTORY workspace cannot contain KEEP_CURRENT artifacts")
        successor_task_id = manifest.get("successor_task_id")
        current_authority = manifest.get("current_authority")
        _require(isinstance(successor_task_id, str) and bool(successor_task_id.strip()), "MIGRATED_HISTORY workspace requires successor_task_id")
        _require(isinstance(current_authority, str) and bool(current_authority.strip()), "MIGRATED_HISTORY workspace requires successor current_authority")
        _require(successor_task_id != task_id, "successor_task_id must differ from migrated task_id")
    else:
        _require(not current_paths, "ARCHIVE workspace cannot contain KEEP_CURRENT artifacts")

    return manifest
