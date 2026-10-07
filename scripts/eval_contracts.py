from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from financial_writing_agent.engine import WritingEngine
from financial_writing_agent.models import ArtifactKind, ContentMode, DeliveryChannel, DistributionMode, GateStatus, Stage, TaskContract, WritingState
from financial_writing_agent.routing import build_task_contract
from financial_writing_agent.runner import AgentRuntime
from financial_writing_agent.runtime_service import _completion_checklist
from financial_writing_agent.schemas import PlatformConstraintSnapshot, StickerPostPayload
from financial_writing_agent.store import SQLiteStateStore, StateConflictError

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "evals" / "scenarios.json"
POLICY = ROOT / "config" / "policy.json"
SKILL = ROOT / "skills" / "financial-writing-agent" / "SKILL.md"


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
        check(state.gates["knowledge_context"].status == GateStatus.N_A, "E01 standalone path must close unavailable recall explicitly")
    return ["runtime starts first", "WORD_FILE_ONLY", "audit report required", "standalone recall boundary explicit"]


def eval_e02() -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        store = SQLiteStateStore(Path(td) / "state.db")
        engine = WritingEngine(store)
        state = engine.start(TaskContract(prompt="继续昨天那篇"))
        state = engine.transition(state, Stage.RESEARCH, reason="test")
        state.set_gate("research_output", GateStatus.PASS, ["done"])
        store.save(state)
        loaded = store.load(state.contract.task_id)
        stale = store.load(state.contract.task_id)
        check(loaded is not None and stale is not None, "E02 checkpoint must reload")
        check(loaded.stage == Stage.RESEARCH, "E02 stage must survive reload")
        check(loaded.gates["research_output"].status == GateStatus.PASS, "E02 passed gates must survive reload")
        loaded.set_gate("newer_writer", GateStatus.PASS, ["new checkpoint"])
        store.save(loaded)
        stale.set_gate("stale_writer", GateStatus.PASS, ["must not overwrite"])
        try:
            store.save(stale)
        except StateConflictError:
            pass
        else:
            raise AssertionError("E02 stale concurrent checkpoint write must be rejected")
        latest = store.load(state.contract.task_id)
        check(latest is not None and "newer_writer" in latest.gates, "E02 latest checkpoint must survive stale write attempt")
        check("stale_writer" not in latest.gates, "E02 stale writer must not cause lost update")
    return ["checkpoint reload", "stage/gates preserved", "stale concurrent write rejected"]


def eval_e03() -> list[str]:
    contract = build_task_contract(
        prompt="这篇同时发雪球、韭研、头条、百家",
        target_platforms=["雪球", "韭研公社", "今日头条", "百家号"],
    )
    check(contract.distribution_mode == DistributionMode.DUAL, "E03 mixed destinations must route DUAL")
    check(ArtifactKind.FINANCE_DEEP_DOCX in contract.required_outputs, "E03 FINANCE_DEEP output required")
    check(ArtifactKind.FINANCE_BROAD_DOCX in contract.required_outputs, "E03 FINANCE_BROAD output required")
    return ["DUAL", "deep output", "broad output"]


def eval_e06() -> list[str]:
    contract = build_task_contract(prompt="根据研报写，字数控制得短一点")
    check("word_count" not in contract.run_constraints, "E06 must not invent a fixed word-count contract")
    return ["no fixed word-count anchor"]


def eval_e07() -> list[str]:
    contract = build_task_contract(prompt="给我直接在聊天框看正文")
    check(contract.delivery_channel == DeliveryChannel.CHAT_TEXT, "E07 explicit chat request must route CHAT_TEXT")
    check(contract.required_outputs == [ArtifactKind.CHAT_TEXT], "E07 Word outputs must not be required")
    check(not contract.visuals_enabled, "E07 chat-text delivery must not force Word visuals")
    return ["CHAT_TEXT", "Word-only outputs N/A", "visuals not forced"]


