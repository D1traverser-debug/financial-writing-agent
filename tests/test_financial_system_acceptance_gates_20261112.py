"""Signed external proof, not callback or Boolean self-certification."""
import copy
import hashlib
import time
import pytest

from financial_writing_agent.acceptance_gates import (
    SYSTEM_GATES, REQUIRED_GATE_EVIDENCE, evaluate_system_acceptance,
)
from financial_writing_agent.provider_attestation import payload_sha256
from trusted_provider_testkit import (
    signed_attestation, signed_method_promotion, signed_method_impact,
    signed_owner_change_approval, signed_owner_message,
)

SHA = "d" * 40


def _proofs(*, reviewer="synthetic-independent-reviewer"):
    proofs = {}
    for gate in SYSTEM_GATES:
        evidence = {field: "synthetic-evidence" for field in REQUIRED_GATE_EVIDENCE[gate]}
        evidence.update({
            "owner_principal": "synthetic-financial-owner",
            "source_sha256": "a"*64,
            "previous_state_blob_sha": "b"*40,
            "resulting_state_blob_sha": "c"*40,
            "state_readback_sha": "c"*40,
            "catalog_revision": 2,
            "affected_task_ids": ["synthetic-task"],
            "write_blob_sha": "d"*40,
            "readback_blob_sha": "d"*40,
            "stale_conflict_status": 409,
            "plugin_id": "plugins_6af591b19a708191a3879e94a7ce8742",
            "release_id": "pluginrel_6af5a82a95f48191ba8d21fa3d188094",
            "fresh_chat_session_ref": "session://synthetic-fresh-chat",
            "tool_invocation_ref": "tool://synthetic-financial-invocation",
            "after_branch_names": ["main"],
            "before_branch_count": 99,
            "archive_tag_count": 98,
            "archive_manifest_sha256": "a"*64,
            "archive_tags_verified": True,
            "final_inventory_sha256": "b"*64,
            "main_protected": True,
            "main_requires_pull_request": True,
            "required_approving_review_count": 1,
            "main_dismiss_stale_reviews": True,
            "main_require_last_push_approval": True,
            "main_enforce_admins": True,
            "main_branches_up_to_date_required": True,
            "main_force_push_disabled": True,
            "main_deletion_disabled": True,
            "required_status_checks": ["test"],
            "required_status_check_apps": [{"context": "test", "app_id": 15368}],
            "main_pull_request_bypass_allowances": {"users": [], "teams": [], "apps": []},
        })
        if gate == "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION":
            source_ref = "chat://synthetic-owner/source-message"
            source_text = "请保留完整财经写作目标并按范围拆分需求。"
            source_sha = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
            change_sha = "b"*64
            message_attestation = signed_owner_message(source_ref, source_text)
            approval = signed_owner_change_approval({
                "source_sha256": source_sha,
                "change_sha256": change_sha,
            })
            evidence.update({
                "source_ref": source_ref,
                "source_sha256": source_sha,
                "owner_message_attestation": message_attestation,
                "change_sha256": change_sha,
                "owner_confirmation_ref": approval["approval_record_ref"],
                "owner_confirmation_attestation": approval,
            })
        if gate == "METHOD_KNOWLEDGE_CRUD_AND_IMPACT":
            promotion_challenge = {
                "knowledge_id": "METHOD-SYNTHETIC",
                "record_sha256": "e"*64,
                "decision_sha256": "f"*64,
                "validation_refs": ["ci://synthetic-method-validation"],
                "review_ref": "review://synthetic-method-promotion",
            }
            impact_challenge = {
                "knowledge_id": "METHOD-SYNTHETIC",
                "target_change_revision": 1,
                "event_sha256": "a"*64,
                "stage_evidence_refs": {
                    "RESEARCH": "evidence://research",
                    "EDITORIAL": "evidence://editorial",
                },
            }
            evidence.update({
                "promotion_challenge": promotion_challenge,
                "promotion_attestation": signed_method_promotion(promotion_challenge),
                "impact_challenge": impact_challenge,
                "impact_attestation": signed_method_impact(impact_challenge),
            })
        if gate == "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW":
            evidence.update({
                "reviewer_principal": reviewer,
                "reviewed_head_sha": SHA,
                "findings_status": "PASS",
            })
        independent = gate == "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW"
        proofs[gate] = signed_attestation(
            "system_gate", actor=reviewer if independent else "synthetic-financial-owner",
            key_env=(
                "FINANCIAL_INDEPENDENT_REVIEW_KEY" if independent
                else "FINANCIAL_PROVIDER_ATTESTATION_KEY"
            ),
            provider_env=(
                "FINANCIAL_INDEPENDENT_REVIEW_PROVIDER_ID" if independent
                else "FINANCIAL_TRUSTED_PROVIDER_ID"
            ),
            gate=gate, target_head_sha=SHA, evidence=evidence,
            evidence_sha256=payload_sha256(evidence),
        )
    return proofs


