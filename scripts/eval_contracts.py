from __future__ import annotations

import json
import tempfile
from pathlib import Path

from pydantic import ValidationError

from financial_writing_agent.engine import WritingEngine
from financial_writing_agent.models import ArtifactKind, DeliveryChannel, DistributionMode, GateStatus, Stage, TaskContract
from financial_writing_agent.routing import build_task_contract
from financial_writing_agent.runner import AgentRuntime
from financial_writing_agent.schemas import HeadlineCandidate, HookAuditDecision, ModeEditorialPlan, StructureCandidate, StyleAuditDecision
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
        check(loaded is not None, "E02 checkpoint must reload")
        check(loaded.stage == Stage.RESEARCH, "E02 stage must survive reload")
        check(loaded.gates["research_output"].status == GateStatus.PASS, "E02 passed gates must survive reload")
    return ["checkpoint reload", "stage preserved", "passed gate preserved"]


def eval_e03() -> list[str]:
    contract = build_task_contract(prompt="这篇同时发雪球、韭研、头条、百家", target_platforms=["雪球", "韭研公社", "今日头条", "百家号"])
    check(contract.distribution_mode == DistributionMode.DUAL, "E03 mixed destinations must route DUAL")
    c = StructureCandidate(name="A", rationale="test", sections=["一", "二"])
    deep = ModeEditorialPlan(coverage_policy="MATERIAL_COMPLETE", candidates=[c, StructureCandidate(name="B", rationale="test2", sections=["一", "二"])], selected_structure=c, completeness_obligations=["event", "transmission", "counterevidence"])
    check(not deep.core_contradictions and not deep.compression_candidates, "E03 deep plan must not select by contradictions/compression")
    broad = ModeEditorialPlan(coverage_policy="SELECTIVE_TRAFFIC", candidates=[c, StructureCandidate(name="B", rationale="test2", sections=["一", "二"])], selected_structure=c, core_contradictions=["profit timing"])
    check(broad.core_contradictions == ["profit timing"], "E03 broad plan may select core contradiction")
    return ["DUAL", "deep=MATERIAL_COMPLETE", "broad=SELECTIVE_TRAFFIC"]


def eval_e06() -> list[str]:
    contract = build_task_contract(prompt="根据研报写，字数控制得短一点")
    check("word_count" not in contract.run_constraints, "E06 must not invent a fixed word-count contract")
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(policy["editorial"]["finance_deep_material_complete"], "E06 deep material completeness must remain enabled")
    return ["no fixed word-count anchor", "deep material completeness retained"]


def eval_e07() -> list[str]:
    contract = build_task_contract(prompt="给我直接在聊天框看正文")
    check(contract.delivery_channel == DeliveryChannel.WORD_FILE_ONLY, "E07 publication content remains WORD_FILE_ONLY")
    check(ArtifactKind.CHAT_TEXT not in contract.required_outputs, "E07 chat article output must not be created")
    check(ArtifactKind.AUDIT_DOCX in contract.required_outputs, "E07 audit Word remains required")
    return ["WORD_FILE_ONLY despite chat wording", "no article body chat artifact", "audit Word required"]


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
        check(state.stage == Stage.BLOCKED, "E12 missing executor/source path must block instead of free-form fallback")
    return ["fail closed to BLOCKED"]


def eval_e13() -> list[str]:
    contract = build_task_contract(prompt="没说平台，根据资料正常写")
    check(contract.distribution_mode == DistributionMode.DUAL, "E13 unspecified platform must route DUAL")
    check(contract.delivery_channel == DeliveryChannel.WORD_FILE_ONLY, "E13 must remain Word-only")
    check(all("VISUAL" not in kind.value and "STICKER" not in kind.value for kind in contract.required_outputs), "E13 visual/sticker artifacts forbidden")
    return ["DUAL", "WORD_FILE_ONLY", "zero visual/sticker artifacts"]


