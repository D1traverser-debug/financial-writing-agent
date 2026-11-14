from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Callable, Mapping
from uuid import uuid4

from . import current_admission, standalone_runtime
from .path_identity import require_article_path
from .schemas import ResearchPackage
from .writing_kernel import (
    INTERNAL_PORTFOLIO_STAGE_SEQUENCE,
    _all_requirement_scopes,
    _portfolio_modes,
    execute_portfolio_stage,
    rebind_portfolio_context_requirements,
    resume_portfolio_context,
    start_portfolio_context,
    validate_portfolio_context,
)


class PortfolioCoordinatorError(RuntimeError):
    """The Financial stage coordinator could not prove a safe resumable transition."""


ArtifactBundleWriter = Callable[[Mapping[str, bytes]], Mapping[str, Any]]


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def _read_provider_artifact(reader: Callable[[str], Any], path: str) -> tuple[bytes, str]:
    try:
        observed = reader(path)
    except Exception as exc:
        raise PortfolioCoordinatorError("PORTFOLIO_PROVIDER_ARTIFACT_READ_FAILED") from exc
    if not isinstance(observed, Mapping):
        raise PortfolioCoordinatorError("PORTFOLIO_PROVIDER_ARTIFACT_MISSING")
    content = observed.get("content")
    blob_sha = observed.get("blob_sha")
    if isinstance(content, str):
        content = content.encode("utf-8")
    if not isinstance(content, bytes) or not isinstance(blob_sha, str):
        raise PortfolioCoordinatorError("PORTFOLIO_PROVIDER_ARTIFACT_RESPONSE_INVALID")
    if standalone_runtime._blob_sha(content) != blob_sha:
        raise PortfolioCoordinatorError("PORTFOLIO_PROVIDER_ARTIFACT_BLOB_SHA_MISMATCH")
    return content, blob_sha


def _latest_context_ref(state: Mapping[str, Any]) -> Mapping[str, Any] | None:
    receipts = state.get("execution_receipts", [])
    if not isinstance(receipts, list):
        raise PortfolioCoordinatorError("PORTFOLIO_OWNER_RECEIPT_HISTORY_INVALID")
    for receipt in reversed(receipts):
        if not isinstance(receipt, Mapping):
            continue
        bindings = receipt.get("input_bindings", {})
        ref = bindings.get("portfolio_context_ref") if isinstance(bindings, Mapping) else None
        if isinstance(ref, Mapping):
            return deepcopy(dict(ref))
    return None


def _requirement_contexts(
    state: Mapping[str, Any],
    required_outputs: list[str],
) -> dict[str, dict[str, Any]]:
    modes = _portfolio_modes(required_outputs)
    interaction_required = "PLATFORM_INTERACTION_PACK_DOCX" in required_outputs
    scopes = _all_requirement_scopes(modes, interaction_required)
    return {
        scope: current_admission.requirement_context_for_scope(state, scope)
        for scope in scopes
    }


def _has_full_universe_requirement(state: Mapping[str, Any]) -> bool:
    authority = state.get("task_requirement_authority", {})
    requirements = authority.get("active_requirements", []) if isinstance(authority, Mapping) else []
    return any(
        isinstance(item, Mapping)
        and item.get("requirement_id") == "full_universe_research_pool"
        for item in requirements
    )


