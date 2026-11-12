"""Financial-native owner-intent admission for task requirement changes.

A model's label is never enough to upgrade advice to explicit user authority.
The real connected client supplies an authenticated user-message reader. This
module binds role, source bytes, exact excerpt and action classification before
the existing single Article Aggregate is mutated.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Callable, Mapping

OWNER_REQUIREMENT_KINDS = {
    "USER_REQUIREMENT": "USER_EXPLICIT",
    "USER_CORRECTION": "USER_CORRECTION",
    "USER_PREFERENCE": "USER_PREFERENCE",
}
NONBINDING_KINDS = frozenset({
    "USER_SUGGESTION", "IMPLEMENTATION_IDEA", "ISSUE_REPORT",
    "ASSISTANT_INFERENCE", "UNKNOWN",
})


class FinancialIntentEvidenceError(ValueError):
    pass


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise FinancialIntentEvidenceError("FINANCIAL_INTENT_" + message)


def _read_verified_user_message(
    source_ref: str,
    excerpt: str,
    owner_instruction_reader: Callable[[str], Mapping[str, Any] | None] | None,
) -> tuple[dict[str, str], str]:
    _require(callable(owner_instruction_reader), "AUTHENTICATED_MESSAGE_READER_REQUIRED")
    try:
        message = owner_instruction_reader(source_ref)
    except Exception as exc:
        raise FinancialIntentEvidenceError("FINANCIAL_INTENT_SOURCE_READ_FAILED") from exc
    _require(isinstance(message, Mapping), "SOURCE_UNAVAILABLE")
    _require(message.get("source_ref") == source_ref, "SOURCE_IDENTITY_MISMATCH")
    _require(message.get("source_role") == "user", "SOURCE_NOT_USER")
    _require(isinstance(message.get("authenticated_actor"), str)
             and bool(message["authenticated_actor"].strip()), "ACTOR_UNAUTHENTICATED")
    content = message.get("text")
    _require(isinstance(content, str) and bool(content), "SOURCE_TEXT_UNAVAILABLE")
    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    _require(sha == message.get("sha256"), "SOURCE_HASH_MISMATCH")
    _require(excerpt in content, "USER_EXCERPT_NOT_FOUND")
    return {
        "source_ref": source_ref,
        "source_sha256": sha,
        "excerpt_sha256": hashlib.sha256(excerpt.encode("utf-8")).hexdigest(),
    }, content


def _verified_user_excerpt(
    source_ref: str,
    excerpt: str,
    owner_instruction_reader: Callable[[str], Mapping[str, Any] | None] | None,
) -> dict[str, str]:
    return _read_verified_user_message(source_ref, excerpt, owner_instruction_reader)[0]


def _change_digest(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def verify_nonbinding_owner_intent(
    intent: Mapping[str, Any] | None,
    *,
    owner_instruction_reader: Callable[[str], Mapping[str, Any] | None] | None,
) -> dict[str, Any]:
    """Keep user ideas/issues visible without pretending they are hard requirements."""
    _require(isinstance(intent, Mapping), "RECORD_REQUIRED")
    _require(set(intent) == {
        "intent", "source_ref", "verbatim_excerpt", "classification_reason",
    }, "FIELDS_INVALID")
    kind = intent.get("intent")
    _require(kind in NONBINDING_KINDS, "NONBINDING_CLASSIFICATION_REQUIRED")
    source_ref, excerpt = intent.get("source_ref"), intent.get("verbatim_excerpt")
    _require(isinstance(source_ref, str) and bool(source_ref.strip()), "SOURCE_REF_REQUIRED")
    _require(isinstance(excerpt, str) and bool(excerpt.strip()), "EXACT_EXCERPT_REQUIRED")
    _require(isinstance(intent.get("classification_reason"), str)
             and bool(intent["classification_reason"].strip()), "RATIONALE_REQUIRED")
    evidence = _verified_user_excerpt(source_ref, excerpt, owner_instruction_reader)
    return {
        **evidence,
        "verified": True,
        "intent": kind,
        "assurance": "PROVIDER_AUTHENTICATED_USER_MESSAGE__NONBINDING_INTENT_ONLY",
    }


def verify_requirement_change_intent(
    intent: Mapping[str, Any] | None,
    *,
    evidence_ref: str,
    upserts: list[Mapping[str, Any]] | None,
    retire_ids: list[str] | None,
    owner_instruction_reader: Callable[[str], Mapping[str, Any] | None] | None,
    owner_semantic_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
    existing_requirements: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Prove provenance, not semantic infallibility of the model's classification.

    A bare chat:// pointer, quoted text supplied by the agent, or caller PASS
    cannot certify a user instruction. The provider must actually read the
    authenticated user's original message and return exact bytes.
    """
    _require(isinstance(intent, Mapping), "RECORD_REQUIRED")
    expected = {"intent", "source_ref", "verbatim_excerpt", "classification_reason"}
    _require(set(intent) == expected, "FIELDS_INVALID")
    kind = intent.get("intent")
    _require(kind in {*OWNER_REQUIREMENT_KINDS, *NONBINDING_KINDS}, "CLASSIFICATION_INVALID")
    _require(kind in OWNER_REQUIREMENT_KINDS, "NONBINDING_USER_OR_MODEL_IDEA")
    source_ref, excerpt = intent.get("source_ref"), intent.get("verbatim_excerpt")
    _require(isinstance(source_ref, str) and bool(source_ref.strip()), "SOURCE_REF_REQUIRED")
    _require(source_ref == evidence_ref, "SOURCE_REF_MISMATCH")
    _require(isinstance(excerpt, str) and bool(excerpt.strip()), "EXACT_EXCERPT_REQUIRED")
    _require(isinstance(intent.get("classification_reason"), str)
             and bool(intent["classification_reason"].strip()), "RATIONALE_REQUIRED")

    upserted = list(upserts or [])
    retired = list(retire_ids or [])
    _require(bool(upserted or retired), "NO_REQUIREMENT_CHANGE")
    _require(not retired or kind == "USER_CORRECTION",
             "RETIRE_REQUIRES_USER_CORRECTION")
    for item in upserted:
        _require(isinstance(item, Mapping), "UPSERT_INVALID")
        _require(item.get("source_kind") == OWNER_REQUIREMENT_KINDS[kind],
                 "UPSERT_CLASSIFICATION_MISMATCH")
        _require(item.get("evidence_ref") == source_ref, "UPSERT_SOURCE_MISMATCH")

    evidence, original_user_text = _read_verified_user_message(
        source_ref, excerpt, owner_instruction_reader,
    )
    old = {
        str(item.get("requirement_id")): deepcopy(dict(item))
        for item in (existing_requirements or [])
        if isinstance(item, Mapping)
    }
    _require(all(item in old for item in retired), "RETIRE_TARGET_NOT_ACTIVE")
    _require(callable(owner_semantic_verifier), "SEMANTIC_VERIFIER_REQUIRED")
    identity = {
        "source_ref": source_ref,
        "source_sha256": evidence["source_sha256"],
        "excerpt_sha256": evidence["excerpt_sha256"],
        "intent": kind,
        "upserts": deepcopy(upserted),
        "retire_ids": sorted(retired),
        "retire_targets": [old[item] for item in sorted(retired)],
    }
    challenge = {
        **identity,
        "change_sha256": _change_digest(identity),
        "original_user_message": original_user_text,
        "verbatim_excerpt": excerpt,
    }
    try:
        answer = owner_semantic_verifier(deepcopy(challenge))
    except Exception as exc:
        raise FinancialIntentEvidenceError("FINANCIAL_INTENT_SEMANTIC_PROVIDER_FAILED") from exc
    _require(isinstance(answer, Mapping) and answer.get("approved") is True,
             "SEMANTIC_APPROVAL_NOT_VERIFIED")
    _require(answer.get("source_sha256") == evidence["source_sha256"]
             and answer.get("change_sha256") == challenge["change_sha256"],
             "SEMANTIC_PROOF_WRONG_SOURCE_OR_CHANGE")
    _require(isinstance(answer.get("reviewer_principal"), str)
             and bool(answer["reviewer_principal"].strip())
             and answer["reviewer_principal"] not in {
                 "financial-agent", "FINANCIAL_WRITING_OWNER", "unverified-model"
             }, "SEMANTIC_INDEPENDENT_REVIEWER_REQUIRED")
    _require(answer.get("assurance") == "OWNER_EXPLICITLY_CONFIRMED_EXACT_CHANGE",
             "SEMANTIC_EXPLICIT_OWNER_CONFIRMATION_REQUIRED")
    return {
        **evidence,
        "verified": True,
        "intent": kind,
        "semantic_approval": {
            "approved": True,
            "source_sha256": evidence["source_sha256"],
            "change_sha256": challenge["change_sha256"],
            "reviewer_principal": answer["reviewer_principal"],
            "assurance": answer["assurance"],
        },
        "assurance": "PROVIDER_AUTHENTICATED_USER_MESSAGE_AND_EXPLICIT_OWNER_CHANGE_APPROVAL",
    }
