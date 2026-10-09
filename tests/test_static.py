import json
from pathlib import Path


def test_unique_rule_ownership():
    data = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    seen = set()
    for _, keys in data.items():
        for key in keys:
            assert key not in seen, key
            seen.add(key)


def test_hook_authorial_prose_market_explanation_and_visual_boundaries():
    ownership = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    assert "hooks" in ownership
    assert "style" in ownership
    assert "market_explanation" in ownership
    assert "cross_finance_title_clickability" in ownership["hooks"]
    assert "authorial_specificity" in ownership["style"]
    assert "uncertainty_calibration" in ownership["style"]
    assert "market_explanation_completeness" in ownership["market_explanation"]
    assert "hindsight_causality_control" in ownership["market_explanation"]
    assert "visuals" not in ownership
    assert Path("skills/financial-writing-agent/references/hooks.md").is_file()
    assert Path("skills/financial-writing-agent/references/market_explanation.md").is_file()
    assert not Path("skills/financial-writing-agent/references/visuals.md").exists()
    assert not Path("financial_writing_agent/resources/references/visuals.md").exists()
    assert not Path("SKILL.md").exists()

    skill = Path("skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    public_server = Path("financial_writing_agent/plugin_server.py").read_text(encoding="utf-8")
    runtime = Path("financial_writing_agent/runtime_service.py").read_text(encoding="utf-8")
    shim = Path("financial_writing_agent/mcp_server.py").read_text(encoding="utf-8")

    assert "references/hooks.md" in skill
    assert "references/market_explanation.md" in skill
    assert "VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED" in skill
    assert "submit_hook_audit" in public_server
    assert "submit_hook_audit" in runtime
    assert "submit_visual_package" not in skill
    assert "submit_visual_package" not in public_server
    assert "submit_visual_package" not in runtime
    assert "@mcp.tool" not in runtime
    assert "@mcp.tool" not in shim
    assert "from .plugin_server import main, mcp" in shim


def test_exact_publication_typography_policy():
    policy = json.loads(Path("config/policy.json").read_text(encoding="utf-8"))
    assert policy["word"]["h1_px"] == 24
    assert policy["word"]["h1_pt"] == 18
    assert policy["word"]["h2_px"] == 20
    assert policy["word"]["h2_pt"] == 15
    assert policy["word"]["body_px"] == 18
    assert policy["word"]["body_pt"] == 13.5
    assert policy["market_explanation"]["multi_hypothesis_required"] is True
    assert policy["style"]["optimize_for_ai_detector"] is False
