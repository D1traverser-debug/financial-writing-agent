from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from financial_writing_agent.checks import (
    analyze_template_scaffolding,
    check_deep_company_grounding,
    check_payload_navigation,
)
from financial_writing_agent.plugin_server import _publicize
from financial_writing_agent.schemas import (
    ArticlePayload,
    AuditProvenance,
    CompanyFinding,
    EvidenceItem,
    GateDecision,
    HeadlineCandidate,
    HeadlinePackage,
    HookAuditDecision,
    MarketExplanationHypothesis,
    ResearchPackage,
    StyleAuditDecision,
)


ANGLE_FAMILIES = [
    "hard_fact",
    "profit_orders",
    "supply_demand",
    "company_divergence",
    "policy_transmission",
    "expectation_gap",
    "global_comparison",
    "validation_risk",
]


def _headline(title: str, family: str = "hard_fact") -> HeadlineCandidate:
    return HeadlineCandidate(
        title=title,
        angle="事件变化",
        angle_family=family,
        target_reader="关注盈利与资产定价的财经读者",
        finance_relevance="影响盈利预期",
        target_reader_click_reason="价格和利润传导存在尚未厘清的兑现差异",
        broader_finance_relevance="",
        primary_gap="市场仍未充分区分",
        promised_payoff="解释利润兑现差异",
        cognitive_load="low",
        wechat_search_terms=["行业关键词"],
        search_evidence_refs=["wechat-search-current-signal"],
    )


def _headline_pool(*, duplicate: bool = False, narrow_families: bool = False):
    items = []
    for i in range(8):
        title = "同一个标题" if duplicate and i in {0, 1} else f"标题{i + 1}：事件变化与兑现差异"
        family = "hard_fact" if narrow_families else ANGLE_FAMILIES[i]
        items.append(_headline(title, family))
    return items


def _company(name: str = "测试股份", materiality: str = "MATERIAL"):
    return CompanyFinding(
        name=name,
        value_chain_class="核心设备",
        materiality=materiality,
        relevance="存在业务相关性",
        exposure_type="DIRECT_BUSINESS",
        benefit_path=["事件→订单"],
        sensitivity_basis=["业务暴露更直接"],
    )


def _universe_coverage(names=None, *, recall_sources=None):
    names = names or ["测试股份"]
    return {
        "status": "COMPLETE",
        "classes": [
            {
                "class_name": "核心设备",
                "economic_role": "设备订单转化",
                "included_companies": names,
                "excluded_companies": [],
                "unresolved_candidates": [],
                "source_refs": ["industry-map-1"],
            }
        ],
        "recall_sources": recall_sources or ["StockBase", "official-company-search"],
        "exclusions": [],
        "missing_classes": [],
        "stop_reason": "已按产业链类别完成召回与排除对账",
    }


def _base_research_kwargs(scope: str = "NOT_MATERIAL", *, names=None):
    names = names or ["测试股份"]
    return {
        "topic": "测试题材",
        "chronology": ["事件发生"],
        "what_changed": ["预期发生变化"],
        "industry_chain": ["上游→核心设备→下游"],
        "transmission_chain": ["事件→订单→利润"],
        "universe": [_company(name) for name in names],
        "universe_coverage": _universe_coverage(names),
        "market_explanation_scope": scope,
        "market_explanation_scope_reason": "只比较产业与盈利兑现" if scope == "NOT_MATERIAL" else "文章需要解释个股价格选择",
        "evidence_ledger": [EvidenceItem(claim="公司存在业务相关性", source="公司公告", confidence="high", core_safe=True)],
        "counterevidence": ["市场交易强度不能证明基本面因果"],
        "provisional_theses": ["需要区分经济受益强弱"],
        "source_boundary": "公开信息",
        "cognition": {"concept_map": ["测试概念"], "industry_logic": ["订单向利润传导"]},
        "coverage": {
            "sweeps_completed": 2,
            "coverage_status": "SATURATED",
            "material_new_items_last_sweep": 0,
            "concept_coverage": "主要概念已覆盖",
            "company_coverage": "按产业链类别完成公司召回",
            "source_diversity": "StockBase、公告与行业资料",
            "stop_reason": "完成类别级召回与排除对账后第二轮未发现重要新增",
        },
    }


