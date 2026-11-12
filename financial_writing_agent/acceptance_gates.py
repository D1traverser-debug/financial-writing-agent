"""Financial system release authority backed by signed provider evidence."""
from __future__ import annotations

from typing import Any, Mapping
import os

from .provider_attestation import (
    FinancialProviderAttestationError,
    expected_owner_principal,
    payload_sha256,
    verify_provider_attestation,
)

SYSTEM_GATES = (
    "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION",
    "LEGAL_ARTICLE_GRAPH_AND_RECOVERY",
    "METHOD_KNOWLEDGE_CRUD_AND_IMPACT",
    "PROVIDER_AUTHENTICATED_RUNTIME_CAS",
    "NATIVE_FINANCIAL_PLUGIN_CLIENT_ACTIVATION",
    "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW",
    "FINANCIAL_MAIN_BRANCH_HYGIENE",
)
GATE_VERSION = "1.1"

REQUIRED_GATE_EVIDENCE = {
    "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION": (
        "source_ref", "source_sha256", "owner_confirmation_ref", "owner_principal",
    ),
    "LEGAL_ARTICLE_GRAPH_AND_RECOVERY": (
        "task_id", "previous_state_blob_sha", "resulting_state_blob_sha",
        "recovery_test_ref", "state_readback_sha",
    ),
    "METHOD_KNOWLEDGE_CRUD_AND_IMPACT": (
        "catalog_revision", "change_event_ref", "affected_task_ids",
        "replay_readback_ref",
    ),
    "PROVIDER_AUTHENTICATED_RUNTIME_CAS": (
        "write_commit_ref", "write_blob_sha", "readback_blob_sha",
        "stale_conflict_status",
    ),
    "NATIVE_FINANCIAL_PLUGIN_CLIENT_ACTIVATION": (
        "plugin_id", "release_id", "fresh_chat_session_ref", "tool_invocation_ref",
    ),
    "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW": (
        "review_ref", "reviewed_head_sha", "reviewer_principal", "findings_status",
    ),
    "FINANCIAL_MAIN_BRANCH_HYGIENE": (
        "before_branch_count", "after_branch_names", "archive_tag_count",
        "branch_inventory_ref",
    ),
}


def _valid_ci_attestation(raw: Mapping[str, Any] | None, head_sha: str) -> bool:
    try:
        record = verify_provider_attestation(
            raw, expected_type="ci_run",
            expected_claims={"target_head_sha": head_sha, "conclusion": "success"},
            key_env="FINANCIAL_CI_ATTESTATION_KEY",
            provider_env="FINANCIAL_CI_PROVIDER_ID",
        )
    except FinancialProviderAttestationError:
        return False
    return (
        isinstance(record.get("run_id"), (str, int))
        and bool(str(record.get("run_id")).strip())
        and isinstance(record.get("workflow"), str)
        and bool(record["workflow"].strip())
        and isinstance(record.get("test_count"), int)
        and record["test_count"] > 0
        and isinstance(record.get("coverage_percent"), (int, float))
        and not isinstance(record.get("coverage_percent"), bool)
        and record["coverage_percent"] >= 85
    )


