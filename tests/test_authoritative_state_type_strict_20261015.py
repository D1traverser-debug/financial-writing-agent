from __future__ import annotations

from copy import deepcopy

import pytest

from financial_writing_agent import owner_guard
from financial_writing_agent.authoritative_state import AuthoritativeStateSnapshot
from financial_writing_agent.current_admission import build_initial_state


def _install_authority(monkeypatch: pytest.MonkeyPatch, state: dict, sha: str = "a" * 40) -> None:
    authoritative = deepcopy(state)

    def _fake(task_id: str, *, repository="D1traverser-debug/financial-writing-agent", ref="main", timeout=10.0):
        return AuthoritativeStateSnapshot(
            task_id=task_id,
            state=deepcopy(authoritative),
            blob_sha=sha,
            path=f"workspaces/articles/{task_id}/STATE.json",
            ref="main",
        )

    monkeypatch.setattr(owner_guard, "fetch_authoritative_state", _fake)


@pytest.mark.strict_authority
@pytest.mark.parametrize(("authoritative_value", "candidate_value"), [(True, 1), (False, 0)])
def test_authoritative_state_comparison_is_json_type_strict(
    monkeypatch: pytest.MonkeyPatch,
    authoritative_value: bool,
    candidate_value: int,
):
    state = build_initial_state(
        task_id=f"type-strict-{int(authoritative_value)}",
        prompt="type strict authority regression",
        source_refs=[],
        executor_identity="strict-test",
    )
    state["proactive_resolution_history"] = [
        {
            "target": "evidence",
            "outcome": "PROVISIONAL",
            "safe_to_continue": authoritative_value,
        }
    ]
    _install_authority(monkeypatch, state)

    tampered = deepcopy(state)
    tampered["proactive_resolution_history"][0]["safe_to_continue"] = candidate_value

    with pytest.raises(owner_guard.GithubChatGuardError, match="differs from authoritative GitHub STATE.json"):
        owner_guard.validate_state(tampered)


@pytest.mark.strict_authority
def test_authoritative_state_comparison_rejects_list_tuple_aliasing(monkeypatch: pytest.MonkeyPatch):
    state = build_initial_state(
        task_id="type-strict-container",
        prompt="container type authority regression",
        source_refs=[],
        executor_identity="strict-test",
    )
    state["proactive_resolution_history"] = [{"attempted_sources": ["filing"]}]
    _install_authority(monkeypatch, state)

    tampered = deepcopy(state)
    tampered["proactive_resolution_history"][0]["attempted_sources"] = ("filing",)

    with pytest.raises(owner_guard.GithubChatGuardError, match="differs from authoritative GitHub STATE.json"):
        owner_guard.validate_state(tampered)
