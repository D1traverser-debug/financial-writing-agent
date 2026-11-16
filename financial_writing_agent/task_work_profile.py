from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field, model_validator

from .task_requirements import StrictModel


class TaskWorkProfile(StrictModel):
    """Derived task-shape projection; TaskRequirementAuthority remains authoritative.

    The canonical Financial article graph is fixed for every article. This profile
    describes the task-specific split between user-locked requirements and editorial
    decisions intentionally left open to the writing system.
    """

    schema_version: Literal["1.0"] = "1.0"
    task_shape: Literal["FIXED_WORKFLOW", "OPEN_ENDED", "HYBRID"]
    fixed_requirement_ids: list[str] = Field(default_factory=list)
    preference_requirement_ids: list[str] = Field(default_factory=list)
    open_decision_domains: list[str] = Field(default_factory=list)
    conditional_modules: list[str] = Field(default_factory=list)
    classification_rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_profile(self):
        for name in (
            "fixed_requirement_ids",
            "preference_requirement_ids",
            "open_decision_domains",
            "conditional_modules",
        ):
            values = getattr(self, name)
            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(f"{name} must contain non-empty strings")
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must be unique")
        if set(self.fixed_requirement_ids) & set(self.preference_requirement_ids):
            raise ValueError("fixed and preference requirement ids must be disjoint")
        has_fixed = bool(self.fixed_requirement_ids)
        has_open = bool(self.open_decision_domains)
        if not has_fixed and not has_open:
            raise ValueError("task profile must identify fixed requirements or open decisions")
        expected = "HYBRID" if has_fixed and has_open else "FIXED_WORKFLOW" if has_fixed else "OPEN_ENDED"
        if self.task_shape != expected:
            raise ValueError(f"task_shape mismatch: expected {expected}")
        if not self.classification_rationale.strip():
            raise ValueError("classification_rationale is required")
        return self


class TaskWorkProfileError(ValueError):
    pass


def _active_requirement_sources(
    requirement_contexts: Mapping[str, object] | None,
) -> dict[str, str]:
    if requirement_contexts is None:
        return {}
    if not isinstance(requirement_contexts, Mapping):
        raise TaskWorkProfileError("requirement_contexts must be a mapping")
    active: dict[str, str] = {}
    for scope, raw_context in requirement_contexts.items():
        if not isinstance(raw_context, Mapping):
            raise TaskWorkProfileError(f"requirement context invalid: {scope}")
        requirements = raw_context.get("requirements")
        if not isinstance(requirements, list):
            raise TaskWorkProfileError(f"requirement list invalid: {scope}")
        for raw in requirements:
            if not isinstance(raw, Mapping):
                raise TaskWorkProfileError(f"requirement record invalid: {scope}")
            requirement_id = str(raw.get("requirement_id", "")).strip()
            source_kind = str(raw.get("source_kind", "")).strip()
            if not requirement_id or source_kind not in {
                "USER_EXPLICIT", "USER_CORRECTION", "USER_PREFERENCE"
            }:
                raise TaskWorkProfileError(f"requirement identity/source invalid: {scope}")
            previous = active.get(requirement_id)
            if previous is not None and previous != source_kind:
                raise TaskWorkProfileError(f"requirement source conflicts across scopes: {requirement_id}")
            active[requirement_id] = source_kind
    return active


def validate_task_work_profile(
    raw: Mapping[str, object],
    requirement_contexts: Mapping[str, object] | None,
) -> dict[str, object]:
    """Validate that the profile classifies every active requirement exactly once."""
    try:
        profile = TaskWorkProfile.model_validate(raw)
    except Exception as exc:
        raise TaskWorkProfileError("task work profile schema invalid") from exc
    active = _active_requirement_sources(requirement_contexts)
    expected_fixed = {
        requirement_id for requirement_id, source in active.items()
        if source in {"USER_EXPLICIT", "USER_CORRECTION"}
    }
    expected_preferences = {
        requirement_id for requirement_id, source in active.items()
        if source == "USER_PREFERENCE"
    }
    if set(profile.fixed_requirement_ids) != expected_fixed:
        raise TaskWorkProfileError("fixed requirement ids do not match active user requirements")
    if set(profile.preference_requirement_ids) != expected_preferences:
        raise TaskWorkProfileError("preference requirement ids do not match active user preferences")
    return profile.model_dump(mode="json")
