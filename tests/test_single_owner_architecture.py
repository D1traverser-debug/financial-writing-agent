import json
import tomllib
from pathlib import Path

from financial_writing_agent.current_admission import build_initial_state
from financial_writing_agent.models import TaskContract

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_current_authority_has_one_financial_owner_path():
    manifest = _json(".uaos/MANIFEST.json")
    adapter = _json(".uaos/ADAPTER.json")
    capabilities = _json(".uaos/CAPABILITIES.json")
    execution = _json("config/EXECUTION_CONTRACT.json")

    parent = "D1traverser-debug/cognition-agent-os@main"
    assert manifest["controller"] == adapter["controller"] == execution["authority"]["controller"] == parent
    assert manifest["skill"]["entrypoint"] == "CAOS_SKILL.md"
    assert manifest["binding"]["adapter_ref"] == ".uaos/ADAPTER.json"
    assert manifest["binding"]["capability_ref"] == ".uaos/CAPABILITIES.json"
    assert manifest["binding"]["controller_ref"] == parent + ":src/cognition_agent_os/domain_contract.py"
    assert manifest["domain_authority"]["product_requirements"] == "docs/product_requirements.md"
    assert manifest["domain_authority"]["architecture"] == "docs/architecture.md"
    assert manifest["domain_authority"]["business_contract"] == "financial_writing_agent/models.py:TaskContract"
    assert manifest["domain_authority"]["article_identity"] == "workspaces/articles/{task_id}/STATE.json::task_id"
    assert manifest["domain_authority"]["current_admission_guard"] == "financial_writing_agent/current_admission.py"
    assert manifest["domain_authority"]["historical_resume_compatibility_guard"] == "financial_writing_agent/resume_compatibility.py"

    assert adapter["controller_task_identity_authority"].startswith("CAOS")
    assert adapter["domain_article_identity_authority"] == "workspaces/articles/{task_id}/STATE.json::task_id"
    assert adapter["session_activation"].startswith("OPT_IN_CAOS_PARENT_INTERACTIVE")
    assert "NO_EQUALITY_REQUIREMENT" in adapter["identity_boundary"]
    assert adapter["business_state_authority"] == "workspaces/articles/{task_id}/STATE.json"
    assert adapter["domain_product_requirement_authority"].endswith("docs/product_requirements.md")
    assert adapter["common_or_cross_domain_evolution_authority"] == "CAOS"
    assert adapter["historical_material_resume_guard"] == "financial_writing_agent/resume_compatibility.py"
    assert adapter["legacy_controller_compatibility"] == "DECOMMISSIONED_OLD_PARENT__COMPATIBLE_DOT_UAOS_FILENAMES_ONLY"

    assert execution["product_path"] == "CAOS_OPT_IN_PARENT_METHOD__DIRECT_FINANCIAL_BUSINESS_OWNER"
    assert execution["execution"]["route_selection"] == "OPT_IN_CAOS_PARENT_OR_DIRECT_FINANCIAL"
    assert execution["execution"]["direct_domain_activation"] is True
    assert execution["execution"]["live_parent_business_proxy_required"] is False
    assert execution["authority"]["alternate_business_state_authority_allowed"] is False
    assert execution["identity"]["article_id_owner"] == "FINANCIAL_WRITING"
    assert execution["identity"]["business_contract_is_identity_free"] is True
    assert execution["identity"]["parent_child_id_equality_required"] is False
    assert execution["hosted_governance"]["parent_read_only_observation"] is True
    assert execution["hosted_governance"]["parent_host_or_plugin_assumed_connected"] is False

    required = set(capabilities["required_caos_parent_responsibilities"])
    assert capabilities["profile_version"] >= 22
    assert {
        "original_goal_and_correction_fidelity", "permission_and_effect_separation",
        "independent_child_business_outcome_readback", "failure_driven_replan_and_sourced_learning",
    }.issubset(required)
    ids = {cap["capability_id"] for cap in capabilities["capabilities"]}
    assert {
        "financial_owner_workflow", "domain_owned_article_identity_and_state",
        "post_evolution_resume_compatibility", "identity_free_business_output_contract",
        "high_judgment_generation_stages", "selective_deep_publication_architecture",
        "event_to_company_causal_grounding", "semantic_review_stages",
        "delivery_and_mechanical_qa", "problem_cognition_root_scope_admission",
        "blocked_recovery_and_system_impact_lifecycle", "proactive_resolution_admission",
        "quality_regression_promotion_gate", "domain_product_requirements_traceability",
    }.issubset(ids)
    assert "uaos_article_binding_validation" not in ids
    assert "D1traverser-debug/universal-agent-os" not in json.dumps(manifest)
    assert "D1traverser-debug/universal-agent-os" not in json.dumps(adapter)
    assert "D1traverser-debug/universal-agent-os" not in json.dumps(capabilities)


