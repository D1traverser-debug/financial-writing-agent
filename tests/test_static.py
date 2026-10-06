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
    server = Path("financial_writing_agent/mcp_server.py").read_text(encoding="utf-8")
    assert "references/visuals.md" in skill
    assert "submit_visual_package" in skill
    assert "submit_visual_package" in server
    assert 'openai/fileParams' in server
