from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from financial_writing_agent.plugin_server import _publicize
from financial_writing_agent.schemas import (
    CompanyFinding,
    EvidenceItem,
    HeadlineCandidate,
    HeadlinePackage,
    HookAuditDecision,
    MarketExplanationHypothesis,
    ResearchPackage,
    StyleAuditDecision,
)


def _headline(title: str) -> HeadlineCandidate:
    return HeadlineCandidate(
        title=title,
        angle="事件变化",
        target_reader="关注盈利与资产定价的财经读者",
        finance_relevance="影响盈利预期",
        target_reader_click_reason="价格和利润传导存在尚未厘清的兑现差异",
        broader_finance_relevance="供需和利润变化具有跨行业资产定价含义",
        primary_gap="市场仍未充分区分",
        promised_payoff="解释利润兑现与市场选择的差异",
        cognitive_load="low",
        wechat_search_terms=["行业关键词"],
        search_evidence_refs=["wechat-search-current-signal"],
    )


def _base_research_kwargs():
    return {
        "topic": "测试题材",
        "chronology": ["事件发生"],
        "what_changed": ["预期发生变化"],
        "industry_chain": ["上游→下游"],
        "transmission_chain": ["事件→订单→利润"],
        "evidence_ledger": [
            EvidenceItem(claim="公司存在业务相关性", source="公司公告", confidence="high", core_safe=True)
        ],
        "counterevidence": ["市场交易强度不能证明基本面因果"],
        "provisional_theses": ["需要区分经济受益与市场选择"],
        "source_boundary": "公开信息",
        "cognition": {
            "concept_map": ["测试概念"],
            "industry_logic": ["订单向利润传导"],
        },
        "coverage": {
            "sweeps_completed": 2,
            "coverage_status": "SATURATED",
            "material_new_items_last_sweep": 0,
            "concept_coverage": "主要概念已覆盖",
            "company_coverage": "主要公司已覆盖",
            "source_diversity": "公告与市场数据",
            "stop_reason": "第二轮未发现重要新增",
        },
    }


def test_stage_schema_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        EvidenceItem(claim="事实", source="公开来源", unexpected_field="must not be silently ignored")


def test_headline_candidates_cannot_hide_duplicates():
    with pytest.raises(ValidationError):
        HeadlinePackage(
            finance_deep_candidates=[_headline("同一个标题"), _headline("同一个标题")],
            finance_deep_selected="同一个标题",
        )


def test_headline_candidate_requires_reader_fit_payoff_and_current_search_evidence():
    with pytest.raises(ValidationError):
        HeadlineCandidate(
            title="标题",
            angle="事件",
            target_reader="财经读者",
            finance_relevance="利润",
            target_reader_click_reason="有未解释的利润差异",
            primary_gap="信息差",
            promised_payoff="解释差异",
            cognitive_load="low",
            wechat_search_terms=[],
            search_evidence_refs=[],
        )


def test_cross_industry_relevance_is_optional_not_universal_title_requirement():
    candidate = HeadlineCandidate(
        title="行业订单变化，利润兑现为什么分化",
        angle="订单与利润",
        target_reader="该行业及相关产业链财经读者",
        finance_relevance="影响订单与利润兑现",
        target_reader_click_reason="同一催化下公司兑现速度不同",
        broader_finance_relevance="",
        primary_gap="谁能更快兑现",
        promised_payoff="区分订单、利润与验证条件",
        cognitive_load="low",
        wechat_search_terms=["行业订单"],
        search_evidence_refs=["wechat-current"],
    )
    assert candidate.broader_finance_relevance == ""


def test_reader_funnel_audit_pass_requires_every_rubric_item_pass():
    with pytest.raises(ValidationError):
        HookAuditDecision(
            status="PASS",
            evidence=["final title and first three sentences inspected"],
            search_terms_checked=["关键词"],
            search_evidence_refs=["current-search-ref"],
            rubric={
                "audience_promise_fit": "PASS",
                "headline_information_value": "PASS",
                "headline_curiosity_balance": "PASS",
                "title_wechat_search_intent": "PASS",
                "opening_three_sentence_retention": "REVISE",
                "continuation_flow": "PASS",
                "completion_payoff": "PASS",
                "title_opening_payoff": "PASS",
            },
        )


def test_supported_market_explanation_requires_evidence_refs():
    with pytest.raises(ValidationError):
        MarketExplanationHypothesis(
            mechanism="注意力与订单失衡共同推动短期价格发现",
            confidence="SUPPORTED_MECHANISM",
            applies_to=["测试股份"],
            evidence_refs=[],
        )


def test_company_universe_requires_market_explanation_map():
    kwargs = _base_research_kwargs()
    kwargs["universe"] = [
        CompanyFinding(
            name="测试股份",
            relevance="存在业务相关性",
            exposure_type="DIRECT_BUSINESS",
            benefit_path=["事件→订单"],
        )
    ]
    with pytest.raises(ValidationError):
        ResearchPackage(**kwargs)


def test_market_explanation_requires_competing_hypotheses_and_epistemic_discipline():
    kwargs = _base_research_kwargs()
    kwargs["universe"] = [
        CompanyFinding(
            name="测试股份",
            relevance="存在业务相关性",
            exposure_type="DIRECT_BUSINESS",
            benefit_path=["事件→订单"],
            sensitivity_basis=["业务暴露更直接"],
            market_selection_signals=["成交活跃"],
            continuation_support=["订单继续确认"],
            reversal_risks=["注意力退潮"],
        )
    ]
    kwargs["market_explanation"] = {
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
    package = ResearchPackage(**kwargs)
    assert len(package.market_explanation.hypotheses_considered) == 2
    assert package.market_explanation.hypotheses_considered[1].confidence == "PLAUSIBLE_INTERPRETATION"


def test_authorial_prose_pass_requires_all_9_dimensions():
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
    decision = StyleAuditDecision(status="PASS", evidence=["逐段复核最终正文九项作者性标准"], rubric=rubric)
    assert decision.status == "PASS"
    with pytest.raises(ValidationError):
        StyleAuditDecision(
            status="PASS",
            evidence=["证据不足"],
            rubric={**rubric, "uncertainty_rhetoric_calibration": "REVISE"},
        )


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