def evaluate_system_acceptance(
    *,
    head_sha: str,
    candidate_proofs: Mapping[str, Mapping[str, Any]] | None = None,
    ci_attestation: Mapping[str, Any] | None = None,
    code_tests_passed: bool = False,
) -> dict[str, Any]:
    """Only signed provider records can close a gate; no verifier callback exists.

    A boolean may describe the local CI step for diagnostics, but it is never
    enough to establish release readiness. Provider keys and owner identity
    are deployment secrets/configuration and are intentionally absent from
    source control and the Skill-only plugin.
    """
    if not isinstance(head_sha, str) or len(head_sha) != 40:
        raise ValueError("FINANCIAL_SYSTEM_HEAD_SHA_REQUIRED")
    proofs = candidate_proofs or {}
    if not isinstance(proofs, Mapping) or set(proofs) - set(SYSTEM_GATES):
        raise ValueError("FINANCIAL_SYSTEM_GATE_IDS_UNKNOWN")
    ci_verified = _valid_ci_attestation(ci_attestation, head_sha)
    results: dict[str, dict[str, Any]] = {}
    try:
        owner = expected_owner_principal()
    except FinancialProviderAttestationError:
        owner = None
    for gate in SYSTEM_GATES:
        raw = proofs.get(gate)
        status = "OPEN__SIGNED_EXTERNAL_EVIDENCE_NOT_VERIFIED"
        reason = "NO_SIGNED_PROVIDER_RECORD"
        if raw is not None:
            try:
                separate_reviewer = gate == "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW"
                record = verify_provider_attestation(
                    raw,
                    expected_type="system_gate",
                    expected_claims={"gate": gate, "target_head_sha": head_sha},
                    key_env=(
                        "FINANCIAL_INDEPENDENT_REVIEW_KEY" if separate_reviewer
                        else "FINANCIAL_PROVIDER_ATTESTATION_KEY"
                    ),
                    provider_env=(
                        "FINANCIAL_INDEPENDENT_REVIEW_PROVIDER_ID" if separate_reviewer
                        else "FINANCIAL_TRUSTED_PROVIDER_ID"
                    ),
                )
                evidence = record.get("evidence")
                if not isinstance(evidence, Mapping):
                    raise FinancialProviderAttestationError("GATE_EVIDENCE_MISSING")
                if record.get("evidence_sha256") != payload_sha256(evidence):
                    raise FinancialProviderAttestationError("GATE_EVIDENCE_DIGEST_MISMATCH")
                missing = [
                    field for field in REQUIRED_GATE_EVIDENCE[gate]
                    if field not in evidence or evidence[field] in (None, "", [])
                ]
                if missing:
                    raise FinancialProviderAttestationError(
                        "GATE_EVIDENCE_FIELDS_MISSING:" + ",".join(missing)
                    )
                if gate == "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW":
                    reviewer = evidence.get("reviewer_principal")
                    if (
                        owner is None or reviewer != record["authenticated_actor"]
                        or reviewer == owner or evidence.get("reviewed_head_sha") != head_sha
                        or record["provider_id"] == os.environ.get("FINANCIAL_TRUSTED_PROVIDER_ID")
                    ):
                        raise FinancialProviderAttestationError("INDEPENDENT_REVIEWER_IDENTITY_OR_HEAD_INVALID")
                status, reason = "VERIFIED_BY_SIGNED_PROVIDER_ATTESTATION", "SIGNED_EXACT_HEAD_EVIDENCE"
            except FinancialProviderAttestationError as exc:
                reason = str(exc)
        results[gate] = {"status": status, "reason": reason}
    not_verified = [
        gate for gate, rec in results.items()
        if rec["status"] != "VERIFIED_BY_SIGNED_PROVIDER_ATTESTATION"
    ]
    if ci_verified:
        code_ci = "PASS__SIGNED_PROVIDER_ATTESTATION"
    elif code_tests_passed is True:
        code_ci = "PASS__LOCAL_JOB_CONTEXT_NOT_SIGNED"
    else:
        code_ci = "NOT_VERIFIED"
    ready = not not_verified and ci_verified
    return {
        "schema_version": GATE_VERSION,
        "product": "financial_writing",
        "target_head_sha": head_sha,
        "code_ci": code_ci,
        "system_status": (
            "ACCEPTED__SIGNED_EXTERNAL_EVIDENCE_VERIFIED"
            if ready else "NOT_READY__REQUIRES_SIGNED_EXTERNAL_EVIDENCE"
        ),
        "gates": results,
        "open_gates": not_verified,
        "ci_attestation_verified": ci_verified,
        "article_editorial_quality": "OUT_OF_SCOPE__NOT_CERTIFIED",
        "caos_mutations_allowed": False,
    }
