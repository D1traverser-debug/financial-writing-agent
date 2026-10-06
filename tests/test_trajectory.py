from financial_writing_agent.controller import WorkflowController
from financial_writing_agent.engine import WritingEngine
from financial_writing_agent.models import GateStatus, Stage, TaskContract
from financial_writing_agent.store import SQLiteStateStore


def test_happy_path_trace_is_deterministic(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    ctl = WorkflowController(engine)
    state = engine.start(TaskContract(prompt="根据两个链接写文章"))

    state = ctl.advance(state)
    assert state.stage == Stage.RESEARCH
    state.set_gate("research_output", GateStatus.PASS, ["ledger"])
    state = ctl.advance(state)
    assert state.stage == Stage.RESEARCH_AUDIT
    state.set_gate("research_audit", GateStatus.PASS, ["judge"])
    state = ctl.advance(state)
    state.set_gate("editorial_plan", GateStatus.PASS, ["topicdna"])
    state = ctl.advance(state)
    state.set_gate("title_audit", GateStatus.PASS, ["title judge"])
    state = ctl.advance(state)
    state.set_gate("draft_output", GateStatus.PASS, ["draft frozen"])
    state = ctl.advance(state)
    state.set_gate("editorial_audit", GateStatus.PASS, ["editor judge"])
    state = ctl.advance(state)
    state.set_gate("delivery_output", GateStatus.PASS, ["docx built"])
    state = ctl.advance(state)
    state.set_gate("mechanical_audit", GateStatus.PASS, ["checks"])
    state = ctl.advance(state)

    for kind in state.contract.required_outputs:
        p = tmp_path / f"{kind}.docx"
        p.write_bytes(b"stub")
        state.add_artifact(kind, str(p))
    state.set_gate("knowledge_sync", GateStatus.N_A, ["no connected write target in trajectory unit test"])
    state.set_gate("final_audit", GateStatus.PASS, ["red team"])
    state = ctl.advance(state)
    assert state.stage == Stage.COMPLETE

    entered = [e.stage.value for e in state.trace if e.event == "STAGE_ENTER"]
    assert entered == [
        "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE", "DRAFT",
        "EDITORIAL_AUDIT", "DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT", "COMPLETE"
    ]


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
