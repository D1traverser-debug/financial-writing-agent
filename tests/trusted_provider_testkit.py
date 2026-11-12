"""Synthetic HMAC provider used only by pytest; never package or deploy."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from uuid import uuid4

from financial_writing_agent.provider_attestation import AUDIENCE, request_sha256


def signed_attestation(
    attestation_type: str, *, actor: str | None = None,
    key_env: str = "FINANCIAL_PROVIDER_ATTESTATION_KEY",
    provider_env: str = "FINANCIAL_TRUSTED_PROVIDER_ID", **claims,
):
    record = {
        "attestation_type": attestation_type,
        "provider_id": os.environ[provider_env],
        "audience": AUDIENCE,
        "authenticated_actor": actor or os.environ["FINANCIAL_OWNER_PRINCIPAL"],
        "issued_at": int(time.time()),
        "nonce": uuid4().hex,
        **claims,
    }
    key = os.environ[key_env].encode("utf-8")
    unsigned = json.dumps(record, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    record["signature"] = hmac.new(key, unsigned, hashlib.sha256).hexdigest()
    return record


def signed_action_authorization(request):
    return signed_attestation(
        "action_authorization",
        approved=True,
        action_id=request["action_id"],
        task_id=request["task_id"],
        operation=request["operation"],
        expected_state_blob_sha=request.get("expected_state_blob_sha"),
        request_sha256=request_sha256(request),
    )


def signed_owner_message(source_ref: str, text: str, *, source_role="user",
                         actor: str | None = None, sha256: str | None = None):
    return signed_attestation(
        "owner_message", actor=actor,
        source_ref=source_ref, source_role=source_role, text=text,
        sha256=sha256 or hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


def signed_owner_change_approval(request):
    return signed_attestation(
        "owner_change_approval",
        approved=True,
        source_sha256=request["source_sha256"],
        change_sha256=request["change_sha256"],
        confirmation_method="EXPLICIT_OWNER_CONFIRMATION",
        approval_record_ref="synthetic://owner-confirmation/" + request["change_sha256"],
    )


def signed_method_action_authorization(request):
    return signed_attestation(
        "method_action_authorization",
        approved=True,
        action_id=request["action_id"],
        domain_id=request["domain_id"],
        operation=request["operation"],
        expected_catalog_blob_sha=request["expected_catalog_blob_sha"],
        request_sha256=request_sha256(request),
    )


def signed_method_promotion(request):
    return signed_attestation(
        "method_promotion_review",
        actor="synthetic-method-reviewer",
        key_env="FINANCIAL_METHOD_REVIEW_KEY",
        provider_env="FINANCIAL_METHOD_REVIEW_PROVIDER_ID",
        approved=True,
        knowledge_id=request["knowledge_id"],
        record_sha256=request["record_sha256"],
        decision_sha256=request["decision_sha256"],
        validation_refs=request["validation_refs"],
        review_ref=request["review_ref"],
    )


def signed_method_impact(request):
    return signed_attestation(
        "method_impact_review",
        actor="synthetic-method-reviewer",
        key_env="FINANCIAL_METHOD_REVIEW_KEY",
        provider_env="FINANCIAL_METHOD_REVIEW_PROVIDER_ID",
        approved=True,
        knowledge_id=request["knowledge_id"],
        target_change_revision=request["target_change_revision"],
        event_sha256=request["event_sha256"],
        stage_evidence_refs=request["stage_evidence_refs"],
        verified_stages=list(request["stage_evidence_refs"]),
    )
