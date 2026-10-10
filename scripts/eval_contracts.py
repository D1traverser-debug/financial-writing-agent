from __future__ import annotations

import json
import tempfile
from pathlib import Path

from pydantic import ValidationError

from financial_writing_agent.checks import analyze_template_scaffolding
from financial_writing_agent.engine import WritingEngine
from financial_writing_agent.models import ArtifactKind, DeliveryChannel, DistributionMode, GateStatus, Stage, TaskContract
from financial_writing_agent.routing import build_task_contract
from financial_writing_agent.runner import AgentRuntime
from financial_writing_agent.schemas import AuditProvenance, CompanyFinding, GateDecision, HeadlineCandidate, HeadlinePackage, ModeEditorialPlan, ResearchPackage, StructureCandidate, StyleAuditDecision
from financial_writing_agent.store import SQLiteStateStore

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "evals" / "scenarios.json"
POLICY = ROOT / "config" / "policy.json"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def eval_e01() -> list[str]:
    contract = build_task_contract(prompt="根据这两个链接写文章", source_refs=["a", "b"])
    check(contract.delivery_channel == DeliveryChannel.WORD_FILE_ONLY, "E01 default delivery must be WORD_FILE_ONLY")
    check(ArtifactKind.AUDIT_DOCX in contract.required_outputs, "E01 audit report must be required")
    with tempfile.TemporaryDirectory() as td:
        runtime = AgentRuntime.with_sqlite(Path(td) / "state.db", executors={})
        state = runtime.start(contract)
        check(state.trace[0].event == "RUNTIME_STARTED", "E01 runtime must start before executor activity")
    return ["runtime starts first", "WORD_FILE_ONLY", "audit report required"]


def eval_e02() -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        store = SQLiteStateStore(Path(td) / "state.db")
        engine = WritingEngine(store)
        state = engine.start(TaskContract(prompt="继续昨天那篇"))
        state = engine.transition(state, Stage.RESEARCH, reason="test")
        state.set_gate("research_output", GateStatus.PASS, ["done"])
        store.save(state)
        loaded = store.load(state.contract.task_id)
        check(loaded is not None and loaded.stage == Stage.RESEARCH, "E02 checkpoint must reload at same stage")
        check(loaded.gates["research_output"].status == GateStatus.PASS, "E02 passed gates must survive reload")
    return ["checkpoint reload", "stage preserved", "passed gate preserved"]


def eval_e03() -> list[str]:
    contract = build_task_contract(prompt="这篇同时发雪球、韭研、头条、百家", target_platforms=["雪球", "韭研公社", "今日头条", "百家号"])
    check(contract.distribution_mode == DistributionMode.DUAL, "E03 mixed destinations must route DUAL")
    c1 = StructureCandidate(name="A", rationale="test", sections=["一", "二"])
    c2 = StructureCandidate(name="B", rationale="test2", sections=["一", "二"])
    deep = ModeEditorialPlan(coverage_policy="MATERIAL_COMPLETE", candidates=[c1, c2], selected_structure=c1, completeness_obligations=["event", "transmission", "counterevidence"], company_coverage_obligations=["all MATERIAL companies"])
    broad = ModeEditorialPlan(coverage_policy="SELECTIVE_TRAFFIC", candidates=[c1, c2], selected_structure=c1, core_contradictions=["profit timing"])
    check(not deep.core_contradictions and not deep.compression_candidates, "E03 deep plan must not select by contradictions/compression")
    check(deep.company_coverage_obligations, "E03 deep plan must carry company coverage obligations")
    check(broad.core_contradictions == ["profit timing"], "E03 broad plan may select core contradiction")
    return ["DUAL", "deep=MATERIAL_COMPLETE + company obligations", "broad=SELECTIVE_TRAFFIC"]


