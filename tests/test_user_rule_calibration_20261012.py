import json

from financial_writing_agent.schemas import ArticlePayload


def _policy():
    return json.loads(open("config/policy.json", encoding="utf-8").read())


def test_reader_funnel_does_not_require_immediate_title_payoff_or_fixed_three_sentence_formula():
    hooks = _policy()["hooks"]
    assert hooks["title_promise_integrity_required"] is True
    assert hooks["title_opening_payoff_required"] is False
    assert hooks["immediate_title_payoff_is_optional"] is True
    assert hooks["first_three_sentences_required"] is False
    assert hooks["early_reader_orientation_required"] is True
    assert hooks["opening_strategy_flexible"] is True
    assert "delayed_nut_graf" in hooks["opening_strategy_examples"]


def test_deep_numbered_navigation_is_encouraged_generously_for_real_branches():
    style = _policy()["style"]
    assert style["numbering_encouraged"] is True
    assert style["deep_numbered_navigation_required_when_branching"] is True
    assert style["deep_numbered_navigation_preference"] == "USE_GENEROUSLY_WHEN_REAL_LAYERS_OR_PARALLEL_BRANCHES_EXIST"


def test_company_comparison_may_be_primary_focus_but_remains_non_actionable():
    policy = _policy()
    assert policy["editorial"]["company_comparison_may_be_primary_focus"] is True
    assert policy["finance_compliance"]["company_comparison_may_be_primary_analytical_focus"] is True
    assert policy["finance_compliance"]["company_comparison_must_remain_non_actionable"] is True


def test_a_share_names_are_automatic_bold_layer_and_semantic_skim_path_still_required():
    policy = _policy()
    assert policy["word"]["auto_bold_company_names"] is True
    assert policy["word"]["auto_bold_scope"] == "A_SHARE_NAMES_SUPPLIED_BY_ARTICLE_DOCUMENT"
    assert policy["style"]["bold_skim_path_required"] is True


def test_concise_risk_has_no_fixed_minimum_character_quota_in_policy_or_schema():
    risk = _policy()["risk_disclaimer"]
    assert risk["min_body_chars"] == 0
    assert risk["concise_complete_preferred"] is True
    assert risk["semantic_completeness_required"] is True

    payload = ArticlePayload(
        title="测试",
        blocks=[
            {"kind": "lead", "text": "**事实**发生变化。"},
            {"kind": "h1", "text": "正文"},
            {"kind": "body", "text": "**比较**需要继续验证，**边界**保持明确。"},
        ],
        risk_disclaimer="需求与业绩可能变化，本文不构成投资建议。",
        stock_names=[],
        skim_path_anchors=["事实", "比较", "边界"],
    )
    assert payload.risk_disclaimer.startswith("需求")


def test_research_rule_is_domain_general_evidence_stage_integrity_not_ai_specific():
    research = _policy()["research"]
    assert research["evidence_stage_non_escalation_required"] is True
    principle = research["evidence_stage_non_escalation_principle"]
    assert "technology/product/capacity/order/delivery/revenue/profit/cash-flow" in principle
    assert "AI" not in principle


def test_audit_defaults_to_complete_applicable_writing_contract():
    audit = _policy()["audit"]
    assert audit["all_applicable_writing_requirements_default_coverage"] is True
    assert audit["special_surface_or_mode_na_must_be_explicit"] is True
