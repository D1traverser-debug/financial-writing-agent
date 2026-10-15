from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

from . import owner_guard
from .cognition_governance import DecisionEnvelope, OperationClass, admission_errors
from .story_quality import AuditStatus, ProductMode, PublicationFitness, StoryBlueprint

WRITING_KERNEL_VERSION = "1.0"


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
    _require(set(modes) == expected, f"story blueprint modes mismatch: expected={sorted(x.value for x in expected)}, actual={sorted(x.value for x in set(modes))}")
    return parsed


def _parse_publication_fitnesses(
    state: Mapping[str, Any], raw: list[Mapping[str, Any]] | None, *, review_status: str
) -> list[PublicationFitness]:
    _require(isinstance(raw, list) and raw, "current EDITORIAL_AUDIT requires publication_fitnesses")
    parsed = [PublicationFitness.model_validate(item) for item in raw]
    modes = [item.product_mode for item in parsed]
    _require(len(modes) == len(set(modes)), "publication_fitnesses must contain at most one result per product mode")
    expected = _expected_longform_modes(state)
    _require(set(modes) == expected, f"publication fitness modes mismatch: expected={sorted(x.value for x in expected)}, actual={sorted(x.value for x in set(modes))}")

    all_pass = all(item.final_status == AuditStatus.PASS for item in parsed)
    if review_status == "PASS":
        _require(all_pass, "EDITORIAL_AUDIT cannot PASS while any publication fitness gate requires revision")
    elif review_status == "REVISE":
        _require(not all_pass, "EDITORIAL_AUDIT REVISE requires at least one publication fitness REVISE result")
    return parsed


def _parse_decision_envelope(raw: Mapping[str, Any] | None) -> DecisionEnvelope:
    _require(isinstance(raw, Mapping), "current RESEARCH transition requires decision_envelope")
    envelope = DecisionEnvelope.model_validate(raw)
    _require(envelope.operation_class == OperationClass.MATERIAL_JUDGMENT, "RESEARCH decision envelope must represent a MATERIAL_JUDGMENT")
    semantic_errors = admission_errors(envelope)
    _require(not semantic_errors, f"decision envelope admission failed: {semantic_errors}")
    return envelope


def build_initial_state(**kwargs: Any) -> dict[str, Any]:
    """Create a current Financial task while delegating business identity/state semantics to owner_guard."""
    state = owner_guard.build_initial_state(**kwargs)
    state["writing_kernel_version"] = WRITING_KERNEL_VERSION
    state["quality_evidence"] = {}
    receipt = state["execution_receipts"][-1]
    receipt.setdefault("input_bindings", {})["writing_kernel_version"] = WRITING_KERNEL_VERSION
    receipt["input_bindings"]["quality_admission_path"] = "financial_writing_agent.current_admission"
    validate_state(state)
    return state


def validate_state(state: Mapping[str, Any]) -> None:
    owner_guard.validate_state(state)
    _require(state.get("writing_kernel_version") == WRITING_KERNEL_VERSION, "current Financial state must bind writing_kernel_version=1.0")
    _require(isinstance(state.get("quality_evidence"), Mapping), "current Financial state requires quality_evidence mapping")


def _invalidate_quality_evidence(state: dict[str, Any], revision_target: str | None) -> list[str]:
    invalidated: list[str] = []
    quality = state.setdefault("quality_evidence", {})
    if revision_target == "RESEARCH":
        keys = tuple(quality.keys())
    elif revision_target == "EDITORIAL":
        keys = ("story_blueprints", "publication_fitnesses")
    elif revision_target in {"TITLE", "DRAFT"}:
        keys = ("publication_fitnesses",)
    else:
        keys = ()
    for key in keys:
        if key in quality:
            quality.pop(key, None)
            invalidated.append(key)
    return invalidated


def advance_state(
    state: Mapping[str, Any],
    *,
    decision_envelope: Mapping[str, Any] | None = None,
    story_blueprints: list[Mapping[str, Any]] | None = None,
    publication_fitnesses: list[Mapping[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Current admission wrapper around the one canonical owner state machine.

    Historical states continue to use owner_guard directly. New 1.0 tasks use this entrypoint so
    research/thesis, story design and publication quality cannot be advanced by a naked PASS label.
    """
    validate_state(state)
    working = deepcopy(dict(state))
    stage = str(state["current_stage"])
    quality = working.setdefault("quality_evidence", {})
    evidence_bindings: dict[str, str] = {}

    if stage == "RESEARCH":
        envelope = _parse_decision_envelope(decision_envelope)
        dumped = envelope.model_dump(mode="json")
        quality["research_decision"] = dumped
        evidence_bindings["decision_envelope_sha256"] = _canonical_digest(dumped)

    if stage == "EDITORIAL":
        blueprints = _parse_story_blueprints(state, story_blueprints)
        dumped = [item.model_dump(mode="json") for item in blueprints]
        quality["story_blueprints"] = dumped
        evidence_bindings["story_blueprints_sha256"] = _canonical_digest(dumped)

    review_status = kwargs.get("review_status")
    if stage == "EDITORIAL_AUDIT" and review_status in {"PASS", "REVISE"}:
        fitnesses = _parse_publication_fitnesses(state, publication_fitnesses, review_status=str(review_status))
        dumped = [item.model_dump(mode="json") for item in fitnesses]
        quality["publication_fitnesses"] = dumped
        evidence_bindings["publication_fitnesses_sha256"] = _canonical_digest(dumped)

    after = owner_guard.advance_state(working, **kwargs)

    if stage == "EDITORIAL_AUDIT" and review_status == "REVISE":
        invalidated = _invalidate_quality_evidence(after, str(kwargs.get("revision_target")))
        if invalidated:
            evidence_bindings["invalidated_quality_evidence"] = ",".join(sorted(invalidated))

    receipt = after["execution_receipts"][-1]
    receipt.setdefault("input_bindings", {})["writing_kernel_version"] = WRITING_KERNEL_VERSION
    receipt["input_bindings"]["quality_admission_path"] = "financial_writing_agent.current_admission"
    receipt["input_bindings"].update(evidence_bindings)
    validate_state(after)
    return after


def attach_material_feedback(state: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
    validate_state(state)
    after = owner_guard.attach_material_feedback(state, **kwargs)
    validate_state(after)
    receipt = after["execution_receipts"][-1]
    receipt.setdefault("input_bindings", {})["writing_kernel_version"] = WRITING_KERNEL_VERSION
    receipt["input_bindings"]["quality_admission_path"] = "financial_writing_agent.current_admission"
    return after
