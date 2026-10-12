from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from .models import Stage
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

# Adapter-local indexes/capabilities derive from the canonical workflow. The chat
# adapter may be more conservative than owner-native execution, but it cannot invent
# a broader stage/revision graph.
STAGE_INDEX = {stage: i for i, stage in enumerate(BUSINESS_STAGE_NAMES)}
ARTIFACT_REQUIRED_FOR_STAGE = {stage: stage for stage in BUSINESS_STAGE_NAMES if stage != "INTAKE"}
CAPABILITY_BY_STAGE = {
    "RESEARCH_AUDIT": "github_chat_review_stages",
    "EDITORIAL_AUDIT": "github_chat_review_stages",
    "FINAL_AUDIT": "github_chat_review_stages",
    "DELIVERY": "github_chat_delivery_and_mechanical_qa",
    "MECHANICAL_AUDIT": "github_chat_delivery_and_mechanical_qa",
}

REQUIRED_STATE_FIELDS = {
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


def _validate_artifact_ref(ref: Any, *, label: str, task_id: str) -> None:
    _require(isinstance(ref, Mapping), f"{label} must be an object")
    path = ref.get("path")
    _require(_nonempty(path), f"{label}.path is required")
    _require(_nonempty(ref.get("blob_sha")), f"{label}.blob_sha is required")
    _require(
        str(path).startswith(f"workspaces/articles/{task_id}/"),
        f"{label}.path must belong to the current article workspace",
    )


def validate_state(state: Mapping[str, Any]) -> None:
    missing = sorted(REQUIRED_STATE_FIELDS - set(state))
    _require(not missing, f"state missing required fields: {missing}")
    _require(state.get("schema_version") == "1.1", "state schema_version must be 1.1")
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
        _require(isinstance(receipt.get("output_refs"), list) and bool(receipt["output_refs"]), "receipt output_refs required")
        _require(receipt.get("result") == "GUARD_ACCEPTED", "chat receipt result must be GUARD_ACCEPTED")
        _require(receipt.get("verification_status") == SELF_ATTESTED_RECEIPT, "chat receipt must remain self-attested")


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
) -> dict[str, Any]:
    _require(_nonempty(executor_identity), "executor_identity is required")
    _require(_nonempty(previous_state_blob_sha), "previous_state_blob_sha is required")
    action_id = action_id or f"{task_id}:{action_kind}:{uuid4()}"
    return {
        "receipt_contract_version": "1.0",
        "receipt_id": f"receipt:{uuid4()}",
        "action_id": action_id,
        "task_id": task_id,
        "stage": stage,
        "capability_id": capability_id,
        "executor_identity": executor_identity,
        "execution_ref": f"github-chat://{task_id}/{action_id}",
        "subject_bindings": dict(subject_bindings),
        "input_bindings": {"previous_state_blob_sha": previous_state_blob_sha, **dict(input_bindings)},
        "output_refs": list(output_refs),
        "result": "GUARD_ACCEPTED",
        "verification_status": SELF_ATTESTED_RECEIPT,
    }


def build_initial_state(
    *,
    task_id: str,
    prompt: str,
    distribution_mode: str,
    source_refs: list[str] | None,
    executor_identity: str,
) -> dict[str, Any]:
    _require(_nonempty(task_id), "task_id is required")
    _require(_nonempty(prompt), "prompt is required")
    receipt = _new_receipt(
        task_id=task_id,
        stage="INTAKE",
        capability_id="github_chat_workflow",
        executor_identity=executor_identity,
        previous_state_blob_sha="NEW_FILE",
        action_kind="INIT",
        subject_bindings={"task_id": task_id, "from_stage": None, "to_stage": "INTAKE"},
        input_bindings={"prompt": prompt, "distribution_mode": distribution_mode},
        output_refs=[_state_path(task_id)],
    )
    state = {
        "schema_version": "1.1",
        "task_id": task_id,
        "execution_mode": GITHUB_CHAT_EXECUTION_MODE,
        "status": "IN_PROGRESS",
        "current_stage": "INTAKE",
        "next_action": "run exact-stage capability handshake, then guard transition INTAKE → RESEARCH",
        "distribution_mode": distribution_mode,
        "prompt": prompt,
        "source_refs": list(source_refs or []),
        "stage_artifacts": {},
        "review_decisions": {},
        "review_assurance": CHAT_REVIEW_ASSURANCE,
        "learning_evidence": [],
        "open_system_impact": [],
        "execution_receipts": [receipt],
        "updated_at": _utc_now(),
    }
    validate_state(state)
    return state


def _required_artifact(stage: str, state: Mapping[str, Any]) -> tuple[str, Mapping[str, Any]] | None:
    key = ARTIFACT_REQUIRED_FOR_STAGE.get(stage)
    if key is None:
        return None
    ref = state.get("stage_artifacts", {}).get(key)
    _validate_artifact_ref(ref, label=f"stage_artifacts.{key}", task_id=str(state["task_id"]))
    return key, ref


