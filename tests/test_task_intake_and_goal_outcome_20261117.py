from __future__ import annotations

import copy
import hashlib

import pytest

from financial_writing_agent import current_admission
from financial_writing_agent.portfolio_coordinator import _prepare_goal_first_intake
from financial_writing_agent.goal_outcome import (
    GoalOutcomeError,
    build_goal_outcome_challenge,
    article_deliverables_sha256,
    verify_goal_outcome_review,
    verify_persisted_goal_outcome_review,
)
from financial_writing_agent.task_intake import (
    TaskIntakeError,
    build_task_intake_review_challenge,
    canonical_sha256,
    validate_task_intake_manifest,
    verify_task_intake_review,
)
from financial_writing_agent.task_requirements import (
    apply_requirement_changes,
    authority_digest,
    empty_requirement_authority,
)
from financial_writing_agent.provider_attestation import payload_sha256
from tests.trusted_provider_testkit import signed_attestation


PROMPT = "请研究AI算力产业链，表达简洁。"
TASK_ID = "goal-first-intake-test"
OUTPUTS = [
    "AUDIT_DOCX",
    "FINANCE_DEEP_DOCX",
    "FINANCE_BROAD_DOCX",
    "PLATFORM_INTERACTION_PACK_DOCX",
]
SOURCE_REF = "chat://user/goal-first-intake-test"


def _requirements():
    return [
        {
            "requirement_id": "topic-focus",
            "statement": "Research and write about the AI computing-power industry chain.",
            "scopes": ["ALL"],
            "affects_from_stage": "RESEARCH",
            "evidence_ref": SOURCE_REF,
            "source_kind": "USER_EXPLICIT",
        },
        {
            "requirement_id": "concise-preference",
            "statement": "Prefer concise prose without sacrificing material explanation.",
            "scopes": ["ALL"],
            "affects_from_stage": "DRAFT",
            "evidence_ref": SOURCE_REF,
            "source_kind": "USER_PREFERENCE",
        },
    ]


def _manifest():
    requirements = _requirements()
    profile = {
        "schema_version": "1.1",
        "workflow_contract": "FINANCIAL_ARTICLE_10_STAGE_V1",
        "source_prompt_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
        "fixed_requirement_ids": ["topic-focus"],
        "preference_requirement_ids": ["concise-preference"],
        "decision_domains": [
            {
                "domain": "TOPIC_SCOPE",
                "disposition": "LOCKED",
                "scopes": ["ALL"],
                "requirement_ids": ["topic-focus"],
                "preference_ids": [],
                "rationale": "The user explicitly fixed the article subject.",
            },
            {
                "domain": "VOICE_AND_LENGTH",
                "disposition": "OPEN",
                "scopes": ["ALL"],
                "requirement_ids": [],
                "preference_ids": ["concise-preference"],
                "rationale": "Concision is a preference, not a hard length constraint.",
            },
        ],
        "conditional_modules": ["COMPANY_UNIVERSE"],
        "execution_rationale": "Keep the workflow fixed while allowing evidence-led company selection and narrative.",
    }
    raw = {
        "task_id": TASK_ID,
        "source_message_ref": SOURCE_REF,
        "source_prompt_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
        "task_objective": "Research and deliver the requested AI computing-power industry-chain article portfolio.",
        "instruction_units": [
            {
                "unit_id": "goal-topic",
                "category": "GOAL",
                "disposition": "BINDING",
                "source_excerpt": "AI算力产业链",
                "requirement_ids": ["topic-focus"],
                "rationale": "The topic is the direct subject of the user's request.",
            },
            {
                "unit_id": "preference-concise",
                "category": "PREFERENCE",
                "disposition": "PREFERENCE",
                "source_excerpt": "表达简洁",
                "requirement_ids": ["concise-preference"],
                "rationale": "The user expresses a preference, not a fixed word count.",
            },
        ],
        "requirements": [
            {"source_unit_ids": ["goal-topic"], "requirement": requirements[0]},
            {"source_unit_ids": ["preference-concise"], "requirement": requirements[1]},
        ],
        "requested_outputs": list(OUTPUTS),
        "success_criteria": [
            {
                "criterion_id": "subject-covered",
                "statement": "The delivered portfolio materially covers the user-requested AI computing-power industry chain.",
                "requirement_ids": ["topic-focus"],
            },
            {
                "criterion_id": "preference-respected",
                "statement": "The writing is concise without omitting material economic explanation.",
                "requirement_ids": ["concise-preference"],
            },
        ],
        "writing_execution_profile": profile,
        "knowledge_routes": [
            {
                "route_id": "current-primary-sources",
                "decision": "REQUIRED",
                "stages": ["RESEARCH"],
                "rationale": "Current issuer, regulator and filing evidence is required for financial claims.",
                "trigger": "Every current financial article.",
            },
            {
                "route_id": "financial-methods",
                "decision": "OPTIONAL",
                "stages": ["RESEARCH", "EDITORIAL"],
                "rationale": "Reuse only methods relevant to the current topic.",
                "trigger": "A material reusable method applies.",
            },
        ],
        "capability_routes": [
            {
                "route_id": "research-and-writing",
                "decision": "REQUIRED",
                "stages": ["RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE", "DRAFT"],
                "rationale": "The article requires research, editorial decisions and prose production.",
                "trigger": "Every article task.",
            },
            {
                "route_id": "verified-word-delivery",
                "decision": "REQUIRED",
                "stages": ["DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT"],
                "rationale": "The requested Word portfolio must be rendered and read back.",
                "trigger": "The immutable Word output contract.",
            },
        ],
    }
    return validate_task_intake_manifest(
        raw, task_id=TASK_ID, prompt=PROMPT, required_outputs=OUTPUTS,
    )


