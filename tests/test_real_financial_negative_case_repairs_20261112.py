"""Negative business regressions: current system must reject audited false passes."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from financial_writing_agent.company_identity import (
    CompanyIdentityError, canonical_company_name, canonical_ticker,
    require_retained_universe_reconciliation, task_retained_universe_baseline,
)
from financial_writing_agent.claim_trace import SourceTraceError, verify_publication_source_trace
from financial_writing_agent.document import ArticleDocument, Block
from financial_writing_agent.financial_fact_guard import FinancialFactConflict, reject_direct_fact_contradictions
from financial_writing_agent.task_publication import TaskPublicationError, verify_task_publication_scope

ROOT = Path(__file__).resolve().parents[1]
V3_PATH = ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v3/STATE.json"


def _real_v3():
    return json.loads(V3_PATH.read_text(encoding="utf-8"))


def _small_research():
    cls = "跨境卖家"
    return SimpleNamespace(
        universe=[
            SimpleNamespace(name="甲公司", ticker="300866", materiality="MATERIAL", value_chain_class=cls),
            SimpleNamespace(name="乙公司", ticker="300773", materiality="MATERIAL", value_chain_class=cls),
            SimpleNamespace(name="丙公司", ticker="002315", materiality="REFERENCE_ONLY", value_chain_class="营销"),
        ],
        company_decision_map=object(),
        universe_coverage=SimpleNamespace(status="COMPLETE", classes=[
            SimpleNamespace(included_companies=["甲公司", "乙公司"]),
            SimpleNamespace(included_companies=["丙公司"]),
        ]),
    )


def _small_article():
    return ArticleDocument(
        title="经营和利润实现路径",
        stock_names=["甲公司", "乙公司", "丙公司"],
        blocks=[
            Block(kind="h1", text="一、经营收入差异"),
            Block(kind="body", text="甲公司收入兑现强于乙公司；乙公司现金流更慢，库存成本较高。"),
            Block(kind="body", text="丙公司是间接概念标签，缺乏直接收入兑现证据。"),
        ],
    )


def test_current_owner_174_company_task_cannot_be_shrunk_to_three():
    with pytest.raises(TaskPublicationError, match="TASK_RETAINED_UNIVERSE_TRUNCATED"):
        verify_task_publication_scope(_real_v3(), _small_article(), _small_research())


def test_full_baseline_174_tickers_is_packaged_and_decidable():
    base = task_retained_universe_baseline(_real_v3()["task_id"])
    assert base is not None and len(base["required_companies"]) == 174
    assert len({v["ticker"] for v in base["required_companies"]}) == 174
    assert canonical_company_name("生 意 宝") == "生意宝"
    assert canonical_ticker("002095.SZ") == "002095"
    assert any(v["name"] == "新华都" for v in base["required_companies"])


def test_ticker_name_cannot_be_changed_silently_in_retained_universe():
    base = task_retained_universe_baseline("cross-border-ecommerce-20261016-v3")
    research = _small_research()
    research.universe = [
        SimpleNamespace(ticker=r["ticker"], name=r["name"])
        for r in base["required_companies"]
    ]
    receipt = require_retained_universe_reconciliation("cross-border-ecommerce-20261016-v3", research)
    assert receipt["baseline_required_count"] == 174
    research.universe[0].name = "并非原来的公司"
    with pytest.raises(CompanyIdentityError, match="IDENTITY_MISMATCH"):
        require_retained_universe_reconciliation("cross-border-ecommerce-20261016-v3", research)


def test_issuer_name_spacing_no_longer_falsely_fails_competing_company_paragraph():
    from financial_writing_agent.checks import paragraph_has_named_economic_comparison
    assert paragraph_has_named_economic_comparison(
        "焦点科技的业务兑现强于生意宝，其收入质量更稳健。",
        ["生 意 宝", "焦点科技"],
    )


@pytest.mark.parametrize(
    ("claim", "source", "marker"),
    [
        ("甲公司2026年营业收入同比增长20%", "甲公司2026年营业收入同比下降20%", "DIRECTION"),
        ("甲公司2026年上半年收入增长20%", "甲公司2026年第三季度收入增长20%", "PERIOD"),
        ("甲公司2026年营业收入20亿元", "甲公司2026年营业收入20万元", "UNIT"),
        ("公司订单增加，收入仍待核对", "公司订单减少，收入仍待核对", "DIRECTION"),
    ],
)
def test_contradictory_financial_language_is_never_marked_source_trace_pass(claim, source, marker):
    with pytest.raises(FinancialFactConflict, match=marker):
        reject_direct_fact_contradictions(claim, source)


def test_actual_source_trace_does_not_accept_growth_vs_decline_inversion():
    source = "甲公司2026年营业收入同比下降20%，主要由于订单减少。"
    article = SimpleNamespace(
        title="方向核验",
        blocks=[SimpleNamespace(kind="body", text="甲公司2026年营业收入同比增长20%，主要由于订单增加。")],
    )
    with pytest.raises(SourceTraceError, match="SOURCE_TRACE_CONFLICT_FINANCIAL_DIRECTION"):
        verify_publication_source_trace(
            article,
            [{
                "claim_id":"false-direction", "block_index":0,
                "claim_excerpt":"甲公司2026年营业收入同比增长20%",
                "source_ref":"test://issuer", "source_excerpt":source,
            }],
            source_reader=lambda _: {
                "text":source,
                "sha256":hashlib.sha256(source.encode()).hexdigest(),
            },
            article_task_id="test-hard-negative",
        )
