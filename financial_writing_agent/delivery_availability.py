from __future__ import annotations

import hashlib
import json
from io import BytesIO
from zipfile import BadZipFile, ZipFile
from typing import Any, Callable, Mapping

from .delivery_contract import REQUIRED_SUPPLEMENTAL_VISIBLE_OUTPUTS
from .delivery_pipeline import CanonicalDeliveryError, validate_delivery_evidence
from .models import ArtifactKind
from .path_identity import require_task_id, require_word_basename
from .private_research import validate_private_research_brief
from .task_requirements import (
    REQUIREMENT_CONTRACT_VERSION, RequirementError,
    active_requirements_for_scope, authority_digest, validate_requirement_authority,
)
from .task_publication import FULL_UNIVERSE_REQUIREMENT, SCOPE_ASSURANCE


class DeliveryAvailabilityError(ValueError):
    pass


ResourceVerifier = Callable[[Mapping[str, Any]], bool]
ResourceBinaryReader = Callable[[str], Mapping[str, Any] | None]


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


def _canonical_digest(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _private_research_digest(state: Mapping[str, Any]) -> str | None:
    quality = state.get("quality_evidence", {})
    if not isinstance(quality, Mapping):
        return None
    raw = quality.get("private_research_brief")
    if not isinstance(raw, Mapping):
        return None
    try:
        admitted = validate_private_research_brief(raw)
    except ValueError as exc:
        raise DeliveryAvailabilityError(f"owner private research evidence is not admitted: {exc}") from exc
    return _canonical_digest(admitted)


def _supplemental_outputs_for_state(state: Mapping[str, Any]) -> list[str]:
    """Require private Word presentation only when current state actually owns admitted private research."""
    has_private = _private_research_digest(state) is not None
    marker = state.get("private_research_contract_version")
    if not has_private or not marker:
        return []
    return [kind.value for kind in REQUIRED_SUPPLEMENTAL_VISIBLE_OUTPUTS]


def _current_deep_task_requirement_ids(state: Mapping[str, Any]) -> list[str]:
    """The exact child-owned Deep obligations that the visible Word must have checked."""
    if state.get("task_requirement_contract_version") != REQUIREMENT_CONTRACT_VERSION:
        return []
    try:
        authority = validate_requirement_authority(state.get("task_requirement_authority"))
        _require(
            state.get("task_requirement_digest") == authority_digest(authority),
            "current task requirement digest changed before visible delivery",
        )
        return sorted(
            item["requirement_id"]
            for item in active_requirements_for_scope(authority, "FINANCE_DEEP")
        )
    except RequirementError as exc:
        raise DeliveryAvailabilityError(f"current task requirement authority invalid: {exc}") from exc


def build_visible_delivery_receipt(
    state: Mapping[str, Any],
    *,
    resources: list[Mapping[str, Any]],
    resource_verifier: ResourceVerifier | None,
    resource_binary_reader: ResourceBinaryReader | None = None,
) -> dict[str, Any]:
    """Bind current user-visible Word resources to a reconciled Financial article.

    Owner state remains the authority for core business outputs. Current-kernel tasks
    with admitted PrivateResearchBrief also require a supplemental private-research Word
    resource at presentation time. Every visible resource must carry current-session
    canonical Delivery evidence proving builder/check/render/visual closure; hashes or
    prior-session attachments alone cannot bypass that gate.
    """
    _require(isinstance(state, Mapping), "state is required")
    task_id = str(state.get("task_id", "")).strip()
    _require(bool(task_id), "state.task_id is required")
    try:
        require_task_id(task_id)
    except ValueError as exc:
        raise DeliveryAvailabilityError("state.task_id is not a canonical article identity") from exc
    owner_required = state.get("required_outputs")
    _require(isinstance(owner_required, list) and owner_required, "state.required_outputs is required")
    owner_required = [str(kind) for kind in owner_required]
    canonical = state.get("delivery_artifacts")
    _require(isinstance(canonical, Mapping), "state.delivery_artifacts is required")
    _require(set(canonical) == set(owner_required), "owner state must reconcile the complete core output set before visible delivery")
    _require(resource_verifier is not None, "current resource_verifier is required")

    supplemental = _supplemental_outputs_for_state(state)
    presentation_required = [*owner_required, *[kind for kind in supplemental if kind not in owner_required]]
    private_digest = _private_research_digest(state)
    current_deep_requirement_ids = _current_deep_task_requirement_ids(state)

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
        try:
            require_word_basename(file_name)
        except ValueError as exc:
            raise DeliveryAvailabilityError(f"{kind}.file_name must be a canonical basename") from exc
        _require(_hex_sha256(digest), f"{kind}.sha256 must be a 64-character hex digest")
        try:
            verified = bool(resource_verifier(resource))
        except Exception:
            verified = False
        _require(verified, f"{kind}.resource_ref was not verified in the current session")
        if state.get("writing_kernel_version") == "1.0":
            # Current Financial task presentation must be backed by actual
            # externally retrieved DOCX bytes, never metadata/hash/PASS only.
            _require(callable(resource_binary_reader),
                     "CURRENT_FINANCIAL_BINARY_READER_REQUIRED")
            try:
                binary = resource_binary_reader(ref)
            except Exception as exc:
                raise DeliveryAvailabilityError(f"{kind} current DOCX readback failed") from exc
            _require(isinstance(binary, Mapping),
                     f"{kind} current DOCX bytes not available")
            content = binary.get("content")
            _require(isinstance(content, bytes) and content.startswith(b"PK\\x03\\x04"),
                     f"{kind} current resource is not a DOCX binary")
            actual = hashlib.sha256(content).hexdigest()
            _require(actual == digest, f"{kind} actual DOCX bytes differ from declared hash")
            try:
                with ZipFile(BytesIO(content)) as archive:
                    _require(
                        "word/document.xml" in archive.namelist()
                        and "[Content_Types].xml" in archive.namelist(),
                        f"{kind} current resource has no valid Word content",
                    )
                    _require(archive.testzip() is None,
                             f"{kind} current DOCX has corrupt ZIP entries")
            except BadZipFile as exc:
                raise DeliveryAvailabilityError(f"{kind} current DOCX zip is invalid") from exc

        try:
            validate_delivery_evidence(resource)
        except CanonicalDeliveryError as exc:
            raise DeliveryAvailabilityError(f"{kind} canonical delivery evidence failed: {exc}") from exc

        regenerated = resource.get("regenerated_from_durable_source") is True
        is_supplemental = kind in supplemental
        evidence = resource["delivery_evidence"]
        if kind == ArtifactKind.FINANCE_DEEP_DOCX.value and current_deep_requirement_ids:
            binding = evidence.get("task_scope_binding")
            _require(isinstance(binding, Mapping), "FINANCE_DEEP current task requirements have no signed publication-scope evidence")
            _require(binding.get("task_id") == task_id, "FINANCE_DEEP scope bound to another article")
            _require(binding.get("requirement_digest") == state["task_requirement_digest"], "FINANCE_DEEP scope bound to stale task revision")
            _require(binding.get("requirement_revision") == state["task_requirement_authority"]["revision"], "FINANCE_DEEP requirement revision mismatch")
            _require(binding.get("mode") == "FINANCE_DEEP", "FINANCE_DEEP publication-scope mode mismatch")
            _require(binding.get("validated_requirement_ids") == current_deep_requirement_ids, "FINANCE_DEEP did not check every active task requirement")
            _require(binding.get("assurance") == SCOPE_ASSURANCE, "FINANCE_DEEP task-scope assurance is not the supported structural gate")
            _require(
                binding.get("strict_universe_visibility") is (FULL_UNIVERSE_REQUIREMENT in current_deep_requirement_ids),
                "FINANCE_DEEP full-universe visibility requirement was not enforced",
            )
            _require(binding.get("observed_stage") in {"DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT"}, "FINANCE_DEEP was built before editorial-admitted DELIVERY stage")
        if is_supplemental:
            _require(kind == ArtifactKind.PRIVATE_RESEARCH_DOCX.value, f"unsupported supplemental output: {kind}")
            _require(regenerated, f"supplemental {kind} must be rendered from durable owner evidence")
            _require(_nonempty(resource.get("source_ref")), f"supplemental {kind} requires source_ref")
            _require(_nonempty(resource.get("source_identity")), f"supplemental {kind} requires source_identity")
            _require(private_digest is not None, "supplemental private research requires admitted owner PrivateResearchBrief")
            _require(
                evidence.get("source_quality_evidence_sha256") == private_digest,
                "supplemental PRIVATE_RESEARCH_DOCX is not bound to the admitted owner PrivateResearchBrief",
            )
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

        presented[kind] = {
            "file_name": file_name,
            "sha256": digest,
            "resource_ref": ref,
            "supplemental": is_supplemental,
            "regenerated_from_durable_source": regenerated,
            "canonical_sha256": canonical_sha,
            "source_ref": evidence.get("source_ref"),
            "source_identity": evidence.get("source_identity"),
            "source_quality_evidence_sha256": evidence.get("source_quality_evidence_sha256"),
            "task_scope_binding": evidence.get("task_scope_binding"),
            "claim_trace_binding": evidence.get("claim_trace_binding"),
            "mechanical_qa": evidence.get("mechanical_qa"),
            "constraint_qa": evidence.get("constraint_qa"),
            "render_qa": evidence.get("render_qa"),
            "visual_qa": evidence.get("visual_qa"),
            "canonical_delivery_path": evidence.get("canonical_delivery_path"),
        }

    return {
        "schema_version": "1.2",
        "task_id": task_id,
        "status": "VISIBLE_DELIVERY_READY",
        "owner_required_outputs": owner_required,
        "supplemental_required_outputs": supplemental,
        "required_outputs": presentation_required,
        "presented_artifacts": presented,
        "business_state_status": state.get("status"),
        "assurance_boundary": "CURRENT_SESSION_CANONICAL_PRESENTATION_ONLY__NOT_A_SECOND_TASK_STATE_AUTHORITY",
    }