def _intake_attestation(manifest=None):
    manifest = manifest or _manifest()
    challenge = build_task_intake_review_challenge(
        task_id=TASK_ID,
        prompt=PROMPT,
        manifest=manifest,
        required_outputs=OUTPUTS,
    )
    return signed_attestation(
        "task_intake_review",
        actor="synthetic-independent-intake-reviewer",
        key_env="FINANCIAL_INTAKE_REVIEW_KEY",
        provider_env="FINANCIAL_INTAKE_REVIEW_PROVIDER_ID",
        approved=True,
        review_scope="TASK_INTAKE_SEMANTIC_COVERAGE",
        task_id=TASK_ID,
        source_prompt_sha256=challenge["source_prompt_sha256"],
        manifest_sha256=challenge["manifest_sha256"],
        covered_instruction_unit_ids=challenge["instruction_unit_ids"],
        requirement_ids=challenge["requirement_ids"],
        uncovered_material_unit_ids=[],
        unmapped_requirement_ids=[],
        blocking_question_ids=[],
        requested_outputs_complete=True,
        success_criteria_complete=True,
        execution_profile_complete=True,
        knowledge_routes_reviewed=True,
        capability_routes_reviewed=True,
    )


def _goal_state():
    manifest = _manifest()
    authority, _ = apply_requirement_changes(
        empty_requirement_authority(),
        upserts=[item["requirement"] for item in manifest["requirements"]],
        evidence_ref=SOURCE_REF,
    )
    artifacts = {}
    texts = []
    for index, kind in enumerate(OUTPUTS):
        if kind == "AUDIT_DOCX":
            continue
        digest = hashlib.sha256(f"{kind}-binary".encode()).hexdigest()
        evidence_digest = hashlib.sha256(f"{kind}-delivery-evidence".encode()).hexdigest()
        resource_ref = f"session://{kind.lower()}"
        artifacts[kind] = {
            "kind": kind,
            "file_name": f"{kind}.docx",
            "resource_ref": resource_ref,
            "sha256": digest,
            "delivery_evidence_sha256": evidence_digest,
        }
        texts.append({
            "kind": kind,
            "resource_ref": resource_ref,
            "sha256": digest,
            "text": f"{kind} actual article content: AI computing-power economics and company differentiation.",
        })
    state = {
        "task_id": TASK_ID,
        "prompt": PROMPT,
        "status": "IN_PROGRESS",
        "current_stage": "FINAL_AUDIT",
        "required_outputs": list(OUTPUTS),
        "delivery_artifacts": artifacts,
        "task_intake_manifest": manifest,
        "task_intake_manifest_sha256": payload_sha256(manifest),
        "task_requirement_authority": authority,
        "task_requirement_digest": authority_digest(authority),
        "execution_receipts": [],
        "stage_artifacts": {},
    }
    return state, texts


