from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from financial_writing_agent.adapters.deterministic import DeliveryExecutor
from financial_writing_agent.harness import freeze_acceptance_contract, validate_draft_against_acceptance
from financial_writing_agent.models import ArtifactKind, ContentMode, WritingState
from financial_writing_agent.routing import build_task_contract
from financial_writing_agent.schemas import DraftPackage, EditorialPlan, HeadlinePackage, PlatformConstraintSnapshot, ResearchPackage, StickerPostPayload


def _snapshot(title_max=20, body_max=200):
    return PlatformConstraintSnapshot(
        verified_at=datetime.now(timezone.utc),
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


def _sticker_research():
    return ResearchPackage.model_validate(
        {
            "topic": "微信贴图事件",
            "chronology": ["事件发生并出现可核验变化"],
            "what_changed": ["事件事实已由原始来源确认"],
            "industry_chain": ["事件→需求→利润预期"],
            "transmission_chain": ["变化→预期差→兑现判断"],
            "universe": [],
            "evidence_ledger": [
                {
                    "claim": "经核验的事件事实",
                    "source": "原始公告",
                    "evidence_type": "official",
                    "confidence": "high",
                    "core_safe": True,
                    "verification_status": "SINGLE_SOURCE_ATTRIBUTED",
                    "source_group": "official-origin",
                    "allowed_wording": "据原始公告披露，事件已出现该变化",
                }
            ],
            "counterevidence": ["兑现程度仍需区分"],
            "unresolved_gaps": [],
            "provisional_theses": ["事件热度与业绩兑现并不等价"],
            "source_boundary": "原始公告已读；未把未核实传闻作为核心事实",
            "cognition": {
                "prior_knowledge_refs": [],
                "concept_map": ["事件变化", "兑现阶段"],
                "industry_logic": ["事件变化影响利润预期但兑现存在差异"],
            },
            "coverage": {
                "sweeps_completed": 2,
                "coverage_status": "SATURATED",
                "material_new_items_last_sweep": 0,
                "concept_coverage": "核心事件与兑现差异已覆盖",
                "company_coverage": "本测试不要求具体公司宇宙",
                "source_diversity": "原始公告与独立检查路径",
                "stop_reason": "第二轮无影响标题锚点的新事实",
            },
        }
    )


def _sticker_editorial_plan():
    selected = {
        "name": "贴图事件矛盾",
        "rationale": "突出一个真实财经矛盾",
        "sections": ["图片主钩子", "正文兑现"],
    }
    alternate = {
        "name": "贴图结果反差",
        "rationale": "用结果反差降低进入门槛",
        "sections": ["反差", "解释"],
    }
    return EditorialPlan.model_validate(
        {
            "topic_dna": {
                "new_fact": "事件出现新变化",
                "main_transmission": "变化传导到利润预期",
                "likely_reader_misjudgment": "把题材热度当成业绩兑现",
                "core_contradictions": ["热度与兑现不一致"],
                "comparison_dimensions": ["兑现阶段"],
                "compression_candidates": ["基础背景"],
                "finance_wide_question": "变化如何影响投资判断",
            },
            "wechat_sticker": {
                "candidates": [selected, alternate],
                "selected_structure": selected,
                "emphasis": ["单一财经矛盾"],
                "side_focus_statement": "本条只解释最关键变化",
                "company_selection_basis": ["兑现阶段"],
            },
        }
    )


def _sticker_headlines():
    base = {
        "finance_relevance": "影响利润预期",
        "factual_anchor": "经核验的事件事实",
        "opening_payoff": "正文立即解释变化与影响",
        "cognitive_load": "low",
    }
    return HeadlinePackage.model_validate(
        {
            "wechat_sticker_candidates": [
                {**base, "title": "事件变化", "angle": "事实反差", "primary_gap": "谁真正兑现"},
                {**base, "title": "变化之后，谁在兑现", "angle": "兑现分化", "primary_gap": "哪些环节已进入兑现"},
                {**base, "title": "热度背后的兑现差", "angle": "叙事与业绩", "primary_gap": "热度为什么没有同步变成利润"},
                {**base, "title": "同一事件，两种结果", "angle": "结果比较", "primary_gap": "为什么同一催化产生不同结果"},
            ],
            "wechat_sticker_selected": "事件变化",
        }
    )


def test_wechat_sticker_is_distinct_content_mode_and_artifact():
    contract = build_task_contract(prompt="做一条微信贴图引流")
    assert contract.content_mode == ContentMode.WECHAT_STICKER_POST
    assert ArtifactKind.WECHAT_STICKER_DOCX in contract.required_outputs
    assert ArtifactKind.FINANCE_DEEP_DOCX not in contract.required_outputs
    assert ArtifactKind.FINANCE_BROAD_DOCX not in contract.required_outputs
    assert ArtifactKind.VISUAL_MANIFEST_JSON in contract.required_outputs


def test_sticker_acceptance_contract_freezes_selected_title():
    contract = build_task_contract(prompt="做一条微信贴图引流", visuals_enabled=False)
    state = WritingState(contract=contract)
    state.working["research"] = _sticker_research().model_dump(mode="json")
    state.working["editorial_plan"] = _sticker_editorial_plan().model_dump(mode="json")
    state.working["headlines"] = _sticker_headlines().model_dump(mode="json")
    frozen = freeze_acceptance_contract(state)
    assert frozen.wechat_sticker is not None
    assert frozen.wechat_sticker.selected_title == "事件变化"
    assert frozen.wechat_sticker.headline_factual_anchor == "经核验的事件事实"
    assert frozen.wechat_sticker.headline_primary_gap == "谁真正兑现"
    assert frozen.wechat_sticker.headline_opening_payoff == "正文立即解释变化与影响"

    payload = StickerPostPayload(
        title="事件变化",
        body="有用信息和一个明确观点。",
        interaction_prompt="你更关注需求还是价格？欢迎留言。",
        risk_disclaimer=_risk(),
        constraints=_snapshot(),
    )
    evidence = validate_draft_against_acceptance(
        state,
        DraftPackage(wechat_sticker_post=payload),
    )
    assert evidence == ["WECHAT_STICKER_POST: title=frozen; headline promises=frozen; platform-specific body contract"]

    changed = payload.model_copy(update={"title": "临时改标题"})
    with pytest.raises(ValueError, match="frozen selected title"):
        validate_draft_against_acceptance(state, DraftPackage(wechat_sticker_post=changed))


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