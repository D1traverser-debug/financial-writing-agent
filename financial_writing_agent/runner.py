from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .controller import WorkflowController
from .engine import WorkflowError, WritingEngine
from .models import Stage, TaskContract, WritingState
from .store import SQLiteStateStore


class StageExecutor(Protocol):
    """Adapter contract. Implementations may use OpenAI Agents SDK, another model, or tests."""

    def execute(self, state: WritingState) -> WritingState:
        ...


class RuntimeUnavailable(RuntimeError):
    pass


class AgentRuntime:
    """Owns the outer loop. It never silently falls back to free-form generation."""

    def __init__(self, engine: WritingEngine, executors: dict[Stage, StageExecutor], *, max_steps: int = 50):
        self.engine = engine
        self.controller = WorkflowController(engine)
        self.executors = executors
        self.max_steps = max_steps

    @classmethod
    def with_sqlite(cls, path: str | Path, executors: dict[Stage, StageExecutor], *, max_steps: int = 50):
        return cls(WritingEngine(SQLiteStateStore(path)), executors, max_steps=max_steps)

    def start(self, contract: TaskContract) -> WritingState:
        state = self.engine.start(contract)
        return self.controller.advance(state)

    def resume(self, task_id: str) -> WritingState:
        # Store restoration replays any pending crash-recovery cleanup in memory before
        # this runtime sees the state. The RUNTIME_RESUMED checkpoint then persists that
        # healed view through normal optimistic CAS.
        state = self.engine.store.load(task_id)
        if state is None:
            raise RuntimeUnavailable(f"checkpoint not found: {task_id}")
        if state.stage == Stage.BLOCKED:
            state = self.engine.resume_blocked(state)
        state.add_trace("RUNTIME_RESUMED", "checkpoint loaded")
        self.engine.store.save(state)
        return state

    def run(self, state: WritingState) -> WritingState:
        steps = 0
        while state.stage not in {Stage.COMPLETE, Stage.BLOCKED}:
            steps += 1
            if steps > self.max_steps:
                return self.engine.block(state, f"max_steps exceeded ({self.max_steps})", resume_stage=state.stage)

            executor = self.executors.get(state.stage)
            if executor is None:
                return self.engine.block(state, f"no executor registered for stage {state.stage.value}", resume_stage=state.stage)

            try:
                stage_before = state.stage
                state.add_trace("EXECUTOR_START", stage_before.value)
                # Persist invocation start before the external/high-judgment execution so
                # an interrupted call cannot be confused with a completed execution.
                self.engine.store.save(state)
                state = executor.execute(state)
                state.add_trace("EXECUTOR_END", stage_before.value)
                if state.stage in {Stage.COMPLETE, Stage.BLOCKED}:
                    # An executor that legitimately terminalized/blocked may already have
                    # persisted that transition; save only the final execution trace here.
                    self.engine.store.save(state)
                    break
                # Successful output + EXECUTOR_END + stage transition are one durable
                # checkpoint. Do not pre-save PASS/output before controller routing.
                state = self.controller.advance(state)
            except (WorkflowError, RuntimeUnavailable) as exc:
                return self.engine.block(state, str(exc), resume_stage=state.stage)
            except Exception as exc:
                return self.engine.block(state, f"executor error at {state.stage.value}: {type(exc).__name__}: {exc}", resume_stage=state.stage)
        return state