def _goal_attestation(state, *, decision="PASS", unmet_id=None):
    _, texts = _goal_state()
    challenge = build_goal_outcome_challenge(state, deliverable_texts=texts)
    authority = state["task_requirement_authority"]
    results = [
        {
            "requirement_id": item["requirement_id"],
            "result": "NOT_SATISFIED" if item["requirement_id"] == unmet_id else "SATISFIED",
            "evidence_refs": [f"review://{item['requirement_id']}"],
        }
        for item in authority["active_requirements"]
    ]
    unmet = sorted(item["requirement_id"] for item in results if item["result"] != "SATISFIED")
    criteria_results = [
        {
            "criterion_id": item["criterion_id"],
            "result": "SATISFIED",
            "evidence_refs": [f"review://criterion/{item['criterion_id']}"],
        }
        for item in challenge["success_criteria"]
    ]
    unmet_criteria = []
    revision_target = "DRAFT" if decision == "REVISE" else None
    return signed_attestation(
        "independent_goal_outcome_review",
        actor="synthetic-independent-goal-reviewer",
        key_env="FINANCIAL_GOAL_REVIEW_KEY",
        provider_env="FINANCIAL_GOAL_REVIEW_PROVIDER_ID",
        approved=True,
        review_scope="FINAL_USER_GOAL_OUTCOME",
        task_id=state["task_id"],
        source_prompt_sha256=challenge["source_prompt_sha256"],
        task_intake_manifest_sha256=challenge["task_intake_manifest_sha256"],
        task_requirement_digest=challenge["task_requirement_digest"],
        article_deliverables_sha256=challenge["article_deliverables_sha256"],
        requirement_results=results,
        requirement_results_sha256=payload_sha256(results),
        unmet_requirement_ids=unmet,
        success_criteria_results=criteria_results,
        success_criteria_results_sha256=payload_sha256(criteria_results),
        unmet_success_criterion_ids=unmet_criteria,
        uncovered_material_requirement_ids=[],
        decision=decision,
        revision_target=revision_target,
        review_summary="The delivered article portfolio was checked against every active requirement.",
    )




def test_coordinator_precomputes_exact_initial_requirement_projection_without_shadow_authority():
    manifest = _manifest()
    attestation = _intake_attestation(manifest)
    state = current_admission.build_initial_state(
        task_id=TASK_ID,
        prompt=PROMPT,
        source_refs=[],
        executor_identity="test",
        goal_first=True,
    )
    prepared = _prepare_goal_first_intake(
        state,
        {
            "task_intake_manifest": manifest,
            "task_intake_review_attestation": attestation,
            "writing_execution_profile": manifest["writing_execution_profile"],
        },
        OUTPUTS,
    )
    expected_authority, _ = apply_requirement_changes(
        empty_requirement_authority(),
        upserts=[item["requirement"] for item in manifest["requirements"]],
        evidence_ref=SOURCE_REF,
    )
    assert prepared["requirement_digest"] == authority_digest(expected_authority)
    assert all(
        context["digest"] == prepared["requirement_digest"]
        for context in prepared["requirement_contexts"].values()
    )
    assert prepared["normalized_seed"]["task_intake_manifest_sha256"] == prepared["manifest_sha256"]
    assert "task_intake_manifest" not in prepared["normalized_seed"]
    assert "task_intake_review_attestation" not in prepared["normalized_seed"]

def test_intake_manifest_preserves_goal_preference_scope_and_required_routes():
    manifest = _manifest()
    assert manifest["task_id"] == TASK_ID
    assert manifest["requested_outputs"] == OUTPUTS
    assert manifest["writing_execution_profile"]["fixed_requirement_ids"] == ["topic-focus"]
    challenge = build_task_intake_review_challenge(
        task_id=TASK_ID, prompt=PROMPT, manifest=manifest, required_outputs=OUTPUTS,
    )
    attestation = _intake_attestation(manifest)
    verified = verify_task_intake_review(attestation, challenge=challenge)
    assert verified["authenticated_actor"] == "synthetic-independent-intake-reviewer"


