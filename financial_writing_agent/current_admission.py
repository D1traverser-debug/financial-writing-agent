from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

from . import owner_guard
from .cognition_governance import DecisionEnvelope, OperationClass, admission_errors
from .path_identity import require_article_path
from .private_research import (
    PRIVATE_RESEARCH_CONTRACT_VERSION,
    SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS,
    validate_private_research_brief,
)
from .story_quality import AuditStatus, ProductMode, PublicationFitness, StoryBlueprint
from .task_requirements import (
    REQUIREMENT_AUTHORITY_PATH,
    REQUIREMENT_CONTRACT_VERSION,
    RequirementError,
    active_requirements_for_scope,
    active_task_scopes,
    apply_requirement_changes,
    authority_digest,
    requirement_applies_to_scopes,
    requirement_scopes_for_stage,
    validate_requirement_applicability,
    empty_requirement_authority,
    validate_requirement_authority,
)
from .task_intake import (
    TASK_INTAKE_CONTRACT_VERSION,
    TaskIntakeError,
    build_task_intake_review_challenge,
    canonical_sha256 as task_intake_canonical_sha256,
    validate_task_intake_manifest,
    verify_task_intake_review,
)
from .goal_outcome import (
    GoalOutcomeError,
    verify_goal_outcome_review,
    verify_persisted_goal_outcome_review,
)

WRITING_KERNEL_VERSION = "1.0"
QUALITY_ADMISSION_PATH = "financial_writing_agent.current_admission"
REQUIREMENT_CAPABILITY_ID = "github_chat_requirement_governance"
REQUIREMENT_SATISFACTION_VERSION = "1.0"
PORTFOLIO_EXECUTION_CONTRACT_VERSION = "1.0"
TASK_INTAKE_STATE_FIELD = "task_intake_contract_version"
GOAL_OUTCOME_REVIEW_HISTORY_FIELD = "goal_outcome_review_history"
PORTFOLIO_COORDINATED_STAGES = frozenset({
    "INTAKE", "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL",
    "TITLE", "DRAFT", "EDITORIAL_AUDIT",
})


class CurrentAdmissionError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CurrentAdmissionError(message)


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _private_research_required(state: Mapping[str, Any]) -> bool:
    return state.get("private_research_contract_version") in SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS


def _requirement_authority_enabled(state: Mapping[str, Any]) -> bool:
    return state.get("task_requirement_contract_version") == REQUIREMENT_CONTRACT_VERSION


