import pytest

from financial_writing_agent.engine import WorkflowError, WritingEngine
from financial_writing_agent.models import Artifact, ArtifactKind, GateStatus, Stage, TaskContract, WritingState
from financial_writing_agent.store import SQLiteStateStore
from financial_writing_agent.system_impact import (
    apply_system_impact_review,
    ensure_system_impact_signal_for_latest_sample,
    open_system_impact_signals,
    pending_system_impact_reviews,
    system_impact_next_action,
)


def _state(sample_type="USER_REJECTION"):
    state = WritingState(contract=TaskContract(task_id="impact-test", prompt="test"))
    state.working["learning_samples"] = [
        {
            "sample_type": sample_type,
            "summary": "文章质量存在明显问题",
            "source_refs": ["artifact://rejected"],
            "promotion_status": "RAW_EVIDENCE_ONLY",
        }
    ]
    return state


def _review_kwargs(signal_id, *, decision="SYSTEM_MAINTENANCE_REQUIRED"):
    return {
        "signal_id": signal_id,
        "problem_statement": "真实拒稿暴露了可能跨文章复现的执行缺口",
        "root_cause_layer": "RUNTIME_OR_SCHEMA",
        "generalization_scope": "material user writing-quality corrections",
        "alternatives": [
            {"mechanism": "prompt reminder", "failure_mode": "still declaration-only"},
            {"mechanism": "durable runtime obligation", "failure_mode": "adds one feedback-path action"},
            {"mechanism": "always run full maintenance", "failure_mode": "overloads the business hot path"},
        ],
        "selected_mechanism": "durable runtime obligation",
        "selection_rationale": "smallest executable owner-level guard that preserves Universal separation",
        "authority_surface": "WritingState + owner MCP feedback path",
        "regression_or_eval_plan": ["negative feedback creates review obligation", "completion cannot ignore pending review"],
        "evidence_refs": ["artifact://rejected", "repo://maintenance-authority"],
        "decision": decision,
        "decision_reason": "the failure can generalize beyond one paragraph repair" if decision == "SYSTEM_MAINTENANCE_REQUIRED" else "review found no reusable system defect",
    }


def test_negative_learning_sample_creates_durable_system_impact_obligation():
    state = _state()
    signal = ensure_system_impact_signal_for_latest_sample(state)
    assert signal is not None
    assert signal["status"] == "PENDING_REVIEW"
    assert state.working["learning_samples"][0]["system_impact_signal_id"] == signal["signal_id"]
    assert len(pending_system_impact_reviews(state)) == 1
    assert "review_writing_system_impact" in system_impact_next_action(state)


def test_acceptance_or_performance_does_not_auto_create_negative_impact_review():
    for sample_type in ("USER_ACCEPTANCE", "POST_PUBLICATION_PERFORMANCE"):
        state = _state(sample_type)
        assert ensure_system_impact_signal_for_latest_sample(state) is None
        assert open_system_impact_signals(state) == []


def test_system_impact_review_requires_real_alternative_comparison_and_selected_match():
    state = _state()
    signal = ensure_system_impact_signal_for_latest_sample(state)
    kwargs = _review_kwargs(signal["signal_id"])
    kwargs["alternatives"] = [{"mechanism": "only idea", "failure_mode": "could fail"}]
    with pytest.raises(ValueError, match="at least two"):
        apply_system_impact_review(state, **kwargs)

    kwargs = _review_kwargs(signal["signal_id"])
    kwargs["selected_mechanism"] = "missing candidate"
    with pytest.raises(ValueError, match="exactly match"):
        apply_system_impact_review(state, **kwargs)


def test_systemic_review_emits_control_signal_and_closure_needs_verified_refs():
    state = _state()
    signal = ensure_system_impact_signal_for_latest_sample(state)
    reviewed = apply_system_impact_review(state, **_review_kwargs(signal["signal_id"]))
    assert reviewed["status"] == "MAINTENANCE_REQUIRED"
    assert reviewed["control_signal"]["signal_type"] == "USER_REPORTED_SYSTEMIC_FAILURE"
    assert reviewed["control_signal"]["authority"] == "NON_AUTHORITATIVE_CONTROL_SIGNAL"
    assert "operational_hygiene@1.0" in system_impact_next_action(state)

    kwargs = _review_kwargs(signal["signal_id"])
    kwargs.update(
        maintenance_ref="repo://commit/fix",
        validation_refs=["ci://run/1"],
        assurance_ceiling="WIRED",
        remaining_open=["live writing outcome still open"],
    )
    with pytest.raises(ValueError, match="REGRESSION_VERIFIED"):
        apply_system_impact_review(state, **kwargs)

    kwargs["assurance_ceiling"] = "REGRESSION_VERIFIED"
    closed = apply_system_impact_review(state, **kwargs)
    assert closed["status"] == "MAINTENANCE_CLOSED"
    assert closed["maintenance_closure"]["maintenance_ref"] == "repo://commit/fix"
    assert open_system_impact_signals(state) == []


def test_review_core_is_immutable_after_escalation():
    state = _state()
    signal = ensure_system_impact_signal_for_latest_sample(state)
    apply_system_impact_review(state, **_review_kwargs(signal["signal_id"]))
    kwargs = _review_kwargs(signal["signal_id"])
    kwargs["problem_statement"] = "post-hoc rewritten diagnosis"
    kwargs.update(
        maintenance_ref="repo://commit/fix",
        validation_refs=["ci://run/1"],
        assurance_ceiling="REGRESSION_VERIFIED",
    )
    with pytest.raises(ValueError, match="immutable"):
        apply_system_impact_review(state, **kwargs)


def test_engine_completion_cannot_ignore_pending_system_impact_review(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = _state()
    ensure_system_impact_signal_for_latest_sample(state)
    state.stage = Stage.FINAL_AUDIT
    state.set_gate("knowledge_sync", GateStatus.N_A, ["test"])
    for name in ["research", "editorial", "mechanical", "final"]:
        state.set_gate(name, GateStatus.PASS, ["ok"])
    for kind in state.contract.required_outputs:
        state.artifacts[kind] = Artifact(kind=kind, path=f"/tmp/{kind.value}.docx", exists=True, sha256="a" * 64)
    with pytest.raises(WorkflowError, match="system-impact review"):
        engine.assert_can_complete(state)


def test_local_review_closes_obligation_without_claiming_system_change():
    state = _state("USER_FEEDBACK")
    signal = ensure_system_impact_signal_for_latest_sample(state)
    reviewed = apply_system_impact_review(
        state,
        **_review_kwargs(signal["signal_id"], decision="NO_CHANGE_WITH_REASON"),
    )
    assert reviewed["status"] == "REVIEWED_NO_MAINTENANCE"
    assert reviewed["maintenance_closure"] is None
    assert open_system_impact_signals(state) == []
