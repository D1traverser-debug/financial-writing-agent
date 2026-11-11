"""Standalone Financial Writing owner-native task interface.

No CAOS, external parent, dedicated daemon or second business controller is
required. A connected Financial plugin/chat client supplies authenticated
GitHub provider callbacks and an independent permission check. The Financial
Article Aggregate alone owns requirements, workflow and completion.

Test callbacks do not certify that a particular ChatGPT plugin has been
installed, authenticated or invoked.
"""
from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from typing import Any, Callable, Mapping

from . import current_admission
from .path_identity import require_article_path, require_task_id

DOMAIN_ID = "financial_writing"
CONTRACT_VERSION = "1.0"
STATE_ROOT = "workspaces/articles"
_ACTION_ID = re.compile(r"[A-Za-z0-9_.:-]{1,180}\Z")
_SHA = re.compile(r"[a-f0-9]{40}\Z")
OPERATIONS = frozenset({"CREATE_ARTICLE", "CHANGE_REQUIREMENTS", "ADVANCE_STAGE", "ATTACH_FEEDBACK"})
CREATE_KEYS = frozenset({
    "prompt", "source_refs", "target_platforms", "distribution_mode",
    "distribution_mode_source", "distribution_mode_override_evidence",
})
REQUIREMENT_KEYS = frozenset({"evidence_ref", "upserts", "retire_ids"})
STAGE_KEYS = frozenset({
    "artifact_key", "artifact_path", "artifact_blob_sha", "review_status",
    "revision_target", "delivery_artifacts", "audit_artifact",
    "decision_envelope", "private_research_brief", "story_blueprints",
    "publication_fitnesses", "requirement_satisfaction",
})
FEEDBACK_KEYS = frozenset({"sample", "system_impact"})


class FinancialAdmissionError(ValueError):
    """Invalid scope, stale state or denied action. No business write accepted."""


class FinancialEffectUnverified(RuntimeError):
    """Remote mutation occurred or was attempted but its exact effect is unknown."""


StateReader = Callable[[str], Mapping[str, Any] | None]
CASWriter = Callable[[str, str | None, str], Mapping[str, Any]]
ArtifactReader = Callable[[str], Mapping[str, Any] | None]
AuthorizationVerifier = Callable[[Mapping[str, Any]], bool]


def _require(ok: bool, why: str) -> None:
    if not ok:
        raise FinancialAdmissionError(why)


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and _SHA.fullmatch(value) is not None


def _state_path(task_id: Any) -> str:
    try:
        slug = require_task_id(task_id)
    except ValueError as exc:
        raise FinancialAdmissionError("INVALID_FINANCIAL_ARTICLE_ID") from exc
    return f"{STATE_ROOT}/{slug}/STATE.json"


def _canonical_payload(state: Mapping[str, Any]) -> str:
    return json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _blob_sha(content: bytes | str) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\x00" + content).hexdigest()


def _strict_json_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_strict_json_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(_strict_json_equal(a, b) for a, b in zip(left, right))
    return left == right


def _read(reader: StateReader, path: str) -> tuple[dict[str, Any], str] | None:
    try:
        raw = reader(path)
    except Exception as exc:
        raise FinancialEffectUnverified("FINANCIAL_PROVIDER_READ_FAILED") from exc
    if raw is None:
        return None
    _require(isinstance(raw, Mapping), "INVALID_PROVIDER_STATE_RESPONSE")
    state, sha = raw.get("state"), raw.get("blob_sha")
    _require(isinstance(state, Mapping) and _valid_sha(sha), "INVALID_PROVIDER_STATE_RESPONSE")
    candidate = deepcopy(dict(state))
    _require(_blob_sha(_canonical_payload(candidate)) == sha or raw.get("provider_exact_blob_verified") is True,
             "PROVIDER_STATE_BLOB_SHA_MISMATCH")
    return candidate, sha


