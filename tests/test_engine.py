import pytest

from financial_writing_agent.engine import WorkflowError, WritingEngine
from financial_writing_agent.models import ArtifactKind, GateStatus, Stage, TaskContract
from financial_writing_agent.store import SQLiteStateStore


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


def test_cannot_complete_before_knowledge_sync_decision(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(prompt="x"))
    state.stage = Stage.FINAL_AUDIT
    for name in ["research", "editorial", "mechanical", "final"]:
        state.set_gate(name, GateStatus.PASS, ["ok"])
    with pytest.raises(WorkflowError, match="knowledge_sync"):
        engine.complete(state)


def test_cannot_complete_without_required_outputs_after_knowledge_decision(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(prompt="x"))
    state.stage = Stage.FINAL_AUDIT
    state.set_gate("knowledge_sync", GateStatus.N_A, ["no connected write target"])
    for name in ["research", "editorial", "mechanical", "final"]:
        state.set_gate(name, GateStatus.PASS, ["ok"])
    with pytest.raises(WorkflowError, match="Missing required outputs"):
        engine.complete(state)
