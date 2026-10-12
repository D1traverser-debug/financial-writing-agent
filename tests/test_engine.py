from pathlib import Path

import pytest

from financial_writing_agent.engine import WorkflowError, WritingEngine
from financial_writing_agent.models import ArtifactKind, GateStatus, Stage, TaskContract
from financial_writing_agent.store import SQLiteStateStore

ROOT = Path(__file__).resolve().parents[1]


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


def test_complete_cannot_be_reached_through_raw_transition(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(prompt="write"))
    state.stage = Stage.FINAL_AUDIT
    with pytest.raises(WorkflowError, match=r"use complete\(\)"):
        engine.transition(state, Stage.COMPLETE, reason="attempt semantic bypass")
    assert state.stage == Stage.FINAL_AUDIT


def test_blocked_cannot_be_entered_through_raw_transition(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(prompt="write"))
    with pytest.raises(WorkflowError, match=r"use block\(\)"):
        engine.transition(state, Stage.BLOCKED, reason="attempt recovery bypass")
    assert state.stage == Stage.INTAKE
    assert state.blocked_reason is None
    assert state.blocked_resume_stage is None


def test_blocked_cannot_be_left_through_raw_transition(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(prompt="write"))
    blocked = engine.block(state, "web unavailable", resume_stage=Stage.RESEARCH)
    assert blocked.stage == Stage.BLOCKED
    assert blocked.blocked_reason == "web unavailable"
    with pytest.raises(WorkflowError, match=r"use resume_blocked\(\)"):
        engine.transition(blocked, Stage.RESEARCH, reason="attempt stale recovery bypass")
    resumed = engine.resume_blocked(blocked)
    assert resumed.stage == Stage.RESEARCH
    assert resumed.blocked_reason is None
    assert resumed.blocked_from_stage is None
    assert resumed.blocked_resume_stage is None


def test_private_transition_primitive_is_engine_local_only():
    offenders: list[str] = []
    for path in (ROOT / "financial_writing_agent").rglob("*.py"):
        if path.name == "engine.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "_apply_transition(" in text:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


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