def eval_e06() -> list[str]:
    contract = build_task_contract(prompt="根据研报写，字数控制得短一点")
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check("word_count" not in contract.run_constraints, "E06 must not invent fixed word count")
    check(policy["editorial"]["finance_deep_material_complete"], "E06 deep material completeness must remain enabled")
    check(policy["editorial"]["finance_deep_representative_stock_shortcut_forbidden"], "E06 representative-stock shortcut must remain forbidden")
    return ["no fixed word-count anchor", "deep material completeness retained", "representative-stock shortcut forbidden"]


def eval_e07() -> list[str]:
    contract = build_task_contract(prompt="给我直接在聊天框看正文")
    check(contract.delivery_channel == DeliveryChannel.WORD_FILE_ONLY, "E07 publication content remains WORD_FILE_ONLY")
    check(all(kind.value != "CHAT_TEXT" for kind in contract.required_outputs), "E07 removed chat-text artifact must never be created")
    check(ArtifactKind.AUDIT_DOCX in contract.required_outputs, "E07 audit Word remains required")
    check(not hasattr(ArtifactKind, "CHAT_TEXT"), "E07 legacy CHAT_TEXT enum must remain deleted")
    return ["WORD_FILE_ONLY", "no legacy chat artifact enum/output", "audit Word required"]


def eval_e11() -> list[str]:
    contract = build_task_contract(prompt="Word已经写好了，直接发我")
    check(contract.delivery_channel == DeliveryChannel.WORD_FILE_ONLY, "E11 remains Word delivery")
    check(ArtifactKind.AUDIT_DOCX in contract.required_outputs, "E11 audit report remains mandatory")
    check(all("VISUAL" not in kind.value for kind in contract.required_outputs), "E11 must not invent visual outputs")
    return ["Word delivery", "audit report required", "no visual outputs"]


def eval_e12() -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        runtime = AgentRuntime.with_sqlite(Path(td) / "state.db", executors={})
        state = runtime.start(build_task_contract(prompt="来源抓不到但你先按常识写吧"))
        state = runtime.run(state)
        check(state.stage == Stage.BLOCKED, "E12 missing executor/source path must block")
    return ["fail closed to BLOCKED"]


def eval_e13() -> list[str]:
    contract = build_task_contract(prompt="没说平台，根据资料正常写")
    check(contract.distribution_mode == DistributionMode.DUAL, "E13 unspecified platform must route DUAL")
    check(contract.delivery_channel == DeliveryChannel.WORD_FILE_ONLY, "E13 must remain Word-only")
    check(all("VISUAL" not in kind.value and "STICKER" not in kind.value and kind.value != "CHAT_TEXT" for kind in contract.required_outputs), "E13 removed artifact contracts forbidden")
    return ["DUAL", "WORD_FILE_ONLY", "no visual/sticker/chat artifacts"]


def eval_e14() -> list[str]:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(policy["defaults"]["language"] == "zh-CN", "E14 language mismatch")
    check(policy["style"]["heading_hierarchy"] == ["一、", "（1）", "①"], "E14 hierarchy mismatch")
    check(policy["style"]["deep_numbered_navigation_required_when_branching"], "E14 deep numbered navigation hardening missing")
    check(policy["word"]["allow_tables"] is False and policy["word"]["tables_are_hard_fail"], "E14 tables must hard fail")
    expected = {"h1_px": 24, "h1_pt": 18, "h2_px": 20, "h2_pt": 15, "body_px": 18, "body_pt": 13.5}
    for key, value in expected.items():
        check(policy["word"][key] == value, f"E14 exact typography mismatch for {key}")
    return ["zh-CN", "一/（1）/①", "deep lower numbering when branching", "tables hard fail"]


def eval_e16() -> list[str]:
    contract = build_task_contract(prompt="写完自动配图并插进Word")
    check(contract.delivery_channel == DeliveryChannel.WORD_FILE_ONLY, "E16 article still Word-only")
    check(all("VISUAL" not in kind.value and "STICKER" not in kind.value for kind in contract.required_outputs), "E16 Financial Writing must not create visual artifacts")
    return ["image work outside Financial Writing", "no visual artifacts"]


