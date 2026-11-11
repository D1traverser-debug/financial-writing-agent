"""Independent R1 path/identity regressions for the existing Financial owner.

These tests exercise public admission and artifact manifests, not a parallel state
authority. The observed gaps existed in main@e580cd4; no live files are written.
"""

from copy import deepcopy

import pytest

from financial_writing_agent import current_admission
from financial_writing_agent.artifact_hygiene import (
    ArtifactHygieneError,
    validate_artifact_status_manifest,
)


def _state(task_id="identity-safe-task"):
    return current_admission.build_initial_state(
        task_id=task_id,
        prompt="跨境电商研究与财经写作",
        source_refs=[],
        executor_identity="test:financial-identity",
    )


@pytest.mark.parametrize(
    "task_id",
    [
        "../other-task",
        "one/other",
        r"one\other",
        "..",
        ".",
        "task/../other",
        " task ",
        "task\x00hidden",
    ],
)
def test_new_task_identity_must_be_one_canonical_path_component(task_id):
    with pytest.raises(ValueError):
        _state(task_id)


@pytest.mark.parametrize(
    "artifact_path",
    [
        "workspaces/articles/identity-safe-task/stages/../other/RESEARCH.json",
        "workspaces/articles/identity-safe-task/stages//RESEARCH.json",
        r"workspaces/articles/identity-safe-task/stages\RESEARCH.json",
        "workspaces/articles/identity-safe-task/./stages/RESEARCH.json",
        "workspaces/articles/identity-safe-task/stages/../../other/STATE.json",
    ],
)
def test_stage_artifact_path_cannot_escape_or_alias_workspace(artifact_path):
    initial = _state()
    research = current_admission.advance_state(
        initial,
        previous_state_blob_sha="a" * 40,
        executor_identity="test:financial-identity",
    )
    tampered = deepcopy(research)
    tampered["stage_artifacts"]["RESEARCH"] = {
        "path": artifact_path,
        "blob_sha": "b" * 40,
    }
    with pytest.raises(ValueError):
        current_admission.validate_state(tampered)


@pytest.mark.parametrize(
    "file_name",
    ["../wrong.docx", r"..\wrong.docx", "reports/deep.docx", "deep.docx\nspoof", "deep.docx\x00"],
)
def test_delivery_file_name_must_be_a_basename(file_name):
    state = _state()
    tampered = deepcopy(state)
    tampered["delivery_artifacts"]["FINANCE_DEEP_DOCX"] = {
        "kind": "FINANCE_DEEP_DOCX",
        "file_name": file_name,
        "sha256": "c" * 64,
    }
    with pytest.raises(ValueError):
        current_admission.validate_state(tampered)


def _manifest():
    return {
        "schema_version": "1.0",
        "task_id": "identity-safe-task",
        "workspace_lifecycle": "CURRENT",
        "current_authority": "workspaces/articles/identity-safe-task/STATE.json",
        "statuses": {"STATE.json": "KEEP_CURRENT"},
    }


@pytest.mark.parametrize("bad_path", ["../other/STATE.json", "a/../../other", "foo//bar", r"foo\bar", "./STATE.json"])
def test_artifact_status_manifest_rejects_noncanonical_relative_paths(bad_path):
    manifest = _manifest()
    manifest["statuses"][bad_path] = "KEEP_FIXTURE"
    with pytest.raises(ArtifactHygieneError):
        validate_artifact_status_manifest(manifest)


def test_migrated_manifest_successor_authority_must_match_declared_successor():
    manifest = {
        "schema_version": "1.0",
        "task_id": "old-task",
        "workspace_lifecycle": "MIGRATED_HISTORY",
        "successor_task_id": "new-task",
        "current_authority": "workspaces/articles/unrelated-task/STATE.json",
        "statuses": {"STATE.json": "ARCHIVE_PROVENANCE"},
    }
    with pytest.raises(ArtifactHygieneError):
        validate_artifact_status_manifest(manifest)


def test_valid_canonical_manifest_and_current_state_remain_supported():
    assert validate_artifact_status_manifest(_manifest())["statuses"]["STATE.json"] == "KEEP_CURRENT"
    current_admission.validate_state(_state())
