from __future__ import annotations

from .models import ResumeVisibility, Stage, TaskClass, WritingState
from .store import SQLiteStateStore


def is_bare_inherit_candidate(state: WritingState) -> bool:
    """Return True only for ordinary cross-chat continuation candidates."""
    contract = state.contract
    return (
        contract.task_class == TaskClass.USER
        and contract.resume_eligible
        and contract.resume_visibility == ResumeVisibility.DEFAULT
        and state.stage != Stage.COMPLETE
    )


def list_resumable_states(store: SQLiteStateStore, limit: int = 10, *, include_complete: bool = False) -> list[WritingState]:
    """Return safe continuation candidates without leaking legacy/test state.

    `list_recent_writing_tasks` is the existing public 16-tool surface, so this
    owner-adapter is intentionally mapped onto that tool rather than adding a
    seventeenth MCP tool during the current Site migration.
    """
    safe_limit = max(1, min(int(limit), 50))
    scan_limit = min(max(safe_limit * 5, 50), 100)
    states = store.list_recent(scan_limit)
    eligible = [
        state
        for state in states
        if state.contract.task_class == TaskClass.USER
        and state.contract.resume_eligible
        and state.contract.resume_visibility == ResumeVisibility.DEFAULT
        and (include_complete or state.stage != Stage.COMPLETE)
    ]
    return eligible[:safe_limit]


def continuity_metadata(state: WritingState) -> dict[str, object]:
    contract = state.contract
    return {
        "task_class": contract.task_class.value,
        "resume_eligible": contract.resume_eligible,
        "resume_visibility": contract.resume_visibility.value,
        "contract_version": contract.contract_version,
        "runtime_version": contract.runtime_version,
        "skill_version": contract.skill_version,
    }
