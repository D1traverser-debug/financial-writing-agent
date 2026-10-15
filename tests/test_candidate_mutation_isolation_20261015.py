from __future__ import annotations

from copy import deepcopy

import pytest

from financial_writing_agent import owner_guard


def _new(task_id: str) -> dict:
    return owner_guard.build_initial_state(
        task_id=task_id,
        prompt="original prompt",
        source_refs=["source-a"],
        executor_identity="isolation-test",
    )


def _valid_transition(before: dict, sha: str) -> dict:
    return owner_guard.advance_state(
        before,
        previous_state_blob_sha=sha,
        executor_identity="isolation-test",
    )


def _valid_feedback(before: dict, sha: str) -> dict:
    return owner_guard.attach_material_feedback(
        before,
        previous_state_blob_sha=sha,
        executor_identity="isolation-test",
        sample={"sample_type": "USER_FEEDBACK", "summary": "material feedback"},
        system_impact={
            "signal_id": "isolation-impact",
            "status": "OPEN",
            "trigger_sample_type": "USER_FEEDBACK",
        },
    )


@pytest.mark.parametrize(
    "mutator",
    [
        lambda state: state.__setitem__("prompt", "silently changed prompt"),
        lambda state: state.__setitem__("source_refs", ["source-b"]),
        lambda state: state.__setitem__(
            "open_system_impact",
            [{"signal_id": "injected", "status": "OPEN", "trigger_sample_type": "USER_FEEDBACK"}],
        ),
        lambda state: state.__setitem__("unowned_extra_field", {"injected": True}),
    ],
)
def test_public_transition_validator_rejects_unowned_top_level_mutations(mutator):
    before = _new("transition-isolation")
    sha = "a" * 40
    valid_after = _valid_transition(before, sha)
    tampered = deepcopy(valid_after)
    mutator(tampered)

    with pytest.raises(owner_guard.GithubChatGuardError, match="unowned|immutable|mutation"):
        owner_guard.validate_transition(before, tampered, previous_state_blob_sha=sha)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda state: state.__setitem__("prompt", "silently changed prompt"),
        lambda state: state.__setitem__("source_refs", ["source-b"]),
        lambda state: state.__setitem__("stage_artifacts", {"DRAFT": {"path": "workspaces/articles/feedback-isolation/DRAFT.json", "blob_sha": "forged"}}),
        lambda state: state.__setitem__("unowned_extra_field", {"injected": True}),
    ],
)
def test_public_feedback_validator_rejects_unowned_top_level_mutations(mutator):
    before = _new("feedback-isolation")
    sha = "b" * 40
    valid_after = _valid_feedback(before, sha)
    tampered = deepcopy(valid_after)
    mutator(tampered)

    with pytest.raises(owner_guard.GithubChatGuardError, match="unowned|immutable|mutation"):
        owner_guard.validate_feedback_update(before, tampered, previous_state_blob_sha=sha)
