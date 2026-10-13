from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RETIRED_CURRENT_TREE_PATHS = (
    "continuity/GITHUB_CHAT_EXECUTION.json",
    "financial_writing_agent/github_chat_guard.py",
    "financial_writing_agent/adapters/deterministic.py",
    "financial_writing_agent/adapters/openai_agents.py",
    "financial_writing_agent/cli.py",
    "financial_writing_agent/controller.py",
    "financial_writing_agent/engine.py",
    "financial_writing_agent/mcp_contracts.py",
    "financial_writing_agent/methodology_receipts.py",
    "financial_writing_agent/network_safety.py",
    "financial_writing_agent/plugin_server.py",
    "financial_writing_agent/runner.py",
    "financial_writing_agent/runtime_factory.py",
    "financial_writing_agent/runtime_service.py",
    "financial_writing_agent/semantic_runtime.py",
    "financial_writing_agent/state_recovery.py",
    "financial_writing_agent/store.py",
    "financial_writing_agent/system_impact.py",
    "plugin.json",
    "scripts/sdk_smoke.py",
    "scripts/mcp_smoke.py",
)


def test_retired_second_runtime_cannot_reenter_current_tree():
    offenders = [path for path in RETIRED_CURRENT_TREE_PATHS if (ROOT / path).exists()]
    assert offenders == [], f"retired Financial runtime files returned to current tree: {offenders}"


def test_current_owner_components_exist():
    required = (
        "continuity/FINANCIAL_OWNER_EXECUTION.json",
        "financial_writing_agent/owner_guard.py",
        "financial_writing_agent/owner_lifecycle.py",
        "financial_writing_agent/workflow_spec.py",
        "financial_writing_agent/models.py",
    )
    missing = [path for path in required if not (ROOT / path).is_file()]
    assert missing == [], f"current Financial owner components missing: {missing}"
