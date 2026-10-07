import pytest

from financial_writing_agent.harness import (
    freeze_acceptance_contract,
    validate_draft_against_acceptance,
    validate_research_against_knowledge_context,
)
from financial_writing_agent.models import DistributionMode, GateStatus, TaskContract, WritingState
from financial_writing_agent.schemas import DraftPackage, EditorialPlan, HeadlinePackage, ResearchPackage


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


def _headline(title: str, anchor: str = "核心事实"):
    return {
        "title": title,
        "angle": "事实冲突",
        "finance_relevance": "利润与估值",
        "factual_anchor": anchor,
        "primary_gap": f"{title}对应的市场信息差",
        "opening_payoff": f"{title}前三句交代变化、矛盾和判断收益",
        "cognitive_load": "low",
    }


def _risk():
    return (
        "本文基于公开信息进行研究，仅用于财经信息交流，不构成投资建议或收益承诺。"
        "相关政策、需求、价格、订单、竞争格局、公司业绩和市场环境均可能变化，请以最新披露为准并独立判断。"
    )


def _research(prior_refs: list[str], source_boundary: str = "公开来源") -> ResearchPackage:
    return ResearchPackage.model_validate(
        {
            "topic": "测试主题",
            "chronology": ["事件发生"],
            "what_changed": ["口径变化"],
            "industry_chain": ["上游→中游→下游"],
            "transmission_chain": ["事件→需求→利润"],
            "universe": [],
            "evidence_ledger": [
                {
                    "claim": "核心事实",
                    "source": "原始公告",
                    "core_safe": True,
                    "verification_status": "SINGLE_SOURCE_ATTRIBUTED",
                    "allowed_wording": "据公司公告披露",
                }
            ],
            "counterevidence": [],
            "unresolved_gaps": [],
            "provisional_theses": ["待验证判断"],
            "source_boundary": source_boundary,
            "cognition": {
                "prior_knowledge_refs": prior_refs,
                "concept_map": ["核心概念"],
                "industry_logic": ["产业逻辑"],
            },
            "coverage": {
                "sweeps_completed": 2,
                "coverage_status": "SATURATED",
                "material_new_items_last_sweep": 0,
                "concept_coverage": "核心与相邻概念已覆盖",
                "company_coverage": "相关公司已扫描",
                "source_diversity": "公告与公开资料",
                "stop_reason": "第二轮无新增重大信息",
            },
        }
    )


def _state(headline_anchor: str = "核心事实") -> WritingState:
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
            "finance_deep_candidates": [_headline("深度版标题", headline_anchor)],
            "finance_broad_candidates": [_headline("综合版标题", headline_anchor)],
            "finance_deep_selected": "深度版标题",
            "finance_broad_selected": "综合版标题",
        }
    )
    state.working["research"] = _research([]).model_dump(mode="json")
    state.working["editorial_plan"] = editorial.model_dump(mode="json")
    state.working["headlines"] = headlines.model_dump(mode="json")
    freeze_acceptance_contract(state)
    return state


def test_knowledge_context_na_forbids_claimed_prior_refs():
    state = WritingState(contract=TaskContract(prompt="知识测试"))
    state.set_gate("knowledge_context", GateStatus.N_A, ["无可用知识库"])
    with pytest.raises(ValueError, match="must be empty"):
        validate_research_against_knowledge_context(state, _research(["kb://invented"]))


def test_knowledge_context_pass_forbids_unrecorded_prior_refs():
    state = WritingState(contract=TaskContract(prompt="知识测试"))
    state.working["knowledge_context_refs"] = ["kb://recorded"]
    state.set_gate("knowledge_context", GateStatus.PASS, ["kb://recorded"])
    with pytest.raises(ValueError, match="not recorded"):
        validate_research_against_knowledge_context(
            state,
            _research(["kb://recorded", "kb://invented"]),
        )

    evidence = validate_research_against_knowledge_context(state, _research(["kb://recorded"]))
    assert any("retrieved_refs=1" in item for item in evidence)
    assert any("reused_refs=1" in item for item in evidence)


def test_task_source_completion_requires_every_source_ref():
    state = WritingState(
        contract=TaskContract(
            prompt="根据两个来源写文章",
            source_refs=["source://one", "source://two"],
        )
    )
    state.set_gate("knowledge_context", GateStatus.N_A, ["无可用知识库"])
    research = _research([], source_boundary="[FULL] source://one")
    with pytest.raises(ValueError, match="source_boundary must account for every TaskContract source_ref"):
        validate_research_against_knowledge_context(state, research)


def test_task_source_completion_accepts_full_partial_unavailable_receipts():
    state = WritingState(
        contract=TaskContract(
            prompt="根据三个来源写文章",
            source_refs=["source://one", "source://two", "source://three"],
        )
    )
    state.set_gate("knowledge_context", GateStatus.N_A, ["无可用知识库"])
    research = _research(
        [],
        source_boundary=(
            "[FULL] source://one\n"
            "[PARTIAL] source://two — 正文被截断，已用可访问部分核边界\n"
            "[UNAVAILABLE] source://three — 原件不可访问，不能作为已读来源"
        ),
    )
    evidence = validate_research_against_knowledge_context(state, research)
    assert "task_source_refs=3; source_completion=accounted" in evidence


def test_headline_anchor_must_match_core_safe_research_claim():
    with pytest.raises(ValueError, match="headline factual_anchor must exactly match a core_safe"):
        _state(headline_anchor="不存在于研究证据中的标题锚点")


def test_dual_acceptance_contract_freezes_independent_structures_and_headline_promises():
    state = _state()
    contract = state.working["acceptance_contract"]
    assert contract["finance_deep"]["expected_h1_count"] == 3
    assert contract["finance_broad"]["expected_h1_count"] == 2
    assert contract["finance_deep"]["selected_structure_name"] != contract["finance_broad"]["selected_structure_name"]
    assert contract["finance_deep"]["headline_factual_anchor"] == "核心事实"
    assert contract["finance_deep"]["headline_primary_gap"] == "深度版标题对应的市场信息差"
    assert "前三句" in contract["finance_deep"]["headline_opening_payoff"]
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