def _stage_payload(
    context: Mapping[str, Any],
    *,
    stage: str,
    state: Mapping[str, Any],
) -> dict[str, Any]:
    shared = context["shared"]
    products = context["products"]
    interaction = context["interaction"]

    if stage == "RESEARCH":
        if _has_full_universe_requirement(state):
            raw = shared.get("research_package")
            try:
                package = ResearchPackage.model_validate(raw)
            except Exception as exc:
                raise PortfolioCoordinatorError(
                    "PORTFOLIO_FULL_UNIVERSE_TYPED_RESEARCH_PACKAGE_REQUIRED"
                ) from exc
            return package.model_dump(mode="json")
        return {
            "decision_envelope": deepcopy(shared.get("decision_envelope")),
            "private_research_brief": deepcopy(shared.get("private_research_brief")),
            "research_outputs": {
                key: deepcopy(value)
                for key, value in shared.items()
                if key not in {
                    "decision_envelope", "private_research_brief",
                    "research_audit_result", "audited_evidence",
                }
            },
        }
    if stage == "RESEARCH_AUDIT":
        return deepcopy(shared.get("research_audit_result", {}))
    if stage == "EDITORIAL":
        return {
            "story_blueprints": {
                mode: deepcopy(item.get("story_blueprint"))
                for mode, item in products.items()
            }
        }
    if stage == "TITLE":
        return {
            "headline_decisions": {
                mode: deepcopy(item.get("headline_decision"))
                for mode, item in products.items()
            }
        }
    if stage == "DRAFT":
        return {
            "longform_products": {
                mode: {
                    key: deepcopy(item.get(key))
                    for key in ("draft", "edited_draft", "publication_candidate")
                    if key in item
                }
                for mode, item in products.items()
            },
            "platform_interaction_pack": (
                deepcopy(interaction.get("platform_interaction_pack"))
                if isinstance(interaction, Mapping) else None
            ),
        }
    if stage == "EDITORIAL_AUDIT":
        return {
            "publication_fitnesses": {
                mode: deepcopy(item.get("publication_fitness"))
                for mode, item in products.items()
                if item.get("publication_fitness") is not None
            },
            "platform_interaction_fitness": (
                deepcopy(interaction.get("platform_interaction_fitness"))
                if isinstance(interaction, Mapping) else None
            ),
        }
    raise PortfolioCoordinatorError(f"PORTFOLIO_STAGE_ARTIFACT_UNSUPPORTED:{stage}")


def _business_stage_artifact(
    context: Mapping[str, Any],
    *,
    stage: str,
    state: Mapping[str, Any],
) -> dict[str, Any]:
    result = context.get("last_stage_result")
    if not isinstance(result, Mapping) or result.get("stage") != stage:
        raise PortfolioCoordinatorError("PORTFOLIO_STAGE_RESULT_NOT_BOUND_TO_CONTEXT")
    return {
        "schema_version": "1.0",
        "artifact_type": "FINANCIAL_PORTFOLIO_BUSINESS_STAGE",
        "task_id": context["task_id"],
        "stage": stage,
        "requirement_digest": context["requirement_digest"],
        "owner_state_stage_before": state["current_stage"],
        "stage_result": deepcopy(dict(result)),
        "payload": _stage_payload(context, stage=stage, state=state),
        "pass_receipt_sha256s": [
            item["receipt_sha256"]
            for item in context["trace"]
            if item.get("business_stage") == stage
        ],
        "assurance": "TYPED_STAGE_OUTPUT_ENVELOPE__OWNER_ADMISSION_AND_PROVIDER_READBACK_REQUIRED",
    }


def _context_ref(
    *,
    task_id: str,
    context: Mapping[str, Any],
    content: bytes,
) -> dict[str, Any]:
    digest = hashlib.sha256(content).hexdigest()
    path = (
        f"workspaces/articles/{task_id}/portfolio/contexts/"
        f"{context['generation']}-{digest}.json"
    )
    return {
        "path": require_article_path(path, task_id),
        "blob_sha": standalone_runtime._blob_sha(content),
        "sha256": digest,
        "stage": context["current_stage"],
        "generation": context["generation"],
    }


def _stage_artifact_ref(
    *,
    task_id: str,
    stage: str,
    receipt: Mapping[str, Any],
    content: bytes,
) -> dict[str, str]:
    receipt_sha = str(receipt.get("receipt_sha256", ""))
    if len(receipt_sha) != 64:
        raise PortfolioCoordinatorError("PORTFOLIO_STAGE_RECEIPT_SHA_INVALID")
    path = f"workspaces/articles/{task_id}/stages/{stage}-{receipt_sha}.json"
    return {
        "path": require_article_path(path, task_id),
        "blob_sha": standalone_runtime._blob_sha(content),
    }


def _write_and_verify_bundle(
    files: Mapping[str, bytes],
    *,
    writer: ArtifactBundleWriter,
    artifact_reader: Callable[[str], Any],
    context_reader: Callable[[str], Any],
    context_path: str,
) -> dict[str, str]:
    if not callable(writer):
        raise PortfolioCoordinatorError("PORTFOLIO_ARTIFACT_BUNDLE_WRITER_REQUIRED")
    try:
        issued = writer(dict(files))
    except Exception as exc:
        raise PortfolioCoordinatorError("PORTFOLIO_ARTIFACT_BUNDLE_WRITE_FAILED") from exc
    if not isinstance(issued, Mapping) or not isinstance(issued.get("blob_shas"), Mapping):
        raise PortfolioCoordinatorError("PORTFOLIO_ARTIFACT_BUNDLE_WRITE_RECEIPT_INVALID")
    verified: dict[str, str] = {}
    for path, expected_content in files.items():
        expected_sha = standalone_runtime._blob_sha(expected_content)
        if issued["blob_shas"].get(path) != expected_sha:
            raise PortfolioCoordinatorError("PORTFOLIO_ARTIFACT_BUNDLE_WRITE_SHA_MISMATCH")
        reader = context_reader if path == context_path else artifact_reader
        actual_content, actual_sha = _read_provider_artifact(reader, path)
        if actual_content != expected_content or actual_sha != expected_sha:
            raise PortfolioCoordinatorError("PORTFOLIO_ARTIFACT_BUNDLE_READBACK_MISMATCH")
        verified[path] = actual_sha
    return verified


