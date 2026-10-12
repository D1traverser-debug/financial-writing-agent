from __future__ import annotations

from .adapters.openai_agents import OpenAIAgentsUnavailable, OpenAIStageExecutor
from .engine import WorkflowError
from .models import Stage, WritingState
from .store import StateConflictError


SEMANTIC_AUDIT_STAGES = {
    Stage.RESEARCH_AUDIT,
    Stage.EDITORIAL_AUDIT,
    Stage.FINAL_AUDIT,
}


def run_owner_semantic_audit_stage(state: WritingState, *, expected_stage: Stage, impl) -> WritingState:
    """Run one proof-bearing owner-native semantic audit stage.

    A CHAT_BRIDGED PASS request may call this gateway, but the caller's verdict is not
    accepted as proof. The server-side owner runtime executes the actual judge(s),
    records runtime trajectory evidence, and lets the authoritative controller persist
    the successful result together with its stage transition.

    EXECUTOR_START is intentionally checkpointed before the external model call so a
    crash can be distinguished from a completed judge run. A successful EXECUTOR_END is
    not pre-saved: controller.advance (or block on failure) owns the next durable
    checkpoint, preventing a durable semantic PASS from being stranded before its route.
    """
    if expected_stage not in SEMANTIC_AUDIT_STAGES:
        raise ValueError(f"not a semantic audit stage: {expected_stage.value}")
    if state.stage != expected_stage:
        raise ValueError(
            f"task {state.contract.task_id} is at {state.stage.value}, expected {expected_stage.value}"
        )

    state.add_trace("EXECUTOR_START", expected_stage.value)
    impl.store.save(state)
    try:
        state = OpenAIStageExecutor(expected_stage).execute(state)
    except StateConflictError:
        # Concurrency conflict is not an audit verdict. Never convert a stale semantic
        # writer into a BLOCKED mutation that would itself attempt to overwrite the winner.
        raise
    except OpenAIAgentsUnavailable as exc:
        return impl.engine.block(
            state,
            f"owner semantic audit runtime unavailable: {exc}",
            resume_stage=expected_stage,
        )
    except Exception as exc:
        return impl.engine.block(
            state,
            f"owner semantic audit executor error at {expected_stage.value}: {type(exc).__name__}: {exc}",
            resume_stage=expected_stage,
        )

    state.add_trace("EXECUTOR_END", expected_stage.value)
    try:
        return impl.controller.advance(state)
    except WorkflowError as exc:
        return impl.engine.block(state, str(exc), resume_stage=expected_stage)
