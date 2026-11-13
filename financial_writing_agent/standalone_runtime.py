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
from io import BytesIO
from zipfile import BadZipFile, ZipFile
from copy import deepcopy
from typing import Any, Callable, Mapping

from . import current_admission, owner_lifecycle, proactive_resolution
from .intent_governance import (
    FinancialIntentEvidenceError, verify_requirement_change_intent, verify_nonbinding_owner_intent,
)
from .method_governance import (
    CATALOG_PATH, METHOD_ACTIONS, MethodGovernanceError,
    mutate_method_catalog, query_methods, validate_method_catalog,
    admitted_method_usage_snapshot, method_dependency_drift,
)
from .path_identity import require_article_path, require_task_id
from .provider_attestation import (
    verify_action_authorization, verify_method_action_authorization,
    verify_persisted_action_authorization, FinancialProviderAttestationError,
)
from .current_research_sources import CurrentResearchEvidenceError, verify_current_research_sources
from .company_identity import CompanyIdentityError, require_retained_universe_reconciliation
from .editorial_review_authority import (IndependentEditorialEvidenceError,
                                         verify_external_editorial_review)

DOMAIN_ID = "financial_writing"
CONTRACT_VERSION = "1.0"
STATE_ROOT = "workspaces/articles"
_ACTION_ID = re.compile(r"[A-Za-z0-9_.:-]{1,180}\Z")
_SHA = re.compile(r"[a-f0-9]{40}\Z")
OPERATIONS = frozenset({
    "CREATE_ARTICLE", "CHANGE_REQUIREMENTS", "ADVANCE_STAGE", "ATTACH_FEEDBACK",
    "RESUME_BLOCKED", "RECORD_PROACTIVE_RESOLUTION", "REVIEW_SYSTEM_IMPACT",
    "RECORD_OWNER_INTENT", "REOPEN_METHOD_DEPENDENCY",
})
CREATE_KEYS = frozenset({
    "prompt", "source_refs", "target_platforms", "distribution_mode",
    "distribution_mode_source", "distribution_mode_override_evidence",
})
REQUIREMENT_KEYS = frozenset({"evidence_ref", "upserts", "retire_ids", "intent_evidence"})
STAGE_KEYS = frozenset({
    "artifact_key", "artifact_path", "artifact_blob_sha", "review_status",
    "revision_target", "delivery_artifacts", "audit_artifact",
    "decision_envelope", "private_research_brief", "story_blueprints",
    "publication_fitnesses", "requirement_satisfaction",
    "supplemental_delivery_artifacts",
})
FEEDBACK_KEYS = frozenset({"sample", "system_impact"})
OWNER_INTENT_KEYS = frozenset({"intent_evidence", "summary"})
METHOD_REOPEN_KEYS = frozenset()
RECOVERY_KEYS = frozenset({"repair_evidence"})
PROACTIVE_KEYS = frozenset({
    "target", "attempted_sources", "evidence_refs", "outcome",
    "candidate", "confidence", "contradictions_or_unknowns",
    "validation_plan", "safe_to_continue",
})
IMPACT_KEYS = frozenset({
    "signal_id", "problem_statement", "root_cause_layer", "generalization_scope",
    "alternatives", "selected_mechanism", "selection_rationale", "authority_surface",
    "regression_or_eval_plan", "evidence_refs", "decision", "decision_reason",
    "maintenance_ref", "validation_refs", "assurance_ceiling", "remaining_open",
})
ACTION_PARAM_KEYS = {
    "CREATE_ARTICLE": CREATE_KEYS,
    "CHANGE_REQUIREMENTS": REQUIREMENT_KEYS,
    "ADVANCE_STAGE": STAGE_KEYS,
    "ATTACH_FEEDBACK": FEEDBACK_KEYS,
    "RESUME_BLOCKED": RECOVERY_KEYS,
    "RECORD_PROACTIVE_RESOLUTION": PROACTIVE_KEYS,
    "REVIEW_SYSTEM_IMPACT": IMPACT_KEYS,
    "RECORD_OWNER_INTENT": OWNER_INTENT_KEYS,
    "REOPEN_METHOD_DEPENDENCY": METHOD_REOPEN_KEYS,
}


class FinancialAdmissionError(ValueError):
    """Invalid scope, stale state or denied action. No business write accepted."""


class FinancialEffectUnverified(RuntimeError):
    """Remote mutation occurred or was attempted but its exact effect is unknown."""


StateReader = Callable[[str], Mapping[str, Any] | None]
CASWriter = Callable[[str, str | None, str], Mapping[str, Any]]
ArtifactReader = Callable[[str], Mapping[str, Any] | None]
AuthorizationVerifier = Callable[[Mapping[str, Any]], Mapping[str, Any] | None]


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
    """Verify provider's actual Git bytes, not caller-asserted metadata."""
    try:
        raw = reader(path)
    except Exception as exc:
        raise FinancialEffectUnverified("FINANCIAL_PROVIDER_READ_FAILED") from exc
    if raw is None:
        return None
    _require(isinstance(raw, Mapping), "INVALID_PROVIDER_STATE_RESPONSE")
    state, sha, content = raw.get("state"), raw.get("blob_sha"), raw.get("content")
    _require(isinstance(state, Mapping) and _valid_sha(sha) and isinstance(content, (str, bytes)),
             "INVALID_PROVIDER_STATE_RESPONSE")
    _require(_blob_sha(content) == sha, "PROVIDER_STATE_BLOB_SHA_MISMATCH")
    try:
        parsed = json.loads(content)
    except (ValueError, TypeError) as exc:
        raise FinancialAdmissionError("PROVIDER_STATE_JSON_INVALID") from exc
    candidate = deepcopy(dict(state))
    _require(_strict_json_equal(candidate, parsed), "PROVIDER_STATE_CONTENT_MISMATCH")
    return candidate, sha

