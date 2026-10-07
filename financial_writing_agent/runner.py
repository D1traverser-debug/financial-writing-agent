from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .controller import WorkflowController
from .engine import WorkflowError, WritingEngine
from .models import GateStatus, Stage, TaskContract, WritingState
from .store import SQLiteStateStore, StateConflictError


class StageExecutor(Protocol):
    """Adapter contract. Implementations may use OpenAI Agents SDK, another model, or tests."""

    def execute(self, state: WritingState) -> WritingState:
        ...


class RuntimeUnavailable(RuntimeError):
    pass


class AgentRuntime:
    """Owns the standalone/local outer loop. It never silently falls back to free-form generation.

    Connected-knowledge reads/writes are intentionally orchestrated by the ChatGPT/MCP path.
    A standalone AgentRuntime therefore records both knowledge_context=N_A and
    knowledge_sync=N_A instead of leaving gates that this runner cannot satisfy.
    """

    def __init__(self, engine: WritingEngine, executors: dict[Stage, StageExecutor], *, max_steps: int = 50):
        self.engine = engine
        self.controller = WorkflowController(engine)
        self.executors = executors
        self.max_steps = max_steps

    @classmethod
    def with_sqlite(cls, path: str | Path, executors: dict[Stage, StageExecutor], *, max_steps: int = 50):
        return cls(WritingEngine(SQLiteStateStore(path)), executors, max_steps=max_steps)

    def _record_standalone_knowledge_boundary(self, state: WritingState) -> None:
        context_gate = state.gates.get("knowledge_context")
        if context_gate is None or context_gate.status == GateStatus.NOT_RUN:
            state.set_gate(
                "knowledge_context",
                GateStatus.N_A,
                ["standalone AgentRuntime has no connected durable-knowledge recall surface"],
                "Use the MCP/ChatGPT path when connected prior-knowledge recall is available.",
            )
            state.add_trace("KNOWLEDGE_CONTEXT_BOUNDARY", "standalone runtime -> N_A")

        sync_gate = state.gates.get("knowledge_sync")
        if sync_gate is None or sync_gate.status == GateStatus.NOT_RUN:
            state.set_gate(
                "knowledge_sync",
                GateStatus.N_A,
                ["standalone AgentRuntime has no connected durable-knowledge writeback surface"],
                "Use the MCP/ChatGPT path when connected knowledge writeback is required.",
            )
            state.add_trace("KNOWLEDGE_SYNC_BOUNDARY", "standalone runtime -> N_A")
        self.engine.store.save(state)

    def start(self, contract: TaskContract) -> WritingState:
        state = self.engine.start(contract)
        self._record_standalone_knowledge_boundary(state)
        return self.controller.advance(state)

    def resume(self, task_id: str) -> WritingState:
        state = self.engine.store.load(task_id)
        if state is None:
            raise RuntimeUnavailable(f"checkpoint not found: {task_id}")
        if state.stage == Stage.BLOCKED:
            state = self.engine.resume_from_blocked(state)
        self._record_standalone_knowledge_boundary(state)
        state.add_trace("RUNTIME_RESUMED", "checkpoint loaded")
        self.engine.store.save(state)
        return state

    def run(self, state: WritingState) -> WritingState:
        steps = 0
        while state.stage not in {Stage.COMPLETE, Stage.BLOCKED}:
            steps += 1
            if steps > self.max_steps:
                return self.engine.block(state, f"max_steps exceeded ({self.max_steps})")

            executor = self.executors.get(state.stage)
            if executor is None:
                return self.engine.block(state, f"no executor registered for stage {state.stage.value}")

            try:
                state.add_trace("EXECUTOR_START", state.stage.value)
                self.engine.store.save(state)
                state = executor.execute(state)
                state.add_trace("EXECUTOR_END", state.stage.value)
                self.engine.store.save(state)
                if state.stage in {Stage.COMPLETE, Stage.BLOCKED}:
                    break
                state = self.controller.advance(state)
            except StateConflictError as exc:
                raise RuntimeUnavailable(
                    f"checkpoint changed concurrently for {state.contract.task_id}; reload the latest state before retrying"
                ) from exc
            except (WorkflowError, RuntimeUnavailable) as exc:
                return self.engine.block(state, str(exc))
            except Exception as exc:
                return self.engine.block(state, f"executor error at {state.stage.value}: {type(exc).__name__}: {exc}")
        return state
