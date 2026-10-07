import pytest

from financial_writing_agent.harness import freeze_acceptance_contract, validate_draft_against_acceptance
from financial_writing_agent.models import DistributionMode, GateStatus, TaskContract, WritingState
from financial_writing_agent.schemas import DraftPackage, EditorialPlan, HeadlinePackage


def _mode(prefix: str, sections: list[str]):
    selected = {
        "name": f"{prefix}-A",
        "rationale": "最贴合当前题材主矛盾",
        "sections": sections,
    }
    alternate = {
        "name": f"{prefix}-B",
        "rationale": "备用比较路径",
        "sections": [f"{prefix}备用一", f"{prefix}备用二"],
    }
    return {
        "candidates": [selected, alternate],
        "selected_structure": selected,
        "emphasis": ["核心因果链"],
        "side_focus_statement": f"{prefix}侧重点",
        "company_selection_basis": ["产业传导位置"],
        "outline_fingerprint_refs": ["recent-outline-1"],
        "outline_collision_notes": ["未发现高度重复"],
    }


def _headline(title: str):
    return {
        "title": title,
        "angle": "事实冲突",
        "finance_relevance": "利润与估值",
        "factual_anchor": "经核验的公告数字",
        "primary_gap": "谁真正兑现",
        "opening_payoff": "前三句交代变化、矛盾和判断收益",
        "cognitive_load": "low",
    }


def _risk():
    return (
        "本文基于公开信息进行研究，仅用于财经信息交流，不构成投资建议或收益承诺。"
        "相关政策、需求、价格、订单、竞争格局、公司业绩和市场环境均可能变化，请以最新披露为准并独立判断。"
    )


def _state() -> WritingState:
    state = WritingState(contract=TaskContract(prompt="双版本文章", distribution_mode=DistributionMode.DUAL))
    editorial = EditorialPlan.model_validate(
        {
            "topic_dna": {
                "new_fact": "事件出现新变化",
                "main_transmission": "需求变化传导到收入利润",
                "likely_reader_misjudgment": "把概念暴露等同于利润兑现",
                "core_contradictions": ["产业受益与市场选择并不重合"],
                "comparison_dimensions": ["兑现阶段", "客户与订单"],
                "compression_candidates": ["教材式背景"],
                "finance_wide_question": "利润兑现速度如何改变估值",
            },
            "finance_deep": _mode("deep", ["深度矛盾", "公司比较", "证伪条件"]),
            "finance_broad": _mode("broad", ["财经相关性", "利润传导"]),
        }
    )
    headlines = HeadlinePackage.model_validate(
        {
            "finance_deep_candidates": [_headline("深度版标题")],
            "finance_broad_candidates": [_headline("综合版标题")],
            "finance_deep_selected": "深度版标题",
            "finance_broad_selected": "综合版标题",
        }
    )
    state.working["editorial_plan"] = editorial.model_dump(mode="json")
    state.working["headlines"] = headlines.model_dump(mode="json")
    freeze_acceptance_contract(state)
    return state


def test_dual_acceptance_contract_freezes_independent_structures():
    state = _state()
    contract = state.working["acceptance_contract"]
    assert contract["finance_deep"]["expected_h1_count"] == 3
    assert contract["finance_broad"]["expected_h1_count"] == 2
    assert contract["finance_deep"]["selected_structure_name"] != contract["finance_broad"]["selected_structure_name"]
    assert state.gates["acceptance_contract"].status == GateStatus.PASS


def test_draft_must_match_frozen_title_and_h1_count():
    state = _state()
    draft = DraftPackage.model_validate(
        {
            "finance_deep": {
                "title": "深度版标题",
                "risk_disclaimer": _risk(),
                "blocks": [
                    {"kind": "lead", "text": "独立导读"},
                    {"kind": "h1", "text": "深度矛盾"},
                    {"kind": "body", "text": "正文一"},
                    {"kind": "h1", "text": "公司比较"},
                    {"kind": "body", "text": "正文二"},
                    {"kind": "h1", "text": "证伪条件"},
                    {"kind": "body", "text": "正文三"},
                ],
            },
            "finance_broad": {
                "title": "综合版标题",
                "risk_disclaimer": _risk(),
                "blocks": [
                    {"kind": "lead", "text": "独立导读"},
                    {"kind": "h1", "text": "财经相关性"},
                    {"kind": "body", "text": "正文一"},
                    {"kind": "h1", "text": "利润传导"},
                    {"kind": "body", "text": "正文二"},
                ],
            },
        }
    )
    evidence = validate_draft_against_acceptance(state, draft)
    assert any("FINANCE_DEEP" in item for item in evidence)
    assert any("FINANCE_BROAD" in item for item in evidence)

    bad = draft.model_copy(deep=True)
    bad.finance_broad.title = "临时改掉的标题"
    with pytest.raises(ValueError, match="frozen selected title"):
        validate_draft_against_acceptance(state, bad)
