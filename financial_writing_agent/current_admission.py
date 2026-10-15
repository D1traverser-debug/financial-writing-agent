from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

from . import owner_guard
from .cognition_governance import DecisionEnvelope, OperationClass, admission_errors
from .story_quality import AuditStatus, ProductMode, PublicationFitness, StoryBlueprint

WRITING_KERNEL_VERSION = owner_guard.CURRENT_WRITING_KERNEL_VERSION
QUALITY_ADMISSION_PATH = owner_guard.CURRENT_QUALITY_ADMISSION_PATH


class CurrentAdmissionError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CurrentAdmissionError(message)


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _expected_longform_modes(state: Mapping[str, Any]) -> set[ProductMode]:
    outputs = set(state.get("required_outputs", []))
    expected: set[ProductMode] = set()
    if "FINANCE_DEEP_DOCX" in outputs:
        expected.add(ProductMode.FINANCE_DEEP)
    if "FINANCE_BROAD_DOCX" in outputs:
        expected.add(ProductMode.FINANCE_BROAD)
    return expected


def _parse_story_blueprints(state: Mapping[str, Any], raw: list[Mapping[str, Any]] | None) -> list[StoryBlueprint]:
    _require(isinstance(raw, list) and raw, "current EDITORIAL transition requires story_blueprints")
    parsed = [StoryBlueprint.model_validate(item) for item in raw]
    modes = [item.product_mode for item in parsed]
    _require(len(modes) == len(set(modes)), "story_blueprints must contain at most one blueprint per product mode")
    expected = _expected_longform_modes(state)
    _require(
        set(modes) == expected,
        f"story blueprint modes mismatch: expected={sorted(x.value for x in expected)}, actual={sorted(x.value for x in set(modes))}",
    )
    return parsed


def _parse_publication_fitnesses(
    state: Mapping[str, Any], raw: list[Mapping[str, Any]] | None, *, review_status: str
) -> list[PublicationFitness]:
    _require(isinstance(raw, list) and raw, "current EDITORIAL_AUDIT requires publication_fitnesses")
    parsed = [PublicationFitness.model_validate(item) for item in raw]
    modes = [item.product_mode for item in parsed]
    _require(len(modes) == len(set(modes)), "publication_fitnesses must contain at most one result per product mode")
    expected = _expected_longform_modes(state)
    _require(
        set(modes) == expected,
        f"publication fitness modes mismatch: expected={sorted(x.value for x in expected)}, actual={sorted(x.value for x in set(modes))}",
    )

    all_pass = all(item.final_status == AuditStatus.PASS for item in parsed)
    if review_status == "PASS":
        _require(all_pass, "EDITORIAL_AUDIT cannot PASS while any publication fitness gate requires revision")
    elif review_status == "REVISE":
        _require(not all_pass, "EDITORIAL_AUDIT REVISE requires at least one publication fitness REVISE result")
    return parsed


def _parse_decision_envelope(raw: Mapping[str, Any] | None) -> DecisionEnvelope:
    _require(isinstance(raw, Mapping), "current RESEARCH transition requires decision_envelope")
    envelope = DecisionEnvelope.model_validate(raw)
    _require(
        envelope.operation_class == OperationClass.MATERIAL_JUDGMENT,
        "RESEARCH decision envelope must represent a MATERIAL_JUDGMENT",
    )
    semantic_errors = admission_errors(envelope)
    _require(not semantic_errors, f"decision envelope admission failed: {semantic_errors}")
    return envelope


def _latest_receipt_digest(state: Mapping[str, Any], binding_key: str, *, admitting_stage: str) -> str | None:
    receipts = state.get("execution_receipts", [])
    if not isinstance(receipts, list):
        return None
    for receipt in reversed(receipts):
        if not isinstance(receipt, Mapping) or receipt.get("stage") != admitting_stage:
            continue
        bindings = receipt.get("input_bindings", {})
        if not isinstance(bindings, Mapping):
            continue
        if bindings.get("quality_admission_path") != QUALITY_ADMISSION_PATH:
            continue
        if bindings.get("writing_kernel_version") != WRITING_KERNEL_VERSION:
            continue
        if binding_key in bindings:
            value = bindings.get(binding_key)
            return str(value) if value is not None else None
    return None


