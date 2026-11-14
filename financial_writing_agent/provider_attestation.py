"""Cryptographically authenticated Financial provider attestations.

Callback injection is a transport mechanism, not an identity boundary. Every
callback result that grants authority must carry a provider HMAC attestation
bound to this audience, provider, authenticated actor, exact claims and a
short freshness window. No key/configuration => fail closed.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from copy import deepcopy
from typing import Any, Mapping

AUDIENCE = "financial-writing-agent"
KEY_ENV = "FINANCIAL_PROVIDER_ATTESTATION_KEY"
PROVIDER_ENV = "FINANCIAL_TRUSTED_PROVIDER_ID"
OWNER_ENV = "FINANCIAL_OWNER_PRINCIPAL"
MAX_AGE_SECONDS = 300
MAX_FUTURE_SKEW_SECONDS = 60


class FinancialProviderAttestationError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def payload_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def expected_owner_principal() -> str:
    value = os.environ.get(OWNER_ENV, "").strip()
    if not value:
        raise FinancialProviderAttestationError("FINANCIAL_EXPECTED_OWNER_NOT_CONFIGURED")
    return value


def _key_and_provider(
    key_env: str = KEY_ENV, provider_env: str = PROVIDER_ENV,
) -> tuple[bytes, str]:
    key = os.environ.get(key_env, "")
    provider = os.environ.get(provider_env, "").strip()
    if len(key.encode("utf-8")) < 32 or not provider:
        raise FinancialProviderAttestationError("FINANCIAL_TRUSTED_PROVIDER_KEY_NOT_CONFIGURED")
    return key.encode("utf-8"), provider


def verify_provider_attestation(
    raw: Mapping[str, Any] | None,
    *,
    expected_type: str,
    expected_claims: Mapping[str, Any] | None = None,
    expected_actor: str | None = None,
    now: int | None = None,
    max_age_seconds: int | None = MAX_AGE_SECONDS,
    key_env: str = KEY_ENV,
    provider_env: str = PROVIDER_ENV,
) -> dict[str, Any]:
    """Verify a signed, fresh, audience-bound provider receipt.

    The secret is deployment configuration, never part of the proposal or
    repository. A callback returning strings/booleans without a valid HMAC is
    not an attestation. The host provider must authenticate the actor before
    signing; this module then verifies the signed identity and exact claims.
    """
    if not isinstance(raw, Mapping):
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_ATTESTATION_MISSING")
    record = deepcopy(dict(raw))
    key, provider_id = _key_and_provider(key_env, provider_env)
    required = {
        "attestation_type", "provider_id", "audience", "authenticated_actor",
        "issued_at", "nonce", "signature",
    }
    if not required.issubset(record):
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_ATTESTATION_FIELDS_MISSING")
    if record.get("attestation_type") != expected_type:
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_ATTESTATION_TYPE_MISMATCH")
    if record.get("provider_id") != provider_id or record.get("audience") != AUDIENCE:
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_ATTESTATION_TRUST_DOMAIN_MISMATCH")
    actor = record.get("authenticated_actor")
    if not isinstance(actor, str) or not actor.strip():
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_ACTOR_MISSING")
    if expected_actor is not None and actor != expected_actor:
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_ACTOR_MISMATCH")
    issued_at = record.get("issued_at")
    if not isinstance(issued_at, int) or isinstance(issued_at, bool):
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_TIMESTAMP_INVALID")
    current = int(time.time()) if now is None else now
    if (max_age_seconds is not None
        and (not isinstance(max_age_seconds, int) or isinstance(max_age_seconds, bool)
             or max_age_seconds <= 0)):
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_MAX_AGE_INVALID")
    if issued_at > current + MAX_FUTURE_SKEW_SECONDS:
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_ATTESTATION_FUTURE_DATED")
    if max_age_seconds is not None and current - issued_at > max_age_seconds:
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_ATTESTATION_EXPIRED")
    nonce = record.get("nonce")
    if not isinstance(nonce, str) or len(nonce) < 16:
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_NONCE_INVALID")
    signature = record.get("signature")
    if not isinstance(signature, str) or len(signature) != 64:
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_SIGNATURE_INVALID")
    unsigned = {key_name: value for key_name, value in record.items() if key_name != "signature"}
    expected_signature = hmac.new(
        key, canonical_json(unsigned).encode("utf-8"), hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_SIGNATURE_MISMATCH")
    for claim, expected in (expected_claims or {}).items():
        if record.get(claim) != expected:
            raise FinancialProviderAttestationError("FINANCIAL_PROVIDER_CLAIM_MISMATCH:" + claim)
    return record


def verify_owner_message(
    raw: Mapping[str, Any] | None, *, source_ref: str,
) -> dict[str, Any]:
    record = verify_provider_attestation(
        raw, expected_type="owner_message",
        expected_claims={"source_ref": source_ref, "source_role": "user"},
        expected_actor=expected_owner_principal(),
    )
    text = record.get("text")
    if not isinstance(text, str) or not text:
        raise FinancialProviderAttestationError("FINANCIAL_OWNER_MESSAGE_TEXT_MISSING")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if record.get("sha256") != digest:
        raise FinancialProviderAttestationError("FINANCIAL_OWNER_MESSAGE_HASH_MISMATCH")
    return record


def verify_owner_change_approval(
    raw: Mapping[str, Any] | None, *,
    source_sha256: str, change_sha256: str,
) -> dict[str, Any]:
    return verify_provider_attestation(
        raw, expected_type="owner_change_approval",
        expected_claims={
            "approved": True,
            "source_sha256": source_sha256,
            "change_sha256": change_sha256,
            "confirmation_method": "EXPLICIT_OWNER_CONFIRMATION",
        },
        expected_actor=expected_owner_principal(),
    )


def request_sha256(request: Mapping[str, Any]) -> str:
    return payload_sha256(request)


def verify_action_authorization(
    raw: Mapping[str, Any] | None, *, request: Mapping[str, Any],
) -> dict[str, Any]:
    return verify_provider_attestation(
        raw, expected_type="action_authorization",
        expected_claims={
            "approved": True,
            "action_id": request["action_id"],
            "task_id": request["task_id"],
            "operation": request["operation"],
            "expected_state_blob_sha": request.get("expected_state_blob_sha"),
            "request_sha256": request_sha256(request),
        },
        expected_actor=expected_owner_principal(),
    )


def verify_persisted_action_authorization(
    raw: Mapping[str, Any] | None, *, expected_claims: Mapping[str, Any],
) -> dict[str, Any]:
    """Re-verify a previously admitted action signature without reapplying its short freshness window.

    Admission checked freshness before the state write. Historical readback checks
    the original signature, owner, provider, audience and exact persisted scope.
    """
    if not isinstance(raw, Mapping):
        raise FinancialProviderAttestationError("FINANCIAL_PERSISTED_ACTION_ATTESTATION_MISSING")
    issued_at = raw.get("issued_at")
    if not isinstance(issued_at, int) or isinstance(issued_at, bool):
        raise FinancialProviderAttestationError("FINANCIAL_PERSISTED_ACTION_TIMESTAMP_INVALID")
    digest = raw.get("request_sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(
        char not in "0123456789abcdef" for char in digest
    ):
        raise FinancialProviderAttestationError("FINANCIAL_PERSISTED_ACTION_REQUEST_DIGEST_INVALID")
    return verify_provider_attestation(
        raw, expected_type="action_authorization",
        expected_claims=expected_claims,
        expected_actor=expected_owner_principal(),
        max_age_seconds=None,
    )


def verify_method_action_authorization(
    raw: Mapping[str, Any] | None, *, request: Mapping[str, Any],
) -> dict[str, Any]:
    return verify_provider_attestation(
        raw, expected_type="method_action_authorization",
        expected_claims={
            "approved": True,
            "action_id": request["action_id"],
            "domain_id": request["domain_id"],
            "operation": request["operation"],
            "knowledge_id": request["parameters"]["knowledge_id"],
            "expected_catalog_blob_sha": request["expected_catalog_blob_sha"],
            "request_sha256": request_sha256(request),
        },
        expected_actor=expected_owner_principal(),
    )


def verify_persisted_method_action_authorization(
    raw: Mapping[str, Any] | None, *, request: Mapping[str, Any],
) -> dict[str, Any]:
    """Recheck immutable method-action signatures after their admission window."""
    if not isinstance(raw, Mapping):
        raise FinancialProviderAttestationError("FINANCIAL_PERSISTED_METHOD_ACTION_ATTESTATION_MISSING")
    issued_at = raw.get("issued_at")
    if not isinstance(issued_at, int) or isinstance(issued_at, bool):
        raise FinancialProviderAttestationError("FINANCIAL_PERSISTED_METHOD_ACTION_TIMESTAMP_INVALID")
    return verify_provider_attestation(
        raw, expected_type="method_action_authorization",
        expected_claims={
            "approved": True,
            "action_id": request["action_id"],
            "domain_id": request["domain_id"],
            "operation": request["operation"],
            "knowledge_id": request["parameters"]["knowledge_id"],
            "expected_catalog_blob_sha": request["expected_catalog_blob_sha"],
            "request_sha256": request_sha256(request),
        },
        expected_actor=expected_owner_principal(),
        max_age_seconds=None,
    )


def _verify_independent_method_review(
    raw: Mapping[str, Any] | None, *, expected_type: str,
    expected_claims: Mapping[str, Any], historical: bool = False,
) -> dict[str, Any]:
    if historical:
        if not isinstance(raw, Mapping):
            raise FinancialProviderAttestationError("FINANCIAL_PERSISTED_METHOD_REVIEW_MISSING")
        issued_at = raw.get("issued_at")
        if not isinstance(issued_at, int) or isinstance(issued_at, bool):
            raise FinancialProviderAttestationError("FINANCIAL_PERSISTED_METHOD_REVIEW_TIMESTAMP_INVALID")
    record = verify_provider_attestation(
        raw, expected_type=expected_type,
        expected_claims=expected_claims,
        key_env="FINANCIAL_METHOD_REVIEW_KEY",
        provider_env="FINANCIAL_METHOD_REVIEW_PROVIDER_ID",
        max_age_seconds=None if historical else MAX_AGE_SECONDS,
    )
    owner = expected_owner_principal()
    if record["authenticated_actor"] == owner:
        raise FinancialProviderAttestationError("FINANCIAL_METHOD_REVIEWER_MUST_DIFFER_FROM_OWNER")
    if record["provider_id"] == os.environ.get(PROVIDER_ENV):
        raise FinancialProviderAttestationError("FINANCIAL_METHOD_REVIEW_PROVIDER_MUST_BE_SEPARATE")
    return record


def verify_method_promotion_attestation(
    raw: Mapping[str, Any] | None, *, challenge: Mapping[str, Any],
) -> dict[str, Any]:
    return _verify_independent_method_review(
        raw, expected_type="method_promotion_review",
        expected_claims={
            "approved": True,
            "knowledge_id": challenge["knowledge_id"],
            "record_sha256": challenge["record_sha256"],
            "decision_sha256": challenge["decision_sha256"],
            "validation_refs": challenge["validation_refs"],
            "review_ref": challenge["review_ref"],
        },
    )


def verify_method_impact_attestation(
    raw: Mapping[str, Any] | None, *, challenge: Mapping[str, Any],
) -> dict[str, Any]:
    return _verify_independent_method_review(
        raw, expected_type="method_impact_review",
        expected_claims={
            "approved": True,
            "knowledge_id": challenge["knowledge_id"],
            "target_change_revision": challenge["target_change_revision"],
            "event_sha256": challenge["event_sha256"],
            "stage_evidence_refs": challenge["stage_evidence_refs"],
            "verified_stages": list(challenge["stage_evidence_refs"]),
        },
    )



def verify_persisted_method_promotion_attestation(
    raw: Mapping[str, Any] | None, *, challenge: Mapping[str, Any],
) -> dict[str, Any]:
    return _verify_independent_method_review(
        raw, expected_type="method_promotion_review", historical=True,
        expected_claims={
            "approved": True,
            "knowledge_id": challenge["knowledge_id"],
            "record_sha256": challenge["record_sha256"],
            "decision_sha256": challenge["decision_sha256"],
            "validation_refs": challenge["validation_refs"],
            "review_ref": challenge["review_ref"],
        },
    )


def verify_persisted_method_impact_attestation(
    raw: Mapping[str, Any] | None, *, challenge: Mapping[str, Any],
) -> dict[str, Any]:
    return _verify_independent_method_review(
        raw, expected_type="method_impact_review", historical=True,
        expected_claims={
            "approved": True,
            "knowledge_id": challenge["knowledge_id"],
            "target_change_revision": challenge["target_change_revision"],
            "event_sha256": challenge["event_sha256"],
            "stage_evidence_refs": challenge["stage_evidence_refs"],
            "verified_stages": list(challenge["stage_evidence_refs"]),
        },
    )

def verify_action_effect_attestation(
    raw: Mapping[str, Any] | None,
    *,
    expected_claims: Mapping[str, Any],
    expected_actor: str,
    expected_provider: str,
    historical: bool = False,
) -> dict[str, Any]:
    """Verify the provider's signed binding between an admitted request and exact state effect.

    The effect receipt is stored beside STATE.json so its signature can bind the
    resulting Git blob SHA without creating a self-referential state hash.
    """
    record = verify_provider_attestation(
        raw,
        expected_type="action_effect",
        expected_claims=expected_claims,
        expected_actor=expected_actor,
        max_age_seconds=None if historical else MAX_AGE_SECONDS,
    )
    if record.get("provider_id") != expected_provider:
        raise FinancialProviderAttestationError(
            "FINANCIAL_ACTION_EFFECT_PROVIDER_MISMATCH"
        )
    return record

