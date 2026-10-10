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
