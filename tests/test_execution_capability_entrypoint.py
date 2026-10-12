import json
from pathlib import Path

from financial_writing_agent.workflow_spec import BUSINESS_STAGE_NAMES

ROOT = Path(__file__).resolve().parents[1]


def test_skill_and_continuity_index_require_execution_capability_handshake():
    skill = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    index = (ROOT / "continuity/TASK_INDEX.md").read_text(encoding="utf-8")
    profile = json.loads((ROOT / "continuity/EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))
    chat = json.loads((ROOT / "continuity/GITHUB_CHAT_EXECUTION.json").read_text(encoding="utf-8"))
    capabilities = {item["capability_id"]: item for item in profile["capabilities"]}

    assert "continuity/EXECUTION_CAPABILITIES.json" in skill
    assert "session" in skill.lower() and "handshake" in skill.lower()
    assert profile["execution_readiness_contract"] == "1.0"
    assert profile["owner"] == "FINANCIAL_WRITING_AGENT_RUNTIME"
    assert profile["profile_version"] == 10

    chat_flow = capabilities["github_chat_workflow"]
    assert chat_flow["executor_type"] == "CHAT_BRIDGED_LLM_WITH_GITHUB_STATE_AND_DETERMINISTIC_TRANSITION_GUARD"
    assert "GitHub_owner_read_write" in chat_flow["required_tools"]
    assert "python_runtime_or_equivalent_deterministic_guard" in chat_flow["required_tools"]
    assert "github_chat_guard" in chat_flow["invocation_path"]
    assert any("DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN" in item for item in chat_flow["evidence_contract"])
    assert any("exact task/stage/capability/action" in item for item in chat_flow["evidence_contract"])
    assert chat["activation"]["free_form_article_fallback_allowed"] is False
    assert chat["authority"]["state_file"] == "workspaces/articles/{task_id}/STATE.json"
    assert chat["authority"]["canonical_workflow_spec"] == "financial_writing_agent/workflow_spec.py"
    assert chat["authority"]["transition_guard"] == "financial_writing_agent/github_chat_guard.py"
    assert chat["workflow"]["terminal_status"] == "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN"
    assert chat["assurance"]["chat_review_can_issue_owner_native_semantic_pass"] is False
    assert chat["assurance"]["guard_pass_is_independent_execution"] is False
    assert "GITHUB_CHAT_EXECUTION.json" in skill
    assert "github_chat_guard" in skill

    generation = capabilities["high_judgment_generation_stages"]
    assert generation["safe_degraded_modes"] == ["CHAT_BRIDGED"]
    assert "RESEARCH_AUDIT" not in generation["scope"]

    semantic = capabilities["semantic_audit_stages"]
    assert semantic["safe_degraded_modes"] == []
    assert semantic["scope"] == "RESEARCH_AUDIT,EDITORIAL_AUDIT,FINAL_AUDIT"
    assert any("EXECUTOR_START" in item and "EXECUTOR_END" in item for item in semantic["evidence_contract"])
    assert any("not provider-attested isolation" in item for item in semantic["evidence_contract"])

    chat_review = capabilities["github_chat_review_stages"]
    assert chat_review["executor_type"] == "CHAT_BRIDGED_SELF_REVIEW_WITH_DETERMINISTIC_ROUTE_GUARD"
    assert "python_runtime_or_equivalent_deterministic_guard" in chat_review["required_tools"]
    assert any("no translation" in item.lower() for item in chat_review["evidence_contract"])

    quality_gate = capabilities["quality_regression_promotion_gate"]
    assert quality_gate["assurance_ceiling"] == "HARNESS_WIRED"
    assert "case_artifact_binding_verifier" in quality_gate["required_tools"]
    assert "candidate_evidence_semantic_verifier" in quality_gate["required_tools"]
    assert "hard_regression_execution_and_semantic_verifier" in quality_gate["required_tools"]
    assert "judge_run_semantic_verifier" in quality_gate["required_tools"]
    assert any("at least two distinct held-out topic families" in item for item in quality_gate["evidence_contract"])
    assert any("exact candidate id and candidate-change ref" in item for item in quality_gate["evidence_contract"])
    assert any("callback presence alone" in item for item in quality_gate["evidence_contract"])


def test_github_chat_uses_canonical_owner_business_sequence_and_cannot_claim_native_complete():
    chat = json.loads((ROOT / "continuity/GITHUB_CHAT_EXECUTION.json").read_text(encoding="utf-8"))
    assert BUSINESS_STAGE_NAMES == (
        "INTAKE", "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE", "DRAFT",
        "EDITORIAL_AUDIT", "DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT",
    )
    assert chat["workflow"]["canonical_stage_order_symbol"] == "BUSINESS_STAGE_ORDER"
    assert "stage_order" not in chat["workflow"]
    assert chat["workflow"]["owner_native_terminal_status"] == "COMPLETE"
    assert chat["workflow"]["terminal_status"] != "COMPLETE"
    assert chat["authority"]["chat_memory_is_business_state_authority"] is False
    assert "same SHA" in chat["checkpoint_contract"]["mutation_guard"]
    assert "execution_receipts" in chat["checkpoint_contract"]["required_fields"]
    assert any("No publishable final article" in item for item in chat["anti_bypass"])
    assert any("No chat self-review" in item for item in chat["anti_bypass"])
    assert any("action-bound execution receipt" in item for item in chat["anti_bypass"])


def test_material_user_feedback_has_real_durable_learning_and_system_impact_paths():
    skill = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    maintenance = (ROOT / "skills/financial-writing-agent/references/maintenance.md").read_text(encoding="utf-8")
    profile = json.loads((ROOT / "continuity/EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))
    chat = json.loads((ROOT / "continuity/GITHUB_CHAT_EXECUTION.json").read_text(encoding="utf-8"))
    capabilities = {item["capability_id"]: item for item in profile["capabilities"]}

    assert "material explicit user edit, feedback, rejection or acceptance" in skill
    assert "OPEN system-impact item" in skill
    assert "material explicit user edit, feedback, rejection or acceptance" in maintenance
    learning = capabilities["learning_evidence_capture"]
    assert learning["assurance_ceiling"] == "SESSION_EXECUTABLE"
    assert "record_writing_learning_sample" in learning["invocation_path"]
    assert any("PENDING_REVIEW" in item for item in learning["evidence_contract"])

    chat_learning = capabilities["github_chat_learning_evidence_capture"]
    assert "GitHub_owner_read_write" in chat_learning["required_tools"]
    assert "python_runtime_or_equivalent_deterministic_guard" in chat_learning["required_tools"]
    assert "github_chat_guard.attach_material_feedback" in chat_learning["invocation_path"]
    assert any("OPEN system-impact" in item for item in chat_learning["evidence_contract"])
    assert "github_chat_guard.attach_material_feedback" in chat["learning_and_maintenance"]["material_user_edit_feedback_rejection"]
    assert chat["learning_and_maintenance"]["owner_plugin_receipt_claim_when_plugin_unavailable"] == "FORBIDDEN"

    impact = capabilities["system_impact_escalation"]
    assert impact["assurance_ceiling"] == "SESSION_EXECUTABLE"
    assert "review_writing_system_impact" in impact["required_tools"]
    assert any("at least two distinct mechanisms" in item for item in impact["evidence_contract"])
    assert any("cannot be bypassed at COMPLETE" in item for item in impact["evidence_contract"])
    assert any("completed tasks with MAINTENANCE_REQUIRED remain discoverable" in item for item in impact["evidence_contract"])
    assert any("does not prove independent verification or improved prose" in item for item in impact["evidence_contract"])


def test_financial_systemic_maintenance_inherits_universal_meta_governance_without_copying_root_policy():
    maintenance = (ROOT / "references/maintenance.md").read_text(encoding="utf-8")
    skill_mirror = (ROOT / "skills/financial-writing-agent/references/maintenance.md").read_text(encoding="utf-8")
    packaged = (ROOT / "financial_writing_agent/resources/references/maintenance.md").read_text(encoding="utf-8")
    adapter = json.loads((ROOT / "continuity/UNIVERSAL_PROTOCOL_ADAPTER.json").read_text(encoding="utf-8"))

    assert maintenance == skill_mirror == packaged
    assert "Universal meta-maintenance entry" in maintenance
    assert "systemic/non-trivial maintenance" in maintenance
    assert "learning/benchmark scout" in maintenance
    assert "instruction" in maintenance and "complexity/efficiency" in maintenance
    assert adapter["methodology"]["profile_refs"]["operational_hygiene"] == "1.0"
    assert adapter["methodology"]["profile_refs"]["evolution"] == "1.0"
    assert "review_writing_system_impact" in adapter["methodology"]["hook_bindings"]["self_maintenance_trigger_path"]


def test_financial_owner_binds_artifact_io_and_all_three_action_receipt_profiles():
    adapter = json.loads((ROOT / "continuity/UNIVERSAL_PROTOCOL_ADAPTER.json").read_text(encoding="utf-8"))
    methodology = adapter["methodology"]

    assert methodology["profile_refs"] == {
        "artifact_io": "1.0",
        "operational_hygiene": "1.0",
        "evolution": "1.0",
    }

    required_artifact_hooks = {
        "durable_task_state_location",
        "authoritative_business_evidence_classes",
        "canonical_artifact_or_file_stores",
        "cache_or_reference_only_stores",
        "stable_identity_strategy",
        "read_freshness_requirements",
        "mutation_conflict_strategy",
        "post_write_verification_method",
        "upstream_to_downstream_invalidation_rule",
        "delete_and_retention_rules",
        "superseded_artifact_cleanup_rule",
        "external_artifact_vault_if_any",
    }
    assert required_artifact_hooks.issubset(methodology["hook_bindings"])
    assurance = adapter["methodology_assurance"]
    assert "PROFILE_10_GITHUB_CHAT_EXECUTION_DECLARED" in assurance["operational_status"]
    assert "OWNER_NATIVE_ACTION_RECEIPT_V1_3_WIRED" in assurance["operational_status"]
    assert "INDEPENDENT_OPERATIONAL_VERIFICATION_PENDING" in assurance["operational_status"]
    wiring = assurance["action_receipt_wiring"]
    assert wiring["receipt_contract_version"] == "1.3"
    assert wiring["receipt_status"] == "UNVERIFIED_OWNER_RECEIPT"
    assert wiring["exact_action_binding_required"] == [
        "task_id", "stage", "action_id", "subject_bindings", "input_bindings"
    ]
    assert wiring["independent_verification_required"] == "EVIDENCE_REF_PLUS_SEMANTIC_HOOK_ASSESSMENT_PLUS_EXACT_ACTION_BINDING"
    assert wiring["wired_profiles"] == ["artifact_io", "operational_hygiene", "evolution"]
    assert "independent" in wiring["remaining_unproven_boundary"].lower()


def test_public_owner_actions_emit_unverified_action_receipts_but_do_not_self_attest():
    server = (ROOT / "financial_writing_agent" / "plugin_server.py").read_text(encoding="utf-8")
    receipt_runtime = (ROOT / "financial_writing_agent" / "methodology_receipts.py").read_text(encoding="utf-8")
    contracts = (ROOT / "financial_writing_agent" / "mcp_contracts.py").read_text(encoding="utf-8")
    profile = json.loads((ROOT / "continuity/EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))
    capabilities = {item["capability_id"]: item for item in profile["capabilities"]}
    receipt_capability = capabilities["methodology_action_receipts"]

    assert "record_learning_evolution_receipt" in server
    assert "record_system_impact_hygiene_receipt" in server
    assert "record_artifact_io_receipt" in server
    assert "methodology_profile_runs" in server
    assert "run_semantic_audit_stage" in server
    assert "review_writing_system_impact" in server
    assert "_reject_unverified_semantic_pass" in server
    assert 'RECEIPT_CONTRACT_VERSION = "1.3"' in receipt_runtime
    assert '"action_binding": {' in receipt_runtime
    assert '"task_id": state.contract.task_id' in receipt_runtime
    assert '"stage": state.stage.value' in receipt_runtime
    assert '"action_id": activation_id' in receipt_runtime
    assert '"subject_bindings": dict(subject_bindings)' in receipt_runtime
    assert '"input_bindings": dict(input_bindings)' in receipt_runtime
    assert "UNVERIFIED_OWNER_RECEIPT" in receipt_runtime
    assert "external_ref_and_semantic_assessment_required" in receipt_runtime
    assert 'receipt_contract_version: Literal["1.3"]' in contracts
    assert "class MethodologyActionBindingSummary" in contracts
    assert "action_binding: MethodologyActionBindingSummary" in contracts
    assert "Financial Writing v0.8.1 is Word-only" in server
    assert "operational conformance" in server
    assert "universal_independent_evidence_ref_verifier_for_operational_pass" in receipt_capability["required_tools"]
    assert "universal_independent_hook_assessment_verifier_for_operational_pass" in receipt_capability["required_tools"]
    assert any("exact action binding" in item.lower() for item in receipt_capability["evidence_contract"])
    assert any("real but irrelevant evidence ref" in item for item in receipt_capability["evidence_contract"])
