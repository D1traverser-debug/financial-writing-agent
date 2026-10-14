from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


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
        "financial_writing_agent/workflow_spec.py", "financial_writing_agent/models.py",
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
    require(manifest["binding"]["deliberation_policy_ref"].endswith("config/DELIBERATION_POLICY.json"), "deliberation binding drift")
    require(manifest["domain_authority"]["product_requirements"] == "docs/product_requirements.md", "domain product-requirement authority drift")
    require(manifest["domain_authority"]["architecture"] == "docs/architecture.md", "domain architecture authority drift")
    require(manifest["domain_authority"]["article_identity"] == "workspaces/articles/{task_id}/STATE.json::task_id", "manifest article identity drift")
    require(manifest["domain_authority"]["business_contract"] == "financial_writing_agent/models.py:TaskContract", "business contract drift")

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
    require(execution["problem_and_evolution"]["every_problem_requires_external_research_and_reflection"] is True, "problem research/reflection floor weakened")
    require(execution["problem_and_evolution"]["one_off_observation_auto_promotes_to_global_rule"] is False, "one-off evidence can auto-promote")
    require(execution["problem_and_evolution"]["systemic_change_requires_regression_or_eval_evidence"] is True, "systemic evolution lost regression/eval gate")

    required_common = set(caps.get("required_uaos_common_capabilities", []))
    require(caps["profile_version"] == 16, "Financial capability profile drift")
    require(caps["uaos_common_capabilities_contract_min"] == "1.5.0", "Financial minimum common contract drift")
    require({
        "product_requirements_and_architecture_governance",
        "mutation_sentinel_and_host_complete_mediation",
        "adaptive_deliberation_and_parent_guidance",
        "governed_self_evolution",
    }.issubset(required_common), "required cognition/evolution/product common capabilities missing")
    require(caps["hosted_cognition_semantics"]["problem_response_floor"] == [
        "MICRO_DIAGNOSIS",
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT",
        "GOVERNING_ASSUMPTION_CHALLENGE",
        "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH",
    ], "hosted cognition problem-response floor drift")
    require(all(cap.get("side_channel_allowed") is False for cap in caps["capabilities"]), "side channel enabled")

    current_skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    discovery = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    product_requirements = (ROOT / "docs/product_requirements.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    require("continuity/" not in current_skill, "current Skill references retired namespace")
    require("no equality requirement" in current_skill.lower(), "current Skill does not state the identity boundary")
    require("TaskContract` is intentionally identity-free" in current_skill, "Skill does not separate article identity from business contract")
    require("A fresh chat may select Financial Writing directly" in current_skill, "Skill lost direct Financial activation")
    require("Mandatory problem response" in current_skill, "Skill lost hosted cognition problem response")
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

    reference_names = ("research.md","knowledge.md","market_explanation.md","audit.md","editorial.md","hooks.md","style.md","platforms.md","delivery.md","maintenance.md")
    for name in reference_names:
        source = (ROOT / "references" / name).read_bytes()
        skill = (ROOT / "skills/financial-writing-agent/references" / name).read_bytes()
        package = (ROOT / "financial_writing_agent/resources/references" / name).read_bytes()
        require(source == skill == package, f"reference mirror drift: {name}")

    print("PASS: Financial keeps one business owner, directly activates, inherits current UAOS cognition/evolution, and owns its product requirements")


if __name__ == "__main__":
    main()
