"""Financial-owned method knowledge lifecycle, using the existing catalog.

No second domain task ledger, no CAOS runtime, and no destructive deletion of
historical source evidence. An adopted method is a *versioned* effective record:
revisions are staged, challenged methods are not operationally retrievable,
and promotion needs an independent provider-verification callback.
"""
from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from .provider_attestation import (
    expected_owner_principal,
    verify_method_action_authorization,
    verify_method_impact_attestation,
    verify_method_promotion_attestation,
)

from .cognition_governance import (
    DecisionEnvelope, EvidenceKind, OperationClass, admission_errors,
)
from .workflow_spec import BUSINESS_STAGE_NAMES

CATALOG_PATH = "knowledge/METHOD_KNOWLEDGE_CATALOG.json"
METHOD_ACTIONS = frozenset({
    "CREATE", "REVISE", "DISCARD_PENDING", "PROMOTE",
    "CHALLENGE", "RETIRE", "RESTORE", "VERIFY_IMPACT",
})
METHOD_STATUSES = frozenset({
    "LEGACY_DECLARED", "CANDIDATE", "ACTIVE", "CHALLENGED", "RETIRED",
})
METHOD_FIELDS = frozenset({
    "knowledge_id", "category", "method", "source_refs", "fit",
    "misfit", "adoption", "revalidation_trigger",
})
_METHOD_ID = re.compile(r"METHOD-[A-Z0-9][A-Z0-9_-]{0,120}\Z")


class MethodGovernanceError(ValueError):
    pass


def _require(ok: bool, reason: str) -> None:
    if not ok:
        raise MethodGovernanceError("FINANCIAL_METHOD_" + reason)


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _record_data(raw: Any) -> dict[str, Any]:
    _require(isinstance(raw, Mapping), "RECORD_REQUIRED")
    _require(set(raw) == METHOD_FIELDS, "RECORD_FIELDS_INVALID")
    obj = deepcopy(dict(raw))
    _require(isinstance(obj["knowledge_id"], str)
             and _METHOD_ID.fullmatch(obj["knowledge_id"]) is not None, "ID_INVALID")
    for key in METHOD_FIELDS - {"knowledge_id", "source_refs"}:
        _require(isinstance(obj[key], str) and bool(obj[key].strip()),
                 f"RECORD_{key.upper()}_REQUIRED")
    refs = obj["source_refs"]
    _require(isinstance(refs, list) and bool(refs)
             and all(isinstance(ref, str) and bool(ref.strip()) for ref in refs),
             "SOURCE_REFS_REQUIRED")
    _require(len(refs) == len(set(refs)), "DUPLICATE_SOURCE_REF")
    return obj


