from __future__ import annotations

from typing import Any, Mapping

PRIVATE_RESEARCH_CONTRACT_VERSION = "1.1"
SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS = frozenset({"1.0", "1.1"})

APPLICABLE = "APPLICABLE"
NOT_MATERIAL = "NOT_MATERIAL"
MODULE_STATUSES = frozenset({APPLICABLE, NOT_MATERIAL})
COVERAGE_STATES = frozenset({"COMPLETE", "BOUNDED_WITH_GAPS"})

V1_0_REQUIRED_MODULES: tuple[str, ...] = (
    "company_universe_and_value_chain",
    "business_granularity",
    "market_cap_and_liquidity",
    "catalyst_strength_and_freshness",
    "benefit_chain_tiering",
    "short_horizon_role_map",
    "market_structure_and_positioning",
    "counterfactual_company_comparison",
    "negative_and_falsification_pool",
    "scenario_tree",
    "next_window_validation",
    "publication_distillation",
)

V1_1_ADDITIONAL_MODULES: tuple[str, ...] = (
    "material_catalyst_and_policy_ledger",
    "driver_sustainability_operability_and_concept_map",
    "cross_segment_global_selection",
)

REQUIRED_MODULES: tuple[str, ...] = V1_0_REQUIRED_MODULES + V1_1_ADDITIONAL_MODULES


class PrivateResearchAdmissionError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PrivateResearchAdmissionError(message)


def required_modules_for_version(version: str) -> tuple[str, ...]:
    _require(
        version in SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS,
        f"unsupported private research contract_version: {version}",
    )
    if version == "1.0":
        return V1_0_REQUIRED_MODULES
    return REQUIRED_MODULES


def validate_private_research_brief(
    raw: Mapping[str, Any] | None,
    *,
    expected_contract_version: str | None = None,
) -> dict[str, Any]:
    """Validate the durable private-research evidence required by Financial tasks.

    1.1 adds three mandatory research jobs for new tasks: a material catalyst/policy ledger,
    driver/sustainability/market-operability/concept mapping, and a second-pass global
    cross-segment selection after within-segment comparison. Historical 1.0 briefs remain
    admissible only for states explicitly carrying the 1.0 marker.

    The contract remains intentionally structural. It proves required research jobs were
    represented and evidence-bound; semantic quality stays the responsibility of Research Audit.
    """

    _require(isinstance(raw, Mapping), "current RESEARCH transition requires private_research_brief")
    brief = dict(raw)

    version = str(brief.get("contract_version", "")).strip()
    _require(
        version in SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS,
        f"private research contract_version must be one of {sorted(SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS)}",
    )
    if expected_contract_version is not None:
        _require(
            expected_contract_version in SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS,
            f"unsupported expected private research contract_version: {expected_contract_version}",
        )
        _require(
            version == expected_contract_version,
            f"private research brief contract_version {version} does not match state marker {expected_contract_version}",
        )

    _require(str(brief.get("as_of", "")).strip(), "private research brief requires non-empty as_of")
    _require(
        brief.get("coverage_state") in COVERAGE_STATES,
        f"private research coverage_state must be one of {sorted(COVERAGE_STATES)}",
    )

    modules = brief.get("modules")
    _require(isinstance(modules, Mapping), "private research brief requires modules mapping")
    required_modules = required_modules_for_version(version)
    missing = [name for name in required_modules if name not in modules]
    _require(not missing, f"private research brief missing required modules: {missing}")

    for name in required_modules:
        module = modules[name]
        _require(isinstance(module, Mapping), f"private research module {name} must be a mapping")
        status = module.get("status")
        _require(status in MODULE_STATUSES, f"private research module {name} has invalid status: {status}")
        _require(str(module.get("summary", "")).strip(), f"private research module {name} requires summary")

        evidence_refs = module.get("evidence_refs", [])
        _require(isinstance(evidence_refs, list), f"private research module {name} evidence_refs must be a list")
        if status == APPLICABLE:
            _require(evidence_refs, f"applicable private research module {name} requires evidence_refs")
        else:
            _require(
                str(module.get("reason", "")).strip(),
                f"NOT_MATERIAL private research module {name} requires reason",
            )

    unresolved = brief.get("unresolved_gaps", [])
    _require(isinstance(unresolved, list), "private research unresolved_gaps must be a list")
    if brief.get("coverage_state") == "COMPLETE":
        _require(not unresolved, "COMPLETE private research cannot retain unresolved_gaps")
    else:
        _require(unresolved, "BOUNDED_WITH_GAPS private research requires unresolved_gaps")

    return brief
