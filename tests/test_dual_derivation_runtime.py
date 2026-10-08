import pytest

from financial_writing_agent import runtime_service
from financial_writing_agent.controller import WorkflowController
from financial_writing_agent.engine import WritingEngine
from financial_writing_agent.models import Stage
from financial_writing_agent.store import SQLiteStateStore


RISK = (
    "本文基于公开信息进行研究，仅用于财经信息交流，不构成投资建议或收益承诺。"
    "产业、订单、业绩、政策和市场交易状态均可能变化，请以最新正式披露为准并独立判断。"
)


def _install_runtime(monkeypatch, tmp_path):
    store = SQLiteStateStore(tmp_path / "dual-runtime.db")
    engine = WritingEngine(store)
    controller = WorkflowController(engine)
    monkeypatch.setattr(runtime_service, "store", store)
    monkeypatch.setattr(runtime_service, "engine", engine)
    monkeypatch.setattr(runtime_service, "controller", controller)
    return store


def _research():
    return {
        "topic": "催化后的公司分化",
        "chronology": ["事件发生", "公司披露进入可验证阶段"],
        "what_changed": ["核心事实"],
        "industry_chain": ["上游供给", "中游制造", "下游需求"],
        "transmission_chain": ["催化→需求变化→订单/利润预期→市场选择"],
        "universe": [
            {
                "name": "甲公司",
                "ticker": "000001",
                "relevance": "直接业务暴露",
                "business_stage": "订单验证阶段",
                "positive_evidence": ["已有业务验证"],
                "negative_evidence": ["利润兑现仍有限"],
                "why_this": "产业位置和订单验证更直接",
                "why_not": ["估值消化仍需利润兑现"],
                "market_role": "核心比较对象",
                "short_term_role": "前排",
            },
            {
                "name": "乙公司",
                "ticker": "000002",
                "relevance": "间接受益",
                "business_stage": "预期阶段",
                "positive_evidence": ["存在产业链关联"],
                "negative_evidence": ["订单验证弱于甲公司"],
                "why_this": "具备弹性",
                "why_not": ["兑现证据较弱"],
                "market_role": "对照公司",
                "short_term_role": "跟随",
            },
        ],
        "evidence_ledger": [
            {
                "claim": "核心事实",
                "source": "公司正式公告",
                "evidence_type": "official",
                "confidence": "high",
                "core_safe": True,
                "verification_status": "SINGLE_SOURCE_ATTRIBUTED",
                "source_group": "issuer-origin",
                "allowed_wording": "据公司正式公告披露，核心事实已经发生",
            }
        ],
        "counterevidence": ["乙公司兑现证据仍弱"],
        "unresolved_gaps": [],
        "provisional_theses": ["同一催化下，甲公司的当前兑现位置强于乙公司"],
        "source_boundary": "公司正式公告已读；未把未核实传闻纳入核心事实",
        "cognition": {
            "prior_knowledge_refs": [],
            "concept_map": ["催化", "订单兑现", "公司分化"],
            "adjacent_or_competing_concepts": ["纯题材映射"],
            "industry_logic": ["实际订单/利润兑现决定公司差异"],
            "short_term_market_structure": ["甲公司当前前排，乙公司跟随"],
            "knowledge_conflicts": [],
        },
        "coverage": {
            "sweeps_completed": 2,
            "coverage_status": "SATURATED",
            "material_new_items_last_sweep": 0,
            "concept_coverage": "主概念、相邻概念和兑现路径已覆盖",
            "company_coverage": "甲乙两个材料性候选已完成相对比较",
            "source_diversity": "正式披露与独立市场检查路径",
            "excluded_scope": [],
            "stop_reason": "第二轮未发现改变当前排序的材料性公司或事实",
        },
    }


def _topic_dna():
    return {
        "new_fact": "核心事实",
        "main_transmission": "催化通过订单兑现影响利润预期",
        "likely_reader_misjudgment": "把概念关联等同于兑现强度",
        "core_contradictions": ["同一催化下兑现阶段不同"],
        "comparison_dimensions": ["兑现阶段", "市场角色"],
        "compression_candidates": ["重复行业背景"],
        "finance_wide_question": "同一催化下为什么公司表现和兑现能力分化",
    }


def _section(title, conclusion, gap, payoff):
    return {
        "h1_title": title,
        "directional_conclusion": conclusion,
        "reader_gap": gap,
        "payoff_requirement": payoff,
        "logical_blocks": ["连续论证"],
        "h3_required_h2_indexes": [],
    }


