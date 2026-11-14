"""Read-only, Financial-owned cross-layer assurance projection.

No second task index, method catalog, controller or inferred owner approval.
The live Article Aggregate and requirement source remain authoritative. This
projection inspects their actual persisted bytes and identifies the earliest
unproved business obligation. A local test/CI run is never an external oracle.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .acceptance_gates import SYSTEM_GATES, evaluate_system_acceptance
from .current_admission import validate_state as validate_current_state
from .method_governance import validate_method_catalog
from .owner_guard import TERMINAL_STATUS
from .workflow_spec import BUSINESS_STAGE_NAMES

REQUIRED_PRODUCT_REQUIREMENTS = frozenset(
    [*(f"PR-{i:02d}" for i in range(1, 19)), "PR-04A"]
)
# These are implementation/navigation pointers, NOT a second specification or
# claims of owner-level verification. The source of requirements is the PR text.
REQUIREMENT_IMPLEMENTATION_PATHS: dict[str, tuple[str, ...]] = {
    "PR-01": ("skills/financial-writing-agent/SKILL.md", "financial_writing_agent/current_admission.py"),
    "PR-02": ("financial_writing_agent/intent_governance.py", "financial_writing_agent/owner_lifecycle.py"),
    "PR-03": ("financial_writing_agent/method_governance.py", "knowledge/METHOD_KNOWLEDGE_CATALOG.json"),
    "PR-04": ("financial_writing_agent/private_research.py", "financial_writing_agent/company_identity.py"),
    "PR-04A": ("financial_writing_agent/current_research_sources.py", "financial_writing_agent/private_research.py"),
    "PR-05": ("financial_writing_agent/cognition_governance.py",),
    "PR-06": ("financial_writing_agent/task_publication.py", "financial_writing_agent/story_quality.py"),
    "PR-07": ("financial_writing_agent/story_quality.py", "financial_writing_agent/routing.py"),
    "PR-08": ("financial_writing_agent/story_quality.py",),
    "PR-09": ("financial_writing_agent/story_quality.py",),
    "PR-10": ("financial_writing_agent/story_quality.py", "financial_writing_agent/claim_trace.py"),
    "PR-11": ("financial_writing_agent/story_quality.py",),
    "PR-12": ("financial_writing_agent/editorial_review_authority.py", "financial_writing_agent/story_quality.py"),
    "PR-13": ("financial_writing_agent/writing_kernel.py",),
    "PR-14": ("financial_writing_agent/routing.py", "financial_writing_agent/models.py"),
    "PR-15": ("financial_writing_agent/delivery_pipeline.py", "financial_writing_agent/delivery_availability.py"),
    "PR-16": ("financial_writing_agent/owner_lifecycle.py", "financial_writing_agent/method_governance.py"),
    "PR-17": ("financial_writing_agent/writing_kernel.py",),
    "PR-18": ("financial_writing_agent/resume_compatibility.py",),
}


def _json(root: Path, rel: str) -> dict[str, Any]:
    result = json.loads((root / rel).read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError(f"NOT_AN_OBJECT:{rel}")
    return result


def _git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _safe_repo_ref(root: Path, reference: Any) -> tuple[str, bool]:
    """Unknown remote URLs are not claimed missing or locally verified."""
    if not isinstance(reference, str) or not reference.strip():
        return ("INVALID_REF", False)
    ref = reference.strip()
    if "://" in ref or ref.startswith("chatgpt-library:"):
        return ("EXTERNAL_UNVERIFIED", False)
    path = Path(ref)
    if path.is_absolute() or ".." in path.parts:
        return ("UNSAFE_REF", False)
    return ("LOCAL_READBACK", (root / path).is_file())


def inspect_active_article(root: Path, state_path: Path) -> dict[str, Any]:
    """Reconcile an actual current article, not a synthetic passed-test fixture."""
    relative = state_path.relative_to(root).as_posix()
    state = _json(root, relative)
    task_id = state.get("task_id")
    errors: list[str] = []
    if not isinstance(task_id, str) or state_path.parent.name != task_id:
        errors.append("CURRENT_ARTICLE_ID_PATH_MISMATCH")
    try:
        validate_current_state(state)
    except (ValueError, TypeError, KeyError) as exc:
        errors.append("CURRENT_ARTICLE_AGGREGATE_INVALID:" + str(exc)[:350])
    stage = state.get("current_stage")
    if stage not in BUSINESS_STAGE_NAMES:
        errors.append("CURRENT_ARTICLE_STAGE_UNKNOWN")
    source_observations = []
    for ref in state.get("source_refs", []):
        status, available = _safe_repo_ref(root, ref)
        source_observations.append({
            "ref": ref if isinstance(ref, str) else "<non-string>",
            "source_kind": status,
            "locally_available": available,
        })
        if status in {"UNSAFE_REF", "INVALID_REF"}:
            errors.append("SOURCE_REF_INVALID")
    stage_readbacks = []
    for stage_key, item in state.get("stage_artifacts", {}).items():
        if not isinstance(item, Mapping):
            errors.append("STAGE_ARTIFACT_METADATA_INVALID")
            continue
        ref, declared = item.get("path"), item.get("blob_sha")
        typ, present = _safe_repo_ref(root, ref)
        actual_sha = None
        if typ == "LOCAL_READBACK" and present:
            actual_sha = _git_blob_sha((root / ref).read_bytes())
        valid = (
            isinstance(ref, str)
            and ref.startswith(f"workspaces/articles/{task_id}/")
            and present and actual_sha == declared
        )
        stage_readbacks.append({
            "stage": stage_key, "path": ref, "exact_git_blob_readback": valid,
        })
        if not valid:
            errors.append(f"STAGE_ARTIFACT_READBACK_FAILED:{stage_key}")
    expected = state.get("required_outputs", [])
    delivered = state.get("delivery_artifacts", {})
    output_keys = set(delivered) if isinstance(delivered, Mapping) else set()
    required_keys = set(expected) if isinstance(expected, list) else set()
    is_terminal = state.get("status") == TERMINAL_STATUS
    if is_terminal and output_keys != required_keys:
        errors.append("TERMINAL_OUTPUT_SET_INCOMPLETE")
    private = state.get("quality_evidence", {})
    quality = private if isinstance(private, Mapping) else {}
    open_steps: list[dict[str, Any]] = []
    if stage == "RESEARCH" and state.get("status") == "IN_PROGRESS":
        for key in ("research_decision", "private_research_brief"):
            if key not in quality:
                open_steps.append({
                    "stage": "RESEARCH", "obligation": key,
                    "status": "OPEN__NOT_PERSISTED",
                })
        open_steps.append({
            "stage": "RESEARCH", "obligation": "current_primary_source_and_universe_validation",
            "status": "OPEN__INDEPENDENT_SOURCE_VERIFICATION_NOT_PROVEN",
        })
    if not is_terminal:
        open_steps.append({
            "stage": stage, "obligation": "actual_terminal_article_and_verified_word_delivery",
            "status": "OPEN__ARTICLE_NOT_TERMINAL",
        })
    else:
        open_steps.append({
            "stage": "FINAL_AUDIT", "obligation": "real_external_editorial_reader_outcome",
            "status": "OPEN__EXTERNAL_BUSINESS_ORACLE_NOT_PROVEN",
        })
    if any(record["source_kind"] != "LOCAL_READBACK" or not record["locally_available"]
           for record in source_observations):
        open_steps.append({
            "stage": "RESEARCH", "obligation": "all_original_source_ref_readbacks",
            "status": "OPEN__SOURCE_REFERENCES_NOT_FULLY_OBSERVED",
        })
    return {
        "task_id": task_id, "path": relative, "status": state.get("status"),
        "stage": stage, "next_owner_action": state.get("next_action"),
        "required_output_kinds": sorted(required_keys),
        "recorded_output_kinds": sorted(output_keys),
        "required_output_count": len(required_keys),
        "recorded_output_count": len(output_keys),
        "active_task_requirement_ids": sorted(
            item.get("requirement_id") for item
            in state.get("task_requirement_authority", {}).get("active_requirements", [])
            if isinstance(item, Mapping) and isinstance(item.get("requirement_id"), str)
        ),
        "source_readbacks": source_observations,
        "stage_artifact_readbacks": stage_readbacks,
        "open_obligations": open_steps,
        "structural_violations": sorted(set(errors)),
        "business_outcome": "NOT_READY__LIVE_EXTERNAL_RESULT_NOT_PROVEN",
        "assurance_boundary": "OWNER_AGGREGATE_INSPECTED__NOT_AN_INDEPENDENT_EDITORIAL_REVIEW",
    }


def project_whole_system(root: Path, *, head_sha: str) -> dict[str, Any]:
    """Project all product/operation dependencies from the existing owners."""
    if not re.fullmatch(r"[a-f0-9]{40}", head_sha):
        raise ValueError("EXACT_SOURCE_HEAD_SHA_REQUIRED")
    root = root.resolve()
    violations: list[str] = []
    config = _json(root, "config/FINANCIAL_MANIFEST.json")
    capability = _json(root, "config/FINANCIAL_CAPABILITIES.json")
    data = _json(root, "config/DATA_AUTHORITY.json")
    plugin = _json(root, "config/CHATGPT_FINANCIAL_PLUGIN.json")
    if not (config.get("controller") == capability.get("owner") ==
            "FINANCIAL_WRITING_OWNER"):
        violations.append("FINANCIAL_OWNER_DIVERGENCE")
    if (config.get("skill_entrypoint") != data.get("operating_skill")
            or data.get("article_state_pattern") != "workspaces/articles/{task_id}/STATE.json"
            or data.get("method_catalog") != "knowledge/METHOD_KNOWLEDGE_CATALOG.json"):
        violations.append("CANONICAL_FINANCIAL_AUTHORITY_DIVERGENCE")
    canonical_plugin = config.get("client_skill_plugin", {})
    for key in ("plugin_id", "release_id", "version"):
        if plugin.get(key) != canonical_plugin.get(key):
            violations.append("PLUGIN_RELEASE_IDENTITY_DRIFT:" + key)
    # A runnable guard cannot be silently downgraded back to prompt-only
    # direct-main CAS in one policy surface while CI reports green elsewhere.
    execution = _json(root, "config/EXECUTION_CONTRACT.json")
    client = execution.get("chatgpt_native_execution", {})
    expected_guard = (
        client.get("direct_main_business_mutation_without_guard_allowed") is False
        and client.get("owner_mutation_guard")
        == "financial_writing_agent.whole_system_assurance.audit_repository_business_changes"
        and client.get("candidate_review_entry") == "scripts/system_acceptance_report.py"
        and client.get("native_client_signed_provider_installed_and_tested") is False
    )
    if not expected_guard:
        violations.append("NATIVE_CLIENT_OWNER_EFFECT_GUARD_DRIFT")
    capability_ids = {
        item.get("id") for item in capability.get("capabilities", [])
        if isinstance(item, Mapping)
    }
    if "chatgpt_native_execution_and_github_persistence" not in capability_ids or (
            "AUTHENTICATED_PROVIDER_ACTION_SIGNER_FOR_OWNER_STATE_OR_METHOD_MUTATION"
            not in capability.get("required_external_capabilities_at_execution", [])):
        violations.append("NATIVE_CLIENT_CAPABILITY_BOUNDARY_DRIFT")
    skill = (root / config["skill_entrypoint"]).read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")
    interface = (root / "docs/STANDALONE_INTERFACE.md").read_text(encoding="utf-8")
    if not (
        "signed provider admission" in skill.lower()
        and "do not direct-update `main`" in skill
        and "not an approved business execution route" in interface
        and "No direct ChatGPT" in readme
    ):
        violations.append("NATIVE_CLIENT_INSTRUCTIONS_EFFECT_GUARD_DRIFT")
    requirement_text = (root / "docs/product_requirements.md").read_text(encoding="utf-8")
    ids = set(re.findall(r"^###\s+(PR-\d{2}A?)\b", requirement_text, re.M))
    if ids != REQUIRED_PRODUCT_REQUIREMENTS:
        violations.append("PRODUCT_REQUIREMENT_HEADING_DRIFT")
    if set(REQUIREMENT_IMPLEMENTATION_PATHS) != REQUIRED_PRODUCT_REQUIREMENTS:
        violations.append("REQUIREMENT_TRACE_INDEX_DRIFT")
    requirement_traces = {}
    for ident in sorted(REQUIRED_PRODUCT_REQUIREMENTS):
        pointers = REQUIREMENT_IMPLEMENTATION_PATHS.get(ident, ())
        absent = [p for p in pointers if not (root / p).is_file()]
        requirement_traces[ident] = {
            "canonical_spec_ref": "docs/product_requirements.md#" + ident,
            "implementation_pointers": list(pointers),
            "missing_pointers": absent,
            "implementation_state": (
                "COMPONENT_PRESENT__BEHAVIOR_AND_OWNER_OUTCOME_UNVERIFIED"
                if ident in ids and pointers and not absent
                else "MISSING_OR_DRIFTED_IMPLEMENTATION_POINTER"
            ),
            "independent_business_outcome": "NOT_VERIFIED",
        }
        if absent:
            violations.append("REQUIREMENT_IMPLEMENTATION_MISSING:" + ident)
    mirror_root = root / "skills/financial-writing-agent/references"
    packaged_root = root / "financial_writing_agent/resources/references"
    mirrors = sorted(p.name for p in mirror_root.glob("*.md"))
    if mirrors != sorted(p.name for p in packaged_root.glob("*.md")):
        violations.append("POLICY_REFERENCE_MIRROR_SET_DRIFT")
    for name in mirrors:
        if not (packaged_root / name).is_file() or (
                mirror_root / name).read_bytes() != (packaged_root / name).read_bytes():
            violations.append("POLICY_REFERENCE_MIRROR_BYTES_DRIFT:" + name)
    try:
        catalog = validate_method_catalog(_json(root, data["method_catalog"]))
        method_observation = {
            "revision": catalog.get("governance_revision", 0),
            "record_count": len(catalog["records"]),
            "pending_count": sum(
                bool(item.get("pending_revision")) for item in catalog["records"]
            ),
            "status": "STRUCTURAL_VALIDATION_ONLY__TRANSFER_OUTCOME_UNVERIFIED",
        }
    except (ValueError, KeyError, TypeError) as exc:
        violations.append("METHOD_AUTHORITY_INVALID:" + str(exc)[:350])
        method_observation = {"status": "INVALID"}
    articles: list[dict[str, Any]] = []
    historical = []
    for state_file in sorted((root / "workspaces/articles").glob("*/STATE.json")):
        marker_file = state_file.parent / "ARTIFACT_STATUS.json"
        if marker_file.is_file():
            try:
                marker = _json(root, marker_file.relative_to(root).as_posix())
                is_current = (marker.get("workspace_lifecycle") == "CURRENT" and
                              marker.get("statuses", {}).get("STATE.json") == "KEEP_CURRENT")
                if marker.get("workspace_lifecycle") == "MIGRATED_HISTORY" and (
                        "KEEP_CURRENT" in marker.get("statuses", {}).values()):
                    violations.append("MIGRATED_HISTORY_HAS_ACTIVE_STATE:" + state_file.parent.name)
            except (ValueError, TypeError) as exc:
                violations.append("ARTICLE_LIFECYCLE_MARKER_INVALID:" + str(exc)[:200])
                is_current = False
        else:
            is_current = False
        if is_current:
            try:
                inspected = inspect_active_article(root, state_file)
                articles.append(inspected)
                violations.extend(
                    f"{state_file.parent.name}:{problem}"
                    for problem in inspected["structural_violations"]
                )
            except (ValueError, TypeError, KeyError) as exc:
                violations.append(f"ACTIVE_ARTICLE_READ_FAILED:{state_file.parent.name}:{str(exc)[:300]}")
        else:
            historical.append(state_file.parent.name)
    if not articles:
        violations.append("NO_CURRENT_ARTICLE_AGGREGATE_MARKED")
    quality = _json(root, data["editorial_readiness"])
    readiness = quality.get("current_readiness", {})
    readiness_result = {
        key: (value.get("status", "UNKNOWN") if isinstance(value, Mapping) else "INVALID")
        for key, value in readiness.items()
    }
    external = evaluate_system_acceptance(head_sha=head_sha, code_tests_passed=False)
    open_control = [
        "NATIVE_CHAT_DIRECT_GITHUB_WRITES_DO_NOT_EXECUTE_PYTHON_ADMISSION_GUARD",
        "LIVE_PROVIDER_AUTHORIZATION_AND_CAS_EFFECT_READBACK_NOT_REPRODUCED_HERE",
        "INDEPENDENT_EDITORIAL_AND_READER_ORACLE_NOT_REPRODUCED_HERE",
    ]
    return {
        "schema_version": "1.0",
        "product": "financial_writing",
        "exact_source_head_sha": head_sha,
        "authority": "READ_ONLY_PROJECTION__CANONICAL_FILES_REMAIN_OWNERS",
        "product_requirement_total": len(REQUIRED_PRODUCT_REQUIREMENTS),
        "product_requirement_traces": requirement_traces,
        "method_catalog": method_observation,
        "current_articles": articles,
        "historical_article_ids": historical,
        "editorial_readiness": readiness_result,
        "external_system_acceptance": external["system_status"],
        "open_system_gates": external["open_gates"],
        "unverified_runtime_boundaries": open_control,
        "structural_violations": sorted(set(violations)),
        "whole_product_status": "NOT_READY__REQUIRES_LIVE_ARTICLE_AND_EXTERNAL_BUSINESS_EVIDENCE",
        "next_legal_step": (
            "REPAIR_STRUCTURAL_VIOLATIONS_BEFORE_ANY_STATE_MUTATION"
            if violations else
            "CLOSE_AUTHENTICATED_EXECUTION_PATH_AND_INDEPENDENT_BUSINESS_EVIDENCE__NO_UNREQUESTED_ARTICLE_PRODUCTION"
        ),
    }


def audit_repository_business_changes(
    changed_paths: list[str],
    *,
    before_reader: Any,
    after_reader: Any,
) -> dict[str, Any]:
    """Cross-entry effect audit for GitHub PR/main production comparisons.

    Reads exact two-revision bytes with injected provider readers. An LLM writing
    files on GitHub does NOT itself execute current_admission or prove owner
    approval; newly changed owner state must carry a provider-verifiable signed
    action and pass the canonical owner-state transition checker. Historical
    workspaces are not mutable present-tense truth. This is an additional CI
    detector, NOT branch-protection/independent provider attestation.
    """
    violations: list[str] = []
    reviewed: list[dict[str, str]] = []
    article_tasks: dict[str, set[str]] = {}
    for rel in sorted(set(changed_paths)):
        if not isinstance(rel, str) or not rel.strip() or rel.startswith("/") or ".." in Path(rel).parts:
            violations.append("INVALID_MUTATION_PATH")
            continue
        path = Path(rel)
        if path.as_posix() == "knowledge/METHOD_KNOWLEDGE_CATALOG.json":
            old_bytes, new_bytes = before_reader(rel), after_reader(rel)
            if not isinstance(old_bytes, bytes) or not isinstance(new_bytes, bytes):
                violations.append("METHOD_AUTHORITY_REMOVED_OR_UNREADABLE")
            else:
                try:
                    old = validate_method_catalog(json.loads(old_bytes))
                    new = validate_method_catalog(json.loads(new_bytes))
                    earlier = old.get("change_history", [])
                    later = new.get("change_history", [])
                    if not (len(later) == len(earlier) + 1
                            and later[:-1] == earlier
                            and new.get("governance_revision") == old.get("governance_revision", 0) + 1):
                        violations.append("METHOD_MUTATION_HISTORY_NOT_APPEND_ONLY")
                except (ValueError, TypeError, KeyError) as exc:
                    violations.append("METHOD_MUTATION_NOT_PROVIDER_ADMITTED:" + str(exc)[:180])
            reviewed.append({"path": rel, "scope": "METHOD_AUTHORITY"})
            continue
        if path.parts[:2] != ("workspaces", "articles"):
            continue
        if len(path.parts) < 4:
            violations.append("INVALID_ARTICLE_WORKSPACE_MUTATION")
            continue
        article_tasks.setdefault(path.parts[2], set()).add(rel)

    for task_id, touched in sorted(article_tasks.items()):
        prefix = f"workspaces/articles/{task_id}/"
        state_ref = prefix + "STATE.json"
        marker_ref = prefix + "ARTIFACT_STATUS.json"
        old_marker = before_reader(marker_ref)
        new_marker = after_reader(marker_ref)
        marker_raw = old_marker if old_marker is not None else new_marker
        if marker_raw is not None:
            try:
                marker = json.loads(marker_raw)
                if marker.get("workspace_lifecycle") == "MIGRATED_HISTORY":
                    violations.append("MIGRATED_ARTICLE_HISTORY_MUTATED:" + task_id)
                    reviewed.append({"path": prefix, "scope": "IMMUTABLE_HISTORY"})
                    continue
            except (ValueError, TypeError, AttributeError):
                violations.append("ARTICLE_LIFECYCLE_MARKER_UNREADABLE:" + task_id)
                continue
        prior_raw = before_reader(state_ref)
        candidate_raw = after_reader(state_ref)
        if state_ref not in touched:
            violations.append("ARTICLE_ARTIFACT_CHANGED_WITHOUT_STATE_REVISION:" + task_id)
            reviewed.append({"path": state_ref, "scope": "OWNER_ARTICLE_MUTATION"})
            continue
        if not isinstance(candidate_raw, bytes):
            violations.append("OWNER_ARTICLE_STATE_DELETED_OR_UNREADABLE:" + task_id)
            continue
        try:
            candidate = json.loads(candidate_raw)
            validate_current_state(candidate)
            if candidate.get("task_id") != task_id:
                raise ValueError("ARTICLE_ID_PATH_MISMATCH")
            if prior_raw is None:
                before = None
                previous_sha = None
                if candidate.get("current_stage") != "INTAKE" or len(candidate.get("execution_receipts", [])) != 1:
                    raise ValueError("NEW_ARTICLE_MUST_START_AT_INTAKE")
            else:
                before = json.loads(prior_raw)
                validate_current_state(before)
                previous_sha = _git_blob_sha(prior_raw)
                prior_receipts = before.get("execution_receipts", [])
                next_receipts = candidate.get("execution_receipts", [])
                if not (len(next_receipts) == len(prior_receipts) + 1
                        and next_receipts[:-1] == prior_receipts):
                    raise ValueError("ARTICLE_RECEIPT_HISTORY_NOT_APPEND_ONLY")
            last_receipt = candidate["execution_receipts"][-1]
            bindings = last_receipt.get("input_bindings", {})
            if not (isinstance(bindings, Mapping)
                    and bindings.get("authorization_contract_version") == "1.0"
                    and isinstance(bindings.get("authorization_verification"), Mapping)):
                raise ValueError("UNSIGNED_NATIVE_CHAT_ARTICLE_MUTATION_DENIED")
            claimed_previous = bindings.get("previous_state_blob_sha")
            if claimed_previous != ("NEW_FILE" if previous_sha is None else previous_sha):
                raise ValueError("ARTICLE_PREVIOUS_GIT_BLOB_MISMATCH")
            from .standalone_runtime import _verify_persisted_action_authorization_history
            _verify_persisted_action_authorization_history(candidate)
            operation = bindings["authorization_verification"].get("operation")
            if before is not None:
                from .owner_guard import validate_feedback_update, validate_transition
                if operation == "ADVANCE_STAGE":
                    validate_transition(
                        before, candidate, previous_state_blob_sha=previous_sha,
                    )
                elif operation == "ATTACH_FEEDBACK":
                    validate_feedback_update(
                        before, candidate, previous_state_blob_sha=previous_sha,
                    )
                else:
                    # Do not mistake a signed *intention* for a proof that
                    # arbitrary before/after bytes equal a legal owner effect.
                    raise ValueError("UNREPLAYED_OWNER_OPERATION_REQUIRES_EXECUTABLE_ADAPTER:" + str(operation))
            elif operation != "CREATE_ARTICLE":
                raise ValueError("NEW_ARTICLE_NOT_AUTHORIZED_AS_CREATE")
        except (ValueError, KeyError, TypeError) as exc:
            violations.append("OWNER_ARTICLE_MUTATION_NOT_ADMITTED:" + task_id + ":" + str(exc)[:240])
        reviewed.append({"path": state_ref, "scope": "OWNER_ARTICLE_MUTATION"})

    return {
        "schema_version": "1.0",
        "business_paths_changed": sum(
            int(item["scope"] in {"OWNER_ARTICLE_MUTATION", "METHOD_AUTHORITY", "IMMUTABLE_HISTORY"})
            for item in reviewed
        ),
        "reviewed_effect_boundaries": reviewed,
        "violations": sorted(set(violations)),
        "status": (
            "REJECTED__UNTRUSTED_OR_UNREPLAYED_BUSINESS_CHANGE" if violations
            else "NO_UNADMITTED_BUSINESS_CHANGE_OBSERVED"
        ),
        "assurance": "DETERMINISTIC_TWO_REVISION_AUDIT__NOT_BRANCH_PROTECTION_OR_EXTERNAL_BUSINESS_OUTCOME",
    }