def test_financial_state_is_article_identity_and_task_contract_is_identity_free():
    contract = TaskContract(prompt="one")
    assert not hasattr(contract, "task_id")
    state = build_initial_state(
        task_id="financial-owned-id",
        prompt="one",
        source_refs=[],
        executor_identity="chat-session:test",
    )
    assert state["task_id"] == "financial-owned-id"
    assert state["writing_kernel_version"] == "1.0"
    assert state["task_requirement_contract_version"] == "1.0"
    assert state["execution_receipts"][0]["task_id"] == "financial-owned-id"
    assert state["execution_receipts"][0]["output_refs"] == ["workspaces/articles/financial-owned-id/STATE.json"]
    assert not (ROOT / "financial_writing_agent/uaos_binding.py").exists()
    assert not (ROOT / "tests/test_uaos_article_binding.py").exists()
    assert not (ROOT / "state").exists()


def test_retired_control_namespace_is_physically_absent():
    assert not (ROOT / "continuity").exists()
    for path in (
        "financial_writing_agent/github_chat_guard.py",
        "plugin.json",
        "scripts/sdk_smoke.py",
        "scripts/mcp_smoke.py",
        "financial_writing_agent/uaos_binding.py",
        "tests/test_uaos_article_binding.py",
    ):
        assert not (ROOT / path).exists(), path
    for path in (
        "CAOS_SKILL.md",
        "UAOS_SKILL.md",
        "financial_writing_agent/caos_bridge.py",
        ".uaos/MANIFEST.json",
        ".uaos/ADAPTER.json",
        ".uaos/CAPABILITIES.json",
        "config/EXECUTION_CONTRACT.json",
        "docs/product_requirements.md",
        "docs/architecture.md",
        "financial_writing_agent/owner_guard.py",
        "financial_writing_agent/current_admission.py",
        "financial_writing_agent/owner_lifecycle.py",
        "financial_writing_agent/proactive_resolution.py",
        "financial_writing_agent/resume_compatibility.py",
        "financial_writing_agent/models.py",
    ):
        assert (ROOT / path).is_file(), path


def test_discovery_skill_is_pointer_not_second_rulebook():
    discovery = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    assert "Discovery Pointer" in discovery
    assert "CAOS_SKILL.md" in discovery
    assert len(discovery.encode("utf-8")) < 4096
    assert "continuity/" not in discovery


def test_package_has_no_second_runtime_dependencies_or_parent_identity_logic():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["version"] == "1.0.3"
    assert "scripts" not in pyproject["project"]
    assert not any(str(dep).lower().startswith("mcp") for dep in pyproject["project"].get("dependencies", []))
    assert "openai" not in pyproject["project"].get("optional-dependencies", {})
    business_package_text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "financial_writing_agent").glob("*.py"))
    assert "UAOS_ARTICLE_TASK_ID" not in business_package_text
    assert "validate_uaos_article_binding" not in business_package_text
    assert "DeliberationController" not in business_package_text
    assert "EvolutionController" not in business_package_text
