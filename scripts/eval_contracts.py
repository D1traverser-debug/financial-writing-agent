from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


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
    assert binding["deliberation_policy_ref"] == "D1traverser-debug/universal-agent-os@main:config/DELIBERATION_POLICY.json"
    assert binding["adapter_ref"] == ".uaos/ADAPTER.json"
    assert binding["capability_ref"] == ".uaos/CAPABILITIES.json"

    domain_authority = manifest["domain_authority"]
    assert domain_authority["product_requirements"] == "docs/product_requirements.md"
    assert domain_authority["architecture"] == "docs/architecture.md"
    assert domain_authority["business_contract"] == "financial_writing_agent/models.py:TaskContract"
    assert domain_authority["article_identity"] == "workspaces/articles/{task_id}/STATE.json::task_id"
    assert domain_authority["proactive_resolution_guard"] == "financial_writing_agent/proactive_resolution.py"

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
    assert caps["profile_version"] == 17
    assert caps["uaos_common_capabilities_contract_min"] == "1.6.0"
    assert caps["uaos_common_behavior_assurance_contract_min"] == "1.2.0"
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
    assert caps["hosted_cognition_semantics"]["problem_response_floor"] == [
        "MICRO_DIAGNOSIS",
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT",
        "GOVERNING_ASSUMPTION_CHALLENGE",
        "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH",
    ]
    assert caps["hosted_behavior_semantics"]["recover_before_user_escalation"] == "OWNER_NATIVE_EXECUTABLE_RECEIPT_AND_ESCALATION_ADMISSION"
    assert "RECOMMENDATION_ONLY_NOT_TERMINAL" in caps["hosted_behavior_semantics"]["problem_to_action_closure"]
    assert execution["problem_and_evolution"]["every_problem_requires_external_research_and_reflection"] is True
    assert execution["problem_and_evolution"]["one_off_observation_auto_promotes_to_global_rule"] is False
    assert execution["problem_and_evolution"]["systemic_change_requires_regression_or_eval_evidence"] is True

    capability_map = {cap["capability_id"]: cap for cap in caps["capabilities"]}
    assert "domain_owned_article_identity_and_state" in capability_map
    assert "identity_free_business_output_contract" in capability_map
    assert "proactive_resolution_admission" in capability_map
    assert "domain_product_requirements_traceability" in capability_map
    assert "UAOS:domain_internal_work_orchestration" in capability_map["high_judgment_generation_stages"]["required"]
    assert "uaos_article_binding_validation" not in capability_map
    assert all(cap.get("side_channel_allowed") is False for cap in caps["capabilities"])

    assert (ROOT / "financial_writing_agent/proactive_resolution.py").is_file()
    assert (ROOT / "financial_writing_agent/current_admission.py").is_file()
    assert (ROOT / "financial_writing_agent/writing_kernel.py").is_file()
    assert (ROOT / "tests/test_executable_proactive_resolution_20261015.py").is_file()
    assert (ROOT / "docs/product_requirements.md").is_file()
    assert (ROOT / "docs/architecture.md").is_file()
    assert not (ROOT / "financial_writing_agent/uaos_binding.py").exists()
    assert not (ROOT / "continuity").exists()

    print(
        "PASS: Financial owns article/product authority, binds UAOS common 1.6 internal orchestration, "
        "inherits current cognition/evolution/behavior contracts, and verifies owner-native admission/recovery evidence"
    )


if __name__ == "__main__":
    main()
