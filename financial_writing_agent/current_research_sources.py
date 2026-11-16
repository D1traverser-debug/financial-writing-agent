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

from .private_research import (
    SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS,
    required_modules_for_version,
    validate_private_research_brief,
)


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


def _package_source_contract(
    research_package: Mapping[str, Any],
    *,
    brief_refs: set[str],
) -> dict[str, str]:
    """Bind every ResearchPackage evidence-ledger source to the admitted brief.

    The returned mapping binds each declared universe-recall source to the
    provider source-family identity that must be observed during readback.
    """
    ledger = research_package.get("evidence_ledger")
    _require(
        isinstance(ledger, list) and bool(ledger),
        "CURRENT_RESEARCH_PACKAGE_EVIDENCE_LEDGER_REQUIRED",
    )
    package_refs: set[str] = set()
    for index, item in enumerate(ledger):
        _require(
            isinstance(item, Mapping),
            f"CURRENT_RESEARCH_PACKAGE_EVIDENCE_LEDGER_ROW_INVALID:{index}",
        )
        source = item.get("source")
        _require(
            isinstance(source, str) and bool(source.strip()),
            f"CURRENT_RESEARCH_PACKAGE_EVIDENCE_SOURCE_INVALID:{index}",
        )
        package_refs.add(source.strip())

    unbound = sorted(package_refs - brief_refs)
    _require(
        not unbound,
        "CURRENT_RESEARCH_PACKAGE_EVIDENCE_NOT_BOUND_TO_PRIVATE_BRIEF:"
        + ",".join(item[:100] for item in unbound[:20]),
    )

    coverage = research_package.get("universe_coverage")
    if not isinstance(coverage, Mapping):
        return {}
    recall_sources = coverage.get("recall_sources", [])
    recall_families = coverage.get("recall_source_families", [])
    if not recall_sources and not recall_families:
        return {}
    _require(
        isinstance(recall_sources, list)
        and isinstance(recall_families, list)
        and len(recall_sources) >= 2
        and len(recall_sources) == len(recall_families),
        "CURRENT_RESEARCH_RECALL_SOURCE_FAMILY_BINDING_INVALID",
    )
    normalized_sources: list[str] = []
    normalized_families: list[str] = []
    for source, family in zip(recall_sources, recall_families):
        _require(
            isinstance(source, str) and bool(source.strip()),
            "CURRENT_RESEARCH_RECALL_SOURCE_REF_INVALID",
        )
        _require(
            isinstance(family, str) and len(family.strip()) >= 3,
            "CURRENT_RESEARCH_RECALL_SOURCE_FAMILY_INVALID",
        )
        normalized_sources.append(source.strip())
        normalized_families.append(family.strip().casefold())
    _require(
        len(normalized_sources) == len(set(normalized_sources)),
        "CURRENT_RESEARCH_RECALL_SOURCE_REF_DUPLICATED",
    )
    _require(
        all(source in package_refs for source in normalized_sources),
        "CURRENT_RESEARCH_RECALL_SOURCE_NOT_IN_EVIDENCE_LEDGER",
    )
    _require(
        len(set(normalized_families)) >= 2,
        "CURRENT_RESEARCH_RECALL_SOURCE_FAMILIES_NOT_DISTINCT",
    )
    return dict(zip(normalized_sources, normalized_families))


