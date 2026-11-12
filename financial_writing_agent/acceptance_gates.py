"""Financial system release authority: green tests are never whole-system acceptance."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Callable, Mapping

SYSTEM_GATES = (
    "ORIGINAL_GOAL_AND_SEMANTIC_CORRECTION",
    "LEGAL_ARTICLE_GRAPH_AND_RECOVERY",
    "METHOD_KNOWLEDGE_CRUD_AND_IMPACT",
    "PROVIDER_AUTHENTICATED_RUNTIME_CAS",
    "NATIVE_FINANCIAL_PLUGIN_CLIENT_ACTIVATION",
    "INDEPENDENT_EXTERNAL_ADVERSARIAL_REVIEW",
    "FINANCIAL_MAIN_BRANCH_HYGIENE",
)
GATE_VERSION = "1.0"


def _digest(raw: Any) -> str:
    return hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def evaluate_system_acceptance(
    *,
    head_sha: str,
    candidate_proofs: Mapping[str, Mapping[str, Any]] | None = None,
    trusted_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
    code_tests_passed: bool = False,
) -> dict[str, Any]:
    """Only an actually trusted external verifier can close a system gate.

    Treating a caller-written PASS flag or the existence of a callback as
    independent certification is forbidden. The provider must check an
    immutable source/actor/effect through its own trust boundary.
    """
    if not isinstance(head_sha, str) or len(head_sha) != 40:
        raise ValueError("FINANCIAL_SYSTEM_HEAD_SHA_REQUIRED")
    proofs = candidate_proofs or {}
    if not isinstance(proofs, Mapping) or set(proofs) - set(SYSTEM_GATES):
        raise ValueError("FINANCIAL_SYSTEM_GATE_IDS_UNKNOWN")
    results: dict[str, dict[str, Any]] = {}
    for gate in SYSTEM_GATES:
        raw = proofs.get(gate)
        status = "OPEN__EXTERNAL_EVIDENCE_NOT_VERIFIED"
        reason = "NO_EXACT_SOURCE_AND_PROVIDER_READBACK"
        if raw is not None:
            if not isinstance(raw, Mapping):
                raise ValueError("FINANCIAL_SYSTEM_EVIDENCE_INVALID")
            evidence = deepcopy(dict(raw))
            if evidence.get("target_head_sha") != head_sha:
                reason = "EVIDENCE_HEAD_MISMATCH"
            elif not callable(trusted_verifier):
                reason = "EXTERNAL_ATTESTOR_UNAVAILABLE"
            else:
                challenge = {
                    "gate": gate,
                    "target_head_sha": head_sha,
                    "source_digest": _digest(evidence),
                    "source": evidence,
                }
                try:
                    observed = trusted_verifier(deepcopy(challenge))
                except Exception:
                    observed = None
                if (
                    isinstance(observed, Mapping)
                    and observed.get("verified") is True
                    and observed.get("gate") == gate
                    and observed.get("target_head_sha") == head_sha
                    and observed.get("source_digest") == challenge["source_digest"]
                    and isinstance(observed.get("independent_principal"), str)
                    and observed["independent_principal"].strip()
                    and observed["independent_principal"] != "FINANCIAL_WRITING_OWNER"
                    and isinstance(observed.get("provider_record_ref"), str)
                    and observed["provider_record_ref"].strip()
                ):
                    status, reason = "VERIFIED_BY_TRUSTED_EXTERNAL_PROVIDER", "PROVIDER_EFFECT_READBACK"
                else:
                    reason = "EXTERNAL_ATTESTATION_REJECTED"
        results[gate] = {"status": status, "reason": reason}
    not_verified = [gate for gate, rec in results.items()
                    if rec["status"] != "VERIFIED_BY_TRUSTED_EXTERNAL_PROVIDER"]
    return {
        "schema_version": GATE_VERSION,
        "product": "financial_writing",
        "target_head_sha": head_sha,
        "code_ci": "PASS" if code_tests_passed is True else "NOT_VERIFIED",
        "system_status": (
            "ACCEPTED__EXTERNAL_EVIDENCE_VERIFIED"
            if not not_verified and code_tests_passed is True
            else "NOT_READY__REQUIRES_EXTERNAL_EVIDENCE"
        ),
        "gates": results,
        "open_gates": not_verified,
        "article_editorial_quality": "OUT_OF_SCOPE__NOT_CERTIFIED",
        "caos_mutations_allowed": False,
    }