def validate_method_catalog(raw: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(raw, Mapping), "CATALOG_REQUIRED")
    catalog = deepcopy(dict(raw))
    _require(catalog.get("schema_version") == "1.0", "CATALOG_VERSION_UNSUPPORTED")
    records = catalog.get("records")
    _require(isinstance(records, list), "CATALOG_RECORDS_INVALID")
    seen: set[str] = set()
    for rec in records:
        _require(isinstance(rec, Mapping), "CATALOG_RECORD_INVALID")
        data = _record_data({key: rec.get(key) for key in METHOD_FIELDS})
        ident = data["knowledge_id"]
        _require(ident not in seen, "DUPLICATE_RECORD_ID")
        seen.add(ident)
        status = rec.get("lifecycle_status", "LEGACY_DECLARED")
        _require(status in METHOD_STATUSES, f"INVALID_STATUS:{ident}")
        revision = rec.get("method_revision", 0)
        _require(type(revision) is int and revision >= 0, "RECORD_REVISION_INVALID")
        pending = rec.get("pending_revision")
        if pending is not None:
            _require(status != "RETIRED", "RETIRED_HAS_PENDING_REVISION")
            _require(_record_data(pending)["knowledge_id"] == ident,
                     "PENDING_RECORD_ID_MISMATCH")
    rev = catalog.get("governance_revision", 0)
    history = catalog.get("change_history", [])
    _require(type(rev) is int and rev >= 0, "CATALOG_REVISION_INVALID")
    _require(isinstance(history, list) and len(history) == rev,
             "CATALOG_HISTORY_REVISION_MISMATCH")
    seen_action_ids: set[str] = set()
    seen_attestation_nonces: set[tuple[str, str]] = set()
    for index, item in enumerate(history, 1):
        _require(isinstance(item, Mapping) and item.get("revision") == index,
                 "CATALOG_HISTORY_SEQUENCE_INVALID")
        _require(item.get("knowledge_id") in seen and item.get("operation") in METHOD_ACTIONS,
                 "CATALOG_HISTORY_EVENT_INVALID")
        auth = item.get("authorization_evidence")
        action_request = item.get("authorization_request")
        _require(isinstance(auth, Mapping), "CATALOG_ACTION_ATTESTATION_MISSING")
        _require(isinstance(action_request, Mapping), "CATALOG_ACTION_REQUEST_MISSING")
        _require(isinstance(auth.get("action_id"), str)
                 and auth["action_id"] not in seen_action_ids,
                 "CATALOG_ACTION_ID_MISSING_OR_REPLAYED")
        seen_action_ids.add(auth["action_id"])
        action_nonce = auth.get("nonce")
        _require(isinstance(action_nonce, str)
                 and (auth.get("provider_id"), action_nonce) not in seen_attestation_nonces,
                 "CATALOG_ACTION_NONCE_MISSING_OR_REPLAYED")
        seen_attestation_nonces.add((auth.get("provider_id"), action_nonce))
        try:
            verified_auth = verify_method_action_authorization(auth, request=action_request)
        except Exception as exc:
            raise MethodGovernanceError("FINANCIAL_METHOD_CATALOG_ACTION_ATTESTATION_INVALID") from exc
        _require(action_request.get("operation") == item.get("operation")
                 and action_request.get("parameters", {}).get("knowledge_id") == item.get("knowledge_id")
                 and action_request.get("action_id") == item.get("authorization_action_id")
                 and action_request.get("expected_catalog_blob_sha") == item.get("authorization_expected_catalog_blob_sha"),
                 "CATALOG_ACTION_REQUEST_EVENT_BINDING_MISMATCH")
        if item.get("operation") == "PROMOTE":
            promoted = item.get("promoted_proof")
            _require(isinstance(promoted, Mapping)
                     and isinstance(promoted.get("attestation"), Mapping),
                     "CATALOG_PROMOTION_ATTESTATION_MISSING")
            challenge = {
                "knowledge_id": item["knowledge_id"],
                "record_sha256": promoted.get("reviewed_record_sha256"),
                "decision_sha256": item.get("decision_sha256"),
                "validation_refs": promoted.get("validation_refs"),
                "review_ref": promoted.get("review_ref"),
            }
            try:
                verified_promotion = verify_method_promotion_attestation(
                    promoted["attestation"], challenge=challenge,
                )
            except Exception as exc:
                raise MethodGovernanceError("FINANCIAL_METHOD_CATALOG_PROMOTION_ATTESTATION_INVALID") from exc
            _require(verified_promotion["authenticated_actor"] == promoted.get("reviewer_principal"),
                     "CATALOG_PROMOTION_REVIEWER_MISMATCH")
            review_nonce = (verified_promotion["provider_id"], verified_promotion["nonce"])
            _require(review_nonce not in seen_attestation_nonces,
                     "CATALOG_REVIEW_ATTESTATION_NONCE_REPLAYED")
            seen_attestation_nonces.add(review_nonce)
        if item.get("operation") == "VERIFY_IMPACT":
            impact = item.get("impact_verification")
            _require(isinstance(impact, Mapping)
                     and isinstance(impact.get("attestation"), Mapping),
                     "CATALOG_IMPACT_ATTESTATION_MISSING")
            challenge = {
                "knowledge_id": item["knowledge_id"],
                "target_change_revision": item.get("target_change_revision"),
                "event_sha256": impact.get("reviewed_event_sha256"),
                "stage_evidence_refs": impact.get("stage_evidence_refs"),
            }
            try:
                verified_impact = verify_method_impact_attestation(
                    impact["attestation"], challenge=challenge,
                )
            except Exception as exc:
                raise MethodGovernanceError("FINANCIAL_METHOD_CATALOG_IMPACT_ATTESTATION_INVALID") from exc
            _require(verified_impact["authenticated_actor"] == impact.get("reviewer_principal"),
                     "CATALOG_IMPACT_REVIEWER_MISMATCH")
            review_nonce = (verified_impact["provider_id"], verified_impact["nonce"])
            _require(review_nonce not in seen_attestation_nonces,
                     "CATALOG_REVIEW_ATTESTATION_NONCE_REPLAYED")
            seen_attestation_nonces.add(review_nonce)
    return catalog


