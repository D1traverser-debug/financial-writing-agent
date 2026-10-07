import pytest

from financial_writing_agent.checks import sha256_file
from financial_writing_agent.models import Artifact, ArtifactKind, TaskContract, WritingState
from financial_writing_agent import plugin_server


def _state_with_artifact(root, data=b"final"):
    task_id = "resource-integrity-test"
    task_dir = root / task_id
    task_dir.mkdir(parents=True)
    path = task_dir / "FINANCE_DEEP.docx"
    path.write_bytes(data)
    state = WritingState(contract=TaskContract(task_id=task_id, prompt="resource test"))
    state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(
        kind=ArtifactKind.FINANCE_DEEP_DOCX,
        path=str(path),
        exists=True,
        sha256=sha256_file(path),
    )
    return state, path


def test_resource_read_rechecks_recorded_checksum(monkeypatch, tmp_path):
    state, path = _state_with_artifact(tmp_path)
    monkeypatch.setattr(plugin_server.impl, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(plugin_server.impl, "_load", lambda task_id: state)

    data = plugin_server._resource_bytes(
        state.contract.task_id,
        ArtifactKind.FINANCE_DEEP_DOCX.value,
        {ArtifactKind.FINANCE_DEEP_DOCX},
    )
    assert data == b"final"

    path.write_bytes(b"tampered-after-complete")
    with pytest.raises(ValueError, match="checksum mismatch at resource read"):
        plugin_server._resource_bytes(
            state.contract.task_id,
            ArtifactKind.FINANCE_DEEP_DOCX.value,
            {ArtifactKind.FINANCE_DEEP_DOCX},
        )


def test_resource_read_rejects_missing_checksum(monkeypatch, tmp_path):
    state, _ = _state_with_artifact(tmp_path)
    state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX].sha256 = None
    monkeypatch.setattr(plugin_server.impl, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(plugin_server.impl, "_load", lambda task_id: state)

    with pytest.raises(ValueError, match="no recorded checksum"):
        plugin_server._resource_bytes(
            state.contract.task_id,
            ArtifactKind.FINANCE_DEEP_DOCX.value,
            {ArtifactKind.FINANCE_DEEP_DOCX},
        )
