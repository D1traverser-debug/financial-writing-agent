import pytest

from financial_writing_agent.controller import WorkflowController
from financial_writing_agent.engine import WorkflowError, WritingEngine
from financial_writing_agent.models import ArtifactKind, GateStatus, Stage, TaskContract
from financial_writing_agent.store import SQLiteStateStore


def _semantic_payload(task_id: str, stage: Stage, reviewer: str, author: str):
    return {
        "status": "PASS",
        "evidence": ["stage-separated owner runtime audit"],
        "provenance": {
            "assurance": "INDEPENDENT_EXECUTOR",
            "reviewer_identity": reviewer,
            "author_identity": author,
            "execution_ref": f"{task_id}:{stage.value}:{reviewer}",
        },
    }


def _record_semantic_stage_pass(state, gates):
    """Unit-test the runtime proof shape without pretending it is provider-attested isolation."""
    state.add_trace("EXECUTOR_START", state.stage.value)
    for gate_name, reviewer, author in gates:
        payload = _semantic_payload(state.contract.task_id, state.stage, reviewer, author)
        state.working[gate_name] = payload
        state.set_gate(gate_name, GateStatus.PASS, payload["evidence"])
    state.add_trace("EXECUTOR_END", state.stage.value)


def test_happy_path_trace_is_deterministic_with_semantic_execution_proof(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    ctl = WorkflowController(engine)
    state = engine.start(TaskContract(prompt="根据两个链接写文章"))

    state = ctl.advance(state)
    assert state.stage == Stage.RESEARCH
    state.set_gate("research_output", GateStatus.PASS, ["ledger"])
    state = ctl.advance(state)
    assert state.stage == Stage.RESEARCH_AUDIT
    _record_semantic_stage_pass(
        state,
        [("research_audit", "Financial Writing Research Auditor", "Financial Writing Researcher")],
    )
    state = ctl.advance(state)
    state.set_gate("editorial_plan", GateStatus.PASS, ["topicdna"])
    state = ctl.advance(state)
    state.set_gate("title_audit", GateStatus.PASS, ["title package"])
    state = ctl.advance(state)
    state.set_gate("draft_output", GateStatus.PASS, ["draft frozen"])
    state = ctl.advance(state)
    _record_semantic_stage_pass(
        state,
        [
            ("hook_audit", "Financial Writing Reader Funnel Judge", "Financial Writing Headline Engine / Financial Writing Writer"),
            ("style_audit", "Financial Writing Authorial Prose Judge", "Financial Writing Writer"),
            ("editorial_audit", "Financial Writing Editorial Auditor", "Financial Writing Writer"),
        ],
    )
    state = ctl.advance(state)
    state.set_gate("delivery_output", GateStatus.PASS, ["docx built"])
    state = ctl.advance(state)
    state.set_gate("mechanical_audit", GateStatus.PASS, ["checks"])
    state = ctl.advance(state)

    for kind in state.contract.required_outputs:
        p = tmp_path / f"{kind.value}.docx"
        p.write_bytes(b"stub")
        state.add_artifact(kind, str(p))
    state.set_gate("knowledge_sync", GateStatus.N_A, ["no connected write target in trajectory unit test"])
    _record_semantic_stage_pass(
        state,
        [("final_audit", "Financial Writing Final Auditor", "Financial Writing Writer / Delivery Executor")],
    )
    state = ctl.advance(state)
    assert state.stage == Stage.COMPLETE

    entered = [e.stage.value for e in state.trace if e.event == "STAGE_ENTER"]
    assert entered == [
        "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE", "DRAFT",
        "EDITORIAL_AUDIT", "DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT", "COMPLETE"
    ]


def test_manual_semantic_pass_without_owner_runtime_execution_cannot_advance(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    ctl = WorkflowController(engine)
    state = ctl.advance(engine.start(TaskContract(prompt="旁路测试")))
    state.set_gate("research_output", GateStatus.PASS, ["ledger"])
    state = ctl.advance(state)
    assert state.stage == Stage.RESEARCH_AUDIT

    state.set_gate("research_audit", GateStatus.PASS, ["手填judge"])
    state.working["research_audit"] = _semantic_payload(
        state.contract.task_id,
        Stage.RESEARCH_AUDIT,
        "fake-reviewer",
        "fake-author",
    )
    with pytest.raises(WorkflowError, match="owner-runtime stage execution proof"):
        ctl.advance(state)
    assert state.stage == Stage.RESEARCH_AUDIT


def test_old_semantic_pass_cannot_be_reused_after_reentering_stage(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    ctl = WorkflowController(engine)
    state = ctl.advance(engine.start(TaskContract(prompt="重放测试")))
    state.set_gate("research_output", GateStatus.PASS, ["ledger"])
    state = ctl.advance(state)
    _record_semantic_stage_pass(state, [("research_audit", "judge", "writer")])
    assert state.semantic_gate_proof_valid("research_audit") is True

    # A new STAGE_ENTER invalidates the old execution segment even if stale payload/gate survived.
    state.add_trace("STAGE_ENTER", Stage.RESEARCH_AUDIT.value)
    assert state.semantic_gate_proof_valid("research_audit") is False


def test_state_resume(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    engine = WritingEngine(store)
    ctl = WorkflowController(engine)
    state = engine.start(TaskContract(prompt="继续文章"))
    state = ctl.advance(state)
    state.set_gate("research_output", GateStatus.PASS, ["done"])
    store.save(state)

    loaded = store.load(state.contract.task_id)
    assert loaded is not None
    assert loaded.stage == Stage.RESEARCH
    assert loaded.gates["research_output"].status == GateStatus.PASS


def test_blocked_state_persists_exact_recovery_cursor_and_can_resume(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    engine = WritingEngine(store)
    ctl = WorkflowController(engine)
    state = ctl.advance(engine.start(TaskContract(prompt="恢复测试")))
    assert state.stage == Stage.RESEARCH

    state = engine.block(state, "temporary research dependency unavailable", resume_stage=Stage.RESEARCH)
    assert state.stage == Stage.BLOCKED
    assert state.blocked_from_stage == Stage.RESEARCH
    assert state.blocked_resume_stage == Stage.RESEARCH

    loaded = store.load(state.contract.task_id)
    assert loaded is not None and loaded.blocked_resume_stage == Stage.RESEARCH

    resumed = engine.resume_blocked(loaded)
    assert resumed.stage == Stage.RESEARCH
    assert resumed.blocked_reason is None
    assert resumed.blocked_resume_stage is None
    assert resumed.blocked_from_stage is None
    assert any(e.event == "RUNTIME_UNBLOCKED" for e in resumed.trace)
