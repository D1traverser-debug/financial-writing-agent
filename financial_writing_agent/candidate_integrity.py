from __future__ import annotations

from typing import Any, Mapping

from .authoritative_state import _json_type_strict_equal
from .models import Stage
from .workflow_spec import (
    REVIEW_STAGE_NAMES,
    invalidated_stage_names_from,
    pass_target_name,
    revision_targets,
)


class CandidateIntegrityError(ValueError):
    pass


TRANSITION_MUTABLE_TOP_LEVEL = frozenset(
    {
        "status",
        "current_stage",
        "next_action",
        "stage_artifacts",
        "review_decisions",
        "delivery_artifacts",
        "quality_evidence",
        "execution_receipts",
        "updated_at",
    }
)

FEEDBACK_MUTABLE_TOP_LEVEL = frozenset(
    {
        "learning_evidence",
        "open_system_impact",
        "execution_receipts",
        "updated_at",
    }
)

LEGACY_MIGRATION_MUTABLE_TOP_LEVEL = frozenset(
    {
        "schema_version",
        "state_ref",
        "target_platforms",
        "distribution_mode_source",
        "delivery_channel",
        "required_outputs",
        "delivery_artifacts",
    }
)

KNOWN_QUALITY_KEYS = frozenset(
    {
        "research_decision",
        "story_blueprints",
        "publication_fitnesses",
    }
)

TERMINAL_STATUS = "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateIntegrityError(message)


def _strict_equal(left: Any, right: Any, message: str) -> None:
    _require(_json_type_strict_equal(left, right), message)


def _mapping(value: Any, *, label: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), f"{label} must be a mapping")
    return value


def _list(value: Any, *, label: str) -> list[Any]:
    _require(isinstance(value, list), f"{label} must be a list")
    return value


def _validate_immutable_by_default(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    mutable_fields: frozenset[str],
    action_label: str,
) -> None:
    if before.get("schema_version") == "1.1":
        mutable_fields = mutable_fields | LEGACY_MIGRATION_MUTABLE_TOP_LEVEL
    all_fields = set(before) | set(after)
    for field in sorted(all_fields - mutable_fields):
        _require(field in before, f"{action_label} cannot inject unowned state field: {field}")
        _require(field in after, f"{action_label} cannot delete immutable state field: {field}")
        _strict_equal(before[field], after[field], f"{action_label} cannot mutate immutable state field: {field}")


def _validate_mapping_delta(
    before_value: Any,
    after_value: Any,
    *,
    mutable_keys: set[str],
    label: str,
) -> None:
    before = _mapping(before_value, label=f"before.{label}")
    after = _mapping(after_value, label=f"after.{label}")
    all_keys = set(before) | set(after)
    for key in sorted(all_keys - mutable_keys):
        _require(key in before, f"{label} cannot inject unowned key: {key}")
        _require(key in after, f"{label} cannot delete immutable key: {key}")
        _strict_equal(before[key], after[key], f"{label} cannot rewrite immutable key: {key}")
    for key in set(after) - set(before):
        _require(key in mutable_keys, f"{label} cannot inject unowned key: {key}")
    for key in set(before) - set(after):
        _require(key in mutable_keys, f"{label} cannot delete immutable key: {key}")


def _last_receipt(after: Mapping[str, Any]) -> Mapping[str, Any]:
    receipts = _list(after.get("execution_receipts"), label="after.execution_receipts")
    _require(bool(receipts), "candidate requires an execution receipt")
    return _mapping(receipts[-1], label="after.execution_receipts[-1]")


def _transition_context(before: Mapping[str, Any], after: Mapping[str, Any]) -> tuple[str, str | None, str | None]:
    stage = str(before.get("current_stage", ""))
    receipt = _last_receipt(after)
    bindings = _mapping(receipt.get("input_bindings"), label="transition receipt input_bindings")
    review_status = bindings.get("review_status")
    revision_target = bindings.get("revision_target")
    return stage, (str(review_status) if review_status is not None else None), (str(revision_target) if revision_target is not None else None)


def _invalidated_names(revision_target: str | None) -> set[str]:
    if not revision_target:
        return set()
    try:
        return set(invalidated_stage_names_from(revision_target))
    except ValueError as exc:
        raise CandidateIntegrityError(str(exc)) from exc


