from __future__ import annotations

from typing import Any, Mapping

from .authoritative_state import _json_type_strict_equal


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


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateIntegrityError(message)


def _validate_immutable_by_default(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    mutable_fields: frozenset[str],
    action_label: str,
) -> None:
    """Require every field not owned by this action to remain type-strictly identical.

    The comparison is immutable-by-default: fields unknown to current code are protected
    automatically instead of becoming silently mutable merely because a validator does
    not know about them yet.
    """
    all_fields = set(before) | set(after)
    for field in sorted(all_fields - mutable_fields):
        _require(field in before, f"{action_label} cannot inject unowned state field: {field}")
        _require(field in after, f"{action_label} cannot delete immutable state field: {field}")
        _require(
            _json_type_strict_equal(before[field], after[field]),
            f"{action_label} cannot mutate immutable state field: {field}",
        )


def validate_transition_candidate_isolation(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    _validate_immutable_by_default(
        before,
        after,
        mutable_fields=TRANSITION_MUTABLE_TOP_LEVEL,
        action_label="transition candidate",
    )


def validate_feedback_candidate_isolation(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    _validate_immutable_by_default(
        before,
        after,
        mutable_fields=FEEDBACK_MUTABLE_TOP_LEVEL,
        action_label="feedback mutation",
    )