def _market_map():
    return {
        "activation_reason": "文章讨论个股价格反应",
        "concept_subtheme_map": ["主概念→细分→公司"],
        "economic_benefit_dimensions": ["业务暴露", "利润敏感度", "兑现时间"],
        "cross_sectional_selection_dimensions": ["注意力", "流动性", "预期差"],
        "hypotheses_considered": [
            {
                "mechanism": "基本面信息扩散",
                "confidence": "SUPPORTED_MECHANISM",
                "applies_to": ["测试股份"],
                "evidence_refs": ["公告-1", "市场数据-1"],
                "counterevidence": ["同行未同步上涨"],
            },
            {
                "mechanism": "注意力与流动性价格压力",
                "confidence": "PLAUSIBLE_INTERPRETATION",
                "applies_to": ["测试股份"],
                "evidence_refs": ["成交数据-1"],
                "counterevidence": ["无法识别投资者类型"],
            },
        ],
        "why_not_evidence": ["另一家公司基本面相关但缺乏同等注意力/流动性证据"],
        "continuation_conditions": ["后续基本面确认"],
        "reversal_conditions": ["仅注意力驱动且基本面不跟进"],
        "unresolved_questions": ["无法证明单一主导原因"],
    }


def _independent_provenance(reviewer="judge", author="writer"):
    return AuditProvenance(
        assurance="INDEPENDENT_EXECUTOR",
        reviewer_identity=reviewer,
        author_identity=author,
        execution_ref="task:stage:judge",
    )


def _deep_payload(*, include_second=True, numbered=True, monitoring_has_stock=True):
    blocks = [
        {"kind": "lead", "text": "**订单变化**正在进入公司层面的兑现比较。"},
        {"kind": "h1", "text": "一、产业链开始进入订单兑现阶段"},
    ]
    if numbered:
        blocks.extend(
            [
                {"kind": "h2", "text": "（1）核心设备先看订单"},
                {"kind": "body", "text": "测试股份的订单变化需要和收入确认一起看。"},
                {"kind": "h2", "text": "（2）同类公司需要横向比较"},
                {"kind": "body", "text": "另一股份的业务阶段不同，不能只看概念标签。" if include_second else "同类公司业务阶段不同。"},
                {"kind": "h2", "text": "（3）兑现节奏决定利润弹性"},
                {"kind": "body", "text": "**利润弹性**取决于交付、价格和成本。"},
            ]
        )
    else:
        long_text = ("测试股份与另一股份需要比较。" if include_second else "测试股份需要比较。") * 180
        blocks.append({"kind": "body", "text": f"**利润弹性**需要拆解。{long_text}"})
    blocks.extend(
        [
            {"kind": "h1", "text": "二、后续验证信号要落到公司"},
            {
                "kind": "body",
                "text": "测试股份要看订单转收入；另一股份要看交付节奏。**验证边界**由公司公告继续确认。"
                if monitoring_has_stock
                else "后续看招标、交付和收入确认。**验证边界**由公告继续确认。",
            },
        ]
    )
    return ArticlePayload(
        title="测试文章",
        blocks=blocks,
        risk_disclaimer="本文基于公开信息进行行业与公司研究，仅用于财经信息交流，不构成投资建议或收益承诺。政策、需求、订单、竞争格局与公司业绩均可能变化，请以最新公告为准并独立判断。",
        stock_names=["测试股份", "另一股份"],
        skim_path_anchors=["订单变化", "利润弹性", "验证边界"],
    )


def test_stage_schema_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        EvidenceItem(claim="事实", source="公开来源", unexpected_field="must not be silently ignored")


def test_headline_candidates_cannot_hide_duplicates():
    with pytest.raises(ValidationError):
        HeadlinePackage(
            finance_deep_candidates=_headline_pool(duplicate=True),
            finance_deep_selected="同一个标题",
        )


def test_headline_pool_requires_multiple_real_angle_families():
    with pytest.raises(ValidationError):
        HeadlinePackage(
            finance_deep_candidates=_headline_pool(narrow_families=True),
            finance_deep_selected="标题1：事件变化与兑现差异",
        )


