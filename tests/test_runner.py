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


def test_new_task_never_inherits_prior_task_state(tmp_path):
    runtime = AgentRuntime.with_sqlite(tmp_path / "state.db", executors={})

    old = runtime.start(TaskContract(prompt="上一篇文章"))
    old.working["selected_title"] = "旧标题绝不能带入新任务"
    old.working["draft"] = {"old_body": "旧正文绝不能带入新任务"}
    old.working["next_exact_action"] = "继续旧稿"
    old.set_gate("old_task_only", GateStatus.PASS, ["old task marker"])
    runtime.engine.store.save(old)

    new = runtime.start(TaskContract(prompt="新开一篇完全不同的文章"))

    assert new.contract.task_id != old.contract.task_id
    assert new.stage == Stage.RESEARCH
    assert "selected_title" not in new.working
    assert "draft" not in new.working
    assert "next_exact_action" not in new.working
    assert "old_task_only" not in new.gates
    assert new.contract.prompt == "新开一篇完全不同的文章"

    persisted_old = runtime.engine.store.load(old.contract.task_id)
    persisted_new = runtime.engine.store.load(new.contract.task_id)
    assert persisted_old is not None and persisted_new is not None
    assert persisted_old.working["selected_title"] == "旧标题绝不能带入新任务"
    assert persisted_new.working == new.working


def test_explicit_resume_restores_only_requested_task(tmp_path):
    runtime = AgentRuntime.with_sqlite(tmp_path / "state.db", executors={})

    first = runtime.start(TaskContract(prompt="任务一"))
    first.working["resume_marker"] = "only-task-one"
    runtime.engine.store.save(first)

    second = runtime.start(TaskContract(prompt="任务二"))
    second.working["resume_marker"] = "only-task-two"
    runtime.engine.store.save(second)

    resumed = runtime.resume(first.contract.task_id)

    assert resumed.contract.task_id == first.contract.task_id
    assert resumed.working["resume_marker"] == "only-task-one"
    assert resumed.contract.task_id != second.contract.task_id
    assert resumed.working["resume_marker"] != "only-task-two"
