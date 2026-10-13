from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from financial_writing_agent.checks import analyze_template_scaffolding
from financial_writing_agent.github_chat_guard import (
    GithubChatGuardError,
    advance_state,
    build_initial_state,
)
from financial_writing_agent.models import ArtifactKind, DeliveryChannel, DistributionMode, TaskContract
from financial_writing_agent.owner_lifecycle import block_review_failure_state, resume_blocked_state
from financial_writing_agent.routing import build_task_contract
from financial_writing_agent.workflow_spec import BUSINESS_STAGE_NAMES, revision_targets
from financial_writing_agent.models import Stage

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "policy.json"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def eval_single_owner_authority() -> list[str]:
    execution = json.loads((ROOT / "continuity" / "FINANCIAL_OWNER_EXECUTION.json").read_text(encoding="utf-8"))
    agent = json.loads((ROOT / "continuity" / "AGENT_MANIFEST.json").read_text(encoding="utf-8"))
    capabilities = json.loads((ROOT / "continuity" / "EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))

    check(execution["product_path"] == "SINGLE_GITHUB_BACKED_FINANCIAL_OWNER", "single owner execution contract missing")
    check(execution["execution"]["route_selection"] == "NONE", "execution route selection must be removed")
    check(execution["authority"]["business_state_ref"] == "main", "business state must remain on main")
    check(execution["authority"]["business_state_root"] == "workspaces/articles/{task_id}", "article state root drift")
    check(execution["authority"]["alternate_runtime_state_authority_allowed"] is False, "alternate runtime state authority enabled")
    check(execution["execution"]["free_form_article_fallback_allowed"] is False, "free-form fallback enabled")
    check(execution["authority"]["canonical_lifecycle_implementation"] == "financial_writing_agent/owner_lifecycle.py", "owner lifecycle not bound")
    check(agent["product_interface"]["execution_mode_selection"] == "NONE", "agent still selects an execution mode")
    check(agent["runtime"]["runtime_type"] == "SINGLE_GITHUB_BACKED_OWNER", "agent runtime is not single-owner")
    check(capabilities["profile_version"] == 11, "capability profile drift")
    check("blocked_recovery" in {item["capability_id"] for item in capabilities["capabilities"]}, "blocked recovery capability missing")
    check("system_impact_lifecycle" in {item["capability_id"] for item in capabilities["capabilities"]}, "system-impact lifecycle capability missing")
    return ["single owner", "main-only state", "no route selection", "owner lifecycle bound"]


def eval_task_contract() -> list[str]:
    contract = build_task_contract(prompt="根据资料正常写")
    check(contract.distribution_mode == DistributionMode.DUAL, "unspecified mode must remain DUAL")
    check(contract.delivery_channel == DeliveryChannel.WORD_FILE_ONLY, "delivery must remain WORD_FILE_ONLY")
    check(
        contract.required_outputs
        == [ArtifactKind.AUDIT_DOCX, ArtifactKind.FINANCE_DEEP_DOCX, ArtifactKind.FINANCE_BROAD_DOCX],
        "default DUAL must require Audit + Deep + Broad in canonical order",
    )
    try:
        TaskContract(
            prompt="bad deserialization",
            distribution_mode=DistributionMode.DUAL,
            required_outputs=[ArtifactKind.AUDIT_DOCX, ArtifactKind.FINANCE_BROAD_DOCX],
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("non-empty mismatched required_outputs must fail closed")
    check(not hasattr(ArtifactKind, "CHAT_TEXT"), "legacy CHAT_TEXT artifact returned")
    return ["DUAL", "WORD_FILE_ONLY", "exact output contract", "no CHAT_TEXT"]


def eval_workflow_graph() -> list[str]:
    check(
        BUSINESS_STAGE_NAMES
        == (
            "INTAKE",
            "RESEARCH",
            "RESEARCH_AUDIT",
            "EDITORIAL",
            "TITLE",
            "DRAFT",
            "EDITORIAL_AUDIT",
            "DELIVERY",
            "MECHANICAL_AUDIT",
            "FINAL_AUDIT",
        ),
        "canonical business stage order drift",
    )
    check(revision_targets(Stage.RESEARCH_AUDIT) == frozenset({Stage.RESEARCH}), "Research audit repair route drift")
    check(
        revision_targets(Stage.FINAL_AUDIT)
        == frozenset({Stage.RESEARCH, Stage.EDITORIAL, Stage.TITLE, Stage.DRAFT, Stage.DELIVERY}),
        "Final audit repair routes drift",
    )
    return ["canonical stage order", "canonical revision targets"]


def _initial(task_id: str = "eval-owner"):
    return build_initial_state(
        task_id=task_id,
        prompt="write a test article",
        source_refs=["source://one"],
        executor_identity="eval:current-owner",
    )


def eval_guard_requires_durable_stage_evidence() -> list[str]:
    state = advance_state(_initial(), previous_state_blob_sha="s0", executor_identity="eval:current-owner")
    try:
        advance_state(state, previous_state_blob_sha="s1", executor_identity="eval:current-owner")
    except GithubChatGuardError as exc:
        check("stage_artifacts.RESEARCH" in str(exc), "missing Research artifact failed for wrong reason")
    else:
        raise AssertionError("RESEARCH must not advance without a durable artifact ref")
    return ["durable stage artifact required", "free-form stage completion rejected"]


def eval_blocked_recovery_uses_persisted_cursor() -> list[str]:
    state = _initial("eval-recovery")
    state = advance_state(state, previous_state_blob_sha="r0", executor_identity="eval:current-owner")
    state = advance_state(
        state,
        previous_state_blob_sha="r1",
        executor_identity="eval:current-owner",
        artifact_key="RESEARCH",
        artifact_path="workspaces/articles/eval-recovery/stages/RESEARCH.json",
        artifact_blob_sha="research-blob",
    )
    blocked = block_review_failure_state(
        state,
        previous_state_blob_sha="r2",
        executor_identity="eval:current-owner",
        artifact_key="RESEARCH_AUDIT",
        artifact_path="workspaces/articles/eval-recovery/reviews/RESEARCH_AUDIT.json",
        artifact_blob_sha="audit-fail-blob",
        revision_target="RESEARCH",
    )
    check(blocked["status"] == "BLOCKED", "review FAIL did not block")
    check(blocked["execution_receipts"][-1]["input_bindings"]["revision_target"] == "RESEARCH", "recovery cursor not persisted")

    resumed = resume_blocked_state(
        blocked,
        previous_state_blob_sha="r3",
        executor_identity="eval:current-owner",
        repair_evidence=["eval://repair", "eval://regression"],
    )
    check(resumed["status"] == "IN_PROGRESS", "recovery did not reopen task")
    check(resumed["current_stage"] == "RESEARCH", "recovery did not use persisted canonical target")
    check(resumed["stage_artifacts"] == {}, "stale target/downstream artifacts survived recovery")
    check(resumed["review_decisions"] == {}, "stale review decision survived recovery")
    return ["FAIL cursor persisted", "repair evidence required", "downstream invalidated"]


def eval_word_and_style_policy() -> list[str]:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    check(policy["word"]["allow_tables"] is False and policy["word"]["tables_are_hard_fail"] is True, "tables must hard fail")
    check(policy["word"]["allow_underline"] is False, "underlines must remain forbidden")
    check(policy["word"]["end_source_section_allowed"] is False, "publication-tail source appendix must remain forbidden")
    check(policy["word"]["auto_bold_company_names"] is True, "supplied A-share company name bolding drift")
    risk = policy["risk_disclaimer"]
    check(risk["required"] and risk["italic"] and risk["inline_paragraph"] and not risk["visible_heading"], "risk disclaimer presentation drift")

    report = analyze_template_scaffolding(
        "真正的变化不是装机而是订单。如果只看装机就会错过。这正是最值得写清楚的地方。"
        "真正的信号不是规划而是交付。如果只看收入也会滞后。这正是核心在于订单的原因。"
        "真正的兑现不是概念而是利润。"
    )
    check(report["requires_revise"], "template-cluster guard must reject repeated AI staging")
    return ["Word hard boundaries", "risk inline italic", "template cluster revise"]


def eval_legacy_quarantine() -> list[str]:
    check(not (ROOT / "continuity" / "GITHUB_CHAT_EXECUTION.json").exists(), "retired dual-adapter contract returned")
    check(not (ROOT / "plugin.json").exists(), "retired plugin discovery manifest returned")
    check(not (ROOT / "scripts" / "sdk_smoke.py").exists(), "retired SDK runtime smoke returned")
    check(not (ROOT / "scripts" / "mcp_smoke.py").exists(), "retired MCP runtime smoke returned")

    execution = json.loads((ROOT / "continuity" / "FINANCIAL_OWNER_EXECUTION.json").read_text(encoding="utf-8"))
    check(execution["checkpoint_contract"]["storage_token_status"] == "LEGACY_INTERNAL_TOKEN_ONLY__NOT_A_ROUTE_SELECTOR", "legacy state token is not quarantined")
    check(execution["legacy_quarantine"]["historical_evals_and_branches"] == "EVIDENCE_ONLY__NEVER_EXECUTION_AUTHORITY", "historical evidence can still become authority")
    return ["no retired discovery contract", "no retired package discovery", "historical evidence only"]


def main() -> None:
    evaluations = [
        ("OWNER", eval_single_owner_authority),
        ("CONTRACT", eval_task_contract),
        ("WORKFLOW", eval_workflow_graph),
        ("DURABLE_EVIDENCE", eval_guard_requires_durable_stage_evidence),
        ("RECOVERY", eval_blocked_recovery_uses_persisted_cursor),
        ("WORD_STYLE", eval_word_and_style_policy),
        ("LEGACY_QUARANTINE", eval_legacy_quarantine),
    ]
    report: dict[str, list[str]] = {}
    for name, fn in evaluations:
        report[name] = fn()
    print(json.dumps({"status": "PASS", "evaluations": report}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
