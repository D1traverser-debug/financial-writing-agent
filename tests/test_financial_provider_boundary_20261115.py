import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_financial_remains_parent_independent_but_requires_a_hosted_provider_action():
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    capabilities = _json("config/FINANCIAL_CAPABILITIES.json")
    execution = _json("config/EXECUTION_CONTRACT.json")

    assert manifest["external_parent_required"] is False
    assert manifest["external_host_required"] is True
    assert manifest["provider_action_required"] is True
    assert manifest["provider_action_endpoint"]["protocol"] == "MCP_OVER_HTTPS"
    assert manifest["provider_action_endpoint"]["status"] == "NOT_DEPLOYED"

    assert capabilities["independent_parent_free"] is True
    assert "HOSTED_FINANCIAL_PROVIDER_ACTION_MCP_ENDPOINT_WITH_AUTHENTICATED_OWNER_IDENTITY" in (
        capabilities["required_external_capabilities_at_execution"]
    )
    assert "NO_EXTERNAL_PARENT" in capabilities["independence_clause"]

    governance = execution["standalone_governance"]
    native = execution["chatgpt_native_execution"]
    assert governance["external_parent_required"] is False
    assert governance["external_provider_host_required"] is True
    assert native["required_provider_action"] == "HOSTED_FINANCIAL_PROVIDER_ACTION_MCP_OVER_HTTPS"
    assert native["provider_action_status"] == "NOT_DEPLOYED"
    assert native["canonical_owner_state_and_method_mutation"].startswith(
        "HOSTED_FINANCIAL_PROVIDER_ACTION_ONLY"
    )


def test_skill_only_plugin_is_not_misrepresented_as_a_live_provider_action():
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    plugin = _json("config/CHATGPT_FINANCIAL_PLUGIN.json")
    canonical = manifest["client_skill_plugin"]

    assert canonical["hosted_mcp_python"] is False
    assert canonical["provider_action_status"] == "NOT_DEPLOYED"
    assert canonical["custom_hosted_service_required"] is True

    assert plugin["skill_only"] is True
    assert plugin["has_hosted_mcp_or_python_action_endpoint"] is False
    assert plugin["custom_hosted_python_mcp_required"] is True
    assert plugin["provider_action_status"] == "NOT_DEPLOYED"
    assert plugin["required_companion_action"] == "FINANCIAL_PROVIDER_ACTION_MCP_OVER_HTTPS"
    assert plugin["version"] == canonical["version"] == "0.1.3"
    assert plugin["release_id"] == canonical["release_id"]


def test_provider_decision_rejects_public_issue_comment_command_bus_and_paid_infra_without_approval():
    decision = (ROOT / "docs/FINANCIAL_PROVIDER_BRIDGE_DECISION_20261115.md").read_text(
        encoding="utf-8"
    )
    assert "repository is public" in decision
    assert "issue-comment command bus is rejected" in decision
    assert "No paid compute" in decision
    assert "authenticated provider confirmation surface" in decision
