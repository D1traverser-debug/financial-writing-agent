from __future__ import annotations

import base64
import json
from copy import deepcopy

import pytest

from financial_writing_agent import authoritative_state, owner_guard
from financial_writing_agent.authoritative_state import AuthoritativeStateSnapshot


def _current(task_id: str) -> dict:
    return owner_guard.build_initial_state(
        task_id=task_id,
        prompt="review regression",
        source_refs=[],
        executor_identity="review-test",
    )


def _install_authority(monkeypatch: pytest.MonkeyPatch, state: dict, sha: str = "a" * 40) -> None:
    def _fake(task_id: str, *, repository="D1traverser-debug/financial-writing-agent", ref="main", timeout=10.0):
        assert task_id == state["task_id"]
        return AuthoritativeStateSnapshot(
            task_id=task_id,
            state=deepcopy(state),
            blob_sha=sha,
            path=f"workspaces/articles/{task_id}/STATE.json",
            ref="main",
        )

    monkeypatch.setattr(owner_guard, "fetch_authoritative_state", _fake)


def _downgrade(candidate: dict) -> dict:
    downgraded = deepcopy(candidate)
    downgraded["schema_version"] = owner_guard.CURRENT_STATE_SCHEMA_VERSION
    downgraded.pop("writing_kernel_version", None)
    downgraded.pop("quality_evidence", None)
    return downgraded


@pytest.mark.strict_authority
def test_public_transition_validator_cannot_downgrade_schema_1_3_candidate(monkeypatch: pytest.MonkeyPatch):
    before = _current("candidate-transition-downgrade")
    sha = "a" * 40
    _install_authority(monkeypatch, before, sha)
    valid_after = owner_guard.advance_state(
        before,
        previous_state_blob_sha=sha,
        executor_identity="review-test",
    )

    with pytest.raises(owner_guard.GithubChatGuardError, match="cannot downgrade governance"):
        owner_guard.validate_transition(
            before,
            _downgrade(valid_after),
            previous_state_blob_sha=sha,
        )


@pytest.mark.strict_authority
def test_public_feedback_validator_cannot_downgrade_schema_1_3_candidate(monkeypatch: pytest.MonkeyPatch):
    before = _current("candidate-feedback-downgrade")
    sha = "b" * 40
    _install_authority(monkeypatch, before, sha)
    valid_after = owner_guard.attach_material_feedback(
        before,
        previous_state_blob_sha=sha,
        executor_identity="review-test",
        sample={"sample_type": "USER_FEEDBACK", "summary": "material feedback"},
        system_impact={
            "signal_id": "impact-review-regression",
            "status": "OPEN",
            "trigger_sample_type": "USER_FEEDBACK",
        },
    )

    with pytest.raises(owner_guard.GithubChatGuardError, match="cannot downgrade governance"):
        owner_guard.validate_feedback_update(
            before,
            _downgrade(valid_after),
            previous_state_blob_sha=sha,
        )


class _FakeResponse:
    def __init__(self, payload: dict):
        self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self._raw


def test_authoritative_resolver_falls_back_to_git_blob_when_contents_are_not_inlined(monkeypatch: pytest.MonkeyPatch):
    task_id = "large-state"
    path = f"workspaces/articles/{task_id}/STATE.json"
    sha = "c" * 40
    state = {"task_id": task_id, "payload": "large-state-content"}
    encoded = base64.b64encode(json.dumps(state).encode("utf-8")).decode("ascii")
    calls: list[str] = []

    def _urlopen(req, timeout):
        calls.append(req.full_url)
        if "/contents/" in req.full_url:
            return _FakeResponse(
                {
                    "type": "file",
                    "path": path,
                    "sha": sha,
                    "size": 2_000_000,
                    "encoding": "none",
                    "content": "",
                }
            )
        assert req.full_url.endswith(f"/git/blobs/{sha}")
        return _FakeResponse({"sha": sha, "encoding": "base64", "content": encoded})

    monkeypatch.setattr(authoritative_state.request, "urlopen", _urlopen)
    snapshot = authoritative_state.fetch_authoritative_state(task_id)
    assert snapshot.blob_sha == sha
    assert snapshot.state == state
    assert len(calls) == 2
    assert "/contents/" in calls[0]
    assert calls[1].endswith(f"/git/blobs/{sha}")


def test_authoritative_blob_fallback_rejects_sha_mismatch(monkeypatch: pytest.MonkeyPatch):
    task_id = "large-state-mismatch"
    path = f"workspaces/articles/{task_id}/STATE.json"
    contents_sha = "d" * 40
    other_sha = "e" * 40
    state = {"task_id": task_id}
    encoded = base64.b64encode(json.dumps(state).encode("utf-8")).decode("ascii")

    def _urlopen(req, timeout):
        if "/contents/" in req.full_url:
            return _FakeResponse(
                {
                    "type": "file",
                    "path": path,
                    "sha": contents_sha,
                    "size": 2_000_000,
                    "encoding": "none",
                    "content": "",
                }
            )
        return _FakeResponse({"sha": other_sha, "encoding": "base64", "content": encoded})

    monkeypatch.setattr(authoritative_state.request, "urlopen", _urlopen)
    with pytest.raises(authoritative_state.AuthoritativeStateError, match="blob SHA mismatch"):
        authoritative_state.fetch_authoritative_state(task_id)
