from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from financial_writing_agent.writing_execution_profile import (
    WritingExecutionProfileError,
    validate_writing_execution_profile,
)


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals" / "execution_profile_semantic_cases.json"
ACTIVE_SCOPES = (
    "ALL", "RESEARCH", "PRIVATE_RESEARCH", "FINANCE_DEEP",
    "FINANCE_BROAD", "PLATFORM_INTERACTION", "DELIVERY",
)


def _contexts(requirements):
    result = {}
    for scope in ACTIVE_SCOPES:
        selected = [
            item for item in requirements
            if "ALL" in item["scopes"] or scope in item["scopes"]
        ]
        result[scope] = {
            "contract_version": "1.0",
            "revision": 1,
            "digest": "a" * 64,
            "requirements": selected,
        }
    return result


def _profile(prompt, requirements, domains):
    fixed = sorted(
        item["requirement_id"] for item in requirements
        if item["source_kind"] in {"USER_EXPLICIT", "USER_CORRECTION"}
    )
    preferences = sorted(
        item["requirement_id"] for item in requirements
        if item["source_kind"] == "USER_PREFERENCE"
    )
    return {
        "schema_version": "1.1",
        "workflow_contract": "FINANCIAL_ARTICLE_10_STAGE_V1",
        "source_prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "fixed_requirement_ids": fixed,
        "preference_requirement_ids": preferences,
        "decision_domains": domains,
        "conditional_modules": [],
        "execution_rationale": "Diagnostic reference profile; live semantic execution is not claimed.",
    }


def test_real_prompt_semantic_reference_cases_are_authority_bound():
    corpus = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    assert corpus["assurance"] == "CHAT_SELF_REVIEW_DIAGNOSTIC_ONLY"
    assert corpus["promotion_eligible"] is False
    assert len(corpus["cases"]) >= 4

    for case in corpus["cases"]:
        profile = _profile(
            case["original_prompt"],
            case["requirements"],
            case["expected_decision_domains"],
        )
        validated = validate_writing_execution_profile(
            profile,
            _contexts(case["requirements"]),
            source_prompt_sha256=profile["source_prompt_sha256"],
        )
        assert validated["decision_domains"] == case["expected_decision_domains"]


def test_vague_topic_does_not_lock_company_universe_or_story_form():
    corpus = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    case = next(x for x in corpus["cases"] if x["case_id"] == "ice-snow-economy-20261013")
    locked = {
        item["domain"] for item in case["expected_decision_domains"]
        if item["disposition"] == "LOCKED"
    }
    assert locked == {"TOPIC_SCOPE"}
    assert "COMPANY_UNIVERSE" not in locked
    assert "NARRATIVE_ENGINE" not in locked
    assert "TITLE" not in locked


def test_user_supplied_company_candidates_do_not_lock_publication_selection():
    corpus = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    case = next(x for x in corpus["cases"] if x["case_id"] == "meta-muse-wonder-ai-20261013")
    by_name = {item["domain"]: item for item in case["expected_decision_domains"]}
    assert by_name["RESEARCH_CANDIDATES"]["disposition"] == "LOCKED"
    assert by_name["PUBLICATION_SELECTION"]["disposition"] == "OPEN"
    assert by_name["COMPANY_CLASSIFICATION"]["disposition"] == "OPEN"


def test_user_supplied_thesis_is_a_research_question_not_a_locked_conclusion():
    corpus = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    for case_id in ("huangjiu-high-end-channel-20261015", "fw-20261012-ai-security-6dd14859"):
        case = next(x for x in corpus["cases"] if x["case_id"] == case_id)
        by_name = {item["domain"]: item for item in case["expected_decision_domains"]}
        assert by_name["FINAL_CAUSAL_CONCLUSION"]["disposition"] == "OPEN"


def test_locked_domain_without_explicit_or_corrective_requirement_is_rejected():
    prompt = "ice snow"
    requirement = {
        "requirement_id": "topic",
        "statement": "Write about ice and snow economy.",
        "scopes": ["ALL"],
        "affects_from_stage": "RESEARCH",
        "evidence_ref": "owner-instruction://topic",
        "source_kind": "USER_EXPLICIT",
    }
    profile = _profile(prompt, [requirement], [{
        "domain": "COMPANY_SCOPE",
        "disposition": "LOCKED",
        "scopes": ["ALL"],
        "requirement_ids": [],
        "preference_ids": [],
        "rationale": "No explicit scope lock exists.",
    }])
    with pytest.raises(WritingExecutionProfileError):
        validate_writing_execution_profile(
            profile, _contexts([requirement]),
            source_prompt_sha256=profile["source_prompt_sha256"],
        )


def test_open_domain_cannot_carry_a_hard_requirement_id():
    prompt = "compare three companies only"
    requirement = {
        "requirement_id": "three-company-only",
        "statement": "Only compare the three named companies.",
        "scopes": ["RESEARCH", "FINANCE_DEEP"],
        "affects_from_stage": "RESEARCH",
        "evidence_ref": "owner-instruction://three-company-only",
        "source_kind": "USER_EXPLICIT",
    }
    profile = _profile(prompt, [requirement], [{
        "domain": "COMPANY_SCOPE",
        "disposition": "OPEN",
        "scopes": ["RESEARCH", "FINANCE_DEEP"],
        "requirement_ids": ["three-company-only"],
        "preference_ids": [],
        "rationale": "Incorrectly treated explicit scope as open.",
    }])
    with pytest.raises(WritingExecutionProfileError):
        validate_writing_execution_profile(
            profile, _contexts([requirement]),
            source_prompt_sha256=profile["source_prompt_sha256"],
        )


