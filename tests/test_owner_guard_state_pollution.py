import pytest

from financial_writing_agent.owner_guard import GithubChatGuardError, build_initial_state, validate_state


def _state():
    return build_initial_state(
        task_id="pollution-task",
        prompt="test",
        distribution_mode="FINANCE_DEEP",
        source_refs=[],
        executor_identity="chat-session:test",
    )


def test_complete_cannot_be_spoofed_in_owner_state():
    state = _state()
    state["status"] = "COMPLETE"
    with pytest.raises(GithubChatGuardError, match="supported GITHUB_CHAT status"):
        validate_state(state)


def test_future_stage_artifact_cannot_be_preseeded_before_stage_is_reached():
    state = _state()
    state["stage_artifacts"]["DRAFT"] = {
        "path": "workspaces/articles/pollution-task/stages/DRAFT.json",
        "blob_sha": "future-draft",
    }
    with pytest.raises(GithubChatGuardError, match="future-stage artifact"):
        validate_state(state)


def test_future_review_decision_cannot_be_preseeded_before_review_stage_is_reached():
    state = _state()
    state["review_decisions"]["FINAL_AUDIT"] = {
        "status": "PASS",
        "assurance": "CHAT_SELF_REVIEW",
    }
    with pytest.raises(GithubChatGuardError, match="future-stage review"):
        validate_state(state)
