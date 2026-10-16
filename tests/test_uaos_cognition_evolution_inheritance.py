import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_hosted_cognition_contract_is_current_pointer_only_and_explicit():
    caps = _json(".uaos/CAPABILITIES.json")
    execution = _json("config/EXECUTION_CONTRACT.json")

    assert caps["profile_version"] >= 21
    assert caps["common_capabilities_inheritance"] == "UAOS_HOSTED"
    assert caps["uaos_common_capabilities_contract_min"] == "1.6.0"
    assert caps["uaos_common_behavior_assurance_contract_min"] == "1.3.0"
    assert "domain_internal_work_orchestration" in caps["required_uaos_common_capabilities"]
    assert caps["uaos_deliberation_policy_ref"].endswith("config/DELIBERATION_POLICY.json")
    assert caps["hosted_cognition_semantics"] == {
        "source": "CURRENT_UAOS_DELIBERATION_POLICY",
        "local_overrides": "NONE",
    }
    assert "problem_response_floor" not in caps["hosted_cognition_semantics"]
    assert caps["hosted_behavior_semantics"]["recover_before_user_escalation"] == "OWNER_NATIVE_EXECUTABLE_RECEIPT_AND_ESCALATION_ADMISSION"
    assert "ONLY_AFTER_ROOT_SCOPE_AND_EVOLUTION_ADMISSION" in caps["hosted_behavior_semantics"]["problem_to_action_closure"]
    assert "EVERY_ADMITTED_PROBLEM_GETS_EXPLICIT_EVOLUTION_DISPOSITION" in caps["hosted_behavior_semantics"]["evolution_before_action"]

    hosted = execution["hosted_governance"]
    assert hosted["deliberation_policy_ref"].endswith("config/DELIBERATION_POLICY.json")
    assert hosted["problem_cognition_owner"] == "CURRENT_UAOS_DELIBERATION_POLICY"
    assert hosted["problem_cognition_inheritance"] == "POINTER_ONLY__NO_COPIED_PARENT_ALGORITHM"
    assert "LIGHTWEIGHT_MAY_USE_CURRENT_EVIDENCE" in hosted["problem_cognition_rule"]
    assert hosted["financial_business_research_is_separate_from_generic_problem_cognition"] is True
    assert "problem_response_floor" not in hosted
    assert "problem_floor_activation" not in hosted

    evolution = execution["problem_and_evolution"]
    assert evolution["generic_problem_cognition_owner"] == "CURRENT_UAOS_DELIBERATION_POLICY"
    assert evolution["generic_problem_cognition_is_copied_locally"] is False
    assert evolution["financial_material_judgment_may_require_stricter_domain_evidence"] is True
    assert "every_problem_requires_external_research_and_reflection" not in evolution
    assert execution["cognition_and_decision"]["problem_or_architecture_change_requires_external_method_evidence"] is True


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
    assert manifest["domain_authority"]["proactive_resolution_guard"] == "financial_writing_agent/proactive_resolution.py"
    assert manifest["binding"]["common_behavior_assurance_ref"].endswith("config/COMMON_BEHAVIOR_ASSURANCE.json")
    assert manifest["binding"]["common_behavior_assurance_min"] == "1.3.0"
    assert manifest["domain_authority"]["root_scope_receipt"].endswith("RootScopeReceipt")
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


def test_financial_maintenance_inherits_risk_adaptive_parent_cognition_and_keeps_all_mirrors_equal():
    root = (ROOT / "references/maintenance.md").read_text(encoding="utf-8")
    packaged = (ROOT / "financial_writing_agent/resources/references/maintenance.md").read_text(encoding="utf-8")
    skill = (ROOT / "skills/financial-writing-agent/references/maintenance.md").read_text(encoding="utf-8")
    assert root == packaged == skill
    assert "Revision: `1.3`" in root
    assert "DELIBERATION_POLICY.json" in root
    assert "LIGHTWEIGHT" in root and "CONTRASTIVE" in root and "STRUCTURED" in root
    assert "must not copy the parent cognition algorithm" in root
    assert "Financial business research is separate from generic problem cognition" in root
    assert "record_proactive_resolution_state" in root
    assert "require_user_escalation_admission" in root
    assert "Problem-to-action closure" in root
    assert "Familiarity alone is neither a waiver nor a reason to force heavyweight research" in root
    assert "Recommendation-only is not terminal" in root
    assert "Parent upcall boundary" in root
    assert "Every defect, correction/rejection" not in root


def test_direct_activation_is_not_replaced_by_parent_business_proxy():
    skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    execution = _json("config/EXECUTION_CONTRACT.json")
    assert "A fresh chat may select Financial Writing directly" in skill
    assert "normal article turns do **not** traverse a live UAOS business proxy" in skill
    assert "Executable proactive resolution before user escalation" in skill
    assert execution["execution"]["direct_domain_activation"] is True
    assert execution["execution"]["live_parent_business_proxy_required"] is False
    assert execution["identity"]["parent_child_id_equality_required"] is False
