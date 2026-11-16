from __future__ import annotations

"""Compatibility import path; new contexts use WritingExecutionProfile."""

from collections.abc import Mapping

from .writing_execution_profile import (
    WritingExecutionProfile,
    WritingExecutionProfileError,
    validate_writing_execution_profile,
)


TaskWorkProfile = WritingExecutionProfile
TaskWorkProfileError = WritingExecutionProfileError


def validate_task_work_profile(
    raw: Mapping[str, object],
    requirement_contexts: Mapping[str, object] | None,
) -> dict[str, object]:
    prompt_sha = raw.get("source_prompt_sha256") if isinstance(raw, Mapping) else None
    if not isinstance(prompt_sha, str):
        raise WritingExecutionProfileError("writing execution profile prompt binding missing")
    return validate_writing_execution_profile(raw, requirement_contexts, source_prompt_sha256=prompt_sha)
