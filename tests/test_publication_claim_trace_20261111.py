"""Synthetic source-corruption counterexamples and canonical Word integration.

These tests prove digest/paragraph/numeric traceability, not independent
financial truth, source authority, plagiarism clearance or reader acceptance.
"""
import hashlib
from copy import deepcopy
from types import SimpleNamespace

import pytest

from financial_writing_agent.claim_trace import (
    SOURCE_TRACE_ASSURANCE, SourceTraceError, verify_publication_source_trace,
)
from financial_writing_agent.current_admission import build_initial_state
from financial_writing_agent.delivery_pipeline import (
    CanonicalDeliveryError, build_verified_article_docx,
)
from financial_writing_agent.document import ArticleDocument, Block
from financial_writing_agent.models import ArtifactKind

SOURCE_REF = "private://user-material/corporate-issuer-2026-q3"
SOURCE_TEXT = "甲公司2026年收入增长12.3%，但成本变化和利润兑现仍然需要进一步核对。"


def _reader(ref):
    assert ref == SOURCE_REF
    return {"text": SOURCE_TEXT, "sha256": hashlib.sha256(SOURCE_TEXT.encode("utf-8")).hexdigest()}


def _article(body=None):
    return ArticleDocument(
        title="行业账本中的证据差异",
        blocks=[
            Block(kind="h1", text="一、收入不能替代利润"),
            Block(kind="body", text=body or "甲公司2026年收入**增长12.3%**，但这一变化不能保证利润同步兑现。"),
        ],
        stock_names=[],
    )


def _rows():
    return [{
        "claim_id": "revenue-01", "block_index": 1,
        "claim_excerpt": "甲公司2026年收入**增长12.3%**",
        "source_ref": SOURCE_REF, "source_excerpt": SOURCE_TEXT,
    }]


def _state():
    return build_initial_state(
        task_id="financial-source-trace-fixture",
        prompt="合规财经报道", source_refs=[],
        executor_identity="test:financial-source-trace",
    )


def test_actual_snapshot_and_full_public_numeric_tokens_are_traced():
    proof = verify_publication_source_trace(
        _article(), _rows(), source_reader=_reader,
        article_task_id="financial-source-trace-fixture",
    )
    assert proof["read_source_snapshot_count"] == 1
    assert proof["traced_block_count"] == 1
    assert proof["numeric_tokens_matched"] == 2
    assert proof["assurance"] == SOURCE_TRACE_ASSURANCE
    assert proof["semantic_fact_entailment_verified"] is False
    assert proof["primary_source_authority_verified"] is False
    assert SOURCE_REF not in str(proof)
    assert SOURCE_TEXT not in str(proof)
    assert len(proof["article_content_sha256"]) == 64


def test_changing_the_source_snapshot_without_changing_sha_fails_closed():
    def forged(ref):
        good = _reader(ref)
        return {"text": "替换后的来源文字，原始数字已不存在。", "sha256": good["sha256"]}

    with pytest.raises(SourceTraceError, match="SOURCE_TRACE_SOURCE_SNAPSHOT_SHA_MISMATCH"):
        verify_publication_source_trace(
            _article(), _rows(), source_reader=forged,
            article_task_id="financial-source-trace-fixture",
        )


def test_source_reference_label_cannot_replace_real_source_text():
    with pytest.raises(SourceTraceError, match="SOURCE_TRACE_SOURCE_READBACK_MISSING"):
        verify_publication_source_trace(
            _article(), _rows(), source_reader=lambda _: None,
            article_task_id="financial-source-trace-fixture",
        )


def test_source_excerpt_must_actually_occur_in_fetched_provider_snapshot():
    row = _rows()
    row[0]["source_excerpt"] = "甲公司2026年的12.3%出现在另一个并不存在的文件里。"
    with pytest.raises(SourceTraceError, match="SOURCE_TRACE_EXCERPT_NOT_IN_SOURCE_SNAPSHOT"):
        verify_publication_source_trace(
            _article(), row, source_reader=_reader,
            article_task_id="financial-source-trace-fixture",
        )


def test_hallucinated_public_numbers_do_not_pass_even_with_a_real_source():
    wrong_article = _article(
        "甲公司2026年收入**增长12.3%**，预计2027年利润增加50%。"
    )
    with pytest.raises(SourceTraceError, match="SOURCE_TRACE_UNSUPPORTED_PUBLIC_NUMBERS"):
        verify_publication_source_trace(
            wrong_article, _rows(), source_reader=_reader,
            article_task_id="financial-source-trace-fixture",
        )


def test_claim_numeric_token_is_checked_against_its_own_excerpt():
    item = _rows()
    item[0]["source_excerpt"] = "关于甲公司经营与成本变化，需要进一步核对利润兑现情况。"
    def reader(ref):
        return {"text": SOURCE_TEXT + item[0]["source_excerpt"],
                "sha256": hashlib.sha256((SOURCE_TEXT + item[0]["source_excerpt"]).encode()).hexdigest()}
    with pytest.raises(SourceTraceError, match="SOURCE_TRACE_CLAIM_NUMBERS_ABSENT_FROM_SOURCE_EXCERPT"):
        verify_publication_source_trace(
            _article(), item, source_reader=reader,
            article_task_id="financial-source-trace-fixture",
        )


