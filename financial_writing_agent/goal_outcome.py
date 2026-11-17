"""Independent final verification of the user's actual writing outcome.

This is deliberately separate from stage PASS receipts and PublicationFitness.
A terminal article state requires a trusted reviewer to assess every active
user requirement against the exact current deliverable set.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

from .provider_attestation import (
    FinancialProviderAttestationError,
    expected_owner_principal,
    payload_sha256,
    verify_provider_attestation,
)
from .models import Stage
from .task_requirements import validate_requirement_authority
from .workflow_spec import revision_targets


GOAL_REVIEW_KEY_ENV = "FINANCIAL_GOAL_REVIEW_KEY"
GOAL_REVIEW_PROVIDER_ENV = "FINANCIAL_GOAL_REVIEW_PROVIDER_ID"
GOAL_REVIEW_REVISION_TARGETS = {
    item.value for item in revision_targets(Stage.FINAL_AUDIT)
}


class GoalOutcomeError(ValueError):
    pass


def article_deliverable_manifest(state: Mapping[str, Any]) -> list[dict[str, str]]:
    required = [
        str(item) for item in state.get("required_outputs", [])
        if str(item) != "AUDIT_DOCX"
    ]
    artifacts = state.get("delivery_artifacts", {})
    if not isinstance(artifacts, Mapping):
        raise GoalOutcomeError("GOAL_OUTCOME_DELIVERY_ARTIFACTS_INVALID")
    manifest: list[dict[str, str]] = []
    for kind in sorted(required):
        item = artifacts.get(kind)
        if not isinstance(item, Mapping):
            raise GoalOutcomeError(f"GOAL_OUTCOME_REQUIRED_DELIVERABLE_MISSING:{kind}")
        fields = {
            "kind": kind,
            "file_name": str(item.get("file_name", "")),
            "resource_ref": str(item.get("resource_ref", "")),
            "sha256": str(item.get("sha256", "")),
            "delivery_evidence_sha256": str(item.get("delivery_evidence_sha256", "")),
        }
        if any(not value for value in fields.values()):
            raise GoalOutcomeError(f"GOAL_OUTCOME_DELIVERABLE_IDENTITY_INCOMPLETE:{kind}")
        if len(fields["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in fields["sha256"]):
            raise GoalOutcomeError(f"GOAL_OUTCOME_DELIVERABLE_SHA_INVALID:{kind}")
        if len(fields["delivery_evidence_sha256"]) != 64 or any(c not in "0123456789abcdef" for c in fields["delivery_evidence_sha256"]):
            raise GoalOutcomeError(f"GOAL_OUTCOME_DELIVERY_EVIDENCE_SHA_INVALID:{kind}")
        manifest.append(fields)
    expected = set(required)
    actual = set(artifacts) - {"AUDIT_DOCX"}
    if actual != expected:
        raise GoalOutcomeError(
            f"GOAL_OUTCOME_DELIVERABLE_SET_MISMATCH:missing={sorted(expected-actual)};"
            f"unexpected={sorted(actual-expected)}"
        )
    if "AUDIT_DOCX" not in state.get("required_outputs", []):
        raise GoalOutcomeError("GOAL_OUTCOME_AUDIT_OUTPUT_CONTRACT_MISSING")
    return manifest


def article_deliverables_sha256(state: Mapping[str, Any]) -> str:
    return payload_sha256(article_deliverable_manifest(state))




def _validate_success_criteria_results(
    verified: Mapping[str, Any],
    *,
    intake_manifest: Mapping[str, Any],
) -> list[str]:
    criteria = intake_manifest.get("success_criteria", [])
    if not isinstance(criteria, list) or not criteria:
        raise FinancialProviderAttestationError("GOAL_REVIEW_SUCCESS_CRITERIA_MISSING")
    expected_ids = sorted(
        str(item.get("criterion_id", ""))
        for item in criteria if isinstance(item, Mapping)
    )
    if len(expected_ids) != len(criteria) or any(not item for item in expected_ids):
        raise FinancialProviderAttestationError("GOAL_REVIEW_SUCCESS_CRITERIA_INVALID")
    results = verified.get("success_criteria_results")
    if not isinstance(results, list):
        raise FinancialProviderAttestationError("GOAL_REVIEW_SUCCESS_CRITERIA_RESULTS_MISSING")
    ids = [
        item.get("criterion_id")
        for item in results if isinstance(item, Mapping)
    ]
    if len(ids) != len(results) or sorted(ids) != expected_ids or len(ids) != len(set(ids)):
        raise FinancialProviderAttestationError("GOAL_REVIEW_SUCCESS_CRITERIA_SET_MISMATCH")
    for item in results:
        if item.get("result") not in {"SATISFIED", "NOT_SATISFIED"}:
            raise FinancialProviderAttestationError("GOAL_REVIEW_SUCCESS_CRITERION_RESULT_INVALID")
        refs = item.get("evidence_refs")
        if not isinstance(refs, list) or not refs or any(
            not isinstance(ref, str) or not ref.strip() for ref in refs
        ):
            raise FinancialProviderAttestationError("GOAL_REVIEW_SUCCESS_CRITERION_EVIDENCE_REQUIRED")
    if verified.get("success_criteria_results_sha256") != payload_sha256(results):
        raise FinancialProviderAttestationError("GOAL_REVIEW_SUCCESS_CRITERIA_DIGEST_MISMATCH")
    unmet = sorted(
        item["criterion_id"] for item in results
        if item["result"] == "NOT_SATISFIED"
    )
    if verified.get("unmet_success_criterion_ids") != unmet:
        raise FinancialProviderAttestationError("GOAL_REVIEW_UNMET_SUCCESS_CRITERIA_MISMATCH")
    return unmet

def build_goal_outcome_challenge(
    state: Mapping[str, Any],
    *,
    deliverable_texts: list[Mapping[str, Any]],
    visible_delivery_receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    authority = validate_requirement_authority(state.get("task_requirement_authority"))
    intake_manifest = state.get("task_intake_manifest")
    if not isinstance(intake_manifest, Mapping):
        raise GoalOutcomeError("GOAL_OUTCOME_TASK_INTAKE_MANIFEST_MISSING")
    requirements = list(authority["active_requirements"])
    if state.get("current_stage") != "FINAL_AUDIT" or state.get("status") != "IN_PROGRESS":
        raise GoalOutcomeError("GOAL_OUTCOME_FINAL_AUDIT_STATE_REQUIRED")
    if state.get("task_requirement_digest") != payload_sha256(authority):
        raise GoalOutcomeError("GOAL_OUTCOME_REQUIREMENT_DIGEST_MISMATCH")
    if not isinstance(intake_manifest, Mapping) or payload_sha256(intake_manifest) != state.get("task_intake_manifest_sha256"):
        raise GoalOutcomeError("GOAL_OUTCOME_INTAKE_MANIFEST_DIGEST_MISMATCH")
    deliverables = article_deliverable_manifest(state)
    texts_by_kind = {
        str(item.get("kind")): item for item in deliverable_texts
        if isinstance(item, Mapping)
    }
    if set(texts_by_kind) != {item["kind"] for item in deliverables}:
        raise GoalOutcomeError("GOAL_OUTCOME_DELIVERABLE_TEXT_SET_MISMATCH")
    for item in deliverables:
        text_record = texts_by_kind[item["kind"]]
        if (
            text_record.get("resource_ref") != item["resource_ref"]
            or text_record.get("sha256") != item["sha256"]
            or not isinstance(text_record.get("text"), str)
            or not text_record["text"].strip()
        ):
            raise GoalOutcomeError(f"GOAL_OUTCOME_DELIVERABLE_TEXT_BINDING_INVALID:{item['kind']}")
    return {
        "review_scope": "FINAL_USER_GOAL_OUTCOME",
        "task_id": state["task_id"],
        "original_user_prompt": state["prompt"],
        "source_prompt_sha256": __import__("hashlib").sha256(
            state["prompt"].encode("utf-8")
        ).hexdigest(),
        "task_intake_manifest": intake_manifest,
        "task_intake_manifest_sha256": state.get("task_intake_manifest_sha256"),
        "success_criteria": intake_manifest.get("success_criteria", []),
        "task_requirement_authority": authority,
        "task_requirement_digest": state.get("task_requirement_digest"),
        "required_outputs": list(state.get("required_outputs", [])),
        "requirements": requirements,
        "requirement_stage_evidence": [
            {
                "stage": receipt.get("stage"),
                "satisfaction": receipt.get("input_bindings", {}).get("task_requirement_satisfaction", []),
            }
            for receipt in state.get("execution_receipts", [])
            if isinstance(receipt, Mapping)
        ],
        "research_artifact_ref": state.get("stage_artifacts", {}).get("RESEARCH"),
        "draft_artifact_ref": state.get("stage_artifacts", {}).get("DRAFT"),
        "article_deliverables": [
            {
                **item,
                "text": texts_by_kind[item["kind"]]["text"],
            }
            for item in deliverables
        ],
        "article_deliverables_sha256": payload_sha256(deliverables),
        "visible_delivery_receipt": dict(visible_delivery_receipt or {}),
        "review_instructions": [
            "Evaluate the actual delivered article text, not stage labels or model self-reports.",
            "Assess every active user requirement, preserving its scope and source authority.",
            "Evaluate every success criterion separately against the actual delivered files.",
            "Check title promise, opening payoff, company-level causal economics, reader value and Deep/Broad differentiation where requested.",
            "Check factual entailment against current primary-source evidence, not only source hashes or citations.",
            "Check originality, natural authorial prose, visual Word quality and exact user-accessible delivery.",
            "Check process requirements against their admitted stage artifacts and evidence references.",
            "Identify omitted, weakened, contradicted or merely asserted requirements.",
            "Do not infer user acceptance; report only independently assessed requirement outcomes.",
        ],
    }


def verify_goal_outcome_review(
    raw: Mapping[str, Any] | None,
    *,
    state: Mapping[str, Any],
    historical: bool = False,
) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise GoalOutcomeError("GOAL_OUTCOME_INDEPENDENT_REVIEW_REQUIRED")
    authority = validate_requirement_authority(state.get("task_requirement_authority"))
    if state.get("current_stage") != "FINAL_AUDIT" or state.get("status") != "IN_PROGRESS":
        raise GoalOutcomeError("GOAL_OUTCOME_FINAL_AUDIT_STATE_REQUIRED")
    expected_ids = sorted(item["requirement_id"] for item in authority["active_requirements"])
    if state.get("task_requirement_digest") != payload_sha256(authority):
        raise GoalOutcomeError("GOAL_OUTCOME_REQUIREMENT_DIGEST_MISMATCH")
    intake_manifest = state.get("task_intake_manifest")
    if not isinstance(intake_manifest, Mapping) or payload_sha256(intake_manifest) != state.get("task_intake_manifest_sha256"):
        raise GoalOutcomeError("GOAL_OUTCOME_INTAKE_MANIFEST_DIGEST_MISMATCH")
    expected_claims = {
        "approved": True,
        "review_scope": "FINAL_USER_GOAL_OUTCOME",
        "task_id": state["task_id"],
        "source_prompt_sha256": __import__("hashlib").sha256(
            state["prompt"].encode("utf-8")
        ).hexdigest(),
        "task_intake_manifest_sha256": state.get("task_intake_manifest_sha256"),
        "task_requirement_digest": state.get("task_requirement_digest"),
        "article_deliverables_sha256": article_deliverables_sha256(state),
    }
    try:
        verified = verify_provider_attestation(
            raw,
            expected_type="independent_goal_outcome_review",
            expected_claims=expected_claims,
            key_env=GOAL_REVIEW_KEY_ENV,
            provider_env=GOAL_REVIEW_PROVIDER_ENV,
            max_age_seconds=None if historical else 300,
        )
        owner = expected_owner_principal()
        if verified["authenticated_actor"] == owner:
            raise FinancialProviderAttestationError("GOAL_REVIEWER_MUST_DIFFER_FROM_OWNER")
        if verified["provider_id"] == os.environ.get("FINANCIAL_TRUSTED_PROVIDER_ID"):
            raise FinancialProviderAttestationError("GOAL_REVIEW_PROVIDER_NOT_INDEPENDENT")
        results = verified.get("requirement_results")
        if not isinstance(results, list):
            raise FinancialProviderAttestationError("GOAL_REVIEW_REQUIREMENT_RESULTS_MISSING")
        ids = [item.get("requirement_id") for item in results if isinstance(item, Mapping)]
        if len(ids) != len(results) or sorted(ids) != expected_ids or len(ids) != len(set(ids)):
            raise FinancialProviderAttestationError("GOAL_REVIEW_REQUIREMENT_SET_MISMATCH")
        for item in results:
            if item.get("result") not in {"SATISFIED", "NOT_SATISFIED"}:
                raise FinancialProviderAttestationError("GOAL_REVIEW_REQUIREMENT_RESULT_INVALID")
            refs = item.get("evidence_refs")
            if not isinstance(refs, list) or not refs or any(
                not isinstance(ref, str) or not ref.strip() for ref in refs
            ):
                raise FinancialProviderAttestationError("GOAL_REVIEW_REQUIREMENT_EVIDENCE_REQUIRED")
        if verified.get("requirement_results_sha256") != payload_sha256(results):
            raise FinancialProviderAttestationError("GOAL_REVIEW_REQUIREMENT_RESULTS_DIGEST_MISMATCH")
        if verified.get("uncovered_material_requirement_ids") != []:
            raise FinancialProviderAttestationError("GOAL_REVIEW_UNCOVERED_REQUIREMENTS_REMAIN")
        unmet_success = _validate_success_criteria_results(
            verified, intake_manifest=intake_manifest,
        )
        if not isinstance(verified.get("review_summary"), str) or not verified["review_summary"].strip():
            raise FinancialProviderAttestationError("GOAL_REVIEW_SUMMARY_REQUIRED")
        unmet = sorted(
            item["requirement_id"] for item in results
            if item["result"] != "SATISFIED"
        )
        if verified.get("unmet_requirement_ids") != unmet:
            raise FinancialProviderAttestationError("GOAL_REVIEW_UNMET_REQUIREMENT_SET_MISMATCH")
        decision = verified.get("decision")
        revision_target = verified.get("revision_target")
        if decision == "PASS":
            if unmet or unmet_success or revision_target is not None:
                raise FinancialProviderAttestationError("GOAL_REVIEW_FALSE_PASS")
        elif decision == "REVISE":
            if not (unmet or unmet_success) or revision_target not in GOAL_REVIEW_REVISION_TARGETS:
                raise FinancialProviderAttestationError("GOAL_REVIEW_REVISION_ROUTE_INVALID")
        elif decision == "FAIL":
            if not (unmet or unmet_success) or revision_target is not None:
                raise FinancialProviderAttestationError("GOAL_REVIEW_FAILURE_ROUTE_INVALID")
        else:
            raise FinancialProviderAttestationError("GOAL_REVIEW_DECISION_INVALID")
    except Exception as exc:
        raise GoalOutcomeError("GOAL_OUTCOME_INDEPENDENT_REVIEW_ATTESTATION_INVALID") from exc
    return verified


def verify_persisted_goal_outcome_review(
    raw: Mapping[str, Any] | None,
    *,
    state: Mapping[str, Any] | None = None,
    require_pass: bool = True,
) -> dict[str, Any]:
    """Reverify a retained signature; when state is supplied, bind it to current output."""
    if not isinstance(raw, Mapping):
        raise GoalOutcomeError("GOAL_OUTCOME_PERSISTED_REVIEW_MISSING")
    if state is None:
        expected_claims = {
            "approved": True,
            "review_scope": "FINAL_USER_GOAL_OUTCOME",
            "task_id": raw.get("task_id"),
            "source_prompt_sha256": raw.get("source_prompt_sha256"),
            "task_intake_manifest_sha256": raw.get("task_intake_manifest_sha256"),
            "task_requirement_digest": raw.get("task_requirement_digest"),
            "article_deliverables_sha256": raw.get("article_deliverables_sha256"),
        }
    else:
        authority = validate_requirement_authority(state.get("task_requirement_authority"))
        expected_claims = {
            "approved": True,
            "review_scope": "FINAL_USER_GOAL_OUTCOME",
            "task_id": state.get("task_id"),
            "source_prompt_sha256": __import__("hashlib").sha256(
                str(state.get("prompt", "")).encode("utf-8")
            ).hexdigest(),
            "task_intake_manifest_sha256": state.get("task_intake_manifest_sha256"),
            "task_requirement_digest": state.get("task_requirement_digest"),
            "article_deliverables_sha256": article_deliverables_sha256(state),
        }
        if state.get("task_requirement_digest") != payload_sha256(authority):
            raise GoalOutcomeError("GOAL_OUTCOME_REQUIREMENT_DIGEST_MISMATCH")
        intake_manifest = state.get("task_intake_manifest")
        if not isinstance(intake_manifest, Mapping) or payload_sha256(intake_manifest) != state.get("task_intake_manifest_sha256"):
            raise GoalOutcomeError("GOAL_OUTCOME_INTAKE_MANIFEST_DIGEST_MISMATCH")
    try:
        verified = verify_provider_attestation(
            raw,
            expected_type="independent_goal_outcome_review",
            expected_claims=expected_claims,
            key_env=GOAL_REVIEW_KEY_ENV,
            provider_env=GOAL_REVIEW_PROVIDER_ENV,
            max_age_seconds=None,
        )
        if verified["authenticated_actor"] == expected_owner_principal():
            raise FinancialProviderAttestationError("GOAL_REVIEWER_MUST_DIFFER_FROM_OWNER")
        if verified["provider_id"] == os.environ.get("FINANCIAL_TRUSTED_PROVIDER_ID"):
            raise FinancialProviderAttestationError("GOAL_REVIEW_PROVIDER_NOT_INDEPENDENT")
        results = verified.get("requirement_results")
        if not isinstance(results, list):
            raise FinancialProviderAttestationError("GOAL_REVIEW_REQUIREMENT_RESULTS_MISSING")
        ids = [item.get("requirement_id") for item in results if isinstance(item, Mapping)]
        if len(ids) != len(results) or len(ids) != len(set(ids)):
            raise FinancialProviderAttestationError("GOAL_REVIEW_REQUIREMENT_SET_INVALID")
        intake_manifest = None
        if state is not None:
            expected_ids = sorted(
                item["requirement_id"]
                for item in validate_requirement_authority(
                    state.get("task_requirement_authority")
                )["active_requirements"]
            )
            if sorted(ids) != expected_ids:
                raise FinancialProviderAttestationError("GOAL_REVIEW_REQUIREMENT_SET_MISMATCH")
            intake_manifest = state.get("task_intake_manifest")
            if not isinstance(intake_manifest, Mapping):
                raise FinancialProviderAttestationError("GOAL_REVIEW_INTAKE_MANIFEST_MISSING")
        if verified.get("requirement_results_sha256") != payload_sha256(results):
            raise FinancialProviderAttestationError("GOAL_REVIEW_REQUIREMENT_RESULTS_DIGEST_MISMATCH")
        if any(
            not isinstance(item.get("requirement_id"), str)
            or not item["requirement_id"].strip()
            or not isinstance(item.get("evidence_refs"), list)
            or not item["evidence_refs"]
            or any(not isinstance(ref, str) or not ref.strip() for ref in item["evidence_refs"])
            for item in results
        ):
            raise FinancialProviderAttestationError("GOAL_REVIEW_REQUIREMENT_EVIDENCE_REQUIRED")
        if verified.get("uncovered_material_requirement_ids") != []:
            raise FinancialProviderAttestationError("GOAL_REVIEW_UNCOVERED_REQUIREMENTS_REMAIN")
        if not isinstance(verified.get("review_summary"), str) or not verified["review_summary"].strip():
            raise FinancialProviderAttestationError("GOAL_REVIEW_SUMMARY_REQUIRED")
        unmet = sorted(
            item.get("requirement_id")
            for item in results
            if item.get("result") == "NOT_SATISFIED"
        )
        if any(item.get("result") not in {"SATISFIED", "NOT_SATISFIED"} for item in results):
            raise FinancialProviderAttestationError("GOAL_REVIEW_REQUIREMENT_RESULT_INVALID")
        if verified.get("unmet_requirement_ids") != unmet:
            raise FinancialProviderAttestationError("GOAL_REVIEW_UNMET_REQUIREMENT_SET_MISMATCH")
        if intake_manifest is not None:
            unmet_success = _validate_success_criteria_results(
                verified, intake_manifest=intake_manifest,
            )
        else:
            criteria_results = verified.get("success_criteria_results")
            if not isinstance(criteria_results, list) or not criteria_results:
                raise FinancialProviderAttestationError("GOAL_REVIEW_SUCCESS_CRITERIA_RESULTS_MISSING")
            criteria_ids = [
                item.get("criterion_id") for item in criteria_results
                if isinstance(item, Mapping)
            ]
            if len(criteria_ids) != len(criteria_results) or len(criteria_ids) != len(set(criteria_ids)) or any(
                not isinstance(item.get("criterion_id"), str)
                or not item["criterion_id"].strip()
                or not isinstance(item.get("evidence_refs"), list)
                or not item["evidence_refs"]
                or any(not isinstance(ref, str) or not ref.strip() for ref in item["evidence_refs"])
                for item in criteria_results
            ):
                raise FinancialProviderAttestationError("GOAL_REVIEW_SUCCESS_CRITERIA_SET_INVALID")
            if verified.get("success_criteria_results_sha256") != payload_sha256(criteria_results):
                raise FinancialProviderAttestationError("GOAL_REVIEW_SUCCESS_CRITERIA_DIGEST_MISMATCH")
            unmet_success = sorted(
                item.get("criterion_id") for item in criteria_results
                if item.get("result") == "NOT_SATISFIED"
            )
            if any(item.get("result") not in {"SATISFIED", "NOT_SATISFIED"} for item in criteria_results):
                raise FinancialProviderAttestationError("GOAL_REVIEW_SUCCESS_CRITERION_RESULT_INVALID")
            if verified.get("unmet_success_criterion_ids") != unmet_success:
                raise FinancialProviderAttestationError("GOAL_REVIEW_UNMET_SUCCESS_CRITERIA_MISMATCH")
        if verified.get("uncovered_material_requirement_ids") != []:
            raise FinancialProviderAttestationError("GOAL_REVIEW_UNCOVERED_REQUIREMENTS_REMAIN")
        if not isinstance(verified.get("review_summary"), str) or not verified["review_summary"].strip():
            raise FinancialProviderAttestationError("GOAL_REVIEW_SUMMARY_REQUIRED")
        if require_pass:
            if any(item.get("result") != "SATISFIED" for item in results) or unmet_success:
                raise FinancialProviderAttestationError("GOAL_REVIEW_ACTIVE_PASS_CONTAINS_UNMET_REQUIREMENTS")
            if verified.get("decision") != "PASS" or verified.get("revision_target") is not None:
                raise FinancialProviderAttestationError("GOAL_REVIEW_ACTIVE_PROOF_NOT_PASS")
        else:
            decision = verified.get("decision")
            target = verified.get("revision_target")
            if decision == "PASS" and (unmet or unmet_success or target is not None):
                raise FinancialProviderAttestationError("GOAL_REVIEW_HISTORICAL_PASS_INVALID")
            if decision == "REVISE" and (not (unmet or unmet_success) or target not in GOAL_REVIEW_REVISION_TARGETS):
                raise FinancialProviderAttestationError("GOAL_REVIEW_HISTORICAL_REVISION_INVALID")
            if decision == "FAIL" and (not (unmet or unmet_success) or target is not None):
                raise FinancialProviderAttestationError("GOAL_REVIEW_HISTORICAL_FAILURE_INVALID")
            if decision not in {"PASS", "REVISE", "FAIL"}:
                raise FinancialProviderAttestationError("GOAL_REVIEW_HISTORICAL_DECISION_INVALID")
    except Exception as exc:
        raise GoalOutcomeError("GOAL_OUTCOME_PERSISTED_REVIEW_INVALID") from exc
    return verified
