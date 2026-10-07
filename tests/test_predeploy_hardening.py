from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from financial_writing_agent.plugin_server import _publicize
from financial_writing_agent.schemas import (
    ArticlePayload,
    EvidenceItem,
    HeadlineCandidate,
    HeadlinePackage,
    OpenAIFileRef,
    PlatformConstraintSnapshot,
)


def _headline(title: str) -> HeadlineCandidate:
    return HeadlineCandidate(
        title=title,
        angle="事件变化",
        finance_relevance="影响盈利预期",
        factual_anchor="公司公告披露的可核事实",
        primary_gap="市场仍未充分区分",
        opening_payoff="开头立即交代变化、矛盾和本文判断收益",
        cognitive_load="low",
    )


def test_stage_schema_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        EvidenceItem(
            claim="事实",
            source="公开来源",
            unexpected_field="must not be silently ignored",
        )


def test_core_safe_evidence_cannot_remain_unresolved():
    with pytest.raises(ValidationError):
        EvidenceItem(
            claim="拟进入核心结论的事实",
            source="公开来源",
            core_safe=True,
            verification_status="UNRESOLVED",
        )


def test_independent_cross_check_requires_independent_source_groups():
    with pytest.raises(ValidationError):
        EvidenceItem(
            claim="关键事实",
            source="原始公告",
            core_safe=True,
            verification_status="INDEPENDENTLY_CROSS_CHECKED",
            source_group="same-origin",
            second_check_source="公告转载",
            second_check_source_group="same-origin",
        )


def test_headline_candidates_cannot_hide_duplicates():
    with pytest.raises(ValidationError):
        HeadlinePackage(
            finance_deep_candidates=[_headline("同一个标题"), _headline("同一个标题")],
            finance_deep_selected="同一个标题",
        )


def test_formal_article_requires_one_independent_lead_before_first_h1():
    risk = "本文基于公开信息进行研究，仅用于财经信息交流，不构成投资建议或收益承诺。相关事实、政策、价格、订单、业绩和市场环境均可能变化，请以最新披露为准并独立判断。"
    with pytest.raises(ValidationError):
        ArticlePayload(
            title="测试",
            blocks=[
                {"kind": "h1", "text": "第一章"},
                {"kind": "body", "text": "正文"},
                {"kind": "body", "text": "继续"},
            ],
            risk_disclaimer=risk,
        )


def test_platform_constraint_snapshot_must_be_fresh():
    with pytest.raises(ValidationError):
        PlatformConstraintSnapshot(
            verified_at=datetime.now(timezone.utc) - timedelta(hours=49),
            source_refs=["current-ui"],
        )


def test_file_param_rejects_private_and_local_targets():
    for url in [
        "http://example.com/file.png",
        "https://127.0.0.1/file.png",
        "https://10.0.0.1/file.png",
        "https://169.254.169.254/latest/meta-data",
        "https://localhost/file.png",
    ]:
        with pytest.raises(ValidationError):
            OpenAIFileRef(download_url=url, file_id="file-1", mime_type="image/png")


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
        "visuals_enabled": False,
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
        "render_pages": {"FINANCE_DEEP_DOCX": ["writing-render://task-1/FINANCE_DEEP_DOCX/1"]},
    }
    public = _publicize(raw)
    artifact = public["artifacts"]["FINANCE_DEEP_DOCX"]
    assert "path" not in artifact
    assert artifact["resource_uri"] == "writing-docx://task-1/FINANCE_DEEP_DOCX"
    assert public["render_pages"]["FINANCE_DEEP_DOCX"] == ["writing-render://task-1/FINANCE_DEEP_DOCX/1"]
    assert public.get("trace_tail") is None
