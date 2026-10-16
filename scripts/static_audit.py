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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    require(not (ROOT / "continuity").exists(), "retired continuity namespace returned")
    for path in (
        "UAOS_SKILL.md", ".uaos/MANIFEST.json", ".uaos/ADAPTER.json",
        ".uaos/CAPABILITIES.json", "config/EXECUTION_CONTRACT.json",
        "docs/product_requirements.md", "docs/architecture.md",
        "financial_writing_agent/owner_guard.py", "financial_writing_agent/owner_lifecycle.py",
        "financial_writing_agent/proactive_resolution.py",
        "financial_writing_agent/problem_action_admission.py",
        "financial_writing_agent/workflow_spec.py", "financial_writing_agent/models.py",
        "evals/EVOLUTION_INDEX.json",
    ):
        require((ROOT / path).is_file(), f"missing current Financial authority: {path}")

    require(not (ROOT / "financial_writing_agent/uaos_binding.py").exists(), "parent identity validator leaked into Financial business package")
    require(not (ROOT / "tests/test_uaos_article_binding.py").exists(), "retired parent/child ID-equality regression test remains")
    require(not (ROOT / "state").exists(), "second parent/controller state plane returned inside Financial repository")

    manifest = load(".uaos/MANIFEST.json")
    adapter = load(".uaos/ADAPTER.json")
    caps = load(".uaos/CAPABILITIES.json")
    execution = load("config/EXECUTION_CONTRACT.json")

    require(manifest["controller"] == "D1traverser-debug/universal-agent-os@main", "controller drift")
    require(manifest["skill"]["entrypoint"] == "UAOS_SKILL.md", "skill drift")
    require(manifest["binding"]["common_capabilities_ref"].endswith("config/COMMON_CAPABILITIES.json"), "common capability binding drift")
    require(manifest["binding"]["common_behavior_assurance_ref"].endswith("config/COMMON_BEHAVIOR_ASSURANCE.json"), "common behavior-assurance binding drift")
    require(version_at_least(manifest["binding"]["common_behavior_assurance_min"], "1.3.0"), "common behavior-assurance minimum drift")
    require(manifest["binding"]["deliberation_policy_ref"].endswith("config/DELIBERATION_POLICY.json"), "deliberation binding drift")
    require(manifest["domain_authority"]["product_requirements"] == "docs/product_requirements.md", "domain product-requirement authority drift")
    require(manifest["domain_authority"]["architecture"] == "docs/architecture.md", "domain architecture authority drift")
    require(manifest["domain_authority"]["article_identity"] == "workspaces/articles/{task_id}/STATE.json::task_id", "manifest article identity drift")
    require(manifest["domain_authority"]["business_contract"] == "financial_writing_agent/models.py:TaskContract", "business contract drift")
    require(manifest["domain_authority"]["proactive_resolution_guard"] == "financial_writing_agent/proactive_resolution.py", "proactive-resolution guard drift")
    require(manifest["domain_authority"]["root_scope_receipt"].endswith("RootScopeReceipt"), "root-scope authority drift")
    require(manifest["domain_authority"]["problem_action_admission"].endswith("finalize_problem_action"), "problem-action admission drift")
    require(manifest["domain_authority"]["canonical_evolution_evidence"] == "evals/EVOLUTION_INDEX.json", "canonical evolution evidence drift")

    require(adapter["session_activation"] == "DIRECT_FINANCIAL_WORK_PLANE_AFTER_DOMAIN_SELECTION__NO_MANDATORY_LIVE_UAOS_BUSINESS_PROXY", "direct Financial activation drift")
    require(adapter["controller_task_identity_authority"] == "UAOS", "controller identity authority drift")
    require(adapter["domain_article_identity_authority"] == "workspaces/articles/{task_id}/STATE.json::task_id", "Financial article identity authority drift")
    require("NO_EQUALITY_REQUIREMENT" in adapter["identity_boundary"], "parent/domain identity namespaces collapsed")
    require(adapter["common_or_cross_domain_evolution_authority"] == "UAOS", "common/cross-domain evolution ownership drift")
    require(adapter["legacy_controller_compatibility"] == "NONE", "legacy controller compatibility returned")

    require(execution["product_path"] == "DIRECT_FINANCIAL_WORK_PLANE_WITH_UAOS_HOSTED_COMMON_GOVERNANCE", "Financial product path drift")
    require(execution["execution"]["route_selection"] == "NONE", "route selector returned")
    require(execution["execution"]["direct_domain_activation"] is True, "direct domain activation disabled")
    require(execution["execution"]["live_parent_business_proxy_required"] is False, "live parent business proxy became mandatory")
    require(execution["authority"]["alternate_business_state_authority_allowed"] is False, "alternate state authority enabled")
    require(execution["identity"]["article_id_owner"] == "FINANCIAL_WRITING", "Financial identity ownership drift")
    require(execution["identity"]["business_contract_is_identity_free"] is True, "TaskContract regained identity ownership")
    require(execution["identity"]["parent_child_id_equality_required"] is False, "parent/child ID equality returned")
    hosted = execution["hosted_governance"]
    require(hosted["problem_cognition_owner"] == "CURRENT_UAOS_DELIBERATION_POLICY", "generic problem cognition owner drift")
    require(hosted["problem_cognition_inheritance"] == "POINTER_ONLY__NO_COPIED_PARENT_ALGORITHM", "parent cognition algorithm copied into Financial contract")
    require(hosted["financial_business_research_is_separate_from_generic_problem_cognition"] is True, "Financial business research collapsed into parent cognition")
    problem = execution["problem_and_evolution"]
    require(problem["generic_problem_cognition_owner"] == "CURRENT_UAOS_DELIBERATION_POLICY", "problem/evolution cognition owner drift")
    require(problem["generic_problem_cognition_is_copied_locally"] is False, "problem/evolution copied parent cognition locally")
    require(problem["financial_material_judgment_may_require_stricter_domain_evidence"] is True, "Financial material evidence floor weakened")
    require(problem["one_off_observation_auto_promotes_to_global_rule"] is False, "one-off evidence can auto-promote")
    require(problem["systemic_change_requires_regression_or_eval_evidence"] is True, "systemic evolution lost regression/eval gate")

    required_common = set(caps.get("required_uaos_common_capabilities", []))
    require(caps["profile_version"] >= 19, "Financial capability profile below Common Behavior 1.3 floor")
    require(version_at_least(caps["uaos_common_capabilities_contract_min"], "1.6.0"), "Financial minimum common capability contract below required floor")
    require(version_at_least(caps["uaos_common_behavior_assurance_contract_min"], "1.3.0"), "Financial minimum common behavior contract below required floor")
    require(caps["canonical_evolution_evidence_ref"] == "evals/EVOLUTION_INDEX.json", "Financial evolution entrypoint drift")
    require({
        "product_requirements_and_architecture_governance",
        "domain_internal_work_orchestration",
        "mutation_sentinel_and_host_complete_mediation",
        "adaptive_deliberation_and_parent_guidance",
        "governed_self_evolution",
    }.issubset(required_common), "required cognition/evolution/product/orchestration common capabilities missing")
    require(caps["uaos_deliberation_policy_ref"].endswith("config/DELIBERATION_POLICY.json"), "Financial deliberation pointer drift")
    cognition = caps["hosted_cognition_semantics"]
    require(cognition == {
        "source": "CURRENT_UAOS_DELIBERATION_POLICY",
        "local_overrides": "NONE",
    }, "hosted cognition pointer drift")
    require("problem_response_floor" not in cognition and "problem_response_rule" not in cognition, "copied parent cognition semantics returned")
    require(caps["hosted_behavior_semantics"]["recover_before_user_escalation"] == "OWNER_NATIVE_EXECUTABLE_RECEIPT_AND_ESCALATION_ADMISSION", "proactive resolution remained declaration-only")
    require("ROOT_HYPOTHESIS_SUPPORT" in caps["hosted_behavior_semantics"]["root_scope_action_grounding"], "root-scope action evidence grounding missing")
    require("RECOMMENDATION_ONLY_NOT_TERMINAL" in caps["hosted_behavior_semantics"]["problem_to_action_closure"], "problem-to-action closure missing")
    capability_map = {cap["capability_id"]: cap for cap in caps["capabilities"]}
    require("problem_cognition_root_scope_admission" in capability_map, "problem cognition/root-scope capability missing")
    require("problem_action_closure_admission" in capability_map, "problem action closure capability missing")
    require("proactive_resolution_admission" in capability_map, "proactive resolution capability missing")
    require("behavioral_trajectory_regression" in capability_map["proactive_resolution_admission"]["required"], "proactive resolution lacks trajectory evidence requirement")
    require("UAOS:domain_internal_work_orchestration" in capability_map["high_judgment_generation_stages"]["required"], "writing kernel orchestration dependency missing")
    require(all(cap.get("side_channel_allowed") is False for cap in caps["capabilities"]), "side channel enabled")

    current_skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    discovery = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    product_requirements = (ROOT / "docs/product_requirements.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    current_skill_lower = current_skill.lower()
    require("continuity/" not in current_skill, "current Skill references retired namespace")
    require("no equality requirement" in current_skill_lower, "current Skill does not state the identity boundary")
    require("TaskContract` is intentionally identity-free" in current_skill, "Skill does not separate article identity from business contract")
    require("a fresh chat may select financial writing directly" in current_skill_lower, "Skill lost direct Financial activation")
    require("mandatory problem response" in current_skill_lower, "Skill lost hosted cognition problem response")
    require("executable proactive resolution" in current_skill_lower, "Skill does not expose executable proactive resolution")
    require("Product completion criteria" in product_requirements, "product requirements lack completion criteria")
    require("Acceptance evidence" in product_requirements, "product requirements are not linked to acceptance evidence")
    require("Hosted cognition architecture" in architecture, "architecture lacks hosted cognition boundary")
    require("Governed evolution architecture" in architecture, "architecture lacks governed evolution boundary")
    require("Discovery Pointer" in discovery and "continuity/" not in discovery, "discovery Skill is not a clean pointer")

    models_text = (ROOT / "financial_writing_agent/models.py").read_text(encoding="utf-8")
    require("task_id:" not in models_text, "TaskContract still carries a duplicate article identity")

    business_package_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "financial_writing_agent").glob("*.py")
    )
    require("UAOS_ARTICLE_TASK_ID" not in business_package_text, "parent identity semantics leaked into Financial package")
    require("validate_uaos_article_binding" not in business_package_text, "UAOS binding validator leaked into Financial package")
    require("DeliberationController" not in business_package_text, "second cognition controller leaked into Financial package")
    require("EvolutionController" not in business_package_text, "second evolution controller leaked into Financial package")
    require("require_user_escalation_admission" in business_package_text, "executable user-escalation admission missing from Financial package")

    reference_names = ("research.md","knowledge.md","market_explanation.md","audit.md","editorial.md","hooks.md","style.md","platforms.md","delivery.md","maintenance.md")
    for name in reference_names:
        source = (ROOT / "references" / name).read_bytes()
        skill = (ROOT / "skills/financial-writing-agent/references" / name).read_bytes()
        package = (ROOT / "financial_writing_agent/resources/references" / name).read_bytes()
        require(source == skill == package, f"reference mirror drift: {name}")

    print("PASS: Financial keeps one business owner, directly activates, binds capability profile >=19 to UAOS common capabilities >=1.6 and behavior >=1.3, inherits current UAOS cognition by pointer only, and operationalizes owner-native root-scope/action admission")


if __name__ == "__main__":
    main()
