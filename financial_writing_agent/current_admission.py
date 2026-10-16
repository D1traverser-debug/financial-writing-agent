from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

from . import owner_guard
from .cognition_governance import DecisionEnvelope, OperationClass, admission_errors
from .private_research import PRIVATE_RESEARCH_CONTRACT_VERSION, validate_private_research_brief
from .story_quality import AuditStatus, ProductMode, PublicationFitness, StoryBlueprint

WRITING_KERNEL_VERSION = "1.0"
QUALITY_ADMISSION_PATH = "financial_writing_agent.current_admission"


class CurrentAdmissionError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CurrentAdmissionError(message)


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _private_research_required(state: Mapping[str, Any]) -> bool:
    return state.get("private_research_contract_version") == PRIVATE_RESEARCH_CONTRACT_VERSION


def _parse_private_research(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    try:
        return validate_private_research_brief(raw)
    except ValueError as exc:
        raise CurrentAdmissionError(str(exc)) from exc


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


def _validate_persisted_quality_evidence(state: Mapping[str, Any]) -> None:
    quality = state.get("quality_evidence", {})
    _require(isinstance(quality, Mapping), "current Financial state requires quality_evidence mapping")
    stage = str(state.get("current_stage"))
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

        raw_private = quality.get("private_research_brief")
        if _private_research_required(state) or raw_private is not None:
            admitted_private = _parse_private_research(raw_private if isinstance(raw_private, Mapping) else None)
            _require_persisted_digest(
                state,
                evidence_key="private_research_brief",
                binding_key="private_research_brief_sha256",
                admitting_stage="RESEARCH",
                evidence_value=admitted_private,
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


def build_initial_state(**kwargs: Any) -> dict[str, Any]:
    """Create a current Financial task while delegating business identity/state semantics to owner_guard."""
    state = owner_guard.build_initial_state(**kwargs)
    state["writing_kernel_version"] = WRITING_KERNEL_VERSION
    state["private_research_contract_version"] = PRIVATE_RESEARCH_CONTRACT_VERSION
    state["quality_evidence"] = {}
    receipt = state["execution_receipts"][-1]
    receipt.setdefault("input_bindings", {})["writing_kernel_version"] = WRITING_KERNEL_VERSION
    receipt["input_bindings"]["private_research_contract_version"] = PRIVATE_RESEARCH_CONTRACT_VERSION
    receipt["input_bindings"]["quality_admission_path"] = QUALITY_ADMISSION_PATH
    validate_state(state)
    return state


def validate_state(state: Mapping[str, Any]) -> None:
    # The current layer owns quality parsing. Use the base owner-state validator here
    # to avoid the owner's public 1.0 dispatch recursively calling back into this module.
    owner_guard._validate_base_state(state)
    _require(state.get("writing_kernel_version") == WRITING_KERNEL_VERSION, "current Financial state must bind writing_kernel_version=1.0")
    private_version = state.get("private_research_contract_version")
    _require(
        private_version in {None, PRIVATE_RESEARCH_CONTRACT_VERSION},
        f"unsupported private_research_contract_version: {private_version}",
    )
    _validate_persisted_quality_evidence(state)


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


def advance_state(
    state: Mapping[str, Any],
    *,
    decision_envelope: Mapping[str, Any] | None = None,
    private_research_brief: Mapping[str, Any] | None = None,
    story_blueprints: list[Mapping[str, Any]] | None = None,
    publication_fitnesses: list[Mapping[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Current admission wrapper around the one canonical owner state machine.

    Historical states continue to use owner_guard directly. New 1.0 tasks use this entrypoint so
    research/thesis, private research, story design and publication quality cannot be advanced by
    a naked PASS label or an unbound side artifact.
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

        if _private_research_required(state) or private_research_brief is not None:
            private_dumped = _parse_private_research(private_research_brief)
            quality["private_research_brief"] = private_dumped
            evidence_bindings["private_research_brief_sha256"] = _canonical_digest(private_dumped)

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

    revision_target = kwargs.get("revision_target")
    planned_invalidated = (
        _planned_quality_invalidations(working, str(revision_target))
        if review_status == "REVISE" and revision_target
        else []
    )

    # The owner guard now enforces 1.0 quality for every public lower-level path. During
    # this one internal sequencing window, the new receipt does not yet carry its quality
    # digest, so defer only that owner-level callback. Full current validation runs below
    # after the receipt is bound; the token is process-local and not a persisted credential.
    after = owner_guard.advance_state(
        working,
        _current_admission_token=owner_guard._CURRENT_ADMISSION_TOKEN,
        **kwargs,
    )

    if planned_invalidated:
        missing = [key for key in planned_invalidated if key in after.get("quality_evidence", {})]
        _require(not missing, f"owner revision failed to invalidate quality evidence: {missing}")
        evidence_bindings["invalidated_quality_evidence"] = ",".join(planned_invalidated)

    receipt = after["execution_receipts"][-1]
    receipt.setdefault("input_bindings", {})["writing_kernel_version"] = WRITING_KERNEL_VERSION
    if _private_research_required(after):
        receipt["input_bindings"]["private_research_contract_version"] = PRIVATE_RESEARCH_CONTRACT_VERSION
    receipt["input_bindings"]["quality_admission_path"] = QUALITY_ADMISSION_PATH
    receipt["input_bindings"].update(evidence_bindings)
    validate_state(after)
    return after


def attach_material_feedback(state: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
    validate_state(state)
    # Feedback does not alter quality objects, so the owner guard can and should perform
    # its normal full 1.0 validation on both sides of this mutation.
    after = owner_guard.attach_material_feedback(state, **kwargs)
    receipt = after["execution_receipts"][-1]
    receipt.setdefault("input_bindings", {})["writing_kernel_version"] = WRITING_KERNEL_VERSION
    if _private_research_required(after):
        receipt["input_bindings"]["private_research_contract_version"] = PRIVATE_RESEARCH_CONTRACT_VERSION
    receipt["input_bindings"]["quality_admission_path"] = QUALITY_ADMISSION_PATH
    validate_state(after)
    return after