def _require_persisted_digest(
    state: Mapping[str, Any], *, evidence_key: str, binding_key: str, admitting_stage: str, evidence_value: Any
) -> None:
    expected = _latest_receipt_digest(state, binding_key, admitting_stage=admitting_stage)
    _require(expected is not None, f"persisted {evidence_key} lacks a {admitting_stage} current-admission receipt digest")
    actual = _canonical_digest(evidence_value)
    _require(actual == expected, f"persisted {evidence_key} no longer matches its latest admitted receipt digest")


def _validate_current_quality_evidence(state: Mapping[str, Any]) -> None:
    """Validate current quality semantics after owner authority has authenticated the state blob.

    Digest bindings are intentionally secondary evidence. The public owner guard first
    resolves the entire STATE.json from GitHub and checks its blob SHA, so a caller cannot
    repair a tampered quality object by rewriting the digest inside the same candidate state.
    """
    quality = state.get("quality_evidence", {})
    _require(isinstance(quality, Mapping), "current Financial state requires quality_evidence mapping")
    stage = str(state.get("current_stage"))
    _require(stage in owner_guard.STAGE_INDEX, "current Financial state has an unsupported stage")
    current_index = owner_guard.STAGE_INDEX[stage]

    if current_index >= owner_guard.STAGE_INDEX["RESEARCH_AUDIT"]:
        raw_decision = quality.get("research_decision")
        _parse_decision_envelope(raw_decision if isinstance(raw_decision, Mapping) else None)
        _require_persisted_digest(
            state,
            evidence_key="research_decision",
            binding_key="decision_envelope_sha256",
            admitting_stage="RESEARCH",
            evidence_value=raw_decision,
        )

    if current_index >= owner_guard.STAGE_INDEX["TITLE"]:
        raw_blueprints = quality.get("story_blueprints")
        blueprints_input = raw_blueprints if isinstance(raw_blueprints, list) else None
        _parse_story_blueprints(state, blueprints_input)
        _require_persisted_digest(
            state,
            evidence_key="story_blueprints",
            binding_key="story_blueprints_sha256",
            admitting_stage="EDITORIAL",
            evidence_value=raw_blueprints,
        )

    if current_index >= owner_guard.STAGE_INDEX["DELIVERY"]:
        raw_fitnesses = quality.get("publication_fitnesses")
        fitness_input = raw_fitnesses if isinstance(raw_fitnesses, list) else None
        _parse_publication_fitnesses(state, fitness_input, review_status="PASS")
        _require_persisted_digest(
            state,
            evidence_key="publication_fitnesses",
            binding_key="publication_fitnesses_sha256",
            admitting_stage="EDITORIAL_AUDIT",
            evidence_value=raw_fitnesses,
        )


# Compatibility alias for callers/tests that used the 1.0.1 private name.
_validate_persisted_quality_evidence = _validate_current_quality_evidence


def build_initial_state(**kwargs: Any) -> dict[str, Any]:
    """Create a current quality-governed Financial task.

    The base owner builds the business contract. This layer upgrades the new task to
    the dedicated quality-state schema before it is persisted for the first time.
    """
    state = owner_guard.build_initial_state(**kwargs)
    state["schema_version"] = owner_guard.QUALITY_STATE_SCHEMA_VERSION
    state["writing_kernel_version"] = WRITING_KERNEL_VERSION
    state["quality_evidence"] = {}
    receipt = state["execution_receipts"][-1]
    receipt.setdefault("input_bindings", {})["writing_kernel_version"] = WRITING_KERNEL_VERSION
    receipt["input_bindings"]["quality_admission_path"] = QUALITY_ADMISSION_PATH
    owner_guard._validate_unpersisted_state(state)
    return state


