from dataclasses import dataclass

from financial_writing_agent.models import GateStatus, Stage, TaskContract, WritingState
from financial_writing_agent.runner import AgentRuntime


@dataclass
class PassExecutor:
    gate: str

    def execute(self, state: WritingState) -> WritingState:
        state.set_gate(self.gate, GateStatus.PASS, ["test evidence"])
        return state


class ExplodingExecutor:
    def execute(self, state: WritingState) -> WritingState:
        raise RuntimeError("simulated adapter failure")


def test_missing_executor_blocks_instead_of_freeform(tmp_path):
    runtime = AgentRuntime.with_sqlite(tmp_path / "state.db", executors={})
    state = runtime.start(TaskContract(prompt="根据两个链接写文章"))
    assert state.stage == Stage.RESEARCH
    state = runtime.run(state)
    assert state.stage == Stage.BLOCKED
    assert state.blocked_resume_stage == Stage.RESEARCH
    assert "no executor" in (state.blocked_reason or "")


def test_executor_exception_blocks_instead_of_freeform(tmp_path):
    runtime = AgentRuntime.with_sqlite(
        tmp_path / "state.db",
        executors={Stage.RESEARCH: ExplodingExecutor()},
    )
    state = runtime.start(TaskContract(prompt="写文章"))
    state = runtime.run(state)
    assert state.stage == Stage.BLOCKED
    assert state.blocked_resume_stage == Stage.RESEARCH
    assert "executor error" in (state.blocked_reason or "")


def test_blocked_checkpoint_resumes_exact_recovery_cursor(tmp_path):
    runtime = AgentRuntime.with_sqlite(tmp_path / "state.db", executors={})
    state = runtime.start(TaskContract(prompt="写文章"))
    state = runtime.run(state)
    task_id = state.contract.task_id
    assert state.stage == Stage.BLOCKED
    assert state.blocked_resume_stage == Stage.RESEARCH

    runtime.executors[Stage.RESEARCH] = PassExecutor("research_output")
    state = runtime.resume(task_id)
    assert state.stage == Stage.RESEARCH
    assert state.blocked_reason is None
    assert state.blocked_from_stage is None
    assert state.blocked_resume_stage is None
    assert "RUNTIME_UNBLOCKED" in [event.event for event in state.trace]


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
