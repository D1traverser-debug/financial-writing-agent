import json
from pathlib import Path


def test_unique_rule_ownership():
    data = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    seen = set()
    for _, keys in data.items():
        for key in keys:
            assert key not in seen, key
            seen.add(key)


def test_visual_workflow_is_explicit_and_owned():
    ownership = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    assert "visuals" in ownership
    assert "visual_planning" in ownership["visuals"]
    assert Path("references/visuals.md").is_file()
    assert not Path("SKILL.md").exists()

    skill = Path("skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    public_server = Path("financial_writing_agent/plugin_server.py").read_text(encoding="utf-8")
    runtime = Path("financial_writing_agent/runtime_service.py").read_text(encoding="utf-8")
    shim = Path("financial_writing_agent/mcp_server.py").read_text(encoding="utf-8")

    assert "references/visuals.md" in skill
    assert "submit_visual_package" in skill
    assert "submit_visual_package" in public_server
    assert "submit_visual_package" in runtime
    assert 'openai/fileParams' in public_server
    assert "@mcp.tool" not in runtime
    assert "@mcp.tool" not in shim
    assert "from .plugin_server import main, mcp" in shim


def test_maintenance_requires_executable_low_judgment_rules_and_canonical_identity():
    ownership = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    maintenance = Path("references/maintenance.md").read_text(encoding="utf-8")

    assert "mechanically_decidable_rule_enforcement" in ownership["maintenance"]
    assert "canonical_system_document_identity" in ownership["maintenance"]
    assert "not migrated merely because prose was updated" in maintenance
    assert "schema/gate/check assertion and a recurrence test" in maintenance
    assert "Canonical system-document identity" in maintenance
    assert "displayed title plus provider identity" in maintenance
