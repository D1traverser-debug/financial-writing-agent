import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_github_chat_is_bound_into_manifest_capabilities_and_skill():
    manifest = json.loads((ROOT / "continuity/AGENT_MANIFEST.json").read_text(encoding="utf-8"))
    profile = json.loads((ROOT / "continuity/EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))
    chat = json.loads((ROOT / "continuity/GITHUB_CHAT_EXECUTION.json").read_text(encoding="utf-8"))
    skill = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")

    kernel = "financial_writing_agent/workflow_spec.py"
    guard = "financial_writing_agent/github_chat_guard.py"
    assert guard in manifest["runtime"]["entrypoints"]
    assert kernel in manifest["workflow"]["transition_guard_refs"]
    assert guard in manifest["workflow"]["transition_guard_refs"]
    assert "continuity/GITHUB_CHAT_EXECUTION.json" in manifest["workflow"]["state_authority_refs"]
    assert chat["authority"]["canonical_workflow_spec"] == kernel
    assert chat["authority"]["transition_guard"] == guard
    assert "github_chat_guard" in skill

    capabilities = {item["capability_id"]: item for item in profile["capabilities"]}
    for capability_id in (
        "github_chat_workflow",
        "github_chat_review_stages",
        "github_chat_delivery_and_mechanical_qa",
        "github_chat_learning_evidence_capture",
    ):
        capability = capabilities[capability_id]
        assert "github_chat_guard" in capability["invocation_path"] or "github_chat_guard" in capability["executor_ref"]
        assert "python_runtime_or_equivalent_deterministic_guard" in capability["required_tools"]
        assert capability["side_channel_allowed"] is False


def test_github_chat_contract_requires_action_bound_receipts_cas_and_one_workflow_authority():
    chat = json.loads((ROOT / "continuity/GITHUB_CHAT_EXECUTION.json").read_text(encoding="utf-8"))
    checkpoint = chat["checkpoint_contract"]

    assert chat["schema_version"] == "1.2"
    assert checkpoint["state_schema_version"] == "1.1"
    assert "execution_receipts" in checkpoint["required_fields"]
    assert "prior state blob SHA" in checkpoint["execution_receipt_rule"]
    assert "same SHA" in checkpoint["mutation_guard"]
    assert "guard PASS" in checkpoint["post_write_verification"]
    assert chat["workflow"]["canonical_stage_order_symbol"] == "BUSINESS_STAGE_ORDER"
    assert "stage_order" not in chat["workflow"]
    assert any("action-bound execution receipt" in item for item in chat["anti_bypass"])


def test_chat_guard_does_not_upgrade_review_assurance():
    chat = json.loads((ROOT / "continuity/GITHUB_CHAT_EXECUTION.json").read_text(encoding="utf-8"))
    assurance = chat["assurance"]

    assert assurance["chat_review_label"] == "CHAT_SELF_REVIEW"
    assert assurance["chat_execution_receipt_label"] == "SELF_ATTESTED_CHAT_EXECUTION_RECEIPT"
    assert assurance["chat_review_can_issue_owner_native_semantic_pass"] is False
    assert assurance["chat_review_can_claim_independent_execution"] is False
    assert assurance["guard_pass_is_independent_execution"] is False
