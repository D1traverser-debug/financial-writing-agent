from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from pydantic import Field, model_validator

from .task_requirements import StrictModel, VALID_SCOPES


WORKFLOW_CONTRACT = "FINANCIAL_ARTICLE_10_STAGE_V1"


class DecisionDomainBinding(StrictModel):
    """Auditable link from a locked/open decision to the existing requirement authority."""

    domain: str = Field(min_length=1)
    disposition: Literal["LOCKED", "OPEN"]
    scopes: list[str] = Field(min_length=1)
    requirement_ids: list[str] = Field(default_factory=list)
    preference_ids: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_binding(self):
        for name in ("scopes", "requirement_ids", "preference_ids"):
            values = getattr(self, name)
            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(f"{name} must contain non-empty strings")
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must be unique")
        unknown = set(self.scopes) - VALID_SCOPES
        if unknown:
            raise ValueError(f"unsupported decision-domain scopes: {sorted(unknown)}")
        if "ALL" in self.scopes and len(self.scopes) != 1:
            raise ValueError("ALL must be the only decision-domain scope")
        if self.disposition == "LOCKED" and not self.requirement_ids:
            raise ValueError("LOCKED decision domain requires explicit/corrective requirement IDs")
        if self.disposition == "OPEN" and self.requirement_ids:
            raise ValueError("OPEN decision domain cannot bind hard requirement IDs")
        if not self.rationale.strip():
            raise ValueError("decision-domain rationale is required")
        return self


class WritingExecutionProfile(StrictModel):
    """Prompt-bound context: invariant process plus evidence-bound locked/open decisions."""

    schema_version: Literal["1.1"] = "1.1"
    workflow_contract: Literal["FINANCIAL_ARTICLE_10_STAGE_V1"] = WORKFLOW_CONTRACT
    source_prompt_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    fixed_requirement_ids: list[str] = Field(default_factory=list)
    preference_requirement_ids: list[str] = Field(default_factory=list)
    decision_domains: list[DecisionDomainBinding] = Field(min_length=1)
    conditional_modules: list[str] = Field(default_factory=list)
    execution_rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_profile(self):
        for name in (
            "fixed_requirement_ids", "preference_requirement_ids", "conditional_modules",
        ):
            values = getattr(self, name)
            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(f"{name} must contain non-empty strings")
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must be unique")
        if set(self.fixed_requirement_ids) & set(self.preference_requirement_ids):
            raise ValueError("fixed and preference requirement IDs must be disjoint")
        if not self.execution_rationale.strip():
            raise ValueError("execution_rationale is required")

        for index, left in enumerate(self.decision_domains):
            for right in self.decision_domains[index + 1:]:
                if left.domain != right.domain:
                    continue
                overlaps = (
                    "ALL" in left.scopes
                    or "ALL" in right.scopes
                    or bool(set(left.scopes) & set(right.scopes))
                )
                if overlaps:
                    raise ValueError(
                        f"decision domain has overlapping dispositions: {left.domain}"
                    )
        return self


class WritingExecutionProfileError(ValueError):
    pass


def _active_requirement_sources(
    requirement_contexts: Mapping[str, object] | None,
) -> dict[str, dict[str, Any]]:
    if requirement_contexts is None:
        return {}
    if not isinstance(requirement_contexts, Mapping):
        raise WritingExecutionProfileError("requirement_contexts must be a mapping")
    active: dict[str, dict[str, Any]] = {}
    for scope, raw_context in requirement_contexts.items():
        if not isinstance(raw_context, Mapping):
            raise WritingExecutionProfileError(f"requirement context invalid: {scope}")
        requirements = raw_context.get("requirements")
        if not isinstance(requirements, list):
            raise WritingExecutionProfileError(f"requirement list invalid: {scope}")
        for raw in requirements:
            if not isinstance(raw, Mapping):
                raise WritingExecutionProfileError(f"requirement record invalid: {scope}")
            raw_requirement_id = raw.get("requirement_id")
            raw_source_kind = raw.get("source_kind")
            raw_scopes = raw.get("scopes")
            raw_evidence_ref = raw.get("evidence_ref")
            if (
                not isinstance(raw_requirement_id, str)
                or not raw_requirement_id.strip()
                or not isinstance(raw_source_kind, str)
                or raw_source_kind not in {"USER_EXPLICIT", "USER_CORRECTION", "USER_PREFERENCE"}
                or not isinstance(raw_scopes, list)
                or not raw_scopes
                or any(not isinstance(item, str) for item in raw_scopes)
                or len(raw_scopes) != len(set(raw_scopes))
                or not set(raw_scopes) <= VALID_SCOPES
                or not isinstance(raw_evidence_ref, str)
                or not raw_evidence_ref.strip()
            ):
                raise WritingExecutionProfileError(
                    f"requirement identity/source/scope/evidence invalid: {scope}"
                )
            requirement_id = raw_requirement_id.strip()
            source_kind = raw_source_kind
            evidence_ref = raw_evidence_ref.strip()
            current = {
                "source_kind": source_kind,
                "scopes": set(raw_scopes),
                "evidence_ref": evidence_ref,
            }
            previous = active.get(requirement_id)
            if previous is not None:
                if (
                    previous["source_kind"] != current["source_kind"]
                    or previous["scopes"] != current["scopes"]
                    or previous["evidence_ref"] != current["evidence_ref"]
                ):
                    raise WritingExecutionProfileError(
                        f"requirement authority conflicts across scopes: {requirement_id}"
                    )
            else:
                active[requirement_id] = current
    return active


