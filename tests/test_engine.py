import pytest

from financial_writing_agent.engine import WorkflowError, WritingEngine
from financial_writing_agent.models import ArtifactKind, DistributionMode, GateStatus, Stage, TaskContract
from financial_writing_agent.store import SQLiteStateStore


def _seed_completion_gates(engine: WritingEngine, state, *, knowledge=GateStatus.N_A):
    for name in engine._required_completion_gates(state):
        if name == "knowledge_sync":
            state.set_gate(name, knowledge, ["knowledge boundary"])
        else:
            state.set_gate(name, GateStatus.PASS, [f"{name} ok"])


def test_start_is_first_trace(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(prompt="根据两个链接写文章"))
    assert state.stage == Stage.INTAKE
    assert state.trace[0].event == "RUNTIME_STARTED"
    assert state.gates["runtime_initialized"].status == GateStatus.PASS
    assert state.gates["knowledge_sync"].status == GateStatus.NOT_RUN


def test_illegal_skip_is_blocked_by_engine(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(prompt="write"))
    with pytest.raises(WorkflowError):
        engine.transition(state, Stage.DRAFT)


def test_dual_word_outputs_are_required():
    c = TaskContract(prompt="x")
    assert set(c.required_outputs) == {
        ArtifactKind.AUDIT_DOCX,
        ArtifactKind.FINANCE_DEEP_DOCX,
        ArtifactKind.FINANCE_BROAD_DOCX,
    }


def test_cannot_complete_when_mandatory_gate_is_absent(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(prompt="x"))
    state.stage = Stage.FINAL_AUDIT
    _seed_completion_gates(engine, state)
    state.gates.pop("style_audit")
    with pytest.raises(WorkflowError, match="Mandatory completion gates missing"):
        engine.complete(state)


def test_cannot_complete_before_knowledge_sync_decision(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(prompt="x"))
    state.stage = Stage.FINAL_AUDIT
    _seed_completion_gates(engine, state, knowledge=GateStatus.NOT_RUN)
    with pytest.raises(WorkflowError, match="knowledge_sync"):
        engine.complete(state)


def test_cannot_complete_without_required_outputs_after_knowledge_decision(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(prompt="x"))
    state.stage = Stage.FINAL_AUDIT
    _seed_completion_gates(engine, state)
    with pytest.raises(WorkflowError, match="Missing required outputs"):
        engine.complete(state)


def test_completion_rechecks_artifact_files_instead_of_trusting_stale_exists_flag(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    contract = TaskContract(prompt="x", required_outputs=[ArtifactKind.AUDIT_DOCX])
    state = engine.start(contract)
    state.stage = Stage.FINAL_AUDIT
    _seed_completion_gates(engine, state)
    path = tmp_path / "audit.docx"
    path.write_bytes(b"valid")
    state.add_artifact(ArtifactKind.AUDIT_DOCX, str(path))
    path.unlink()

    with pytest.raises(WorkflowError, match="after readback"):
        engine.complete(state)


def test_completion_rechecks_artifact_checksum(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    contract = TaskContract(prompt="x", required_outputs=[ArtifactKind.AUDIT_DOCX])
    state = engine.start(contract)
    state.stage = Stage.FINAL_AUDIT
    _seed_completion_gates(engine, state)
    path = tmp_path / "audit.docx"
    path.write_bytes(b"original")
    state.add_artifact(ArtifactKind.AUDIT_DOCX, str(path))
    state.artifacts[ArtifactKind.AUDIT_DOCX].sha256 = engine._sha256(path)
    path.write_bytes(b"tampered")

    with pytest.raises(WorkflowError, match="checksum mismatch"):
        engine.complete(state)


def test_completion_requires_every_final_acceptance_criterion(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    contract = TaskContract(
        prompt="x",
        distribution_mode=DistributionMode.FINANCE_DEEP,
        required_outputs=[ArtifactKind.AUDIT_DOCX],
    )
    state = engine.start(contract)
    state.stage = Stage.FINAL_AUDIT
    _seed_completion_gates(engine, state)
    path = tmp_path / "audit.docx"
    path.write_bytes(b"valid")
    state.add_artifact(ArtifactKind.AUDIT_DOCX, str(path))

    required = engine._required_final_evidence_keys(state)
    missing_key = "FINANCE_DEEP.opening_payoff"
    assert missing_key in required
    state.working["final_audit"] = {
        "acceptance_evidence": [
            f"{key}: concrete frozen-final evidence"
            for key in sorted(required - {missing_key})
        ]
    }
    with pytest.raises(WorkflowError, match="opening_payoff"):
        engine.complete(state)


def test_revision_invalidation_clears_stale_downstream_passes_and_outputs(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(prompt="x"))
    state.stage = Stage.FINAL_AUDIT
    for name in [
        "research_output",
        "research_audit",
        "editorial_plan",
        "acceptance_contract",
        "title_audit",
        "draft_output",
        "style_audit",
        "editorial_audit",
        "delivery_output",
        "mechanical_audit",
        "final_audit",
    ]:
        state.set_gate(name, GateStatus.PASS, ["old pass"])
    state.set_gate("knowledge_sync", GateStatus.PASS, ["old receipt"])
    path = tmp_path / "old.docx"
    path.write_bytes(b"old")
    state.add_artifact(ArtifactKind.FINANCE_DEEP_DOCX, str(path))

    engine.invalidate_for_revision(state, Stage.RESEARCH, reason="factual defect")

    assert state.gates["research_output"].status == GateStatus.NOT_RUN
    assert state.gates["final_audit"].status == GateStatus.NOT_RUN
    assert state.gates["knowledge_sync"].status == GateStatus.NOT_RUN
    assert ArtifactKind.FINANCE_DEEP_DOCX not in state.artifacts
    assert state.working["revision_history"][-1]["target_stage"] == "RESEARCH"