def _read_method_catalog(
    reader: StateReader | None,
) -> tuple[dict[str, Any], str]:
    _require(callable(reader), "FINANCIAL_METHOD_CATALOG_READER_REQUIRED")
    source = _read(reader, CATALOG_PATH)
    _require(source is not None, "FINANCIAL_METHOD_CATALOG_NOT_AVAILABLE")
    try:
        return validate_method_catalog(source[0]), source[1]
    except MethodGovernanceError as exc:
        raise FinancialAdmissionError(str(exc)) from exc


def _current_method_ids(state: Mapping[str, Any]) -> list[str]:
    quality = state.get("quality_evidence", {})
    decision = quality.get("research_decision", {}) if isinstance(quality, Mapping) else {}
    learned = decision.get("learned_items", []) if isinstance(decision, Mapping) else []
    return sorted({
        item for item in learned if isinstance(item, str)
        and item.startswith("METHOD-") and re.fullmatch(r"METHOD-[A-Z0-9_-]+", item)
    })


def _persisted_method_snapshot(state: Mapping[str, Any]) -> Mapping[str, Any] | None:
    for receipt in reversed(state.get("execution_receipts", [])):
        if receipt.get("stage") != "RESEARCH":
            continue
        snapshot = receipt.get("input_bindings", {}).get("method_usage_snapshot")
        if isinstance(snapshot, Mapping):
            return snapshot
    return None


def _diagnose_persisted_method_drift(
    state: Mapping[str, Any], reader: StateReader | None,
) -> tuple[list[dict[str, Any]], str]:
    prior = _persisted_method_snapshot(state)
    _require(prior is not None, "FINANCIAL_METHOD_NO_ADMITTED_USAGE_SNAPSHOT")
    catalog, catalog_sha = _read_method_catalog(reader)
    try:
        changes = method_dependency_drift(catalog, prior)
    except MethodGovernanceError as exc:
        raise FinancialAdmissionError(str(exc)) from exc
    return changes, catalog_sha


def _verify_article_method_usage(
    candidate: dict[str, Any], *,
    leaving_stage: str,
    method_catalog_reader: StateReader | None,
) -> dict[str, Any] | None:
    ids = _current_method_ids(candidate)
    prior = _persisted_method_snapshot(candidate)
    if leaving_stage == "RESEARCH":
        if not ids:
            return None
        catalog, catalog_sha = _read_method_catalog(method_catalog_reader)
        try:
            fresh = admitted_method_usage_snapshot(catalog, ids)
        except MethodGovernanceError as exc:
            raise FinancialAdmissionError(str(exc)) from exc
        candidate["execution_receipts"][-1]["input_bindings"]["method_usage_snapshot"] = fresh
        candidate["execution_receipts"][-1]["input_bindings"]["method_catalog_blob_sha"] = catalog_sha
        current_admission.validate_state(candidate)
        return {"method_catalog_blob_sha": catalog_sha, "usage_snapshot": fresh}

    # A lawful REVISE / reentry to RESEARCH already invalidates the old evidence.
    if candidate.get("current_stage") in {"INTAKE", "RESEARCH"}:
        return None
    if prior is None:
        _require(not ids, "FINANCIAL_METHOD_REFERENCE_WITHOUT_ADMITTED_SNAPSHOT")
        return None
    changes, catalog_sha = _diagnose_persisted_method_drift(candidate, method_catalog_reader)
    _require(not changes, "FINANCIAL_METHOD_DEPENDENCY_STALE__REOPEN_REQUIRED")
    return {
        "method_catalog_blob_sha": catalog_sha,
        "usage_snapshot": dict(prior), "stale_methods": [],
    }


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
    reconciliation = None
    active_ids = {
        item.get("requirement_id")
        for item in candidate.get("task_requirement_authority", {}).get("active_requirements", [])
        if isinstance(item, Mapping)
    }
    if key == "RESEARCH" and "full_universe_research_pool" in active_ids:
        from .schemas import ResearchPackage
        try:
            parsed = json.loads(content)
            research = ResearchPackage.model_validate(parsed)
            reconciliation = require_retained_universe_reconciliation(candidate["task_id"], research)
        except (ValueError, TypeError, CompanyIdentityError) as exc:
            raise FinancialAdmissionError("FINANCIAL_RESEARCH_UNIVERSE_NOT_RECONCILED") from exc
        _require(reconciliation is not None, "FINANCIAL_TASK_RESEARCH_BASELINE_NOT_CONFIGURED")
    return {"artifact_key": key, "path": path, "verified_blob_sha": expected,
            "retained_universe_reconciliation": reconciliation}


def _verify_requirement_satisfaction_sources(
    satisfaction: list[Mapping[str, Any]],
    research_sources: Mapping[str, Any],
    *,
    stage_artifact_path: str | None = None,
) -> dict[str, Any]:
    """Verify evidence refs resolve to bytes read in this admission.

    This proves source availability and byte identity only; it does not certify
    that the source semantically supports the requirement.
    """
    snapshots = research_sources.get("snapshots")
    _require(isinstance(snapshots, list), "FINANCIAL_RESEARCH_SOURCE_READBACK_MISSING")
    known = {
        item.get("source_ref_sha256")
        for item in snapshots if isinstance(item, Mapping)
    }
    stage_artifact_digest = None
    if stage_artifact_path:
        stage_artifact_digest = hashlib.sha256(stage_artifact_path.encode("utf-8")).hexdigest()
        known.add(stage_artifact_digest)
    checked = 0
    for item in satisfaction:
        _require(isinstance(item, Mapping),
                 "FINANCIAL_REQUIREMENT_SATISFACTION_RECORD_INVALID")
        refs = item.get("evidence_refs")
        _require(isinstance(refs, list) and bool(refs),
                 "FINANCIAL_REQUIREMENT_SATISFACTION_EVIDENCE_REFS_MISSING")
        ref_digests: set[str] = set()
        for ref in refs:
            _require(isinstance(ref, str) and bool(ref.strip()),
                     "FINANCIAL_REQUIREMENT_SATISFACTION_SOURCE_REF_INVALID")
            digest = hashlib.sha256(ref.encode("utf-8")).hexdigest()
            _require(
                digest in known,
                "FINANCIAL_REQUIREMENT_SATISFACTION_UNREAD_SOURCE",
            )
            ref_digests.add(digest)
            checked += 1
        if stage_artifact_digest is not None:
            _require(
                stage_artifact_digest in ref_digests,
                "FINANCIAL_REQUIREMENT_SATISFACTION_CURRENT_STAGE_ARTIFACT_NOT_BOUND",
            )
    return {
        "checked_evidence_ref_count": checked,
        "assurance": "SOURCE_BYTE_READBACK_ONLY__SEMANTIC_SUPPORT_NOT_CERTIFIED",
        "semantic_support_verified": False,
    }


