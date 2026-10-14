import json
import tomllib
from pathlib import Path

from financial_writing_agent.models import TaskContract
from financial_writing_agent.owner_guard import build_initial_state

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
    assert manifest["domain_authority"]["business_contract"] == "financial_writing_agent/models.py:TaskContract"
    assert manifest["domain_authority"]["article_identity"] == "workspaces/articles/{task_id}/STATE.json::task_id"
    assert adapter["controller_task_identity_authority"] == "UAOS"
    assert adapter["domain_article_identity_authority"] == "workspaces/articles/{task_id}/STATE.json::task_id"
    assert "NO_EQUALITY_REQUIREMENT" in adapter["identity_boundary"]
    assert adapter["business_state_authority"] == "workspaces/articles/{task_id}/STATE.json"
    assert adapter["legacy_controller_compatibility"] == "NONE"
    assert execution["product_path"] == "UAOS_TO_SINGLE_GITHUB_BACKED_FINANCIAL_OWNER"
    assert execution["execution"]["route_selection"] == "NONE"
    assert execution["authority"]["alternate_business_state_authority_allowed"] is False
    assert execution["identity"]["article_id_owner"] == "FINANCIAL_WRITING"
    assert execution["identity"]["business_contract_is_identity_free"] is True
    assert execution["identity"]["parent_child_id_equality_required"] is False
    assert {cap["capability_id"] for cap in capabilities["capabilities"]} >= {
        "financial_owner_workflow", "domain_owned_article_identity_and_state",
        "identity_free_business_output_contract", "high_judgment_generation_stages",
        "semantic_review_stages", "delivery_and_mechanical_qa",
        "blocked_recovery_and_system_impact_lifecycle",
    }
    assert "uaos_article_binding_validation" not in {cap["capability_id"] for cap in capabilities["capabilities"]}


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
    assert state["execution_receipts"][0]["task_id"] == "financial-owned-id"
    assert state["execution_receipts"][0]["output_refs"] == ["workspaces/articles/financial-owned-id/STATE.json"]
    assert not (ROOT / "financial_writing_agent/uaos_binding.py").exists()
    assert not (ROOT / "tests/test_uaos_article_binding.py").exists()
    assert not (ROOT / "state").exists()


def test_retired_control_namespace_is_physically_absent():
    assert not (ROOT / "continuity").exists()
    for path in (
        "financial_writing_agent/github_chat_guard.py", "plugin.json",
        "scripts/sdk_smoke.py", "scripts/mcp_smoke.py",
        "financial_writing_agent/uaos_binding.py", "tests/test_uaos_article_binding.py",
    ):
        assert not (ROOT / path).exists(), path
    for path in (
        "UAOS_SKILL.md", ".uaos/MANIFEST.json", ".uaos/ADAPTER.json",
        ".uaos/CAPABILITIES.json", "config/EXECUTION_CONTRACT.json",
        "financial_writing_agent/owner_guard.py", "financial_writing_agent/owner_lifecycle.py",
        "financial_writing_agent/models.py",
    ):
        assert (ROOT / path).is_file(), path


def test_discovery_skill_is_pointer_not_second_rulebook():
    discovery = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    assert "Discovery Pointer" in discovery
    assert "UAOS_SKILL.md" in discovery
    assert len(discovery.encode("utf-8")) < 4096
    assert "continuity/" not in discovery


def test_package_has_no_second_runtime_dependencies_or_parent_identity_logic():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "scripts" not in pyproject["project"]
    assert not any(str(dep).lower().startswith("mcp") for dep in pyproject["project"].get("dependencies", []))
    assert "openai" not in pyproject["project"].get("optional-dependencies", {})
    business_package_text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "financial_writing_agent").glob("*.py"))
    assert "UAOS_ARTICLE_TASK_ID" not in business_package_text
    assert "validate_uaos_article_binding" not in business_package_text