def eval_e08() -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        engine = WritingEngine(SQLiteStateStore(Path(td) / "state.db"))
        state = engine.start(build_task_contract(prompt="正常写一篇，不用我提醒流程", visuals_enabled=False))
        required = engine._required_completion_gates(state)
        expected = {
            "runtime_initialized", "knowledge_context", "research_output", "research_audit", "editorial_plan",
            "acceptance_contract", "title_audit", "draft_output", "style_audit",
            "editorial_audit", "delivery_output", "mechanical_audit", "knowledge_sync", "final_audit",
        }
        check(expected.issubset(required), f"E08 mandatory gate inventory incomplete: {sorted(expected - required)}")
        check(state.contract.delivery_channel == DeliveryChannel.WORD_FILE_ONLY, "E08 normal writing must remain WORD_FILE_ONLY")
        final_keys = engine._required_final_evidence_keys(state)
        check("FINANCE_DEEP.opening_first_three_sentences" in final_keys, "E08 first-three-sentence evidence key missing")
        check("FINANCE_BROAD.bold_scan_skeleton" in final_keys, "E08 bold scan-skeleton evidence key missing")
    skill = SKILL.read_text(encoding="utf-8")
    check("Under `WORD_FILE_ONLY`, do not paste the article body" in skill, "E08 Skill must prohibit body paste under Word-only")
    return ["mandatory gate inventory", "knowledge recall gate", "acceptance contract", "opening/bold final evidence", "WORD_FILE_ONLY body omission"]


def eval_e11() -> list[str]:
    contract = build_task_contract(prompt="Word已经写好了，直接发我")
    check(contract.delivery_channel == DeliveryChannel.WORD_FILE_ONLY, "E11 remains Word delivery")
    check(ArtifactKind.AUDIT_DOCX in contract.required_outputs, "E11 audit report remains mandatory")
    check(not contract.visuals_enabled, "E11 existing Word should not invent a new visual requirement")
    return ["Word delivery", "audit report still required", "no invented visuals"]


def eval_e12() -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        runtime = AgentRuntime.with_sqlite(Path(td) / "state.db", executors={})
        state = runtime.start(build_task_contract(prompt="来源抓不到但你先按常识写吧", visuals_enabled=False))
        state = runtime.run(state)
        check(state.stage == Stage.BLOCKED, "E12 missing executor/source path must block instead of free-form fallback")
        check(state.working.get("blocked_from_stage") == "RESEARCH", "E12 block must record originating stage")
        resumed = runtime.resume(state.contract.task_id)
        check(resumed.stage == Stage.RESEARCH, "E12 resume must return exactly to recorded originating stage")
        check(resumed.blocked_reason is None, "E12 resume must clear blocked reason")
    return ["fail closed to BLOCKED", "origin stage recorded", "explicit recovery to original stage"]


def eval_e13() -> list[str]:
    contract = build_task_contract(prompt="没说平台，根据资料正常写")
    check(contract.distribution_mode == DistributionMode.DUAL, "E13 unspecified platform must route DUAL")
    check(contract.visuals_enabled, "E13 new Word article visuals must be enabled")
    check(ArtifactKind.VISUAL_MANIFEST_JSON in contract.required_outputs, "E13 visual manifest must be required")
    return ["DUAL", "visuals enabled", "visual manifest required"]


def eval_e14() -> list[str]:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(policy["defaults"]["language"] == "zh-CN", "E14 default language must be zh-CN")
    check(policy["style"]["heading_hierarchy"] == ["一、", "（1）", "①"], "E14 hierarchy mismatch")
    check("·" in policy["style"]["forbidden_heading_prefixes"], "E14 middle dot must be forbidden as heading prefix")
    return ["zh-CN", "一/（1）/①", "middle dot forbidden"]


def eval_e17() -> list[str]:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(policy["risk_disclaimer"]["required"], "E17 risk disclaimer must be mandatory")
    check(policy["risk_disclaimer"]["min_body_chars"] > 0, "E17 minimum substance must be nonzero")
    return ["risk mandatory", f"min_chars={policy['risk_disclaimer']['min_body_chars']}"]