def _allowed_revision_targets(stage: str) -> set[str]:
    try:
        stage_enum = Stage(stage)
    except ValueError:
        return set()
    return {target.value for target in revision_targets(stage_enum)}


def _validate_route_delta(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    stage: str,
    review_status: str | None,
    revision_target: str | None,
) -> str | None:
    _require(
        before.get("status") == "IN_PROGRESS",
        "ordinary transition source state must be IN_PROGRESS; blocked/terminal state requires its dedicated lifecycle path",
    )

    if stage in REVIEW_STAGE_NAMES:
        _require(
            review_status in {"PASS", "REVISE", "FAIL"},
            f"{stage} transition receipt must bind review_status PASS/REVISE/FAIL",
        )
        if review_status == "PASS":
            expected = pass_target_name(stage)
            _require(expected is not None, f"no canonical PASS route from {stage}")
            if expected == "COMPLETE":
                _require(after.get("status") == TERMINAL_STATUS, "FINAL_AUDIT PASS must use bounded terminal status")
                _require(after.get("current_stage") == stage, "terminal FINAL_AUDIT state must remain on FINAL_AUDIT")
            else:
                _require(after.get("status") == "IN_PROGRESS", f"{stage} PASS must remain IN_PROGRESS")
                _require(after.get("current_stage") == expected, f"{stage} PASS must advance to {expected}")
        elif review_status == "REVISE":
            allowed = _allowed_revision_targets(stage)
            _require(revision_target in allowed, f"{stage} REVISE revision_target must be one of {sorted(allowed)}")
            _require(after.get("status") == "IN_PROGRESS", f"{stage} REVISE must remain IN_PROGRESS")
            _require(after.get("current_stage") == revision_target, f"{stage} REVISE must route to {revision_target}")
        else:
            allowed = _allowed_revision_targets(stage)
            _require(revision_target in allowed, f"{stage} FAIL revision_target must be one of {sorted(allowed)}")
            _require(after.get("status") == "BLOCKED", f"{stage} FAIL must block")
            _require(after.get("current_stage") == stage, f"{stage} FAIL must remain on the failed stage")
        return review_status

    _require(review_status is None, f"{stage} is not a review stage and cannot bind review_status")
    _require(revision_target is None, f"{stage} is not a review stage and cannot bind revision_target")
    expected = pass_target_name(stage)
    _require(expected is not None and expected != "COMPLETE", f"no forward transition from {stage}")
    _require(after.get("status") == "IN_PROGRESS", f"{stage} forward transition must remain IN_PROGRESS")
    _require(after.get("current_stage") == expected, f"{stage} must advance to {expected}")
    return None


def _validate_stage_artifact_delta(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    stage: str,
    review_status: str | None,
    revision_target: str | None,
) -> None:
    before_artifacts = _mapping(before.get("stage_artifacts", {}), label="before.stage_artifacts")
    after_artifacts = _mapping(after.get("stage_artifacts", {}), label="after.stage_artifacts")
    if review_status == "REVISE" and revision_target:
        expected = {key: value for key, value in before_artifacts.items() if key not in _invalidated_names(revision_target)}
        _strict_equal(expected, dict(after_artifacts), "stage_artifacts must equal the canonical revision invalidation result")
        return
    _validate_mapping_delta(
        before_artifacts,
        after_artifacts,
        mutable_keys=({stage} if stage != "INTAKE" else set()),
        label="stage_artifacts",
    )


def _validate_review_delta(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    stage: str,
    review_status: str | None,
    revision_target: str | None,
) -> None:
    before_reviews = _mapping(before.get("review_decisions", {}), label="before.review_decisions")
    after_reviews = _mapping(after.get("review_decisions", {}), label="after.review_decisions")
    if stage not in REVIEW_STAGE_NAMES:
        _strict_equal(dict(before_reviews), dict(after_reviews), "non-review transition cannot mutate review_decisions")
        return
    if review_status == "REVISE" and revision_target:
        expected = {key: value for key, value in before_reviews.items() if key not in _invalidated_names(revision_target)}
        _strict_equal(expected, dict(after_reviews), "review_decisions must equal the canonical revision invalidation result")
        return

    _validate_mapping_delta(before_reviews, after_reviews, mutable_keys={stage}, label="review_decisions")
    review = _mapping(after_reviews.get(stage), label=f"after.review_decisions.{stage}")
    _require(review.get("status") == review_status, f"{stage} review decision status must bind the receipt review_status")
    after_artifacts = _mapping(after.get("stage_artifacts", {}), label="after.stage_artifacts")
    stage_artifact = _mapping(after_artifacts.get(stage), label=f"after.stage_artifacts.{stage}")
    _strict_equal(
        stage_artifact,
        review.get("artifact_ref"),
        f"{stage} review decision artifact_ref must bind the exact admitted stage artifact",
    )