def _ci():
    return signed_attestation(
        "ci_run", actor="github-actions[bot]",
        key_env="FINANCIAL_CI_ATTESTATION_KEY",
        provider_env="FINANCIAL_CI_PROVIDER_ID",
        target_head_sha=SHA, conclusion="success",
        run_id="43212206584", workflow="financial-writing-agent-ci",
        test_count=397, coverage_percent=87,
    )


def test_green_local_ci_boolean_without_signed_provider_attestation_is_not_release_proof():
    verdict = evaluate_system_acceptance(head_sha=SHA, code_tests_passed=True)
    assert verdict["code_ci"] == "PASS__LOCAL_JOB_CONTEXT_NOT_SIGNED"
    assert verdict["system_status"].startswith("NOT_READY")
    assert len(verdict["open_gates"]) == len(SYSTEM_GATES)


def test_model_written_verified_labels_and_fake_provider_refs_do_not_certify():
    proofs = {
        gate: {
            "verified": True, "target_head_sha": SHA,
            "independent_principal": "made-up-reviewer",
            "provider_record_ref": "fake://pass",
        } for gate in SYSTEM_GATES
    }
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs,
        ci_attestation={"conclusion":"success","target_head_sha":SHA},
        code_tests_passed=True,
    )
    assert result["system_status"].startswith("NOT_READY")
    assert all(r["reason"] == "FINANCIAL_PROVIDER_ATTESTATION_FIELDS_MISSING"
               for r in result["gates"].values())


def test_callback_injection_is_not_an_acceptance_api():
    with pytest.raises(TypeError):
        evaluate_system_acceptance(
            head_sha=SHA, trusted_verifier=lambda _: {"verified": True},
            code_tests_passed=True,
        )


def test_signed_synthetic_gate_and_ci_receipts_exercise_verifier_but_are_not_live_receipts():
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=_proofs(), ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert result["system_status"] == "ACCEPTED__SIGNED_EXTERNAL_EVIDENCE_VERIFIED", result
    assert result["ci_attestation_verified"] is True
    assert result["open_gates"] == []
    # The signature key is installed by pytest conftest only; this is a test of
    # signature verification, never a production acceptance record.


@pytest.mark.parametrize("nested_field", ["promotion_attestation", "impact_attestation"])
def test_method_gate_rejects_tampered_independent_review_even_with_valid_outer_receipt(nested_field):
    proofs = _proofs()
    gate = "METHOD_KNOWLEDGE_CRUD_AND_IMPACT"
    outer = proofs[gate]
    evidence = copy.deepcopy(outer["evidence"])
    evidence[nested_field]["signature"] = "0" * 64
    proofs[gate] = signed_attestation(
        "system_gate", actor="synthetic-financial-owner",
        gate=gate, target_head_sha=SHA, evidence=evidence,
        evidence_sha256=payload_sha256(evidence),
    )
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert "METHOD_INDEPENDENT_REVIEW_ATTESTATION_INVALID" in result["gates"][gate]["reason"]


def test_method_gate_malformed_signed_challenge_fails_closed_without_crashing():
    proofs = _proofs()
    gate = "METHOD_KNOWLEDGE_CRUD_AND_IMPACT"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    evidence["promotion_challenge"].pop("record_sha256")
    proofs[gate] = signed_attestation(
        "system_gate", actor="synthetic-financial-owner",
        gate=gate, target_head_sha=SHA, evidence=evidence,
        evidence_sha256=payload_sha256(evidence),
    )
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert "METHOD_PROMOTION_DIGEST_INVALID" in result["gates"][gate]["reason"]


