from __future__ import annotations

import pytest

from financial_writing_agent.task_work_profile import (
    TaskWorkProfile,
    TaskWorkProfileError,
    validate_task_work_profile,
)


def _contexts(requirements=()):
    scopes = ("ALL", "RESEARCH", "PRIVATE_RESEARCH", "FINANCE_DEEP", "FINANCE_BROAD")
    return {
        scope: {"requirements": [dict(item) for item in requirements]}
        for scope in scopes
    }


def _requirement(requirement_id, source_kind="USER_EXPLICIT"):
    return {
        "requirement_id": requirement_id,
        "source_kind": source_kind,
    }


def _profile(**overrides):
    value = {
        "schema_version": "1.0",
        "task_shape": "OPEN_ENDED",
        "fixed_requirement_ids": [],
        "preference_requirement_ids": [],
        "open_decision_domains": ["THESIS", "ANGLE", "STORY_STRUCTURE", "TITLE", "VOICE"],
        "conditional_modules": ["COMPANY_UNIVERSE"],
        "classification_rationale": "The user gives a goal and topic while leaving editorial decisions open.",
    }
    value.update(overrides)
    return value


def test_open_ended_profile_preserves_editorial_freedom_without_inventing_fixed_requirements():
    profile = validate_task_work_profile(_profile(), _contexts())
    assert profile["task_shape"] == "OPEN_ENDED"
    assert profile["fixed_requirement_ids"] == []
    assert profile["open_decision_domains"]


def test_fixed_workflow_profile_requires_every_explicit_requirement_and_no_open_decisions():
    requirements = [_requirement("exact-outline"), _requirement("fixed-title", "USER_CORRECTION")]
    profile = _profile(
        task_shape="FIXED_WORKFLOW",
        fixed_requirement_ids=["exact-outline", "fixed-title"],
        open_decision_domains=[],
    )
    result = validate_task_work_profile(profile, _contexts(requirements))
    assert result["task_shape"] == "FIXED_WORKFLOW"
    assert set(result["fixed_requirement_ids"]) == {"exact-outline", "fixed-title"}


def test_hybrid_profile_separates_locked_requirements_from_open_editorial_decisions():
    requirements = [
        _requirement("fixed-word-count"),
        _requirement("preferred-tone", "USER_PREFERENCE"),
    ]
    profile = _profile(
        task_shape="HYBRID",
        fixed_requirement_ids=["fixed-word-count"],
        preference_requirement_ids=["preferred-tone"],
        open_decision_domains=["THESIS", "ANGLE", "STORY_STRUCTURE"],
    )
    result = validate_task_work_profile(profile, _contexts(requirements))
    assert result["task_shape"] == "HYBRID"
    assert result["fixed_requirement_ids"] == ["fixed-word-count"]
    assert result["preference_requirement_ids"] == ["preferred-tone"]
    assert result["open_decision_domains"] == ["THESIS", "ANGLE", "STORY_STRUCTURE"]


def test_profile_cannot_omit_or_invent_active_fixed_requirements():
    requirements = [_requirement("fixed-title")]
    omitted = _profile(task_shape="OPEN_ENDED", open_decision_domains=["THESIS"])
    with pytest.raises(TaskWorkProfileError, match="fixed requirement ids"):
        validate_task_work_profile(omitted, _contexts(requirements))

    invented = _profile(
        task_shape="HYBRID",
        fixed_requirement_ids=["not-an-active-requirement"],
        open_decision_domains=["THESIS"],
    )
    with pytest.raises(TaskWorkProfileError, match="fixed requirement ids"):
        validate_task_work_profile(invented, _contexts(requirements))


def test_profile_cannot_misclassify_preferences_as_hard_requirements():
    requirements = [_requirement("preferred-tone", "USER_PREFERENCE")]
    profile = _profile(
        task_shape="HYBRID",
        fixed_requirement_ids=["preferred-tone"],
        open_decision_domains=["THESIS"],
    )
    with pytest.raises(TaskWorkProfileError, match="fixed requirement ids"):
        validate_task_work_profile(profile, _contexts(requirements))


@pytest.mark.parametrize(
    "profile",
    [
        _profile(task_shape="FIXED_WORKFLOW"),
        _profile(task_shape="HYBRID"),
        _profile(open_decision_domains=[]),
        _profile(open_decision_domains=["THESIS", "THESIS"]),
        _profile(conditional_modules=["COMPANY_UNIVERSE", "COMPANY_UNIVERSE"]),
    ],
)
def test_internally_inconsistent_task_shapes_fail_closed(profile):
    with pytest.raises(ValueError):
        TaskWorkProfile.model_validate(profile)
