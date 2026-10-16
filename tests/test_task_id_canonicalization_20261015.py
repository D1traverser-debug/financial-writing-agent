from __future__ import annotations

import pytest

from financial_writing_agent import authoritative_state, owner_guard


@pytest.mark.parametrize("task_id", [" padded", "padded ", " padded "])
def test_public_builder_rejects_task_id_whitespace_aliases(task_id: str):
    with pytest.raises(owner_guard.GithubChatGuardError, match="leading or trailing whitespace"):
        owner_guard.build_initial_state(
            task_id=task_id,
            prompt="canonical task id regression",
            source_refs=[],
            executor_identity="task-id-test",
        )


@pytest.mark.parametrize("task_id", [" padded", "padded ", " padded "])
def test_authoritative_resolver_rejects_task_id_whitespace_before_network_io(
    monkeypatch: pytest.MonkeyPatch,
    task_id: str,
):
    def _unexpected_urlopen(*args, **kwargs):
        raise AssertionError("non-canonical task id must fail before GitHub I/O")

    monkeypatch.setattr(authoritative_state.request, "urlopen", _unexpected_urlopen)
    with pytest.raises(authoritative_state.AuthoritativeStateError, match="leading or trailing whitespace"):
        authoritative_state.fetch_authoritative_state(task_id)


def test_base_state_validation_rejects_padded_task_identity():
    state = owner_guard.build_initial_state(
        task_id="canonical-task",
        prompt="canonical task id regression",
        source_refs=[],
        executor_identity="task-id-test",
    )
    state["task_id"] = " canonical-task "
    with pytest.raises(owner_guard.GithubChatGuardError, match="leading or trailing whitespace"):
        owner_guard._validate_unpersisted_state(state)