def test_headline_candidate_requires_reader_fit_payoff_and_current_search_evidence():
    with pytest.raises(ValidationError):
        HeadlineCandidate(
            title="标题",
            angle="事件",
            angle_family="hard_fact",
            target_reader="财经读者",
            finance_relevance="利润",
            target_reader_click_reason="有未解释的利润差异",
            primary_gap="信息差",
            promised_payoff="解释差异",
            cognitive_load="low",
            wechat_search_terms=[],
            search_evidence_refs=[],
        )


def test_cross_industry_relevance_is_optional():
    assert _headline("行业订单变化，利润兑现为什么分化").broader_finance_relevance == ""


def test_universe_company_must_be_reconciled_to_class_ledger():
    kwargs = _base_research_kwargs(names=["测试股份", "另一股份"])
    kwargs["universe_coverage"] = _universe_coverage(["测试股份"])
    with pytest.raises(ValidationError):
        ResearchPackage(**kwargs)


def test_universe_recall_requires_two_materially_different_sources():
    kwargs = _base_research_kwargs()
    kwargs["universe_coverage"] = _universe_coverage(["测试股份"], recall_sources=["同一来源"])
    with pytest.raises(ValidationError):
        ResearchPackage(**kwargs)


def test_deep_company_guard_rejects_silent_material_company_omission():
    research = ResearchPackage(**_base_research_kwargs(names=["测试股份", "另一股份"]))
    payload = _deep_payload(include_second=False, monitoring_has_stock=False)
    errors = check_deep_company_grounding(payload, research)
    assert any("另一股份" in error for error in errors)


def test_deep_monitoring_section_must_map_signals_to_stocks():
    research = ResearchPackage(**_base_research_kwargs(names=["测试股份", "另一股份"]))
    payload = _deep_payload(monitoring_has_stock=False)
    errors = check_deep_company_grounding(payload, research)
    assert any("monitoring/validation section" in error for error in errors)


def test_deep_navigation_guard_rejects_long_unstructured_article():
    payload = _deep_payload(numbered=False)
    errors = check_payload_navigation(payload, deep=True)
    assert errors


def test_template_cluster_guard_flags_repeated_ai_staging():
    text = (
        "真正的拐点不是装机，而是订单。"
        "如果只看装机，就会错过变化。这正是最值得写清楚的地方。"
        "真正的变化不在数据，而在交付。"
        "如果只看收入，也会滞后。这正是核心在于订单的原因。"
        "真正的受益不是概念，而是兑现。"
    )
    report = analyze_template_scaffolding(text)
    assert report["requires_revise"] is True


def test_reader_funnel_revise_requires_repair_target():
    rubric = {
        "audience_promise_fit": "PASS",
        "headline_information_value": "PASS",
        "headline_curiosity_balance": "PASS",
        "headline_strategy_diversity": "PASS",
        "title_wechat_search_intent": "PASS",
        "opening_three_sentence_retention": "REVISE",
        "continuation_flow": "PASS",
        "completion_payoff": "PASS",
        "title_opening_payoff": "PASS",
    }
    with pytest.raises(ValidationError):
        HookAuditDecision(
            status="REVISE",
            evidence=["opening inspected"],
            search_terms_checked=["关键词"],
            search_evidence_refs=["current-search-ref"],
            rubric=rubric,
            revision_notes=["重写前三句"],
        )
    decision = HookAuditDecision(
        status="REVISE",
        evidence=["opening inspected"],
        search_terms_checked=["关键词"],
        search_evidence_refs=["current-search-ref"],
        rubric=rubric,
        revision_target="DRAFT",
        revision_notes=["重写前三句"],
    )
    assert decision.revision_target == "DRAFT"


def test_chat_self_review_cannot_pass_semantic_audits():
    hook_rubric = {
        "audience_promise_fit": "PASS",
        "headline_information_value": "PASS",
        "headline_curiosity_balance": "PASS",
        "headline_strategy_diversity": "PASS",
        "title_wechat_search_intent": "PASS",
        "opening_three_sentence_retention": "PASS",
        "continuation_flow": "PASS",
        "completion_payoff": "PASS",
        "title_opening_payoff": "PASS",
    }
    with pytest.raises(ValidationError):
        HookAuditDecision(
            status="PASS",
            evidence=["inspected"],
            search_terms_checked=["关键词"],
            search_evidence_refs=["ref"],
            rubric=hook_rubric,
        )
    with pytest.raises(ValidationError):
        GateDecision(status="PASS", evidence=["self-reviewed"])