def _binding_scope_is_within_requirement(
    binding_scopes: set[str],
    requirement_scopes: set[str],
) -> bool:
    if "ALL" in requirement_scopes:
        return True
    if "ALL" in binding_scopes:
        return False
    return binding_scopes <= requirement_scopes


def _requirement_scope_is_fully_mapped(
    requirement_scopes: set[str],
    mapped_scopes: set[str],
) -> bool:
    if "ALL" in requirement_scopes:
        return "ALL" in mapped_scopes
    if "ALL" in mapped_scopes:
        return True
    return requirement_scopes <= mapped_scopes


def validate_writing_execution_profile(
    raw: Mapping[str, object],
    requirement_contexts: Mapping[str, object] | None,
    *,
    source_prompt_sha256: str,
) -> dict[str, object]:
    """Validate prompt binding, exact requirement projection and domain-to-authority links."""
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
        rid for rid, item in active.items()
        if item["source_kind"] in {"USER_EXPLICIT", "USER_CORRECTION"}
    }
    expected_preferences = {
        rid for rid, item in active.items()
        if item["source_kind"] == "USER_PREFERENCE"
    }
    if set(profile.fixed_requirement_ids) != expected_fixed:
        raise WritingExecutionProfileError(
            "fixed requirement IDs do not match active user requirements"
        )
    if set(profile.preference_requirement_ids) != expected_preferences:
        raise WritingExecutionProfileError(
            "preference requirement IDs do not match active user preferences"
        )

    mapped_fixed: set[str] = set()
    mapped_preferences: set[str] = set()
    fixed_scope_map: dict[str, set[str]] = {rid: set() for rid in expected_fixed}
    preference_scope_map: dict[str, set[str]] = {rid: set() for rid in expected_preferences}

    for binding in profile.decision_domains:
        binding_scopes = set(binding.scopes)
        if binding.disposition == "LOCKED" and not binding.requirement_ids:
            raise WritingExecutionProfileError(
                f"locked decision domain lacks hard requirement evidence: {binding.domain}"
            )
        if binding.disposition == "OPEN" and binding.requirement_ids:
            raise WritingExecutionProfileError(
                f"open decision domain carries hard requirement evidence: {binding.domain}"
            )
        for requirement_id in binding.requirement_ids:
            if requirement_id not in expected_fixed:
                raise WritingExecutionProfileError(
                    f"decision domain references non-fixed requirement: {requirement_id}"
                )
            declared_scopes = active[requirement_id]["scopes"]
            if not _binding_scope_is_within_requirement(binding_scopes, declared_scopes):
                raise WritingExecutionProfileError(
                    f"decision domain widens requirement scope: {binding.domain}:{requirement_id}"
                )
            mapped_fixed.add(requirement_id)
            fixed_scope_map[requirement_id].update(binding_scopes)
        for preference_id in binding.preference_ids:
            if preference_id not in expected_preferences:
                raise WritingExecutionProfileError(
                    f"decision domain references non-preference requirement: {preference_id}"
                )
            declared_scopes = active[preference_id]["scopes"]
            if not _binding_scope_is_within_requirement(binding_scopes, declared_scopes):
                raise WritingExecutionProfileError(
                    f"decision domain widens preference scope: {binding.domain}:{preference_id}"
                )
            mapped_preferences.add(preference_id)
            preference_scope_map[preference_id].update(binding_scopes)

    if mapped_fixed != expected_fixed:
        raise WritingExecutionProfileError(
            "decision domains do not map every active fixed requirement"
        )
    if mapped_preferences != expected_preferences:
        raise WritingExecutionProfileError(
            "decision domains do not map every active preference"
        )
    for requirement_id, declared_scopes in (
        (rid, item["scopes"]) for rid, item in active.items()
        if item["source_kind"] in {"USER_EXPLICIT", "USER_CORRECTION"}
    ):
        if not _requirement_scope_is_fully_mapped(
            declared_scopes, fixed_scope_map[requirement_id],
        ):
            raise WritingExecutionProfileError(
                f"fixed requirement scope is not fully mapped: {requirement_id}"
            )
    for preference_id, declared_scopes in (
        (rid, item["scopes"]) for rid, item in active.items()
        if item["source_kind"] == "USER_PREFERENCE"
    ):
        if not _requirement_scope_is_fully_mapped(
            declared_scopes, preference_scope_map[preference_id],
        ):
            raise WritingExecutionProfileError(
                f"preference scope is not fully mapped: {preference_id}"
            )
    return profile.model_dump(mode="json")