def _deep_plan():
    selected = {
        "name": "兑现分化主线",
        "rationale": "先解释催化，再比较公司兑现与市场位置",
        "sections": ["催化为什么不是平均受益", "甲乙公司的兑现差异"],
    }
    alternate = {
        "name": "公司比较主线",
        "rationale": "直接以公司差异进入产业逻辑",
        "sections": ["甲公司强在哪里", "乙公司差在哪里"],
    }
    return {
        "topic_dna": _topic_dna(),
        "finance_deep": {
            "candidates": [selected, alternate],
            "selected_structure": selected,
            "emphasis": ["完整因果链", "公司相对判断"],
            "side_focus_statement": "聚焦能改变当前公司排序的兑现证据",
            "company_selection_basis": ["兑现阶段", "市场角色"],
            "section_expectations": [
                _section(
                    "催化为什么不是平均受益",
                    "产业催化不会平均映射到所有概念股",
                    "真正决定差异的变量是什么",
                    "用产业位置和兑现阶段解释分化",
                ),
                _section(
                    "甲乙公司的兑现差异",
                    "甲公司当前兑现位置强于乙公司",
                    "差距来自业务还是市场角色",
                    "用订单验证、负面证据和市场角色完成比较",
                ),
            ],
        },
    }


def _broad_plan():
    selected = {
        "name": "同一催化两种结果",
        "rationale": "用公司分化降低进入门槛",
        "sections": ["同一催化为何走出两种结果", "真正兑现的是谁"],
    }
    alternate = {
        "name": "结果先行",
        "rationale": "先给分化结果再解释原因",
        "sections": ["为什么不能只看概念", "兑现差异如何形成"],
    }
    return {
        "topic_dna": _topic_dna(),
        "finance_broad": {
            "candidates": [selected, alternate],
            "selected_structure": selected,
            "emphasis": ["低门槛", "结果反差", "引流钩子"],
            "side_focus_statement": "只保留能解释甲乙分化的主链",
            "company_selection_basis": ["兑现阶段", "市场角色"],
            "section_expectations": [
                _section(
                    "同一催化为何走出两种结果",
                    "同一题材并不等于同一兑现强度",
                    "为什么市场没有平均选择所有公司",
                    "用甲乙公司的兑现差异解释结果",
                ),
                _section(
                    "真正兑现的是谁",
                    "甲公司当前兑现位置更靠前",
                    "这个结论靠什么而不是靠概念标签",
                    "用已确认业务与当前角色完成判断",
                ),
            ],
        },
    }


def _headlines(mode):
    prefix = "深" if mode == "deep" else "广"
    angles = ["反差", "结果", "因果", "公司分化", "身位", "兑现阶段", "数字锚点", "误区纠正"]
    gaps = ["谁在兑现", "为什么分化", "谁更靠前", "概念为何失真"]
    candidates = [
        {
            "title": f"{prefix}标题{i+1}",
            "angle": angle,
            "finance_relevance": "决定当前公司比较和利润预期",
            "factual_anchor": "核心事实",
            "primary_gap": gaps[i % len(gaps)],
            "opening_payoff": "开头直接给出当前分化判断并开始解释原因",
            "cognitive_load": "low" if i < 4 else "medium",
        }
        for i, angle in enumerate(angles)
    ]
    if mode == "deep":
        return {"finance_deep_candidates": candidates, "finance_deep_selected": "深标题1"}
    return {"finance_broad_candidates": candidates, "finance_broad_selected": "广标题1"}


def _deep_draft():
    return {
        "finance_deep": {
            "title": "深标题1",
            "blocks": [
                {"kind": "lead", "text": "核心事实已经改变了比较基准：当前不是所有相关公司都处在同一个兑现阶段。"},
                {"kind": "h1", "text": "催化为什么不是平均受益"},
                {"kind": "body", "text": "产业链位置不同，催化传到订单和利润的速度就不同。甲公司已有更直接的业务验证，乙公司仍更多停留在预期层。"},
                {"kind": "h1", "text": "甲乙公司的兑现差异"},
                {"kind": "body", "text": "当前证据下，甲公司兑现位置更靠前：业务验证更直接，市场角色也更前排；乙公司有弹性，但订单兑现证据较弱，因此当前排序低于甲公司。"},
            ],
            "risk_disclaimer": RISK,
            "stock_names": ["甲公司", "乙公司"],
        }
    }


