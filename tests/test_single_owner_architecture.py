import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_current_authority_has_one_financial_owner_path():
    manifest = _json(".uaos/MANIFEST.json")
    adapter = _json(".uaos/ADAPTER.json")
    capabilities = _json(".uaos/CAPABILITIES.json")
    execution = _json("config/EXECUTION_CONTRACT.json")
    assert manifest["controller"] == "D1traverser-debug/universal-agent-os@main"
    assert manifest["skill"]["entrypoint"] == "UAOS_SKILL.md"
    assert manifest["binding"]["adapter_ref"] == ".uaos/ADAPTER.json"
    assert adapter["task_identity_authority"] == "UAOS"
    assert adapter["cross_chat_continuity_authority"] == "UAOS"
    assert adapter["business_state_authority"] == "workspaces/articles/{task_id}/STATE.json"
    assert adapter["article_binding_validator"] == "financial_writing_agent.uaos_binding.validate_uaos_article_binding"
    assert adapter["legacy_controller_compatibility"] == "NONE"
    assert execution["product_path"] == "UAOS_TO_SINGLE_GITHUB_BACKED_FINANCIAL_OWNER"
    assert execution["execution"]["route_selection"] == "NONE"
    assert execution["authority"]["alternate_business_state_authority_allowed"] is False
    assert execution["uaos_article_task_binding"]["identity_rule"] == "UAOS_ARTICLE_TASK_ID_EQUALS_FINANCIAL_STATE_TASK_ID"
    assert {cap["capability_id"] for cap in capabilities["capabilities"]} >= {
        "financial_owner_workflow", "uaos_article_binding_validation",
        "high_judgment_generation_stages", "semantic_review_stages",
        "delivery_and_mechanical_qa", "blocked_recovery_and_system_impact_lifecycle",
    }


def test_binding_is_a_join_not_a_second_controller_surface():
    source = (ROOT / "financial_writing_agent/uaos_binding.py").read_text(encoding="utf-8")
    assert "validate_uaos_article_binding" in source
    assert "TaskRecord" not in source
    assert "TaskIndex" not in source
    assert "sqlite" not in source.lower()
    assert "lease" not in source.lower()
    assert not (ROOT / "state").exists()


def test_retired_control_namespace_is_physically_absent():
    assert not (ROOT / "continuity").exists()
    for path in (
        "financial_writing_agent/github_chat_guard.py", "plugin.json",
        "scripts/sdk_smoke.py", "scripts/mcp_smoke.py",
    ):
        assert not (ROOT / path).exists(), path
    for path in (
        "UAOS_SKILL.md", ".uaos/MANIFEST.json", ".uaos/ADAPTER.json",
        ".uaos/CAPABILITIES.json", "config/EXECUTION_CONTRACT.json",
        "financial_writing_agent/owner_guard.py", "financial_writing_agent/owner_lifecycle.py",
        "financial_writing_agent/uaos_binding.py",
    ):
        assert (ROOT / path).is_file(), path


def test_discovery_skill_is_pointer_not_second_rulebook():
    discovery = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    assert "Discovery Pointer" in discovery
    assert "UAOS_SKILL.md" in discovery
    assert len(discovery.encode("utf-8")) < 4096
    assert "continuity/" not in discovery


def test_package_has_no_second_runtime_dependencies():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "scripts" not in pyproject["project"]
    assert not any(str(dep).lower().startswith("mcp") for dep in pyproject["project"].get("dependencies", []))
    assert "openai" not in pyproject["project"].get("optional-dependencies", {})
