from __future__ import annotations

from pathlib import Path

from .adapters.deterministic import DeliveryExecutor, MechanicalAuditExecutor
from .adapters.openai_agents import build_openai_executors
from .models import Stage
from .runner import AgentRuntime


def build_runtime(*, state_db: str | Path = "financial_writing_state.db", runs_dir: str | Path = "runs", model: str | None = None, require_render: bool = True) -> AgentRuntime:
    executors = build_openai_executors(model=model)
    executors[Stage.DELIVERY] = DeliveryExecutor(root=runs_dir)
    executors[Stage.MECHANICAL_AUDIT] = MechanicalAuditExecutor(require_render=require_render)
    return AgentRuntime.with_sqlite(state_db, executors=executors)
