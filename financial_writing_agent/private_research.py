from __future__ import annotations

from typing import Any, Mapping

PRIVATE_RESEARCH_CONTRACT_VERSION = "1.0"

APPLICABLE = "APPLICABLE"
NOT_MATERIAL = "NOT_MATERIAL"
MODULE_STATUSES = frozenset({APPLICABLE, NOT_MATERIAL})
COVERAGE_STATES = frozenset({"COMPLETE", "BOUNDED_WITH_GAPS"})

REQUIRED_MODULES: tuple[str, ...] = (
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


class PrivateResearchAdmissionError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PrivateResearchAdmissionError(message)


def validate_private_research_brief(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate the durable private-research evidence required by new Financial tasks.

    The contract is intentionally structural. It proves that the required research jobs were
    represented and evidence-bound; it does not pretend that semantic quality can be reduced
    to one numeric score. Modules that genuinely do not apply must say NOT_MATERIAL and give
    a reason rather than fabricating market/short-horizon analysis.
    """

    _require(isinstance(raw, Mapping), "current RESEARCH transition requires private_research_brief")
    brief = dict(raw)

    _require(
        brief.get("contract_version") == PRIVATE_RESEARCH_CONTRACT_VERSION,
        f"private research contract_version must be {PRIVATE_RESEARCH_CONTRACT_VERSION}",
    )
    _require(str(brief.get("as_of", "")).strip(), "private research brief requires non-empty as_of")
    _require(
        brief.get("coverage_state") in COVERAGE_STATES,
        f"private research coverage_state must be one of {sorted(COVERAGE_STATES)}",
    )

    modules = brief.get("modules")
    _require(isinstance(modules, Mapping), "private research brief requires modules mapping")
    missing = [name for name in REQUIRED_MODULES if name not in modules]
    _require(not missing, f"private research brief missing required modules: {missing}")

    for name in REQUIRED_MODULES:
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
