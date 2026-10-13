import json
from pathlib import Path

from financial_writing_agent.workflow_spec import BUSINESS_STAGE_NAMES

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
    assert c["authority"]["canonical_workflow_spec"] == "financial_writing_agent/workflow_spec.py"
    assert c["authority"]["transition_guard"] == "financial_writing_agent/github_chat_guard.py"
    assert c["authority"]["lifecycle_guard"] == "financial_writing_agent/github_chat_lifecycle.py"
    assert "deterministic" in c["activation"]["when"].lower()


def test_every_material_stage_has_durable_evidence_obligation_without_second_stage_list():
    c = contract()
    evidence = c["stage_evidence"]
    assert BUSINESS_STAGE_NAMES == (
        "INTAKE", "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE", "DRAFT",
        "EDITORIAL_AUDIT", "DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT",
    )
    assert c["workflow"]["canonical_stage_order_symbol"] == "BUSINESS_STAGE_ORDER"
    assert "stage_order" not in c["workflow"]
    for stage in BUSINESS_STAGE_NAMES[1:]:
        assert stage in evidence
        assert evidence[stage].strip()
    assert "stage_artifacts" in c["checkpoint_contract"]["required_fields"]
    assert "review_assurance" in c["checkpoint_contract"]["required_fields"]
    assert "execution_receipts" in c["checkpoint_contract"]["required_fields"]
    assert "blocked_recovery" in c["checkpoint_contract"]


def test_chat_review_and_lifecycle_never_upgrade_themselves_to_native_or_independent_pass():
    c = contract()
    assurance = c["assurance"]
    assert assurance["chat_review_label"] == "CHAT_SELF_REVIEW"
    assert assurance["chat_execution_receipt_label"] == "SELF_ATTESTED_CHAT_EXECUTION_RECEIPT"
    assert assurance["chat_lifecycle_closure_label"] == "SELF_ATTESTED_CHAT_EVIDENCE_BINDING"
    assert assurance["chat_review_can_issue_owner_native_semantic_pass"] is False
    assert assurance["chat_review_can_claim_independent_execution"] is False
    assert assurance["guard_pass_is_independent_execution"] is False
    assert assurance["lifecycle_evidence_ref_binding_is_independent_verification"] is False
    assert c["workflow"]["terminal_status"] == "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN"
    assert c["workflow"]["terminal_status"] != c["workflow"]["owner_native_terminal_status"]


def test_material_negative_feedback_cannot_be_chat_only_or_silently_cleared():
    c = contract()
    rule = c["learning_and_maintenance"]["material_user_edit_feedback_rejection"]
    lifecycle = c["learning_and_maintenance"]["system_impact_lifecycle"]
    assert "github_chat_guard.attach_material_feedback" in rule
    assert "OPEN system-impact" in rule
    assert "same guarded STATE.json mutation" in rule
    assert "github_chat_lifecycle.review_system_impact_state" in lifecycle
    assert "SELF_ATTESTED_CHAT_EVIDENCE_BINDING" in lifecycle
    assert c["learning_and_maintenance"]["owner_plugin_receipt_claim_when_plugin_unavailable"] == "FORBIDDEN"


def test_failure_modes_fail_closed_at_exact_missing_capability():
    c = contract()
    failure = c["failure_behavior"]
    assert "BLOCK" in failure["missing_transition_guard"]
    assert "BLOCK" in failure["missing_lifecycle_guard"]
    assert "BLOCK" in failure["missing_github_write"]
    assert "do not invent current evidence" in failure["missing_web_for_current_fact_research"]
    assert "DOCX delivery OPEN" in failure["missing_document_tooling"]
    assert "do not fabricate PASS" in failure["missing_independent_or_owner_native_audit"]
    assert "STATE.json" in failure["context_or_connection_loss"]
