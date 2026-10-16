from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator


REQUIREMENT_CONTRACT_VERSION = "1.0"
REQUIREMENT_AUTHORITY_PATH = "financial_writing_agent.task_requirements"
# Requirement invalidation must use the existing Financial revision graph rather than
# inventing a second rollback topology. These are exactly the canonical revision
# invalidation targets owned by workflow_spec.py.
VALID_AFFECTED_STAGES = {
    "RESEARCH",
    "EDITORIAL",
    "TITLE",
    "DRAFT",
    "DELIVERY",
}
VALID_SCOPES = {
    "ALL",
    "RESEARCH",
    "PRIVATE_RESEARCH",
    "FINANCE_DEEP",
    "FINANCE_BROAD",
    "PLATFORM_INTERACTION",
    "DELIVERY",
}


class RequirementError(ValueError):
    pass


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TaskRequirement(StrictModel):
    requirement_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    scopes: list[str] = Field(min_length=1)
    affects_from_stage: str
    evidence_ref: str = Field(min_length=1)
    source_kind: str = "USER_EXPLICIT"

    @model_validator(mode="after")
    def validate_requirement(self):
        unknown_scopes = sorted(set(self.scopes) - VALID_SCOPES)
        if unknown_scopes:
            raise ValueError(f"unsupported requirement scopes: {unknown_scopes}")
        if self.affects_from_stage not in VALID_AFFECTED_STAGES:
            raise ValueError(f"unsupported affects_from_stage: {self.affects_from_stage}")
        return self


class RequirementHistoryEntry(StrictModel):
    revision: int = Field(ge=1)
    action: str
    requirement_id: str = Field(min_length=1)
    previous: dict[str, Any] | None = None
    current: dict[str, Any] | None = None
    evidence_ref: str = Field(min_length=1)


class RequirementAuthority(StrictModel):
    contract_version: str = REQUIREMENT_CONTRACT_VERSION
    revision: int = Field(ge=0)
    active_requirements: list[TaskRequirement] = Field(default_factory=list)
    history: list[RequirementHistoryEntry] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_authority(self):
        if self.contract_version != REQUIREMENT_CONTRACT_VERSION:
            raise ValueError(f"unsupported requirement contract version: {self.contract_version}")
        ids = [item.requirement_id for item in self.active_requirements]
        if len(ids) != len(set(ids)):
            raise ValueError("active requirement ids must be unique")
        if self.history and max(item.revision for item in self.history) > self.revision:
            raise ValueError("requirement history revision cannot exceed authority revision")
        return self


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def empty_requirement_authority() -> dict[str, Any]:
    return RequirementAuthority(revision=0).model_dump(mode="json")


def validate_requirement_authority(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise RequirementError("task requirement authority is required")
    try:
        authority = RequirementAuthority.model_validate(raw)
    except ValueError as exc:
        raise RequirementError(str(exc)) from exc
    return authority.model_dump(mode="json")


def authority_digest(raw: Mapping[str, Any] | None) -> str:
    return canonical_digest(validate_requirement_authority(raw))


def active_requirements_for_scope(raw: Mapping[str, Any], scope: str) -> list[dict[str, Any]]:
    if scope not in VALID_SCOPES:
        raise RequirementError(f"unsupported requirement scope: {scope}")
    authority = RequirementAuthority.model_validate(raw)
    return [
        item.model_dump(mode="json")
        for item in authority.active_requirements
        if "ALL" in item.scopes or scope in item.scopes
    ]


def apply_requirement_changes(
    raw: Mapping[str, Any],
    *,
    upserts: list[Mapping[str, Any]] | None = None,
    retire_ids: list[str] | None = None,
    evidence_ref: str,
) -> tuple[dict[str, Any], list[str]]:
    """Apply one bounded requirement transaction and return changed affected stages.

    Requirement content remains task-scoped evidence. This function does not promote a
    task requirement into a Financial-wide rule.
    """
    if not evidence_ref or not str(evidence_ref).strip():
        raise RequirementError("requirement change requires evidence_ref")

    authority = RequirementAuthority.model_validate(raw)
    active = {item.requirement_id: item for item in authority.active_requirements}
    changed_stages: list[str] = []
    history = list(authority.history)
    next_revision = authority.revision + 1

    retire_set = {str(item).strip() for item in (retire_ids or []) if str(item).strip()}
    for requirement_id in sorted(retire_set):
        previous = active.pop(requirement_id, None)
        if previous is None:
            raise RequirementError(f"cannot retire unknown active requirement: {requirement_id}")
        changed_stages.append(previous.affects_from_stage)
        history.append(
            RequirementHistoryEntry(
                revision=next_revision,
                action="RETIRE",
                requirement_id=requirement_id,
                previous=previous.model_dump(mode="json"),
                current=None,
                evidence_ref=evidence_ref,
            )
        )

    seen_upserts: set[str] = set()
    for raw_item in upserts or []:
        try:
            item = TaskRequirement.model_validate(raw_item)
        except ValueError as exc:
            raise RequirementError(str(exc)) from exc
        if item.requirement_id in seen_upserts:
            raise RequirementError(f"duplicate upsert requirement_id: {item.requirement_id}")
        seen_upserts.add(item.requirement_id)
        previous = active.get(item.requirement_id)
        if previous is not None and previous.model_dump(mode="json") == item.model_dump(mode="json"):
            continue
        if previous is not None:
            changed_stages.append(previous.affects_from_stage)
        changed_stages.append(item.affects_from_stage)
        active[item.requirement_id] = item
        history.append(
            RequirementHistoryEntry(
                revision=next_revision,
                action="REPLACE" if previous is not None else "ADD",
                requirement_id=item.requirement_id,
                previous=previous.model_dump(mode="json") if previous is not None else None,
                current=item.model_dump(mode="json"),
                evidence_ref=evidence_ref,
            )
        )

    if not history or (history and history[-1].revision != next_revision):
        raise RequirementError("requirement transaction made no effective change")

    updated = RequirementAuthority(
        contract_version=REQUIREMENT_CONTRACT_VERSION,
        revision=next_revision,
        active_requirements=sorted(active.values(), key=lambda item: item.requirement_id),
        history=history,
    )
    return updated.model_dump(mode="json"), changed_stages


def requirement_snapshot(raw: Mapping[str, Any]) -> dict[str, Any]:
    authority = RequirementAuthority.model_validate(deepcopy(dict(raw)))
    dumped = authority.model_dump(mode="json")
    return {
        "contract_version": REQUIREMENT_CONTRACT_VERSION,
        "revision": dumped["revision"],
        "digest": canonical_digest(dumped),
        "active_requirements": dumped["active_requirements"],
    }
