"""One Financial business owner, one article state, no mandatory parent runtime."""
import json
import tomllib
from pathlib import Path

from financial_writing_agent.current_admission import build_initial_state
from financial_writing_agent.models import TaskContract
from financial_writing_agent.standalone_runtime import DOMAIN_ID, OPERATIONS

ROOT = Path(__file__).resolve().parents[1]


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_current_authority_has_one_financial_owner_path():
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    caps = _json("config/FINANCIAL_CAPABILITIES.json")
    execution = _json("config/EXECUTION_CONTRACT.json")
    assert DOMAIN_ID == manifest["domain_id"] == caps["domain_id"] == execution["domain_id"]
    assert manifest["controller"] == caps["owner"] == execution["authority"]["controller"] == "FINANCIAL_WRITING_OWNER"
    assert manifest["skill_entrypoint"] == caps["entrypoint"] == "skills/financial-writing-agent/SKILL.md"
    assert manifest["external_parent_required"] is False
    assert manifest["external_host_required"] is False
    assert manifest["state_authority"] == "workspaces/articles/{task_id}/STATE.json"
    assert manifest["provider_adapter"] == "financial_writing_agent.standalone_runtime"
    native = manifest["chatgpt_native_runtime"]
    assert native["orchestrator"] == "CHATGPT_MODEL_WITH_FINANCIAL_SKILL"
    assert native["persistence_provider"] == "CONNECTED_USER_GITHUB_CONNECTOR"
    assert native["write_protocol"] == "GIT_BLOB_TREE_COMMIT_UPDATE_REF_EXPECTED_SHA__OWNER_STATE_OR_METHOD_CATALOG_AND_SIGNED_EFFECT_RECEIPT_ATOMIC_BUNDLE"
    assert native["requires_hosted_python_mcp"] is False
    assert execution["execution"]["route_selection"] == "DIRECT_FINANCIAL_ONLY"
    assert execution["execution"]["live_parent_business_proxy_required"] is False
    assert execution["authority"]["alternate_business_state_authority_allowed"] is False
    assert execution["identity"]["article_id_owner"] == "FINANCIAL_WRITING"
    assert execution["identity"]["business_contract_is_identity_free"] is True
    assert execution["standalone_governance"]["external_parent_required"] is False
    assert {"CREATE_ARTICLE", "CHANGE_REQUIREMENTS", "ADVANCE_STAGE", "ATTACH_FEEDBACK"} <= OPERATIONS
    assert len({c["id"] for c in caps["capabilities"]}) == len(caps["capabilities"])
    data = _json("config/DATA_AUTHORITY.json")
    assert data["business_authority"] == "github://D1traverser-debug/financial-writing-agent@main"
    assert data["no_parallel_article_ledger"] is True
    assert data["no_external_parent_runtime"] is True


def test_financial_state_is_article_identity_and_task_contract_identity_free():
    contract = TaskContract(prompt="one")
    assert not hasattr(contract, "task_id")
    state = build_initial_state(
        task_id="financial-owned-id", prompt="one", source_refs=[], executor_identity="test",
    )
    assert state["task_id"] == "financial-owned-id"
    assert state["writing_kernel_version"] == "1.0"
    assert state["task_requirement_contract_version"] == "1.0"
    assert state["execution_receipts"][0]["task_id"] == "financial-owned-id"
    assert state["execution_receipts"][0]["output_refs"] == [
        "workspaces/articles/financial-owned-id/STATE.json",
    ]


def test_retired_parent_paths_are_historical_and_current_entry_is_financial():
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    assert (ROOT / manifest["skill_entrypoint"]).exists()
    assert (ROOT / "financial_writing_agent/standalone_runtime.py").exists()
    for name in ("FINANCIAL_SKILL.md", "CAOS_SKILL.md", "UAOS_SKILL.md", ".uaos", "docs/CAOS_CHILD_INTERFACE.md"):
        assert not (ROOT / name).exists()
    for path in ("continuity", "state", "TASK_INDEX.json", "references"):
        assert not (ROOT / path).exists()


def test_discovery_skill_is_real_operating_entry_not_second_parent_pointer():
    skill = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    assert "Independent Operating Skill" in skill
    assert "standalone_runtime.py" in skill
    for marker in ("create_blob", "create_tree", "create_commit", "update_ref", "expected_sha", "fetch_file"):
        assert marker in skill
    assert "Decision" in skill and "Execution" in skill
    assert "PrivateResearchBrief" in skill
    assert "continuity/" not in skill


def test_installed_package_has_no_caos_required_dependencies():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["version"] == "1.1.0"
    assert "scripts" not in project["project"]
    deps = project["project"].get("dependencies", [])
    assert not any("caos" in d.lower() or "uaos" in d.lower() for d in deps)
    assert not any(d.lower().startswith("mcp") for d in deps)
    modules = (ROOT / "financial_writing_agent/standalone_runtime.py").read_text(encoding="utf-8")
    assert "caos_bridge" not in modules
    assert "cognition_agent_os" not in modules



def test_standalone_interface_uses_canonical_skill_paths_and_no_hosted_claim():
    interface = (ROOT / "docs/STANDALONE_INTERFACE.md").read_text(encoding="utf-8")
    assert "canonical operating Skill source" in interface
    assert "skills/financial-writing-agent/references/maintenance.md" in interface
    assert "skills/financial-writing-agent/skills/" not in interface