def eval_e17() -> list[str]:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(policy["risk_disclaimer"]["required"], "E17 risk disclaimer must be mandatory")
    check(policy["risk_disclaimer"]["min_body_chars"] > 0, "E17 minimum substance must be nonzero")
    return ["risk mandatory", f"min_chars={policy['risk_disclaimer']['min_body_chars']}"]


def _headline(title: str, broader: str = "", family: str = "profit_orders") -> HeadlineCandidate:
    return HeadlineCandidate(
        title=title,
        angle="利润传导",
        angle_family=family,
        target_reader="关注盈利与定价的财经读者",
        finance_relevance="影响盈利预期和估值",
        target_reader_click_reason="同一变化下利润兑现路径仍有重要差异",
        broader_finance_relevance=broader,
        primary_gap="市场尚未区分兑现环节",
        promised_payoff="解释订单与利润兑现差异",
        cognitive_load="low",
        wechat_search_terms=["行业关键词"],
        search_evidence_refs=["current-wechat-search-evidence"],
    )


def eval_e18() -> list[str]:
    candidate = _headline("价格变化之后，利润会落到哪里")
    check(candidate.target_reader and candidate.target_reader_click_reason and candidate.promised_payoff, "E18 qualified reader-value fields must exist")
    check(candidate.broader_finance_relevance == "", "E18 cross-industry relevance must be optional")
    check(candidate.wechat_search_terms and candidate.search_evidence_refs, "E18 current search evidence is required")
    with_missing = dict(
        title="无搜索证据", angle="x", angle_family="hard_fact", target_reader="财经读者", finance_relevance="x",
        target_reader_click_reason="x", primary_gap="x", promised_payoff="x", cognitive_load="low",
        wechat_search_terms=[], search_evidence_refs=[]
    )
    try:
        HeadlineCandidate(**with_missing)
    except ValidationError:
        pass
    else:
        raise AssertionError("E18 search evidence cannot be omitted")
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(policy["hooks"]["headline_angle_families_min"] >= 5, "E18 title pool strategy diversity missing")
    check(policy["hooks"]["cross_finance_clickability_required"] is False, "E18 cross-industry clickability must not be universal")
    return ["qualified target-reader fit", "5+ headline angle families", "optional broader-finance relevance", "WeChat search evidence required"]


def eval_e19() -> list[str]:
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
    provenance = AuditProvenance(assurance="INDEPENDENT_EXECUTOR", reviewer_identity="prose-judge", author_identity="writer", execution_ref="eval:e19")
    decision = StyleAuditDecision(status="PASS", evidence=["final text reread against consolidated nine-part authorial prose rubric"], rubric=rubric, provenance=provenance)
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(decision.status == "PASS", "E19 independent all-dimension review should allow PASS")
    check(policy["style"]["template_cluster_guard_required"], "E19 deterministic template-cluster guard missing")
    report = analyze_template_scaffolding("真正的变化不是装机而是订单。如果只看装机就会错过。这正是最值得写清楚的地方。真正的信号不是规划而是交付。如果只看并网也会滞后。这正是核心在于订单的原因。真正的兑现不是概念而是利润。")
    check(report["requires_revise"], "E19 clustered AI staging must trigger revision")
    try:
        StyleAuditDecision(status="PASS", evidence=["self review"], rubric=rubric)
    except ValidationError:
        pass
    else:
        raise AssertionError("E19 chat self-review must not PASS")
    return ["9-part Natural Authorial Prose rubric", "template-cluster guard", "self-review cannot PASS"]


