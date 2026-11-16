from __future__ import annotations

import pytest

from financial_writing_agent.writing_execution_profile import (
    WritingExecutionProfile,
    WritingExecutionProfileError,
    validate_writing_execution_profile,
)


def _contexts(requirements=()):
    scopes = ("ALL", "RESEARCH", "PRIVATE_RESEARCH", "FINANCE_DEEP", "FINANCE_BROAD")
    return {scope: {"requirements": [dict(item) for item in requirements]} for scope in scopes}


def _requirement(requirement_id, source_kind="USER_EXPLICIT"):
    return {"requirement_id": requirement_id, "source_kind": source_kind}


def _profile(**overrides):
    value = {
        "schema_version": "1.0",
        "workflow_contract": "FINANCIAL_ARTICLE_10_STAGE_V1",
        "source_prompt_sha256": "a" * 64,
        "fixed_requirement_ids": [],
        "preference_requirement_ids": [],
        "locked_decision_domains": [],
        "open_decision_domains": ["THESIS", "ANGLE", "NARRATIVE_ENGINE", "TITLE", "VOICE"],
        "conditional_modules": ["COMPANY_UNIVERSE"],
        "execution_rationale": "The business workflow remains fixed while unspecified editorial choices follow evidence and reader needs.",
    }
    value.update(overrides)
    return value


def test_one_workflow_contract_supports_different_content_led_editorial_decisions():
    event_led = WritingExecutionProfile.model_validate(_profile(
        open_decision_domains=["THESIS", "EVENT_TRANSMISSION", "COMPANY_COMPARISON", "TITLE"],
    ))
    company_cycle = WritingExecutionProfile.model_validate(_profile(
        open_decision_domains=["THESIS", "VALUATION_GAP", "COMPANY_DIVERGENCE", "NARRATIVE_ENGINE"],
    ))
    assert event_led.workflow_contract == company_cycle.workflow_contract
    assert event_led.open_decision_domains != company_cycle.open_decision_domains


def test_all_active_explicit_requirements_and_preferences_are_bound_exactly():
    requirements = [
        _requirement("fixed-outline"),
        _requirement("corrected-title", "USER_CORRECTION"),
        _requirement("preferred-tone", "USER_PREFERENCE"),
    ]
    profile = _profile(
        fixed_requirement_ids=["fixed-outline", "corrected-title"],
        preference_requirement_ids=["preferred-tone"],
        locked_decision_domains=["TITLE", "OUTPUT_FORMAT"],
        open_decision_domains=["THESIS", "ANGLE", "NARRATIVE_ENGINE"],
    )
    result = validate_writing_execution_profile(
        profile, _contexts(requirements), source_prompt_sha256="a" * 64,
    )
    assert set(result["fixed_requirement_ids"]) == {"fixed-outline", "corrected-title"}
    assert result["preference_requirement_ids"] == ["preferred-tone"]


def test_missing_or_invented_requirement_ids_fail_closed():
    requirements = [_requirement("fixed-title")]
    with pytest.raises(WritingExecutionProfileError, match="fixed requirement ids"):
        validate_writing_execution_profile(
            _profile(), _contexts(requirements), source_prompt_sha256="a" * 64,
        )
    with pytest.raises(WritingExecutionProfileError, match="fixed requirement ids"):
        validate_writing_execution_profile(
            _profile(fixed_requirement_ids=["invented-id"]),
            _contexts(requirements), source_prompt_sha256="a" * 64,
        )


def test_preferences_cannot_be_promoted_to_hard_requirements():
    requirements = [_requirement("preferred-tone", "USER_PREFERENCE")]
    profile = _profile(fixed_requirement_ids=["preferred-tone"])
    with pytest.raises(WritingExecutionProfileError, match="fixed requirement ids"):
        validate_writing_execution_profile(
            profile, _contexts(requirements), source_prompt_sha256="a" * 64,
        )


def test_locked_and_open_decision_domains_cannot_overlap():
    with pytest.raises(ValueError, match="both locked and open"):
        WritingExecutionProfile.model_validate(_profile(
            locked_decision_domains=["TITLE"],
            open_decision_domains=["TITLE", "THESIS"],
        ))


def test_execution_profile_must_be_bound_to_the_exact_original_prompt():
    with pytest.raises(WritingExecutionProfileError, match="prompt binding mismatch"):
        validate_writing_execution_profile(
            _profile(), _contexts(), source_prompt_sha256="b" * 64,
        )


def test_execution_profile_has_no_whole_task_shape_classifier():
    profile = WritingExecutionProfile.model_validate(_profile())
    assert profile.workflow_contract == "FINANCIAL_ARTICLE_10_STAGE_V1"
    assert not hasattr(profile, "task_shape")
