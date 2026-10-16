from copy import deepcopy

import pytest

from financial_writing_agent.current_admission import (
    CurrentAdmissionError,
    advance_state,
    apply_task_requirement_change,
    build_initial_state,
    requirement_context_for_scope,
    validate_state,
)
from financial_writing_agent.task_requirements import REQUIREMENT_CONTRACT_VERSION


EXECUTOR = "TEST:GITHUB_CHAT"


def _state():
    return build_initial_state(
        task_id="requirement-authority-test",
        prompt="跨境电商",
        source_refs=[],
        executor_identity=EXECUTOR,
    )


def _req(requirement_id="deep-shape", stage="EDITORIAL", statement="Deep只做横向比较"):
    return {
        "requirement_id": requirement_id,
        "statement": statement,
        "scopes": ["FINANCE_DEEP"],
        "affects_from_stage": stage,
        "evidence_ref": "chat://user/requirement-1",
        "source_kind": "USER_EXPLICIT",
    }


def test_new_current_task_binds_empty_requirement_authority():
    state = _state()
    assert state["task_requirement_contract_version"] == REQUIREMENT_CONTRACT_VERSION
    assert state["task_requirement_authority"]["revision"] == 0
    assert state["task_requirement_authority"]["active_requirements"] == []
    receipt = state["execution_receipts"][-1]["input_bindings"]
    assert receipt["task_requirement_digest"] == state["task_requirement_digest"]
    assert receipt["task_requirement_revision"] == 0


def test_requirement_change_is_task_authority_not_feedback_and_stage_receipts_bind_it():
    state = _state()
    changed = apply_task_requirement_change(
        state,
        previous_state_blob_sha="a" * 40,
        executor_identity=EXECUTOR,
        evidence_ref="chat://user/requirement-1",
        upserts=[_req()],
    )
    assert changed["current_stage"] == "INTAKE"
    assert changed["task_requirement_authority"]["revision"] == 1
    context = requirement_context_for_scope(changed, "FINANCE_DEEP")
    assert [item["requirement_id"] for item in context["requirements"]] == ["deep-shape"]
    assert context["digest"] == changed["task_requirement_digest"]

    advanced = advance_state(
        changed,
        previous_state_blob_sha="b" * 40,
        executor_identity=EXECUTOR,
    )
    assert advanced["current_stage"] == "RESEARCH"
    receipt = advanced["execution_receipts"][-1]["input_bindings"]
    assert receipt["task_requirement_revision"] == 1
    assert receipt["task_requirement_digest"] == advanced["task_requirement_digest"]


def test_late_requirement_change_reexecutes_current_affected_stage():
    state = _state()
    state = advance_state(
        state,
        previous_state_blob_sha="a" * 40,
        executor_identity=EXECUTOR,
    )
    assert state["current_stage"] == "RESEARCH"

    changed = apply_task_requirement_change(
        state,
        previous_state_blob_sha="b" * 40,
        executor_identity=EXECUTOR,
        evidence_ref="chat://user/requirement-research",
        upserts=[_req(requirement_id="scope-reset", stage="RESEARCH", statement="研究范围发生材料性变化")],
    )
    assert changed["current_stage"] == "RESEARCH"
    assert changed["status"] == "IN_PROGRESS"
    assert "re-execute RESEARCH" in changed["next_action"]
    assert "revision 1" in changed["next_action"]
    latest = changed["execution_receipts"][-1]
    assert latest["capability_id"] == "github_chat_requirement_governance"
    assert latest["input_bindings"]["affected_from_stage"] == "RESEARCH"


def test_requirement_cannot_invent_noncanonical_invalidation_target():
    state = _state()
    with pytest.raises(CurrentAdmissionError, match="unsupported affects_from_stage"):
        apply_task_requirement_change(
            state,
            previous_state_blob_sha="a" * 40,
            executor_identity=EXECUTOR,
            evidence_ref="chat://user/requirement-intake",
            upserts=[_req(requirement_id="invalid-target", stage="INTAKE", statement="不能发明新的回退拓扑")],
        )


def test_requirement_authority_tamper_is_detected():
    state = _state()
    state = apply_task_requirement_change(
        state,
        previous_state_blob_sha="a" * 40,
        executor_identity=EXECUTOR,
        evidence_ref="chat://user/requirement-1",
        upserts=[_req()],
    )
    tampered = deepcopy(state)
    tampered["task_requirement_authority"]["active_requirements"][0]["statement"] = "被静默改写"
    with pytest.raises(CurrentAdmissionError, match="digest mismatch"):
        validate_state(tampered)


def test_requirement_replacement_preserves_history_and_updates_digest():
    state = _state()
    state = apply_task_requirement_change(
        state,
        previous_state_blob_sha="a" * 40,
        executor_identity=EXECUTOR,
        evidence_ref="chat://user/v1",
        upserts=[_req(statement="Deep携带全量公司池")],
    )
    old_digest = state["task_requirement_digest"]
    state = apply_task_requirement_change(
        state,
        previous_state_blob_sha="b" * 40,
        executor_identity=EXECUTOR,
        evidence_ref="chat://user/v2",
        upserts=[_req(statement="Deep不放全量附录池，只做横向比较")],
    )
    assert state["task_requirement_authority"]["revision"] == 2
    assert state["task_requirement_digest"] != old_digest
    assert state["task_requirement_authority"]["active_requirements"][0]["statement"] == "Deep不放全量附录池，只做横向比较"
    actions = [item["action"] for item in state["task_requirement_authority"]["history"]]
    assert actions == ["ADD", "REPLACE"]
