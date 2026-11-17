"""Task-intake contract: preserve the complete user goal before execution.

The manifest is task-scoped evidence owned by the Financial Article Aggregate.
It separates binding requirements from preferences, open decisions and
nonbinding ideas. A separate authenticated reviewer must challenge coverage
against the original prompt before INTAKE can advance.
"""
from __future__ import annotations

import hashlib
import os
from collections.abc import Mapping
from typing import Any, Literal

from pydantic import Field, model_validator

from .provider_attestation import (
    FinancialProviderAttestationError,
    expected_owner_principal,
    verify_provider_attestation,
)
from .task_requirements import (
    StrictModel,
    TaskRequirement,
    active_task_scopes,
    validate_requirement_applicability,
)
from .writing_execution_profile import validate_writing_execution_profile
from .workflow_spec import BUSINESS_STAGE_NAMES


TASK_INTAKE_CONTRACT_VERSION = "1.0"
INTAKE_REVIEW_KEY_ENV = "FINANCIAL_INTAKE_REVIEW_KEY"
INTAKE_REVIEW_PROVIDER_ENV = "FINANCIAL_INTAKE_REVIEW_PROVIDER_ID"
KNOWN_STAGES = frozenset(BUSINESS_STAGE_NAMES)


class TaskIntakeError(ValueError):
    pass


class IntakeInstructionUnit(StrictModel):
    unit_id: str = Field(min_length=1)
    category: Literal[
        "GOAL", "REQUIREMENT", "CORRECTION", "PREFERENCE", "SUGGESTION",
        "ISSUE", "QUESTION", "APPROVAL", "CONTEXT",
    ]
    disposition: Literal[
        "BINDING", "PREFERENCE", "OPEN", "NONBINDING", "CLARIFICATION_REQUIRED",
    ]
    source_excerpt: str = Field(min_length=1)
    requirement_ids: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_classification(self):
        if len(self.requirement_ids) != len(set(self.requirement_ids)):
            raise ValueError("instruction-unit requirement_ids must be unique")
        if self.disposition in {"BINDING", "PREFERENCE"} and not self.requirement_ids:
            raise ValueError("binding/preference instruction units must map to requirements")
        if self.disposition not in {"BINDING", "PREFERENCE"} and self.requirement_ids:
            raise ValueError("open/nonbinding/clarification units cannot create authoritative requirements")
        if self.disposition == "PREFERENCE" and self.category != "PREFERENCE":
            raise ValueError("PREFERENCE disposition requires PREFERENCE category")
        if self.disposition == "BINDING" and self.category not in {"GOAL", "REQUIREMENT", "CORRECTION"}:
            raise ValueError("BINDING disposition requires GOAL/REQUIREMENT/CORRECTION category")
        if self.disposition == "NONBINDING" and self.category not in {"SUGGESTION", "ISSUE"}:
            raise ValueError("NONBINDING disposition requires SUGGESTION or ISSUE category")
        if self.disposition == "CLARIFICATION_REQUIRED" and self.category != "QUESTION":
            raise ValueError("CLARIFICATION_REQUIRED disposition requires QUESTION category")
        return self


class IntakeRequirementLink(StrictModel):
    source_unit_ids: list[str] = Field(min_length=1)
    requirement: TaskRequirement

    @model_validator(mode="after")
    def validate_sources(self):
        if len(self.source_unit_ids) != len(set(self.source_unit_ids)):
            raise ValueError("requirement source_unit_ids must be unique")
        return self


class IntakeRouteDecision(StrictModel):
    route_id: str = Field(min_length=1)
    decision: Literal["REQUIRED", "OPTIONAL", "NOT_REQUIRED"]
    stages: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)
    trigger: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_route(self):
        if len(self.stages) != len(set(self.stages)):
            raise ValueError("route stages must be unique")
        unknown = set(self.stages) - KNOWN_STAGES
        if unknown:
            raise ValueError(f"unknown route stages: {sorted(unknown)}")
        if self.decision == "NOT_REQUIRED" and self.stages:
            raise ValueError("NOT_REQUIRED route cannot claim execution stages")
        if self.decision != "NOT_REQUIRED" and not self.stages:
            raise ValueError("required/optional route must identify execution stages")
        return self