def test_intake_manifest_rejects_wrong_task_prompt_output_and_route_coverage():
    manifest = _manifest()
    with pytest.raises(TaskIntakeError, match="TASK_INTAKE_TASK_ID_BINDING_MISMATCH"):
        validate_task_intake_manifest(
            {**manifest, "task_id": "another-task"},
            task_id=TASK_ID, prompt=PROMPT, required_outputs=OUTPUTS,
        )
    with pytest.raises(TaskIntakeError, match="TASK_INTAKE_PROMPT_BINDING_MISMATCH"):
        validate_task_intake_manifest(
            manifest, task_id=TASK_ID, prompt=PROMPT + " changed", required_outputs=OUTPUTS,
        )
    with pytest.raises(TaskIntakeError, match="TASK_INTAKE_OUTPUT_CONTRACT_MISMATCH"):
        validate_task_intake_manifest(
            {**manifest, "requested_outputs": OUTPUTS[:-1]},
            task_id=TASK_ID, prompt=PROMPT, required_outputs=OUTPUTS,
        )
    broken_routes = copy.deepcopy(manifest)
    broken_routes["knowledge_routes"][0]["decision"] = "OPTIONAL"
    with pytest.raises(TaskIntakeError, match="TASK_INTAKE_REQUIRED_RESEARCH_KNOWLEDGE_ROUTE_MISSING"):
        validate_task_intake_manifest(
            broken_routes, task_id=TASK_ID, prompt=PROMPT, required_outputs=OUTPUTS,
        )


def test_intake_review_signature_binds_exact_manifest_and_independent_reviewer():
    manifest = _manifest()
    attestation = _intake_attestation(manifest)
    challenge = build_task_intake_review_challenge(
        task_id=TASK_ID, prompt=PROMPT, manifest=manifest, required_outputs=OUTPUTS,
    )
    changed = copy.deepcopy(manifest)
    changed["task_objective"] += " altered"
    changed_challenge = build_task_intake_review_challenge(
        task_id=TASK_ID, prompt=PROMPT, manifest=changed, required_outputs=OUTPUTS,
    )
    with pytest.raises(TaskIntakeError, match="TASK_INTAKE_INDEPENDENT_REVIEW_ATTESTATION_INVALID"):
        verify_task_intake_review(attestation, challenge=changed_challenge)
    assert challenge["manifest_sha256"] != changed_challenge["manifest_sha256"]


def test_goal_first_intake_atomically_admits_initial_requirements_and_review():
    manifest = _manifest()
    attestation = _intake_attestation(manifest)
    state = current_admission.build_initial_state(
        task_id=TASK_ID,
        prompt=PROMPT,
        source_refs=[],
        executor_identity="test",
        goal_first=True,
    )
    context_ref = {
        "path": f"workspaces/articles/{TASK_ID}/portfolio/contexts/1-intake.json",
        "blob_sha": "a" * 40,
        "sha256": "b" * 64,
        "stage": "RESEARCH",
        "generation": 1,
    }
    admitted = current_admission.advance_state(
        state,
        previous_state_blob_sha="c" * 40,
        executor_identity="test",
        portfolio_context_ref=context_ref,
        task_intake_manifest=manifest,
        task_intake_review_attestation=attestation,
    )
    current_admission.validate_state(admitted)
    assert admitted["current_stage"] == "RESEARCH"
    assert admitted["task_requirement_authority"]["revision"] == 1
    assert {
        item["requirement_id"]
        for item in admitted["task_requirement_authority"]["active_requirements"]
    } == {"topic-focus", "concise-preference"}
    assert admitted["task_intake_manifest_sha256"] == canonical_sha256(manifest)
    assert admitted["execution_receipts"][-1]["input_bindings"]["initial_requirement_revision"] == 1