def _apply_quality_invalidation(value: Mapping[str, Any], revision_target: str) -> dict[str, Any]:
    expected = dict(value)
    if revision_target == "RESEARCH":
        expected.clear()
    elif revision_target == "EDITORIAL":
        expected.pop("story_blueprints", None)
        expected.pop("publication_fitnesses", None)
    elif revision_target in {"TITLE", "DRAFT"}:
        expected.pop("publication_fitnesses", None)
    return expected


def _validate_quality_delta(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    stage: str,
    review_status: str | None,
    revision_target: str | None,
) -> None:
    if before.get("schema_version") != "1.3":
        _strict_equal(
            before.get("quality_evidence"),
            after.get("quality_evidence"),
            "historical transition cannot mutate quality_evidence",
        )
        return
    before_quality = _mapping(before.get("quality_evidence", {}), label="before.quality_evidence")
    after_quality = _mapping(after.get("quality_evidence", {}), label="after.quality_evidence")
    unknown_before = set(before_quality) - KNOWN_QUALITY_KEYS
    unknown_after = set(after_quality) - KNOWN_QUALITY_KEYS
    _require(not unknown_before, f"before.quality_evidence contains unknown keys: {sorted(unknown_before)}")
    _require(not unknown_after, f"after.quality_evidence contains unknown keys: {sorted(unknown_after)}")
    if review_status == "REVISE" and revision_target:
        _strict_equal(
            _apply_quality_invalidation(before_quality, revision_target),
            dict(after_quality),
            "quality_evidence must equal the canonical revision invalidation result",
        )
        return
    mutable: set[str] = set()
    if stage == "RESEARCH":
        mutable.add("research_decision")
    elif stage == "EDITORIAL":
        mutable.add("story_blueprints")
    elif stage == "EDITORIAL_AUDIT" and review_status == "PASS":
        mutable.add("publication_fitnesses")
    _validate_mapping_delta(before_quality, after_quality, mutable_keys=mutable, label="quality_evidence")


def _validate_delivery_delta(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    stage: str,
    review_status: str | None,
    revision_target: str | None,
) -> None:
    before_delivery = _mapping(before.get("delivery_artifacts", {}), label="before.delivery_artifacts")
    after_delivery = _mapping(after.get("delivery_artifacts", {}), label="after.delivery_artifacts")
    if review_status == "REVISE" and revision_target and "DELIVERY" in _invalidated_names(revision_target):
        _strict_equal({}, dict(after_delivery), "delivery_artifacts must clear when revision invalidates DELIVERY")
        return
    if stage == "DELIVERY":
        return
    if stage == "FINAL_AUDIT" and review_status == "PASS":
        _validate_mapping_delta(before_delivery, after_delivery, mutable_keys={"AUDIT_DOCX"}, label="delivery_artifacts")
        return
    _strict_equal(dict(before_delivery), dict(after_delivery), "transition cannot mutate delivery_artifacts at this stage")


def _validate_common_receipt_identity(receipt: Mapping[str, Any], *, task_id: str, action_kind: str) -> None:
    _require(receipt.get("receipt_contract_version") == "1.1", "receipt_contract_version must remain 1.1")
    receipt_id = receipt.get("receipt_id")
    _require(isinstance(receipt_id, str) and receipt_id.startswith("receipt:"), "receipt_id must use canonical receipt identity")
    action_id = receipt.get("action_id")
    prefix = f"{task_id}:{action_kind}:"
    _require(isinstance(action_id, str) and action_id.startswith(prefix), f"action_id must bind canonical {action_kind} action")
    _require(receipt.get("task_id") == task_id, "receipt task_id must bind the current article")
    _require(
        receipt.get("execution_ref") == f"github-chat://{task_id}/{action_id}",
        "execution_ref must bind the receipt action_id",
    )


