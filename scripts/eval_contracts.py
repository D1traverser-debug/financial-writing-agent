from __future__ import annotations

import json
import tempfile
from pathlib import Path

from pydantic import ValidationError

from financial_writing_agent.engine import WritingEngine
from financial_writing_agent.models import ArtifactKind, ContentMode, DeliveryChannel, DistributionMode, GateStatus, Stage, TaskContract
from financial_writing_agent.routing import build_task_contract
from financial_writing_agent.runner import AgentRuntime
from financial_writing_agent.schemas import PlatformConstraintSnapshot, StickerPostPayload
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
    return ["fail closed to BLOCKED"]


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
        verified_at="2026-10-06T23:00:00+08:00",
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
    "E17": eval_e17,
    "E18": eval_e18,
    "E19": eval_e19,
}

SPEC_ONLY = {
    "E04": "partial retitle/resume routing requires an existing live task and is validated in targeted regression",
    "E05": "universe breadth and why-this/why-not are semantic research assertions",
    "E08": "full all-stage execution is trajectory/E2E coverage, not a contract-only check",
    "E09": "experience-sample promotion is a maintenance-policy assertion",
    "E10": "durable-rule promotion is a maintenance-policy assertion",
    "E15": "broad/deep cognition plus connected knowledge reuse/writeback requires semantic/connector regression",
    "E16": "creative image generation is model-side; deterministic insertion is covered by unit/mechanical tests",
    "E20": "visible checklist is a final-delivery semantic/trajectory assertion",
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
