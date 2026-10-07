from financial_writing_agent.adapters.mock import ExplodingExecutor, PassExecutor
from financial_writing_agent.models import GateStatus, Stage, TaskContract
from financial_writing_agent.runner import AgentRuntime


def test_missing_executor_blocks_instead_of_freeform(tmp_path):
    runtime = AgentRuntime.with_sqlite(tmp_path / "state.db", executors={})
    state = runtime.start(TaskContract(prompt="根据两个链接写文章"))
    assert state.stage == Stage.RESEARCH
    state = runtime.run(state)
    assert state.stage == Stage.BLOCKED
    assert "no executor" in (state.blocked_reason or "")


def test_executor_exception_blocks_instead_of_freeform(tmp_path):
    runtime = AgentRuntime.with_sqlite(
        tmp_path / "state.db",
        executors={Stage.RESEARCH: ExplodingExecutor()},
    )
    state = runtime.start(TaskContract(prompt="写文章"))
    state = runtime.run(state)
    assert state.stage == Stage.BLOCKED
    assert "executor error" in (state.blocked_reason or "")


def test_runtime_starts_before_research_executor(tmp_path):
    runtime = AgentRuntime.with_sqlite(
        tmp_path / "state.db",
        executors={Stage.RESEARCH: PassExecutor("research_output")},
        max_steps=1,
    )
    state = runtime.start(TaskContract(prompt="根据来源写文章"))
    assert state.trace[0].event == "RUNTIME_STARTED"
    state = runtime.run(state)
    events = [e.event for e in state.trace]
    assert events.index("RUNTIME_STARTED") < events.index("EXECUTOR_START")


def test_standalone_runtime_records_explicit_knowledge_na_boundary(tmp_path):
    runtime = AgentRuntime.with_sqlite(tmp_path / "state.db", executors={})
    state = runtime.start(TaskContract(prompt="本地诊断"))
    assert state.gates["knowledge_sync"].status == GateStatus.N_A
    assert any(event.event == "KNOWLEDGE_SYNC_BOUNDARY" for event in state.trace)

    resumed = runtime.resume(state.contract.task_id)
    assert resumed.gates["knowledge_sync"].status == GateStatus.N_A