def eval_e18() -> list[str]:
    contract = build_task_contract(prompt="做一条微信贴图引流")
    check(contract.content_mode == ContentMode.WECHAT_STICKER_POST, "E18 must route to WECHAT_STICKER_POST")
    check(ArtifactKind.WECHAT_STICKER_DOCX in contract.required_outputs, "E18 sticker Word output required")
    policy = json.loads(POLICY.read_text(encoding="utf-8"))["wechat_sticker"]
    check(policy["hard_coded_title_limit"] is None and policy["hard_coded_body_limit"] is None, "E18 remembered limits must not be hard-coded")
    snapshot = PlatformConstraintSnapshot(
        verified_at=datetime.now(timezone.utc),
        source_refs=["current-wechat-publisher-ui"],
        title_max_chars=4,
        body_max_chars=100,
    )
    try:
        StickerPostPayload(
            title="超过限制的标题",
            body="有用信息",
            risk_disclaimer="本文基于公开信息整理，仅用于财经信息交流，不构成投资建议或收益承诺，请以最新公告为准并独立判断。",
            constraints=snapshot,
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("E18 verified dynamic title limit must be enforced")
    return ["distinct content mode", "dynamic constraint snapshot", "no remembered hard-coded limits"]


def eval_e19() -> list[str]:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    phrases = set(policy["style"]["hard_fail_extreme_phrases"])
    check("最强" in phrases and "最牛" in phrases, "E19 core extreme phrases missing")
    check("最近" not in phrases and "最后" not in phrases, "E19 factual temporal words must not be mechanically banned")
    check(policy["style"]["anti_ai_semantic_audit"], "E19 anti-AI semantic audit must be enabled")
    check(policy["style"]["anti_ai_judge_required"], "E19 independent anti-AI judge must be required")
    return ["extreme phrase policy", "temporal-word safe", "independent anti-AI semantic judge"]


def eval_e20() -> list[str]:
    state = WritingState(contract=TaskContract(prompt="写完把所有要求检查一遍给我"), stage=Stage.COMPLETE)
    for name in ["research_audit", "editorial_audit", "style_audit", "mechanical_audit", "final_audit"]:
        state.set_gate(name, GateStatus.PASS, ["eval"])
    state.set_gate("knowledge_context", GateStatus.N_A, ["eval recall boundary"])
    state.set_gate("knowledge_sync", GateStatus.N_A, ["eval writeback boundary"])
    checklist = _completion_checklist(state)
    required_top = {"runtime_gates", "research_evidence", "structure_style_continuity", "word_render", "compliance_risk", "visuals", "knowledge"}
    check(required_top.issubset(checklist), f"E20 checklist missing keys: {sorted(required_top - set(checklist))}")
    check(checklist["runtime_gates"] == "PASS", "E20 completed runtime must expose PASS")
    check(checklist["knowledge"]["context_gate"] == "N_A", "E20 visible checklist must expose recall decision")
    check(checklist["knowledge"]["sync_gate"] == "N_A", "E20 visible checklist must expose writeback decision")
    skill = SKILL.read_text(encoding="utf-8")
    check("Under `WORD_FILE_ONLY`, do not paste the article body" in skill, "E20 final checklist must not imply article-body paste")
    return ["visible completion checklist schema", "knowledge recall/writeback visible", "research/style/Word/compliance coverage", "Word-only body omission"]


EXECUTABLE = {
    "E01": eval_e01,
    "E02": eval_e02,
    "E03": eval_e03,
    "E06": eval_e06,
    "E07": eval_e07,
    "E08": eval_e08,
    "E11": eval_e11,
    "E12": eval_e12,
    "E13": eval_e13,
    "E14": eval_e14,
    "E17": eval_e17,
    "E18": eval_e18,
    "E19": eval_e19,
    "E20": eval_e20,
}

SEMANTIC_OR_LIVE = {
    "E05": "universe breadth, material-company depth and why-this/why-not require semantic research/live-model evaluation",
    "E15": "connected prior-knowledge recall, current re-verification and writeback receipts require connector/live regression",
    "E16": "creative image generation is model-side; deterministic file ingest/insertion/render are covered separately, full visual behavior requires live E2E",
}

KNOWN_GAPS = {
    "E04": "title-only mutation of an existing persisted article is not yet a dedicated public MCP workflow; do not claim deterministic support",
    "E09": "promotion of one platform-performance sample into durable experience memory is governance/maintenance work, not yet an executable runtime action",
    "E10": "durable user rule promotion/update is documented but not yet exposed as an executable maintenance workflow in this Writing Agent",
}


def main() -> None:
    payload = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    scenarios = payload.get("evals", [])
    ids = [row["id"] for row in scenarios]
    check(len(ids) == len(set(ids)), "scenario IDs must be unique")
    expected = set(EXECUTABLE) | set(SEMANTIC_OR_LIVE) | set(KNOWN_GAPS)
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
        elif sid in SEMANTIC_OR_LIVE:
            report.append({"id": sid, "status": "LIVE_OR_SEMANTIC_REQUIRED", "reason": SEMANTIC_OR_LIVE[sid]})
        else:
            report.append({"id": sid, "status": "KNOWN_GAP", "reason": KNOWN_GAPS[sid]})

    print(json.dumps({"results": report, "failures": failures}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
