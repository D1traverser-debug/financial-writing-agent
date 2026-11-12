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


def _key_and_provider() -> tuple[bytes, str]:
    key = os.environ.get(KEY_ENV, "")
    provider = os.environ.get(PROVIDER_ENV, "").strip()
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
    max_age_seconds: int = MAX_AGE_SECONDS,
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
    key, provider_id = _key_and_provider()
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
    if issued_at > current + MAX_FUTURE_SKEW_SECONDS or current - issued_at > max_age_seconds:
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