def verify_current_research_sources(
    raw_brief: Mapping[str, Any],
    *,
    source_reader: Callable[[str], Mapping[str, Any] | None] | None,
    research_package: Mapping[str, Any] | None = None,
    as_of: datetime | None = None,
    maximum_brief_age_days: int = 7,
    maximum_snapshot_age_days: int = 7,
) -> dict[str, Any]:
    """Require exact provider bytes and recency for every applicable module source.

    Both PrivateResearchBrief 1.0 and 1.1 are supported according to the
    persisted task marker. When a full-universe ResearchPackage is supplied,
    every evidence-ledger source must also occur in the brief's module refs;
    the actual provider family of each declared recall source is checked
    against the package's family ledger.
    
    Source reader returns text, sha256, retrieved_at, and source_family. It is a
    distinct external provider callback; a draft's own made-up URLs cannot be
    treated as retrievable source bytes. Primary authority and financial truth
    still require a separately admitted domain fact/independent expert review.
    """
    version = str(raw_brief.get("contract_version", "")).strip()
    _require(
        version in SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS,
        "CURRENT_RESEARCH_PRIVATE_BRIEF_VERSION_UNSUPPORTED",
    )
    brief = validate_private_research_brief(
        raw_brief, expected_contract_version=version,
    )
    _require(callable(source_reader), "CURRENT_RESEARCH_SOURCE_READER_REQUIRED")
    now = (as_of or datetime.now(timezone.utc)).astimezone(timezone.utc)
    freeze = _utc(brief["as_of"], "CURRENT_RESEARCH_AS_OF")
    age = (now - freeze).total_seconds()
    _require(-86400 <= age <= maximum_brief_age_days * 86400,
             "CURRENT_RESEARCH_BRIEF_STALE_OR_FUTURE")

    refs: set[str] = set()
    for name in required_modules_for_version(version):
        module = brief["modules"][name]
        if module["status"] != "APPLICABLE":
            continue
        normalized: list[str] = []
        for ref in module["evidence_refs"]:
            _require(
                isinstance(ref, str) and bool(ref.strip()),
                f"CURRENT_RESEARCH_SOURCE_REF_INVALID:{name}",
            )
            normalized.append(ref.strip())
        _require(
            len(normalized) == len(set(normalized)),
            f"CURRENT_RESEARCH_SOURCE_REF_DUPLICATED:{name}",
        )
        refs.update(normalized)

    _require(bool(refs), "CURRENT_RESEARCH_SOURCE_REFS_MISSING")
    expected_recall_families: dict[str, str] = {}
    if research_package is not None:
        _require(
            isinstance(research_package, Mapping),
            "CURRENT_RESEARCH_PACKAGE_INVALID",
        )
        expected_recall_families = _package_source_contract(
            research_package, brief_refs=refs,
        )

    receipt: list[dict[str, Any]] = []
    families: set[str] = set()
    observed_family_by_ref: dict[str, str] = {}
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
        observed_family_by_ref[ref] = family.casefold()
        expected_family = expected_recall_families.get(ref)
        if expected_family is not None:
            _require(
                family.casefold() == expected_family,
                f"CURRENT_RESEARCH_RECALL_SOURCE_FAMILY_MISMATCH:{ref[:80]}",
            )
        receipt.append({
            "source_ref_sha256": hashlib.sha256(ref.encode("utf-8")).hexdigest(),
            "body_sha256": sha,
            "source_family": family,
            "retrieved_at": retrieved.isoformat(),
        })

    _require(len(families) >= 2, "CURRENT_RESEARCH_TWO_SOURCE_FAMILIES_REQUIRED")
    actual_recall_families = {
        observed_family_by_ref[ref] for ref in expected_recall_families
    }
    if expected_recall_families:
        _require(
            len(actual_recall_families) >= 2,
            "CURRENT_RESEARCH_RECALL_SOURCE_FAMILIES_NOT_DISTINCT",
        )
    return {
        "schema_version": "1.0",
        "private_research_contract_version": version,
        "brief_as_of": freeze.isoformat(),
        "source_snapshots_observed": len(receipt),
        "source_families": sorted(families),
        "universe_recall_source_families": sorted(actual_recall_families),
        "snapshots": receipt,
        "assurance": "PROVIDER_BYTES_AND_RECENCY_ONLY__PRIMARY_AUTHORITY_AND_FACT_ENTAILMENT_NOT_VERIFIED",
        "primary_source_authority_verified": False,
        "financial_facts_verified": False,
    }