def query_methods(
    catalog: Mapping[str, Any],
    *,
    knowledge_id: str | None = None,
    operational_only: bool = False,
    category: str | None = None,
) -> list[dict[str, Any]]:
    checked = validate_method_catalog(catalog)
    out: list[dict[str, Any]] = []
    for raw in checked["records"]:
        rec = dict(raw)
        rec.setdefault("lifecycle_status", "LEGACY_DECLARED")
        if knowledge_id is not None and rec["knowledge_id"] != knowledge_id:
            continue
        if category is not None and rec["category"] != category:
            continue
        if operational_only and rec["lifecycle_status"] != "ACTIVE":
            continue
        out.append(deepcopy(rec))
    return out


def _validate_method_decision(
    raw: Mapping[str, Any], evidence_refs: list[str], affected_stages: list[str],
) -> dict[str, Any]:
    _require(isinstance(raw, Mapping), "DECISION_REQUIRED")
    try:
        envelope = DecisionEnvelope.model_validate(raw)
    except ValueError as exc:
        raise MethodGovernanceError("FINANCIAL_METHOD_DECISION_INVALID") from exc
    _require(envelope.operation_class is OperationClass.MATERIAL_JUDGMENT,
             "MATERIAL_DECISION_REQUIRED")
    _require(not admission_errors(envelope), "DECISION_EVIDENCE_ADMISSION_FAILED")
    available = {item.ref for item in envelope.evidence}
    kinds = {item.kind for item in envelope.evidence}
    _require(EvidenceKind.EXTERNAL_METHOD in kinds, "EXTERNAL_METHOD_EVIDENCE_REQUIRED")
    _require(isinstance(evidence_refs, list) and bool(evidence_refs)
             and all(isinstance(ref, str) and ref in available for ref in evidence_refs),
             "EVIDENCE_UNGROUNDED")
    _require(isinstance(affected_stages, list) and bool(affected_stages)
             and all(stage in BUSINESS_STAGE_NAMES for stage in affected_stages)
             and len(affected_stages) == len(set(affected_stages)),
             "AFFECTED_STAGES_REQUIRED")
    return envelope.model_dump(mode="json")


