import pytest
from pydantic import ValidationError

from financial_writing_agent.schemas import ResearchFailure, ResearchPackage


def _base_research():
    return {
        "topic": "电网设备",
        "chronology": ["事件发生"],
        "what_changed": ["订单预期变化"],
        "industry_chain": ["设备→系统→应用"],
        "transmission_chain": ["需求→订单→收入"],
        "universe": [
            {
                "name": "国电南瑞",
                "ticker": "600406",
                "relevance": "电网自动化",
            }
        ],
        "evidence_ledger": [
            {
                "claim": "核心事实",
                "source": "公司公告",
                "core_safe": True,
                "verification_status": "SINGLE_SOURCE_ATTRIBUTED",
                "allowed_wording": "据公司公告",
            }
        ],
        "counterevidence": ["订单存在执行不确定性"],
        "provisional_theses": ["订单增长可能改善收入兑现"],
        "source_boundary": "[FULL] source://announcement",
        "cognition": {
            "concept_map": ["智能电网"],
            "industry_logic": ["电网投资传导至设备订单"],
        },
        "coverage": {
            "sweeps_completed": 2,
            "coverage_status": "SATURATED",
            "material_new_items_last_sweep": 0,
            "concept_coverage": "主要概念已覆盖",
            "company_coverage": "主要公司已覆盖",
            "source_diversity": "公告与行业资料",
            "stop_reason": "第二轮未发现重大新项",
        },
    }


def test_order_book_claim_without_level2_boundary_is_rejected():
    payload = _base_research()
    payload["cognition"]["short_term_market_structure"] = ["封单明显增强"]
    with pytest.raises(ValidationError, match="order-book"):
        ResearchPackage.model_validate(payload)


def test_level2_order_book_claim_requires_real_capability_receipt_and_then_passes():
    payload = _base_research()
    payload["cognition"]["short_term_market_structure"] = ["封单明显增强"]
    payload["market_data_boundary"] = {
        "as_of": "2026-10-08T09:30:00+08:00",
        "data_level": "LEVEL2",
        "source_refs": ["level2://provider/receipt-1"],
        "order_book_available": True,
        "tick_data_available": False,
        "limitations": ["仅核盘口队列，不声称逐笔成交方向"],
    }
    research = ResearchPackage.model_validate(payload)
    assert research.market_data_boundary.data_level == "LEVEL2"
    assert research.market_data_boundary.order_book_available is True


def test_qiangchou_inference_requires_level2_order_book_or_tick_evidence():
    payload = _base_research()
    payload["universe"][0]["fund_flow_signals"] = ["资金明显抢筹"]
    payload["market_data_boundary"] = {
        "as_of": "2026-10-08T09:30:00+08:00",
        "data_level": "STANDARD",
        "source_refs": ["quote://standard/receipt-1"],
    }
    with pytest.raises(ValidationError, match="抢筹"):
        ResearchPackage.model_validate(payload)


def test_same_path_retry_receipt_allows_at_most_one_retry():
    with pytest.raises(ValidationError):
        ResearchFailure(
            failed_action="fetch-source-A",
            failure_reason="temporary error",
            retry_attempts=2,
            impact_on_result="source still missing",
        )

    failure = ResearchFailure(
        failed_action="fetch-source-A",
        failure_reason="temporary error",
        retry_attempts=1,
        alternative_source_or_tool="official mirror",
        impact_on_result="resolved through fallback",
        resolved=True,
    )
    assert failure.retry_attempted is True
    assert failure.retry_attempts == 1


def test_duplicate_failed_action_receipts_must_be_consolidated():
    payload = _base_research()
    receipt = {
        "failed_action": "fetch-source-A",
        "failure_reason": "temporary error",
        "retry_attempts": 1,
        "alternative_source_or_tool": "official mirror",
        "impact_on_result": "fallback used",
        "resolved": True,
    }
    payload["failed_tools_or_sources"] = [receipt, dict(receipt)]
    with pytest.raises(ValidationError, match="duplicate failed_action"):
        ResearchPackage.model_validate(payload)
