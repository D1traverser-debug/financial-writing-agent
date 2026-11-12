"""Independent-of-CAOS research source-byte and freshness admission.

This verifies external provider readbacks, source snapshot digests and current
as-of discipline; a valid SHA does not establish source truth or entailment.
A live provider must obtain the bytes itself, not accept text minted by the
article author as proof of current issuer/regulator fact.
"""
from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from typing import Any

from .private_research import REQUIRED_MODULES, validate_private_research_brief


class CurrentResearchEvidenceError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CurrentResearchEvidenceError(message)


def _utc(value: Any, label: str) -> datetime:
    _require(isinstance(value, str) and bool(value.strip()), f"{label}_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CurrentResearchEvidenceError(f"{label}_ISO_INVALID") from exc
    # Date-only freezes explicitly use UTC rather than hidden local timezone.
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def verify_current_research_sources(
    raw_brief: Mapping[str, Any],
    *,
    source_reader: Callable[[str], Mapping[str, Any] | None] | None,
    as_of: datetime | None = None,
    maximum_brief_age_days: int = 7,
    maximum_snapshot_age_days: int = 7,
) -> dict[str, Any]:
    """Require actual exact-body SHA/recency for every APPLICABLE module reference.

    Source reader returns text, sha256, retrieved_at, and source_family. It is a
    distinct external provider callback; a draft's own made-up URLs cannot be
    treated as retrievable source bytes. Primary authority and financial truth
    still require a separately admitted domain fact/independent expert review.
    """
    brief = validate_private_research_brief(raw_brief, expected_contract_version="1.1")
    _require(callable(source_reader), "CURRENT_RESEARCH_SOURCE_READER_REQUIRED")
    now = (as_of or datetime.now(timezone.utc)).astimezone(timezone.utc)
    freeze = _utc(brief["as_of"], "CURRENT_RESEARCH_AS_OF")
    age = (now - freeze).total_seconds()
    _require(-86400 <= age <= maximum_brief_age_days * 86400,
             "CURRENT_RESEARCH_BRIEF_STALE_OR_FUTURE")

    refs: set[str] = set()
    for name in REQUIRED_MODULES:
        module = brief["modules"][name]
        if module["status"] == "APPLICABLE":
            refs.update(str(ref).strip() for ref in module["evidence_refs"])
    _require(bool(refs), "CURRENT_RESEARCH_SOURCE_REFS_MISSING")

    receipt: list[dict[str, Any]] = []
    families: set[str] = set()
    for ref in sorted(refs):
        _require(bool(ref), "CURRENT_RESEARCH_SOURCE_REF_EMPTY")
        try:
            observed = source_reader(ref)
        except Exception as exc:
            raise CurrentResearchEvidenceError("CURRENT_RESEARCH_SOURCE_READ_FAILED") from exc
        _require(isinstance(observed, Mapping), f"CURRENT_RESEARCH_SOURCE_NOT_FOUND:{ref[:80]}")
        text_value, sha = observed.get("text"), observed.get("sha256")
        _require(isinstance(text_value, str) and len(text_value.strip()) >= 20,
                 "CURRENT_RESEARCH_SOURCE_BODY_TOO_SHORT")
        _require(isinstance(sha, str) and re.fullmatch(r"[a-f0-9]{64}", sha) is not None,
                 "CURRENT_RESEARCH_SOURCE_SHA_INVALID")
        _require(hashlib.sha256(text_value.encode("utf-8")).hexdigest() == sha,
                 "CURRENT_RESEARCH_SOURCE_SHA_MISMATCH")
        retrieved = _utc(observed.get("retrieved_at"), "CURRENT_RESEARCH_SOURCE_RETRIEVED_AT")
        snapshot_age = (now - retrieved).total_seconds()
        _require(-86400 <= snapshot_age <= maximum_snapshot_age_days * 86400,
                 "CURRENT_RESEARCH_SOURCE_SNAPSHOT_STALE_OR_FUTURE")
        family = observed.get("source_family")
        _require(isinstance(family, str) and len(family.strip()) >= 3,
                 "CURRENT_RESEARCH_SOURCE_FAMILY_REQUIRED")
        family = family.strip()
        families.add(family)
        receipt.append({
            "source_ref_sha256": hashlib.sha256(ref.encode("utf-8")).hexdigest(),
            "body_sha256": sha,
            "source_family": family,
            "retrieved_at": retrieved.isoformat(),
        })
    _require(len(families) >= 2, "CURRENT_RESEARCH_TWO_SOURCE_FAMILIES_REQUIRED")
    return {
        "schema_version": "1.0",
        "brief_as_of": freeze.isoformat(),
        "source_snapshots_observed": len(receipt),
        "source_families": sorted(families),
        "snapshots": receipt,
        "assurance": "PROVIDER_BYTES_AND_RECENCY_ONLY__PRIMARY_AUTHORITY_AND_FACT_ENTAILMENT_NOT_VERIFIED",
        "primary_source_authority_verified": False,
        "financial_facts_verified": False,
    }
