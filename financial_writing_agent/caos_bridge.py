"""CAOS -> Financial owner-native bridge (never a second article controller).

CAOS owns owner-goal deliberation and may propose an action. The child alone
adjudicates article requirements, stage, evidence and delivery. Production IO
must be supplied by a trusted caller; absence of grant, provider CAS or
independent readback fails closed. This module does NOT install a ChatGPT
plugin, initialize a CAOS Host, or grant remote permissions by its presence.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from typing import Any, Callable, Mapping

from . import current_admission
from .path_identity import require_task_id

PARENT_REPOSITORY = "D1traverser-debug/cognition-agent-os"
BRIDGE_SCHEMA_VERSION = "1.0"
ARTICLE_STATE_ROOT = "workspaces/articles"
_SHA = re.compile(r"[0-9a-f]{40}\Z")
_ACTION_ID = re.compile(r"[A-Za-z0-9_.:-]{1,180}\Z")
OPERATIONS = frozenset({"CREATE_ARTICLE", "ADVANCE_STAGE", "CHANGE_REQUIREMENTS"})
ADVANCE_PARAMETER_KEYS = frozenset({
    "artifact_key", "artifact_path", "artifact_blob_sha", "review_status",
    "revision_target", "delivery_artifacts", "audit_artifact",
    "decision_envelope", "private_research_brief", "story_blueprints",
    "publication_fitnesses", "requirement_satisfaction",
})
CHANGE_PARAMETER_KEYS = frozenset({"evidence_ref", "upserts", "retire_ids"})
CREATE_PARAMETER_KEYS = frozenset({
    "prompt", "source_refs", "target_platforms", "distribution_mode",
    "distribution_mode_source", "distribution_mode_override_evidence",
})


class CAOSChildAdmissionError(ValueError):
    pass


class CAOSChildEffectUnverified(RuntimeError):
    pass


StateReader = Callable[[str], Mapping[str, Any] | None]
CASWriter = Callable[[str, str | None, str], Mapping[str, Any]]
GrantVerifier = Callable[[Mapping[str, Any]], bool]


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise CAOSChildAdmissionError(message)


def _article_path(task_id: str) -> str:
    try:
        task_id = require_task_id(task_id)
    except ValueError as exc:
        raise CAOSChildAdmissionError("INVALID_FINANCIAL_ARTICLE_ID") from exc
    return f"{ARTICLE_STATE_ROOT}/{task_id}/STATE.json"


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(_SHA.fullmatch(value))


def _reader_result(reader: StateReader, path: str) -> tuple[dict[str, Any], str] | None:
    raw = reader(path)
    if raw is None:
        return None
    _require(isinstance(raw, Mapping), "STATE_PROVIDER_RESPONSE_INVALID")
    state, sha = raw.get("state"), raw.get("blob_sha")
    _require(isinstance(state, Mapping) and _valid_sha(sha), "STATE_PROVIDER_RESPONSE_INVALID")
    return deepcopy(dict(state)), sha


def _canonical_payload(state: Mapping[str, Any]) -> str:
    return json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _blob_sha(payload: str) -> str:
    data = payload.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\x00" + data).hexdigest()


def observe_article(task_id: str, *, state_reader: StateReader) -> dict[str, Any]:
    """Read child-native state without inferring audience/semantic acceptance."""
    path = _article_path(task_id)
    record = _reader_result(state_reader, path)
    _require(record is not None, "CHILD_STATE_NOT_FOUND")
    state, blob_sha = record
    _require(state.get("task_id") == task_id, "CHILD_IDENTITY_MISMATCH")
    current_admission.validate_state(state)
    status = str(state["status"])
    quality = state.get("quality_evidence") or {}
    return {
        "contract_version": BRIDGE_SCHEMA_VERSION,
        "kind": "CAOS_FINANCIAL_CHILD_OBSERVATION",
        "parent_repository": PARENT_REPOSITORY,
        "task_id": task_id,
        "state_ref": path,
        "state_blob_sha": blob_sha,
        "stage": state["current_stage"],
        "business_status": status,
        "requirement_revision": state["task_requirement_authority"]["revision"],
        "requirement_digest": state["task_requirement_digest"],
        "quality_evidence_keys": sorted(quality),
        "required_outputs": list(state.get("required_outputs", [])),
        "recorded_outputs": sorted(state.get("delivery_artifacts", {})),
        "content_quality_independently_verified": False,
        "owner_outcome_independently_verified": False,
        "parent_controller_may_rewrite_child_state": False,
        "observation_is_not_permission_or_publication_acceptance": True,
    }


def _validate_request(raw: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(raw, Mapping), "CAOS_REQUEST_MUST_BE_MAPPING")
    required = {
        "schema_version", "parent_repository", "goal_id", "goal_revision",
        "action_id", "task_id", "operation", "expected_state_blob_sha", "parameters",
    }
    _require(set(raw) == required, "CAOS_REQUEST_FIELDS_MISMATCH")
    req = deepcopy(dict(raw))
    _require(req["schema_version"] == BRIDGE_SCHEMA_VERSION, "CAOS_BRIDGE_VERSION_MISMATCH")
    _require(req["parent_repository"] == PARENT_REPOSITORY, "CAOS_PARENT_IDENTITY_MISMATCH")
    _require(isinstance(req["goal_id"], str) and bool(req["goal_id"].strip()), "CAOS_GOAL_ID_REQUIRED")
    _require(type(req["goal_revision"]) is int and req["goal_revision"] >= 1, "CAOS_GOAL_REVISION_INVALID")
    _require(isinstance(req["action_id"], str) and bool(_ACTION_ID.fullmatch(req["action_id"])), "CAOS_ACTION_ID_INVALID")
    _article_path(req["task_id"])
    operation = req["operation"]
    _require(operation in OPERATIONS, "UNSUPPORTED_CHILD_MUTATION")
    sha = req["expected_state_blob_sha"]
    _require(sha is None if operation == "CREATE_ARTICLE" else _valid_sha(sha), "CHILD_EXPECTED_BLOB_SHA_REQUIRED")
    _require(isinstance(req["parameters"], Mapping), "CHILD_PARAMETERS_INVALID")
    allowed = (
        CREATE_PARAMETER_KEYS if operation == "CREATE_ARTICLE"
        else ADVANCE_PARAMETER_KEYS if operation == "ADVANCE_STAGE"
        else CHANGE_PARAMETER_KEYS
    )
    _require(set(req["parameters"]).issubset(allowed), "CHILD_PARAMETER_SCOPE_EXCEEDED")
    return req


def admit_parent_article_action(
    request: Mapping[str, Any],
    *,
    state_reader: StateReader,
    cas_writer: CASWriter | None,
    grant_verifier: GrantVerifier | None,
) -> dict[str, Any]:
    """Perform an action only through current_admission and provider CAS.

    Requires externally trusted, exact-goal grant verification and provider
    compare-and-swap/write readback. No self-attested permission flag is
    accepted; a parent request is an untrusted proposal until verified.
    """
    req = _validate_request(request)
    _require(grant_verifier is not None and cas_writer is not None,
             "CHILD_WRITE_REQUIRES_TRUSTED_GRANT_AND_PROVIDER_CAS")
    try:
        authorized = grant_verifier(deepcopy(req))
    except Exception as exc:
        raise CAOSChildAdmissionError("CAOS_GRANT_NOT_VERIFIED") from exc
    _require(authorized is True, "CAOS_GRANT_NOT_VERIFIED")

    task_id = req["task_id"]
    path = _article_path(task_id)
    observed = _reader_result(state_reader, path)
    operation, params = req["operation"], deepcopy(dict(req["parameters"]))
    if operation == "CREATE_ARTICLE":
        _require(observed is None, "CHILD_ARTICLE_ALREADY_EXISTS")
        params.setdefault("source_refs", [])
        _require(isinstance(params.get("prompt"), str) and bool(params["prompt"].strip()), "CHILD_PROMPT_REQUIRED")
        candidate = current_admission.build_initial_state(
            task_id=task_id,
            executor_identity=f"caos:{req['goal_id']}:{req['action_id']}",
            **params,
        )
        previous_sha = None
    else:
        _require(observed is not None, "CHILD_STATE_NOT_FOUND")
        state, previous_sha = observed
        _require(previous_sha == req["expected_state_blob_sha"], "CHILD_STATE_CHANGED_CONCURRENTLY")
        _require(state.get("task_id") == task_id, "CHILD_IDENTITY_MISMATCH")
        current_admission.validate_state(state)
        if operation == "ADVANCE_STAGE":
            candidate = current_admission.advance_state(
                state, previous_state_blob_sha=previous_sha,
                executor_identity=f"caos:{req['goal_id']}:{req['action_id']}",
                **params,
            )
        else:
            candidate = current_admission.apply_task_requirement_change(
                state, previous_state_blob_sha=previous_sha,
                executor_identity=f"caos:{req['goal_id']}:{req['action_id']}",
                **params,
            )

    current_admission.validate_state(candidate)
    payload = _canonical_payload(candidate)
    expected_new_sha = _blob_sha(payload)
    try:
        issued = cas_writer(path, previous_sha, payload)
    except Exception as exc:
        raise CAOSChildEffectUnverified("PROVIDER_WRITE_NOT_CONFIRMED") from exc
    if not isinstance(issued, Mapping) or issued.get("blob_sha") != expected_new_sha:
        raise CAOSChildEffectUnverified("PROVIDER_RETURNED_UNVERIFIED_BLOB")

    after = _reader_result(state_reader, path)
    if after is None or after[1] != expected_new_sha or after[0] != candidate:
        raise CAOSChildEffectUnverified("CHILD_PROVIDER_READBACK_MISMATCH")
    current_admission.validate_state(after[0])
    return {
        "contract_version": BRIDGE_SCHEMA_VERSION,
        "kind": "CAOS_FINANCIAL_CHILD_CAS_OBSERVED",
        "parent_repository": PARENT_REPOSITORY,
        "goal_id": req["goal_id"],
        "goal_revision": req["goal_revision"],
        "action_id": req["action_id"],
        "task_id": task_id,
        "operation": operation,
        "state_ref": path,
        "previous_blob_sha": previous_sha,
        "observed_new_blob_sha": expected_new_sha,
        "resulting_stage": after[0]["current_stage"],
        "resulting_business_status": after[0]["status"],
        "provider_commit_ref": issued.get("commit_ref"),
        "child_state_cas_verified": True,
        "parent_business_acceptance": False,
        "independent_editorial_quality_verified": False,
    }
