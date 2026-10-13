import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_current_authority_has_one_financial_owner_path():
    agent = _json("continuity/AGENT_MANIFEST.json")
    execution = _json("continuity/FINANCIAL_OWNER_EXECUTION.json")
    capabilities = _json("continuity/EXECUTION_CAPABILITIES.json")
    universal = _json("continuity/UNIVERSAL_PROTOCOL_ADAPTER.json")
    task = _json("continuity/tasks/financial-writing-main/TASK_MANIFEST.json")

    assert agent["product_interface"]["entry_model"] == "SINGLE_OWNER_ENTRY"
    assert agent["product_interface"]["execution_mode_selection"] == "NONE"
    assert agent["runtime"]["runtime_type"] == "SINGLE_GITHUB_BACKED_OWNER"
    assert agent["runtime"]["alternate_business_state_runtime_allowed"] is False

    assert execution["product_path"] == "SINGLE_GITHUB_BACKED_FINANCIAL_OWNER"
    assert execution["execution"]["route_selection"] == "NONE"
    assert execution["authority"]["business_state_ref"] == "main"
    assert execution["authority"]["business_state_root"] == "workspaces/articles/{task_id}"
    assert execution["authority"]["alternate_runtime_state_authority_allowed"] is False
    assert execution["execution"]["free_form_article_fallback_allowed"] is False

    assert capabilities["profile_version"] == 11
    assert {cap["capability_id"] for cap in capabilities["capabilities"]} >= {
        "financial_owner_workflow",
        "high_judgment_generation_stages",
        "semantic_review_stages",
        "delivery_and_mechanical_qa",
    }
    assert all(cap["side_channel_allowed"] is False for cap in capabilities["capabilities"])
    assert all(cap["safe_degraded_modes"] == [] for cap in capabilities["capabilities"])

    assert universal["execution_mode_binding"]["route_selection"] == "NONE"
    assert universal["execution_mode_binding"]["business_state_authority"] == "main/workspaces/articles/{task_id}"
    assert universal["legacy_quarantine"]["legacy_presence_may_activate_route"] is False

    assert "PROFILE_11__SINGLE_GITHUB_BACKED_FINANCIAL_OWNER" in task["runtime_version"]
    assert "continuity/FINANCIAL_OWNER_EXECUTION.json" in task["artifact_refs"]
    assert "continuity/GITHUB_CHAT_EXECUTION.json" not in task["artifact_refs"]


def test_retired_discovery_and_runtime_entrypoints_are_not_current_surface():
    assert not (ROOT / "continuity" / "GITHUB_CHAT_EXECUTION.json").exists()
    assert not (ROOT / "plugin.json").exists()

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "scripts" not in pyproject["project"]

    agent = _json("continuity/AGENT_MANIFEST.json")
    current_refs = json.dumps(agent, ensure_ascii=False)
    for retired in (
        "continuity/GITHUB_CHAT_EXECUTION.json",
        "financial_writing_agent/store.py",
        "financial_writing_agent/runtime_service.py",
        "financial_writing_agent/plugin_server.py",
    ):
        assert retired not in json.dumps(agent["workflow"]["state_authority_refs"], ensure_ascii=False)
    assert '"runtime_type": "HYBRID"' not in current_refs


def test_legacy_execution_token_is_quarantined_not_a_route_selector():
    execution = _json("continuity/FINANCIAL_OWNER_EXECUTION.json")
    checkpoint = execution["checkpoint_contract"]
    assert checkpoint["current_execution_mode_storage_token"] == "GITHUB_CHAT"
    assert checkpoint["storage_token_status"] == "LEGACY_INTERNAL_TOKEN_ONLY__NOT_A_ROUTE_SELECTOR"
    assert execution["execution"]["route_selection"] == "NONE"


def test_current_docs_do_not_reintroduce_dual_adapter_operating_model():
    current_docs = [
        ROOT / "README.md",
        ROOT / "docs" / "architecture.md",
        ROOT / "skills" / "financial-writing-agent" / "SKILL.md",
        ROOT / "continuity" / "TASK_INDEX.md",
        ROOT / "continuity" / "tasks" / "financial-writing-main" / "HANDOFF.md",
        ROOT / "deploy" / "chatgpt-site" / "SITE_SPEC.md",
    ]
    forbidden = (
        "two execution adapters behind one business owner",
        "two execution adapters",
        "owner-native Python/plugin 实际可用时",
        "choose OWNER_NATIVE",
        "Otherwise guarded GitHub-chat execution",
    )
    for path in current_docs:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text, f"{path.relative_to(ROOT)} contains retired marker: {marker}"
