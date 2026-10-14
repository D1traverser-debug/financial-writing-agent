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
    assert manifest["binding"] == {
        "controller_ref": "D1traverser-debug/universal-agent-os@main:CURRENT_SYSTEM.json",
        "adapter_ref": ".uaos/ADAPTER.json",
        "capability_ref": ".uaos/CAPABILITIES.json",
    }
    assert adapter["business_state_authority"] == "workspaces/articles/{task_id}/STATE.json"
    assert adapter["article_binding_validator"] == "financial_writing_agent.uaos_binding.validate_uaos_article_binding"
    assert execution["authority"]["business_state_root"] == "workspaces/articles/{task_id}"
    assert execution["authority"]["uaos_binding_validator"] == adapter["article_binding_validator"]
    assert execution["uaos_article_task_binding"]["identity_rule"] == "UAOS_ARTICLE_TASK_ID_EQUALS_FINANCIAL_STATE_TASK_ID"
    assert execution["uaos_article_task_binding"]["router_task_id"] == "financial-writing:main"
    assert execution["execution"]["free_form_article_fallback_allowed"] is False
    required = set(caps["required_uaos_common_capabilities"])
    assert {
        "cross_chat_continuity_and_recovery",
        "hierarchical_authority_governance",
        "adaptive_deliberation_and_parent_guidance",
        "governed_self_evolution",
    }.issubset(required)
    assert any(cap["capability_id"] == "uaos_article_binding_validation" for cap in caps["capabilities"])
    assert all(cap.get("side_channel_allowed") is False for cap in caps["capabilities"])
    assert not (ROOT / "continuity").exists()
    print("PASS: Financial architecture/evaluation contracts match current UAOS binding")


if __name__ == "__main__":
    main()