def _parse_private_research(
    raw: Mapping[str, Any] | None,
    *,
    expected_contract_version: str | None = None,
) -> dict[str, Any]:
    try:
        return validate_private_research_brief(raw, expected_contract_version=expected_contract_version)
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
    if set(modes) == {ProductMode.FINANCE_DEEP, ProductMode.FINANCE_BROAD}:
        deep = next(item for item in parsed if item.product_mode == ProductMode.FINANCE_DEEP)
        broad = next(item for item in parsed if item.product_mode == ProductMode.FINANCE_BROAD)
        # Exact or cosmetic Deep->Broad copying is not independent acquisition
        # architecture. This is a clone detector, NOT an editorial-quality score.
        dimensions = (
            lambda item: (
                item.reader_job, item.reader_starting_state, item.article_promise,
                item.central_question, item.narrative_engine.value,
                item.opening.concrete_anchor, item.opening.reader_information_gap,
                tuple(section.working_heading for section in item.sections),
                item.ending_payoff,
            )
        )
        different = sum(
            left != right
            for left, right in zip(dimensions(deep), dimensions(broad))
        )
        _require(
            different >= 3,
            "FINANCE_BROAD_BLUEPRINT_NOT_INDEPENDENT_OF_DEEP:"
            "separate reader, promise, opening, narrative path and payoff required",
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
    actual = set(modes)
    if review_status == "PASS":
        _require(
            actual == expected,
            f"publication fitness modes mismatch: expected={sorted(x.value for x in expected)}, actual={sorted(x.value for x in actual)}",
        )
    else:
        _require(
            actual.issubset(expected),
            f"publication fitness modes mismatch: expected subset of={sorted(x.value for x in expected)}, actual={sorted(x.value for x in actual)}",
        )

    all_pass = all(item.final_status == AuditStatus.PASS for item in parsed)
    if review_status == "PASS":
        _require(all_pass, "EDITORIAL_AUDIT cannot PASS while any publication fitness gate requires revision")
    elif review_status == "REVISE":
        _require(
            any(item.final_status == AuditStatus.REVISE for item in parsed),
            "EDITORIAL_AUDIT REVISE requires at least one publication fitness REVISE result",
        )
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


def _bind_requirement_receipt(state: dict[str, Any]) -> None:
    _require(_requirement_authority_enabled(state), "current Financial state requires Task Requirement Authority v1.0")
    authority = validate_requirement_authority(state.get("task_requirement_authority"))
    digest = authority_digest(authority)
    state["task_requirement_digest"] = digest
    receipt = state["execution_receipts"][-1]
    bindings = receipt.setdefault("input_bindings", {})
    bindings["task_requirement_contract_version"] = REQUIREMENT_CONTRACT_VERSION
    bindings["task_requirement_revision"] = authority["revision"]
    bindings["task_requirement_digest"] = digest
    bindings["task_requirement_authority_path"] = REQUIREMENT_AUTHORITY_PATH


def bind_current_governance_receipt(state: dict[str, Any]) -> None:
    """Bind one already-appended current-task mutation receipt to all current governance owners.

    Lifecycle/proactive helpers may own their domain-specific mutation semantics, but no
    current writing-kernel mutation may leave this aggregate without these bindings.
    """
    _require(state.get("writing_kernel_version") == WRITING_KERNEL_VERSION, "current governance binding requires writing_kernel_version=1.0")
    receipts = state.get("execution_receipts", [])
    _require(isinstance(receipts, list) and receipts, "current governance binding requires an execution receipt")
    receipt = receipts[-1]
    bindings = receipt.setdefault("input_bindings", {})
    bindings["writing_kernel_version"] = WRITING_KERNEL_VERSION
    private_version = state.get("private_research_contract_version")
    if private_version in SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS:
        bindings["private_research_contract_version"] = str(private_version)
    bindings["quality_admission_path"] = QUALITY_ADMISSION_PATH
    portfolio_version = state.get("portfolio_execution_contract_version")
    if portfolio_version is not None:
        _require(
            portfolio_version == PORTFOLIO_EXECUTION_CONTRACT_VERSION,
            "unsupported portfolio_execution_contract_version",
        )
        bindings["portfolio_execution_contract_version"] = portfolio_version
    _bind_requirement_receipt(state)


def _active_requirement_items(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    authority = validate_requirement_authority(state.get("task_requirement_authority"))
    return list(authority["active_requirements"])


def _requirements_due_at_stage(state: Mapping[str, Any], stage: str) -> list[dict[str, Any]]:
    try:
        stage_scopes = requirement_scopes_for_stage(stage, state.get("required_outputs", []))
    except RequirementError as exc:
        raise CurrentAdmissionError(str(exc)) from exc
    return sorted(
        [
            item for item in _active_requirement_items(state)
            if item.get("affects_from_stage") == stage
            and requirement_applies_to_scopes(item, stage_scopes)
        ],
        key=lambda item: str(item["requirement_id"]),
    )


def _normalize_requirement_satisfaction(
    state: Mapping[str, Any],
    stage: str,
    raw: list[Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    due = _requirements_due_at_stage(state, stage)
    due_by_id = {str(item["requirement_id"]): item for item in due}
    supplied = list(raw or [])
    if not due:
        _require(not supplied, f"{stage} has no newly due task requirements; requirement_satisfaction must be empty")
        return []
    _require(supplied, f"{stage} transition requires task requirement satisfaction evidence for {sorted(due_by_id)}")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in supplied:
        _require(isinstance(entry, Mapping), "requirement_satisfaction entry must be an object")
        requirement_id = str(entry.get("requirement_id", "")).strip()
        _require(requirement_id in due_by_id, f"unexpected requirement_satisfaction requirement_id: {requirement_id or 'MISSING'}")
        _require(requirement_id not in seen, f"duplicate requirement_satisfaction requirement_id: {requirement_id}")
        _require(entry.get("result") == "SATISFIED", f"requirement {requirement_id} must be SATISFIED before leaving {stage}")
        evidence_refs = entry.get("evidence_refs")
        _require(
            isinstance(evidence_refs, list)
            and bool(evidence_refs)
            and all(isinstance(ref, str) and bool(ref.strip()) for ref in evidence_refs),
            f"requirement {requirement_id} requires evidence_refs as nonempty strings",
        )
        normalized_refs = [ref.strip() for ref in evidence_refs]
        _require(
            len(normalized_refs) == len(set(normalized_refs)),
            f"requirement {requirement_id} evidence_refs must be unique after normalization",
        )
        requirement = due_by_id[requirement_id]
        normalized.append(
            {
                "requirement_id": requirement_id,
                "requirement_sha256": _canonical_digest(requirement),
                "result": "SATISFIED",
                "evidence_refs": normalized_refs,
                "notes": str(entry.get("notes", "")).strip(),
            }
        )
        seen.add(requirement_id)
    _require(seen == set(due_by_id), f"requirement_satisfaction mismatch: required={sorted(due_by_id)}, actual={sorted(seen)}")
    return sorted(normalized, key=lambda item: item["requirement_id"])


def _validate_requirement_satisfaction_history(state: Mapping[str, Any]) -> None:
    receipts = state.get("execution_receipts", [])
    _require(isinstance(receipts, list), "task requirement satisfaction requires execution receipts")
    stage = str(state.get("current_stage"))
    current_index = owner_guard.STAGE_INDEX[stage]
    due_requirements = [
        requirement
        for affected_stage in ("RESEARCH", "EDITORIAL", "TITLE", "DRAFT", "DELIVERY")
        for requirement in _requirements_due_at_stage(state, affected_stage)
    ]
    for requirement in due_requirements:
        affected_stage = str(requirement["affects_from_stage"])
        # A requirement becomes due when the task tries to leave its affected stage.
        # If the task is still at that stage, the current stage may legitimately be unsatisfied.
        if current_index <= owner_guard.STAGE_INDEX[affected_stage]:
            continue
        expected_digest = _canonical_digest(requirement)
        found = False
        for receipt in receipts:
            if not isinstance(receipt, Mapping) or receipt.get("stage") != affected_stage:
                continue
            bindings = receipt.get("input_bindings", {})
            if not isinstance(bindings, Mapping):
                continue
            entries = bindings.get("task_requirement_satisfaction", [])
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, Mapping):
                    continue
                if entry.get("requirement_id") == requirement["requirement_id"] and entry.get("requirement_sha256") == expected_digest and entry.get("result") == "SATISFIED":
                    refs = entry.get("evidence_refs")
                    if isinstance(refs, list) and refs:
                        found = True
                        break
            if found:
                break
        _require(found, f"active requirement {requirement['requirement_id']} has no admitted satisfaction evidence at {affected_stage}")


def _validate_requirement_binding(state: Mapping[str, Any]) -> None:
    _require(
        state.get("task_requirement_contract_version") == REQUIREMENT_CONTRACT_VERSION,
        "current Financial state requires task_requirement_contract_version=1.0; pre-contract tasks must use migrate_task_requirement_authority",
    )
    try:
        authority = validate_requirement_authority(state.get("task_requirement_authority"))
        digest = authority_digest(authority)
    except RequirementError as exc:
        raise CurrentAdmissionError(str(exc)) from exc
    _require(state.get("task_requirement_digest") == digest, "task requirement authority digest mismatch")
    receipts = state.get("execution_receipts", [])
    _require(isinstance(receipts, list) and receipts, "task requirement authority requires execution receipts")
    latest = receipts[-1]
    bindings = latest.get("input_bindings", {}) if isinstance(latest, Mapping) else {}
    _require(bindings.get("task_requirement_contract_version") == REQUIREMENT_CONTRACT_VERSION, "latest state mutation did not bind task requirement contract")
    _require(bindings.get("task_requirement_authority_path") == REQUIREMENT_AUTHORITY_PATH, "latest state mutation used a non-canonical task requirement authority")
    _require(bindings.get("task_requirement_revision") == authority["revision"], "latest state mutation task requirement revision mismatch")
    _require(bindings.get("task_requirement_digest") == digest, "latest state mutation task requirement digest mismatch")
    _validate_requirement_satisfaction_history(state)


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
            expected_version = state.get("private_research_contract_version")
            admitted_private = _parse_private_research(
                raw_private if isinstance(raw_private, Mapping) else None,
                expected_contract_version=str(expected_version) if expected_version is not None else None,
            )
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


def build_initial_state(*, goal_first: bool = False, **kwargs: Any) -> dict[str, Any]:
    """Create a current Financial task; production-created tasks use goal-first intake."""
    state = owner_guard.build_initial_state(
        _current_admission_token=owner_guard._CURRENT_ADMISSION_TOKEN,
        **kwargs,
    )
    state["writing_kernel_version"] = WRITING_KERNEL_VERSION
    state["private_research_contract_version"] = PRIVATE_RESEARCH_CONTRACT_VERSION
    state["quality_evidence"] = {}
    state["task_requirement_contract_version"] = REQUIREMENT_CONTRACT_VERSION
    state["task_requirement_authority"] = empty_requirement_authority()
    state["task_requirement_digest"] = authority_digest(state["task_requirement_authority"])
    state["portfolio_execution_contract_version"] = PORTFOLIO_EXECUTION_CONTRACT_VERSION
    if goal_first:
        state[TASK_INTAKE_STATE_FIELD] = TASK_INTAKE_CONTRACT_VERSION
        state["execution_receipts"][0]["input_bindings"][TASK_INTAKE_STATE_FIELD] = (
            TASK_INTAKE_CONTRACT_VERSION
        )
    bind_current_governance_receipt(state)
    validate_state(state)
    return state


def _validate_pre_requirement_migration_state(state: Mapping[str, Any]) -> None:
    owner_guard._validate_base_state(state)
    _require(state.get("writing_kernel_version") == WRITING_KERNEL_VERSION, "requirement migration only applies to current writing-kernel tasks")
    _require(not _requirement_authority_enabled(state), "task already has Task Requirement Authority v1.0")
    private_version = state.get("private_research_contract_version")
    _require(
        private_version is None or private_version in SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS,
        f"unsupported private_research_contract_version: {private_version}",
    )
    _validate_persisted_quality_evidence(state)


def portfolio_context_required_for_stage(state: Mapping[str, Any]) -> bool:
    """New/current tasks must advance portfolio-owned stages through the coordinator."""
    return (
        state.get("portfolio_execution_contract_version")
        == PORTFOLIO_EXECUTION_CONTRACT_VERSION
        and state.get("current_stage") in PORTFOLIO_COORDINATED_STAGES
    )


def _validate_portfolio_execution_binding(state: Mapping[str, Any]) -> None:
    version = state.get("portfolio_execution_contract_version")
    receipts = state.get("execution_receipts", [])
    latest_bindings = (
        receipts[-1].get("input_bindings", {})
        if isinstance(receipts, list) and receipts and isinstance(receipts[-1], Mapping)
        else {}
    )
    bound_version = (
        latest_bindings.get("portfolio_execution_contract_version")
        if isinstance(latest_bindings, Mapping) else None
    )
    if version is None:
        _require(
            bound_version is None,
            "portfolio execution contract marker cannot be removed from an admitted task",
        )
        return
    _require(
        version == PORTFOLIO_EXECUTION_CONTRACT_VERSION
        and bound_version == version,
        "portfolio execution contract must be bound by the latest owner receipt",
    )


def _validate_task_intake_state(state: Mapping[str, Any]) -> None:
    marker = state.get(TASK_INTAKE_STATE_FIELD)
    fields = (
        "task_intake_manifest",
        "task_intake_manifest_sha256",
        "task_intake_review_attestation",
    )
    receipts = state.get("execution_receipts", [])
    initial_bindings = (
        receipts[0].get("input_bindings", {})
        if isinstance(receipts, list) and receipts and isinstance(receipts[0], Mapping)
        else {}
    )
    if marker is None:
        _require(
            initial_bindings.get(TASK_INTAKE_STATE_FIELD) is None,
            "TASK_INTAKE_CONTRACT_MARKER_REMOVED_FROM_INITIAL_RECEIPT",
        )
        _require(
            not any(name in state for name in fields),
            "task intake evidence cannot exist without the goal-first intake contract",
        )
        return
    _require(
        marker == TASK_INTAKE_CONTRACT_VERSION
        and initial_bindings.get(TASK_INTAKE_STATE_FIELD) == TASK_INTAKE_CONTRACT_VERSION,
        "unsupported or unbound task_intake_contract_version",
    )
    authority = validate_requirement_authority(state.get("task_requirement_authority"))
    if state.get("current_stage") == "INTAKE":
        _require(
            authority["revision"] == 0 and not authority["active_requirements"],
            "goal-first INTAKE must not pre-populate task requirement authority",
        )
        _require(
            not any(name in state for name in fields),
            "goal-first INTAKE evidence is admitted only by the INTAKE transition",
        )
        return
    _require(
        all(name in state for name in fields),
        "goal-first task cannot leave INTAKE without its admitted manifest and independent review",
    )
    try:
        normalized = validate_task_intake_manifest(
            state.get("task_intake_manifest"),
            task_id=str(state["task_id"]),
            prompt=str(state["prompt"]),
            required_outputs=list(state.get("required_outputs", [])),
        )
    except TaskIntakeError as exc:
        raise CurrentAdmissionError(str(exc)) from exc
    _require(
        normalized == state.get("task_intake_manifest"),
        "TASK_INTAKE_MANIFEST_NOT_CANONICALLY_NORMALIZED",
    )
    manifest_sha = task_intake_canonical_sha256(normalized)
    _require(
        state.get("task_intake_manifest_sha256") == manifest_sha,
        "TASK_INTAKE_MANIFEST_DIGEST_MISMATCH",
    )
    intake_receipts = [
        receipt for receipt in receipts
        if isinstance(receipt, Mapping)
        and receipt.get("stage") == "INTAKE"
        and isinstance(receipt.get("input_bindings"), Mapping)
        and receipt["input_bindings"].get(TASK_INTAKE_STATE_FIELD) == TASK_INTAKE_CONTRACT_VERSION
    ]
    _require(
        len(intake_receipts) == 1,
        "TASK_INTAKE_ADMISSION_RECEIPT_MISSING_OR_DUPLICATED",
    )
    intake_bindings = intake_receipts[0]["input_bindings"]
    _require(
        intake_bindings.get("task_intake_manifest_sha256") == manifest_sha
        and intake_bindings.get("task_intake_review_attestation_sha256")
        == _canonical_digest(state.get("task_intake_review_attestation"))
        and intake_bindings.get("initial_requirement_revision") == 1,
        "TASK_INTAKE_ADMISSION_RECEIPT_BINDING_MISMATCH",
    )
    initial_requirements = [
        item["requirement"]
        for item in normalized["requirements"]
    ]
    initial_history = [
        item.get("current")
        for item in authority["history"]
        if item.get("revision") == 1 and item.get("action") == "ADD"
    ]
    _require(
        sorted(initial_requirements, key=lambda item: item["requirement_id"])
        == sorted(initial_history, key=lambda item: item["requirement_id"]),
        "TASK_INTAKE_INITIAL_REQUIREMENT_AUTHORITY_MISMATCH",
    )
    challenge = build_task_intake_review_challenge(
        task_id=str(state["task_id"]),
        prompt=str(state["prompt"]),
        manifest=normalized,
        required_outputs=list(state.get("required_outputs", [])),
    )
    try:
        verify_task_intake_review(
            state.get("task_intake_review_attestation"),
            challenge=challenge,
            historical=True,
        )
    except TaskIntakeError as exc:
        raise CurrentAdmissionError(str(exc)) from exc


def _validate_goal_outcome_state(state: Mapping[str, Any]) -> None:
    marker = state.get(TASK_INTAKE_STATE_FIELD)
    history = state.get(GOAL_OUTCOME_REVIEW_HISTORY_FIELD, [])
    _require(isinstance(history, list), "goal outcome review history must be a list")
    review_receipts = [
        receipt for receipt in state.get("execution_receipts", [])
        if isinstance(receipt, Mapping)
        and receipt.get("stage") == "FINAL_AUDIT"
        and isinstance(receipt.get("input_bindings"), Mapping)
        and receipt["input_bindings"].get("goal_outcome_review_attestation_sha256")
    ]
    _require(
        len(review_receipts) == len(history),
        "GOAL_OUTCOME_REVIEW_HISTORY_RECEIPT_COUNT_MISMATCH",
    )
    receipts_by_digest = {
        receipt["input_bindings"]["goal_outcome_review_attestation_sha256"]: receipt
        for receipt in review_receipts
    }
    for entry in history:
        _require(isinstance(entry, Mapping), "goal outcome review history entry must be an object")
        attestation = entry.get("attestation")
        _require(isinstance(attestation, Mapping), "goal outcome review history attestation missing")
        digest = _canonical_digest(attestation)
        _require(
            entry.get("attestation_sha256") == digest,
            "GOAL_OUTCOME_REVIEW_HISTORY_DIGEST_MISMATCH",
        )
        receipt = receipts_by_digest.get(digest)
        _require(isinstance(receipt, Mapping), "GOAL_OUTCOME_REVIEW_HISTORY_RECEIPT_MISSING")
        bindings = receipt["input_bindings"]
        _require(
            bindings.get("goal_outcome_review_decision") == entry.get("decision")
            == attestation.get("decision")
            and bindings.get("goal_outcome_requirement_results_sha256")
            == attestation.get("requirement_results_sha256"),
            "GOAL_OUTCOME_REVIEW_HISTORY_RECEIPT_BINDING_MISMATCH",
        )
        try:
            verified = verify_persisted_goal_outcome_review(
                attestation, require_pass=False,
            )
        except GoalOutcomeError as exc:
            raise CurrentAdmissionError(str(exc)) from exc
        _require(
            entry.get("decision") == verified.get("decision"),
            "GOAL_OUTCOME_REVIEW_HISTORY_DECISION_MISMATCH",
        )
    active = state.get("goal_outcome_review")
    if marker != TASK_INTAKE_CONTRACT_VERSION:
        _require(
            active is None and not history,
            "goal outcome review evidence requires goal-first intake contract",
        )
        return
    if state.get("status") == owner_guard.TERMINAL_STATUS:
        _require(isinstance(active, Mapping), "GOAL_OUTCOME_TERMINAL_STATE_REQUIRES_INDEPENDENT_PASS")
        _require(
            bool(history)
            and history[-1].get("decision") == "PASS"
            and history[-1].get("attestation") == active,
            "GOAL_OUTCOME_ACTIVE_PASS_MUST_BE_LATEST_ADMITTED_REVIEW",
        )
        try:
            verified = verify_persisted_goal_outcome_review(active, state=state)
        except GoalOutcomeError as exc:
            raise CurrentAdmissionError(str(exc)) from exc
        _require(
            verified.get("decision") == "PASS",
            "GOAL_OUTCOME_TERMINAL_STATE_REQUIRES_INDEPENDENT_PASS",
        )
        _require(
            verified.get("requirement_results_sha256") == _canonical_digest(
                verified.get("requirement_results", [])
            ),
            "GOAL_OUTCOME_TERMINAL_REQUIREMENT_RESULTS_DIGEST_MISMATCH",
        )
    else:
        _require(
            active is None,
            "GOAL_OUTCOME_ACTIVE_PASS_CANNOT_SURVIVE_NONTERMINAL_STATE",
        )


def validate_state(state: Mapping[str, Any]) -> None:
    owner_guard._validate_base_state(state)
    _require(state.get("writing_kernel_version") == WRITING_KERNEL_VERSION, "current Financial state must bind writing_kernel_version=1.0")
    private_version = state.get("private_research_contract_version")
    _require(
        private_version is None or private_version in SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS,
        f"unsupported private_research_contract_version: {private_version}",
    )
    _validate_persisted_quality_evidence(state)
    _validate_requirement_binding(state)
    _validate_portfolio_execution_binding(state)
    _validate_task_intake_state(state)
    _validate_goal_outcome_state(state)


def requirement_context_for_scope(state: Mapping[str, Any], scope: str) -> dict[str, Any]:
    """Return the exact active task requirements a stage/product must consume."""
    validate_state(state)
    try:
        active_scopes = active_task_scopes(state.get("required_outputs", []))
    except RequirementError as exc:
        raise CurrentAdmissionError(str(exc)) from exc
    _require(scope in active_scopes, f"task requirement scope is not active for requested outputs: {scope}")
    authority = validate_requirement_authority(state.get("task_requirement_authority"))
    return {
        "contract_version": REQUIREMENT_CONTRACT_VERSION,
        "revision": authority["revision"],
        "digest": state["task_requirement_digest"],
        "requirements": active_requirements_for_scope(authority, scope),
    }


def _planned_quality_invalidations(state: Mapping[str, Any], revision_target: str | None) -> list[str]:
    quality = state.get("quality_evidence", {})
    if not isinstance(quality, Mapping):
        return []
    if revision_target in {"INTAKE", "RESEARCH"}:
        keys = tuple(quality.keys())
    elif revision_target == "EDITORIAL":
        keys = ("story_blueprints", "publication_fitnesses")
    elif revision_target in {"TITLE", "DRAFT"}:
        keys = ("publication_fitnesses",)
    else:
        keys = ()
    return sorted(key for key in keys if key in quality)


def _archive_invalidated_quality(state: dict[str, Any], *, reason: str, earliest_stage: str) -> None:
    quality = state.get("quality_evidence")
    if not isinstance(quality, Mapping) or not quality:
        return
    state.setdefault("quality_evidence_history", []).append(
        {
            "archived_at": owner_guard._utc_now(),
            "reason": reason,
            "invalidated_from_stage": earliest_stage,
            "quality_evidence": deepcopy(dict(quality)),
        }
    )


def migrate_task_requirement_authority(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    evidence_ref: str,
    requirements: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Migrate a pre-P10 current task without rewriting its historical receipts.

    Material supplied requirements are admitted in one new migration transaction and
    invalidate from their earliest affected stage. Historical receipts/artifacts remain
    provenance; the migrated current state must replay under the new authority.
    """
    _validate_pre_requirement_migration_state(state)
    _require(bool(str(previous_state_blob_sha).strip()), "previous_state_blob_sha is required")
    _require(bool(str(executor_identity).strip()), "executor_identity is required")
    _require(bool(str(evidence_ref).strip()), "evidence_ref is required")
    working = deepcopy(dict(state))
    for item in requirements or []:
        try:
            validate_requirement_applicability(item, working.get("required_outputs", []))
        except RequirementError as exc:
            raise CurrentAdmissionError(str(exc)) from exc
    authority = empty_requirement_authority()
    changed_stages: list[str] = []
    if requirements:
        try:
            authority, changed_stages = apply_requirement_changes(
                authority,
                upserts=requirements,
                retire_ids=None,
                evidence_ref=evidence_ref,
            )
        except RequirementError as exc:
            raise CurrentAdmissionError(str(exc)) from exc

    working["task_requirement_contract_version"] = REQUIREMENT_CONTRACT_VERSION
    working["task_requirement_authority"] = authority
    working["task_requirement_digest"] = authority_digest(authority)
    before_stage = str(working["current_stage"])
    invalidated: list[str] = []
    earliest_stage: str | None = None
    if changed_stages:
        earliest_stage = min(changed_stages, key=lambda item: owner_guard.STAGE_INDEX[item])
        if owner_guard.STAGE_INDEX[before_stage] >= owner_guard.STAGE_INDEX[earliest_stage]:
            _archive_invalidated_quality(working, reason="TASK_REQUIREMENT_AUTHORITY_MIGRATION", earliest_stage=earliest_stage)
            invalidated = owner_guard._invalidate_from(working, earliest_stage)
            working["status"] = "IN_PROGRESS"
            working["current_stage"] = earliest_stage
            working["next_action"] = f"replay {earliest_stage} under migrated task requirement authority revision {authority['revision']}"

    receipt = owner_guard._new_receipt(
        task_id=str(working["task_id"]),
        stage=before_stage,
        capability_id=REQUIREMENT_CAPABILITY_ID,
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind="REQUIREMENT_AUTHORITY_MIGRATION",
        subject_bindings={
            "task_id": working["task_id"],
            "from_stage": before_stage,
            "to_stage": working["current_stage"],
            "requirement_revision": authority["revision"],
        },
        input_bindings={
            "evidence_ref": evidence_ref,
            "affected_from_stage": earliest_stage,
            "invalidated_stage_refs": invalidated,
            "migration_from_missing_requirement_authority": True,
        },
        output_refs=[f"workspaces/articles/{working['task_id']}/STATE.json"],
    )
    working["execution_receipts"] = list(state["execution_receipts"]) + [receipt]
    working["updated_at"] = owner_guard._utc_now()
    bind_current_governance_receipt(working)
    validate_state(working)
    return working


def apply_task_requirement_change(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    evidence_ref: str,
    upserts: list[Mapping[str, Any]] | None = None,
    retire_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Persist task-scoped requirement changes and invalidate only affected downstream work."""
    validate_state(state)
    _require(bool(str(previous_state_blob_sha).strip()), "previous_state_blob_sha is required")
    _require(bool(str(executor_identity).strip()), "executor_identity is required")
    working = deepcopy(dict(state))
    for item in upserts or []:
        try:
            validate_requirement_applicability(item, working.get("required_outputs", []))
        except RequirementError as exc:
            raise CurrentAdmissionError(str(exc)) from exc

    try:
        authority, changed_stages = apply_requirement_changes(
            working["task_requirement_authority"],
            upserts=upserts,
            retire_ids=retire_ids,
            evidence_ref=evidence_ref,
        )
    except RequirementError as exc:
        raise CurrentAdmissionError(str(exc)) from exc

    before_stage = str(working["current_stage"])
    earliest_stage = min(changed_stages, key=lambda item: owner_guard.STAGE_INDEX[item])
    working["task_requirement_authority"] = authority
    working["task_requirement_digest"] = authority_digest(authority)

    invalidated: list[str] = []
    if owner_guard.STAGE_INDEX[before_stage] >= owner_guard.STAGE_INDEX[earliest_stage]:
        _archive_invalidated_quality(working, reason="TASK_REQUIREMENT_CHANGE", earliest_stage=earliest_stage)
        invalidated = owner_guard._invalidate_from(working, earliest_stage)
        working["status"] = "IN_PROGRESS"
        working["current_stage"] = earliest_stage
        working["next_action"] = f"re-execute {earliest_stage} under task requirement revision {authority['revision']}"

    changed_ids = sorted(
        {
            *[str(item.get("requirement_id", "")) for item in (upserts or []) if str(item.get("requirement_id", ""))],
            *[str(item) for item in (retire_ids or []) if str(item)],
        }
    )
    receipt = owner_guard._new_receipt(
        task_id=str(working["task_id"]),
        stage=before_stage,
        capability_id=REQUIREMENT_CAPABILITY_ID,
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind="REQUIREMENT_CHANGE",
        subject_bindings={
            "task_id": working["task_id"],
            "from_stage": before_stage,
            "to_stage": working["current_stage"],
            "requirement_revision": authority["revision"],
        },
        input_bindings={
            "evidence_ref": evidence_ref,
            "changed_requirement_ids": changed_ids,
            "affected_from_stage": earliest_stage,
            "invalidated_stage_refs": invalidated,
        },
        output_refs=[f"workspaces/articles/{working['task_id']}/STATE.json"],
    )
    working["execution_receipts"] = list(state["execution_receipts"]) + [receipt]
    working["updated_at"] = owner_guard._utc_now()
    bind_current_governance_receipt(working)
    validate_state(working)
    return working


def advance_state(
    state: Mapping[str, Any],
    *,
    decision_envelope: Mapping[str, Any] | None = None,
    private_research_brief: Mapping[str, Any] | None = None,
    story_blueprints: list[Mapping[str, Any]] | None = None,
    publication_fitnesses: list[Mapping[str, Any]] | None = None,
    requirement_satisfaction: list[Mapping[str, Any]] | None = None,
    portfolio_context_ref: Mapping[str, Any] | None = None,
    task_intake_manifest: Mapping[str, Any] | None = None,
    task_intake_review_attestation: Mapping[str, Any] | None = None,
    goal_outcome_review: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Single public Article Aggregate transition for current writing-kernel tasks."""
    validate_state(state)
    working = deepcopy(dict(state))
    stage = str(state["current_stage"])
    if stage in owner_guard.REVIEW_STAGE_NAMES and kwargs.get("review_status") == "FAIL":
        allowed_targets = owner_guard._revision_target_names(stage)
        _require(
            kwargs.get("revision_target") in allowed_targets,
            f"FAIL revision_target must be one of {sorted(allowed_targets)}",
        )
    quality = working.setdefault("quality_evidence", {})
    evidence_bindings: dict[str, Any] = {}

    intake_reviewed: dict[str, Any] | None = None
    if stage == "INTAKE" and state.get(TASK_INTAKE_STATE_FIELD) == TASK_INTAKE_CONTRACT_VERSION:
        _require(
            isinstance(portfolio_context_ref, Mapping),
            "TASK_INTAKE_PORTFOLIO_CONTEXT_REQUIRED",
        )
        try:
            normalized_manifest = validate_task_intake_manifest(
                task_intake_manifest,
                task_id=str(state["task_id"]),
                prompt=str(state["prompt"]),
                required_outputs=list(state.get("required_outputs", [])),
            )
            challenge = build_task_intake_review_challenge(
                task_id=str(state["task_id"]),
                prompt=str(state["prompt"]),
                manifest=normalized_manifest,
                required_outputs=list(state.get("required_outputs", [])),
            )
            intake_reviewed = verify_task_intake_review(
                task_intake_review_attestation,
                challenge=challenge,
            )
        except TaskIntakeError as exc:
            raise CurrentAdmissionError(str(exc)) from exc
        _require(
            state["task_requirement_authority"].get("revision") == 0,
            "TASK_INTAKE_INITIAL_REQUIREMENT_AUTHORITY_MUST_BE_EMPTY",
        )
        upserts = [
            item["requirement"]
            for item in normalized_manifest["requirements"]
        ]
        try:
            for item in upserts:
                validate_requirement_applicability(item, state.get("required_outputs", []))
            initial_authority, _ = apply_requirement_changes(
                state["task_requirement_authority"],
                upserts=upserts,
                evidence_ref=normalized_manifest["source_message_ref"],
            )
        except RequirementError as exc:
            raise CurrentAdmissionError(str(exc)) from exc
        working["task_requirement_authority"] = initial_authority
        working["task_requirement_digest"] = authority_digest(initial_authority)
        working["task_intake_manifest"] = normalized_manifest
        working["task_intake_manifest_sha256"] = challenge["manifest_sha256"]
        working["task_intake_review_attestation"] = deepcopy(dict(task_intake_review_attestation or {}))
        evidence_bindings["task_intake_contract_version"] = TASK_INTAKE_CONTRACT_VERSION
        evidence_bindings["task_intake_manifest_sha256"] = challenge["manifest_sha256"]
        evidence_bindings["task_intake_review_attestation_sha256"] = _canonical_digest(
            task_intake_review_attestation
        )
        evidence_bindings["initial_requirement_revision"] = initial_authority["revision"]
    elif any(value is not None for value in (
        task_intake_manifest, task_intake_review_attestation,
    )):
        raise CurrentAdmissionError("TASK_INTAKE_EVIDENCE_ONLY_ALLOWED_AT_GOAL_FIRST_INTAKE")

    verified_goal_review: dict[str, Any] | None = None
    if stage == "FINAL_AUDIT" and state.get(TASK_INTAKE_STATE_FIELD) == TASK_INTAKE_CONTRACT_VERSION:
        try:
            verified_goal_review = verify_goal_outcome_review(
                goal_outcome_review,
                state=state,
            )
        except GoalOutcomeError as exc:
            raise CurrentAdmissionError(str(exc)) from exc
        decision = str(verified_goal_review.get("decision"))
        review_status = str(kwargs.get("review_status"))
        _require(
            review_status == decision,
            "GOAL_OUTCOME_DECISION_MUST_MATCH_FINAL_AUDIT_REVIEW_STATUS",
        )
        if decision == "REVISE":
            _require(
                kwargs.get("revision_target") == verified_goal_review.get("revision_target"),
                "GOAL_OUTCOME_REVISION_TARGET_MISMATCH",
            )
        else:
            _require(
                kwargs.get("revision_target") is None,
                "GOAL_OUTCOME_NON_REVISION_DECISION_CANNOT_SET_REVISION_TARGET",
            )
        evidence_bindings["goal_outcome_review_attestation_sha256"] = _canonical_digest(
            goal_outcome_review
        )
        evidence_bindings["goal_outcome_review_decision"] = decision
        evidence_bindings["goal_outcome_requirement_results_sha256"] = verified_goal_review.get(
            "requirement_results_sha256"
        )
    elif goal_outcome_review is not None:
        raise CurrentAdmissionError("GOAL_OUTCOME_REVIEW_ONLY_ALLOWED_AT_GOAL_FIRST_FINAL_AUDIT")

    satisfaction = _normalize_requirement_satisfaction(state, stage, requirement_satisfaction)
    if satisfaction:
        evidence_bindings["task_requirement_satisfaction_version"] = REQUIREMENT_SATISFACTION_VERSION
        evidence_bindings["task_requirement_satisfaction"] = satisfaction
        evidence_bindings["task_requirement_satisfaction_sha256"] = _canonical_digest(satisfaction)

    if stage == "RESEARCH":
        envelope = _parse_decision_envelope(decision_envelope)
        dumped = envelope.model_dump(mode="json")
        quality["research_decision"] = dumped
        evidence_bindings["decision_envelope_sha256"] = _canonical_digest(dumped)

        if _private_research_required(state) or private_research_brief is not None:
            expected_version = state.get("private_research_contract_version")
            private_dumped = _parse_private_research(
                private_research_brief,
                expected_contract_version=str(expected_version) if expected_version is not None else None,
            )
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
        if review_status == "REVISE":
            order = ("RESEARCH", "EDITORIAL", "TITLE", "DRAFT")
            targets = [
                item.revision_target for item in fitnesses
                if item.final_status == AuditStatus.REVISE
            ]
            _require(bool(targets), "EDITORIAL_AUDIT REVISE requires a fitness revision target")
            expected_target = min(targets, key=order.index)
            _require(
                kwargs.get("revision_target") == expected_target,
                "EDITORIAL_AUDIT revision_target must match the earliest target in publication_fitnesses",
            )
        dumped = [item.model_dump(mode="json") for item in fitnesses]
        quality["publication_fitnesses"] = dumped
        evidence_bindings["publication_fitnesses_sha256"] = _canonical_digest(dumped)

    revision_target = kwargs.get("revision_target")
    planned_invalidated = (
        _planned_quality_invalidations(working, str(revision_target))
        if review_status == "REVISE" and revision_target
        else []
    )
    if planned_invalidated:
        _archive_invalidated_quality(working, reason=f"WORKFLOW_REVISION_FROM_{stage}", earliest_stage=str(revision_target))

    after = owner_guard.advance_state(
        working,
        _current_admission_token=owner_guard._CURRENT_ADMISSION_TOKEN,
        **kwargs,
    )

    if portfolio_context_ref is not None:
        if (
            not isinstance(portfolio_context_ref, Mapping)
            or set(portfolio_context_ref) != {"path", "blob_sha", "sha256", "stage", "generation"}
        ):
            raise CurrentAdmissionError("PORTFOLIO_CONTEXT_REFERENCE_INVALID")
        try:
            context_path = require_article_path(
                portfolio_context_ref.get("path"), after["task_id"],
            )
        except ValueError as exc:
            raise CurrentAdmissionError("PORTFOLIO_CONTEXT_REFERENCE_PATH_INVALID") from exc
        if "/portfolio/contexts/" not in context_path:
            raise CurrentAdmissionError("PORTFOLIO_CONTEXT_REFERENCE_PATH_SCOPE_INVALID")
        blob_sha = portfolio_context_ref.get("blob_sha")
        context_sha = portfolio_context_ref.get("sha256")
        generation = portfolio_context_ref.get("generation")
        if (
            not isinstance(blob_sha, str) or len(blob_sha) != 40
            or any(char not in "0123456789abcdef" for char in blob_sha)
            or not isinstance(context_sha, str) or len(context_sha) != 64
            or any(char not in "0123456789abcdef" for char in context_sha)
            or not isinstance(generation, int) or generation < 0
            or portfolio_context_ref.get("stage") != after["current_stage"]
        ):
            raise CurrentAdmissionError("PORTFOLIO_CONTEXT_REFERENCE_BINDING_INVALID")
        evidence_bindings["portfolio_context_ref"] = {
            "path": context_path,
            "blob_sha": blob_sha,
            "sha256": context_sha,
            "stage": after["current_stage"],
            "generation": generation,
        }
        # A legacy task is promoted to the coordinator contract only when its
        # first typed context is bound to the owner transition.
        after["portfolio_execution_contract_version"] = (
            PORTFOLIO_EXECUTION_CONTRACT_VERSION
        )

    if planned_invalidated:
        missing = [key for key in planned_invalidated if key in after.get("quality_evidence", {})]
        _require(not missing, f"owner revision failed to invalidate quality evidence: {missing}")
        evidence_bindings["invalidated_quality_evidence"] = ",".join(planned_invalidated)

    if verified_goal_review is not None:
        attestation = deepcopy(dict(goal_outcome_review or {}))
        history = list(after.get(GOAL_OUTCOME_REVIEW_HISTORY_FIELD, []))
        history.append({
            "attestation": attestation,
            "attestation_sha256": _canonical_digest(attestation),
            "decision": verified_goal_review["decision"],
        })
        after[GOAL_OUTCOME_REVIEW_HISTORY_FIELD] = history
        if verified_goal_review["decision"] == "PASS":
            after["goal_outcome_review"] = attestation
        else:
            after.pop("goal_outcome_review", None)

    bind_current_governance_receipt(after)
    receipt = after["execution_receipts"][-1]
    receipt["input_bindings"].update(evidence_bindings)
    validate_state(after)
    return after


def attach_material_feedback(state: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
    validate_state(state)
    after = owner_guard.attach_material_feedback(
        state,
        _current_admission_token=owner_guard._CURRENT_ADMISSION_TOKEN,
        **kwargs,
    )
    bind_current_governance_receipt(after)
    validate_state(after)
    return after
