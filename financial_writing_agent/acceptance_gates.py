"""Financial system release authority backed by signed provider evidence."""
from __future__ import annotations

from typing import Any, Mapping
import hashlib
import json
import os
from pathlib import Path
import re

from .provider_attestation import (
    FinancialProviderAttestationError,
    expected_owner_principal,
    payload_sha256,
    verify_provider_attestation,
    verify_owner_message,
    verify_owner_change_approval,
    verify_persisted_method_promotion_attestation,
    verify_persisted_method_impact_attestation,
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
GATE_VERSION = "1.2"


def _configured_financial_plugin_identity() -> tuple[str, str]:
    manifest_path = Path(__file__).resolve().parents[1] / "config" / "FINANCIAL_MANIFEST.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        plugin = manifest["client_skill_plugin"]
        plugin_id = plugin["plugin_id"]
        release_id = plugin["release_id"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise FinancialProviderAttestationError(
            "FINANCIAL_PLUGIN_MANIFEST_UNAVAILABLE"
        ) from exc
    if (not isinstance(plugin_id, str) or not plugin_id.startswith("plugins_")
            or not isinstance(release_id, str) or not release_id.startswith("pluginrel_")):
        raise FinancialProviderAttestationError("FINANCIAL_PLUGIN_MANIFEST_IDENTITY_INVALID")
    return plugin_id, release_id


REQUIRED_GATE_EVIDENCE = {
    "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION": (
        "source_ref", "source_sha256", "owner_message_attestation",
        "change_sha256", "owner_confirmation_ref",
        "owner_confirmation_attestation", "owner_principal",
    ),
    "LEGAL_ARTICLE_GRAPH_AND_RECOVERY": (
        "task_id", "previous_state_blob_sha", "resulting_state_blob_sha",
        "recovery_test_ref", "state_readback_sha",
    ),
    "METHOD_KNOWLEDGE_CRUD_AND_IMPACT": (
        "catalog_revision", "change_event_ref", "affected_task_ids",
        "replay_readback_ref", "promotion_challenge", "promotion_attestation",
        "impact_challenge", "impact_attestation",
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
        "branch_inventory_ref", "archive_manifest_sha256", "archive_tags_verified",
        "final_inventory_sha256", "main_protected", "main_requires_pull_request",
        "required_approving_review_count", "main_dismiss_stale_reviews",
        "main_require_last_push_approval", "main_force_push_disabled",
        "main_deletion_disabled", "required_status_checks",
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
    except (FinancialProviderAttestationError, TypeError, ValueError):
        return False
    return (
        isinstance(record.get("run_id"), (str, int))
        and not isinstance(record.get("run_id"), bool)
        and bool(str(record.get("run_id")).strip())
        and isinstance(record.get("workflow"), str)
        and bool(record["workflow"].strip())
        and isinstance(record.get("test_count"), int)
        and not isinstance(record.get("test_count"), bool)
        and record["test_count"] > 0
        and isinstance(record.get("coverage_percent"), (int, float))
        and not isinstance(record.get("coverage_percent"), bool)
        and 85 <= record["coverage_percent"] <= 100
    )


def _validate_gate_evidence(
    gate: str, evidence: Mapping[str, Any], *, head_sha: str,
    authenticated_actor: str, owner_principal: str | None,
) -> None:
    def require(ok: bool, code: str):
        if not ok:
            raise FinancialProviderAttestationError("GATE_EVIDENCE_INVALID:" + code)

    if gate == "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION":
        require(owner_principal is not None
                and evidence.get("owner_principal") == owner_principal,
                "OWNER_PRINCIPAL_MISMATCH")
        source_ref = evidence.get("source_ref")
        require(isinstance(source_ref, str) and bool(source_ref.strip()),
                "OWNER_SOURCE_REF_INVALID")
        source_sha = evidence.get("source_sha256")
        change_sha = evidence.get("change_sha256")
        require(isinstance(source_sha, str)
                and re.fullmatch(r"[a-f0-9]{64}", source_sha) is not None,
                "OWNER_SOURCE_SHA_INVALID")
        require(isinstance(change_sha, str)
                and re.fullmatch(r"[a-f0-9]{64}", change_sha) is not None,
                "OWNER_CHANGE_SHA_INVALID")
        message_attestation = evidence.get("owner_message_attestation")
        require(isinstance(message_attestation, Mapping),
                "OWNER_MESSAGE_ATTESTATION_MISSING")
        try:
            verified_message = verify_owner_message(
                message_attestation, source_ref=source_ref,
            )
        except (FinancialProviderAttestationError, KeyError, TypeError, ValueError) as exc:
            raise FinancialProviderAttestationError(
                "OWNER_MESSAGE_ATTESTATION_INVALID:" + str(exc)
            ) from exc
        require(
            hashlib.sha256(verified_message["text"].encode("utf-8")).hexdigest() == source_sha,
            "OWNER_SOURCE_SHA_MISMATCH",
        )
        approval = evidence.get("owner_confirmation_attestation")
        require(isinstance(approval, Mapping), "OWNER_CHANGE_ATTESTATION_MISSING")
        try:
            verified_approval = verify_owner_change_approval(
                approval, source_sha256=source_sha, change_sha256=change_sha,
            )
        except (FinancialProviderAttestationError, KeyError, TypeError, ValueError) as exc:
            raise FinancialProviderAttestationError(
                "OWNER_CHANGE_ATTESTATION_INVALID:" + str(exc)
            ) from exc
        require(
            evidence.get("owner_confirmation_ref") == verified_approval.get("approval_record_ref"),
            "OWNER_CONFIRMATION_REF_MISMATCH",
        )
    elif gate == "LEGAL_ARTICLE_GRAPH_AND_RECOVERY":
        previous = evidence.get("previous_state_blob_sha")
        resulting = evidence.get("resulting_state_blob_sha")
        require(isinstance(previous, str) and re.fullmatch(r"[a-f0-9]{40}", previous) is not None,
                "PREVIOUS_STATE_SHA_INVALID")
        require(isinstance(resulting, str) and re.fullmatch(r"[a-f0-9]{40}", resulting) is not None
                and evidence.get("state_readback_sha") == resulting,
                "RESULT_STATE_READBACK_MISMATCH")
    elif gate == "METHOD_KNOWLEDGE_CRUD_AND_IMPACT":
        require(isinstance(evidence.get("catalog_revision"), int)
                and not isinstance(evidence.get("catalog_revision"), bool)
                and evidence["catalog_revision"] > 0,
                "METHOD_CATALOG_REVISION_INVALID")
        affected = evidence.get("affected_task_ids")
        require(isinstance(affected, list) and bool(affected)
                and all(isinstance(item, str) and item.strip() for item in affected)
                and len(affected) == len(set(affected)),
                "METHOD_IMPACT_CLOSURE_INVALID")
        promotion_challenge = evidence.get("promotion_challenge")
        impact_challenge = evidence.get("impact_challenge")
        require(isinstance(promotion_challenge, Mapping), "METHOD_PROMOTION_CHALLENGE_MISSING")
        require(isinstance(impact_challenge, Mapping), "METHOD_IMPACT_CHALLENGE_MISSING")
        require(isinstance(promotion_challenge.get("knowledge_id"), str)
                and bool(promotion_challenge["knowledge_id"].strip()),
                "METHOD_PROMOTION_KNOWLEDGE_ID_INVALID")
        require(re.fullmatch(r"[a-f0-9]{64}", str(promotion_challenge.get("record_sha256", ""))) is not None
                and re.fullmatch(r"[a-f0-9]{64}", str(promotion_challenge.get("decision_sha256", ""))) is not None,
                "METHOD_PROMOTION_DIGEST_INVALID")
        require(isinstance(promotion_challenge.get("validation_refs"), list)
                and bool(promotion_challenge["validation_refs"])
                and all(isinstance(item, str) and item.strip() for item in promotion_challenge["validation_refs"])
                and isinstance(promotion_challenge.get("review_ref"), str)
                and bool(promotion_challenge["review_ref"].strip()),
                "METHOD_PROMOTION_REVIEW_SCOPE_INVALID")
        require(
            impact_challenge.get("knowledge_id") == promotion_challenge.get("knowledge_id"),
            "METHOD_PROMOTION_IMPACT_KNOWLEDGE_ID_MISMATCH",
        )
        require(isinstance(impact_challenge.get("knowledge_id"), str)
                and bool(impact_challenge["knowledge_id"].strip())
                and isinstance(impact_challenge.get("target_change_revision"), int)
                and not isinstance(impact_challenge.get("target_change_revision"), bool)
                and impact_challenge["target_change_revision"] > 0
                and re.fullmatch(r"[a-f0-9]{64}", str(impact_challenge.get("event_sha256", ""))) is not None,
                "METHOD_IMPACT_CHALLENGE_INVALID")
        stage_evidence = impact_challenge.get("stage_evidence_refs")
        require(isinstance(stage_evidence, Mapping) and bool(stage_evidence)
                and all(isinstance(key, str) and key.strip()
                        and isinstance(value, str) and value.strip()
                        for key, value in stage_evidence.items()),
                "METHOD_IMPACT_STAGE_EVIDENCE_INVALID")
        try:
            verify_persisted_method_promotion_attestation(
                evidence.get("promotion_attestation"), challenge=promotion_challenge,
            )
            verify_persisted_method_impact_attestation(
                evidence.get("impact_attestation"), challenge=impact_challenge,
            )
        except (FinancialProviderAttestationError, KeyError, TypeError, ValueError) as exc:
            raise FinancialProviderAttestationError(
                "METHOD_INDEPENDENT_REVIEW_ATTESTATION_INVALID:" + str(exc)
            ) from exc
    elif gate == "PROVIDER_AUTHENTICATED_RUNTIME_CAS":
        require(isinstance(evidence.get("write_blob_sha"), str)
                and re.fullmatch(r"[a-f0-9]{40}", evidence["write_blob_sha"]) is not None
                and evidence.get("write_blob_sha") == evidence.get("readback_blob_sha"),
                "CAS_WRITE_READBACK_MISMATCH")
        require(type(evidence.get("stale_conflict_status")) is int
                and evidence.get("stale_conflict_status") == 409,
                "CAS_STALE_WRITE_NOT_REJECTED")
    elif gate == "NATIVE_FINANCIAL_PLUGIN_CLIENT_ACTIVATION":
        expected_plugin_id, expected_release_id = _configured_financial_plugin_identity()
        require(evidence.get("plugin_id") == expected_plugin_id,
                "NATIVE_FINANCIAL_PLUGIN_ID_MISMATCH")
        require(evidence.get("release_id") == expected_release_id,
                "NATIVE_FINANCIAL_PLUGIN_RELEASE_MISMATCH")
        require(isinstance(evidence.get("fresh_chat_session_ref"), str)
                and bool(evidence["fresh_chat_session_ref"].strip())
                and isinstance(evidence.get("tool_invocation_ref"), str)
                and bool(evidence["tool_invocation_ref"].strip()),
                "NATIVE_PLUGIN_RELEASE_OR_INVOCATION_IDENTITY_MISSING")
    elif gate == "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW":
        require(authenticated_actor != owner_principal
                and evidence.get("reviewer_principal") == authenticated_actor,
                "INDEPENDENT_REVIEWER_NOT_SEPARATE")
        require(evidence.get("reviewed_head_sha") == head_sha,
                "INDEPENDENT_REVIEW_HEAD_MISMATCH")
        require(evidence.get("findings_status") in {
            "PASS", "PASS_WITH_NONBLOCKING_FINDINGS",
        }, "INDEPENDENT_REVIEW_HAS_BLOCKING_FINDINGS")
    elif gate == "FINANCIAL_MAIN_BRANCH_HYGIENE":
        names = evidence.get("after_branch_names")
        require(names == ["main"], "REMOTE_REPOSITORY_NOT_SINGLE_MAIN")
        before = evidence.get("before_branch_count")
        archived = evidence.get("archive_tag_count")
        require(type(before) is int and before >= 1
                and type(archived) is int and archived == before - 1,
                "HISTORICAL_BRANCH_HEADS_NOT_FULLY_ARCHIVED")
        require(re.fullmatch(r"[a-f0-9]{64}", str(evidence.get("archive_manifest_sha256", ""))) is not None,
                "ARCHIVE_MANIFEST_DIGEST_INVALID")
        require(evidence.get("archive_tags_verified") is True,
                "ARCHIVE_TAG_READBACK_NOT_VERIFIED")
        require(re.fullmatch(r"[a-f0-9]{64}", str(evidence.get("final_inventory_sha256", ""))) is not None,
                "FINAL_BRANCH_INVENTORY_DIGEST_INVALID")
        require(evidence.get("main_protected") is True,
                "MAIN_BRANCH_NOT_PROTECTED")
        require(evidence.get("main_requires_pull_request") is True,
                "MAIN_PULL_REQUEST_REQUIRED_RULE_MISSING")
        approvals = evidence.get("required_approving_review_count")
        require(type(approvals) is int and approvals >= 1,
                "MAIN_INDEPENDENT_APPROVAL_REQUIRED")
        require(evidence.get("main_dismiss_stale_reviews") is True,
                "MAIN_STALE_REVIEWS_NOT_DISMISSED")
        require(evidence.get("main_require_last_push_approval") is True,
                "MAIN_LAST_PUSH_APPROVAL_REQUIRED")
        require(evidence.get("main_force_push_disabled") is True,
                "MAIN_FORCE_PUSH_NOT_DISABLED")
        require(evidence.get("main_deletion_disabled") is True,
                "MAIN_DELETION_NOT_DISABLED")
        checks = evidence.get("required_status_checks")
        require(isinstance(checks, list) and "test" in checks,
                "MAIN_FINANCIAL_CI_REQUIRED_CHECK_MISSING")


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
    if not isinstance(head_sha, str) or re.fullmatch(r"[a-f0-9]{40}", head_sha) is None:
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
                if owner is None:
                    raise FinancialProviderAttestationError("FINANCIAL_EXPECTED_OWNER_NOT_CONFIGURED")
                if not separate_reviewer and record.get("authenticated_actor") != owner:
                    raise FinancialProviderAttestationError("SYSTEM_GATE_ACTOR_MUST_MATCH_OWNER")
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
                if gate == "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW" and (
                    record["provider_id"] == os.environ.get("FINANCIAL_TRUSTED_PROVIDER_ID")
                ):
                    raise FinancialProviderAttestationError("INDEPENDENT_REVIEW_PROVIDER_NOT_SEPARATE")
                _validate_gate_evidence(
                    gate, evidence, head_sha=head_sha,
                    authenticated_actor=record["authenticated_actor"],
                    owner_principal=owner,
                )
                status, reason = "VERIFIED_BY_SIGNED_PROVIDER_ATTESTATION", "SIGNED_EXACT_HEAD_EVIDENCE"
            except (FinancialProviderAttestationError, KeyError, TypeError, ValueError) as exc:
                reason = str(exc) or type(exc).__name__
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