def _invalidate_from(state: dict[str, Any], target_stage: str) -> list[str]:
    """Invalidate target-stage and downstream derived evidence after a revision route."""
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
    return invalidated


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
) -> dict[str, Any]:
    validate_state(state)
    before = deepcopy(dict(state))
    after = deepcopy(dict(state))
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
    input_bindings: dict[str, Any] = {"from_stage": stage}
    if required:
        key, ref = required
        input_bindings["required_artifact_key"] = key
        input_bindings["required_artifact_blob_sha"] = ref["blob_sha"]
        output_refs.append(str(ref["path"]))

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
    )
    after["execution_receipts"] = list(before["execution_receipts"]) + [receipt]
    after["updated_at"] = _utc_now()
    validate_transition(before, after, previous_state_blob_sha=previous_state_blob_sha)
    return after


def attach_material_feedback(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    sample: Mapping[str, Any],
    system_impact: Mapping[str, Any],
) -> dict[str, Any]:
    validate_state(state)
    _require(sample.get("sample_type") in {"USER_EDIT", "USER_FEEDBACK", "USER_REJECTION"}, "material feedback sample_type invalid")
    _require(_nonempty(sample.get("summary")), "feedback summary required")
    _require(_nonempty(system_impact.get("signal_id")), "system-impact signal_id required")
    _require(system_impact.get("status") == "OPEN", "system-impact status must be OPEN")
    _require(system_impact.get("trigger_sample_type") == sample.get("sample_type"), "system-impact trigger_sample_type mismatch")

    before = deepcopy(dict(state))
    after = deepcopy(dict(state))
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
        input_bindings={"feedback_summary": sample["summary"], "signal_status": system_impact["status"]},
        output_refs=[_state_path(str(before["task_id"]))],
    )
    after["execution_receipts"] = list(before["execution_receipts"]) + [receipt]
    after["updated_at"] = _utc_now()
    validate_feedback_update(before, after, previous_state_blob_sha=previous_state_blob_sha)
    return after


def validate_transition(before: Mapping[str, Any], after: Mapping[str, Any], *, previous_state_blob_sha: str) -> None:
    validate_state(before)
    validate_state(after)
    _require(before["task_id"] == after["task_id"], "task_id cannot change")
    _require(len(after["execution_receipts"]) == len(before["execution_receipts"]) + 1, "exactly one execution receipt must be appended")
    _require(after["execution_receipts"][:-1] == before["execution_receipts"], "prior execution receipts are immutable")
    receipt = after["execution_receipts"][-1]
    _require(receipt["input_bindings"].get("previous_state_blob_sha") == previous_state_blob_sha, "receipt must bind current GitHub state blob SHA")
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
            if expected == "COMPLETE":
                _require(after.get("status") == TERMINAL_STATUS, "FINAL_AUDIT PASS must use bounded chat terminal status")
                _require(after.get("current_stage") == stage, "terminal chat state keeps FINAL_AUDIT as last stage")
            else:
                _require(after.get("current_stage") == expected, f"{stage} PASS must advance to {expected}")
        elif review_status == "REVISE":
            target = receipt["input_bindings"].get("revision_target")
            _require(target in _revision_target_names(stage), f"{stage} REVISE target unsupported")
            _require(after.get("current_stage") == target, f"{stage} REVISE must route to {target}")
            for downstream in invalidated_stage_names_from(str(target)):
                _require(downstream not in after.get("stage_artifacts", {}), f"stale artifact survived revision: {downstream}")
                _require(downstream not in after.get("review_decisions", {}), f"stale review survived revision: {downstream}")
        elif review_status == "FAIL":
            _require(after.get("status") == "BLOCKED" and after.get("current_stage") == stage, f"{stage} FAIL must block in place")
        else:
            raise GithubChatGuardError(f"{stage} review status invalid")
    else:
        expected = pass_target_name(stage)
        _require(expected is not None and expected != "COMPLETE", f"no forward transition from {stage}")
        _require(after.get("current_stage") == expected, f"stage skip/route mismatch: {stage} must advance to {expected}")

    required = ARTIFACT_REQUIRED_FOR_STAGE.get(stage)
    if required and receipt["input_bindings"].get("review_status") != "REVISE":
        _validate_artifact_ref(after.get("stage_artifacts", {}).get(required), label=f"stage_artifacts.{required}", task_id=str(after["task_id"]))


def validate_feedback_update(before: Mapping[str, Any], after: Mapping[str, Any], *, previous_state_blob_sha: str) -> None:
    validate_state(before)
    validate_state(after)
    _require(before["task_id"] == after["task_id"], "task_id cannot change")
    _require(before["current_stage"] == after["current_stage"], "feedback checkpoint cannot change current_stage")
    _require(len(after.get("learning_evidence", [])) == len(before.get("learning_evidence", [])) + 1, "exactly one learning sample must be appended")
    _require(len(after["open_system_impact"]) == len(before["open_system_impact"]) + 1, "exactly one OPEN system-impact item must be appended")
    _require(len(after["execution_receipts"]) == len(before["execution_receipts"]) + 1, "feedback checkpoint must append exactly one execution receipt")
    _require(after["execution_receipts"][:-1] == before["execution_receipts"], "prior execution receipts are immutable")
    receipt = after["execution_receipts"][-1]
    _require(receipt["capability_id"] == "github_chat_learning_evidence_capture", "feedback receipt capability mismatch")
    _require(receipt["input_bindings"].get("previous_state_blob_sha") == previous_state_blob_sha, "feedback receipt must bind current state blob SHA")
