from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from .authoritative_state import AuthoritativeStateError, fetch_authoritative_state
from .candidate_integrity import (
    CandidateIntegrityError,
    validate_feedback_candidate_isolation,
    validate_transition_candidate_isolation,
)
from .models import ArtifactKind, DeliveryChannel, DistributionMode, Stage, TaskContract
from .routing import build_task_contract
from .workflow_spec import (
    BUSINESS_STAGE_NAMES,
    REVIEW_STAGE_NAMES,
    invalidated_stage_names_from,
    pass_target_name,
    revision_targets,
)

GITHUB_CHAT_EXECUTION_MODE = "GITHUB_CHAT"
CHAT_REVIEW_ASSURANCE = "CHAT_SELF_REVIEW"
TERMINAL_STATUS = "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN"
SELF_ATTESTED_RECEIPT = "SELF_ATTESTED_CHAT_EXECUTION_RECEIPT"
ALLOWED_STATUS = {"IN_PROGRESS", "BLOCKED", TERMINAL_STATUS}
CURRENT_STATE_SCHEMA_VERSION = "1.2"
QUALITY_STATE_SCHEMA_VERSION = "1.3"
LEGACY_STATE_SCHEMA_VERSION = "1.1"
SUPPORTED_STATE_SCHEMA_VERSIONS = {
    LEGACY_STATE_SCHEMA_VERSION,
    CURRENT_STATE_SCHEMA_VERSION,
    QUALITY_STATE_SCHEMA_VERSION,
}
MAIN_STATE_REF = "main"
MODE_SOURCE_CANONICAL = "CANONICAL_ROUTING"
MODE_SOURCE_USER_EXPLICIT = "USER_EXPLICIT_OVERRIDE"
MODE_SOURCE_LEGACY = "LEGACY_STATE_MIGRATION"
CURRENT_WRITING_KERNEL_VERSION = "1.0"
CURRENT_QUALITY_ADMISSION_PATH = "financial_writing_agent.current_admission"

STAGE_INDEX = {stage: i for i, stage in enumerate(BUSINESS_STAGE_NAMES)}
ARTIFACT_REQUIRED_FOR_STAGE = {stage: stage for stage in BUSINESS_STAGE_NAMES if stage != "INTAKE"}
CAPABILITY_BY_STAGE = {
    "RESEARCH_AUDIT": "github_chat_review_stages",
    "EDITORIAL_AUDIT": "github_chat_review_stages",
    "FINAL_AUDIT": "github_chat_review_stages",
    "DELIVERY": "github_chat_delivery_and_mechanical_qa",
    "MECHANICAL_AUDIT": "github_chat_delivery_and_mechanical_qa",
}

BASE_REQUIRED_STATE_FIELDS = {
    "schema_version",
    "task_id",
    "execution_mode",
    "status",
    "current_stage",
    "next_action",
    "distribution_mode",
    "prompt",
    "source_refs",
    "stage_artifacts",
    "review_assurance",
    "open_system_impact",
    "execution_receipts",
    "updated_at",
}
CURRENT_REQUIRED_STATE_FIELDS = BASE_REQUIRED_STATE_FIELDS | {
    "state_ref",
    "target_platforms",
    "distribution_mode_source",
    "delivery_channel",
    "required_outputs",
    "delivery_artifacts",
}
QUALITY_REQUIRED_STATE_FIELDS = CURRENT_REQUIRED_STATE_FIELDS | {
    "writing_kernel_version",
    "quality_evidence",
}
REQUIRED_RECEIPT_FIELDS = {
    "receipt_id",
    "action_id",
    "task_id",
    "stage",
    "capability_id",
    "executor_identity",
    "execution_ref",
    "subject_bindings",
    "input_bindings",
    "output_refs",
    "result",
}
CONTRACT_FIELDS = (
    "state_ref",
    "target_platforms",
    "distribution_mode",
    "distribution_mode_source",
    "delivery_channel",
    "required_outputs",
)


