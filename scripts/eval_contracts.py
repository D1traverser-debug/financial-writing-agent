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
    assert manifest["domain_authority"]["task_contract"] == "financial_writing_agent/models.py:TaskContract"
    assert adapter["controller_task_identity_authority"] == "UAOS"
    assert "financial_writing_agent.models.TaskContract.task_id" in adapter["domain_task_identity_authority"]
    assert "NO_EQUALITY_REQUIREMENT" in adapter["identity_boundary"]
    assert adapter["business_state_authority"] == "workspaces/articles/{task_id}/STATE.json"
    assert execution["authority"]["business_state_root"] == "workspaces/articles/{task_id}"
    assert execution["identity"]["task_id_owner"] == "FINANCIAL_WRITING"
    assert execution["identity"]["parent_child_id_equality_required"] is False
    assert execution["execution"]["free_form_article_fallback_allowed"] is False
    required = set(caps["required_uaos_common_capabilities"])
    assert {
        "cross_chat_continuity_and_recovery",
        "hierarchical_authority_governance",
        "adaptive_deliberation_and_parent_guidance",
        "governed_self_evolution",
    }.issubset(required)
    capability_ids = {cap["capability_id"] for cap in caps["capabilities"]}
    assert "domain_owned_article_identity_and_state" in capability_ids
    assert "uaos_article_binding_validation" not in capability_ids
    assert all(cap.get("side_channel_allowed") is False for cap in caps["capabilities"])
    assert not (ROOT / "financial_writing_agent/uaos_binding.py").exists()
    assert not (ROOT / "continuity").exists()
    print("PASS: Financial owns article identity/state; UAOS remains adapter-level controller only")


if __name__ == "__main__":
    main()