def test_every_substantive_public_paragraph_needs_a_source_ledger_binding():
    article = _article()
    article.blocks.append(Block(kind="body", text="乙公司的经营兑现尚无足够证据。"))
    with pytest.raises(SourceTraceError, match="SOURCE_TRACE_UNSUPPORTED_PUBLIC_PARAGRAPHS"):
        verify_publication_source_trace(
            article, _rows(), source_reader=_reader,
            article_task_id="financial-source-trace-fixture",
        )


def test_numeric_public_title_requires_independently_covered_title_claim():
    article = _article()
    article.title = "2026年行业账本"
    with pytest.raises(SourceTraceError, match="SOURCE_TRACE_UNSUPPORTED_PUBLIC_PARAGRAPHS"):
        verify_publication_source_trace(
            article, _rows(), source_reader=_reader,
            article_task_id="financial-source-trace-fixture",
        )


def test_duplicate_claim_ids_or_boolean_indices_are_never_valid_evidence():
    rows = _rows()
    rows.append(dict(rows[0]))
    with pytest.raises(SourceTraceError, match="SOURCE_TRACE_CLAIM_ID_INVALID_OR_DUPLICATE"):
        verify_publication_source_trace(
            _article(), rows, source_reader=_reader,
            article_task_id="financial-source-trace-fixture",
        )
    rows = _rows()
    rows[0]["block_index"] = True
    with pytest.raises(SourceTraceError, match="SOURCE_TRACE_BLOCK_INDEX_INVALID"):
        verify_publication_source_trace(
            _article(), rows, source_reader=_reader,
            article_task_id="financial-source-trace-fixture",
        )


def test_current_financial_word_build_saves_source_trace_not_private_source_bytes(tmp_path):
    build = build_verified_article_docx(
        _article(), tmp_path / "source-verified.docx",
        artifact_kind=ArtifactKind.FINANCE_DEEP_DOCX,
        required_bold_anchors=["增长12.3%"], require_risk_disclaimer=False,
        task_state=_state(), research=SimpleNamespace(universe=[]),
        claim_bindings=_rows(), source_reader=_reader,
    )
    assert build["task_scope_binding"]["task_id"] == "financial-source-trace-fixture"
    assert build["claim_trace_binding"]["read_source_snapshot_count"] == 1
    assert build["source_trace_assurance"] == SOURCE_TRACE_ASSURANCE
    assert SOURCE_REF not in str(build)
    assert SOURCE_TEXT not in str(build)


def test_current_builder_fails_before_creating_word_if_source_snapshots_are_false(tmp_path):
    target = tmp_path / "unsupported.docx"
    with pytest.raises(CanonicalDeliveryError, match="current source-to-paragraph trace failed"):
        build_verified_article_docx(
            _article(), target,
            artifact_kind=ArtifactKind.FINANCE_DEEP_DOCX,
            required_bold_anchors=["增长12.3%"], require_risk_disclaimer=False,
            task_state=_state(), research=SimpleNamespace(universe=[]),
            claim_bindings=_rows(), source_reader=lambda _: None,
        )
    assert not target.exists()


@pytest.mark.parametrize(
    ("claim_period", "source_period"),
    [
        ("2025年上半年", "2025 H1"),
        ("2025半年度", "2025年上半年"),
        ("2025年第三季度", "2025Q3"),
        ("2025年全年", "2025年度"),
        ("2025年年报", "2025 FY"),
    ],
)
def test_financial_period_synonyms_do_not_create_false_source_conflict(claim_period, source_period):
    from financial_writing_agent.financial_fact_guard import reject_direct_fact_contradictions

    reject_direct_fact_contradictions(
        f"甲公司{claim_period}营业收入增长10%。",
        f"甲公司{source_period}营业收入增长10%。",
    )


@pytest.mark.parametrize(
    ("claim_period", "source_period"),
    [
        ("2025年上半年", "2025 H2"),
        ("2025年第三季度", "2025 Q2"),
        ("2025年全年", "2024年度"),
    ],
)
def test_financial_period_normalization_still_rejects_different_periods(claim_period, source_period):
    from financial_writing_agent.financial_fact_guard import (
        FinancialFactConflict, reject_direct_fact_contradictions,
    )

    with pytest.raises(FinancialFactConflict, match="SOURCE_TRACE_CONFLICT_REPORTING_PERIOD"):
        reject_direct_fact_contradictions(
            f"甲公司{claim_period}营业收入增长10%。",
            f"甲公司{source_period}营业收入增长10%。",
        )


def test_real_publication_source_trace_accepts_equivalent_period_notation_without_certifying_semantics():
    from types import SimpleNamespace
    from financial_writing_agent.claim_trace import verify_publication_source_trace

    claim = "甲公司2025年上半年营业收入增长10%。"
    excerpt = "甲公司2025 H1营业收入增长10%，其它费用仍待核对。"
    article = SimpleNamespace(title="公司财报核对", blocks=[
        SimpleNamespace(kind="body", text=claim),
    ])
    evidence = [{
        "claim_id": "period-1", "block_index": 0, "claim_excerpt": claim,
        "source_ref": "issuer://financial-2025-h1", "source_excerpt": excerpt,
    }]
    snapshot = {"text": excerpt, "sha256": hashlib.sha256(excerpt.encode("utf-8")).hexdigest()}
    result = verify_publication_source_trace(
        article, evidence, article_task_id="period-normalization-check",
        source_reader=lambda ref: snapshot if ref == "issuer://financial-2025-h1" else None,
    )
    assert result["traced_block_count"] == 1
    assert result["primary_source_authority_verified"] is False
    assert result["semantic_fact_entailment_verified"] is False