def eval_e21() -> list[str]:
    company = CompanyFinding(name="甲公司", value_chain_class="海缆", materiality="MATERIAL", relevance="海缆订单", exposure_type="DIRECT_BUSINESS")
    kwargs = {
        "topic": "海上风电",
        "chronology": ["项目启动"],
        "what_changed": ["招标施工推进"],
        "industry_chain": ["海缆→整机→基础→安装"],
        "transmission_chain": ["项目→订单→排产→收入"],
        "universe": [company],
        "universe_coverage": {
            "status": "COMPLETE",
            "classes": [{"class_name": "海缆", "economic_role": "送出与阵列电缆", "included_companies": ["甲公司"], "source_refs": ["industry-map"]}],
            "recall_sources": ["StockBase", "official-search"],
            "stop_reason": "class-level reconciliation complete",
        },
        "market_explanation_scope": "NOT_MATERIAL",
        "market_explanation_scope_reason": "只讨论经济兑现",
        "evidence_ledger": [{"claim": "项目推进", "source": "official"}],
        "provisional_theses": ["订单先于并网兑现"],
        "source_boundary": "公开信息",
        "cognition": {"concept_map": ["海风"], "industry_logic": ["项目到订单"]},
        "coverage": {"sweeps_completed": 2, "coverage_status": "SATURATED", "material_new_items_last_sweep": 0, "concept_coverage": "covered", "company_coverage": "class-accounted", "source_diversity": "two sources", "stop_reason": "no material new class after reconciliation"},
    }
    package = ResearchPackage(**kwargs)
    check(package.universe_coverage.status == "COMPLETE", "E21 class-level universe ledger missing")
    bad = dict(kwargs)
    bad["universe_coverage"] = {**kwargs["universe_coverage"], "recall_sources": ["one-source"]}
    try:
        ResearchPackage(**bad)
    except ValidationError:
        pass
    else:
        raise AssertionError("E21 one-source universe recall must fail")
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(policy["editorial"]["finance_deep_material_company_mentions_required"], "E21 material companies must be Deep mention obligations")
    check(policy["audit"]["universe_to_deep_article_reconciliation_required"], "E21 final reconciliation missing")
    return ["class-level universe ledger", ">=2 recall sources", "MATERIAL-company Deep obligations", "universe-to-article reconciliation"]


EXECUTABLE = {
    "E01": eval_e01,
    "E02": eval_e02,
    "E03": eval_e03,
    "E06": eval_e06,
    "E07": eval_e07,
    "E11": eval_e11,
    "E12": eval_e12,
    "E13": eval_e13,
    "E14": eval_e14,
    "E16": eval_e16,
    "E17": eval_e17,
    "E18": eval_e18,
    "E19": eval_e19,
    "E21": eval_e21,
}

SPEC_ONLY = {
    "E04": "revision invalidation is covered by runtime regression tests",
    "E05": "universe breadth, deep completeness and market-explanation coverage are semantic research assertions",
    "E08": "full all-stage execution is trajectory/E2E coverage",
    "E09": "Writing DNA promotion requires provenance across explicit/repeated/corpus evidence",
    "E10": "durable Reader Funnel rule promotion is a maintenance-policy assertion",
    "E15": "connected knowledge reuse plus material-completeness mapping requires semantic/connector regression",
    "E20": "visible chat checklist plus audit Word is a final-delivery semantic/trajectory assertion",
}


def main() -> None:
    payload = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    scenarios = payload.get("evals", [])
    ids = [row["id"] for row in scenarios]
    check(len(ids) == len(set(ids)), "scenario IDs must be unique")
    expected = set(EXECUTABLE) | set(SPEC_ONLY)
    check(set(ids) == expected, f"scenario registry mismatch: file={sorted(ids)} registry={sorted(expected)}")

    report: list[dict[str, object]] = []
    failures: list[str] = []
    for row in scenarios:
        sid = row["id"]
        check(bool(row.get("assertions", [])), f"{sid} must declare assertions")
        if sid in EXECUTABLE:
            try:
                report.append({"id": sid, "status": "PASS", "evidence": EXECUTABLE[sid]()})
            except Exception as exc:
                failures.append(f"{sid}: {type(exc).__name__}: {exc}")
                report.append({"id": sid, "status": "FAIL", "error": str(exc)})
        else:
            report.append({"id": sid, "status": "SPEC_ONLY", "reason": SPEC_ONLY[sid]})

    print(json.dumps({"results": report, "failures": failures}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
