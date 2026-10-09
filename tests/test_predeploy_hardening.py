from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from financial_writing_agent.plugin_server import _publicize
from financial_writing_agent.schemas import EvidenceItem, HeadlineCandidate, HeadlinePackage, HookAuditDecision


def _headline(title: str) -> HeadlineCandidate:
    return HeadlineCandidate(
        title=title,
        angle="事件变化",
        finance_relevance="影响盈利预期",
        cross_finance_click_reason="价格和利润变化对跨行业资金都有估值含义",
        primary_gap="市场仍未充分区分",
        cognitive_load="low",
        wechat_search_terms=["行业关键词"],
        search_evidence_refs=["wechat-search-current-signal"],
    )


def test_stage_schema_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        EvidenceItem(claim="事实", source="公开来源", unexpected_field="must not be silently ignored")


def test_headline_candidates_cannot_hide_duplicates():
    with pytest.raises(ValidationError):
        HeadlinePackage(
            finance_deep_candidates=[_headline("同一个标题"), _headline("同一个标题")],
            finance_deep_selected="同一个标题",
        )


def test_headline_candidate_requires_current_search_evidence():
    with pytest.raises(ValidationError):
        HeadlineCandidate(
            title="标题",
            angle="事件",
            finance_relevance="利润",
            cross_finance_click_reason="跨行业财经相关",
            primary_gap="信息差",
            cognitive_load="low",
            wechat_search_terms=[],
            search_evidence_refs=[],
        )


def test_hook_audit_pass_requires_every_rubric_item_pass():
    with pytest.raises(ValidationError):
        HookAuditDecision(
            status="PASS",
            evidence=["final title and first three sentences inspected"],
            search_terms_checked=["关键词"],
            search_evidence_refs=["current-search-ref"],
            rubric={
                "title_cross_finance_clickability": "PASS",
                "title_wechat_search_intent": "PASS",
                "opening_three_sentence_retention": "REVISE",
                "h1_continuation_power": "PASS",
                "paragraph_forward_pull": "PASS",
                "title_opening_payoff": "PASS",
            },
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