def _verify_stage_bytes(candidate: Mapping[str, Any], reader: ArtifactReader | None) -> dict[str, Any] | None:
    receipts = candidate["execution_receipts"]
    bindings = receipts[-1]["input_bindings"]
    key = bindings.get("required_artifact_key")
    if key is None:
        return None
    _require(reader is not None, "FINANCIAL_REQUIRED_STAGE_ARTIFACT_READER_MISSING")
    ref = candidate.get("stage_artifacts", {}).get(key)
    _require(isinstance(ref, Mapping), "FINANCIAL_REQUIRED_STAGE_ARTIFACT_REFERENCE_MISSING")
    try:
        path = require_article_path(ref.get("path"), candidate["task_id"])
    except ValueError as exc:
        raise FinancialAdmissionError("FINANCIAL_STAGE_ARTIFACT_PATH_INVALID") from exc
    expected = ref.get("blob_sha")
    _require(_valid_sha(expected) and bindings.get("required_artifact_blob_sha") == expected,
             "FINANCIAL_STAGE_ARTIFACT_RECEIPT_SHA_INVALID")
    try:
        observed = reader(path)
    except Exception as exc:
        raise FinancialEffectUnverified("FINANCIAL_STAGE_ARTIFACT_READ_FAILED") from exc
    _require(isinstance(observed, Mapping), "FINANCIAL_STAGE_ARTIFACT_BYTES_MISSING")
    content, claimed_sha = observed.get("content"), observed.get("blob_sha")
    _require(isinstance(content, (str, bytes)) and _valid_sha(claimed_sha),
             "FINANCIAL_STAGE_ARTIFACT_BYTES_INVALID")
    _require(_blob_sha(content) == claimed_sha == expected,
             "FINANCIAL_STAGE_ARTIFACT_BYTES_SHA_MISMATCH")
    return {"artifact_key": key, "path": path, "verified_blob_sha": expected}


def observe_article(task_id: str, *, state_reader: StateReader) -> dict[str, Any]:
    """Read actual child-owned business state; never imply editorial acceptance."""
    path = _state_path(task_id)
    record = _read(state_reader, path)
    _require(record is not None, "FINANCIAL_ARTICLE_NOT_FOUND")
    state, sha = record
    _require(state["task_id"] == task_id, "FINANCIAL_ARTICLE_ID_MISMATCH")
    current_admission.validate_state(state)
    return {
        "contract_version": CONTRACT_VERSION, "domain_id": DOMAIN_ID,
        "task_id": task_id, "state_ref": path, "state_blob_sha": sha,
        "stage": state["current_stage"], "business_status": state["status"],
        "requirement_revision": state["task_requirement_authority"]["revision"],
        "requirement_digest": state["task_requirement_digest"],
        "required_outputs": list(state["required_outputs"]),
        "recorded_outputs": sorted(state.get("delivery_artifacts", {})),
        "independent_editorial_quality_verified": False,
        "owner_outcome_verified": False,
    }


def _request(raw: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(raw, Mapping), "FINANCIAL_ACTION_MUST_BE_MAPPING")
    required = {
        "schema_version", "domain_id", "action_id", "task_id",
        "operation", "expected_state_blob_sha", "parameters",
    }
    _require(set(raw) == required, "FINANCIAL_ACTION_FIELDS_MISMATCH")
    r = deepcopy(dict(raw))
    _require(r["schema_version"] == CONTRACT_VERSION and r["domain_id"] == DOMAIN_ID,
             "FINANCIAL_ACTION_CONTRACT_MISMATCH")
    _state_path(r["task_id"])
    _require(isinstance(r["action_id"], str) and _ACTION_ID.fullmatch(r["action_id"]) is not None,
             "FINANCIAL_ACTION_ID_INVALID")
    op = r["operation"]
    _require(isinstance(op, str) and op in OPERATIONS, "FINANCIAL_ACTION_NOT_SUPPORTED")
    sha = r["expected_state_blob_sha"]
    _require(sha is None if op == "CREATE_ARTICLE" else _valid_sha(sha),
             "FINANCIAL_EXPECTED_STATE_BLOB_REQUIRED")
    params = r["parameters"]
    _require(isinstance(params, Mapping), "FINANCIAL_ACTION_PARAMETERS_INVALID")
    allowed = (
        CREATE_KEYS if op == "CREATE_ARTICLE" else REQUIREMENT_KEYS if op == "CHANGE_REQUIREMENTS"
        else STAGE_KEYS if op == "ADVANCE_STAGE" else FEEDBACK_KEYS
    )
    _require(set(params).issubset(allowed), "FINANCIAL_ACTION_PARAMETERS_SCOPE_EXCEEDED")
    return r


