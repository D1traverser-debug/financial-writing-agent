from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Literal, Mapping

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

# These scopes are activated by the immutable TaskContract output set. Research
# is shared, so every requested product scope can constrain RESEARCH; later
# product stages consume only their own branch. DELIVERY is always a real owner
# stage, while PRIVATE_RESEARCH is mandatory for current writing-kernel tasks.
OUTPUT_SCOPE_MAP = {
    "FINANCE_DEEP_DOCX": "FINANCE_DEEP",
    "FINANCE_BROAD_DOCX": "FINANCE_BROAD",
    "PLATFORM_INTERACTION_PACK_DOCX": "PLATFORM_INTERACTION",
}
ALWAYS_ACTIVE_SCOPES = {"ALL", "RESEARCH", "PRIVATE_RESEARCH", "DELIVERY"}
ALLOWED_OUTPUT_KINDS = {
    "AUDIT_DOCX", "PRIVATE_RESEARCH_DOCX", *OUTPUT_SCOPE_MAP,
}
SCOPE_AFFECTED_STAGES = {
    "ALL": set(VALID_AFFECTED_STAGES),
    "RESEARCH": {"RESEARCH"},
    "PRIVATE_RESEARCH": {"RESEARCH"},
    "FINANCE_DEEP": set(VALID_AFFECTED_STAGES),
    "FINANCE_BROAD": set(VALID_AFFECTED_STAGES),
    "PLATFORM_INTERACTION": {"RESEARCH", "DRAFT", "DELIVERY"},
    "DELIVERY": {"DELIVERY"},
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
    # No model/default path may fabricate the user's authority for inferred text.
    source_kind: str


    @model_validator(mode="after")
    def validate_requirement(self):
        unknown_scopes = sorted(set(self.scopes) - VALID_SCOPES)
        if unknown_scopes:
            raise ValueError(f"unsupported requirement scopes: {unknown_scopes}")
        if len(self.scopes) != len(set(self.scopes)):
            raise ValueError("requirement scopes must be unique")
        if self.source_kind not in {"USER_EXPLICIT", "USER_CORRECTION", "USER_PREFERENCE"}:
            raise ValueError("non-authoritative suggestion, hypothesis or issue cannot enter active TaskRequirement")
        if self.affects_from_stage not in VALID_AFFECTED_STAGES:
            raise ValueError(f"unsupported affects_from_stage: {self.affects_from_stage}")
        return self


class RequirementHistoryEntry(StrictModel):
    revision: int = Field(ge=1)
    action: Literal["ADD", "REPLACE", "RETIRE"]
    requirement_id: str = Field(min_length=1)
    previous: dict[str, Any] | None = None
    current: dict[str, Any] | None = None
    evidence_ref: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_history_transition(self):
        if self.action == "ADD":
            if self.previous is not None or self.current is None:
                raise ValueError("ADD history requires previous=null and current")
        elif self.action == "REPLACE":
            if self.previous is None or self.current is None:
                raise ValueError("REPLACE history requires both previous and current")
        elif self.action == "RETIRE":
            if self.previous is None or self.current is not None:
                raise ValueError("RETIRE history requires previous and current=null")

        for label, raw in (("previous", self.previous), ("current", self.current)):
            if raw is None:
                continue
            try:
                parsed = TaskRequirement.model_validate(raw)
            except ValueError as exc:
                raise ValueError(f"{label} history requirement is invalid") from exc
            if parsed.requirement_id != self.requirement_id:
                raise ValueError(f"{label} history requirement_id mismatch")
        return self


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
        if ids != sorted(ids):
            raise ValueError("active requirements must use canonical requirement_id order")

        if self.revision == 0:
            if self.history or self.active_requirements:
                raise ValueError("revision-zero requirement authority must be empty")
            return self
        if not self.history:
            raise ValueError("nonzero requirement authority requires complete change history")

        revisions = [item.revision for item in self.history]
        if revisions != sorted(revisions):
            raise ValueError("requirement history must be in revision order")
        if set(revisions) != set(range(1, self.revision + 1)) or revisions[-1] != self.revision:
            raise ValueError("requirement history must contain every authority revision exactly in order")

        replayed: dict[str, dict[str, Any]] = {}
        revision_seen_ids: set[str] = set()
        revision_evidence_ref: str | None = None
        current_revision = 0
        for entry in self.history:
            if entry.revision != current_revision:
                current_revision = entry.revision
                revision_seen_ids = set()
                revision_evidence_ref = entry.evidence_ref
            elif entry.evidence_ref != revision_evidence_ref:
                raise ValueError("one requirement revision must use one owner evidence_ref")
            if entry.requirement_id in revision_seen_ids:
                raise ValueError("one requirement revision cannot mutate the same requirement twice")
            revision_seen_ids.add(entry.requirement_id)

            previous = entry.previous
            current = entry.current
            active_before = replayed.get(entry.requirement_id)
            if entry.action == "ADD":
                if active_before is not None:
                    raise ValueError("ADD history cannot add an already-active requirement")
                replayed[entry.requirement_id] = dict(current or {})
            elif entry.action == "REPLACE":
                if active_before is None or active_before != previous:
                    raise ValueError("REPLACE history previous value does not match replayed authority")
                replayed[entry.requirement_id] = dict(current or {})
            elif entry.action == "RETIRE":
                if active_before is None or active_before != previous:
                    raise ValueError("RETIRE history previous value does not match replayed authority")
                del replayed[entry.requirement_id]

        active_dump = {
            item.requirement_id: item.model_dump(mode="json")
            for item in self.active_requirements
        }
        if replayed != active_dump:
            raise ValueError("active requirements do not match complete replayed history")
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


def active_task_scopes(required_outputs: Any) -> list[str]:
    """Return the requirement scopes that can affect this immutable output contract."""
    if not isinstance(required_outputs, (list, tuple, set)) or not required_outputs:
        raise RequirementError("task required_outputs are required for scope resolution")
    outputs: set[str] = set()
    for raw in required_outputs:
        value = getattr(raw, "value", raw)
        if not isinstance(value, str) or not value.strip():
            raise RequirementError("task required_outputs contain an invalid output kind")
        outputs.add(value.strip())
    unknown = sorted(outputs - ALLOWED_OUTPUT_KINDS)
    if unknown:
        raise RequirementError(f"unsupported task output kinds for requirement scope resolution: {unknown}")
    scopes = set(ALWAYS_ACTIVE_SCOPES)
    scopes.update(OUTPUT_SCOPE_MAP[item] for item in outputs if item in OUTPUT_SCOPE_MAP)
    return sorted(scopes)


def requirement_applies_to_scopes(requirement: Mapping[str, Any], scopes: Any) -> bool:
    """Whether a requirement applies to one stage's admitted scope projection."""
    try:
        parsed = TaskRequirement.model_validate(requirement)
    except ValueError as exc:
        raise RequirementError("invalid task requirement during scope resolution") from exc
    selected = set(scopes)
    return "ALL" in parsed.scopes or bool(selected.intersection(parsed.scopes))


def requirement_applies_to_task(requirement: Mapping[str, Any], required_outputs: Any) -> bool:
    """Whether at least one scope of a requirement is active in the task's output contract."""
    return requirement_applies_to_scopes(requirement, active_task_scopes(required_outputs))


def requirement_scopes_for_stage(stage: str, required_outputs: Any) -> list[str]:
    """Canonical stage-to-scope projection shared by the coordinator and owner aggregate."""
    active = set(active_task_scopes(required_outputs))
    product_scopes = active - ALWAYS_ACTIVE_SCOPES
    longform_scopes = product_scopes.intersection({"FINANCE_DEEP", "FINANCE_BROAD"})
    if stage in {"RESEARCH", "RESEARCH_AUDIT"}:
        scopes = {"ALL", "RESEARCH", "PRIVATE_RESEARCH", *product_scopes}
    elif stage in {"EDITORIAL", "TITLE"}:
        scopes = {"ALL", *longform_scopes}
    elif stage in {"DRAFT", "EDITORIAL_AUDIT"}:
        scopes = {"ALL", *product_scopes}
    elif stage in {"DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT"}:
        scopes = {"ALL", "DELIVERY", *product_scopes}
    elif stage == "INTAKE":
        scopes = {"ALL"}
    else:
        raise RequirementError(f"unsupported task requirement stage: {stage}")
    return sorted(scopes)


def validate_requirement_applicability(
    requirement: Mapping[str, Any],
    required_outputs: Any,
) -> dict[str, Any]:
    """Reject requirements that target no requested product or an impossible scope/stage pair."""
    try:
        parsed = TaskRequirement.model_validate(requirement)
    except ValueError as exc:
        raise RequirementError(str(exc)) from exc
    active = set(active_task_scopes(required_outputs))
    applicable = set(parsed.scopes).intersection(active)
    if "ALL" not in parsed.scopes and not applicable:
        raise RequirementError(
            f"requirement {parsed.requirement_id} scopes do not match the requested outputs"
        )
    if "ALL" not in parsed.scopes:
        incompatible = sorted(
            scope for scope in applicable
            if parsed.affects_from_stage not in SCOPE_AFFECTED_STAGES[scope]
        )
        if incompatible:
            raise RequirementError(
                f"requirement {parsed.requirement_id} affects_from_stage "
                f"{parsed.affects_from_stage} is incompatible with active scopes {incompatible}"
            )
    return parsed.model_dump(mode="json")


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

    if retire_ids is not None and not isinstance(retire_ids, list):
        raise RequirementError("retire_ids must be a list")
    raw_retire_ids = list(retire_ids or [])
    if any(not isinstance(item, str) or not item.strip() for item in raw_retire_ids):
        raise RequirementError("retire_ids must contain nonempty strings")
    normalized_retire_ids = [item.strip() for item in raw_retire_ids]
    if len(normalized_retire_ids) != len(set(normalized_retire_ids)):
        raise RequirementError("duplicate retire requirement_id")
    retire_set = set(normalized_retire_ids)
    if upserts is not None and not isinstance(upserts, list):
        raise RequirementError("upserts must be a list")
    upsert_ids = [str(item.get("requirement_id", "")).strip() for item in (upserts or [])
                  if isinstance(item, Mapping)]
    if retire_set.intersection(upsert_ids):
        raise RequirementError("cannot simultaneously retire and upsert the same active requirement")

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
