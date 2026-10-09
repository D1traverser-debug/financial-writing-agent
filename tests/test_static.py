import json
from pathlib import Path


def test_unique_rule_ownership():
    data = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    seen = set()
    for _, keys in data.items():
        for key in keys:
            assert key not in seen, key
            seen.add(key)


def test_hook_and_human_voice_workflow_is_explicit_and_visuals_removed():
    ownership = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    assert "hooks" in ownership
    assert "style" in ownership
    assert "cross_finance_title_clickability" in ownership["hooks"]
    assert "human_voice" in ownership["style"]
    assert "visuals" not in ownership
    assert Path("skills/financial-writing-agent/references/hooks.md").is_file()
    assert not Path("skills/financial-writing-agent/references/visuals.md").exists()
    assert not Path("financial_writing_agent/resources/references/visuals.md").exists()
    assert not Path("SKILL.md").exists()

    skill = Path("skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    public_server = Path("financial_writing_agent/plugin_server.py").read_text(encoding="utf-8")
    runtime = Path("financial_writing_agent/runtime_service.py").read_text(encoding="utf-8")
    shim = Path("financial_writing_agent/mcp_server.py").read_text(encoding="utf-8")

    assert "references/hooks.md" in skill
    assert "submit_hook_audit" in public_server
    assert "submit_hook_audit" in runtime
    assert "submit_visual_package" not in skill
    assert "submit_visual_package" not in public_server
    assert "submit_visual_package" not in runtime
    assert "@mcp.tool" not in runtime
    assert "@mcp.tool" not in shim
    assert "from .plugin_server import main, mcp" in shim
