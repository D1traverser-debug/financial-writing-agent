import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_skill_and_continuity_index_require_execution_capability_handshake():
    skill = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    index = (ROOT / "continuity/TASK_INDEX.md").read_text(encoding="utf-8")
    profile = json.loads((ROOT / "continuity/EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))

    assert "continuity/EXECUTION_CAPABILITIES.json" in skill
    assert "continuity/EXECUTION_CAPABILITIES.json" in index
    assert "session" in skill.lower() and "handshake" in skill.lower()
    assert profile["execution_readiness_contract"] == "1.0"
    assert profile["owner"] == "FINANCIAL_WRITING_AGENT_RUNTIME"


def test_material_user_feedback_has_real_durable_learning_evidence_path():
    skill = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    maintenance = (ROOT / "skills/financial-writing-agent/references/maintenance.md").read_text(encoding="utf-8")
    profile = json.loads((ROOT / "continuity/EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))
    capabilities = {item["capability_id"]: item for item in profile["capabilities"]}

    assert "material explicit user edit, feedback, rejection or acceptance" in skill
    assert "durable learning was not persisted" in skill
    assert "material explicit user edit, feedback, rejection or acceptance" in maintenance
    assert "learning_evidence_capture" in capabilities
    learning = capabilities["learning_evidence_capture"]
    assert learning["assurance_ceiling"] == "SESSION_EXECUTABLE"
    assert "record_writing_learning_sample" in learning["invocation_path"]
    assert any("persisted sample receipt" in item for item in learning["evidence_contract"])


def test_financial_owner_binds_artifact_io_for_real_file_and_artifact_work():
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
    assert adapter["methodology_assurance"]["operational_status"] == "ACTION_LEVEL_PROFILE_ACTIVATION_AND_INDEPENDENT_EVIDENCE_RECEIPT_NOT_YET_PROVEN"


def test_public_owner_actions_emit_unverified_action_receipts_but_do_not_self_attest():
    server = (ROOT / "financial_writing_agent" / "plugin_server.py").read_text(encoding="utf-8")
    receipt_runtime = (ROOT / "financial_writing_agent" / "methodology_receipts.py").read_text(encoding="utf-8")
    contracts = (ROOT / "financial_writing_agent" / "mcp_contracts.py").read_text(encoding="utf-8")

    assert "record_learning_evolution_receipt" in server
    assert "record_artifact_io_receipt" in server
    assert "methodology_profile_runs" in server
    assert "UNVERIFIED_OWNER_RECEIPT" in receipt_runtime
    assert "external_required" in receipt_runtime
    assert "MethodologyProfileRunSummary" in contracts
    assert "Financial Writing v0.7 is Word-only" in server
    assert "Financial Writing v0.6 is Word-only" not in server
    assert "operational conformance" in server
