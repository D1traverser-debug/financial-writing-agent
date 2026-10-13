from __future__ import annotations

from typing import Any, Callable, Mapping


class DeliveryAvailabilityError(ValueError):
    pass


ResourceVerifier = Callable[[Mapping[str, Any]], bool]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DeliveryAvailabilityError(message)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _hex_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdefABCDEF" for ch in value)
    )


def build_visible_delivery_receipt(
    state: Mapping[str, Any],
    *,
    resources: list[Mapping[str, Any]],
    resource_verifier: ResourceVerifier | None,
) -> dict[str, Any]:
    """Bind current user-visible Word resources to a completed Financial article.

    Durable owner state proves the business/output contract and canonical binary identities.
    It does not prove that a prior chat attachment or external-file handle is still available
    in the current session. This presentation gate requires a fresh resource for every
    required output before the chat may claim that the files are currently deliverable.

    A current resource can be either:
    1. the canonical binary, whose sha256 must equal owner state; or
    2. a regenerated binary produced from durable publication/audit source. Regeneration
       is a new binary instance and must carry source identity plus fresh mechanical and
       render QA; its sha256 is not required to equal the historical canonical binary.
    """
    _require(isinstance(state, Mapping), "state is required")
    task_id = str(state.get("task_id", "")).strip()
    _require(bool(task_id), "state.task_id is required")
    required = state.get("required_outputs")
    _require(isinstance(required, list) and required, "state.required_outputs is required")
    canonical = state.get("delivery_artifacts")
    _require(isinstance(canonical, Mapping), "state.delivery_artifacts is required")
    _require(set(canonical) == set(required), "owner state must reconcile the complete required output set before visible delivery")
    _require(resource_verifier is not None, "current resource_verifier is required")

    by_kind: dict[str, Mapping[str, Any]] = {}
    for resource in resources:
        _require(isinstance(resource, Mapping), "visible delivery resource must be an object")
        kind = str(resource.get("kind", "")).strip()
        _require(kind in required, f"unexpected visible delivery resource kind: {kind or 'MISSING'}")
        _require(kind not in by_kind, f"duplicate visible delivery resource kind: {kind}")
        by_kind[kind] = resource
    _require(set(by_kind) == set(required), f"visible delivery output mismatch: required={sorted(required)}, actual={sorted(by_kind)}")

    presented: dict[str, dict[str, Any]] = {}
    for kind in required:
        resource = by_kind[kind]
        ref = str(resource.get("resource_ref", "")).strip()
        file_name = str(resource.get("file_name", "")).strip()
        digest = str(resource.get("sha256", "")).strip().lower()
        _require(bool(ref), f"{kind}.resource_ref is required for current visible delivery")
        _require(bool(file_name), f"{kind}.file_name is required")
        _require(_hex_sha256(digest), f"{kind}.sha256 must be a 64-character hex digest")
        try:
            verified = bool(resource_verifier(resource))
        except Exception:
            verified = False
        _require(verified, f"{kind}.resource_ref was not verified in the current session")

        canonical_meta = canonical[kind]
        canonical_sha = str(canonical_meta.get("sha256", "")).strip().lower()
        _require(_hex_sha256(canonical_sha), f"canonical {kind}.sha256 is invalid")
        regenerated = resource.get("regenerated_from_durable_source") is True
        if regenerated:
            _require(_nonempty(resource.get("source_ref")), f"regenerated {kind} requires source_ref")
            _require(_nonempty(resource.get("source_identity")), f"regenerated {kind} requires source_identity")
            _require(resource.get("mechanical_qa") == "PASS", f"regenerated {kind} requires fresh mechanical_qa=PASS")
            _require(resource.get("render_qa") == "PASS", f"regenerated {kind} requires fresh render_qa=PASS")
        else:
            _require(digest == canonical_sha, f"non-regenerated {kind} binary hash must match canonical owner state")

        presented[kind] = {
            "file_name": file_name,
            "sha256": digest,
            "resource_ref": ref,
            "regenerated_from_durable_source": regenerated,
            "canonical_sha256": canonical_sha,
            "source_ref": resource.get("source_ref") if regenerated else None,
            "source_identity": resource.get("source_identity") if regenerated else None,
            "mechanical_qa": resource.get("mechanical_qa") if regenerated else None,
            "render_qa": resource.get("render_qa") if regenerated else None,
        }

    return {
        "schema_version": "1.0",
        "task_id": task_id,
        "status": "VISIBLE_DELIVERY_READY",
        "required_outputs": list(required),
        "presented_artifacts": presented,
        "business_state_status": state.get("status"),
        "assurance_boundary": "CURRENT_SESSION_RESOURCE_AVAILABILITY_ONLY__NOT_A_SECOND_TASK_STATE_AUTHORITY",
    }
