import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_hosted_cognition_contract_is_current_and_explicit():
    caps = _json(".uaos/CAPABILITIES.json")
    execution = _json("config/EXECUTION_CONTRACT.json")

    assert caps["common_capabilities_inheritance"] == "UAOS_HOSTED"
    assert caps["uaos_common_capabilities_contract_min"] == "1.5.0"
    assert caps["hosted_cognition_semantics"]["problem_response_floor"] == [
        "MICRO_DIAGNOSIS",
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT",
        "GOVERNING_ASSUMPTION_CHALLENGE",
        "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH",
    ]
    assert caps["hosted_cognition_semantics"]["rule"].startswith("EVERY_DETECTED_PROBLEM_REQUIRES_RESEARCH_AND_REFLECTION")
    assert execution["problem_and_evolution"]["every_problem_requires_external_research_and_reflection"] is True
    assert execution["hosted_governance"]["problem_floor_activation"] == "EVERY_DETECTED_PROBLEM__FAMILIARITY_IS_NOT_A_WAIVER"


def test_domain_evolution_ownership_remains_financial_and_parent_common_scope_stays_external():
    caps = _json(".uaos/CAPABILITIES.json")
    adapter = _json(".uaos/ADAPTER.json")
    execution = _json("config/EXECUTION_CONTRACT.json")

    assert caps["domain_evolution_role"] == "DOMAIN_EVIDENCE_EVAL_AND_BUSINESS_OWNER_PROMOTION"
    assert "COMMON_OR_CROSS_DOMAIN_CHANGE_UPCALLS_UAOS" in caps["domain_evolution_semantics"]
    assert adapter["common_or_cross_domain_evolution_authority"] == "UAOS"
    assert "owner_lifecycle.py" in adapter["domain_evolution_authority"]
    assert execution["hosted_governance"]["domain_evolution_owner"] == "FINANCIAL_WRITING_FOR_FINANCIAL_BUSINESS_RULES"
    assert execution["hosted_governance"]["common_cross_domain_evolution_owner"] == "UAOS"
    assert execution["problem_and_evolution"]["one_off_observation_auto_promotes_to_global_rule"] is False
    assert execution["problem_and_evolution"]["systemic_change_requires_regression_or_eval_evidence"] is True
    assert execution["problem_and_evolution"]["post_promotion_observation_required_for_evolution_closure"] is True


def test_product_requirements_are_domain_owned_and_mapped_to_acceptance():
    manifest = _json(".uaos/MANIFEST.json")
    adapter = _json(".uaos/ADAPTER.json")
    ownership = _json("config/rule_ownership.json")
    product = (ROOT / "docs/product_requirements.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")

    assert manifest["domain_authority"]["product_requirements"] == "docs/product_requirements.md"
    assert adapter["domain_product_requirement_authority"].endswith("docs/product_requirements.md")
    assert "product" in ownership and "cognition" in ownership
    for phrase in (
        "Product outcome",
        "Primary user journeys",
        "Functional requirement map",
        "Failure and recovery semantics",
        "Cognition inheritance contract",
        "Evolution inheritance contract",
        "Explicit non-goals",
        "Product completion criteria",
    ):
        assert phrase in product
    assert "Acceptance evidence" in product
    assert "Hosted cognition architecture" in architecture
    assert "Governed evolution architecture" in architecture
    assert "Product architecture review" in architecture


def test_financial_maintenance_requires_problem_research_reflection_and_keeps_packaged_mirror_equal():
    root = (ROOT / "references/maintenance.md").read_text(encoding="utf-8")
    packaged = (ROOT / "financial_writing_agent/resources/references/maintenance.md").read_text(encoding="utf-8")
    assert root == packaged
    assert "Any detected problem activates the UAOS-hosted cognition floor" in root
    assert "Familiarity is not a waiver" in root
    assert "relevant external research" in root
    assert "compare at least two credible alternatives" in root
    assert "observe post-promotion behavior and keep, rollback or retire" in root
    assert "Parent upcall boundary" in root


def test_direct_activation_is_not_replaced_by_parent_business_proxy():
    skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    execution = _json("config/EXECUTION_CONTRACT.json")
    assert "A fresh chat may select Financial Writing directly" in skill
    assert "normal article turns do **not** traverse a live UAOS business proxy" in skill
    assert execution["execution"]["direct_domain_activation"] is True
    assert execution["execution"]["live_parent_business_proxy_required"] is False
    assert execution["identity"]["parent_child_id_equality_required"] is False
