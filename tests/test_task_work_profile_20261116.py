from __future__ import annotations

import pytest

from financial_writing_agent.writing_execution_profile import (
    WritingExecutionProfile,
    WritingExecutionProfileError,
    validate_writing_execution_profile,
)


ACTIVE_SCOPES = ("ALL", "RESEARCH", "PRIVATE_RESEARCH", "FINANCE_DEEP", "FINANCE_BROAD")


def _contexts(requirements=()):
    result = {}
    for scope in ACTIVE_SCOPES:
        selected = [
            dict(item) for item in requirements
            if "ALL" in item["scopes"] or scope in item["scopes"]
        ]
        result[scope] = {"requirements": selected}
    return result


def _requirement(requirement_id, source_kind="USER_EXPLICIT", scopes=("ALL",)):
    return {
        "requirement_id": requirement_id,
        "statement": f"User {source_kind} requirement {requirement_id}.",
        "scopes": list(scopes),
        "affects_from_stage": "RESEARCH",
        "evidence_ref": f"owner-instruction://{requirement_id}",
        "source_kind": source_kind,
    }


def _domain(
    name,
    *,
    disposition="OPEN",
    scopes=("ALL",),
    requirement_ids=(),
    preference_ids=(),
):
    return {
        "domain": name,
        "disposition": disposition,
        "scopes": list(scopes),
        "requirement_ids": list(requirement_ids),
        "preference_ids": list(preference_ids),
        "rationale": f"Reference rationale for {name}.",
    }


def _profile(**overrides):
    value = {
        "schema_version": "1.1",
        "workflow_contract": "FINANCIAL_ARTICLE_10_STAGE_V1",
        "source_prompt_sha256": "a" * 64,
        "fixed_requirement_ids": [],
        "preference_requirement_ids": [],
        "decision_domains": [
            _domain(name)
            for name in ("THESIS", "ANGLE", "NARRATIVE_ENGINE", "TITLE", "VOICE")
        ],
        "conditional_modules": ["COMPANY_UNIVERSE"],
        "execution_rationale": "The business workflow remains fixed while unspecified editorial choices follow evidence and reader needs.",
    }
    value.update(overrides)
    return value


def test_one_workflow_contract_supports_different_content_led_editorial_decisions():
    event_led = WritingExecutionProfile.model_validate(_profile(
        decision_domains=[
            _domain(name)
            for name in ("THESIS", "EVENT_TRANSMISSION", "COMPANY_COMPARISON", "TITLE")
        ],
    ))
    company_cycle = WritingExecutionProfile.model_validate(_profile(
        decision_domains=[
            _domain(name)
            for name in ("THESIS", "VALUATION_GAP", "COMPANY_DIVERGENCE", "NARRATIVE_ENGINE")
        ],
    ))
    assert event_led.workflow_contract == company_cycle.workflow_contract
    assert event_led.decision_domains != company_cycle.decision_domains


def test_all_active_explicit_requirements_and_preferences_are_bound_exactly():
    requirements = [
        _requirement("fixed-outline"),
        _requirement("corrected-title", "USER_CORRECTION"),
        _requirement("preferred-tone", "USER_PREFERENCE"),
    ]
    profile = _profile(
        fixed_requirement_ids=["fixed-outline", "corrected-title"],
        preference_requirement_ids=["preferred-tone"],
        decision_domains=[
            _domain("OUTLINE", disposition="LOCKED", requirement_ids=["fixed-outline"]),
            _domain("TITLE", disposition="LOCKED", requirement_ids=["corrected-title"]),
            _domain("VOICE", preference_ids=["preferred-tone"]),
        ],
    )
    result = validate_writing_execution_profile(
        profile, _contexts(requirements), source_prompt_sha256="a" * 64,
    )
    assert set(result["fixed_requirement_ids"]) == {"fixed-outline", "corrected-title"}
    assert result["preference_requirement_ids"] == ["preferred-tone"]


def test_missing_or_invented_requirement_ids_fail_closed():
    requirements = [_requirement("fixed-title")]
    with pytest.raises(WritingExecutionProfileError, match="fixed requirement IDs"):
        validate_writing_execution_profile(
            _profile(), _contexts(requirements), source_prompt_sha256="a" * 64,
        )
    invented = _profile(
        fixed_requirement_ids=["invented-id"],
        decision_domains=[
            _domain("TITLE", disposition="LOCKED", requirement_ids=["invented-id"]),
        ],
    )
    with pytest.raises(WritingExecutionProfileError, match="fixed requirement IDs"):
        validate_writing_execution_profile(
            invented, _contexts(requirements), source_prompt_sha256="a" * 64,
        )


def test_preferences_cannot_be_promoted_to_hard_requirements():
    requirements = [_requirement("preferred-tone", "USER_PREFERENCE")]
    profile = _profile(
        fixed_requirement_ids=["preferred-tone"],
        decision_domains=[
            _domain("VOICE", disposition="LOCKED", requirement_ids=["preferred-tone"]),
        ],
    )
    with pytest.raises(WritingExecutionProfileError, match="fixed requirement IDs"):
        validate_writing_execution_profile(
            profile, _contexts(requirements), source_prompt_sha256="a" * 64,
        )


def test_locked_and_open_decision_domains_cannot_overlap_in_the_same_scope():
    with pytest.raises(ValueError, match="overlapping dispositions"):
        WritingExecutionProfile.model_validate(_profile(
            decision_domains=[
                _domain("TITLE", disposition="LOCKED", requirement_ids=["fixed-title"]),
                _domain("TITLE", disposition="OPEN"),
            ],
        ))


def test_execution_profile_must_be_bound_to_the_exact_original_prompt():
    with pytest.raises(WritingExecutionProfileError, match="prompt binding mismatch"):
        validate_writing_execution_profile(
            _profile(), _contexts(), source_prompt_sha256="b" * 64,
        )


def test_execution_profile_has_no_whole_task_shape_classifier():
    profile = WritingExecutionProfile.model_validate(_profile())
    assert profile.workflow_contract == "FINANCIAL_ARTICLE_10_STAGE_V1"
    assert profile.schema_version == "1.1"
    assert not hasattr(profile, "task_shape")
