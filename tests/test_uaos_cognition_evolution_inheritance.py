"""Legacy-binding regression: CAOS is the current parent; Financial owns business."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_caos_cognition_is_opt_in_not_legacy_hosted_self_certification():
    caps = _json(".uaos/CAPABILITIES.json")
    execution = _json("config/EXECUTION_CONTRACT.json")
    manifest = _json(".uaos/MANIFEST.json")

    assert manifest["controller"] == "D1traverser-debug/cognition-agent-os@main"
    assert caps["common_capabilities_inheritance"] == "PARENT_NATIVE_WHEN_PRESENT__NO_IMPLIED_RUNTIME"
    assert caps["caos_domain_contract_ref"].endswith("src/cognition_agent_os/domain_contract.py")
    assert "opt_in_route_selection" in caps["required_caos_parent_responsibilities"]
    assert "competing_causal_hypotheses_and_falsification" in caps["required_caos_parent_responsibilities"]
    assert caps["hosted_cognition_semantics"] == {
        "source": "CAOS_INTERACTIVE_PARENT_METHOD_WHEN_SELECTED",
        "local_overrides": "NONE",
        "implementation_evidence": "NOT_EQUIVALENT_TO_NATIVE_HOST_ACTIVATION",
    }
    assert execution["hosted_governance"]["problem_cognition_owner"] == "CAOS_OPT_IN_COGNITION_PARENT"
    assert execution["hosted_governance"]["parent_read_only_observation"] is True
    assert execution["hosted_governance"]["parent_host_or_plugin_assumed_connected"] is False
    assert execution["hosted_governance"]["financial_business_research_is_separate_from_generic_problem_cognition"] is True
    assert execution["problem_and_evolution"]["generic_problem_cognition_owner"] == "CAOS_OPT_IN_COGNITION_PARENT"
    assert execution["problem_and_evolution"]["generic_problem_cognition_is_copied_locally"] is False
    assert execution["cognition_and_decision"]["problem_or_architecture_change_requires_external_method_evidence"] is True


def test_domain_evolution_remains_child_owned_with_caos_only_for_common_scope():
    caps = _json(".uaos/CAPABILITIES.json")
    adapter = _json(".uaos/ADAPTER.json")
    execution = _json("config/EXECUTION_CONTRACT.json")
    assert caps["domain_evolution_role"] == "DOMAIN_EVIDENCE_EVAL_AND_BUSINESS_OWNER_PROMOTION"
    assert "COMMON_CROSS_DOMAIN_UPCALL_CAOS" in caps["domain_evolution_semantics"]
    assert adapter["common_or_cross_domain_evolution_authority"] == "CAOS"
    assert "owner_lifecycle.py" in adapter["domain_evolution_authority"]
    assert execution["hosted_governance"]["domain_evolution_owner"] == "FINANCIAL_WRITING_FOR_FINANCIAL_BUSINESS_RULES"
    assert execution["hosted_governance"]["common_cross_domain_evolution_owner"] == "CAOS"
    assert execution["problem_and_evolution"]["one_off_observation_auto_promotes_to_global_rule"] is False
    assert execution["problem_and_evolution"]["systemic_change_requires_regression_or_eval_evidence"] is True
    assert execution["problem_and_evolution"]["post_promotion_observation_required_for_evolution_closure"] is True


def test_product_requirements_and_domain_business_policies_are_still_financial_owned():
    m = _json(".uaos/MANIFEST.json")
    adapter = _json(".uaos/ADAPTER.json")
    ownership = _json("config/rule_ownership.json")
    product = (ROOT / "docs/product_requirements.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    assert m["domain_authority"]["product_requirements"] == "docs/product_requirements.md"
    assert m["domain_authority"]["proactive_resolution_guard"] == "financial_writing_agent/proactive_resolution.py"
    assert m["binding"]["common_behavior_assurance_ref"].endswith("docs/PRODUCT-READINESS-GATE.md")
    assert m["domain_authority"]["root_scope_receipt"].endswith("RootScopeReceipt")
    assert adapter["domain_product_requirement_authority"].endswith("docs/product_requirements.md")
    assert "product" in ownership and "cognition" in ownership
    for phrase in (
        "Product outcome", "Primary user journeys", "Functional requirement map",
        "Failure and recovery semantics", "Cognition inheritance contract",
        "Evolution inheritance contract", "Explicit non-goals", "Product completion criteria",
        "Acceptance evidence",
    ):
        assert phrase in product
    assert "Hosted cognition architecture" in architecture
    assert "Governed evolution architecture" in architecture
    assert "Product architecture review" in architecture
    assert "CAOS child integration boundary" in architecture


def test_financial_maintenance_uses_caos_method_and_all_packaged_mirrors_match():
    root = (ROOT / "references/maintenance.md").read_text(encoding="utf-8")
    packaged = (ROOT / "financial_writing_agent/resources/references/maintenance.md").read_text(encoding="utf-8")
    skill_ref = (ROOT / "skills/financial-writing-agent/references/maintenance.md").read_text(encoding="utf-8")
    assert root == packaged == skill_ref
    assert "Revision: `2.0-CAOS`" in root
    assert "cognition-agent-os" in root
    assert "competing" in root.lower() or "Compare" in root
    assert "must not" in root.lower()
    assert "record_proactive_resolution_state" in root
    assert "require_user_escalation_admission" in root
    assert "Financial" in root and "CAOS" in root
    assert "Common/cross-domain discoveries" in root
    assert "independent" in root.lower()


def test_caos_skill_direct_financial_activation_and_no_parent_business_proxy():
    skill = (ROOT / "CAOS_SKILL.md").read_text(encoding="utf-8")
    execution = _json("config/EXECUTION_CONTRACT.json")
    assert "direct Financial activation" in skill
    assert "caos_bridge.admit_parent_article_action" in skill
    assert "current_admission.apply_task_requirement_change" in skill
    assert "read" in skill.lower() and "independent" in skill.lower()
    assert execution["execution"]["direct_domain_activation"] is True
    assert execution["execution"]["live_parent_business_proxy_required"] is False
    assert execution["identity"]["parent_child_id_equality_required"] is False