class GithubChatGuardError(ValueError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GithubChatGuardError(message)


def _state_path(task_id: str) -> str:
    return f"workspaces/articles/{task_id}/STATE.json"


def _expected_capability(stage: str) -> str:
    return CAPABILITY_BY_STAGE.get(stage, "github_chat_workflow")


def _revision_target_names(stage: str) -> set[str]:
    try:
        stage_enum = Stage(stage)
    except ValueError:
        return set()
    return {target.value for target in revision_targets(stage_enum)}


def _required_outputs_for_mode(distribution_mode: str) -> list[str]:
    try:
        mode = DistributionMode(distribution_mode)
    except ValueError as exc:
        raise GithubChatGuardError(f"unsupported distribution_mode: {distribution_mode}") from exc
    contract = TaskContract(prompt="contract-validation", distribution_mode=mode)
    return [kind.value for kind in contract.required_outputs]


def _required_article_outputs(state: Mapping[str, Any]) -> set[str]:
    return {kind for kind in state.get("required_outputs", []) if kind != ArtifactKind.AUDIT_DOCX.value}


def _validate_artifact_ref(ref: Any, *, label: str, task_id: str) -> None:
    _require(isinstance(ref, Mapping), f"{label} must be an object")
    path = ref.get("path")
    _require(_nonempty(path), f"{label}.path is required")
    _require(_nonempty(ref.get("blob_sha")), f"{label}.blob_sha is required")
    _require(
        str(path).startswith(f"workspaces/articles/{task_id}/"),
        f"{label}.path must belong to the current article workspace",
    )


def _validate_delivery_artifact_metadata(meta: Any, *, kind: str) -> None:
    _require(isinstance(meta, Mapping), f"delivery_artifacts.{kind} must be an object")
    _require(meta.get("kind") == kind, f"delivery_artifacts.{kind}.kind mismatch")
    _require(_nonempty(meta.get("file_name")), f"delivery_artifacts.{kind}.file_name is required")
    sha = meta.get("sha256")
    _require(
        isinstance(sha, str)
        and len(sha) == 64
        and all(ch in "0123456789abcdefABCDEF" for ch in sha),
        f"delivery_artifacts.{kind}.sha256 must be a 64-character hex digest",
    )


def _normalize_delivery_artifacts(items: list[Mapping[str, Any]] | None) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for item in items or []:
        _require(isinstance(item, Mapping), "delivery artifact must be an object")
        kind = str(item.get("kind", ""))
        _require(kind in {member.value for member in ArtifactKind}, f"unsupported delivery artifact kind: {kind}")
        _require(kind not in normalized, f"duplicate delivery artifact kind: {kind}")
        payload = dict(item)
        _validate_delivery_artifact_metadata(payload, kind=kind)
        normalized[kind] = payload
    return normalized


def _require_article_output_contract(state: Mapping[str, Any]) -> None:
    expected = _required_article_outputs(state)
    actual = set(state.get("delivery_artifacts", {}))
    _require(actual == expected, f"article delivery outputs mismatch: required={sorted(expected)}, actual={sorted(actual)}")


def _require_full_output_contract(state: Mapping[str, Any]) -> None:
    expected = set(state.get("required_outputs", []))
    actual = set(state.get("delivery_artifacts", {}))
    _require(actual == expected, f"final delivery outputs mismatch: required={sorted(expected)}, actual={sorted(actual)}")


def _upgrade_legacy_state(state: Mapping[str, Any], *, state_ref: str) -> dict[str, Any]:
    upgraded = deepcopy(dict(state))
    if upgraded.get("schema_version") != LEGACY_STATE_SCHEMA_VERSION:
        return upgraded
    _require(state_ref == MAIN_STATE_REF, "legacy GITHUB_CHAT state may only be resumed after placement on main")
    mode = str(upgraded.get("distribution_mode", ""))
    upgraded["schema_version"] = CURRENT_STATE_SCHEMA_VERSION
    upgraded["state_ref"] = MAIN_STATE_REF
    upgraded["target_platforms"] = []
    upgraded["distribution_mode_source"] = MODE_SOURCE_LEGACY
    upgraded["delivery_channel"] = DeliveryChannel.WORD_FILE_ONLY.value
    upgraded["required_outputs"] = _required_outputs_for_mode(mode)
    upgraded["delivery_artifacts"] = {}
    return upgraded


def _validate_current_provenance(state: Mapping[str, Any]) -> None:
    _require(
        state.get("schema_version") == QUALITY_STATE_SCHEMA_VERSION,
        "current Financial quality state must use schema_version=1.3",
    )
    _require(
        state.get("writing_kernel_version") == CURRENT_WRITING_KERNEL_VERSION,
        "current Financial quality state must bind writing_kernel_version=1.0",
    )
    _require(isinstance(state.get("quality_evidence"), Mapping), "current Financial state requires quality_evidence mapping")
    receipts = state.get("execution_receipts", [])
    _require(isinstance(receipts, list) and bool(receipts), "current Financial state requires execution receipts")
    first = receipts[0]
    _require(isinstance(first, Mapping) and first.get("stage") == "INTAKE", "current Financial state requires canonical INIT receipt")
    for index, receipt in enumerate(receipts):
        _require(isinstance(receipt, Mapping), "current Financial receipt must be an object")
        bindings = receipt.get("input_bindings", {})
        _require(isinstance(bindings, Mapping), "current Financial receipt input_bindings required")
        _require(
            bindings.get("writing_kernel_version") == CURRENT_WRITING_KERNEL_VERSION,
            f"current Financial receipt {index} lost writing-kernel provenance",
        )
        _require(
            bindings.get("quality_admission_path") == CURRENT_QUALITY_ADMISSION_PATH,
            f"current Financial receipt {index} lost quality-admission provenance",
        )


def _validate_base_state(state: Mapping[str, Any]) -> None:
    schema = state.get("schema_version")
    _require(schema in SUPPORTED_STATE_SCHEMA_VERSIONS, f"unsupported state schema_version: {schema}")
    if schema == QUALITY_STATE_SCHEMA_VERSION:
        required_fields = QUALITY_REQUIRED_STATE_FIELDS
    elif schema == CURRENT_STATE_SCHEMA_VERSION:
        required_fields = CURRENT_REQUIRED_STATE_FIELDS
    else:
        required_fields = BASE_REQUIRED_STATE_FIELDS
    missing = sorted(required_fields - set(state))
    _require(not missing, f"state missing required fields: {missing}")
    _require(state.get("execution_mode") == GITHUB_CHAT_EXECUTION_MODE, "execution_mode must be GITHUB_CHAT")
    _require(_nonempty(state.get("task_id")), "task_id is required")
    _require(state.get("current_stage") in BUSINESS_STAGE_NAMES, "current_stage is not a supported Financial stage")
    _require(state.get("status") in ALLOWED_STATUS, "status is not a supported GITHUB_CHAT status")
    if state.get("status") == TERMINAL_STATUS:
        _require(state.get("current_stage") == "FINAL_AUDIT", "bounded terminal status requires FINAL_AUDIT as current_stage")
    _require(state.get("review_assurance") == CHAT_REVIEW_ASSURANCE, "review_assurance must remain CHAT_SELF_REVIEW")
    _require(isinstance(state.get("stage_artifacts"), Mapping), "stage_artifacts must be an object")
    _require(isinstance(state.get("open_system_impact"), list), "open_system_impact must be a list")
    _require(isinstance(state.get("review_decisions", {}), Mapping), "review_decisions must be an object")
    _require(isinstance(state.get("learning_evidence", []), list), "learning_evidence must be a list")

    if schema in {CURRENT_STATE_SCHEMA_VERSION, QUALITY_STATE_SCHEMA_VERSION}:
        _require(state.get("state_ref") == MAIN_STATE_REF, "GITHUB_CHAT business state must live on main")
        _require(isinstance(state.get("target_platforms"), list), "target_platforms must be a list")
        _require(
            state.get("distribution_mode_source")
            in {MODE_SOURCE_CANONICAL, MODE_SOURCE_USER_EXPLICIT, MODE_SOURCE_LEGACY},
            "distribution_mode_source invalid",
        )
        _require(state.get("delivery_channel") == DeliveryChannel.WORD_FILE_ONLY.value, "delivery_channel must remain WORD_FILE_ONLY")
        expected_outputs = _required_outputs_for_mode(str(state.get("distribution_mode")))
        _require(state.get("required_outputs") == expected_outputs, f"required_outputs drift from TaskContract: expected={expected_outputs}")
        _require(isinstance(state.get("delivery_artifacts"), Mapping), "delivery_artifacts must be an object")
        for kind, meta in state.get("delivery_artifacts", {}).items():
            _require(kind in expected_outputs, f"unexpected delivery artifact kind: {kind}")
            _validate_delivery_artifact_metadata(meta, kind=kind)
        if state.get("status") == TERMINAL_STATUS:
            _require_full_output_contract(state)

    current_index = STAGE_INDEX[str(state["current_stage"])]
    for key, ref in state.get("stage_artifacts", {}).items():
        _require(key in STAGE_INDEX and key != "INTAKE", f"unknown stage_artifact key: {key}")
        _require(STAGE_INDEX[key] <= current_index, f"future-stage artifact is not allowed before reaching {key}")
        _validate_artifact_ref(ref, label=f"stage_artifacts.{key}", task_id=str(state["task_id"]))
    for key in state.get("review_decisions", {}):
        _require(key in REVIEW_STAGE_NAMES, f"review_decisions contains non-review stage: {key}")
        _require(STAGE_INDEX[key] <= current_index, f"future-stage review is not allowed before reaching {key}")

    receipts = state.get("execution_receipts")
    _require(isinstance(receipts, list) and receipts, "execution_receipts must be a non-empty list")
    seen_receipts: set[str] = set()
    seen_actions: set[str] = set()
    for receipt in receipts:
        _require(isinstance(receipt, Mapping), "execution receipt must be an object")
        missing_receipt = sorted(REQUIRED_RECEIPT_FIELDS - set(receipt))
        _require(not missing_receipt, f"execution receipt missing fields: {missing_receipt}")
        receipt_id = str(receipt.get("receipt_id"))
        action_id = str(receipt.get("action_id"))
        _require(receipt_id not in seen_receipts, f"duplicate receipt_id: {receipt_id}")
        _require(action_id not in seen_actions, f"duplicate action_id: {action_id}")
        seen_receipts.add(receipt_id)
        seen_actions.add(action_id)
        _require(receipt.get("task_id") == state.get("task_id"), "receipt task_id mismatch")
        _require(_nonempty(receipt.get("executor_identity")), "receipt executor_identity is required")
        _require(_nonempty(receipt.get("execution_ref")), "receipt execution_ref is required")
        _require(isinstance(receipt.get("subject_bindings"), Mapping) and bool(receipt["subject_bindings"]), "receipt subject_bindings required")
        _require(isinstance(receipt.get("input_bindings"), Mapping) and bool(receipt["input_bindings"]), "receipt input_bindings required")
        if "state_ref" in receipt.get("input_bindings", {}):
            _require(receipt["input_bindings"]["state_ref"] == MAIN_STATE_REF, "receipt state_ref must be main")
        _require(isinstance(receipt.get("output_refs"), list) and bool(receipt["output_refs"]), "receipt output_refs required")
        _require(receipt.get("result") == "GUARD_ACCEPTED", "chat receipt result must be GUARD_ACCEPTED")
        _require(receipt.get("verification_status") == SELF_ATTESTED_RECEIPT, "chat receipt must remain self-attested")

    if schema == QUALITY_STATE_SCHEMA_VERSION:
        _validate_current_provenance(state)


def _validate_unpersisted_state(state: Mapping[str, Any]) -> None:
    _validate_base_state(state)
    if state.get("schema_version") != QUALITY_STATE_SCHEMA_VERSION:
        return
    try:
        from .current_admission import _validate_current_quality_evidence

        _validate_current_quality_evidence(state)
    except ValueError as exc:
        raise GithubChatGuardError(f"current Financial quality admission failed: {exc}") from exc


def _resolve_authoritative_state(
    state: Mapping[str, Any],
    *,
    expected_blob_sha: str | None = None,
) -> None:
    task_id = str(state.get("task_id", "")).strip()
    _require(bool(task_id), "task_id is required before authoritative state resolution")
    try:
        snapshot = fetch_authoritative_state(task_id, ref=MAIN_STATE_REF)
    except AuthoritativeStateError as exc:
        raise GithubChatGuardError(str(exc)) from exc
    _require(snapshot.state == dict(state), "candidate state differs from authoritative GitHub STATE.json")
    if expected_blob_sha is not None:
        clean_expected = str(expected_blob_sha).strip().lower()
        _require(snapshot.blob_sha == clean_expected, "previous_state_blob_sha does not match authoritative GitHub STATE.json")


def validate_state(state: Mapping[str, Any]) -> None:
    _validate_unpersisted_state(state)
    _resolve_authoritative_state(state)


def _validate_persisted_state(state: Mapping[str, Any], *, previous_state_blob_sha: str) -> None:
    _validate_unpersisted_state(state)
    _resolve_authoritative_state(state, expected_blob_sha=previous_state_blob_sha)


def _new_receipt(
    *,
    task_id: str,
    stage: str,
    capability_id: str,
    executor_identity: str,
    previous_state_blob_sha: str,
    action_kind: str,
    subject_bindings: Mapping[str, Any],
    input_bindings: Mapping[str, Any],
    output_refs: list[str],
    action_id: str | None = None,
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    _require(_nonempty(executor_identity), "executor_identity is required")
    _require(_nonempty(previous_state_blob_sha), "previous_state_blob_sha is required")
    _require(state_ref == MAIN_STATE_REF, "GITHUB_CHAT material mutations must target main")
    action_id = action_id or f"{task_id}:{action_kind}:{uuid4()}"
    return {
        "receipt_contract_version": "1.1",
        "receipt_id": f"receipt:{uuid4()}",
        "action_id": action_id,
        "task_id": task_id,
        "stage": stage,
        "capability_id": capability_id,
        "executor_identity": executor_identity,
        "execution_ref": f"github-chat://{task_id}/{action_id}",
        "subject_bindings": dict(subject_bindings),
        "input_bindings": {"previous_state_blob_sha": previous_state_blob_sha, "state_ref": state_ref, **dict(input_bindings)},
        "output_refs": list(output_refs),
        "result": "GUARD_ACCEPTED",
        "verification_status": SELF_ATTESTED_RECEIPT,
    }


def _current_receipt_bindings(state: Mapping[str, Any]) -> dict[str, str]:
    if state.get("schema_version") != QUALITY_STATE_SCHEMA_VERSION:
        return {}
    return {
        "writing_kernel_version": CURRENT_WRITING_KERNEL_VERSION,
        "quality_admission_path": CURRENT_QUALITY_ADMISSION_PATH,
    }


def build_initial_state(
    *,
    task_id: str,
    prompt: str,
    source_refs: list[str] | None,
    executor_identity: str,
    target_platforms: list[str] | None = None,
    distribution_mode: str | None = None,
    distribution_mode_source: str | None = None,
    distribution_mode_override_evidence: str | None = None,
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    _require(_nonempty(task_id), "task_id is required")
    _require(_nonempty(prompt), "prompt is required")
    _require(state_ref == MAIN_STATE_REF, "new GITHUB_CHAT tasks must be created on main")
    refs = list(source_refs or [])
    platforms = list(target_platforms or [])

    if distribution_mode is None:
        _require(distribution_mode_source in {None, MODE_SOURCE_CANONICAL}, "distribution_mode_source must be CANONICAL_ROUTING when mode is inferred")
        _require(not _nonempty(distribution_mode_override_evidence), "canonical routing must not carry single-mode override evidence")
        contract = build_task_contract(prompt=prompt, source_refs=refs, target_platforms=platforms)
        mode_source = MODE_SOURCE_CANONICAL
        override_evidence = None
    else:
        _require(distribution_mode_source == MODE_SOURCE_USER_EXPLICIT, "distribution_mode override requires USER_EXPLICIT_OVERRIDE provenance")
        _require(_nonempty(distribution_mode_override_evidence), "distribution_mode override requires exact user prompt evidence")
        override_evidence = str(distribution_mode_override_evidence).strip()
        _require(override_evidence in prompt, "distribution_mode override evidence must be an exact substring of the user prompt")
        try:
            mode = DistributionMode(distribution_mode)
        except ValueError as exc:
            raise GithubChatGuardError(f"unsupported distribution_mode: {distribution_mode}") from exc
        contract = TaskContract(
            prompt=prompt,
            source_refs=refs,
            target_platforms=platforms,
            distribution_mode=mode,
            delivery_channel=DeliveryChannel.WORD_FILE_ONLY,
        )
        mode_source = MODE_SOURCE_USER_EXPLICIT

    required_outputs = [kind.value for kind in contract.required_outputs]
    receipt = _new_receipt(
        task_id=task_id,
        stage="INTAKE",
        capability_id="github_chat_workflow",
        executor_identity=executor_identity,
        previous_state_blob_sha="NEW_FILE",
        action_kind="INIT",
        subject_bindings={"task_id": task_id, "from_stage": None, "to_stage": "INTAKE"},
        input_bindings={
            "prompt": prompt,
            "target_platforms": platforms,
            "distribution_mode": contract.distribution_mode.value,
            "distribution_mode_source": mode_source,
            "distribution_mode_override_evidence": override_evidence,
            "delivery_channel": contract.delivery_channel.value,
            "required_outputs": required_outputs,
            "writing_kernel_version": CURRENT_WRITING_KERNEL_VERSION,
            "quality_admission_path": CURRENT_QUALITY_ADMISSION_PATH,
        },
        output_refs=[_state_path(task_id)],
        state_ref=state_ref,
    )
    state = {
        "schema_version": QUALITY_STATE_SCHEMA_VERSION,
        "writing_kernel_version": CURRENT_WRITING_KERNEL_VERSION,
        "quality_evidence": {},
        "task_id": task_id,
        "execution_mode": GITHUB_CHAT_EXECUTION_MODE,
        "status": "IN_PROGRESS",
        "current_stage": "INTAKE",
        "next_action": "run exact-stage capability handshake, then guard transition INTAKE → RESEARCH",
        "state_ref": MAIN_STATE_REF,
        "target_platforms": platforms,
        "distribution_mode": contract.distribution_mode.value,
        "distribution_mode_source": mode_source,
        "delivery_channel": contract.delivery_channel.value,
        "required_outputs": required_outputs,
        "delivery_artifacts": {},
        "prompt": prompt,
        "source_refs": refs,
        "stage_artifacts": {},
        "review_decisions": {},
        "review_assurance": CHAT_REVIEW_ASSURANCE,
        "learning_evidence": [],
        "open_system_impact": [],
        "execution_receipts": [receipt],
        "updated_at": _utc_now(),
    }
    _validate_unpersisted_state(state)
    return state


def _required_artifact(stage: str, state: Mapping[str, Any]) -> tuple[str, Mapping[str, Any]] | None:
    key = ARTIFACT_REQUIRED_FOR_STAGE.get(stage)
    if key is None:
        return None
    ref = state.get("stage_artifacts", {}).get(key)
    _validate_artifact_ref(ref, label=f"stage_artifacts.{key}", task_id=str(state["task_id"]))
    return key, ref


def _invalidate_from(state: dict[str, Any], target_stage: str) -> list[str]:
    try:
        downstream = invalidated_stage_names_from(target_stage)
    except ValueError as exc:
        raise GithubChatGuardError(str(exc)) from exc
    invalidated: list[str] = []
    artifacts = state.setdefault("stage_artifacts", {})
    reviews = state.setdefault("review_decisions", {})
    for stage in downstream:
        if stage in artifacts:
            artifacts.pop(stage, None)
            invalidated.append(stage)
        reviews.pop(stage, None)
    if "DELIVERY" in downstream:
        state["delivery_artifacts"] = {}

    quality = state.get("quality_evidence")
    if isinstance(quality, dict):
        if target_stage == "RESEARCH":
            quality.clear()
        elif target_stage == "EDITORIAL":
            quality.pop("story_blueprints", None)
            quality.pop("publication_fitnesses", None)
        elif target_stage in {"TITLE", "DRAFT"}:
            quality.pop("publication_fitnesses", None)
    return invalidated


def _prepare_transition_quality(
    state: Mapping[str, Any],
    *,
    decision_envelope: Mapping[str, Any] | None,
    story_blueprints: list[Mapping[str, Any]] | None,
    publication_fitnesses: list[Mapping[str, Any]] | None,
    review_status: str | None,
    revision_target: str | None,
) -> tuple[dict[str, Any], dict[str, str], list[str]]:
    if state.get("schema_version") != QUALITY_STATE_SCHEMA_VERSION:
        _require(
            decision_envelope is None and story_blueprints is None and publication_fitnesses is None,
            "legacy Financial state cannot accept current quality-admission payloads",
        )
        return deepcopy(dict(state)), {}, []
    try:
        from .current_admission import _prepare_quality_transition

        return _prepare_quality_transition(
            state,
            decision_envelope=decision_envelope,
            story_blueprints=story_blueprints,
            publication_fitnesses=publication_fitnesses,
            review_status=review_status,
            revision_target=revision_target,
        )
    except ValueError as exc:
        raise GithubChatGuardError(f"current Financial quality admission failed: {exc}") from exc


def advance_state(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    artifact_key: str | None = None,
    artifact_path: str | None = None,
    artifact_blob_sha: str | None = None,
    review_status: str | None = None,
    revision_target: str | None = None,
    delivery_artifacts: list[Mapping[str, Any]] | None = None,
    audit_artifact: Mapping[str, Any] | None = None,
    decision_envelope: Mapping[str, Any] | None = None,
    story_blueprints: list[Mapping[str, Any]] | None = None,
    publication_fitnesses: list[Mapping[str, Any]] | None = None,
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    _require(state_ref == MAIN_STATE_REF, "GITHUB_CHAT material mutations must target main")
    _validate_persisted_state(state, previous_state_blob_sha=previous_state_blob_sha)
    before = _upgrade_legacy_state(state, state_ref=state_ref)
    _validate_unpersisted_state(before)
    working, quality_bindings, planned_quality_invalidations = _prepare_transition_quality(
        before,
        decision_envelope=decision_envelope,
        story_blueprints=story_blueprints,
        publication_fitnesses=publication_fitnesses,
        review_status=review_status,
        revision_target=revision_target,
    )
    after = deepcopy(working)
    stage = str(before["current_stage"])
    _require(before.get("status") != TERMINAL_STATUS, "terminal chat state cannot advance")
    _require(before.get("status") != "BLOCKED", "BLOCKED chat state must be explicitly repaired before advance")

    if artifact_key is not None:
        _require(artifact_key == ARTIFACT_REQUIRED_FOR_STAGE.get(stage), f"artifact_key must match current stage {stage}")
        _require(_nonempty(artifact_path) and _nonempty(artifact_blob_sha), "artifact path/blob_sha required together")
        ref = {"path": artifact_path, "blob_sha": artifact_blob_sha}
        _validate_artifact_ref(ref, label=f"stage_artifacts.{artifact_key}", task_id=str(before["task_id"]))
        after.setdefault("stage_artifacts", {})[artifact_key] = ref

    required = _required_artifact(stage, after)
    output_refs = [_state_path(str(before["task_id"]))]
    input_bindings: dict[str, Any] = {
        "from_stage": stage,
        **_current_receipt_bindings(before),
        **quality_bindings,
    }
    if required:
        key, ref = required
        input_bindings["required_artifact_key"] = key
        input_bindings["required_artifact_blob_sha"] = ref["blob_sha"]
        output_refs.append(str(ref["path"]))

    if stage == "DELIVERY":
        provided = _normalize_delivery_artifacts(delivery_artifacts)
        _require(provided, "DELIVERY requires structured article delivery_artifacts")
        _require(ArtifactKind.AUDIT_DOCX.value not in provided, "AUDIT_DOCX is finalized at FINAL_AUDIT, not DELIVERY")
        after["delivery_artifacts"] = provided
        _require_article_output_contract(after)
        input_bindings["required_article_outputs"] = sorted(_required_article_outputs(after))
        input_bindings["delivered_article_outputs"] = sorted(provided)

    if stage == "MECHANICAL_AUDIT" and review_status == "PASS":
        _require_article_output_contract(after)

    subject_bindings: dict[str, Any] = {"task_id": before["task_id"], "from_stage": stage}
    capability_id = _expected_capability(stage)

    if stage in REVIEW_STAGE_NAMES:
        _require(review_status in {"PASS", "REVISE", "FAIL"}, f"{stage} requires review_status PASS/REVISE/FAIL")
        _require(required is not None, f"{stage} requires persisted review artifact")
        review = {"status": review_status, "artifact_ref": dict(required[1]), "assurance": CHAT_REVIEW_ASSURANCE}
        if review_status == "PASS":
            next_stage = pass_target_name(stage)
            _require(next_stage is not None, f"no canonical PASS transition is defined from {stage}")
            review["revision_target"] = None
            after.setdefault("review_decisions", {})[stage] = review
            if next_stage == "COMPLETE":
                _require(isinstance(audit_artifact, Mapping), "FINAL_AUDIT PASS requires structured AUDIT_DOCX metadata")
                audit_map = _normalize_delivery_artifacts([audit_artifact])
                _require(set(audit_map) == {ArtifactKind.AUDIT_DOCX.value}, "FINAL_AUDIT audit_artifact must be AUDIT_DOCX")
                merged = dict(after.get("delivery_artifacts", {}))
                merged.update(audit_map)
                after["delivery_artifacts"] = merged
                _require_full_output_contract(after)
                input_bindings["required_outputs"] = list(after["required_outputs"])
                input_bindings["final_delivery_outputs"] = sorted(merged)
                after["status"] = TERMINAL_STATUS
                after["current_stage"] = stage
                after["next_action"] = "owner-native/independent certification remains OPEN unless stronger evidence is separately obtained"
                subject_bindings["to_stage"] = None
                subject_bindings["terminal_status"] = TERMINAL_STATUS
            else:
                after["current_stage"] = next_stage
                after["next_action"] = f"execute and persist {next_stage}"
                subject_bindings["to_stage"] = next_stage
        elif review_status == "REVISE":
            allowed = _revision_target_names(stage)
            _require(revision_target in allowed, f"{stage} revision_target must be one of {sorted(allowed)}")
            review["revision_target"] = revision_target
            after.setdefault("review_decisions", {})[stage] = review
            invalidated = _invalidate_from(after, str(revision_target))
            after["current_stage"] = revision_target
            after["next_action"] = f"revise and persist a new {revision_target} artifact before advancing"
            subject_bindings["to_stage"] = revision_target
            input_bindings["invalidated_stage_refs"] = invalidated
            if planned_quality_invalidations:
                still_present = [key for key in planned_quality_invalidations if key in after.get("quality_evidence", {})]
                _require(not still_present, f"owner revision failed to invalidate quality evidence: {still_present}")
                input_bindings["invalidated_quality_evidence"] = ",".join(planned_quality_invalidations)
        else:
            review["revision_target"] = None
            after.setdefault("review_decisions", {})[stage] = review
            after["status"] = "BLOCKED"
            after["current_stage"] = stage
            after["next_action"] = f"resolve {stage} failure before any further stage transition"
            subject_bindings["to_stage"] = stage
            subject_bindings["blocked"] = True
        input_bindings["review_status"] = review_status
        if revision_target:
            input_bindings["revision_target"] = revision_target
    else:
        _require(review_status is None and revision_target is None, f"{stage} is not a review stage")
        next_stage = pass_target_name(stage)
        _require(next_stage is not None and next_stage != "COMPLETE", f"no regular forward transition is defined from {stage}")
        after["current_stage"] = next_stage
        after["next_action"] = f"execute and persist {next_stage}"
        subject_bindings["to_stage"] = next_stage

    receipt = _new_receipt(
        task_id=str(before["task_id"]),
        stage=stage,
        capability_id=capability_id,
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind="TRANSITION",
        subject_bindings=subject_bindings,
        input_bindings=input_bindings,
        output_refs=output_refs,
        state_ref=state_ref,
    )
    after["execution_receipts"] = list(before["execution_receipts"]) + [receipt]
    after["updated_at"] = _utc_now()
    _validate_transition_core(before, after, previous_state_blob_sha=previous_state_blob_sha)
    return after


def attach_material_feedback(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    sample: Mapping[str, Any],
    system_impact: Mapping[str, Any],
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    _require(state_ref == MAIN_STATE_REF, "GITHUB_CHAT material mutations must target main")
    _validate_persisted_state(state, previous_state_blob_sha=previous_state_blob_sha)
    before = _upgrade_legacy_state(state, state_ref=state_ref)
    _validate_unpersisted_state(before)
    _require(sample.get("sample_type") in {"USER_EDIT", "USER_FEEDBACK", "USER_REJECTION"}, "material feedback sample_type invalid")
    _require(_nonempty(sample.get("summary")), "feedback summary required")
    _require(_nonempty(system_impact.get("signal_id")), "system-impact signal_id required")
    _require(system_impact.get("status") == "OPEN", "system-impact status must be OPEN")
    _require(system_impact.get("trigger_sample_type") == sample.get("sample_type"), "system-impact trigger_sample_type mismatch")

    after = deepcopy(dict(before))
    after.setdefault("learning_evidence", []).append(dict(sample))
    after.setdefault("open_system_impact", []).append(dict(system_impact))
    receipt = _new_receipt(
        task_id=str(before["task_id"]),
        stage=str(before["current_stage"]),
        capability_id="github_chat_learning_evidence_capture",
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind="MATERIAL_FEEDBACK",
        subject_bindings={
            "task_id": before["task_id"],
            "sample_type": sample["sample_type"],
            "signal_id": system_impact["signal_id"],
        },
        input_bindings={
            "feedback_summary": sample["summary"],
            "signal_status": system_impact["status"],
            **_current_receipt_bindings(before),
        },
        output_refs=[_state_path(str(before["task_id"]))],
        state_ref=state_ref,
    )
    after["execution_receipts"] = list(before["execution_receipts"]) + [receipt]
    after["updated_at"] = _utc_now()
    _validate_feedback_update_core(before, after, previous_state_blob_sha=previous_state_blob_sha)
    return after


def _validate_contract_immutability(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    for field in CONTRACT_FIELDS:
        _require(before.get(field) == after.get(field), f"task contract field cannot change during transition: {field}")


def _validate_governance_immutability(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    """Prevent public candidate validators from downgrading the governing state schema."""
    before_schema = before.get("schema_version")
    after_schema = after.get("schema_version")
    if before_schema == QUALITY_STATE_SCHEMA_VERSION:
        _require(after_schema == QUALITY_STATE_SCHEMA_VERSION, "schema-1.3 current state cannot downgrade governance")
        _require(
            after.get("writing_kernel_version") == before.get("writing_kernel_version") == CURRENT_WRITING_KERNEL_VERSION,
            "current Financial writing-kernel provenance cannot change during mutation",
        )
    elif before_schema == CURRENT_STATE_SCHEMA_VERSION:
        _require(after_schema == CURRENT_STATE_SCHEMA_VERSION, "schema-1.2 historical state cannot change schema during mutation")
    elif before_schema == LEGACY_STATE_SCHEMA_VERSION:
        _require(
            after_schema in {LEGACY_STATE_SCHEMA_VERSION, CURRENT_STATE_SCHEMA_VERSION},
            "schema-1.1 legacy state may only remain legacy or migrate to schema 1.2",
        )


def _validate_transition_core(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
) -> None:
    _validate_unpersisted_state(before)
    try:
        validate_transition_candidate_isolation(before, after)
    except CandidateIntegrityError as exc:
        raise GithubChatGuardError(str(exc)) from exc
    _validate_unpersisted_state(after)
    _require(before["task_id"] == after["task_id"], "task_id cannot change")
    _validate_governance_immutability(before, after)
    _validate_contract_immutability(before, after)
    _require(len(after["execution_receipts"]) == len(before["execution_receipts"]) + 1, "exactly one execution receipt must be appended")
    _require(after["execution_receipts"][:-1] == before["execution_receipts"], "prior execution receipts are immutable")
    receipt = after["execution_receipts"][-1]
    _require(receipt["input_bindings"].get("previous_state_blob_sha") == previous_state_blob_sha, "receipt must bind current GitHub state blob SHA")
    _require(receipt["input_bindings"].get("state_ref") == MAIN_STATE_REF, "receipt must bind main state_ref")
    _require(receipt["stage"] == before["current_stage"], "receipt stage must bind the stage being left/reviewed")
    _require(receipt["capability_id"] == _expected_capability(str(before["current_stage"])), "receipt capability_id does not match stage executor")

    stage = str(before["current_stage"])
    if stage in REVIEW_STAGE_NAMES:
        review = after.get("review_decisions", {}).get(stage)
        if review is None and receipt["input_bindings"].get("review_status") == "REVISE":
            review_status = "REVISE"
        else:
            _require(isinstance(review, Mapping), f"{stage} review decision missing")
            _require(review.get("assurance") == CHAT_REVIEW_ASSURANCE, "chat review assurance may not be upgraded")
            review_status = review.get("status")
        if review_status == "PASS":
            expected = pass_target_name(stage)
            _require(expected is not None, f"no canonical PASS route from {stage}")
            if stage == "MECHANICAL_AUDIT":
                _require_article_output_contract(after)
            if expected == "COMPLETE":
                _require(after.get("status") == TERMINAL_STATUS, "FINAL_AUDIT PASS must use bounded chat terminal status")
                _require(after.get("current_stage") == stage, "terminal chat state keeps FINAL_AUDIT as last stage")
                _require_full_output_contract(after)
            else:
                _require(after.get("current_stage") == expected, f"{stage} PASS must advance to {expected}")
        elif review_status == "REVISE":
            target = receipt["input_bindings"].get("revision_target")
            _require(target in _revision_target_names(stage), f"{stage} REVISE target unsupported")
            _require(after.get("current_stage") == target, f"{stage} REVISE must route to {target}")
            for downstream in invalidated_stage_names_from(str(target)):
                _require(downstream not in after.get("stage_artifacts", {}), f"stale artifact survived revision: {downstream}")
                _require(downstream not in after.get("review_decisions", {}), f"stale review survived revision: {downstream}")
            if "DELIVERY" in invalidated_stage_names_from(str(target)):
                _require(after.get("delivery_artifacts") == {}, "stale delivery artifacts survived revision")
        elif review_status == "FAIL":
            _require(after.get("status") == "BLOCKED" and after.get("current_stage") == stage, f"{stage} FAIL must block in place")
        else:
            raise GithubChatGuardError(f"{stage} review status invalid")
    else:
        expected = pass_target_name(stage)
        _require(expected is not None and expected != "COMPLETE", f"no forward transition from {stage}")
        _require(after.get("current_stage") == expected, f"stage skip/route mismatch: {stage} must advance to {expected}")
        if stage == "DELIVERY":
            _require_article_output_contract(after)

    required = ARTIFACT_REQUIRED_FOR_STAGE.get(stage)
    if required and receipt["input_bindings"].get("review_status") != "REVISE":
        _validate_artifact_ref(after.get("stage_artifacts", {}).get(required), label=f"stage_artifacts.{required}", task_id=str(after["task_id"]))


def validate_transition(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
) -> None:
    _validate_persisted_state(before, previous_state_blob_sha=previous_state_blob_sha)
    _validate_transition_core(before, after, previous_state_blob_sha=previous_state_blob_sha)


def _validate_feedback_update_core(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
) -> None:
    _validate_unpersisted_state(before)
    try:
        validate_feedback_candidate_isolation(before, after)
    except CandidateIntegrityError as exc:
        raise GithubChatGuardError(str(exc)) from exc
    _validate_unpersisted_state(after)
    _require(before["task_id"] == after["task_id"], "task_id cannot change")
    _validate_governance_immutability(before, after)
    _validate_contract_immutability(before, after)
    _require(before["current_stage"] == after["current_stage"], "feedback checkpoint cannot change current_stage")
    _require(len(after.get("learning_evidence", [])) == len(before.get("learning_evidence", [])) + 1, "exactly one learning sample must be appended")
    _require(len(after["open_system_impact"]) == len(before["open_system_impact"]) + 1, "exactly one OPEN system-impact item must be appended")
    _require(len(after["execution_receipts"]) == len(before["execution_receipts"]) + 1, "feedback checkpoint must append exactly one execution receipt")
    _require(after["execution_receipts"][:-1] == before["execution_receipts"], "prior execution receipts are immutable")
    receipt = after["execution_receipts"][-1]
    _require(receipt["capability_id"] == "github_chat_learning_evidence_capture", "feedback receipt capability mismatch")
    _require(receipt["input_bindings"].get("previous_state_blob_sha") == previous_state_blob_sha, "feedback receipt must bind current state blob SHA")
    _require(receipt["input_bindings"].get("state_ref") == MAIN_STATE_REF, "feedback receipt must bind main state_ref")


def validate_feedback_update(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
) -> None:
    _validate_persisted_state(before, previous_state_blob_sha=previous_state_blob_sha)
    _validate_feedback_update_core(before, after, previous_state_blob_sha=previous_state_blob_sha)