def _owner_action_parameters(
    context: Mapping[str, Any],
    *,
    stage: str,
    artifact_ref: Mapping[str, str],
    context_ref: Mapping[str, Any],
    state: Mapping[str, Any],
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "artifact_key": stage,
        "artifact_path": artifact_ref["path"],
        "artifact_blob_sha": artifact_ref["blob_sha"],
        "portfolio_context_ref": dict(context_ref),
    }
    result = context["last_stage_result"]
    if stage == "RESEARCH":
        params["decision_envelope"] = deepcopy(context["shared"].get("decision_envelope"))
        params["private_research_brief"] = deepcopy(context["shared"].get("private_research_brief"))
    elif stage == "EDITORIAL":
        params["story_blueprints"] = [
            deepcopy(item["story_blueprint"])
            for item in context["products"].values()
        ]
    elif stage in {"RESEARCH_AUDIT", "EDITORIAL_AUDIT"}:
        params["review_status"] = result["status"]
        if result.get("revision_target") is not None:
            params["revision_target"] = result["revision_target"]
        if stage == "EDITORIAL_AUDIT" and result["status"] in {"PASS", "REVISE"}:
            params["publication_fitnesses"] = [
                deepcopy(item["publication_fitness"])
                for item in context["products"].values()
                if item.get("publication_fitness") is not None
            ]
    satisfaction = deepcopy(result.get("requirement_satisfaction", []))
    stage_path = artifact_ref["path"]
    for item in satisfaction:
        refs = item.setdefault("evidence_refs", [])
        if stage_path not in refs:
            refs.append(stage_path)
    params["requirement_satisfaction"] = satisfaction
    return params