def _validate_transition_receipt_identity(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    stage: str,
    review_status: str | None,
    revision_target: str | None,
) -> None:
    receipt = _last_receipt(after)
    task_id = str(before.get("task_id", ""))
    _require(bool(task_id), "transition candidate requires task_id")
    _validate_common_receipt_identity(receipt, task_id=task_id, action_kind="TRANSITION")
    subject = _mapping(receipt.get("subject_bindings"), label="transition receipt subject_bindings")
    bindings = _mapping(receipt.get("input_bindings"), label="transition receipt input_bindings")
    _require(subject.get("task_id") == task_id, "transition receipt subject task_id mismatch")
    _require(subject.get("from_stage") == stage, "transition receipt subject from_stage mismatch")
    _require(bindings.get("from_stage") == stage, "transition receipt input from_stage mismatch")

    if stage in REVIEW_STAGE_NAMES:
        _require(bindings.get("review_status") == review_status, "review receipt review_status mismatch")
        if review_status in {"REVISE", "FAIL"}:
            _require(bindings.get("revision_target") == revision_target, f"{review_status} receipt revision_target mismatch")
        elif "revision_target" in bindings:
            _require(bindings.get("revision_target") in {None, ""}, "PASS receipt cannot bind a revision_target")

        if review_status == "PASS":
            if after.get("status") == TERMINAL_STATUS:
                _require(subject.get("to_stage") is None, "terminal review receipt to_stage must be null")
                _require(subject.get("terminal_status") == TERMINAL_STATUS, "terminal review receipt must bind terminal_status")
            else:
                _require(subject.get("to_stage") == after.get("current_stage"), "PASS receipt to_stage mismatch")
        elif review_status == "REVISE":
            _require(subject.get("to_stage") == revision_target, "REVISE receipt to_stage mismatch")
        elif review_status == "FAIL":
            _require(subject.get("to_stage") == stage, "FAIL receipt must remain on the failed stage")
            _require(subject.get("blocked") is True, "FAIL receipt must bind blocked=true")
    else:
        _require("review_status" not in bindings, "non-review receipt cannot bind review_status")
        _require("revision_target" not in bindings, "non-review receipt cannot bind revision_target")
        _require(subject.get("to_stage") == after.get("current_stage"), "transition receipt to_stage mismatch")

    output_refs = _list(receipt.get("output_refs"), label="transition receipt output_refs")
    expected_count = 1 if stage == "INTAKE" else 2
    _require(len(output_refs) == expected_count, "transition receipt output_refs count does not match stage output ownership")
    state_path = f"workspaces/articles/{task_id}/STATE.json"
    _require(output_refs[0] == state_path, "transition receipt must bind canonical STATE.json first")

    if expected_count == 2:
        _require(bindings.get("required_artifact_key") == stage, "transition receipt required_artifact_key must bind current stage")
        bound_sha = bindings.get("required_artifact_blob_sha")
        _require(isinstance(bound_sha, str) and bool(bound_sha.strip()), "transition receipt must bind required_artifact_blob_sha")
        artifact_path = output_refs[1]
        _require(
            isinstance(artifact_path, str) and artifact_path.startswith(f"workspaces/articles/{task_id}/"),
            "transition receipt artifact output must belong to the current article workspace",
        )
        if review_status != "REVISE":
            after_artifacts = _mapping(after.get("stage_artifacts", {}), label="after.stage_artifacts")
            stage_artifact = _mapping(after_artifacts.get(stage), label=f"after.stage_artifacts.{stage}")
            _require(artifact_path == stage_artifact.get("path"), "transition receipt artifact output must equal admitted stage artifact path")
            _require(bound_sha == stage_artifact.get("blob_sha"), "transition receipt artifact SHA must equal admitted stage artifact blob_sha")


def _validate_append_one(before_value: Any, after_value: Any, *, label: str) -> Any:
    before = _list(before_value, label=f"before.{label}")
    after = _list(after_value, label=f"after.{label}")
    _require(len(after) == len(before) + 1, f"{label} mutation must append exactly one item")
    _strict_equal(before, after[:-1], f"{label} mutation cannot rewrite prior history")
    return after[-1]


