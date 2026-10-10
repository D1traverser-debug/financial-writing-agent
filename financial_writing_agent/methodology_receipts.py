from __future__ import annotations

from typing import Any

from .models import GateStatus, WritingState


PROFILE_VERSION = "1.0"
RECEIPT_CONTRACT_VERSION = "1.1"

ARTIFACT_IO_HOOKS = (
    "durable_task_state_location",
    "authoritative_business_evidence_classes",
    "canonical_artifact_or_file_stores",
    "cache_or_reference_only_stores",
    "stable_identity_strategy",
    "read_freshness_requirements",
    "mutation_conflict_strategy",
    "post_write_verification_method",
    "upstream_to_downstream_invalidation_rule",
    "delete_and_retention_rules",
    "superseded_artifact_cleanup_rule",
    "external_artifact_vault_if_any",
)

EVOLUTION_HOOKS = (
    "learning_evidence_location",
    "eval_or_regression_promotion_path",
    "superseded_mechanism_cleanup_rule",
)


def _assessment(status: str, reason: str, refs: list[str]) -> dict[str, Any]:
    if status not in {"INVOKED", "NOT_APPLICABLE_FOR_ACTION"}:
        raise ValueError(f"unsupported hook assessment status: {status}")
    clean_reason = reason.strip()
    clean_refs = list(dict.fromkeys(ref.strip() for ref in refs if isinstance(ref, str) and ref.strip()))
    if not clean_reason:
        raise ValueError("hook assessment reason must not be empty")
    if not clean_refs:
        raise ValueError("hook assessment evidence refs must not be empty")
    return {"status": status, "reason": clean_reason, "evidence_refs": clean_refs}


def _append_profile_run(
    state: WritingState,
    *,
    profile_id: str,
    trigger: str,
    hook_order: tuple[str, ...],
    hook_assessments: dict[str, dict[str, Any]],
    evidence_refs: list[str],
) -> dict[str, Any]:
    if set(hook_assessments) != set(hook_order):
        missing = sorted(set(hook_order) - set(hook_assessments))
        extra = sorted(set(hook_assessments) - set(hook_order))
        raise ValueError(f"profile receipt hook coverage mismatch: missing={missing}, extra={extra}")

    invoked_hooks = [
        hook for hook in hook_order
        if hook_assessments[hook].get("status") == "INVOKED"
    ]
    if not invoked_hooks:
        raise ValueError("methodology profile run must invoke at least one hook")

    clean_refs = list(dict.fromkeys(ref.strip() for ref in evidence_refs if isinstance(ref, str) and ref.strip()))
    if not clean_refs:
        raise ValueError("methodology profile run requires evidence refs")

    runs = state.working.setdefault("methodology_profile_runs", [])
    activation_id = f"{state.contract.task_id}:{profile_id}:{len(runs) + 1:04d}"
    run = {
        "receipt_contract_version": RECEIPT_CONTRACT_VERSION,
        "profile_id": profile_id,
        "profile_version": PROFILE_VERSION,
        "activation_id": activation_id,
        "trigger": trigger.strip(),
        "invoked_hooks": invoked_hooks,
        "hook_assessments": hook_assessments,
        "evidence_refs": clean_refs,
        "verification_status": "UNVERIFIED_OWNER_RECEIPT",
    }
    if not run["trigger"]:
        raise ValueError("methodology profile run trigger must not be empty")

    runs.append(run)
    state.add_trace(
        "METHODOLOGY_PROFILE_RUN",
        f"profile={profile_id}@{PROFILE_VERSION}; activation={activation_id}; invoked={','.join(invoked_hooks)}; verification=external_required",
    )
    return run


def record_learning_evolution_receipt(state: WritingState) -> dict[str, Any]:
    samples = state.working.get("learning_samples") or []
    if not samples:
        raise ValueError("cannot record evolution receipt without persisted learning evidence")

    sample_index = len(samples) - 1
    sample_ref = f"writingstate://{state.contract.task_id}/learning_samples/{sample_index}"
    assessments = {
        "learning_evidence_location": _assessment(
            "INVOKED",
            "The current action persisted one raw Writing-DNA evidence sample in authoritative WritingState.",
            [sample_ref],
        ),
        "eval_or_regression_promotion_path": _assessment(
            "NOT_APPLICABLE_FOR_ACTION",
            "This action records raw evidence only and does not attempt production-rule or quality-method promotion.",
            [sample_ref],
        ),
        "superseded_mechanism_cleanup_rule": _assessment(
            "NOT_APPLICABLE_FOR_ACTION",
            "No production mechanism changed during raw evidence capture, so no superseded mechanism exists to retire in this action.",
            [sample_ref],
        ),
    }
    return _append_profile_run(
        state,
        profile_id="evolution",
        trigger="PERSIST_RAW_WRITING_LEARNING_EVIDENCE",
        hook_order=EVOLUTION_HOOKS,
        hook_assessments=assessments,
        evidence_refs=[sample_ref],
    )