def mutate_method_catalog(
    raw: Mapping[str, Any],
    *,
    operation: str,
    knowledge_id: str,
    proposed_record: Mapping[str, Any] | None = None,
    decision_envelope: Mapping[str, Any] | None = None,
    evidence_refs: list[str] | None = None,
    affected_stages: list[str] | None = None,
    promotion_evidence: Mapping[str, Any] | None = None,
    promotion_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
    impact_target_revision: int | None = None,
    impact_evidence: Mapping[str, Any] | None = None,
    impact_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
    authorization_evidence: Mapping[str, Any] | None = None,
    action_request: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    checked = validate_method_catalog(raw)
    _require(operation in METHOD_ACTIONS, "ACTION_UNSUPPORTED")
    _require(isinstance(knowledge_id, str) and _METHOD_ID.fullmatch(knowledge_id) is not None,
             "ID_INVALID")
    evidence = list(evidence_refs or [])
    stages = list(affected_stages or [])
    _require(isinstance(action_request, Mapping)
             and set(action_request) == {
                 "schema_version", "domain_id", "action_id", "operation",
                 "expected_catalog_blob_sha", "parameters",
             }, "ACTION_REQUEST_REQUIRED")
    _require(action_request.get("schema_version") == "1.0"
             and action_request.get("domain_id") == "financial_writing"
             and action_request.get("operation") == operation
             and action_request.get("parameters", {}).get("knowledge_id") == knowledge_id,
             "ACTION_REQUEST_SCOPE_MISMATCH")
    _require(isinstance(action_request.get("expected_catalog_blob_sha"), str)
             and re.fullmatch(r"[a-f0-9]{40}", action_request["expected_catalog_blob_sha"]) is not None,
             "ACTION_REQUEST_CATALOG_SHA_INVALID")
    _require(isinstance(authorization_evidence, Mapping), "ACTION_AUTHORIZATION_ATTESTATION_REQUIRED")
    try:
        verify_method_action_authorization(authorization_evidence, request=action_request)
    except Exception as exc:
        raise MethodGovernanceError("FINANCIAL_METHOD_ACTION_AUTHORIZATION_ATTESTATION_INVALID") from exc
    request_params = action_request["parameters"]
    expected_params = {
        "knowledge_id": knowledge_id,
        "proposed_record": proposed_record,
        "decision_envelope": decision_envelope,
        "evidence_refs": evidence,
        "affected_stages": stages,
        "promotion_evidence": promotion_evidence,
        "impact_target_revision": impact_target_revision,
        "impact_evidence": impact_evidence,
    }
    _require(set(request_params).issubset(expected_params), "ACTION_REQUEST_PARAMETERS_EXCEEDED")
    for key, value in request_params.items():
        _require(_digest(value) == _digest(expected_params[key]),
                 "ACTION_REQUEST_ARGUMENT_MISMATCH:" + key)
    for key in ("knowledge_id", "decision_envelope", "evidence_refs", "affected_stages"):
        _require(key in request_params, "ACTION_REQUEST_PARAMETER_MISSING:" + key)
    decision = _validate_method_decision(decision_envelope, evidence, stages)

    catalog = deepcopy(checked)
    records = catalog["records"]
    position = next((i for i, record in enumerate(records)
                     if record["knowledge_id"] == knowledge_id), None)
    before = deepcopy(records[position]) if position is not None else None
    current_status = (before or {}).get("lifecycle_status", "LEGACY_DECLARED")
    promoted_proof = None
    impact_proof = None

    if operation == "CREATE":
        _require(position is None, "ALREADY_EXISTS")
        data = _record_data(proposed_record)
        _require(data["knowledge_id"] == knowledge_id, "PROPOSED_ID_MISMATCH")
        after = {**data, "lifecycle_status": "CANDIDATE", "method_revision": 1}
        records.append(after)
    else:
        _require(position is not None, "NOT_FOUND")
        after = deepcopy(before)
        _require(current_status in METHOD_STATUSES, "CURRENT_STATUS_INVALID")
        after.setdefault("lifecycle_status", current_status)
        if operation == "REVISE":
            _require(current_status != "RETIRED", "RETIRED_CANNOT_REVISE")
            _require(after.get("pending_revision") is None,
                     "PENDING_REVISION_MUST_BE_DISCARDED_OR_PROMOTED")
            candidate = _record_data(proposed_record)
            _require(candidate["knowledge_id"] == knowledge_id, "PROPOSED_ID_MISMATCH")
            _require(_digest(candidate) != _digest({k: after[k] for k in METHOD_FIELDS}),
                     "NO_EFFECTIVE_CHANGE")
            after["pending_revision"] = candidate
        elif operation == "DISCARD_PENDING":
            _require(after.get("pending_revision") is not None, "NO_PENDING_REVISION")
            after.pop("pending_revision")
        elif operation == "PROMOTE":
            _require(current_status not in {"RETIRED", "CHALLENGED"},
                     "CHALLENGED_OR_RETIRED_CANNOT_PROMOTE_DIRECTLY")
            proposed = after.get("pending_revision", {k: after[k] for k in METHOD_FIELDS})
            _require(isinstance(promotion_evidence, Mapping), "PROMOTION_EVIDENCE_REQUIRED")
            refs = promotion_evidence.get("validation_refs")
            _require(isinstance(refs, list) and bool(refs) and all(
                isinstance(ref, str) and bool(ref.strip()) for ref in refs
            ), "PROMOTION_TEST_REFS_REQUIRED")
            _require(isinstance(promotion_evidence.get("review_ref"), str)
                     and bool(promotion_evidence["review_ref"].strip()), "PROMOTION_REVIEW_REF_REQUIRED")
            _require(callable(promotion_verifier), "INDEPENDENT_PROMOTION_VERIFIER_REQUIRED")
            reviewed_sha = _digest(proposed)
            challenge = {
                "knowledge_id": knowledge_id,
                "record_sha256": reviewed_sha,
                "decision_sha256": _digest(decision),
                "validation_refs": refs,
                "review_ref": promotion_evidence["review_ref"],
            }
            try:
                proof = verify_method_promotion_attestation(
                    promotion_verifier(deepcopy(challenge)), challenge=challenge,
                )
            except Exception as exc:
                raise MethodGovernanceError(
                    "FINANCIAL_METHOD_INDEPENDENT_PROMOTION_ATTESTATION_FAILED"
                ) from exc
            promoted_proof = {
                "reviewer_principal": proof["authenticated_actor"],
                "provider_id": proof["provider_id"],
                "reviewed_record_sha256": reviewed_sha,
                "validation_refs": refs,
                "review_ref": challenge["review_ref"],
                "attestation_signature": proof["signature"],
                "attestation": deepcopy(dict(proof)),
                "assurance": "HMAC_SIGNED_EXTERNAL_METHOD_PROMOTION_REVIEW__OUTCOME_REVALIDATION_OPEN",
            }
            after = {**proposed, "lifecycle_status": "ACTIVE",
                     "method_revision": int(before.get("method_revision", 0)) + 1}
        elif operation == "CHALLENGE":
            _require(current_status not in {"CHALLENGED", "RETIRED"},
                     "NOT_CHALLENGEABLE")
            after["lifecycle_status"] = "CHALLENGED"
            after["method_revision"] = int(before.get("method_revision", 0)) + 1
        elif operation == "RETIRE":
            _require(current_status != "RETIRED", "ALREADY_RETIRED")
            after.pop("pending_revision", None)
            after["lifecycle_status"] = "RETIRED"
            after["method_revision"] = int(before.get("method_revision", 0)) + 1
        elif operation == "RESTORE":
            _require(current_status in {"RETIRED", "CHALLENGED"},
                     "RESTORE_ONLY_RETIRED_OR_CHALLENGED")
            after.pop("pending_revision", None)
            after["lifecycle_status"] = "CANDIDATE"
            after["method_revision"] = int(before.get("method_revision", 0)) + 1
        elif operation == "VERIFY_IMPACT":
            prior = checked.get("change_history", [])
            _require(type(impact_target_revision) is int
                     and 0 < impact_target_revision <= len(prior), "IMPACT_TARGET_REVISION_INVALID")
            target = prior[impact_target_revision - 1]
            _require(target.get("knowledge_id") == knowledge_id
                     and target.get("operation") != "VERIFY_IMPACT"
                     and target.get("impact_review_state")
                     == "OPEN__AFFECTED_WORKFLOWS_REVALIDATION_REQUIRED",
                     "IMPACT_TARGET_NOT_OPEN")
            _require(not any(
                e.get("operation") == "VERIFY_IMPACT"
                and e.get("target_change_revision") == impact_target_revision
                for e in prior
            ), "IMPACT_ALREADY_CLOSED")
            _require(isinstance(impact_evidence, Mapping)
                     and set(impact_evidence) == {"stage_evidence_refs"},
                     "IMPACT_STAGE_EVIDENCE_REQUIRED")
            stage_refs = impact_evidence["stage_evidence_refs"]
            _require(isinstance(stage_refs, Mapping)
                     and set(stage_refs) == set(target["affected_stages"])
                     and all(isinstance(ref, str) and bool(ref.strip())
                             for ref in stage_refs.values()), "IMPACT_STAGE_COVERAGE_MISMATCH")
            _require(callable(impact_verifier), "IMPACT_INDEPENDENT_VERIFIER_REQUIRED")
            challenge = {
                "knowledge_id": knowledge_id,
                "target_change_revision": impact_target_revision,
                "event_sha256": _digest(target),
                "stage_evidence_refs": dict(stage_refs),
            }
            try:
                proof = verify_method_impact_attestation(
                    impact_verifier(deepcopy(challenge)), challenge=challenge,
                )
            except Exception as exc:
                raise MethodGovernanceError(
                    "FINANCIAL_METHOD_IMPACT_ATTESTATION_FAILED"
                ) from exc
            impact_proof = {
                "target_change_revision": impact_target_revision,
                "reviewed_event_sha256": challenge["event_sha256"],
                "verified_stages": list(stage_refs),
                "stage_evidence_refs": dict(stage_refs),
                "reviewer_principal": proof["authenticated_actor"],
                "provider_id": proof["provider_id"],
                "attestation_signature": proof["signature"],
                "attestation": deepcopy(dict(proof)),
                "assurance": "HMAC_SIGNED_EXTERNAL_METHOD_STAGE_REVALIDATION__LIVE_READER_OUTCOME_OPEN",
            }
        if operation != "VERIFY_IMPACT":
            records[position] = after

    revision = checked.get("governance_revision", 0) + 1
    history = deepcopy(checked.get("change_history", []))
    event = {
        "revision": revision,
        "operation": operation,
        "knowledge_id": knowledge_id,
        "prior_record_sha256": _digest(before) if before is not None else None,
        "result_record_sha256": _digest(after),
        "decision_sha256": _digest(decision),
        "evidence_refs": evidence,
        "affected_stages": stages,
        "promoted_proof": promoted_proof,
        "impact_verification": impact_proof,
        "authorization_evidence": deepcopy(dict(authorization_evidence)) if isinstance(authorization_evidence, Mapping) else None,
        "authorization_request": deepcopy(dict(action_request)) if isinstance(action_request, Mapping) else None,
        "authorization_action_id": authorization_evidence.get("action_id") if isinstance(authorization_evidence, Mapping) else None,
        "authorization_expected_catalog_blob_sha": authorization_evidence.get("expected_catalog_blob_sha") if isinstance(authorization_evidence, Mapping) else None,
        "target_change_revision": impact_target_revision if operation == "VERIFY_IMPACT" else None,
        "impact_review_state": (
            "CLOSED__EXTERNAL_STAGE_EVIDENCE_READBACK"
            if operation == "VERIFY_IMPACT"
            else "OPEN__AFFECTED_WORKFLOWS_REVALIDATION_REQUIRED"
        ),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    history.append(event)
    catalog["change_history"] = history
    catalog["governance_revision"] = revision
    catalog["updated_at"] = event["recorded_at"]
    validate_method_catalog(catalog)
    return catalog, {
        "operation": operation,
        "knowledge_id": knowledge_id,
        "catalog_revision": revision,
        "lifecycle_status": after.get("lifecycle_status", "LEGACY_DECLARED"),
        "impact_review_state": event["impact_review_state"],
        "change_event_sha256": _digest(event),
        "promotion_review": promoted_proof,
    }


def _effective_record_fingerprint(record: Mapping[str, Any]) -> str:
    """Pending method edits do not mutate the currently effective method."""
    return _digest({key: val for key, val in record.items()
                    if key != "pending_revision"})


def admitted_method_usage_snapshot(
    catalog: Mapping[str, Any], method_ids: list[str],
) -> dict[str, Any]:
    """Bind exact active methods, not their descriptive legacy adoption labels."""
    checked = validate_method_catalog(catalog)
    _require(isinstance(method_ids, list) and len(method_ids) == len(set(method_ids)),
             "USAGE_METHOD_IDS_INVALID")
    actual: list[dict[str, Any]] = []
    for method_id in sorted(method_ids):
        records = query_methods(checked, knowledge_id=method_id)
        _require(len(records) == 1, f"USAGE_METHOD_MISSING:{method_id}")
        record = records[0]
        _require(record["lifecycle_status"] == "ACTIVE",
                 f"USAGE_METHOD_NOT_ADMITTED:{method_id}")
        actual.append({
            "knowledge_id": method_id,
            "record_sha256": _effective_record_fingerprint(record),
            "method_revision": record.get("method_revision"),
        })
    return {
        "catalog_revision": checked.get("governance_revision", 0),
        "methods": actual,
        "assurance": "ACTIVE_METHOD_RECORD_READBACK__ARTICLE_OUTCOME_OPEN",
    }


def method_dependency_drift(
    catalog: Mapping[str, Any], snapshot: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Find changed effective method dependencies; ignore unrelated proposals.

    Drift must have an append-only change-event cause. A changed hash without
    a corresponding event is a source-history conflict, not permission to
    guess the next method or silently continue.
    """
    checked = validate_method_catalog(catalog)
    _require(isinstance(snapshot, Mapping), "METHOD_SNAPSHOT_REQUIRED")
    revision = snapshot.get("catalog_revision")
    methods = snapshot.get("methods")
    _require(type(revision) is int and 0 <= revision <= checked.get("governance_revision", 0),
             "METHOD_SNAPSHOT_REVISION_INVALID")
    _require(isinstance(methods, list), "METHOD_SNAPSHOT_METHODS_INVALID")
    changes: list[dict[str, Any]] = []
    for prior in methods:
        _require(isinstance(prior, Mapping), "METHOD_SNAPSHOT_ITEM_INVALID")
        name = prior.get("knowledge_id")
        _require(isinstance(name, str) and bool(name), "METHOD_SNAPSHOT_ID_INVALID")
        records = query_methods(checked, knowledge_id=name)
        current = records[0] if len(records) == 1 else None
        current_sha = _effective_record_fingerprint(current) if current else None
        old_sha = prior.get("record_sha256")
        _require(isinstance(old_sha, str) and len(old_sha) == 64,
                 "METHOD_SNAPSHOT_HASH_INVALID")
        if old_sha == current_sha:
            continue
        events = [
            event for event in checked.get("change_history", [])
            if event["revision"] > revision and event["knowledge_id"] == name
            and event["operation"] not in {"REVISE", "DISCARD_PENDING", "VERIFY_IMPACT"}
        ]
        _require(bool(events), f"METHOD_DRIFT_WITHOUT_CHANGE_PROVENANCE:{name}")
        affected = sorted(
            {stage for event in events for stage in event["affected_stages"]},
            key=lambda s: BUSINESS_STAGE_NAMES.index(s),
        )
        _require(bool(affected), "METHOD_DRIFT_WITHOUT_AFFECTED_STAGES")
        changes.append({
            "knowledge_id": name,
            "prior_record_sha256": old_sha,
            "current_record_sha256": current_sha,
            "current_lifecycle_status": current.get("lifecycle_status") if current else None,
            "change_revisions": [event["revision"] for event in events],
            "affected_stages": affected,
            "earliest_affected_stage": affected[0],
        })
    return changes
