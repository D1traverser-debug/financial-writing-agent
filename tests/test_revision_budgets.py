from financial_writing_agent.controller import WorkflowController
from financial_writing_agent.engine import WritingEngine
from financial_writing_agent.models import GateStatus, Stage, TaskContract
from financial_writing_agent.store import SQLiteStateStore


def test_research_revision_budget_allows_one_revision_then_blocks_second(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    controller = WorkflowController(engine)
    contract = TaskContract(
        prompt="写文章",
        run_constraints={
            "research_max_rounds": 2,
            "title_max_rounds": 3,
            "draft_max_rounds": 2,
        },
    )
    state = engine.start(contract)
    state = engine.transition(state, Stage.RESEARCH, reason="test setup")
    state = engine.transition(state, Stage.RESEARCH_AUDIT, reason="test setup")

    state.set_gate("research_audit", GateStatus.REVISE, ["补研究"], "first revision")
    state = controller.advance(state)
    assert state.stage == Stage.RESEARCH
    assert state.attempts["research_revision_count"] == 1
    assert state.blocked_reason is None

    state = engine.transition(state, Stage.RESEARCH_AUDIT, reason="second audit")
    state.set_gate("research_audit", GateStatus.REVISE, ["仍需补研究"], "second revision")
    state = controller.advance(state)

    assert state.stage == Stage.BLOCKED
    assert state.attempts["research_revision_count"] == 2
    assert "revision budget exhausted" in (state.blocked_reason or "")
    assert "requested_round=3" in (state.blocked_reason or "")
    assert "max_rounds=2" in (state.blocked_reason or "")