def record_artifact_io_receipt(state: WritingState) -> dict[str, Any]:
    gate = state.gates.get("mechanical_audit")
    if gate is None or gate.status != GateStatus.PASS:
        raise ValueError("artifact_io receipt requires mechanical_audit PASS")

    artifact_refs = [
        f"writingartifact://{state.contract.task_id}/{kind.value}/{artifact.sha256}"
        for kind, artifact in state.artifacts.items()
        if artifact.exists and artifact.sha256
    ]
    if not artifact_refs:
        raise ValueError("artifact_io receipt requires at least one existing hash-bound artifact")

    gate_ref = f"writingstate://{state.contract.task_id}/gates/mechanical_audit"
    state_ref = f"writingstate://{state.contract.task_id}/current"
    primary_refs = [gate_ref, state_ref, *artifact_refs]

    assessments = {
        "durable_task_state_location": _assessment(
            "INVOKED",
            "The delivery/mechanical action loaded and persisted authoritative WritingState.",
            [state_ref],
        ),
        "authoritative_business_evidence_classes": _assessment(
            "INVOKED",
            "Mechanical gate evidence and hash-bound publication artifacts were recorded as owner evidence.",
            [gate_ref, *artifact_refs],
        ),
        "canonical_artifact_or_file_stores": _assessment(
            "INVOKED",
            "Required Word artifacts were built in the configured owner runtime artifact store.",
            artifact_refs,
        ),
        "cache_or_reference_only_stores": _assessment(
            "NOT_APPLICABLE_FOR_ACTION",
            "This deterministic owner delivery action did not promote any reference/cache store into authority.",
            [state_ref],
        ),
        "stable_identity_strategy": _assessment(
            "INVOKED",
            "Each persisted publication artifact is bound to task identity, artifact kind and SHA-256.",
            artifact_refs,
        ),
        "read_freshness_requirements": _assessment(
            "INVOKED",
            "The deterministic delivery/mechanical action operated on the current persisted task state and current artifact bytes.",
            [state_ref, gate_ref],
        ),
        "mutation_conflict_strategy": _assessment(
            "INVOKED",
            "The owner state-machine stage guard and current task writer path governed this state mutation.",
            [state_ref],
        ),
        "post_write_verification_method": _assessment(
            "INVOKED",
            "Artifact existence/hash checks and mechanical/render audit completed before this receipt was emitted.",
            [gate_ref, *artifact_refs],
        ),
        "upstream_to_downstream_invalidation_rule": _assessment(
            "NOT_APPLICABLE_FOR_ACTION",
            "This successful delivery/mechanical action did not change an upstream research/editorial/draft input and therefore triggered no downstream invalidation.",
            [gate_ref],
        ),
        "delete_and_retention_rules": _assessment(
            "NOT_APPLICABLE_FOR_ACTION",
            "This action created/verified current outputs and did not request destructive deletion or retention cleanup.",
            [gate_ref],
        ),
        "superseded_artifact_cleanup_rule": _assessment(
            "NOT_APPLICABLE_FOR_ACTION",
            "No revision or supersession cleanup was requested in this successful mechanical-audit action.",
            [gate_ref],
        ),
        "external_artifact_vault_if_any": _assessment(
            "NOT_APPLICABLE_FOR_ACTION",
            "This action did not upload or promote an external artifact vault.",
            [gate_ref],
        ),
    }
    return _append_profile_run(
        state,
        profile_id="artifact_io",
        trigger="BUILD_AND_MECHANICALLY_VERIFY_PUBLICATION_ARTIFACTS",
        hook_order=ARTIFACT_IO_HOOKS,
        hook_assessments=assessments,
        evidence_refs=primary_refs,
    )