def test_supported_market_explanation_requires_evidence_refs():
    with pytest.raises(ValidationError):
        MarketExplanationHypothesis(
            mechanism="注意力与订单失衡共同推动短期价格发现",
            confidence="SUPPORTED_MECHANISM",
            applies_to=["测试股份"],
            evidence_refs=[],
        )


def test_company_universe_does_not_by_itself_activate_market_explanation():
    package = ResearchPackage(**_base_research_kwargs("NOT_MATERIAL"))
    assert package.market_explanation_scope == "NOT_MATERIAL"
    assert package.market_explanation is None


def test_required_market_explanation_scope_requires_map():
    kwargs = _base_research_kwargs("REQUIRED")
    with pytest.raises(ValidationError):
        ResearchPackage(**kwargs)


def test_not_material_scope_forbids_market_explanation_map():
    kwargs = _base_research_kwargs("NOT_MATERIAL")
    kwargs["market_explanation"] = _market_map()
    with pytest.raises(ValidationError):
        ResearchPackage(**kwargs)


def test_market_explanation_requires_competing_hypotheses_and_epistemic_discipline():
    kwargs = _base_research_kwargs("REQUIRED")
    kwargs["market_explanation"] = _market_map()
    package = ResearchPackage(**kwargs)
    assert len(package.market_explanation.hypotheses_considered) == 2
    assert package.market_explanation.hypotheses_considered[1].confidence == "PLAUSIBLE_INTERPRETATION"


def test_authorial_prose_pass_requires_independent_executor_and_all_9_dimensions():
    rubric = {
        "fidelity_and_responsibility": "PASS",
        "semantic_contribution": "PASS",
        "argument_progression": "PASS",
        "reader_calibration": "PASS",
        "authorial_selectivity": "PASS",
        "evidence_specificity": "PASS",
        "structural_rhythm_naturalness": "PASS",
        "template_redundancy_control": "PASS",
        "uncertainty_rhetoric_calibration": "PASS",
    }
    decision = StyleAuditDecision(
        status="PASS",
        evidence=["逐段复核九项作者性标准"],
        rubric=rubric,
        provenance=_independent_provenance("prose-judge", "writer"),
    )
    assert decision.status == "PASS"
    with pytest.raises(ValidationError):
        StyleAuditDecision(status="PASS", evidence=["self"], rubric=rubric)

    revised = StyleAuditDecision(
        status="REVISE",
        evidence=["发现模板重复"],
        rubric={**rubric, "template_redundancy_control": "REVISE"},
        revision_target="DRAFT",
        revision_notes=["重写相关段落"],
    )
    assert revised.revision_target == "DRAFT"


def test_public_artifacts_never_expose_server_local_paths():
    raw = {
        "task_id": "task-1",
        "status": "COMPLETE",
        "current_stage": "COMPLETE",
        "topic": "测试",
        "prompt_preview": "测试",
        "content_mode": "FORMAL_ARTICLE",
        "distribution_mode": "FINANCE_DEEP",
        "delivery_channel": "WORD_FILE_ONLY",
        "required_outputs": ["FINANCE_DEEP_DOCX"],
        "gate_status": {},
        "blocked_reason": None,
        "blocked_resume_stage": None,
        "learning_sample_count": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "next_action": "deliver",
        "trace_tail": [{"secret": "internal"}],
        "artifacts": {
            "FINANCE_DEEP_DOCX": {
                "path": "/data/runs/task-1/FINANCE_DEEP.docx",
                "exists": True,
                "sha256": "abc",
            }
        },
    }
    public = _publicize(raw)
    artifact = public["artifacts"]["FINANCE_DEEP_DOCX"]
    assert "path" not in artifact
    assert artifact["resource_uri"] == "writing-docx://task-1/FINANCE_DEEP_DOCX"
    assert public.get("trace_tail") is None