def run_next_portfolio_stage(
    task_id: str,
    *,
    seed_inputs: Mapping[str, Any] | None = None,
    execute_pass: Callable[..., Mapping[str, Any]] | None = None,
    research_audit: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
    requirement_satisfaction: list[Mapping[str, Any]] | None = None,
    state_reader: Callable[[str], Any],
    artifact_reader: Callable[[str], Any],
    portfolio_context_reader: Callable[[str], Any],
    artifact_bundle_writer: ArtifactBundleWriter,
    authorization_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None],
    bundle_cas_writer: Callable[..., Mapping[str, Any]],
    effect_attestation_signer: Callable[[Mapping[str, Any]], Mapping[str, Any] | None],
    effect_receipt_reader: Callable[[str], Any],
    source_snapshot_reader: Callable[[str], Mapping[str, Any] | None] | None = None,
    independent_editorial_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
    owner_instruction_reader: Callable[[str], Mapping[str, Any] | None] | None = None,
    owner_semantic_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
    method_catalog_reader: Callable[[str], Any] | None = None,
    action_id: str | None = None,
) -> dict[str, Any]:
    """Execute, persist, read back and owner-admit exactly one Financial business stage.

    The caller supplies authenticated provider adapters. This function never creates
    user authorization, never writes CAOS, and never treats local hash receipts as
    a substitute for provider readback or Article Aggregate admission.
    """
    state_path = standalone_runtime._state_path(task_id)
    observed = standalone_runtime._read(state_reader, state_path)
    if observed is None:
        raise PortfolioCoordinatorError("PORTFOLIO_ARTICLE_STATE_NOT_FOUND")
    state, state_sha = observed
    if state.get("task_id") != task_id:
        raise PortfolioCoordinatorError("PORTFOLIO_ARTICLE_IDENTITY_MISMATCH")
    current_admission.validate_state(state)
    if state.get("status") == "BLOCKED":
        raise PortfolioCoordinatorError("PORTFOLIO_OWNER_STATE_BLOCKED_REQUIRES_EXPLICIT_RECOVERY")
    if state.get("status") != "IN_PROGRESS":
        raise PortfolioCoordinatorError("PORTFOLIO_OWNER_STATE_NOT_IN_PROGRESS")

    required_outputs = list(state.get("required_outputs", []))
    contexts = _requirement_contexts(state, required_outputs)
    owner_stage = str(state["current_stage"])
    context_ref = _latest_context_ref(state)
    context: dict[str, Any]

    if context_ref is None:
        if owner_stage not in {"INTAKE", "RESEARCH"}:
            raise PortfolioCoordinatorError("PORTFOLIO_RESUME_CONTEXT_REF_MISSING")
        if not isinstance(seed_inputs, Mapping):
            raise PortfolioCoordinatorError("PORTFOLIO_INITIAL_SEED_INPUTS_REQUIRED")
        normalized_seed = {
            key: value for key, value in seed_inputs.items()
            if key not in {"task_id", "requirement_digest", "task_requirement_contexts"}
        }
        context = start_portfolio_context(
            normalized_seed,
            required_outputs=required_outputs,
            task_id=task_id,
            requirement_digest=state["task_requirement_digest"],
            requirement_contexts=contexts,
            current_stage="RESEARCH",
        )
    else:
        context_path = require_article_path(context_ref.get("path"), task_id)
        context_bytes, context_blob_sha = _read_provider_artifact(
            portfolio_context_reader, context_path,
        )
        if context_blob_sha != context_ref.get("blob_sha"):
            raise PortfolioCoordinatorError("PORTFOLIO_CONTEXT_REF_BLOB_SHA_MISMATCH")
        if hashlib.sha256(context_bytes).hexdigest() != context_ref.get("sha256"):
            raise PortfolioCoordinatorError("PORTFOLIO_CONTEXT_REF_SHA256_MISMATCH")
        try:
            context = json.loads(context_bytes)
            validate_portfolio_context(context)
        except Exception as exc:
            raise PortfolioCoordinatorError("PORTFOLIO_PERSISTED_CONTEXT_INVALID") from exc
        if context.get("task_id") != task_id:
            raise PortfolioCoordinatorError("PORTFOLIO_CONTEXT_TASK_ID_MISMATCH")
        if context.get("required_output_kinds") != sorted(required_outputs):
            raise PortfolioCoordinatorError("PORTFOLIO_CONTEXT_OUTPUT_CONTRACT_MISMATCH")
        if context.get("current_stage") != owner_stage:
            raise PortfolioCoordinatorError("PORTFOLIO_CONTEXT_OWNER_STAGE_MISMATCH")
        if context.get("requirement_digest") != state.get("task_requirement_digest"):
            context = rebind_portfolio_context_requirements(
                context,
                requirement_digest=state["task_requirement_digest"],
                requirement_contexts=contexts,
                current_stage=owner_stage,
            )
        elif context.get("requirement_contexts") is None:
            context = rebind_portfolio_context_requirements(
                context,
                requirement_digest=state["task_requirement_digest"],
                requirement_contexts=contexts,
                current_stage=owner_stage,
            )
        if context.get("execution_status") == "BLOCKED":
            context = resume_portfolio_context(context, owner_state=state)

    if owner_stage == "INTAKE":
        if context["current_stage"] != "RESEARCH":
            raise PortfolioCoordinatorError("PORTFOLIO_INTAKE_CONTEXT_MUST_START_AT_RESEARCH")
        context_bytes = _canonical_json_bytes(context)
        next_context_ref = _context_ref(task_id=task_id, context=context, content=context_bytes)
        _write_and_verify_bundle(
            {next_context_ref["path"]: context_bytes},
            writer=artifact_bundle_writer,
            artifact_reader=artifact_reader,
            context_reader=portfolio_context_reader,
            context_path=next_context_ref["path"],
        )
        proposal = {
            "schema_version": standalone_runtime.CONTRACT_VERSION,
            "domain_id": standalone_runtime.DOMAIN_ID,
            "action_id": action_id or f"financial-portfolio-intake-{uuid4().hex}",
            "task_id": task_id,
            "operation": "ADVANCE_STAGE",
            "expected_state_blob_sha": state_sha,
            "parameters": {"portfolio_context_ref": next_context_ref},
        }
        admission = standalone_runtime.admit_article_action(
            proposal,
            state_reader=state_reader,
            cas_writer=None,
            authorization_verifier=authorization_verifier,
            bundle_cas_writer=bundle_cas_writer,
            effect_attestation_signer=effect_attestation_signer,
            effect_receipt_reader=effect_receipt_reader,
            artifact_reader=artifact_reader,
            portfolio_context_reader=portfolio_context_reader,
            source_snapshot_reader=source_snapshot_reader,
            independent_editorial_verifier=independent_editorial_verifier,
            owner_instruction_reader=owner_instruction_reader,
            owner_semantic_verifier=owner_semantic_verifier,
            method_catalog_reader=method_catalog_reader,
        )
        return {
            "task_id": task_id,
            "executed_stage": "INTAKE",
            "next_stage": admission["stage"],
            "owner_admission": admission,
            "portfolio_context_ref": next_context_ref,
            "stage_artifact_ref": None,
        }

    if owner_stage not in INTERNAL_PORTFOLIO_STAGE_SEQUENCE:
        raise PortfolioCoordinatorError(
            f"PORTFOLIO_INTERNAL_STAGE_SEQUENCE_COMPLETE_OR_UNSUPPORTED:{owner_stage}"
        )
    if context.get("current_stage") != owner_stage:
        raise PortfolioCoordinatorError("PORTFOLIO_CONTEXT_STAGE_MISMATCH")

    next_context = execute_portfolio_stage(
        context,
        stage=owner_stage,
        execute_pass=execute_pass,
        research_audit=research_audit if owner_stage == "RESEARCH_AUDIT" else None,
        requirement_satisfaction=requirement_satisfaction,
    )
    stage_receipt = (
        next_context["stage_receipts"][-1]
        if next_context.get("stage_receipts")
        and next_context["stage_receipts"][-1].get("stage") == owner_stage
        else next_context["revision_history"][-1]["stage_receipt"]
    )
    artifact = _business_stage_artifact(
        next_context, stage=owner_stage, state=state,
    )
    artifact_bytes = _canonical_json_bytes(artifact)
    stage_ref = _stage_artifact_ref(
        task_id=task_id,
        stage=owner_stage,
        receipt=stage_receipt,
        content=artifact_bytes,
    )
    context_bytes = _canonical_json_bytes(next_context)
    next_context_ref = _context_ref(
        task_id=task_id, context=next_context, content=context_bytes,
    )
    _write_and_verify_bundle(
        {
            stage_ref["path"]: artifact_bytes,
            next_context_ref["path"]: context_bytes,
        },
        writer=artifact_bundle_writer,
        artifact_reader=artifact_reader,
        context_reader=portfolio_context_reader,
        context_path=next_context_ref["path"],
    )

    params = _owner_action_parameters(
        next_context,
        stage=owner_stage,
        artifact_ref=stage_ref,
        context_ref=next_context_ref,
        state=state,
    )
    proposal = {
        "schema_version": standalone_runtime.CONTRACT_VERSION,
        "domain_id": standalone_runtime.DOMAIN_ID,
        "action_id": action_id or f"financial-portfolio-{owner_stage.lower()}-{uuid4().hex}",
        "task_id": task_id,
        "operation": "ADVANCE_STAGE",
        "expected_state_blob_sha": state_sha,
        "parameters": params,
    }
    admission = standalone_runtime.admit_article_action(
        proposal,
        state_reader=state_reader,
        cas_writer=None,
        authorization_verifier=authorization_verifier,
        bundle_cas_writer=bundle_cas_writer,
        effect_attestation_signer=effect_attestation_signer,
        effect_receipt_reader=effect_receipt_reader,
        artifact_reader=artifact_reader,
        portfolio_context_reader=portfolio_context_reader,
        source_snapshot_reader=source_snapshot_reader,
        independent_editorial_verifier=independent_editorial_verifier,
        owner_instruction_reader=owner_instruction_reader,
        owner_semantic_verifier=owner_semantic_verifier,
        method_catalog_reader=method_catalog_reader,
    )
    if admission.get("stage") != next_context.get("current_stage"):
        raise PortfolioCoordinatorError("PORTFOLIO_OWNER_ADMISSION_STAGE_READBACK_MISMATCH")
    expected_status = "BLOCKED" if next_context.get("execution_status") == "BLOCKED" else "IN_PROGRESS"
    if admission.get("business_status") != expected_status:
        raise PortfolioCoordinatorError("PORTFOLIO_OWNER_ADMISSION_STATUS_READBACK_MISMATCH")
    return {
        "task_id": task_id,
        "executed_stage": owner_stage,
        "next_stage": admission["stage"],
        "stage_result": deepcopy(next_context.get("last_stage_result")),
        "owner_admission": admission,
        "stage_artifact_ref": stage_ref,
        "portfolio_context_ref": next_context_ref,
        "portfolio_context": next_context,
    }