class IntakeSuccessCriterion(StrictModel):
    criterion_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    requirement_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_criterion(self):
        if len(self.requirement_ids) != len(set(self.requirement_ids)):
            raise ValueError("success criterion requirement_ids must be unique")
        return self


class TaskIntakeManifest(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    task_id: str = Field(min_length=1)
    source_message_ref: str = Field(min_length=1)
    source_prompt_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    task_objective: str = Field(min_length=1)
    instruction_units: list[IntakeInstructionUnit] = Field(min_length=1)
    requirements: list[IntakeRequirementLink] = Field(min_length=1)
    requested_outputs: list[str] = Field(min_length=1)
    success_criteria: list[IntakeSuccessCriterion] = Field(min_length=1)
    writing_execution_profile: dict[str, Any]
    knowledge_routes: list[IntakeRouteDecision] = Field(min_length=1)
    capability_routes: list[IntakeRouteDecision] = Field(min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    blocking_questions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_ids(self):
        for name, values in (
            ("instruction unit", [item.unit_id for item in self.instruction_units]),
            ("requirement", [item.requirement.requirement_id for item in self.requirements]),
            ("requested output", self.requested_outputs),
            ("success criterion", [item.criterion_id for item in self.success_criteria]),
            ("knowledge route", [item.route_id for item in self.knowledge_routes]),
            ("capability route", [item.route_id for item in self.capability_routes]),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{name} IDs must be unique")
        if any(not item.strip() for item in self.requested_outputs):
            raise ValueError("requested_outputs cannot contain empty values")
        if any(not item.strip() for item in self.assumptions):
            raise ValueError("assumptions cannot contain empty values")
        if any(not item.strip() for item in self.blocking_questions):
            raise ValueError("blocking_questions cannot contain empty values")
        return self


def canonical_sha256(value: Any) -> str:
    import json
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_task_intake_manifest(
    raw: Mapping[str, Any] | None,
    *,
    task_id: str,
    prompt: str,
    required_outputs: list[str],
) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise TaskIntakeError("TASK_INTAKE_MANIFEST_REQUIRED")
    try:
        manifest = TaskIntakeManifest.model_validate(raw)
    except Exception as exc:
        raise TaskIntakeError(f"TASK_INTAKE_MANIFEST_SCHEMA_INVALID:{exc}") from exc
    normalized = manifest.model_dump(mode="json")
    prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if manifest.task_id != task_id:
        raise TaskIntakeError("TASK_INTAKE_TASK_ID_BINDING_MISMATCH")
    if manifest.source_prompt_sha256 != prompt_sha:
        raise TaskIntakeError("TASK_INTAKE_PROMPT_BINDING_MISMATCH")
    if not prompt.strip() or not manifest.task_objective.strip():
        raise TaskIntakeError("TASK_INTAKE_OBJECTIVE_REQUIRED")
    if manifest.blocking_questions:
        raise TaskIntakeError("TASK_INTAKE_BLOCKING_QUESTIONS_REMAIN")
    if any(unit.disposition == "CLARIFICATION_REQUIRED" for unit in manifest.instruction_units):
        raise TaskIntakeError("TASK_INTAKE_CLARIFICATION_REQUIRED")

    unit_by_id = {unit.unit_id: unit for unit in manifest.instruction_units}
    if len(unit_by_id) != len(manifest.instruction_units):
        raise TaskIntakeError("TASK_INTAKE_DUPLICATE_INSTRUCTION_UNIT")
    for unit in manifest.instruction_units:
        if unit.source_excerpt not in prompt:
            raise TaskIntakeError(f"TASK_INTAKE_SOURCE_EXCERPT_NOT_IN_PROMPT:{unit.unit_id}")

    requirement_by_id: dict[str, dict[str, Any]] = {}
    requirement_unit_ids: dict[str, set[str]] = {}
    for link in manifest.requirements:
        requirement = link.requirement.model_dump(mode="json")
        requirement_id = requirement["requirement_id"]
        if requirement_id in requirement_by_id:
            raise TaskIntakeError(f"TASK_INTAKE_DUPLICATE_REQUIREMENT:{requirement_id}")
        if requirement["evidence_ref"] != manifest.source_message_ref:
            raise TaskIntakeError(f"TASK_INTAKE_REQUIREMENT_SOURCE_MISMATCH:{requirement_id}")
        unknown_units = set(link.source_unit_ids) - set(unit_by_id)
        if unknown_units:
            raise TaskIntakeError(f"TASK_INTAKE_REQUIREMENT_SOURCE_UNIT_UNKNOWN:{requirement_id}")
        try:
            requirement = validate_requirement_applicability(requirement, required_outputs)
        except Exception as exc:
            raise TaskIntakeError(f"TASK_INTAKE_REQUIREMENT_SCOPE_INVALID:{requirement_id}") from exc
        if requirement["source_kind"] == "USER_CORRECTION":
            expected_disposition = "BINDING"
        elif requirement["source_kind"] == "USER_PREFERENCE":
            expected_disposition = "PREFERENCE"
        else:
            expected_disposition = "BINDING"
        for unit_id in link.source_unit_ids:
            unit = unit_by_id[unit_id]
            if requirement_id not in unit.requirement_ids:
                raise TaskIntakeError(f"TASK_INTAKE_REQUIREMENT_UNIT_LINK_DIVERGED:{requirement_id}:{unit_id}")
            if unit.disposition != expected_disposition:
                raise TaskIntakeError(f"TASK_INTAKE_REQUIREMENT_DISPOSITION_MISMATCH:{requirement_id}:{unit_id}")
        requirement_by_id[requirement_id] = requirement
        requirement_unit_ids[requirement_id] = set(link.source_unit_ids)

    for unit in manifest.instruction_units:
        for requirement_id in unit.requirement_ids:
            if requirement_id not in requirement_by_id:
                raise TaskIntakeError(f"TASK_INTAKE_INSTRUCTION_UNIT_UNKNOWN_REQUIREMENT:{unit.unit_id}:{requirement_id}")
            if unit.unit_id not in requirement_unit_ids[requirement_id]:
                raise TaskIntakeError(f"TASK_INTAKE_INSTRUCTION_UNIT_LINK_MISSING:{unit.unit_id}:{requirement_id}")
    if not any(
        unit.disposition == "BINDING" and unit.category == "GOAL"
        for unit in manifest.instruction_units
    ):
        raise TaskIntakeError("TASK_INTAKE_EXPLICIT_TASK_GOAL_UNIT_REQUIRED")

    required_set = set(required_outputs)
    requested_set = set(manifest.requested_outputs)
    if required_set != requested_set:
        raise TaskIntakeError(
            "TASK_INTAKE_OUTPUT_CONTRACT_MISMATCH:"
            f"missing={sorted(required_set - requested_set)};"
            f"unexpected={sorted(requested_set - required_set)}"
        )
    all_requirement_ids = set(requirement_by_id)
    criterion_ids = {
        requirement_id
        for criterion in manifest.success_criteria
        for requirement_id in criterion.requirement_ids
    }
    if criterion_ids - all_requirement_ids:
        raise TaskIntakeError("TASK_INTAKE_SUCCESS_CRITERION_UNKNOWN_REQUIREMENT")
    if criterion_ids != all_requirement_ids:
        raise TaskIntakeError("TASK_INTAKE_SUCCESS_CRITERIA_DO_NOT_COVER_ALL_REQUIREMENTS")

    scopes = active_task_scopes(required_outputs)
    requirement_values = list(requirement_by_id.values())
    contexts = {
        scope: {
            "requirements": [
                item for item in requirement_values
                if "ALL" in item["scopes"] or scope in item["scopes"]
            ],
        }
        for scope in scopes
    }
    try:
        validate_writing_execution_profile(
            manifest.writing_execution_profile,
            contexts,
            source_prompt_sha256=prompt_sha,
        )
    except Exception as exc:
        raise TaskIntakeError(f"TASK_INTAKE_WRITING_EXECUTION_PROFILE_INVALID:{exc}") from exc

    if not any(
        route.decision == "REQUIRED" and "RESEARCH" in route.stages
        for route in manifest.knowledge_routes
    ):
        raise TaskIntakeError("TASK_INTAKE_REQUIRED_RESEARCH_KNOWLEDGE_ROUTE_MISSING")
    if not any(
        route.decision == "REQUIRED"
        and set(route.stages).intersection({"EDITORIAL", "TITLE", "DRAFT", "DELIVERY"})
        for route in manifest.capability_routes
    ):
        raise TaskIntakeError("TASK_INTAKE_REQUIRED_WRITING_CAPABILITY_ROUTE_MISSING")
    if not any(
        route.decision == "REQUIRED"
        and set(route.stages).intersection({"DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT"})
        for route in manifest.capability_routes
    ):
        raise TaskIntakeError("TASK_INTAKE_REQUIRED_DELIVERY_CAPABILITY_ROUTE_MISSING")
    normalized["requirements"] = [
        {
            "source_unit_ids": list(link.source_unit_ids),
            "requirement": link.requirement.model_dump(mode="json"),
        }
        for link in manifest.requirements
    ]
    return normalized


def build_task_intake_review_challenge(
    *,
    task_id: str,
    prompt: str,
    manifest: Mapping[str, Any],
    required_outputs: list[str],
) -> dict[str, Any]:
    normalized = validate_task_intake_manifest(
        manifest, task_id=task_id, prompt=prompt, required_outputs=required_outputs,
    )
    requirement_ids = sorted(
        item["requirement"]["requirement_id"] for item in normalized["requirements"]
    )
    instruction_unit_ids = sorted(item["unit_id"] for item in normalized["instruction_units"])
    return {
        "review_scope": "TASK_INTAKE_SEMANTIC_COVERAGE",
        "task_id": task_id,
        "original_user_prompt": prompt,
        "source_prompt_sha256": normalized["source_prompt_sha256"],
        "source_message_ref": normalized["source_message_ref"],
        "manifest": normalized,
        "manifest_sha256": canonical_sha256(normalized),
        "required_outputs": sorted(required_outputs),
        "requirement_ids": requirement_ids,
        "instruction_unit_ids": instruction_unit_ids,
        "review_instructions": [
            "Reconstruct every material user instruction from the complete original prompt.",
            "Check negation, scope, exceptions, corrections, preferences, suggestions and questions.",
            "Check that each binding clause is represented by a correctly scoped requirement.",
            "Check that no preference, suggestion, issue or open decision was promoted to user authority.",
            "Check the requested output contract, success criteria, knowledge routes and capability routes.",
            "Reject if any material clause is omitted, weakened, widened, contradicted or misclassified.",
        ],
    }


def verify_task_intake_review(
    raw: Mapping[str, Any] | None,
    *,
    challenge: Mapping[str, Any],
    historical: bool = False,
) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise TaskIntakeError("TASK_INTAKE_INDEPENDENT_REVIEW_REQUIRED")
    try:
        verified = verify_provider_attestation(
            raw,
            expected_type="task_intake_review",
            expected_claims={
                "approved": True,
                "review_scope": "TASK_INTAKE_SEMANTIC_COVERAGE",
                "task_id": challenge["task_id"],
                "source_prompt_sha256": challenge["source_prompt_sha256"],
                "manifest_sha256": challenge["manifest_sha256"],
                "covered_instruction_unit_ids": challenge["instruction_unit_ids"],
                "requirement_ids": challenge["requirement_ids"],
                "uncovered_material_unit_ids": [],
                "unmapped_requirement_ids": [],
                "blocking_question_ids": [],
                "requested_outputs_complete": True,
                "success_criteria_complete": True,
                "execution_profile_complete": True,
                "knowledge_routes_reviewed": True,
                "capability_routes_reviewed": True,
            },
            key_env=INTAKE_REVIEW_KEY_ENV,
            provider_env=INTAKE_REVIEW_PROVIDER_ENV,
            max_age_seconds=None if historical else 300,
        )
        owner = expected_owner_principal()
        if verified["authenticated_actor"] == owner:
            raise FinancialProviderAttestationError("TASK_INTAKE_REVIEWER_MUST_DIFFER_FROM_OWNER")
        if verified["provider_id"] == os.environ.get("FINANCIAL_TRUSTED_PROVIDER_ID"):
            raise FinancialProviderAttestationError("TASK_INTAKE_REVIEW_PROVIDER_NOT_INDEPENDENT")
    except Exception as exc:
        raise TaskIntakeError("TASK_INTAKE_INDEPENDENT_REVIEW_ATTESTATION_INVALID") from exc
    return verified