def _broad_draft(*, stocks=None, extra=""):
    return {
        "finance_broad": {
            "title": "广标题1",
            "blocks": [
                {"kind": "lead", "text": "同一个催化，为什么两家公司走出两种结果？差别不在概念标签，而在兑现位置。"},
                {"kind": "h1", "text": "同一催化为何走出两种结果"},
                {"kind": "body", "text": "甲公司的业务验证更直接，乙公司仍偏预期。" + extra},
                {"kind": "h1", "text": "真正兑现的是谁"},
                {"kind": "body", "text": "当前甲公司兑现位置更靠前，这个排序来自业务验证和相对市场角色，而不是题材热度。"},
            ],
            "risk_disclaimer": RISK,
            "stock_names": stocks if stocks is not None else ["甲公司"],
        }
    }


def test_dual_runtime_forces_deep_first_then_broad_derivation(monkeypatch, tmp_path):
    store = _install_runtime(monkeypatch, tmp_path)
    started = runtime_service.start_writing_task(
        prompt="根据催化全面研究后写财经深度版和大众引流版",
        visuals_enabled=False,
    )
    task_id = started["task_id"]
    assert started["current_stage"] == "RESEARCH"

    runtime_service.record_knowledge_context(task_id, "N_A", notes=["test has no connected durable store"])
    researched = runtime_service.submit_research(task_id, _research())
    assert researched["current_stage"] == "RESEARCH_AUDIT"
    editorial = runtime_service.submit_research_audit(
        task_id,
        {"status": "PASS", "evidence": ["universe, evidence and comparison depth are sufficient"]},
    )
    assert editorial["current_stage"] == "EDITORIAL"

    premature = _deep_plan()
    premature["finance_broad"] = _broad_plan()["finance_broad"]
    with pytest.raises(ValueError, match="must not pre-plan FINANCE_BROAD"):
        runtime_service.submit_editorial_plan(task_id, premature)

    titled = runtime_service.submit_editorial_plan(task_id, _deep_plan())
    assert titled["current_stage"] == "TITLE"
    drafted = runtime_service.submit_headlines(task_id, _headlines("deep"))
    assert drafted["current_stage"] == "DRAFT"

    broad_stage = runtime_service.submit_draft(task_id, _deep_draft())
    assert broad_stage["current_stage"] == "BROAD_DERIVATION"
    assert broad_stage["broad_derivation_phase"] == "EDITORIAL"
    assert broad_stage["gate_status"]["broad_derivation"] == "NOT_RUN"

    with pytest.raises(ValueError, match="current broad-derivation subphase"):
        runtime_service.submit_headlines(task_id, _headlines("broad"))

    broad_title_phase = runtime_service.submit_editorial_plan(task_id, _broad_plan())
    assert broad_title_phase["broad_derivation_phase"] == "TITLE"
    broad_draft_phase = runtime_service.submit_headlines(task_id, _headlines("broad"))
    assert broad_draft_phase["broad_derivation_phase"] == "DRAFT"

    with pytest.raises(ValueError, match="must not introduce new stocks"):
        runtime_service.submit_draft(task_id, _broad_draft(stocks=["甲公司", "丙公司"]))

    too_long = _broad_draft(extra="重复内容" * 200)
    with pytest.raises(ValueError, match="must be a compressed derivative"):
        runtime_service.submit_draft(task_id, too_long)

    audit_stage = runtime_service.submit_draft(task_id, _broad_draft())
    assert audit_stage["current_stage"] == "EDITORIAL_AUDIT"
    assert audit_stage["gate_status"]["broad_derivation"] == "PASS"

    state = store.load(task_id)
    assert state is not None
    assert state.stage == Stage.EDITORIAL_AUDIT
    receipt = state.working["dual_derivation_receipt"]
    assert receipt["broad_chars"] < receipt["deep_chars"]
    assert receipt["new_stock_names"] == []
    assert set(receipt["broad_stock_names"]).issubset(set(receipt["deep_stock_names"]))


def test_hook_diversity_rejects_superficial_candidate_set(monkeypatch, tmp_path):
    _install_runtime(monkeypatch, tmp_path)
    started = runtime_service.start_writing_task(prompt="测试标题钩子", visuals_enabled=False)
    task_id = started["task_id"]
    runtime_service.record_knowledge_context(task_id, "N_A", notes=["test"])
    runtime_service.submit_research(task_id, _research())
    runtime_service.submit_research_audit(task_id, {"status": "PASS", "evidence": ["ok"]})
    runtime_service.submit_editorial_plan(task_id, _deep_plan())

    shallow = _headlines("deep")
    for candidate in shallow["finance_deep_candidates"]:
        candidate["angle"] = "同一个角度"
        candidate["primary_gap"] = "同一个信息缺口"
    with pytest.raises(ValueError, match="lacks hook-angle diversity"):
        runtime_service.submit_headlines(task_id, shallow)