def test_goal_first_intake_cannot_advance_without_independent_manifest_review():
    state = current_admission.build_initial_state(
        task_id=TASK_ID,
        prompt=PROMPT,
        source_refs=[],
        executor_identity="test",
        goal_first=True,
    )
    with pytest.raises(current_admission.CurrentAdmissionError, match="TASK_INTAKE_MANIFEST_SCHEMA_INVALID|TASK_INTAKE_MANIFEST_REQUIRED"):
        current_admission.advance_state(
            state,
            previous_state_blob_sha="c" * 40,
            executor_identity="test",
            portfolio_context_ref={
                "path": f"workspaces/articles/{TASK_ID}/portfolio/contexts/1-intake.json",
                "blob_sha": "a" * 40,
                "sha256": "b" * 64,
                "stage": "RESEARCH",
                "generation": 1,
            },
        )


def test_final_goal_review_binds_all_active_requirements_and_exact_deliverable_bytes():
    state, texts = _goal_state()
    challenge = build_goal_outcome_challenge(state, deliverable_texts=texts)
    attestation = _goal_attestation(state)
    verified = verify_goal_outcome_review(attestation, state=state)
    assert verified["decision"] == "PASS"
    assert verified["requirement_results_sha256"] == payload_sha256(verified["requirement_results"])
    assert article_deliverables_sha256(state) == challenge["article_deliverables_sha256"]
    persisted = verify_persisted_goal_outcome_review(attestation, state=state)
    assert persisted["decision"] == "PASS"


def test_final_goal_review_rejects_missing_requirement_and_changed_deliverable():
    state, texts = _goal_state()
    attestation = _goal_attestation(state)
    bad = copy.deepcopy(attestation)
    bad["article_deliverables_sha256"] = "0" * 64
    # Re-signing is deliberately not attempted: the original signature must fail.
    with pytest.raises(GoalOutcomeError, match="GOAL_OUTCOME_INDEPENDENT_REVIEW_ATTESTATION_INVALID"):
        verify_goal_outcome_review(bad, state=state)

    changed_state = copy.deepcopy(state)
    changed_state["delivery_artifacts"]["FINANCE_DEEP_DOCX"]["sha256"] = "f" * 64
    with pytest.raises(GoalOutcomeError, match="GOAL_OUTCOME_INDEPENDENT_REVIEW_ATTESTATION_INVALID"):
        verify_goal_outcome_review(attestation, state=changed_state)






def test_revision_targets_and_intake_stage_catalog_reuse_the_canonical_workflow():
    from financial_writing_agent.goal_outcome import GOAL_REVIEW_REVISION_TARGETS
    from financial_writing_agent.owner_guard import _revision_target_names
    from financial_writing_agent.task_intake import KNOWN_STAGES
    from financial_writing_agent.workflow_spec import BUSINESS_STAGE_NAMES

    assert GOAL_REVIEW_REVISION_TARGETS == _revision_target_names("FINAL_AUDIT")
    assert KNOWN_STAGES == frozenset(BUSINESS_STAGE_NAMES)

def test_goal_review_fail_is_blocking_and_does_not_claim_a_revision_route():
    state, _ = _goal_state()
    attestation = _goal_attestation(
        state, decision="FAIL", unmet_id="topic-focus",
    )
    verified = verify_goal_outcome_review(attestation, state=state)
    assert verified["decision"] == "FAIL"
    assert verified["revision_target"] is None
    historical = verify_persisted_goal_outcome_review(
        attestation, require_pass=False,
    )
    assert historical["decision"] == "FAIL"
    assert historical["revision_target"] is None

def test_goal_review_revise_decision_is_valid_history_but_never_an_active_pass():
    state, _ = _goal_state()
    attestation = _goal_attestation(
        state, decision="REVISE", unmet_id="topic-focus",
    )
    with pytest.raises(GoalOutcomeError, match="GOAL_OUTCOME_INDEPENDENT_REVIEW_ATTESTATION_INVALID"):
        verify_persisted_goal_outcome_review(attestation, state=state)
    historical = verify_persisted_goal_outcome_review(
        attestation, require_pass=False,
    )
    assert historical["decision"] == "REVISE"
