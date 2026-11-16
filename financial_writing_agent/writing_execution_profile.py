from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field, model_validator

from .task_requirements import StrictModel


WORKFLOW_CONTRACT = "FINANCIAL_ARTICLE_10_STAGE_V1"


class WritingExecutionProfile(StrictModel):
    """Prompt-bound execution context: fixed process, user-locked constraints, open editorial choices."""

    schema_version: Literal["1.0"] = "1.0"
    workflow_contract: Literal["FINANCIAL_ARTICLE_10_STAGE_V1"] = WORKFLOW_CONTRACT
    source_prompt_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    fixed_requirement_ids: list[str] = Field(default_factory=list)
    preference_requirement_ids: list[str] = Field(default_factory=list)
    locked_decision_domains: list[str] = Field(default_factory=list)
    open_decision_domains: list[str] = Field(default_factory=list)
    conditional_modules: list[str] = Field(default_factory=list)
    execution_rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_profile(self):
        for name in (
            "fixed_requirement_ids", "preference_requirement_ids",
            "locked_decision_domains", "open_decision_domains", "conditional_modules",
        ):
            values = getattr(self, name)
            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(f"{name} must contain non-empty strings")
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must be unique")
        if set(self.fixed_requirement_ids) & set(self.preference_requirement_ids):
            raise ValueError("fixed and preference requirement ids must be disjoint")
        if set(self.locked_decision_domains) & set(self.open_decision_domains):
            raise ValueError("a decision domain cannot be both locked and open")
        if not self.execution_rationale.strip():
            raise ValueError("execution_rationale is required")
        return self


class WritingExecutionProfileError(ValueError):
    pass


def _active_requirement_sources(
    requirement_contexts: Mapping[str, object] | None,
) -> dict[str, str]:
    if requirement_contexts is None:
        return {}
    if not isinstance(requirement_contexts, Mapping):
        raise WritingExecutionProfileError("requirement_contexts must be a mapping")
    active: dict[str, str] = {}
    for scope, raw_context in requirement_contexts.items():
        if not isinstance(raw_context, Mapping):
            raise WritingExecutionProfileError(f"requirement context invalid: {scope}")
        requirements = raw_context.get("requirements")
        if not isinstance(requirements, list):
            raise WritingExecutionProfileError(f"requirement list invalid: {scope}")
        for raw in requirements:
            if not isinstance(raw, Mapping):
                raise WritingExecutionProfileError(f"requirement record invalid: {scope}")
            requirement_id = str(raw.get("requirement_id", "")).strip()
            source_kind = str(raw.get("source_kind", "")).strip()
            if not requirement_id or source_kind not in {
                "USER_EXPLICIT", "USER_CORRECTION", "USER_PREFERENCE"
            }:
                raise WritingExecutionProfileError(f"requirement identity/source invalid: {scope}")
            previous = active.get(requirement_id)
            if previous is not None and previous != source_kind:
                raise WritingExecutionProfileError(
                    f"requirement source conflicts across scopes: {requirement_id}"
                )
            active[requirement_id] = source_kind
    return active


def validate_writing_execution_profile(
    raw: Mapping[str, object],
    requirement_contexts: Mapping[str, object] | None,
    *,
    source_prompt_sha256: str,
) -> dict[str, object]:
    """Validate prompt binding and exact requirement projection; never classify whole tasks."""
    if not isinstance(raw, Mapping):
        raise WritingExecutionProfileError("writing execution profile must be a mapping")
    if raw.get("source_prompt_sha256") != source_prompt_sha256:
        raise WritingExecutionProfileError("writing execution profile prompt binding mismatch")
    try:
        profile = WritingExecutionProfile.model_validate(raw)
    except Exception as exc:
        raise WritingExecutionProfileError("writing execution profile schema invalid") from exc
    active = _active_requirement_sources(requirement_contexts)
    expected_fixed = {
        rid for rid, source in active.items() if source in {"USER_EXPLICIT", "USER_CORRECTION"}
    }
    expected_preferences = {
        rid for rid, source in active.items() if source == "USER_PREFERENCE"
    }
    if set(profile.fixed_requirement_ids) != expected_fixed:
        raise WritingExecutionProfileError("fixed requirement ids do not match active user requirements")
    if set(profile.preference_requirement_ids) != expected_preferences:
        raise WritingExecutionProfileError("preference requirement ids do not match active user preferences")
    return profile.model_dump(mode="json")
