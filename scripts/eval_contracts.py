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
    assert manifest["domain_authority"]["business_contract"] == "financial_writing_agent/models.py:TaskContract"
    assert manifest["domain_authority"]["article_identity"] == "workspaces/articles/{task_id}/STATE.json::task_id"
    assert adapter["controller_task_identity_authority"] == "UAOS"
    assert adapter["domain_article_identity_authority"] == "workspaces/articles/{task_id}/STATE.json::task_id"
    assert "NO_EQUALITY_REQUIREMENT" in adapter["identity_boundary"]
    assert adapter["business_state_authority"] == "workspaces/articles/{task_id}/STATE.json"
    assert execution["authority"]["business_state_root"] == "workspaces/articles/{task_id}"
    assert execution["identity"]["article_id_owner"] == "FINANCIAL_WRITING"
    assert execution["identity"]["business_contract_is_identity_free"] is True
    assert execution["identity"]["parent_child_id_equality_required"] is False
    assert execution["task_contract"]["identity_free"] is True
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
    assert "identity_free_business_output_contract" in capability_ids
    assert "uaos_article_binding_validation" not in capability_ids
    assert all(cap.get("side_channel_allowed") is False for cap in caps["capabilities"])
    assert not (ROOT / "financial_writing_agent/uaos_binding.py").exists()
    assert not (ROOT / "continuity").exists()
    print("PASS: Financial STATE owns article identity; TaskContract is identity-free; UAOS stays at the adapter boundary")


if __name__ == "__main__":
    main()
