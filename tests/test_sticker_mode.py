import pytest
from pydantic import ValidationError

from financial_writing_agent.adapters.deterministic import DeliveryExecutor
from financial_writing_agent.models import ArtifactKind, ContentMode, WritingState
from financial_writing_agent.routing import build_task_contract
from financial_writing_agent.schemas import DraftPackage, PlatformConstraintSnapshot, StickerPostPayload


def _snapshot(title_max=20, body_max=200):
    return PlatformConstraintSnapshot(
        verified_at="2026-10-06T23:00:00+08:00",
        source_refs=["current-wechat-publisher-ui"],
        title_max_chars=title_max,
        body_max_chars=body_max,
        image_max_count=9,
    )


def _risk():
    return (
        "本文基于公开信息整理，仅用于财经信息交流，不构成投资建议或收益承诺。"
        "政策、价格、订单、业绩与市场情绪均可能变化，请以最新公告为准并独立判断。"
    )


def test_wechat_sticker_is_distinct_content_mode_and_artifact():
    contract = build_task_contract(prompt="做一条微信贴图引流")
    assert contract.content_mode == ContentMode.WECHAT_STICKER_POST
    assert ArtifactKind.WECHAT_STICKER_DOCX in contract.required_outputs
    assert ArtifactKind.FINANCE_DEEP_DOCX not in contract.required_outputs
    assert ArtifactKind.FINANCE_BROAD_DOCX not in contract.required_outputs
    assert ArtifactKind.VISUAL_MANIFEST_JSON in contract.required_outputs


def test_sticker_payload_enforces_verified_dynamic_limits():
    with pytest.raises(ValidationError):
        StickerPostPayload(
            title="这个标题超过限制",
            body="有用信息",
            risk_disclaimer=_risk(),
            constraints=_snapshot(title_max=4),
        )

    payload = StickerPostPayload(
        title="事件变化",
        body="有用信息和一个明确观点。",
        interaction_prompt="你更关注需求还是价格？欢迎留言。",
        risk_disclaimer=_risk(),
        constraints=_snapshot(),
    )
    assert payload.constraints.source_refs


def test_sticker_word_delivery_without_visuals_when_user_explicitly_opts_out(tmp_path):
    contract = build_task_contract(prompt="先只写微信贴图文案，不做图", visuals_enabled=False)
    payload = StickerPostPayload(
        title="事件变化",
        body="有用信息和一个明确观点。",
        interaction_prompt="你更关注需求还是价格？欢迎留言。",
        risk_disclaimer=_risk(),
        constraints=_snapshot(),
    )
    state = WritingState(contract=contract)
    state.working["draft"] = DraftPackage(wechat_sticker_post=payload).model_dump(mode="json")
    state = DeliveryExecutor(root=tmp_path).execute(state)
    artifact = state.artifacts[ArtifactKind.WECHAT_STICKER_DOCX]
    assert artifact.exists