def test_system_method_gate_accepts_durable_historical_nested_review_receipts():
    proofs = _proofs()
    gate = "METHOD_KNOWLEDGE_CRUD_AND_IMPACT"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    old_issued_at = int(time.time()) - 86400
    promotion = evidence["promotion_challenge"]
    evidence["promotion_attestation"] = signed_attestation(
        "method_promotion_review", actor="synthetic-method-reviewer",
        key_env="FINANCIAL_METHOD_REVIEW_KEY",
        provider_env="FINANCIAL_METHOD_REVIEW_PROVIDER_ID",
        issued_at=old_issued_at, approved=True,
        knowledge_id=promotion["knowledge_id"],
        record_sha256=promotion["record_sha256"],
        decision_sha256=promotion["decision_sha256"],
        validation_refs=promotion["validation_refs"],
        review_ref=promotion["review_ref"],
    )
    impact = evidence["impact_challenge"]
    evidence["impact_attestation"] = signed_attestation(
        "method_impact_review", actor="synthetic-method-reviewer",
        key_env="FINANCIAL_METHOD_REVIEW_KEY",
        provider_env="FINANCIAL_METHOD_REVIEW_PROVIDER_ID",
        issued_at=old_issued_at, approved=True,
        knowledge_id=impact["knowledge_id"],
        target_change_revision=impact["target_change_revision"],
        event_sha256=impact["event_sha256"],
        stage_evidence_refs=impact["stage_evidence_refs"],
        verified_stages=list(impact["stage_evidence_refs"]),
    )
    proofs[gate] = signed_attestation(
        "system_gate", actor="synthetic-financial-owner",
        gate=gate, target_head_sha=SHA, evidence=evidence,
        evidence_sha256=payload_sha256(evidence),
    )
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate not in result["open_gates"]


def test_system_gate_proof_must_be_signed_for_the_configured_owner():
    proofs = _proofs()
    gate = "LEGAL_ARTICLE_GRAPH_AND_RECOVERY"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    proofs[gate] = signed_attestation(
        "system_gate", actor="synthetic-attacker",
        gate=gate, target_head_sha=SHA, evidence=evidence,
        evidence_sha256=payload_sha256(evidence),
    )
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert result["gates"][gate]["reason"] == "SYSTEM_GATE_ACTOR_MUST_MATCH_OWNER"


def test_method_gate_rejects_validly_signed_reviews_for_different_knowledge_items():
    proofs = _proofs()
    gate = "METHOD_KNOWLEDGE_CRUD_AND_IMPACT"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    challenge = dict(evidence["impact_challenge"])
    challenge["knowledge_id"] = "METHOD-OTHER"
    evidence["impact_challenge"] = challenge
    evidence["impact_attestation"] = signed_method_impact(challenge)
    proofs[gate] = signed_attestation(
        "system_gate", actor="synthetic-financial-owner",
        gate=gate, target_head_sha=SHA, evidence=evidence,
        evidence_sha256=payload_sha256(evidence),
    )
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert "METHOD_PROMOTION_IMPACT_KNOWLEDGE_ID_MISMATCH" in result["gates"][gate]["reason"]


def test_release_gate_rejects_non_hex_head_and_boolean_ci_test_count():
    with pytest.raises(ValueError, match="HEAD_SHA_REQUIRED"):
        evaluate_system_acceptance(head_sha="z" * 40)
    ci = signed_attestation(
        "ci_run", actor="github-actions[bot]",
        key_env="FINANCIAL_CI_ATTESTATION_KEY",
        provider_env="FINANCIAL_CI_PROVIDER_ID",
        target_head_sha=SHA, conclusion="success",
        run_id="synthetic-run", workflow="financial-writing-agent-ci",
        test_count=True, coverage_percent=87,
    )
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=_proofs(), ci_attestation=ci,
        code_tests_passed=True,
    )
    assert result["ci_attestation_verified"] is False
    assert result["system_status"].startswith("NOT_READY")


def test_owner_cannot_attest_the_independent_external_review_gate():
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=_proofs(reviewer="synthetic-financial-owner"),
        ci_attestation=_ci(), code_tests_passed=True,
    )
    assert "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW" in result["open_gates"]


def test_wrong_head_and_missing_gate_specific_evidence_are_rejected():
    proofs = _proofs()
    proofs[SYSTEM_GATES[0]] = signed_attestation(
        "system_gate", gate=SYSTEM_GATES[0], target_head_sha="e"*40,
        evidence={"source_ref":"x"}, evidence_sha256=payload_sha256({"source_ref":"x"}),
    )
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert SYSTEM_GATES[0] in result["open_gates"]


def test_owner_goal_gate_rejects_unbound_confirmation_reference():
    proofs = _proofs()
    gate = "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    evidence["owner_confirmation_ref"] = "fake://arbitrary-reference"
    _resign_owner_gate(proofs, evidence)
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert "OWNER_CONFIRMATION_REF_MISMATCH" in result["gates"][gate]["reason"]


def test_owner_goal_gate_rejects_confirmation_for_different_change_digest():
    proofs = _proofs()
    gate = "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    evidence["change_sha256"] = "c"*64
    _resign_owner_gate(proofs, evidence)
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert "OWNER_CHANGE_ATTESTATION_INVALID" in result["gates"][gate]["reason"]


def test_owner_goal_gate_rejects_missing_nested_confirmation_signature():
    proofs = _proofs()
    gate = "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    evidence.pop("owner_confirmation_attestation")
    _resign_owner_gate(proofs, evidence)
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert "GATE_EVIDENCE_FIELDS_MISSING" in result["gates"][gate]["reason"]


