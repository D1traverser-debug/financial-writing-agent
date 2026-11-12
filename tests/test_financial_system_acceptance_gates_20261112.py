"""No whole-system PASS from pass counts, local labels or simulated callbacks."""
import pytest

from financial_writing_agent.acceptance_gates import (
    SYSTEM_GATES, evaluate_system_acceptance,
)

SHA = "d" * 40


def _proofs():
    return {
        gate: {"target_head_sha": SHA, "source_ref": f"provider://test/{gate}"}
        for gate in SYSTEM_GATES
    }


def test_green_ci_without_real_owner_client_provider_and_independent_review_is_not_ready():
    verdict = evaluate_system_acceptance(head_sha=SHA, code_tests_passed=True)
    assert verdict["code_ci"] == "PASS"
    assert verdict["system_status"].startswith("NOT_READY")
    assert len(verdict["open_gates"]) == len(SYSTEM_GATES)


def test_model_written_accepted_and_fake_pass_text_do_not_certify():
    proofs = {key: {**value, "verified": True, "pass": "ALL_GOOD"}
              for key, value in _proofs().items()}
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=proofs, code_tests_passed=True)
    assert result["system_status"].startswith("NOT_READY")
    assert all(r["reason"] == "EXTERNAL_ATTESTOR_UNAVAILABLE"
               for r in result["gates"].values())


def test_reviewer_must_attest_exact_sha_gate_and_immutable_source_digest():
    def fake_wrong_target(challenge):
        return {"verified": True, "gate": "SOME_OTHER_GATE",
                "target_head_sha": SHA, "source_digest": "f"*64,
                "independent_principal": "independent-test-author",
                "provider_record_ref": "provider://foo"}
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=_proofs(),
        trusted_verifier=fake_wrong_target, code_tests_passed=True,
    )
    assert result["system_status"].startswith("NOT_READY")


def test_external_attestor_interface_can_be_synthetically_replayed_without_real_certification():
    def mock_external(challenge):
        return {
            "verified": True, "gate": challenge["gate"],
            "target_head_sha": challenge["target_head_sha"],
            "source_digest": challenge["source_digest"],
            "independent_principal": "synthetic-test-independent-reviewer",
            "provider_record_ref": "synthetic://test-trusted-callback",
        }
    result = evaluate_system_acceptance(
        head_sha=SHA, candidate_proofs=_proofs(),
        trusted_verifier=mock_external, code_tests_passed=True,
    )
    assert result["system_status"].startswith("ACCEPTED")
    # This proves only acceptance algorithm correctness under a *fake* attestor.
    # It must never be reused as a real provider acceptance receipt.
    assert set(result["gates"]) == set(SYSTEM_GATES)


@pytest.mark.parametrize("bad", [{"UNKNOWN_GATE": {}}, {SYSTEM_GATES[0]: "PASS"}])
def test_bad_gate_identity_or_unstructured_evidence_is_rejected(bad):
    with pytest.raises(ValueError):
        evaluate_system_acceptance(head_sha=SHA, candidate_proofs=bad)