def admit_article_action(
    proposal: Mapping[str, Any],
    *,
    state_reader: StateReader,
    cas_writer: CASWriter | None,
    authorization_verifier: AuthorizationVerifier | None,
    artifact_reader: ArtifactReader | None = None,
) -> dict[str, Any]:
    """Use existing Financial admissions and genuine provider CAS/readback.

    authorization_verifier is supplied by an authenticated Financial client;
    a model flag like "authorized": true is never permission. No CAOS token,
    parent goal id or parent service exists in this call contract.
    """
    r = _request(proposal)
    _require(callable(authorization_verifier) and callable(cas_writer),
             "FINANCIAL_TRUSTED_AUTH_AND_CAS_REQUIRED")
    try:
        authorized = authorization_verifier(deepcopy(r))
    except Exception as exc:
        raise FinancialAdmissionError("FINANCIAL_AUTHORIZATION_NOT_VERIFIED") from exc
    _require(authorized is True, "FINANCIAL_AUTHORIZATION_NOT_VERIFIED")
    path = _state_path(r["task_id"])
    observed = _read(state_reader, path)
    op = r["operation"]
    params = deepcopy(dict(r["parameters"]))
    if op == "CREATE_ARTICLE":
        _require(observed is None, "FINANCIAL_ARTICLE_ALREADY_EXISTS")
        params.setdefault("source_refs", [])
        _require(isinstance(params.get("prompt"), str) and bool(params["prompt"].strip()),
                 "FINANCIAL_ARTICLE_PROMPT_REQUIRED")
        candidate = current_admission.build_initial_state(
            task_id=r["task_id"], executor_identity=f"financial:{r['action_id']}",
            **params,
        )
        previous_sha = None
    else:
        _require(observed is not None, "FINANCIAL_ARTICLE_NOT_FOUND")
        state, previous_sha = observed
        _require(previous_sha == r["expected_state_blob_sha"], "FINANCIAL_STATE_CHANGED_CONCURRENTLY")
        _require(state["task_id"] == r["task_id"], "FINANCIAL_ARTICLE_ID_MISMATCH")
        current_admission.validate_state(state)
        call = {
            "previous_state_blob_sha": previous_sha,
            "executor_identity": f"financial:{r['action_id']}",
            **params,
        }
        if op == "ADVANCE_STAGE":
            candidate = current_admission.advance_state(state, **call)
        elif op == "CHANGE_REQUIREMENTS":
            candidate = current_admission.apply_task_requirement_change(state, **call)
        else:
            candidate = current_admission.attach_material_feedback(state, **call)

    current_admission.validate_state(candidate)
    stage_bytes = _verify_stage_bytes(candidate, artifact_reader) if op == "ADVANCE_STAGE" else None
    payload = _canonical_payload(candidate)
    expected_new_sha = _blob_sha(payload)
    try:
        issued = cas_writer(path, previous_sha, payload)
    except Exception as exc:
        raise FinancialEffectUnverified("FINANCIAL_PROVIDER_WRITE_OUTCOME_UNKNOWN") from exc
    if not isinstance(issued, Mapping) or issued.get("blob_sha") != expected_new_sha:
        raise FinancialEffectUnverified("FINANCIAL_PROVIDER_WRITE_SHA_MISMATCH")
    after = _read(state_reader, path)
    if after is None or after[1] != expected_new_sha or not _strict_json_equal(after[0], candidate):
        raise FinancialEffectUnverified("FINANCIAL_STATE_READBACK_MISMATCH")
    current_admission.validate_state(after[0])
    return {
        "contract_version": CONTRACT_VERSION, "domain_id": DOMAIN_ID,
        "task_id": r["task_id"], "action_id": r["action_id"], "operation": op,
        "state_ref": path, "previous_blob_sha": previous_sha,
        "observed_new_blob_sha": expected_new_sha,
        "provider_commit_ref": issued.get("commit_ref"),
        "stage": after[0]["current_stage"], "business_status": after[0]["status"],
        "required_stage_artifact_verified": stage_bytes,
        "child_state_cas_verified": True,
        "independent_editorial_quality_verified": False,
        "owner_outcome_verified": False,
    }