def test_owner_goal_gate_accepts_only_matching_signed_source_and_change():
    proofs = _proofs()
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION" not in result["open_gates"]


def _resign_owner_gate(proofs, evidence, gate="ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION"):
    proofs[gate] = signed_attestation(
        "system_gate", actor="synthetic-financial-owner",
        key_env="FINANCIAL_PROVIDER_ATTESTATION_KEY",
        provider_env="FINANCIAL_TRUSTED_PROVIDER_ID",
        gate=gate, target_head_sha=SHA, evidence=evidence,
        evidence_sha256=payload_sha256(evidence),
    )


@pytest.mark.parametrize(
    ("field", "wrong", "reason"),
    [
        ("plugin_id", "plugins_not_financial", "NATIVE_FINANCIAL_PLUGIN_ID_MISMATCH"),
        ("release_id", "pluginrel_old_release", "NATIVE_FINANCIAL_PLUGIN_RELEASE_MISMATCH"),
    ],
)
def test_native_client_gate_requires_exact_manifest_plugin_and_release(field, wrong, reason):
    proofs = _proofs()
    gate = "NATIVE_FINANCIAL_PLUGIN_CLIENT_ACTIVATION"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    evidence[field] = wrong
    _resign_owner_gate(proofs, evidence, gate)
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert reason in result["gates"][gate]["reason"]


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("main_protected", False, "MAIN_BRANCH_NOT_PROTECTED"),
        ("main_requires_pull_request", False, "MAIN_PULL_REQUEST_REQUIRED_RULE_MISSING"),
        ("required_approving_review_count", 0, "MAIN_INDEPENDENT_APPROVAL_REQUIRED"),
        ("main_dismiss_stale_reviews", False, "MAIN_STALE_REVIEWS_NOT_DISMISSED"),
        ("main_require_last_push_approval", False, "MAIN_LAST_PUSH_APPROVAL_REQUIRED"),
        ("main_enforce_admins", False, "MAIN_ADMIN_ENFORCEMENT_REQUIRED"),
        ("main_branches_up_to_date_required", False, "MAIN_BRANCH_UP_TO_DATE_REQUIRED"),
        ("main_force_push_disabled", False, "MAIN_FORCE_PUSH_NOT_DISABLED"),
        ("main_deletion_disabled", False, "MAIN_DELETION_NOT_DISABLED"),
        ("required_status_checks", ["other-check"], "MAIN_FINANCIAL_CI_REQUIRED_CHECK_MISSING"),
        ("required_status_check_apps", [{"context": "test", "app_id": 1}], "MAIN_FINANCIAL_CI_CHECK_APP_ID_MISMATCH"),
        ("main_pull_request_bypass_allowances", {"users": ["D1traverser-debug"], "teams": [], "apps": []}, "MAIN_PULL_REQUEST_BYPASS_NOT_ALLOWED"),
        ("archive_tags_verified", False, "ARCHIVE_TAG_READBACK_NOT_VERIFIED"),
    ],
)
def test_main_hygiene_gate_rejects_unprotected_or_unverified_archive(field, value, reason):
    proofs = _proofs()
    gate = "FINANCIAL_MAIN_BRANCH_HYGIENE"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    evidence[field] = value
    _resign_owner_gate(proofs, evidence, gate)
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert reason in result["gates"][gate]["reason"]


def test_owner_goal_gate_rejects_source_sha_not_matching_authenticated_message():
    proofs = _proofs()
    gate = "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    evidence["source_sha256"] = "c"*64
    _resign_owner_gate(proofs, evidence, gate)
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert "OWNER_SOURCE_SHA_MISMATCH" in result["gates"][gate]["reason"]


def test_owner_goal_gate_rejects_message_attestation_for_different_source_ref():
    proofs = _proofs()
    gate = "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    evidence["source_ref"] = "chat://different-owner-message"
    _resign_owner_gate(proofs, evidence, gate)
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert "OWNER_MESSAGE_ATTESTATION_INVALID" in result["gates"][gate]["reason"]


def test_owner_goal_gate_rejects_missing_original_message_attestation():
    proofs = _proofs()
    gate = "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION"
    evidence = copy.deepcopy(proofs[gate]["evidence"])
    evidence.pop("owner_message_attestation")
    _resign_owner_gate(proofs, evidence, gate)
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, ci_attestation=_ci(),
        code_tests_passed=True,
    )
    assert gate in result["open_gates"]
    assert "GATE_EVIDENCE_FIELDS_MISSING" in result["gates"][gate]["reason"]