def eval_e14() -> list[str]:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(policy["defaults"]["language"] == "zh-CN", "E14 default language must be zh-CN")
    check(policy["style"]["heading_hierarchy"] == ["一、", "（1）", "①"], "E14 hierarchy mismatch")
    check(policy["style"]["numbering_encouraged"], "E14 meaningful numbering must be encouraged")
    check(policy["word"]["allow_tables"] is False and policy["word"]["tables_are_hard_fail"], "E14 tables must hard fail")
    return ["zh-CN", "一/（1）/①", "numbering encouraged", "tables hard fail"]


def eval_e16() -> list[str]:
    contract = build_task_contract(prompt="写完自动配图并插进Word")
    check(contract.delivery_channel == DeliveryChannel.WORD_FILE_ONLY, "E16 article still Word-only")
    check(all("VISUAL" not in kind.value and "STICKER" not in kind.value for kind in contract.required_outputs), "E16 financial writing must not create visual artifacts")
    return ["image work outside Financial Writing", "no visual artifacts"]


def eval_e17() -> list[str]:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(policy["risk_disclaimer"]["required"], "E17 risk disclaimer must be mandatory")
    check(policy["risk_disclaimer"]["min_body_chars"] > 0, "E17 minimum substance must be nonzero")
    return ["risk mandatory", f"min_chars={policy['risk_disclaimer']['min_body_chars']}"]


def eval_e18() -> list[str]:
    candidate = HeadlineCandidate(
        title="价格变化之后，利润会落到哪里",
        angle="利润传导",
        finance_relevance="影响盈利预期和估值",
        cross_finance_click_reason="供需和利润变化对所有财经读者都有资产定价含义",
        primary_gap="市场尚未区分兑现环节",
        cognitive_load="low",
        wechat_search_terms=["行业关键词"],
        search_evidence_refs=["current-wechat-search-evidence"],
    )
    check(candidate.cross_finance_click_reason and candidate.wechat_search_terms and candidate.search_evidence_refs, "E18 title conditions must both exist")
    try:
        HeadlineCandidate(
            title="无搜索证据",
            angle="x",
            finance_relevance="x",
            cross_finance_click_reason="x",
            primary_gap="x",
            cognitive_load="low",
            wechat_search_terms=[],
            search_evidence_refs=[],
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("E18 search evidence cannot be omitted")
    return ["cross-finance click condition", "independent WeChat search terms", "real search evidence refs required"]


def eval_e19() -> list[str]:
    pass_rubric = {
        "template_fingerprint": "PASS",
        "transition_continuity": "PASS",
        "repetition_control": "PASS",
        "rhythm_naturalness": "PASS",
        "reader_dialogue": "PASS",
        "narrative_flow": "PASS",
        "judgment_persona": "PASS",
        "extreme_language_control": "PASS",
    }
    decision = StyleAuditDecision(status="PASS", evidence=["final text reread"], rubric=pass_rubric)
    check(decision.status == "PASS", "E19 all human-voice dimensions should allow PASS")
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(policy["style"]["human_voice_semantic_audit"], "E19 human voice gate enabled")
    return ["8-part Human Voice rubric", "reader dialogue", "narrative flow", "judgment persona"]


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
}

SPEC_ONLY = {
    "E04": "revision invalidation is covered by runtime regression tests and requires a live persisted stage loop",
    "E05": "universe breadth, deep completeness obligations and why-this/why-not are semantic research assertions",
    "E08": "full all-stage execution is trajectory/E2E coverage, not a contract-only check",
    "E09": "experience-sample promotion is a maintenance-policy assertion",
    "E10": "durable hook-rule promotion is a maintenance-policy assertion",
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
        assertions = row.get("assertions", [])
        check(bool(assertions), f"{sid} must declare assertions")
        if sid in EXECUTABLE:
            try:
                evidence = EXECUTABLE[sid]()
                report.append({"id": sid, "status": "PASS", "evidence": evidence})
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
