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

from .cognition_governance import (
    DecisionEnvelope, EvidenceKind, OperationClass, admission_errors,
)
from .workflow_spec import BUSINESS_STAGE_NAMES

CATALOG_PATH = "knowledge/METHOD_KNOWLEDGE_CATALOG.json"
METHOD_ACTIONS = frozenset({
    "CREATE", "REVISE", "DISCARD_PENDING", "PROMOTE",
    "CHALLENGE", "RETIRE", "RESTORE",
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
    for index, item in enumerate(history, 1):
        _require(isinstance(item, Mapping) and item.get("revision") == index,
                 "CATALOG_HISTORY_SEQUENCE_INVALID")
        _require(item.get("knowledge_id") in seen and item.get("operation") in METHOD_ACTIONS,
                 "CATALOG_HISTORY_EVENT_INVALID")
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
) -> tuple[dict[str, Any], dict[str, Any]]:
    checked = validate_method_catalog(raw)
    _require(operation in METHOD_ACTIONS, "ACTION_UNSUPPORTED")
    _require(isinstance(knowledge_id, str) and _METHOD_ID.fullmatch(knowledge_id) is not None,
             "ID_INVALID")
    evidence = list(evidence_refs or [])
    stages = list(affected_stages or [])
    decision = _validate_method_decision(decision_envelope, evidence, stages)

    catalog = deepcopy(checked)
    records = catalog["records"]
    position = next((i for i, record in enumerate(records)
                     if record["knowledge_id"] == knowledge_id), None)
    before = deepcopy(records[position]) if position is not None else None
    current_status = (before or {}).get("lifecycle_status", "LEGACY_DECLARED")
    promoted_proof = None

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
                proof = promotion_verifier(deepcopy(challenge))
            except Exception as exc:
                raise MethodGovernanceError("FINANCIAL_METHOD_INDEPENDENT_PROMOTION_CHECK_FAILED") from exc
            _require(isinstance(proof, Mapping) and proof.get("verified") is True,
                     "INDEPENDENT_PROMOTION_NOT_VERIFIED")
            _require(proof.get("reviewed_record_sha256") == reviewed_sha,
                     "PROMOTION_REVIEWED_RECORD_MISMATCH")
            _require(isinstance(proof.get("reviewer_principal"), str)
                     and bool(proof["reviewer_principal"].strip())
                     and proof["reviewer_principal"] != "FINANCIAL_WRITING_OWNER",
                     "PROMOTION_INDEPENDENT_REVIEWER_REQUIRED")
            _require(proof.get("validation_refs") == refs,
                     "PROMOTION_TEST_EVIDENCE_MISMATCH")
            promoted_proof = {
                "reviewer_principal": proof["reviewer_principal"],
                "reviewed_record_sha256": reviewed_sha,
                "validation_refs": refs,
                "review_ref": challenge["review_ref"],
                "assurance": "EXTERNAL_PROVIDER_PROMOTION_REVIEW__OUTCOME_REVALIDATION_OPEN",
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
        "impact_review_state": "OPEN__AFFECTED_WORKFLOWS_REVALIDATION_REQUIRED",
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
        "lifecycle_status": after["lifecycle_status"],
        "impact_review_state": event["impact_review_state"],
        "change_event_sha256": _digest(event),
        "promotion_review": promoted_proof,
    }
