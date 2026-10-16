from __future__ import annotations

from enum import Enum
from typing import Any, Mapping


CURRENT_WRITING_KERNEL_VERSION = "1.0"


class ResumeCompatibilityDecision(str, Enum):
    CURRENT_STATE = "CURRENT_STATE"
    HISTORICAL_PROVENANCE_ONLY = "HISTORICAL_PROVENANCE_ONLY"
    CURRENT_SUCCESSOR_REQUIRED = "CURRENT_SUCCESSOR_REQUIRED"


class ResumeCompatibilityError(ValueError):
    pass


def assess_resume_compatibility(
    state: Mapping[str, Any],
    *,
    intent: str | None,
) -> dict[str, Any]:
    """Classify whether an article state can legally continue under current quality claims.

    Historical Financial states remain immutable provenance. They may still be inspected or
    reproduced under explicitly historical semantics, but they cannot silently inherit the
    semantic assurance of the current writing kernel after a material architecture upgrade.
    """
    current = state.get("writing_kernel_version") == CURRENT_WRITING_KERNEL_VERSION
    if current:
        return {
            "decision": ResumeCompatibilityDecision.CURRENT_STATE.value,
            "reason": "state already carries the current writing-kernel marker and quality evidence contract",
            "requires_successor": False,
        }

    if intent == ResumeCompatibilityDecision.HISTORICAL_PROVENANCE_ONLY.value:
        return {
            "decision": ResumeCompatibilityDecision.HISTORICAL_PROVENANCE_ONLY.value,
            "reason": "caller explicitly requested historical-semantics continuation; no current-kernel quality claim is permitted",
            "requires_successor": False,
        }

    reasons = ["state predates current writing-kernel quality admission"]
    learning = state.get("learning_evidence", [])
    if isinstance(learning, list) and any(
        isinstance(item, Mapping) and item.get("sample_type") in {"USER_REJECTION", "USER_FEEDBACK", "USER_EDIT"}
        for item in learning
    ):
        reasons.append("state carries material corrective feedback")
    impacts = state.get("open_system_impact", [])
    if isinstance(impacts, list) and impacts:
        reasons.append("state carries open system-impact evidence")

    return {
        "decision": ResumeCompatibilityDecision.CURRENT_SUCCESSOR_REQUIRED.value,
        "reason": "; ".join(reasons),
        "requires_successor": True,
    }


def require_material_resume_admission(state: Mapping[str, Any], *, intent: str | None) -> dict[str, Any]:
    result = assess_resume_compatibility(state, intent=intent)
    if result["decision"] == ResumeCompatibilityDecision.CURRENT_SUCCESSOR_REQUIRED.value:
        raise ResumeCompatibilityError(
            "historical Financial state cannot be materially advanced as current-quality output; "
            "create a current-kernel successor/replay instead: " + str(result["reason"])
        )
    return result
