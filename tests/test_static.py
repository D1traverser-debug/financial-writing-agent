import json
from pathlib import Path


def test_unique_rule_ownership():
    data = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    seen = set()
    for _, keys in data.items():
        for key in keys:
            assert key not in seen, key
            seen.add(key)


def test_current_rule_boundaries_and_legacy_removal():
    ownership = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    assert "hooks" in ownership
    assert "style" in ownership
    assert "market_explanation" in ownership
    assert "reader_funnel" in ownership["hooks"]
    assert "qualified_click" in ownership["hooks"]
    assert "headline_curiosity_balance" in ownership["hooks"]
    assert "authorial_selectivity" in ownership["style"]
    assert "argument_progression" in ownership["style"]
    assert "writing_dna_learning" in ownership["style"]
    assert "uncertainty_rhetoric_calibration" in ownership["style"]
    assert "market_explanation_completeness" in ownership["market_explanation"]
    assert "hindsight_causality_control" in ownership["market_explanation"]
    assert "cross_finance_title_clickability" not in ownership["hooks"]
    assert "visuals" not in ownership

    assert Path("skills/financial-writing-agent/references/hooks.md").is_file()
    assert Path("skills/financial-writing-agent/references/market_explanation.md").is_file()
    assert not Path("skills/financial-writing-agent/references/visuals.md").exists()
    assert not Path("financial_writing_agent/resources/references/visuals.md").exists()
    assert not Path("financial_writing_agent/mcp_server.py").exists()
    assert not Path("continuity/tasks/ai-pharma-writing/HANDOFF.md").exists()
    assert not Path("continuity/tasks/site-runtime-gate-a2/HANDOFF.md").exists()
    assert not Path("SKILL.md").exists()

    skill = Path("skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    public_server = Path("financial_writing_agent/plugin_server.py").read_text(encoding="utf-8")
    runtime = Path("financial_writing_agent/runtime_service.py").read_text(encoding="utf-8")
    models = Path("financial_writing_agent/models.py").read_text(encoding="utf-8")
    contracts = Path("financial_writing_agent/mcp_contracts.py").read_text(encoding="utf-8")

    assert "Reader Funnel / Hook Gate" in skill
    assert "Natural Authorial Prose / Writing DNA Gate" in skill
    assert "cross-industry finance clickability" in skill
    assert "not a universal hard requirement" in skill
    assert "references/market_explanation.md" in skill
    assert "VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED" in skill
    assert "submit_hook_audit" in public_server
    assert "submit_hook_audit" in runtime
    assert "writing-docx://{task_id}/{kind}" in public_server
    for removed in ("submit_visual_package", "WECHAT_STICKER_POST", "writing-text://", "CHAT_TEXT"):
        assert removed not in skill
        assert removed not in public_server
        assert removed not in models
        assert removed not in contracts
    assert "@mcp.tool" not in runtime


def test_reader_funnel_and_writing_dna_policy():
    policy = json.loads(Path("config/policy.json").read_text(encoding="utf-8"))
    assert policy["hooks"]["qualified_click_required"] is True
    assert policy["hooks"]["mode_specific_reader_fit_required"] is True
    assert policy["hooks"]["cross_finance_clickability_required"] is False
    assert policy["hooks"]["headline_information_value_required"] is True
    assert policy["hooks"]["headline_curiosity_balance_required"] is True
    assert policy["hooks"]["completion_payoff_required"] is True
    assert policy["hooks"]["account_performance_over_generic_demographics"] is True
    dna = policy["style"]["writing_dna_learning"]
    assert dna["one_off_edit_is_candidate_only"] is True
    assert dna["repeated_independent_patterns_can_promote"] is True
    assert dna["external_skill_rules_are_candidates_only"] is True
    assert policy["style"]["optimize_for_ai_detector"] is False


def test_exact_publication_typography_policy():
    policy = json.loads(Path("config/policy.json").read_text(encoding="utf-8"))
    assert policy["word"]["h1_px"] == 24
    assert policy["word"]["h1_pt"] == 18
    assert policy["word"]["h2_px"] == 20
    assert policy["word"]["h2_pt"] == 15
    assert policy["word"]["body_px"] == 18
    assert policy["word"]["body_pt"] == 13.5
    assert policy["market_explanation"]["multi_hypothesis_required"] is True
