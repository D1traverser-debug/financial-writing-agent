"""Executable regression for live cross-border v3 task/publication scope binding.

All company names and economic phrases below are synthetic test data. Passing
these tests proves deterministic contract behavior, not primary-source truth.
"""
import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

from financial_writing_agent.current_admission import apply_task_requirement_change
from financial_writing_agent.delivery_availability import _current_deep_task_requirement_ids
from financial_writing_agent.delivery_pipeline import (
    CanonicalDeliveryError, build_verified_article_docx, finalize_delivery_evidence,
)
from financial_writing_agent.document import ArticleDocument, Block
from financial_writing_agent.models import ArtifactKind
from financial_writing_agent.task_publication import (
    FULL_UNIVERSE_REQUIREMENT, TaskPublicationError, verify_task_publication_scope,
)

ROOT = Path(__file__).resolve().parents[1]


def _v3():
    return json.loads(
        (ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v3/STATE.json")
        .read_text(encoding="utf-8")
    )


def _company(name, *, materiality="MATERIAL", cls="跨境卖家"):
    return SimpleNamespace(name=name, materiality=materiality, value_chain_class=cls)


def _research():
    companies = [
        _company("甲公司"), _company("乙公司"),
        _company("丙公司", materiality="REFERENCE_ONLY", cls="营销"),
    ]
    classes = [
        SimpleNamespace(included_companies=["甲公司", "乙公司"]),
        SimpleNamespace(included_companies=["丙公司"]),
    ]
    return SimpleNamespace(
        universe=companies, company_decision_map=object(),
        universe_coverage=SimpleNamespace(status="COMPLETE", classes=classes),
    )


def _article(*, include_weak=True, weak_reason=True):
    blocks = [
        Block(kind="h1", text="经营变化与兑现差异"),
        Block(kind="body", text="甲公司收入兑现强于乙公司；乙公司库存成本更高，现金回流更慢。"),
    ]
    if include_weak:
        blocks.append(
            Block(kind="body", text="丙公司只是间接概念标签，缺乏直接营收兑现证据。"
                  if weak_reason else "丙公司也值得讨论。")
        )
    return ArticleDocument(
        title="公司经济性比较", blocks=blocks,
        stock_names=["甲公司", "乙公司", "丙公司"],
    )


def test_actual_v3_task_requires_full_visible_retained_universe():
    state = _v3()
    assert _current_deep_task_requirement_ids(state) == [FULL_UNIVERSE_REQUIREMENT]
    result = verify_task_publication_scope(state, _article(), _research())
    assert result["task_id"] == state["task_id"]
    assert result["strict_universe_visibility"] is True
    assert result["company_names_checked"] == 3
    assert result["validated_requirement_ids"] == [FULL_UNIVERSE_REQUIREMENT]
    assert "STRUCTURAL" in result["assurance"]


def test_weak_retained_company_cannot_silently_disappear_from_full_universe_deep():
    with pytest.raises(TaskPublicationError, match="including non-material"):
        verify_task_publication_scope(_v3(), _article(include_weak=False), _research())


def test_weak_incidental_name_needs_explicit_visible_reason_not_just_name_dump():
    with pytest.raises(TaskPublicationError, match="weak/incidental retained company lacks visible explanation"):
        verify_task_publication_scope(_v3(), _article(weak_reason=False), _research())


def test_empty_or_not_complete_private_universe_cannot_be_presented_as_full():
    research = _research()
    research.universe_coverage.status = "BOUNDED_WITH_GAPS"
    with pytest.raises(TaskPublicationError, match="status=COMPLETE"):
        verify_task_publication_scope(_v3(), _article(), research)


def test_full_universe_checks_class_accounting_not_just_visibility():
    research = _research()
    research.universe_coverage.classes[1].included_companies = []
    with pytest.raises(TaskPublicationError, match="no included value-chain classification"):
        verify_task_publication_scope(_v3(), _article(), research)


def test_segment_specific_economic_verdict_required_even_when_global_pair_exists():
    research = _research()
    research.universe += [_company("丁公司", cls="海外仓"), _company("戊公司", cls="海外仓")]
    research.universe_coverage.classes.append(SimpleNamespace(included_companies=["丁公司", "戊公司"]))
    article = _article()
    article.blocks.append(Block(kind="body", text="丁公司和戊公司均涉及海外仓。"))
    article.stock_names.extend(["丁公司", "戊公司"])
    with pytest.raises(TaskPublicationError, match="full-universe segment lacks named economic comparison: 海外仓"):
        verify_task_publication_scope(_v3(), article, research)


def test_unknown_task_scope_cannot_be_autocertified_as_met():
    state = apply_task_requirement_change(
        _v3(), previous_state_blob_sha="a" * 40,
        executor_identity="TEST:OWNER", evidence_ref="chat://user/manual",
        upserts=[{
            "requirement_id": "new-semantic-check-not-implemented",
            "statement": "指定来源和叙事形式必须重新验证",
            "scopes": ["FINANCE_DEEP"], "affects_from_stage": "DRAFT",
            "evidence_ref": "chat://user/manual", "source_kind": "USER_EXPLICIT",
        }],
    )
    with pytest.raises(TaskPublicationError, match="unimplemented FINANCE_DEEP task requirements"):
        verify_task_publication_scope(state, _article(), _research())


def test_same_state_structural_success_not_proof_of_editorial_or_fact_verification():
    result = verify_task_publication_scope(_v3(), _article(), _research())
    assert result["observed_stage"] == "RESEARCH"
    assert "NOT_INDEPENDENTLY_VERIFIED" in result["assurance"]


def test_signed_word_receipt_has_actual_v3_digest_but_pre_audit_cannot_be_released(tmp_path):
    state = _v3()
    build = build_verified_article_docx(
        _article(), tmp_path / "cross-border-scope-test.docx",
        artifact_kind=ArtifactKind.FINANCE_DEEP_DOCX,
        required_bold_anchors=[],
        require_risk_disclaimer=False,
        task_state=state, research=_research(),
    )
    assert build["task_scope_binding"]["requirement_digest"] == state["task_requirement_digest"]
    assert build["task_scope_binding"]["company_names_checked"] == 3
    with pytest.raises(CanonicalDeliveryError, match="admitted editorial audit and DELIVERY stage"):
        finalize_delivery_evidence(
            build,
            source_ref=f"workspaces/articles/{state['task_id']}/publication/FINANCE_DEEP.json",
            source_identity="git-blob:synthetic",
            render_qa="PASS", visual_qa="PASS",
        )


def test_generic_builder_never_claims_task_scope_when_not_given_state(tmp_path):
    build = build_verified_article_docx(
        _article(), tmp_path / "generic.docx",
        artifact_kind=ArtifactKind.FINANCE_DEEP_DOCX,
        required_bold_anchors=[], require_risk_disclaimer=False,
    )
    assert build["task_scope_assurance"] == "NOT_CHECKED"
    assert "task_scope_binding" not in build


def test_builder_cannot_accept_research_without_authoritative_task_state(tmp_path):
    with pytest.raises(CanonicalDeliveryError, match="research without task_state"):
        build_verified_article_docx(
            _article(), tmp_path / "bad.docx",
            artifact_kind=ArtifactKind.FINANCE_DEEP_DOCX,
            required_bold_anchors=[], require_risk_disclaimer=False,
            research=_research(),
        )
