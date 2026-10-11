from financial_writing_agent.methodology_receipts import (
    ARTIFACT_IO_HOOKS,
    EVOLUTION_HOOKS,
    OPERATIONAL_HYGIENE_HOOKS,
    record_artifact_io_receipt,
    record_learning_evolution_receipt,
    record_system_impact_hygiene_receipt,
)
from financial_writing_agent.models import Artifact, ArtifactKind, GateRecord, GateStatus, TaskContract, WritingState
from financial_writing_agent.system_impact import apply_system_impact_review, ensure_system_impact_signal_for_latest_sample


def _state() -> WritingState:
    return WritingState(contract=TaskContract(task_id="receipt-test", prompt="测试财经文章"))


def _assert_action_binding(run, state):
    binding = run["action_binding"]
    assert binding["task_id"] == state.contract.task_id
    assert binding["stage"] == state.stage.value
    assert binding["action_id"] == run["activation_id"]
    assert binding["subject_bindings"]
    assert binding["input_bindings"]


def test_learning_receipt_is_action_scoped_and_cannot_self_certify():
    state = _state()
    state.working["learning_samples"] = [{"sample_type":"USER_REJECTION","summary":"用户明确拒绝当前文章质量","promotion_status":"RAW_EVIDENCE_ONLY"}]
    signal = ensure_system_impact_signal_for_latest_sample(state)
    run = record_learning_evolution_receipt(state)
    assert run["profile_id"] == "evolution"
    assert run["profile_version"] == "1.0"
    assert run["receipt_contract_version"] == "1.3"
    assert run["verification_status"] == "UNVERIFIED_OWNER_RECEIPT"
    assert set(run["hook_assessments"]) == set(EVOLUTION_HOOKS)
    assert run["invoked_hooks"] == ["learning_evidence_location"]
    assert run["hook_assessments"]["eval_or_regression_promotion_path"]["status"] == "NOT_APPLICABLE_FOR_ACTION"
    assert "PASS" not in run.values()
    _assert_action_binding(run, state)
    assert run["action_binding"]["subject_bindings"]["learning_sample_ref"].endswith("/0")
    assert run["action_binding"]["subject_bindings"]["system_impact_signal_ref"].endswith(signal["signal_id"])


def test_system_impact_review_emits_operational_hygiene_receipt_without_self_certifying():
    state = _state()
    state.working["learning_samples"] = [{"sample_type":"USER_REJECTION","summary":"文章只做了局部修补","promotion_status":"RAW_EVIDENCE_ONLY"}]
    signal = ensure_system_impact_signal_for_latest_sample(state)
    apply_system_impact_review(
        state,
        signal_id=signal["signal_id"],
        problem_statement="material feedback can be locally patched without system-level review",
        root_cause_layer="RUNTIME_OR_SCHEMA",
        generalization_scope="material financial-writing feedback",
        alternatives=[
            {"mechanism":"add another prompt reminder","failure_mode":"still declaration-only"},
            {"mechanism":"persist owner review obligation","failure_mode":"adds one feedback cold-path action"},
        ],
        selected_mechanism="persist owner review obligation",
        selection_rationale="smallest executable bridge into Universal maintenance",
        authority_surface="WritingState + owner MCP",
        regression_or_eval_plan=["feedback creates obligation", "systemic review creates control signal"],
        evidence_refs=["artifact://rejected-article"],
        decision="SYSTEM_MAINTENANCE_REQUIRED",
        decision_reason="the defect is a repeatable execution-policy gap",
    )
    run = record_system_impact_hygiene_receipt(state, signal["signal_id"])
    assert run["profile_id"] == "operational_hygiene"
    assert run["verification_status"] == "UNVERIFIED_OWNER_RECEIPT"
    assert set(run["hook_assessments"]) == set(OPERATIONAL_HYGIENE_HOOKS)
    assert "observability_or_incident_evidence_location" in run["invoked_hooks"]
    assert "self_maintenance_trigger_path" in run["invoked_hooks"]
    assert "reliability_or_change_freeze_guard" in run["invoked_hooks"]
    assert run["hook_assessments"]["garbage_collection_owner_and_dependency_rule"]["status"] == "NOT_APPLICABLE_FOR_ACTION"
    _assert_action_binding(run, state)
    assert run["action_binding"]["subject_bindings"]["control_signal_id"].startswith("fwa-")
    assert "PASS" not in run.values()


def test_operational_hygiene_receipt_requires_completed_review():
    state = _state()
    state.working["learning_samples"] = [{"sample_type":"USER_FEEDBACK","summary":"需要系统判断","promotion_status":"RAW_EVIDENCE_ONLY"}]
    signal = ensure_system_impact_signal_for_latest_sample(state)
    try:
        record_system_impact_hygiene_receipt(state, signal["signal_id"])
    except ValueError as exc:
        assert "completed system-impact review" in str(exc)
    else:
        raise AssertionError("operational_hygiene receipt must not exist before review")


def test_artifact_receipt_assesses_every_hook_and_binds_exact_inputs():
    state = _state()
    state.gates["mechanical_audit"] = GateRecord(name="mechanical_audit", status=GateStatus.PASS, evidence=["rendered_pages=2", "underlines=0"])
    state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(kind=ArtifactKind.FINANCE_DEEP_DOCX, path="/tmp/deep.docx", exists=True, sha256="a" * 64)
    run = record_artifact_io_receipt(state)
    assert run["receipt_contract_version"] == "1.3"
    assert run["profile_id"] == "artifact_io"
    assert set(run["hook_assessments"]) == set(ARTIFACT_IO_HOOKS)
    assert "post_write_verification_method" in run["invoked_hooks"]
    assert run["hook_assessments"]["delete_and_retention_rules"]["status"] == "NOT_APPLICABLE_FOR_ACTION"
    assert run["verification_status"] == "UNVERIFIED_OWNER_RECEIPT"
    _assert_action_binding(run, state)
    assert "artifact_set" in run["action_binding"]["input_bindings"]
    assert any(item.event == "METHODOLOGY_PROFILE_RUN" and "action_bound=true" in item.detail for item in state.trace)


def test_artifact_receipt_fails_closed_without_mechanical_pass():
    state = _state()
    state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(kind=ArtifactKind.FINANCE_DEEP_DOCX, path="/tmp/deep.docx", exists=True, sha256="b" * 64)
    try:
        record_artifact_io_receipt(state)
    except ValueError as exc:
        assert "mechanical_audit PASS" in str(exc)
    else:
        raise AssertionError("artifact receipt must not exist without mechanical PASS")


def test_artifact_receipt_fails_closed_without_hash_bound_output():
    state = _state()
    state.gates["mechanical_audit"] = GateRecord(name="mechanical_audit", status=GateStatus.PASS)
    state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(kind=ArtifactKind.FINANCE_DEEP_DOCX, path="/tmp/deep.docx", exists=True, sha256=None)
    try:
        record_artifact_io_receipt(state)
    except ValueError as exc:
        assert "hash-bound artifact" in str(exc)
    else:
        raise AssertionError("artifact receipt must require stable artifact identity")
