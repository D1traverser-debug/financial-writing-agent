"""Financial-native owner-intent admission for task requirement changes.

A model's label is never enough to upgrade advice to explicit user authority.
The real connected client supplies an authenticated user-message reader. This
module binds role, source bytes, exact excerpt and action classification before
the existing single Article Aggregate is mutated.
"""
from __future__ import annotations

import hashlib
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


def verify_requirement_change_intent(
    intent: Mapping[str, Any] | None,
    *,
    evidence_ref: str,
    upserts: list[Mapping[str, Any]] | None,
    retire_ids: list[str] | None,
    owner_instruction_reader: Callable[[str], Mapping[str, Any] | None] | None,
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
        "verified": True,
        "intent": kind,
        "source_ref": source_ref,
        "source_sha256": sha,
        "excerpt_sha256": hashlib.sha256(excerpt.encode("utf-8")).hexdigest(),
        "assurance": "PROVIDER_AUTHENTICATED_USER_MESSAGE_AND_EXACT_EXCERPT__SEMANTIC_INTENT_UNDER_REVIEW",
    }
