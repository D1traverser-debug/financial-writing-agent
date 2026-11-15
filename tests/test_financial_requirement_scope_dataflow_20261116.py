from __future__ import annotations

import pytest

from financial_writing_agent import current_admission
from financial_writing_agent.current_admission import CurrentAdmissionError
from financial_writing_agent.task_requirements import (
    active_requirements_for_scope,
    active_task_scopes,
    apply_requirement_changes,
    empty_requirement_authority,
    requirement_applies_to_task,
    requirement_scopes_for_stage,
    validate_requirement_applicability,
)
from financial_writing_agent.writing_kernel import (
    _due_requirements_for_stage,
    _requirement_contexts_for_pass,
)


def _requirement(requirement_id, scopes, stage):
    return {
        "requirement_id": requirement_id,
        "statement": f"User requirement {requirement_id}",
        "scopes": scopes,
        "affects_from_stage": stage,
        "evidence_ref": f"owner-instruction://{requirement_id}",
        "source_kind": "USER_EXPLICIT",
    }


def _authority(requirements):
    authority, _ = apply_requirement_changes(
        empty_requirement_authority(),
        upserts=requirements,
        retire_ids=None,
        evidence_ref="owner-instruction://scope-regression-suite",
    )
    return authority


def _outputs():
    return [
        "AUDIT_DOCX",
        "FINANCE_DEEP_DOCX",
        "FINANCE_BROAD_DOCX",
        "PLATFORM_INTERACTION_PACK_DOCX",
    ]


def _contexts(authority, outputs):
    scopes = active_task_scopes(outputs)
    return {
        scope: {
            "contract_version": authority["contract_version"],
            "revision": authority["revision"],
            "digest": current_admission.authority_digest(authority),
            "requirements": active_requirements_for_scope(authority, scope),
        }
        for scope in scopes
    }


def test_owner_and_portfolio_use_the_same_stage_scope_projection():
    requirements = [
        _requirement("all-research", ["ALL"], "RESEARCH"),
        _requirement("research-only", ["RESEARCH"], "RESEARCH"),
        _requirement("private-research", ["PRIVATE_RESEARCH"], "RESEARCH"),
        _requirement("deep-research", ["FINANCE_DEEP"], "RESEARCH"),
        _requirement("broad-research", ["FINANCE_BROAD"], "RESEARCH"),
        _requirement("interaction-research", ["PLATFORM_INTERACTION"], "RESEARCH"),
        _requirement("deep-editorial", ["FINANCE_DEEP"], "EDITORIAL"),
        _requirement("broad-title", ["FINANCE_BROAD"], "TITLE"),
        _requirement("interaction-draft", ["PLATFORM_INTERACTION"], "DRAFT"),
        _requirement("delivery-only", ["DELIVERY"], "DELIVERY"),
        _requirement("deep-delivery", ["FINANCE_DEEP"], "DELIVERY"),
    ]
    authority = _authority(requirements)
    outputs = _outputs()
    state = {
        "required_outputs": outputs,
        "task_requirement_authority": authority,
    }
    contexts = _contexts(authority, outputs)

    for stage in ("RESEARCH", "EDITORIAL", "TITLE", "DRAFT", "DELIVERY"):
        owner_ids = {
            item["requirement_id"]
            for item in current_admission._requirements_due_at_stage(state, stage)
        }
        portfolio_ids = set(_due_requirements_for_stage(
            contexts,
            stage=stage,
            modes=["FINANCE_DEEP", "FINANCE_BROAD"],
            interaction_required=True,
        ))
        assert owner_ids == portfolio_ids, stage

    assert set(requirement_scopes_for_stage("RESEARCH", outputs)) == {
        "ALL", "RESEARCH", "PRIVATE_RESEARCH",
        "FINANCE_DEEP", "FINANCE_BROAD", "PLATFORM_INTERACTION",
    }
    assert set(requirement_scopes_for_stage("DELIVERY", outputs)) == {
        "ALL", "DELIVERY", "FINANCE_DEEP", "FINANCE_BROAD", "PLATFORM_INTERACTION",
    }


