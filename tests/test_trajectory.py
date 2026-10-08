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
    state.set_gate("knowledge_context", GateStatus.N_A, ["no connected recall in trajectory unit test"])
    state.set_gate("research_output", GateStatus.PASS, ["ledger"])
    state = ctl.advance(state)
    assert state.stage == Stage.RESEARCH_AUDIT
    state.set_gate("research_audit", GateStatus.PASS, ["judge"])
    state = ctl.advance(state)
    state.set_gate("editorial_plan", GateStatus.PASS, ["deep topicdna"])
    state = ctl.advance(state)
    state.set_gate("title_audit", GateStatus.PASS, ["deep title judge"])
    state.set_gate("acceptance_contract", GateStatus.PASS, ["deep article-level contract frozen"])
    state = ctl.advance(state)
    state.set_gate("draft_output", GateStatus.PASS, ["deep mother draft frozen"])
    state = ctl.advance(state)
    assert state.stage == Stage.BROAD_DERIVATION
    assert state.working["broad_derivation_phase"] == "EDITORIAL"
    state.set_gate("broad_derivation", GateStatus.PASS, ["broad derived from frozen deep mother"])
    state = ctl.advance(state)
    assert state.stage == Stage.EDITORIAL_AUDIT
    state.set_gate("style_audit", GateStatus.PASS, ["style judge"])
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
        state.artifacts[kind].sha256 = engine._sha256(p)
    state.set_gate("knowledge_sync", GateStatus.N_A, ["no connected write target in trajectory unit test"])
    required_evidence = engine._required_final_evidence_keys(state)
    assert "DUAL.cross_version_consistency" in required_evidence
    assert "DUAL.deep_master_quality" in required_evidence
    assert "DUAL.broad_derivation_fidelity" in required_evidence
    assert "DUAL.broad_hook_strength" in required_evidence
    assert "FINANCE_DEEP.opening_first_three_sentences" in required_evidence
    assert "FINANCE_DEEP.hook_quality" in required_evidence
    assert "FINANCE_BROAD.stock_judgment_clarity" in required_evidence
    assert "FINANCE_BROAD.bold_scan_skeleton" in required_evidence
    state.working["final_audit"] = {
        "acceptance_evidence": [f"{key}: verified on frozen final content" for key in sorted(required_evidence)]
    }
    state.set_gate("final_audit", GateStatus.PASS, ["red team"])
    state = ctl.advance(state)
    assert state.stage == Stage.COMPLETE

    entered = [e.stage.value for e in state.trace if e.event == "STAGE_ENTER"]
    assert entered == [
        "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE", "DRAFT", "BROAD_DERIVATION",
        "EDITORIAL_AUDIT", "DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT", "COMPLETE"
    ]


def test_research_cannot_advance_without_knowledge_context_decision(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    ctl = WorkflowController(engine)
    state = engine.start(TaskContract(prompt="测试知识召回门禁"))
    state = ctl.advance(state)
    state.set_gate("research_output", GateStatus.PASS, ["research done"])

    try:
        ctl.advance(state)
    except Exception as exc:
        assert "knowledge_context" in str(exc)
    else:
        raise AssertionError("RESEARCH must not advance before knowledge_context PASS/N_A")


def test_title_cannot_advance_without_frozen_acceptance_contract(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    ctl = WorkflowController(engine)
    state = engine.start(TaskContract(prompt="测试"))
    state = ctl.advance(state)
    state.set_gate("knowledge_context", GateStatus.N_A, ["test"])
    state.set_gate("research_output", GateStatus.PASS, ["ok"])
    state = ctl.advance(state)
    state.set_gate("research_audit", GateStatus.PASS, ["ok"])
    state = ctl.advance(state)
    state.set_gate("editorial_plan", GateStatus.PASS, ["ok"])
    state = ctl.advance(state)
    state.set_gate("title_audit", GateStatus.PASS, ["ok"])

    try:
        ctl.advance(state)
    except Exception as exc:
        assert "acceptance_contract" in str(exc)
    else:
        raise AssertionError("TITLE must not advance without acceptance_contract")


def test_state_resume(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    engine = WritingEngine(store)
    ctl = WorkflowController(engine)
    state = engine.start(TaskContract(prompt="继续文章"))
    state = ctl.advance(state)
    state.set_gate("knowledge_context", GateStatus.N_A, ["test"])
    state.set_gate("research_output", GateStatus.PASS, ["done"])
    store.save(state)

    loaded = store.load(state.contract.task_id)
    assert loaded is not None
    assert loaded.stage == Stage.RESEARCH
    assert loaded.gates["research_output"].status == GateStatus.PASS


def test_blocked_task_resumes_to_recorded_original_stage(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    engine = WritingEngine(store)
    state = engine.start(TaskContract(prompt="恢复测试"))
    state = engine.transition(state, Stage.RESEARCH, reason="test")
    state = engine.transition(state, Stage.BLOCKED, reason="manual transition should not be used for recovery metadata")
    assert state.stage == Stage.BLOCKED

    # A genuine block records the original stage; use a fresh state for that contract.
    state2 = engine.start(TaskContract(prompt="真实阻断恢复"))
    state2 = engine.transition(state2, Stage.RESEARCH, reason="test")
    state2 = engine.block(state2, "temporary source outage")
    assert state2.stage == Stage.BLOCKED
    assert state2.working["blocked_from_stage"] == "RESEARCH"
    resumed = engine.resume_from_blocked(state2)
    assert resumed.stage == Stage.RESEARCH
    assert resumed.blocked_reason is None
    assert "blocked_from_stage" not in resumed.working
