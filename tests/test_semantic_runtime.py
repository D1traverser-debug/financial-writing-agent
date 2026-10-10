from types import SimpleNamespace

from financial_writing_agent.controller import WorkflowController
from financial_writing_agent.engine import WritingEngine
from financial_writing_agent.models import GateStatus, Stage, TaskContract
from financial_writing_agent.semantic_runtime import run_owner_semantic_audit_stage
from financial_writing_agent.store import SQLiteStateStore


class FakeSuccessfulResearchAuditor:
    def __init__(self, stage):
        assert stage == Stage.RESEARCH_AUDIT
        self.stage = stage

    def execute(self, state):
        state.working["research_audit"] = {
            "status": "PASS",
            "evidence": ["owner runtime fake judge evidence"],
            "provenance": {
                "assurance": "INDEPENDENT_EXECUTOR",
                "reviewer_identity": "Financial Writing Research Auditor",
                "author_identity": "Financial Writing Researcher",
                "execution_ref": f"{state.contract.task_id}:{state.stage.value}:test-judge",
            },
        }
        state.set_gate("research_audit", GateStatus.PASS, ["owner runtime fake judge evidence"])
        return state


class FakeUnavailableAuditor:
    def __init__(self, stage):
        self.stage = stage

    def execute(self, state):
        raise RuntimeError("model runtime unavailable")


def _impl(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    engine = WritingEngine(store)
    return SimpleNamespace(store=store, engine=engine, controller=WorkflowController(engine))


def _research_audit_state(tmp_path):
    impl = _impl(tmp_path)
    state = impl.engine.start(TaskContract(prompt="semantic runtime test"))
    state = impl.controller.advance(state)
    state.set_gate("research_output", GateStatus.PASS, ["ledger"])
    state = impl.controller.advance(state)
    assert state.stage == Stage.RESEARCH_AUDIT
    return impl, state


def test_owner_semantic_gateway_runs_stage_and_advances(monkeypatch, tmp_path):
    impl, state = _research_audit_state(tmp_path)
    monkeypatch.setattr("financial_writing_agent.semantic_runtime.OpenAIStageExecutor", FakeSuccessfulResearchAuditor)

    result = run_owner_semantic_audit_stage(state, expected_stage=Stage.RESEARCH_AUDIT, impl=impl)

    assert result.stage == Stage.EDITORIAL
    assert result.semantic_gate_proof_valid("research_audit") is True
    stage_events = [(event.stage, event.event) for event in result.trace]
    assert (Stage.RESEARCH_AUDIT, "EXECUTOR_START") in stage_events
    assert (Stage.RESEARCH_AUDIT, "EXECUTOR_END") in stage_events


def test_owner_semantic_gateway_fails_closed_to_recoverable_block(monkeypatch, tmp_path):
    impl, state = _research_audit_state(tmp_path)
    monkeypatch.setattr("financial_writing_agent.semantic_runtime.OpenAIStageExecutor", FakeUnavailableAuditor)

    result = run_owner_semantic_audit_stage(state, expected_stage=Stage.RESEARCH_AUDIT, impl=impl)

    assert result.stage == Stage.BLOCKED
    assert result.blocked_resume_stage == Stage.RESEARCH_AUDIT
    assert "owner semantic audit executor error" in (result.blocked_reason or "")


def test_gateway_rejects_wrong_stage_before_executor(monkeypatch, tmp_path):
    impl, state = _research_audit_state(tmp_path)
    monkeypatch.setattr("financial_writing_agent.semantic_runtime.OpenAIStageExecutor", FakeSuccessfulResearchAuditor)

    try:
        run_owner_semantic_audit_stage(state, expected_stage=Stage.FINAL_AUDIT, impl=impl)
    except ValueError as exc:
        assert "expected FINAL_AUDIT" in str(exc)
    else:
        raise AssertionError("wrong-stage semantic gateway must fail closed")
