from financial_writing_agent.methodology_receipts import (
    ARTIFACT_IO_HOOKS,
    EVOLUTION_HOOKS,
    record_artifact_io_receipt,
    record_learning_evolution_receipt,
)
from financial_writing_agent.models import Artifact, ArtifactKind, GateRecord, GateStatus, TaskContract, WritingState


def _state() -> WritingState:
    return WritingState(contract=TaskContract(task_id="receipt-test", prompt="测试财经文章"))


def test_learning_receipt_is_action_scoped_and_cannot_self_certify():
    state = _state()
    state.working["learning_samples"] = [
        {
            "sample_type": "USER_REJECTION",
            "summary": "用户明确拒绝当前文章质量",
            "promotion_status": "RAW_EVIDENCE_ONLY",
        }
    ]

    run = record_learning_evolution_receipt(state)

    assert run["profile_id"] == "evolution"
    assert run["profile_version"] == "1.0"
    assert run["receipt_contract_version"] == "1.2"
    assert run["verification_status"] == "UNVERIFIED_OWNER_RECEIPT"
    assert set(run["hook_assessments"]) == set(EVOLUTION_HOOKS)
    assert run["invoked_hooks"] == ["learning_evidence_location"]
    assert run["hook_assessments"]["eval_or_regression_promotion_path"]["status"] == "NOT_APPLICABLE_FOR_ACTION"
    assert "PASS" not in run.values()


def test_artifact_receipt_assesses_every_hook_without_fake_invocation():
    state = _state()
    state.gates["mechanical_audit"] = GateRecord(
        name="mechanical_audit",
        status=GateStatus.PASS,
        evidence=["rendered_pages=2", "underlines=0"],
    )
    state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(
        kind=ArtifactKind.FINANCE_DEEP_DOCX,
        path="/tmp/deep.docx",
        exists=True,
        sha256="a" * 64,
    )

    run = record_artifact_io_receipt(state)

    assert run["receipt_contract_version"] == "1.2"
    assert run["profile_id"] == "artifact_io"
    assert set(run["hook_assessments"]) == set(ARTIFACT_IO_HOOKS)
    assert "post_write_verification_method" in run["invoked_hooks"]
    assert run["hook_assessments"]["delete_and_retention_rules"]["status"] == "NOT_APPLICABLE_FOR_ACTION"
    assert run["hook_assessments"]["external_artifact_vault_if_any"]["status"] == "NOT_APPLICABLE_FOR_ACTION"
    assert run["verification_status"] == "UNVERIFIED_OWNER_RECEIPT"
    assert any("external_ref_and_semantic_assessment_required" in item["detail"] for item in state.trace if item.get("event") == "METHODOLOGY_PROFILE_RUN")


def test_artifact_receipt_fails_closed_without_mechanical_pass():
    state = _state()
    state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(
        kind=ArtifactKind.FINANCE_DEEP_DOCX,
        path="/tmp/deep.docx",
        exists=True,
        sha256="b" * 64,
    )

    try:
        record_artifact_io_receipt(state)
    except ValueError as exc:
        assert "mechanical_audit PASS" in str(exc)
    else:
        raise AssertionError("artifact receipt must not exist without mechanical PASS")


def test_artifact_receipt_fails_closed_without_hash_bound_output():
    state = _state()
    state.gates["mechanical_audit"] = GateRecord(name="mechanical_audit", status=GateStatus.PASS)
    state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(
        kind=ArtifactKind.FINANCE_DEEP_DOCX,
        path="/tmp/deep.docx",
        exists=True,
        sha256=None,
    )

    try:
        record_artifact_io_receipt(state)
    except ValueError as exc:
        assert "hash-bound artifact" in str(exc)
    else:
        raise AssertionError("artifact receipt must require stable artifact identity")
