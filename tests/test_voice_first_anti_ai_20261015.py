import json
from pathlib import Path

from financial_writing_agent.checks import analyze_template_scaffolding

ROOT = Path(__file__).resolve().parents[1]


def _policy():
    return json.loads((ROOT / "config/policy.json").read_text(encoding="utf-8"))


def test_single_template_signal_is_diagnostic_not_failure():
    result = analyze_template_scaffolding("这次不是价格先变，而是渠道先变。随后公司之间的兑现差异开始拉开。")
    assert result["total"] == 1
    assert result["requires_revise"] is False


def test_clustered_scaffolding_still_triggers_review():
    text = (
        "真正的变化不在价格，而在渠道。如果只看价格，就会漏掉兑现。这正是最值得关注的地方。"
        "真正的问题不是产品，而是客户。如果只看产品，也会错过差异。这正是核心在于渠道的原因。"
        "真正的机会不是概念，而是兑现。"
    )
    assert analyze_template_scaffolding(text)["requires_revise"] is True


def test_policy_is_voice_first_not_anti_ai_generation_template():
    policy = _policy()
    style = policy["style"]
    assert policy["contract_version"] == "0.9.1"
    assert style["voice_material_first_generation_required"] is True
    assert style["voice_evidence_priority"][0] == "USER_APPROVED_OR_EDITED_SAMPLES"
    assert style["template_cluster_signals_are_diagnostic_not_generation_mandates"] is True
    assert style["single_template_signal_hit_is_not_failure"] is True
    assert style["syntactic_variation_is_diagnostic_not_generation_mandate"] is True
    assert style["paragraph_role_variation_is_diagnostic_not_generation_mandate"] is True
    assert style["comparative_verdict_prose_order_is_flexible"] is True
    assert style["minimum_effective_revision_required"] is True
    assert style["platform_caricature_humanization_forbidden"] is True
    assert style["same_model_critic_passes_are_not_independent_verification"] is True


def test_reader_funnel_is_outcome_gate_not_sentence_slot_formula():
    hooks = _policy()["hooks"]
    assert hooks["first_three_sentence_jobs_are_collective_outcomes_not_one_to_one_slots"] is True
    assert hooks["first_three_sentence_order_and_syntax_flexible"] is True
    assert hooks["headline_target_is_reader_outcome_not_sentence_formula"] is True


def test_audit_requires_semantic_confirmation_before_template_revision():
    audit = _policy()["audit"]
    assert audit["template_cluster_guard_is_review_trigger"] is True
    assert audit["template_cluster_requires_semantic_confirmation_before_revise"] is True
    assert audit["same_model_critic_passes_do_not_upgrade_assurance"] is True


def test_current_reader_value_rule_rejects_humanizer_caricature():
    rule = (ROOT / "references/reader_value.md").read_text(encoding="utf-8")
    assert "去AI味” is not a generation style" in rule
    assert "Voice evidence priority" in rule
    assert "not generation mandates" in rule
    assert "platform caricature" in rule
    assert "minimum effective revision" in rule
    assert "not independent verification" in rule
    assert "map these jobs mechanically to sentence 1/2/3" in rule