def _latest_research_source_readback(state: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """Reuse only a previously admitted RESEARCH source snapshot set."""
    receipts = state.get("execution_receipts", [])
    if not isinstance(receipts, list):
        return None
    for receipt in reversed(receipts):
        if not isinstance(receipt, Mapping) or receipt.get("stage") != "RESEARCH":
            continue
        bindings = receipt.get("input_bindings", {})
        if not isinstance(bindings, Mapping):
            continue
        readback = bindings.get("research_source_readback")
        if isinstance(readback, Mapping) and isinstance(readback.get("snapshots"), list):
            return readback
    return None


def _verify_product_word_bytes(
    candidate: Mapping[str, Any], reader: ArtifactReader | None,
) -> dict[str, Any]:
    """Read current-article DOCX bytes before DELIVERY and FINAL_AUDIT state writes.

    This does not certify independent editorial judgment or replace the
    separately required per-page visible delivery inspection.
    """
    _require(callable(reader), "FINANCIAL_WORD_BINARY_READER_REQUIRED")
    outputs = candidate.get("delivery_artifacts", {})
    _require(isinstance(outputs, Mapping) and bool(outputs),
             "FINANCIAL_WORD_OUTPUT_MANIFEST_MISSING")
    verified: list[dict[str, str]] = []
    seen_refs: set[str] = set()
    from docx import Document

    for kind, meta in sorted(outputs.items()):
        _require(isinstance(meta, Mapping), f"FINANCIAL_WORD_METADATA_INVALID:{kind}")
        ref = meta.get("resource_ref")
        try:
            path = require_article_path(ref, candidate["task_id"])
        except ValueError as exc:
            raise FinancialAdmissionError(f"FINANCIAL_WORD_RESOURCE_REF_INVALID:{kind}") from exc
        _require(path.rsplit("/", 1)[-1] == meta["file_name"],
                 f"FINANCIAL_WORD_FILE_NAME_MISMATCH:{kind}")
        _require(path not in seen_refs, f"FINANCIAL_WORD_RESOURCE_REUSED:{kind}")
        seen_refs.add(path)
        try:
            observed = reader(path)
        except Exception as exc:
            raise FinancialEffectUnverified("FINANCIAL_WORD_PROVIDER_READ_FAILED") from exc
        _require(isinstance(observed, Mapping), f"FINANCIAL_WORD_BINARY_MISSING:{kind}")
        binary, claimed_sha = observed.get("content"), observed.get("blob_sha")
        _require(isinstance(binary, bytes) and binary[:2] == b"PK",
                 f"FINANCIAL_WORD_DOCX_BYTES_INVALID:{kind}")
        _require(_blob_sha(binary) == claimed_sha,
                 f"FINANCIAL_WORD_PROVIDER_BLOB_MISMATCH:{kind}")
        _require(hashlib.sha256(binary).hexdigest() == str(meta["sha256"]).lower(),
                 f"FINANCIAL_WORD_BINARY_SHA256_MISMATCH:{kind}")
        try:
            with ZipFile(BytesIO(binary)) as archive:
                names = set(archive.namelist())
                _require("word/document.xml" in names and "[Content_Types].xml" in names,
                         f"FINANCIAL_WORD_DOCX_STRUCTURE_INVALID:{kind}")
                _require(archive.testzip() is None, f"FINANCIAL_WORD_DOCX_CORRUPT:{kind}")
            Document(BytesIO(binary))
        except (BadZipFile, KeyError, ValueError, OSError) as exc:
            raise FinancialAdmissionError(f"FINANCIAL_WORD_DOCX_OPEN_FAILED:{kind}") from exc

        # A valid ZIP/DOCX and matching hash are not sufficient for publication.
        # Require the canonical Delivery receipt, exact render/page inspection,
        # source identity and (for long-form) task-scope + claim-trace bindings.
        try:
            from .delivery_pipeline import validate_delivery_evidence
            validate_delivery_evidence(meta)
        except Exception as exc:
            raise FinancialAdmissionError(
                f"FINANCIAL_WORD_DELIVERY_EVIDENCE_INVALID:{kind}"
            ) from exc
        delivery = meta.get("delivery_evidence")
        _require(isinstance(delivery, Mapping),
                 f"FINANCIAL_WORD_DELIVERY_EVIDENCE_MISSING:{kind}")
        draft = candidate.get("stage_artifacts", {}).get("DRAFT")
        _require(isinstance(draft, Mapping),
                 "FINANCIAL_WORD_CURRENT_DRAFT_REFERENCE_MISSING")
        _require(
            delivery.get("source_ref") == draft.get("path")
            and delivery.get("source_identity") == f"git-blob:{draft.get('blob_sha')}",
            f"FINANCIAL_WORD_DRAFT_SOURCE_BINDING_MISMATCH:{kind}",
        )
        if kind in {"FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"}:
            scope = delivery.get("task_scope_binding")
            _require(isinstance(scope, Mapping),
                     f"FINANCIAL_WORD_TASK_SCOPE_BINDING_MISSING:{kind}")
            _require(
                scope.get("task_id") == candidate.get("task_id")
                and scope.get("requirement_digest") == candidate.get("task_requirement_digest")
                and scope.get("requirement_revision")
                    == candidate.get("task_requirement_authority", {}).get("revision")
                and scope.get("mode") == kind.removesuffix("_DOCX")
                and scope.get("observed_stage") == "DELIVERY"
                and scope.get("draft_artifact_path") == draft.get("path")
                and scope.get("draft_artifact_blob_sha") == draft.get("blob_sha"),
                f"FINANCIAL_WORD_TASK_SCOPE_BINDING_MISMATCH:{kind}",
            )
            trace = delivery.get("claim_trace_binding")
            _require(
                isinstance(trace, Mapping)
                and trace.get("task_id") == candidate.get("task_id")
                and trace.get("assurance")
                    == "SOURCE_TEXT_AND_NUMERALS_OBSERVED__SEMANTIC_ENTAILMENT_NOT_VERIFIED"
                and type(trace.get("traced_block_count")) is int
                and trace["traced_block_count"] >= 1
                and type(trace.get("read_source_snapshot_count")) is int
                and trace["read_source_snapshot_count"] >= 1,
                f"FINANCIAL_WORD_SOURCE_TRACE_BINDING_INVALID:{kind}",
            )
        render = delivery.get("render_inspection_receipt")
        verified.append({
            "kind": kind, "resource_ref": path,
            "blob_sha": claimed_sha, "sha256": hashlib.sha256(binary).hexdigest(),
            "delivery_evidence_sha256": meta.get("delivery_evidence_sha256"),
            "rendered_page_count": render.get("rendered_page_count") if isinstance(render, Mapping) else None,
        })
    return {
        "assurance": "CANONICAL_BUILD__CURRENT_DRAFT_BOUND__SOURCE_TRACE__RENDERED_PAGE_READBACK__EDITORIAL_INDEPENDENCE_OPEN",
        "verified_count": len(verified), "files": verified,
    }


def _verify_visible_delivery(
    candidate: Mapping[str, Any],
    supplemental_resources: list[Mapping[str, Any]],
    reader: ArtifactReader | None,
) -> dict[str, Any]:
    """Verify the complete visible output set before the terminal state CAS."""
    _require(callable(reader), "FINANCIAL_VISIBLE_DELIVERY_BINARY_READER_REQUIRED")
    _require(
        isinstance(supplemental_resources, list)
        and all(isinstance(item, Mapping) for item in supplemental_resources),
        "FINANCIAL_SUPPLEMENTAL_DELIVERY_RESOURCES_INVALID",
    )

    cache: dict[str, Mapping[str, Any] | None] = {}

    def read_once(ref: str) -> Mapping[str, Any] | None:
        if ref not in cache:
            try:
                cache[ref] = reader(ref)
            except Exception as exc:
                raise FinancialEffectUnverified(
                    "FINANCIAL_VISIBLE_DELIVERY_PROVIDER_READ_FAILED"
                ) from exc
        return cache[ref]

    source_stage_readbacks: list[dict[str, str]] = []
    for stage_key in ("RESEARCH", "DRAFT"):
        stage_ref = candidate.get("stage_artifacts", {}).get(stage_key)
        _require(isinstance(stage_ref, Mapping),
                 f"FINANCIAL_VISIBLE_DELIVERY_{stage_key}_REFERENCE_MISSING")
        try:
            stage_path = require_article_path(stage_ref.get("path"), candidate["task_id"])
        except (KeyError, ValueError) as exc:
            raise FinancialAdmissionError(
                f"FINANCIAL_VISIBLE_DELIVERY_{stage_key}_PATH_INVALID"
            ) from exc
        observed_stage = read_once(stage_path)
        _require(isinstance(observed_stage, Mapping),
                 f"FINANCIAL_VISIBLE_DELIVERY_{stage_key}_BYTES_MISSING")
        content, claimed_blob = observed_stage.get("content"), observed_stage.get("blob_sha")
        _require(
            isinstance(content, (bytes, str))
            and _valid_sha(claimed_blob)
            and _blob_sha(content) == claimed_blob == stage_ref.get("blob_sha"),
            f"FINANCIAL_VISIBLE_DELIVERY_SOURCE_STAGE_BYTES_MISMATCH:{stage_key}",
        )
        source_stage_readbacks.append({
            "stage": stage_key, "path": stage_path, "verified_blob_sha": claimed_blob,
        })

    research = candidate.get("stage_artifacts", {}).get("RESEARCH")
    if supplemental_resources:
        _require(isinstance(research, Mapping),
                 "FINANCIAL_PRIVATE_RESEARCH_STAGE_REFERENCE_MISSING")
        expected_source = research.get("path")
        expected_identity = f"git-blob:{research.get('blob_sha')}"
        seen = {
            item.get("resource_ref")
            for item in candidate.get("delivery_artifacts", {}).values()
            if isinstance(item, Mapping)
        }
        for item in supplemental_resources:
            _require(item.get("kind") == "PRIVATE_RESEARCH_DOCX",
                     "FINANCIAL_SUPPLEMENTAL_OUTPUT_KIND_INVALID")
            _require(item.get("regenerated_from_durable_source") is True,
                     "FINANCIAL_PRIVATE_RESEARCH_WORD_NOT_REGENERATED")
            try:
                resource_path = require_article_path(item.get("resource_ref"), candidate["task_id"])
            except (KeyError, ValueError) as exc:
                raise FinancialAdmissionError(
                    "FINANCIAL_PRIVATE_RESEARCH_RESOURCE_PATH_INVALID"
                ) from exc
            _require(resource_path not in seen,
                     "FINANCIAL_VISIBLE_DELIVERY_RESOURCE_REUSED")
            seen.add(resource_path)
            _require(
                item.get("source_ref") == expected_source
                and item.get("source_identity") == expected_identity,
                "FINANCIAL_PRIVATE_RESEARCH_SOURCE_IDENTITY_MISMATCH",
            )
            evidence = item.get("delivery_evidence")
            _require(isinstance(evidence, Mapping)
                     and evidence.get("source_ref") == expected_source
                     and evidence.get("source_identity") == expected_identity,
                     "FINANCIAL_PRIVATE_RESEARCH_DELIVERY_EVIDENCE_SOURCE_MISMATCH")

    def verify_resource(resource: Mapping[str, Any]) -> bool:
        try:
            ref = require_article_path(resource.get("resource_ref"), candidate["task_id"])
        except (KeyError, ValueError):
            return False
        observed = read_once(ref)
        if not isinstance(observed, Mapping):
            return False
        content, claimed_blob = observed.get("content"), observed.get("blob_sha")
        if not isinstance(content, bytes) or _blob_sha(content) != claimed_blob:
            return False
        return hashlib.sha256(content).hexdigest() == str(resource.get("sha256", "")).lower()

    try:
        from .delivery_availability import (
            DeliveryAvailabilityError, build_visible_delivery_receipt,
        )
        resources = [
            *list(candidate.get("delivery_artifacts", {}).values()),
            *[dict(item) for item in supplemental_resources],
        ]
        receipt = build_visible_delivery_receipt(
            candidate,
            resources=resources,
            resource_verifier=verify_resource,
            resource_binary_reader=read_once,
        )
    except DeliveryAvailabilityError as exc:
        raise FinancialAdmissionError(
            f"FINANCIAL_VISIBLE_DELIVERY_NOT_READY:{exc}"
        ) from exc
    receipt["source_stage_artifact_readback"] = source_stage_readbacks
    return receipt


def _verify_persisted_action_authorization_history(
    state: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify signed receipts that declare the provider-authorization contract.

    Earlier receipts remain immutable self-attested provenance and are counted
    as legacy; every receipt written by the current standalone action port must
    carry a complete, re-verifiable provider signature.
    """
    receipts = state.get("execution_receipts", [])
    _require(isinstance(receipts, list) and receipts,
             "FINANCIAL_ACTION_RECEIPT_HISTORY_MISSING")
    verified = 0
    legacy = 0
    seen_action_ids: set[str] = set()
    seen_nonces: set[tuple[str, str]] = set()
    for receipt in receipts:
        bindings = receipt.get("input_bindings", {})
        if bindings.get("authorization_contract_version") is None:
            legacy += 1
            continue
        _require(bindings.get("authorization_contract_version") == "1.0",
                 "FINANCIAL_ACTION_RECEIPT_AUTHORIZATION_VERSION_UNSUPPORTED")
        proof = bindings.get("authorization_verification")
        previous_sha = bindings.get("previous_state_blob_sha")
        executor = receipt.get("executor_identity")
        _require(isinstance(executor, str) and executor.startswith("financial:"),
                 "FINANCIAL_ACTION_RECEIPT_EXECUTOR_SCOPE_INVALID")
        action_id = executor[len("financial:"):]
        _require(bool(action_id), "FINANCIAL_ACTION_RECEIPT_ACTION_ID_MISSING")
        _require(action_id not in seen_action_ids,
                 "FINANCIAL_ACTION_RECEIPT_ACTION_ID_REPLAYED")
        seen_action_ids.add(action_id)
        _require(isinstance(proof, Mapping),
                 "FINANCIAL_ACTION_RECEIPT_ATTESTATION_MISSING")
        nonce = proof.get("nonce")
        provider_id = proof.get("provider_id")
        _require(isinstance(provider_id, str) and isinstance(nonce, str)
                 and len(nonce) >= 16
                 and (provider_id, nonce) not in seen_nonces,
                 "FINANCIAL_ACTION_RECEIPT_NONCE_MISSING_OR_REPLAYED")
        seen_nonces.add((provider_id, nonce))
        expected_previous = None if previous_sha == "NEW_FILE" else previous_sha
        operation = proof.get("operation")
        _require(operation in OPERATIONS,
                 "FINANCIAL_ACTION_RECEIPT_OPERATION_INVALID")
        try:
            verify_persisted_action_authorization(
                proof,
                expected_claims={
                    "approved": True,
                    "action_id": action_id,
                    "task_id": state["task_id"],
                    "operation": operation,
                    "expected_state_blob_sha": expected_previous,
                },
            )
        except Exception as exc:
            raise FinancialAdmissionError(
                "FINANCIAL_PERSISTED_ACTION_AUTHORIZATION_INVALID"
            ) from exc
        verified += 1
    return {
        "verified_signed_receipts": verified,
        "legacy_self_attested_receipts": legacy,
        "assurance": (
            "ALL_RECEIPTS_SIGNED_AND_REVERIFIED" if legacy == 0
            else "SIGNED_NEW_RECEIPTS__LEGACY_HISTORY_RETAINED_AS_UNVERIFIED_PROVENANCE"
        ),
    }


def observe_article(task_id: str, *, state_reader: StateReader) -> dict[str, Any]:
    """Read actual child-owned business state; never imply editorial acceptance."""
    path = _state_path(task_id)
    record = _read(state_reader, path)
    _require(record is not None, "FINANCIAL_ARTICLE_NOT_FOUND")
    state, sha = record
    _require(state["task_id"] == task_id, "FINANCIAL_ARTICLE_ID_MISMATCH")
    current_admission.validate_state(state)
    authorization_history = _verify_persisted_action_authorization_history(state)
    authority = state["task_requirement_authority"]
    visible_delivery_receipt = None
    for receipt in reversed(state.get("execution_receipts", [])):
        if not isinstance(receipt, Mapping):
            continue
        bindings = receipt.get("input_bindings", {})
        if isinstance(bindings, Mapping) and isinstance(bindings.get("visible_delivery_receipt"), Mapping):
            visible_delivery_receipt = dict(bindings["visible_delivery_receipt"])
            break
    open_impacts = [
        {"signal_id": entry.get("signal_id"), "status": entry.get("status")}
        for entry in state.get("open_system_impact", [])
    ]
    blocked_target = (
        owner_lifecycle._blocking_recovery_cursor(state)
        if state["status"] == "BLOCKED" else None
    )
    return {
        "contract_version": CONTRACT_VERSION, "domain_id": DOMAIN_ID,
        "task_id": task_id, "state_ref": path, "state_blob_sha": sha,
        "stage": state["current_stage"], "business_status": state["status"],
        "next_action": state["next_action"],
        "blocked_recovery_target": blocked_target,
        "open_system_impact": open_impacts,
        "active_requirement_ids": sorted(
            item["requirement_id"] for item in authority["active_requirements"]
        ),
        "open_nonbinding_intents": [
            {"intent_id": event["intent_id"], "intent": event["intent"],
             "status": event["status"], "summary": event["summary"]}
            for event in state.get("intent_history", [])
            if event.get("status") == "OPEN__NONBINDING"
        ],
        "requirement_revision": authority["revision"],
        "requirement_digest": state["task_requirement_digest"],
        "required_outputs": list(state["required_outputs"]),
        "recorded_outputs": sorted(state.get("delivery_artifacts", {})),
        "visible_delivery_status": (
            visible_delivery_receipt.get("status")
            if visible_delivery_receipt is not None else "NOT_VERIFIED"
        ),
        "visible_delivery_receipt": visible_delivery_receipt,
        "authorization_history": authorization_history,
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
    allowed = ACTION_PARAM_KEYS[op]
    _require(set(params).issubset(allowed), "FINANCIAL_ACTION_PARAMETERS_SCOPE_EXCEEDED")
    return r


def admit_article_action(
    proposal: Mapping[str, Any],
    *,
    state_reader: StateReader,
    cas_writer: CASWriter | None,
    authorization_verifier: AuthorizationVerifier | None,
    artifact_reader: ArtifactReader | None = None,
    source_snapshot_reader: Callable[[str], Mapping[str, Any] | None] | None = None,
    independent_editorial_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
    owner_instruction_reader: Callable[[str], Mapping[str, Any] | None] | None = None,
    owner_semantic_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
    method_catalog_reader: StateReader | None = None,
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
        authorization_attestation = verify_action_authorization(
            authorization_verifier(deepcopy(r)), request=r,
        )
    except Exception as exc:
        raise FinancialAdmissionError("FINANCIAL_AUTHORIZATION_NOT_VERIFIED__ATTESTATION_FAILED") from exc
    # Preserve the complete signed receipt (never the raw user message) so a
    # later independent audit can re-verify provider, audience, actor, scope,
    # freshness, nonce and signature rather than trusting a hand-picked summary.
    authorization_evidence = deepcopy(authorization_attestation)
    path = _state_path(r["task_id"])
    observed = _read(state_reader, path)
    op = r["operation"]
    params = deepcopy(dict(r["parameters"]))
    supplemental_delivery_artifacts = params.pop("supplemental_delivery_artifacts", None)
    if supplemental_delivery_artifacts is not None:
        _require(
            op == "ADVANCE_STAGE" and observed is not None
            and observed[0].get("current_stage") == "FINAL_AUDIT",
            "FINANCIAL_SUPPLEMENTAL_DELIVERY_ONLY_ALLOWED_AT_FINAL_AUDIT",
        )
        _require(
            isinstance(supplemental_delivery_artifacts, list)
            and all(isinstance(item, Mapping) for item in supplemental_delivery_artifacts),
            "FINANCIAL_SUPPLEMENTAL_DELIVERY_RESOURCES_INVALID",
        )
    owner_intent_evidence = None
    nonbinding_intent_evidence = None
    if op == "RECORD_OWNER_INTENT":
        try:
            nonbinding_intent_evidence = verify_nonbinding_owner_intent(
                params.pop("intent_evidence", None),
                owner_instruction_reader=owner_instruction_reader,
            )
        except FinancialIntentEvidenceError as exc:
            raise FinancialAdmissionError(str(exc)) from exc
    if op == "CHANGE_REQUIREMENTS":
        try:
            owner_intent_evidence = verify_requirement_change_intent(
                params.pop("intent_evidence", None),
                evidence_ref=params.get("evidence_ref"),
                upserts=params.get("upserts"), retire_ids=params.get("retire_ids"),
                owner_instruction_reader=owner_instruction_reader,
                owner_semantic_verifier=owner_semantic_verifier,
                existing_requirements=(
                    observed[0].get("task_requirement_authority", {}).get("active_requirements", [])
                    if observed is not None else []
                ),
                expected_state_blob_sha=r["expected_state_blob_sha"],
            )
        except FinancialIntentEvidenceError as exc:
            raise FinancialAdmissionError(str(exc)) from exc
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
        _verify_persisted_action_authorization_history(state)
        call = {
            "previous_state_blob_sha": previous_sha,
            "executor_identity": f"financial:{r['action_id']}",
            **params,
        }
        if op == "ADVANCE_STAGE":
            candidate = current_admission.advance_state(state, **call)
        elif op == "CHANGE_REQUIREMENTS":
            candidate = current_admission.apply_task_requirement_change(state, **call)
        elif op == "ATTACH_FEEDBACK":
            candidate = current_admission.attach_material_feedback(state, **call)
        elif op == "RESUME_BLOCKED":
            candidate = owner_lifecycle.resume_blocked_state(state, **call)
        elif op == "RECORD_PROACTIVE_RESOLUTION":
            candidate = proactive_resolution.record_proactive_resolution_state(state, **call)
        elif op == "REVIEW_SYSTEM_IMPACT":
            candidate = owner_lifecycle.review_system_impact_state(state, **call)
        elif op == "RECORD_OWNER_INTENT":
            candidate = owner_lifecycle.record_nonbinding_intent_state(
                state, verified_intent=nonbinding_intent_evidence, **call,
            )
        elif op == "REOPEN_METHOD_DEPENDENCY":
            changes, catalog_sha = _diagnose_persisted_method_drift(
                state, method_catalog_reader,
            )
            _require(bool(changes), "FINANCIAL_METHOD_NO_DEPENDENCY_CHANGE")
            candidate = owner_lifecycle.reopen_method_dependent_article_state(
                state,
                previous_state_blob_sha=previous_sha,
                executor_identity=call["executor_identity"],
                method_dependency_changes=changes,
                verified_catalog_blob_sha=catalog_sha,
            )
        else:
            raise FinancialAdmissionError("FINANCIAL_ACTION_DISPATCH_UNKNOWN")

    candidate["execution_receipts"][-1]["input_bindings"]["authorization_contract_version"] = "1.0"
    candidate["execution_receipts"][-1]["input_bindings"]["authorization_verification"] = authorization_evidence
    if owner_intent_evidence is not None:
        candidate["execution_receipts"][-1]["input_bindings"]["owner_intent_verification"] = owner_intent_evidence
    current_admission.validate_state(candidate)
    _verify_persisted_action_authorization_history(candidate)
    method_usage = None
    if op == "ADVANCE_STAGE" and observed is not None:
        method_usage = _verify_article_method_usage(
            candidate, leaving_stage=observed[0]["current_stage"],
            method_catalog_reader=method_catalog_reader,
        )
    stage_bytes = _verify_stage_bytes(candidate, artifact_reader) if op == "ADVANCE_STAGE" else None
    word_bytes = None
    if op == "ADVANCE_STAGE" and observed is not None and observed[0]["current_stage"] in {
        "DELIVERY", "FINAL_AUDIT",
    }:
        word_bytes = _verify_product_word_bytes(candidate, artifact_reader)
        candidate["execution_receipts"][-1]["input_bindings"]["product_word_binary_readback"] = word_bytes
        current_admission.validate_state(candidate)
    research_sources = None
    satisfaction_readback = None
    if op == "ADVANCE_STAGE" and observed is not None and observed[0]["current_stage"] == "RESEARCH":
        try:
            research_sources = verify_current_research_sources(
                candidate["quality_evidence"]["private_research_brief"],
                source_reader=source_snapshot_reader,
            )
        except CurrentResearchEvidenceError as exc:
            raise FinancialAdmissionError(str(exc)) from exc
        satisfaction = candidate["execution_receipts"][-1]["input_bindings"].get(
            "task_requirement_satisfaction", []
        )
        if satisfaction:
            satisfaction_readback = _verify_requirement_satisfaction_sources(
                satisfaction, research_sources,
                stage_artifact_path=stage_bytes["path"] if stage_bytes is not None else None,
            )
        candidate["execution_receipts"][-1]["input_bindings"]["research_source_readback"] = research_sources
        if satisfaction_readback is not None:
            candidate["execution_receipts"][-1]["input_bindings"]["task_requirement_satisfaction_source_readback"] = satisfaction_readback
        current_admission.validate_state(candidate)
    elif op == "ADVANCE_STAGE" and observed is not None:
        satisfaction = candidate["execution_receipts"][-1]["input_bindings"].get(
            "task_requirement_satisfaction", []
        )
        if satisfaction:
            prior_research_sources = _latest_research_source_readback(candidate)
            try:
                satisfaction_readback = _verify_requirement_satisfaction_sources(
                    satisfaction,
                    prior_research_sources if prior_research_sources is not None else {"snapshots": []},
                    stage_artifact_path=stage_bytes["path"] if stage_bytes is not None else None,
                )
            except FinancialAdmissionError:
                raise
            candidate["execution_receipts"][-1]["input_bindings"]["task_requirement_satisfaction_source_readback"] = satisfaction_readback
            current_admission.validate_state(candidate)
    independent_editorial_proof = None
    if op == "ADVANCE_STAGE" and observed is not None and observed[0]["current_stage"] == "EDITORIAL_AUDIT":
        try:
            independent_editorial_proof = verify_external_editorial_review(
                candidate, candidate["quality_evidence"].get("publication_fitnesses", []),
                draft_reader=artifact_reader,
                provider_verifier=independent_editorial_verifier,
            )
        except IndependentEditorialEvidenceError as exc:
            raise FinancialAdmissionError(str(exc)) from exc
        if independent_editorial_proof is not None:
            candidate["execution_receipts"][-1]["input_bindings"]["independent_editorial_proof"] = independent_editorial_proof
            current_admission.validate_state(candidate)
    visible_delivery_receipt = None
    if op == "ADVANCE_STAGE" and observed is not None and observed[0]["current_stage"] == "FINAL_AUDIT":
        visible_delivery_receipt = _verify_visible_delivery(
            candidate,
            supplemental_delivery_artifacts or [],
            artifact_reader,
        )
        candidate["execution_receipts"][-1]["input_bindings"]["supplemental_delivery_artifacts"] = deepcopy(
            supplemental_delivery_artifacts or []
        )
        candidate["execution_receipts"][-1]["input_bindings"]["visible_delivery_receipt"] = visible_delivery_receipt
        current_admission.validate_state(candidate)

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
        "product_word_binary_readback": word_bytes,
        "research_source_readback": research_sources,
        "method_usage_readback": method_usage,
        "independent_editorial_review_readback": independent_editorial_proof,
        "visible_delivery_receipt": visible_delivery_receipt,
        "child_state_cas_verified": True,
        "independent_editorial_quality_verified": False,
        "owner_outcome_verified": False,
    }


def observe_method_catalog(
    *, catalog_reader: StateReader, knowledge_id: str | None = None,
    operational_only: bool = False,
) -> dict[str, Any]:
    """Read the single existing Financial method catalog; no new task ledger."""
    record = _read(catalog_reader, CATALOG_PATH)
    _require(record is not None, "FINANCIAL_METHOD_CATALOG_UNAVAILABLE")
    raw, sha = record
    try:
        catalog = validate_method_catalog(raw)
        methods = query_methods(catalog, knowledge_id=knowledge_id,
                                operational_only=operational_only)
    except MethodGovernanceError as exc:
        raise FinancialAdmissionError(str(exc)) from exc
    history = catalog.get("change_history", [])
    closed_revisions = {
        event["target_change_revision"] for event in history
        if event.get("operation") == "VERIFY_IMPACT"
        and isinstance(event.get("impact_verification"), Mapping)
    }
    return {
        "domain_id": DOMAIN_ID, "catalog_ref": CATALOG_PATH,
        "catalog_blob_sha": sha,
        "governance_revision": catalog.get("governance_revision", 0),
        "records": methods,
        "open_revalidation": [
            {
                "change_revision": event["revision"],
                "knowledge_id": event["knowledge_id"],
                "affected_stages": event["affected_stages"],
            }
            for event in history
            if event.get("impact_review_state")
            == "OPEN__AFFECTED_WORKFLOWS_REVALIDATION_REQUIRED"
            and event["revision"] not in closed_revisions
        ],
        "live_article_effect_verified": False,
    }


def admit_method_action(
    request: Mapping[str, Any],
    *,
    catalog_reader: StateReader,
    catalog_cas_writer: CASWriter | None,
    authorization_verifier: AuthorizationVerifier | None,
    promotion_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
    impact_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Independent Financial-domain method CRUD via existing catalog Git CAS.

    This separate *action scope* writes only knowledge/METHOD_KNOWLEDGE_CATALOG,
    not an independent business state controller or a method Task Index.
    It can be served by the same Financial Skill/client and trusted Git provider.
    """
    _require(isinstance(request, Mapping), "FINANCIAL_METHOD_ACTION_INVALID")
    required = {"schema_version", "domain_id", "action_id", "operation",
                "expected_catalog_blob_sha", "parameters"}
    _require(set(request) == required, "FINANCIAL_METHOD_ACTION_FIELDS_INVALID")
    _require(request.get("schema_version") == CONTRACT_VERSION
             and request.get("domain_id") == DOMAIN_ID,
             "FINANCIAL_METHOD_ACTION_DOMAIN_INVALID")
    _require(isinstance(request.get("action_id"), str)
             and _ACTION_ID.fullmatch(request["action_id"]) is not None,
             "FINANCIAL_METHOD_ACTION_ID_INVALID")
    operation = request.get("operation")
    _require(operation in METHOD_ACTIONS, "FINANCIAL_METHOD_ACTION_NOT_SUPPORTED")
    _require(_valid_sha(request.get("expected_catalog_blob_sha")),
             "FINANCIAL_METHOD_EXPECTED_SHA_REQUIRED")
    params = request.get("parameters")
    _require(isinstance(params, Mapping), "FINANCIAL_METHOD_ACTION_PARAMS_INVALID")
    allowed = {
        "knowledge_id", "proposed_record", "decision_envelope", "evidence_refs",
        "affected_stages", "promotion_evidence", "impact_target_revision",
        "impact_evidence",
    }
    _require(set(params).issubset(allowed), "FINANCIAL_METHOD_ACTION_PARAMS_EXCEEDED")
    _require(callable(authorization_verifier) and callable(catalog_cas_writer),
             "FINANCIAL_METHOD_TRUSTED_AUTH_AND_CAS_REQUIRED")
    try:
        authorization_attestation = verify_method_action_authorization(
            authorization_verifier(deepcopy(dict(request))), request=request,
        )
    except Exception as exc:
        raise FinancialAdmissionError(
            "FINANCIAL_METHOD_AUTHORIZATION_ATTESTATION_NOT_VERIFIED"
        ) from exc
    # Preserve the complete signed receipt for later append-only catalog verification.
    authorization_evidence = deepcopy(authorization_attestation)

    observed = _read(catalog_reader, CATALOG_PATH)
    _require(observed is not None, "FINANCIAL_METHOD_CATALOG_UNAVAILABLE")
    before, previous_sha = observed
    _require(previous_sha == request["expected_catalog_blob_sha"],
             "FINANCIAL_METHOD_CATALOG_CHANGED_CONCURRENTLY")
    try:
        candidate, receipt = mutate_method_catalog(
            before, operation=operation,
            knowledge_id=params.get("knowledge_id"),
            proposed_record=params.get("proposed_record"),
            decision_envelope=params.get("decision_envelope"),
            evidence_refs=params.get("evidence_refs"),
            affected_stages=params.get("affected_stages"),
            promotion_evidence=params.get("promotion_evidence"),
            promotion_verifier=promotion_verifier,
            impact_target_revision=params.get("impact_target_revision"),
            impact_evidence=params.get("impact_evidence"),
            impact_verifier=impact_verifier,
            authorization_evidence=authorization_evidence,
            action_request=request,
            observed_catalog_blob_sha=previous_sha,
        )
    except MethodGovernanceError as exc:
        raise FinancialAdmissionError(str(exc)) from exc
    payload = _canonical_payload(candidate)
    expected_new_sha = _blob_sha(payload)
    try:
        issued = catalog_cas_writer(CATALOG_PATH, previous_sha, payload)
    except Exception as exc:
        raise FinancialEffectUnverified("FINANCIAL_METHOD_WRITE_OUTCOME_UNKNOWN") from exc
    if not isinstance(issued, Mapping) or issued.get("blob_sha") != expected_new_sha:
        raise FinancialEffectUnverified("FINANCIAL_METHOD_WRITE_SHA_MISMATCH")
    verified = _read(catalog_reader, CATALOG_PATH)
    if (verified is None or verified[1] != expected_new_sha
            or not _strict_json_equal(verified[0], candidate)):
        raise FinancialEffectUnverified("FINANCIAL_METHOD_CATALOG_READBACK_MISMATCH")
    validate_method_catalog(verified[0])
    return {
        "contract_version": CONTRACT_VERSION, "domain_id": DOMAIN_ID,
        "catalog_ref": CATALOG_PATH, "action_id": request["action_id"],
        "operation": operation, "knowledge_id": params.get("knowledge_id"),
        "previous_catalog_blob_sha": previous_sha,
        "observed_catalog_blob_sha": expected_new_sha,
        "provider_commit_ref": issued.get("commit_ref"),
        "governance_revision": candidate["governance_revision"],
        "method_change_receipt": receipt,
        "authorization_verification": authorization_evidence,
        "method_catalog_cas_verified": True,
        "live_article_effect_verified": False,
    }