def test_shared_research_receives_product_scoped_requirements_only_when_due_at_research():
    authority = _authority([
        _requirement("all-research", ["ALL"], "RESEARCH"),
        _requirement("deep-research", ["FINANCE_DEEP"], "RESEARCH"),
        _requirement("deep-editorial", ["FINANCE_DEEP"], "EDITORIAL"),
        _requirement("broad-research", ["FINANCE_BROAD"], "RESEARCH"),
        _requirement("interaction-research", ["PLATFORM_INTERACTION"], "RESEARCH"),
    ])
    contexts = _contexts(authority, _outputs())

    shared = _requirement_contexts_for_pass(
        contexts, "SHARED", stage="RESEARCH",
        modes=["FINANCE_DEEP", "FINANCE_BROAD"],
        interaction_required=True,
    )
    assert set(shared) == {
        "ALL", "RESEARCH", "PRIVATE_RESEARCH",
        "FINANCE_DEEP", "FINANCE_BROAD", "PLATFORM_INTERACTION",
    }
    assert [item["requirement_id"] for item in shared["FINANCE_DEEP"]["requirements"]] == [
        "deep-research"
    ]
    assert [item["requirement_id"] for item in shared["FINANCE_BROAD"]["requirements"]] == [
        "broad-research"
    ]
    assert [item["requirement_id"] for item in shared["PLATFORM_INTERACTION"]["requirements"]] == [
        "interaction-research"
    ]

    deep_editorial = _requirement_contexts_for_pass(
        contexts, "FINANCE_DEEP", stage="EDITORIAL",
        modes=["FINANCE_DEEP", "FINANCE_BROAD"],
        interaction_required=True,
    )
    assert set(deep_editorial) == {"ALL", "FINANCE_DEEP"}
    assert {item["requirement_id"] for item in deep_editorial["FINANCE_DEEP"]["requirements"]} == {
        "deep-research", "deep-editorial",
    }
    assert "broad-research" not in {
        item["requirement_id"] for item in deep_editorial["FINANCE_DEEP"]["requirements"]
    }


def test_broad_only_task_does_not_activate_deep_scope_requirements():
    broad_outputs = ["AUDIT_DOCX", "FINANCE_BROAD_DOCX"]
    deep = _requirement("deep-only", ["FINANCE_DEEP"], "RESEARCH")
    assert "FINANCE_DEEP" not in active_task_scopes(broad_outputs)
    assert not requirement_applies_to_task(deep, broad_outputs)
    assert "FINANCE_BROAD" in requirement_scopes_for_stage("RESEARCH", broad_outputs)

    authority = _authority([
        deep,
        _requirement("broad-only", ["FINANCE_BROAD"], "RESEARCH"),
    ])
    synthetic_state = {
        "required_outputs": broad_outputs,
        "task_requirement_authority": authority,
    }
    due = current_admission._requirements_due_at_stage(synthetic_state, "RESEARCH")
    assert [item["requirement_id"] for item in due] == ["broad-only"]


def test_requirement_change_rejects_unrequested_product_scope_and_impossible_stage_pair():
    prompt = "Only Broad output."
    state = current_admission.build_initial_state(
        task_id="scope-broad-only-20261116",
        prompt=prompt,
        source_refs=[],
        executor_identity="scope-test",
        distribution_mode="FINANCE_BROAD",
        distribution_mode_source="USER_EXPLICIT",
        distribution_mode_override_evidence="Only Broad output",
    )
    with pytest.raises(CurrentAdmissionError, match="scopes do not match the requested outputs"):
        current_admission.apply_task_requirement_change(
            state,
            previous_state_blob_sha="a" * 40,
            executor_identity="scope-test",
            evidence_ref="owner-instruction://deep-only",
            upserts=[_requirement("deep-only", ["FINANCE_DEEP"], "RESEARCH")],
            retire_ids=None,
        )

    with pytest.raises(ValueError, match="incompatible with active scopes"):
        validate_requirement_applicability(
            _requirement("interaction-title", ["PLATFORM_INTERACTION"], "TITLE"),
            _outputs(),
        )


def test_full_universe_requirement_is_active_only_when_its_product_is_requested():
    requirement = _requirement(
        "full_universe_research_pool", ["FINANCE_DEEP"], "RESEARCH",
    )
    assert requirement_applies_to_task(requirement, _outputs())
    assert not requirement_applies_to_task(
        requirement, ["AUDIT_DOCX", "FINANCE_BROAD_DOCX"],
    )
