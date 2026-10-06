from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from financial_writing_agent.plugin_server import _publicize
from financial_writing_agent.schemas import (
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
        primary_gap="市场仍未充分区分",
        cognitive_load="low",
    )


def test_stage_schema_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        EvidenceItem(
            claim="事实",
            source="公开来源",
            unexpected_field="must not be silently ignored",
        )


def test_headline_candidates_cannot_hide_duplicates():
    with pytest.raises(ValidationError):
        HeadlinePackage(
            finance_deep_candidates=[_headline("同一个标题"), _headline("同一个标题")],
            finance_deep_selected="同一个标题",
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
    }
    public = _publicize(raw)
    artifact = public["artifacts"]["FINANCE_DEEP_DOCX"]
    assert "path" not in artifact
    assert artifact["resource_uri"] == "writing-docx://task-1/FINANCE_DEEP_DOCX"
    assert public.get("trace_tail") is None
