from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def version_at_least(actual: str, minimum: str) -> bool:
    def parts(value: str) -> tuple[int, ...]:
        return tuple(int(item) for item in value.split("."))

    return parts(actual) >= parts(minimum)


def main() -> None:
    manifest = load(".uaos/MANIFEST.json")
    adapter = load(".uaos/ADAPTER.json")
    caps = load(".uaos/CAPABILITIES.json")
    execution = load("config/EXECUTION_CONTRACT.json")

    assert manifest["status"] == "UAOS_CONTROL_PLANE_ACTIVE"
    binding = manifest["binding"]
    assert binding["controller_ref"] == "D1traverser-debug/universal-agent-os@main:CURRENT_SYSTEM.json"
    assert binding["common_capabilities_ref"] == "D1traverser-debug/universal-agent-os@main:config/COMMON_CAPABILITIES.json"
    assert binding["common_behavior_assurance_ref"] == "D1traverser-debug/universal-agent-os@main:config/COMMON_BEHAVIOR_ASSURANCE.json"
    assert version_at_least(binding["common_behavior_assurance_min"], "1.3.0")
    assert binding["deliberation_policy_ref"] == "D1traverser-debug/universal-agent-os@main:config/DELIBERATION_POLICY.json"
    assert binding["adapter_ref"] == ".uaos/ADAPTER.json"
    assert binding["capability_ref"] == ".uaos/CAPABILITIES.json"

    domain_authority = manifest["domain_authority"]
    assert domain_authority["product_requirements"] == "docs/product_requirements.md"
    assert domain_authority["architecture"] == "docs/architecture.md"
    assert domain_authority["business_contract"] == "financial_writing_agent/models.py:TaskContract"
    assert domain_authority["article_identity"] == "workspaces/articles/{task_id}/STATE.json::task_id"
    assert domain_authority["proactive_resolution_guard"] == "financial_writing_agent/proactive_resolution.py"
    assert domain_authority["root_scope_receipt"].endswith("RootScopeReceipt")
    assert domain_authority["problem_action_admission"].endswith("finalize_problem_action")
    assert domain_authority["canonical_evolution_evidence"] == "evals/EVOLUTION_INDEX.json"

    assert adapter["session_activation"] == "DIRECT_FINANCIAL_WORK_PLANE_AFTER_DOMAIN_SELECTION__NO_MANDATORY_LIVE_UAOS_BUSINESS_PROXY"
    assert adapter["controller_task_identity_authority"] == "UAOS"
    assert adapter["domain_article_identity_authority"] == "workspaces/articles/{task_id}/STATE.json::task_id"
    assert "NO_EQUALITY_REQUIREMENT" in adapter["identity_boundary"]
    assert adapter["business_state_authority"] == "workspaces/articles/{task_id}/STATE.json"
    assert adapter["common_or_cross_domain_evolution_authority"] == "UAOS"

    assert execution["product_path"] == "DIRECT_FINANCIAL_WORK_PLANE_WITH_UAOS_HOSTED_COMMON_GOVERNANCE"
    assert execution["authority"]["business_state_root"] == "workspaces/articles/{task_id}"
    assert execution["identity"]["article_id_owner"] == "FINANCIAL_WRITING"
    assert execution["identity"]["business_contract_is_identity_free"] is True
    assert execution["identity"]["parent_child_id_equality_required"] is False
    assert execution["task_contract"]["identity_free"] is True
    assert execution["execution"]["direct_domain_activation"] is True
    assert execution["execution"]["live_parent_business_proxy_required"] is False
    assert execution["execution"]["free_form_article_fallback_allowed"] is False

    required = set(caps["required_uaos_common_capabilities"])
    assert caps["profile_version"] >= 19
    assert version_at_least(caps["uaos_common_capabilities_contract_min"], "1.6.0")
    assert version_at_least(caps["uaos_common_behavior_assurance_contract_min"], "1.3.0")
    assert caps["canonical_evolution_evidence_ref"] == "evals/EVOLUTION_INDEX.json"
    assert {
        "intent_and_requirement_governance",
        "product_requirements_and_architecture_governance",
        "domain_internal_work_orchestration",
        "cross_chat_continuity_and_recovery",
        "hierarchical_authority_governance",
        "mutation_sentinel_and_host_complete_mediation",
        "adaptive_deliberation_and_parent_guidance",
        "governed_self_evolution",
    }.issubset(required)
    assert caps["uaos_deliberation_policy_ref"].endswith("config/DELIBERATION_POLICY.json")
    cognition = caps["hosted_cognition_semantics"]
    assert cognition == {
        "source": "CURRENT_UAOS_DELIBERATION_POLICY",
        "local_overrides": "NONE",
    }
    assert "problem_response_floor" not in cognition
    assert "problem_response_rule" not in cognition
    assert caps["hosted_behavior_semantics"]["recover_before_user_escalation"] == "OWNER_NATIVE_EXECUTABLE_RECEIPT_AND_ESCALATION_ADMISSION"
    assert "ROOT_HYPOTHESIS_SUPPORT" in caps["hosted_behavior_semantics"]["root_scope_action_grounding"]
    assert "RECOMMENDATION_ONLY_NOT_TERMINAL" in caps["hosted_behavior_semantics"]["problem_to_action_closure"]
    hosted = execution["hosted_governance"]
    assert hosted["problem_cognition_owner"] == "CURRENT_UAOS_DELIBERATION_POLICY"
    assert hosted["problem_cognition_inheritance"] == "POINTER_ONLY__NO_COPIED_PARENT_ALGORITHM"
    assert hosted["financial_business_research_is_separate_from_generic_problem_cognition"] is True
    problem = execution["problem_and_evolution"]
    assert problem["generic_problem_cognition_owner"] == "CURRENT_UAOS_DELIBERATION_POLICY"
    assert problem["generic_problem_cognition_is_copied_locally"] is False
    assert problem["financial_material_judgment_may_require_stricter_domain_evidence"] is True
    assert problem["one_off_observation_auto_promotes_to_global_rule"] is False
    assert problem["systemic_change_requires_regression_or_eval_evidence"] is True

    capability_map = {cap["capability_id"]: cap for cap in caps["capabilities"]}
    assert "domain_owned_article_identity_and_state" in capability_map
    assert "identity_free_business_output_contract" in capability_map
    assert "problem_cognition_root_scope_admission" in capability_map
    assert "problem_action_closure_admission" in capability_map
    assert "proactive_resolution_admission" in capability_map
    assert "domain_product_requirements_traceability" in capability_map
    assert "UAOS:domain_internal_work_orchestration" in capability_map["high_judgment_generation_stages"]["required"]
    assert "uaos_article_binding_validation" not in capability_map
    assert all(cap.get("side_channel_allowed") is False for cap in caps["capabilities"])

    assert (ROOT / "financial_writing_agent/proactive_resolution.py").is_file()
    assert (ROOT / "financial_writing_agent/problem_action_admission.py").is_file()
    assert (ROOT / "financial_writing_agent/current_admission.py").is_file()
    assert (ROOT / "financial_writing_agent/writing_kernel.py").is_file()
    assert (ROOT / "tests/test_problem_action_admission_v1.py").is_file()
    assert (ROOT / "tests/test_executable_proactive_resolution_20261015.py").is_file()
    assert (ROOT / "evals/EVOLUTION_INDEX.json").is_file()
    assert (ROOT / "docs/product_requirements.md").is_file()
    assert (ROOT / "docs/architecture.md").is_file()
    assert not (ROOT / "financial_writing_agent/uaos_binding.py").exists()
    assert not (ROOT / "continuity").exists()

    print(
        "PASS: Financial owns article/product authority, binds capability profile >=19 to UAOS common capabilities >=1.6 and behavior >=1.3, "
        "inherits current UAOS cognition by pointer only, and verifies owner-native root-scope/action closure admission"
    )


if __name__ == "__main__":
    main()