def test_preference_can_guide_open_domain_but_cannot_create_a_lock():
    prompt = "I prefer concise prose."
    preference = {
        "requirement_id": "concise-preference",
        "statement": "Prefer concise prose.",
        "scopes": ["ALL"],
        "affects_from_stage": "DRAFT",
        "evidence_ref": "owner-preference://concise",
        "source_kind": "USER_PREFERENCE",
    }
    open_profile = _profile(prompt, [preference], [{
        "domain": "VOICE_AND_LENGTH",
        "disposition": "OPEN",
        "scopes": ["ALL"],
        "requirement_ids": [],
        "preference_ids": ["concise-preference"],
        "rationale": "Concision guides the choice without fixing a universal length.",
    }])
    validate_writing_execution_profile(
        open_profile, _contexts([preference]),
        source_prompt_sha256=open_profile["source_prompt_sha256"],
    )

    locked_profile = _profile(prompt, [preference], [{
        "domain": "VOICE_AND_LENGTH",
        "disposition": "LOCKED",
        "scopes": ["ALL"],
        "requirement_ids": [],
        "preference_ids": ["concise-preference"],
        "rationale": "Incorrectly promoted a preference to a lock.",
    }])
    with pytest.raises(WritingExecutionProfileError):
        validate_writing_execution_profile(
            locked_profile, _contexts([preference]),
            source_prompt_sha256=locked_profile["source_prompt_sha256"],
        )


def test_domain_binding_cannot_widen_requirement_scope():
    prompt = "Deep-only scope"
    requirement = {
        "requirement_id": "deep-only",
        "statement": "This requirement applies only to Deep.",
        "scopes": ["FINANCE_DEEP"],
        "affects_from_stage": "RESEARCH",
        "evidence_ref": "owner-instruction://deep-only",
        "source_kind": "USER_EXPLICIT",
    }
    profile = _profile(prompt, [requirement], [{
        "domain": "COMPANY_SCOPE",
        "disposition": "LOCKED",
        "scopes": ["ALL"],
        "requirement_ids": ["deep-only"],
        "preference_ids": [],
        "rationale": "Incorrectly widened a Deep-only requirement to all products.",
    }])
    with pytest.raises(WritingExecutionProfileError):
        validate_writing_execution_profile(
            profile, _contexts([requirement]),
            source_prompt_sha256=profile["source_prompt_sha256"],
        )


def test_one_domain_can_be_locked_and_open_only_in_non_overlapping_product_scopes():
    prompt = "Deep is limited; Broad remains editorially open."
    requirement = {
        "requirement_id": "deep-only",
        "statement": "Limit Deep to the named comparison set.",
        "scopes": ["FINANCE_DEEP"],
        "affects_from_stage": "RESEARCH",
        "evidence_ref": "owner-instruction://deep-only",
        "source_kind": "USER_EXPLICIT",
    }
    profile = _profile(prompt, [requirement], [
        {
            "domain": "COMPANY_SCOPE",
            "disposition": "LOCKED",
            "scopes": ["FINANCE_DEEP"],
            "requirement_ids": ["deep-only"],
            "preference_ids": [],
            "rationale": "The Deep comparison scope is explicitly bounded.",
        },
        {
            "domain": "COMPANY_SCOPE",
            "disposition": "OPEN",
            "scopes": ["FINANCE_BROAD"],
            "requirement_ids": [],
            "preference_ids": [],
            "rationale": "No equivalent Broad company-scope restriction exists.",
        },
    ])
    validate_writing_execution_profile(
        profile, _contexts([requirement]),
        source_prompt_sha256=profile["source_prompt_sha256"],
    )


def test_every_active_fixed_requirement_must_be_mapped_to_a_decision_domain():
    prompt = "only compare three companies"
    requirement = {
        "requirement_id": "three-company-only",
        "statement": "Only compare the three named companies.",
        "scopes": ["RESEARCH", "FINANCE_DEEP"],
        "affects_from_stage": "RESEARCH",
        "evidence_ref": "owner-instruction://three-company-only",
        "source_kind": "USER_EXPLICIT",
    }
    profile = _profile(prompt, [requirement], [{
        "domain": "THESIS",
        "disposition": "OPEN",
        "scopes": ["ALL"],
        "requirement_ids": [],
        "preference_ids": [],
        "rationale": "No binding requirement is mapped here.",
    }])
    with pytest.raises(WritingExecutionProfileError, match="do not map every active fixed requirement"):
        validate_writing_execution_profile(
            profile, _contexts([requirement]),
            source_prompt_sha256=profile["source_prompt_sha256"],
        )


def test_every_active_preference_must_be_mapped_without_becoming_a_lock():
    prompt = "I prefer concise prose."
    preference = {
        "requirement_id": "concise-preference",
        "statement": "Prefer concise prose.",
        "scopes": ["ALL"],
        "affects_from_stage": "DRAFT",
        "evidence_ref": "owner-preference://concise",
        "source_kind": "USER_PREFERENCE",
    }
    profile = _profile(prompt, [preference], [{
        "domain": "VOICE",
        "disposition": "OPEN",
        "scopes": ["ALL"],
        "requirement_ids": [],
        "preference_ids": [],
        "rationale": "No preference is mapped to this domain.",
    }])
    with pytest.raises(WritingExecutionProfileError, match="do not map every active preference"):
        validate_writing_execution_profile(
            profile, _contexts([preference]),
            source_prompt_sha256=profile["source_prompt_sha256"],
        )