def validate_state(state: Mapping[str, Any]) -> None:
    """Validate current state against owner semantics and the authoritative GitHub blob."""
    owner_guard.validate_state(state)
    _require(
        state.get("schema_version") == owner_guard.QUALITY_STATE_SCHEMA_VERSION,
        "current Financial state must use schema_version=1.3",
    )


def _planned_quality_invalidations(state: Mapping[str, Any], revision_target: str | None) -> list[str]:
    quality = state.get("quality_evidence", {})
    if not isinstance(quality, Mapping):
        return []
    if revision_target == "RESEARCH":
        keys = tuple(quality.keys())
    elif revision_target == "EDITORIAL":
        keys = ("story_blueprints", "publication_fitnesses")
    elif revision_target in {"TITLE", "DRAFT"}:
        keys = ("publication_fitnesses",)
    else:
        keys = ()
    return sorted(key for key in keys if key in quality)


def _prepare_quality_transition(
    state: Mapping[str, Any],
    *,
    decision_envelope: Mapping[str, Any] | None,
    story_blueprints: list[Mapping[str, Any]] | None,
    publication_fitnesses: list[Mapping[str, Any]] | None,
    review_status: str | None,
    revision_target: str | None,
) -> tuple[dict[str, Any], dict[str, str], list[str]]:
    """Parse current quality evidence before one atomic owner transition.

    This function never mutates persisted authority and never creates a receipt. The
    owner guard owns both the state transition and receipt binding in the same call.
    """
    owner_guard._validate_unpersisted_state(state)
    working = deepcopy(dict(state))
    stage = str(state["current_stage"])
    quality = working.setdefault("quality_evidence", {})
    evidence_bindings: dict[str, str] = {}

    if stage == "RESEARCH":
        envelope = _parse_decision_envelope(decision_envelope)
        dumped = envelope.model_dump(mode="json")
        quality["research_decision"] = dumped
        evidence_bindings["decision_envelope_sha256"] = _canonical_digest(dumped)
    else:
        _require(decision_envelope is None, f"decision_envelope is only valid at RESEARCH, not {stage}")

    if stage == "EDITORIAL":
        blueprints = _parse_story_blueprints(state, story_blueprints)
        dumped = [item.model_dump(mode="json") for item in blueprints]
        quality["story_blueprints"] = dumped
        evidence_bindings["story_blueprints_sha256"] = _canonical_digest(dumped)
    else:
        _require(story_blueprints is None, f"story_blueprints are only valid at EDITORIAL, not {stage}")

    if stage == "EDITORIAL_AUDIT" and review_status in {"PASS", "REVISE"}:
        fitnesses = _parse_publication_fitnesses(state, publication_fitnesses, review_status=str(review_status))
        dumped = [item.model_dump(mode="json") for item in fitnesses]
        quality["publication_fitnesses"] = dumped
        evidence_bindings["publication_fitnesses_sha256"] = _canonical_digest(dumped)
    else:
        _require(
            publication_fitnesses is None,
            f"publication_fitnesses are only valid for EDITORIAL_AUDIT PASS/REVISE, not {stage}",
        )

    planned_invalidated = (
        _planned_quality_invalidations(working, str(revision_target))
        if review_status == "REVISE" and revision_target
        else []
    )
    return working, evidence_bindings, planned_invalidated


def advance_state(
    state: Mapping[str, Any],
    *,
    decision_envelope: Mapping[str, Any] | None = None,
    story_blueprints: list[Mapping[str, Any]] | None = None,
    publication_fitnesses: list[Mapping[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Thin current entrypoint over the canonical owner transition.

    There is no sequencing token and no post-hoc receipt mutation. The owner guard
    authenticates GitHub state, parses current quality evidence and binds its digest
    in the same transition.
    """
    return owner_guard.advance_state(
        state,
        decision_envelope=decision_envelope,
        story_blueprints=story_blueprints,
        publication_fitnesses=publication_fitnesses,
        **kwargs,
    )


def attach_material_feedback(state: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
    return owner_guard.attach_material_feedback(state, **kwargs)
