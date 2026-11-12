"""Cryptographic provider trust boundaries; all signing keys here are synthetic pytest-only."""
import pytest

from financial_writing_agent.provider_attestation import (
    FinancialProviderAttestationError,
    verify_action_authorization,
    verify_owner_change_approval,
    verify_owner_message,
    verify_provider_attestation,
    verify_method_action_authorization,
    verify_method_promotion_attestation,
    verify_method_impact_attestation,
    request_sha256,
)
from trusted_provider_testkit import (
    signed_action_authorization, signed_owner_change_approval, signed_owner_message,
    signed_attestation, signed_method_action_authorization,
    signed_method_promotion, signed_method_impact,
)


def test_valid_signed_owner_message_is_bound_to_expected_owner_and_source():
    raw = signed_owner_message("message://1", "完整原始消息")
    verified = verify_owner_message(raw, source_ref="message://1")
    assert verified["authenticated_actor"] == "synthetic-financial-owner"


def test_unsigned_or_self_hashed_user_mapping_is_not_authentication():
    import hashlib
    text = "完整原始消息"
    forged = {
        "source_ref": "message://1", "source_role": "user",
        "authenticated_actor": "synthetic-financial-owner",
        "text": text, "sha256": hashlib.sha256(text.encode()).hexdigest(),
    }
    with pytest.raises(FinancialProviderAttestationError):
        verify_owner_message(forged, source_ref="message://1")


@pytest.mark.parametrize("mutate", [
    lambda r: r.update(authenticated_actor="attacker"),
    lambda r: r.update(audience="other-app"),
    lambda r: r.update(provider_id="other-provider"),
    lambda r: r.update(signature="0"*64),
    lambda r: r.update(issued_at=1),
    lambda r: r.update(source_ref="message://other"),
])
def test_tampered_identity_scope_freshness_or_source_invalidates_signature(mutate):
    raw = signed_owner_message("message://1", "完整原始消息")
    mutate(raw)
    with pytest.raises(FinancialProviderAttestationError):
        verify_owner_message(raw, source_ref="message://1")


def test_missing_deployment_key_fails_closed(monkeypatch):
    raw = signed_owner_message("message://1", "完整原始消息")
    monkeypatch.delenv("FINANCIAL_PROVIDER_ATTESTATION_KEY")
    with pytest.raises(FinancialProviderAttestationError, match="KEY_NOT_CONFIGURED"):
        verify_owner_message(raw, source_ref="message://1")


def test_owner_change_approval_is_bound_to_owner_source_and_exact_mutation():
    challenge = {"source_sha256":"a"*64,"change_sha256":"b"*64}
    signed = signed_owner_change_approval(challenge)
    result = verify_owner_change_approval(
        signed, source_sha256="a"*64, change_sha256="b"*64)
    assert result["authenticated_actor"] == "synthetic-financial-owner"
    with pytest.raises(FinancialProviderAttestationError):
        verify_owner_change_approval(
            signed, source_sha256="a"*64, change_sha256="c"*64)


def test_authorization_is_bound_to_exact_request_and_previous_state():
    request = {
        "action_id":"a1", "task_id":"t1", "operation":"CREATE_ARTICLE",
        "expected_state_blob_sha":None, "parameters":{"prompt":"x"},
    }
    signed = signed_action_authorization(request)
    assert verify_action_authorization(signed, request=request)["approved"] is True
    altered = {**request, "parameters":{"prompt":"different"}}
    with pytest.raises(FinancialProviderAttestationError):
        verify_action_authorization(signed, request=altered)


def test_callback_returning_boolean_or_fabricated_principal_cannot_authorize():
    request = {
        "action_id":"a1", "task_id":"t1", "operation":"CREATE_ARTICLE",
        "expected_state_blob_sha":None, "parameters":{},
    }
    with pytest.raises(FinancialProviderAttestationError):
        verify_action_authorization(True, request=request)
    forged = signed_attestation(
        "action_authorization", actor="attacker", approved=True,
        action_id=request["action_id"], task_id=request["task_id"],
        operation=request["operation"], expected_state_blob_sha=None,
        request_sha256=request_sha256(request),
    )
    with pytest.raises(FinancialProviderAttestationError):
        verify_action_authorization(forged, request=request)


def test_method_action_authorization_is_signed_owner_bound_and_catalog_cas_bound():
    request = {
        "schema_version":"1.0", "domain_id":"financial_writing",
        "action_id":"method-a1", "operation":"CREATE",
        "expected_catalog_blob_sha":"a"*40,
        "parameters":{"knowledge_id":"METHOD-ONE"},
    }
    signed = signed_method_action_authorization(request)
    verified = verify_method_action_authorization(signed, request=request)
    assert verified["authenticated_actor"] == "synthetic-financial-owner"
    changed = {**request, "expected_catalog_blob_sha":"b"*40}
    with pytest.raises(FinancialProviderAttestationError):
        verify_method_action_authorization(signed, request=changed)
    with pytest.raises(FinancialProviderAttestationError):
        verify_method_action_authorization(True, request=request)


def test_method_promotion_requires_separate_signed_reviewer_and_exact_record_decision():
    challenge = {
        "knowledge_id":"METHOD-ONE", "record_sha256":"a"*64,
        "decision_sha256":"b"*64, "validation_refs":["ci://exact"],
        "review_ref":"review://exact",
    }
    signed = signed_method_promotion(challenge)
    verified = verify_method_promotion_attestation(signed, challenge=challenge)
    assert verified["authenticated_actor"] == "synthetic-method-reviewer"
    assert verified["provider_id"] == "synthetic-method-review-provider"
    altered = {**challenge, "record_sha256":"c"*64}
    with pytest.raises(FinancialProviderAttestationError):
        verify_method_promotion_attestation(signed, challenge=altered)
    owner_signed = signed_attestation(
        "method_promotion_review", actor="synthetic-financial-owner",
        key_env="FINANCIAL_METHOD_REVIEW_KEY",
        provider_env="FINANCIAL_METHOD_REVIEW_PROVIDER_ID",
        approved=True, **challenge,
    )
    with pytest.raises(FinancialProviderAttestationError, match="DIFFER_FROM_OWNER"):
        verify_method_promotion_attestation(owner_signed, challenge=challenge)


def test_method_impact_requires_separate_signed_reviewer_and_exact_stage_set():
    challenge = {
        "knowledge_id":"METHOD-ONE", "target_change_revision":3,
        "event_sha256":"d"*64,
        "stage_evidence_refs":{"RESEARCH":"evidence://research","EDITORIAL":"evidence://editorial"},
    }
    signed = signed_method_impact(challenge)
    verified = verify_method_impact_attestation(signed, challenge=challenge)
    assert verified["authenticated_actor"] == "synthetic-method-reviewer"
    altered = {**challenge, "stage_evidence_refs":{"RESEARCH":"evidence://other"}}
    with pytest.raises(FinancialProviderAttestationError):
        verify_method_impact_attestation(signed, challenge=altered)
