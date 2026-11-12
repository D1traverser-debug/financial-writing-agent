"""Signed external proof, not callback or Boolean self-certification."""
import pytest

from financial_writing_agent.acceptance_gates import (
    SYSTEM_GATES, REQUIRED_GATE_EVIDENCE, evaluate_system_acceptance,
)
from financial_writing_agent.provider_attestation import payload_sha256
from trusted_provider_testkit import signed_attestation

SHA = "d" * 40


def _proofs(*, reviewer="synthetic-independent-reviewer"):
    proofs = {}
    for gate in SYSTEM_GATES:
        evidence = {
            field: (
                ["synthetic-task"] if field == "affected_task_ids"
                else ["main"] if field == "after_branch_names"
                else "synthetic-evidence"
            )
            for field in REQUIRED_GATE_EVIDENCE[gate]
        }
        if gate == "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW":
            evidence.update({
                "reviewer_principal": reviewer,
                "reviewed_head_sha": SHA,
                "findings_status": "NO_UNRESOLVED_CRITICAL_FINDINGS",
            })
        proofs[gate] = signed_attestation(
            "system_gate", actor=reviewer if gate == "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW"
            else "synthetic-financial-owner",
            gate=gate, target_head_sha=SHA, evidence=evidence,
            evidence_sha256=payload_sha256(evidence),
        )
    return proofs


def _ci():
    return signed_attestation(
        "ci_run", actor="github-actions[bot]",
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
    assert all(r["reason"] == "FINANCIAL_PROVIDER_ATTESTATION_MISSING"
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
    assert result["system_status"] == "ACCEPTED__SIGNED_EXTERNAL_EVIDENCE_VERIFIED"
    assert result["ci_attestation_verified"] is True
    assert result["open_gates"] == []
    # The signature key is installed by pytest conftest only; this is a test of
    # signature verification, never a production acceptance record.


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
