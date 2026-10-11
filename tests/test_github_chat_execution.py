import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def contract():
    return json.loads((ROOT / "continuity/GITHUB_CHAT_EXECUTION.json").read_text(encoding="utf-8"))


def test_github_chat_is_explicit_not_freeform_fallback():
    c = contract()
    assert c["execution_mode"] == "CHAT_BRIDGED"
    assert c["executor_type"] == "CHAT_BRIDGED_LLM_WITH_GITHUB_STATE"
    assert c["activation"]["free_form_article_fallback_allowed"] is False
    assert c["authority"]["chat_memory_is_business_state_authority"] is False
    assert c["authority"]["site_or_mcp_deployment_is_required_for_this_mode"] is False


def test_every_material_stage_has_durable_evidence_obligation():
    c = contract()
    stages = c["workflow"]["stage_order"]
    evidence = c["stage_evidence"]
    assert stages == [
        "INTAKE", "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE", "DRAFT",
        "EDITORIAL_AUDIT", "DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT",
    ]
    for stage in stages[1:]:
        assert stage in evidence
        assert evidence[stage].strip()
    assert "stage_artifacts" in c["checkpoint_contract"]["required_fields"]
    assert "review_assurance" in c["checkpoint_contract"]["required_fields"]


def test_chat_review_never_upgrades_itself_to_native_or_independent_pass():
    c = contract()
    assurance = c["assurance"]
    assert assurance["chat_review_label"] == "CHAT_SELF_REVIEW"
    assert assurance["chat_review_can_issue_owner_native_semantic_pass"] is False
    assert assurance["chat_review_can_claim_independent_execution"] is False
    assert c["workflow"]["terminal_status"] == "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN"
    assert c["workflow"]["terminal_status"] != c["workflow"]["owner_native_terminal_status"]


def test_material_negative_feedback_cannot_be_chat_only():
    c = contract()
    rule = c["learning_and_maintenance"]["material_user_edit_feedback_rejection"]
    assert "same GitHub mutation set" in rule
    assert "OPEN system-impact" in rule
    assert c["learning_and_maintenance"]["owner_plugin_receipt_claim_when_plugin_unavailable"] == "FORBIDDEN"


def test_failure_modes_fail_closed_at_exact_missing_capability():
    c = contract()
    failure = c["failure_behavior"]
    assert "BLOCK" in failure["missing_github_write"]
    assert "do not invent current evidence" in failure["missing_web_for_current_fact_research"]
    assert "DOCX delivery OPEN" in failure["missing_document_tooling"]
    assert "do not fabricate PASS" in failure["missing_independent_or_owner_native_audit"]
    assert "STATE.json" in failure["context_or_connection_loss"]
