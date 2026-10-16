from __future__ import annotations

from typing import Any, Callable, Mapping

from .delivery_contract import REQUIRED_SUPPLEMENTAL_VISIBLE_OUTPUTS
from .delivery_pipeline import CanonicalDeliveryError, validate_delivery_evidence
from .models import ArtifactKind


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


def _supplemental_outputs_for_state(state: Mapping[str, Any]) -> list[str]:
    """Require private Word presentation only when current state actually owns admitted private research."""
    quality = state.get("quality_evidence", {})
    has_private = isinstance(quality, Mapping) and isinstance(quality.get("private_research_brief"), Mapping)
    marker = state.get("private_research_contract_version")
    if not has_private or not marker:
        return []
    return [kind.value for kind in REQUIRED_SUPPLEMENTAL_VISIBLE_OUTPUTS]


def build_visible_delivery_receipt(
    state: Mapping[str, Any],
    *,
    resources: list[Mapping[str, Any]],
    resource_verifier: ResourceVerifier | None,
) -> dict[str, Any]:
    """Bind current user-visible Word resources to a reconciled Financial article.

    Owner state remains the authority for core business outputs. Current-kernel tasks
    with admitted PrivateResearchBrief also require a supplemental private-research Word
    resource at presentation time. Every visible resource must carry canonical Delivery
    evidence proving builder/check/render/visual closure; hashes or old attachments alone
    cannot bypass that gate.
    """
    _require(isinstance(state, Mapping), "state is required")
    task_id = str(state.get("task_id", "")).strip()
    _require(bool(task_id), "state.task_id is required")
    owner_required = state.get("required_outputs")
    _require(isinstance(owner_required, list) and owner_required, "state.required_outputs is required")
    owner_required = [str(kind) for kind in owner_required]
    canonical = state.get("delivery_artifacts")
    _require(isinstance(canonical, Mapping), "state.delivery_artifacts is required")
    _require(set(canonical) == set(owner_required), "owner state must reconcile the complete core output set before visible delivery")
    _require(resource_verifier is not None, "current resource_verifier is required")

    supplemental = _supplemental_outputs_for_state(state)
    presentation_required = [*owner_required, *[kind for kind in supplemental if kind not in owner_required]]

    by_kind: dict[str, Mapping[str, Any]] = {}
    for resource in resources:
        _require(isinstance(resource, Mapping), "visible delivery resource must be an object")
        kind = str(resource.get("kind", "")).strip()
        _require(kind in presentation_required, f"unexpected visible delivery resource kind: {kind or 'MISSING'}")
        _require(kind not in by_kind, f"duplicate visible delivery resource kind: {kind}")
        by_kind[kind] = resource
    _require(
        set(by_kind) == set(presentation_required),
        f"visible delivery output mismatch: required={sorted(presentation_required)}, actual={sorted(by_kind)}",
    )

    presented: dict[str, dict[str, Any]] = {}
    for kind in presentation_required:
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

        try:
            validate_delivery_evidence(resource)
        except CanonicalDeliveryError as exc:
            raise DeliveryAvailabilityError(f"{kind} canonical delivery evidence failed: {exc}") from exc

        regenerated = resource.get("regenerated_from_durable_source") is True
        is_supplemental = kind in supplemental
        if is_supplemental:
            _require(kind == ArtifactKind.PRIVATE_RESEARCH_DOCX.value, f"unsupported supplemental output: {kind}")
            _require(regenerated, f"supplemental {kind} must be rendered from durable owner evidence")
            _require(_nonempty(resource.get("source_ref")), f"supplemental {kind} requires source_ref")
            _require(_nonempty(resource.get("source_identity")), f"supplemental {kind} requires source_identity")
            canonical_sha = None
        else:
            canonical_meta = canonical[kind]
            canonical_sha = str(canonical_meta.get("sha256", "")).strip().lower()
            _require(_hex_sha256(canonical_sha), f"canonical {kind}.sha256 is invalid")
            if regenerated:
                _require(_nonempty(resource.get("source_ref")), f"regenerated {kind} requires source_ref")
                _require(_nonempty(resource.get("source_identity")), f"regenerated {kind} requires source_identity")
            else:
                _require(digest == canonical_sha, f"non-regenerated {kind} binary hash must match canonical owner state")

        evidence = resource["delivery_evidence"]
        presented[kind] = {
            "file_name": file_name,
            "sha256": digest,
            "resource_ref": ref,
            "supplemental": is_supplemental,
            "regenerated_from_durable_source": regenerated,
            "canonical_sha256": canonical_sha,
            "source_ref": evidence.get("source_ref"),
            "source_identity": evidence.get("source_identity"),
            "mechanical_qa": evidence.get("mechanical_qa"),
            "constraint_qa": evidence.get("constraint_qa"),
            "render_qa": evidence.get("render_qa"),
            "visual_qa": evidence.get("visual_qa"),
            "canonical_delivery_path": evidence.get("canonical_delivery_path"),
        }

    return {
        "schema_version": "1.1",
        "task_id": task_id,
        "status": "VISIBLE_DELIVERY_READY",
        "owner_required_outputs": owner_required,
        "supplemental_required_outputs": supplemental,
        "required_outputs": presentation_required,
        "presented_artifacts": presented,
        "business_state_status": state.get("status"),
        "assurance_boundary": "CURRENT_SESSION_CANONICAL_PRESENTATION_ONLY__NOT_A_SECOND_TASK_STATE_AUTHORITY",
    }