def validate_transition_candidate_isolation(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    _validate_immutable_by_default(
        before,
        after,
        mutable_fields=TRANSITION_MUTABLE_TOP_LEVEL,
        action_label="transition candidate",
    )
    _validate_append_one(
        before.get("execution_receipts", []),
        after.get("execution_receipts", []),
        label="execution_receipts",
    )
    stage, receipt_review_status, revision_target = _transition_context(before, after)
    effective_review_status = _validate_route_delta(
        before,
        after,
        stage=stage,
        review_status=receipt_review_status,
        revision_target=revision_target,
    )
    _validate_stage_artifact_delta(
        before,
        after,
        stage=stage,
        review_status=effective_review_status,
        revision_target=revision_target,
    )
    _validate_review_delta(
        before,
        after,
        stage=stage,
        review_status=effective_review_status,
        revision_target=revision_target,
    )
    _validate_quality_delta(
        before,
        after,
        stage=stage,
        review_status=effective_review_status,
        revision_target=revision_target,
    )
    _validate_delivery_delta(
        before,
        after,
        stage=stage,
        review_status=effective_review_status,
        revision_target=revision_target,
    )
    _validate_transition_receipt_identity(
        before,
        after,
        stage=stage,
        review_status=effective_review_status,
        revision_target=revision_target,
    )


def _validate_feedback_append_semantics(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    sample = _validate_append_one(
        before.get("learning_evidence", []),
        after.get("learning_evidence", []),
        label="learning_evidence",
    )
    impact = _validate_append_one(
        before.get("open_system_impact", []),
        after.get("open_system_impact", []),
        label="open_system_impact",
    )
    sample_map = _mapping(sample, label="appended learning_evidence")
    impact_map = _mapping(impact, label="appended open_system_impact")
    sample_type = sample_map.get("sample_type")
    _require(sample_type in {"USER_EDIT", "USER_FEEDBACK", "USER_REJECTION"}, "appended learning sample_type is invalid")
    summary = sample_map.get("summary")
    _require(isinstance(summary, str) and bool(summary.strip()), "appended learning summary is required")
    signal_id = impact_map.get("signal_id")
    _require(isinstance(signal_id, str) and bool(signal_id.strip()), "appended system-impact signal_id is required")
    prior_impacts = _list(before.get("open_system_impact", []), label="before.open_system_impact")
    _require(
        all(not isinstance(item, Mapping) or item.get("signal_id") != signal_id for item in prior_impacts),
        "appended system-impact signal_id must be unique within open_system_impact",
    )
    _require(impact_map.get("status") == "OPEN", "appended system-impact status must be OPEN")
    _require(impact_map.get("trigger_sample_type") == sample_type, "appended system-impact trigger_sample_type mismatch")

    receipt = _last_receipt(after)
    task_id = str(before.get("task_id", ""))
    _require(bool(task_id), "feedback candidate requires task_id")
    _validate_common_receipt_identity(receipt, task_id=task_id, action_kind="MATERIAL_FEEDBACK")
    subject = _mapping(receipt.get("subject_bindings"), label="feedback receipt subject_bindings")
    bindings = _mapping(receipt.get("input_bindings"), label="feedback receipt input_bindings")
    _require(subject.get("task_id") == task_id, "feedback receipt subject task_id mismatch")
    _require(subject.get("sample_type") == sample_type, "feedback receipt sample_type does not bind appended sample")
    _require(subject.get("signal_id") == signal_id, "feedback receipt signal_id does not bind appended system-impact")
    _require(bindings.get("feedback_summary") == summary, "feedback receipt summary does not bind appended sample")
    _require(bindings.get("signal_status") == "OPEN", "feedback receipt signal_status does not bind appended system-impact")
    output_refs = _list(receipt.get("output_refs"), label="feedback receipt output_refs")
    _strict_equal(
        [f"workspaces/articles/{task_id}/STATE.json"],
        output_refs,
        "feedback receipt output_refs must bind only canonical STATE.json",
    )


def validate_feedback_candidate_isolation(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    _validate_immutable_by_default(
        before,
        after,
        mutable_fields=FEEDBACK_MUTABLE_TOP_LEVEL,
        action_label="feedback mutation",
    )
    _validate_append_one(
        before.get("execution_receipts", []),
        after.get("execution_receipts", []),
        label="execution_receipts",
    )
    _validate_feedback_append_semantics(before, after)
