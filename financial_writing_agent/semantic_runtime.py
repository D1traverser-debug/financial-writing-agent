from __future__ import annotations

from .adapters.openai_agents import OpenAIAgentsUnavailable, OpenAIStageExecutor
from .engine import WorkflowError
from .models import Stage, WritingState


SEMANTIC_AUDIT_STAGES = {
    Stage.RESEARCH_AUDIT,
    Stage.EDITORIAL_AUDIT,
    Stage.FINAL_AUDIT,
}


def run_owner_semantic_audit_stage(state: WritingState, *, expected_stage: Stage, impl) -> WritingState:
    """Run one proof-bearing owner-native semantic audit stage.

    A CHAT_BRIDGED PASS request may call this gateway, but the caller's verdict is not
    accepted as proof. The server-side owner runtime executes the actual judge(s),
    records runtime trajectory evidence, persists the result, and only then lets the
    authoritative controller decide whether the stage may advance.
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
    impl.store.save(state)
    try:
        return impl.controller.advance(state)
    except WorkflowError as exc:
        return impl.engine.block(state, str(exc), resume_stage=expected_stage)
