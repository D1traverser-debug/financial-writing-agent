"""Render/visual QA cannot be self-issued by passing two PASS strings.

Synthetic page fixtures exercise receipt integrity. A separate CI render smoke
must still execute LibreOffice and pdftoppm on real Word output.
"""
import hashlib
import struct
import zlib
from pathlib import Path

import pytest

from financial_writing_agent.claim_trace import verify_publication_source_trace
from financial_writing_agent.delivery_pipeline import (
    CanonicalDeliveryError, _issue_build_receipt,
    build_verified_article_docx, finalize_delivery_evidence,
    render_word_and_review_pages, validate_delivery_evidence,
)
from financial_writing_agent.document import ArticleDocument, Block
from financial_writing_agent.models import ArtifactKind


def _png(width=2, height=2):
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data +
                struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\xff\xff\xff" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def _build(tmp_path):
    article = ArticleDocument(
        title="测试", stock_names=[],
        blocks=[
            Block(kind="h1", text="事实比较"),
            Block(kind="body", text="这是一段包含**可检查语义锚点**的审稿文本。"),
        ],
    )
    path = tmp_path / "deep.docx"
    build = build_verified_article_docx(
        article, path, artifact_kind=ArtifactKind.FINANCE_DEEP_DOCX,
        required_bold_anchors=["可检查语义锚点"],
        require_risk_disclaimer=False,
    )
    return path, build


def _fake_renderer(monkeypatch, page_count=2):
    def impl(docx_path, render_dir):
        out = Path(render_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{Path(docx_path).stem}.pdf").write_bytes(b"%PDF-1.4 fixture")
        paths = []
        for i in range(1, page_count + 1):
            page = out / f"page-{i}.png"
            page.write_bytes(_png())
            paths.append(str(page))
        return paths
    monkeypatch.setattr("financial_writing_agent.rendering.render_docx_pages", impl)


def _reviewer(data):
    assert data["page_png_bytes"].startswith(b"\x89PNG")
    assert len(data["page_sha256"]) == 64
    return {"status": "PASS", "review_ref": f"test://visual-review/page-{data['page_index']}"}


def _task_bound_receipt(original):
    body = {k: v for k, v in original.items() if k not in ("builder_attestation", "builder_receipt_version")}
    body["task_scope_binding"] = {
        "task_id": "article-render-test", "requirement_digest": "f" * 64,
        "requirement_revision": 1, "mode": "FINANCE_DEEP",
        "validated_requirement_ids": ["deep_complete_retained_universe"],
        "strict_universe_visibility": True, "company_names_checked": 3,
        "observed_stage": "DELIVERY",
        "draft_artifact_path": "workspaces/articles/article-render-test/stages/DRAFT.json",
        "draft_artifact_blob_sha": "a" * 40,
        "assurance": "STRUCTURAL_TASK_SCOPE_ONLY__FACTS_AND_EDITORIAL_NOT_INDEPENDENTLY_VERIFIED",
    }
    # Synthetic reviewer-independent source binding. This fixture exercises
    # signed wiring; it is not an externally verified financial article.
    source_text = "这是一段包含可检查语义锚点的审稿文本，供渲染联调。"
    article = ArticleDocument(
        title="测试", stock_names=[],
        blocks=[
            Block(kind="h1", text="事实比较"),
            Block(kind="body", text="这是一段包含**可检查语义锚点**的审稿文本。"),
        ],
    )
    body["claim_trace_binding"] = verify_publication_source_trace(
        article, [{
            "claim_id": "fixture-anchor",
            "block_index": 1,
            "claim_excerpt": "这是一段包含**可检查语义锚点**的审稿文本",
            "source_ref": "test://synthetic/anchor",
            "source_excerpt": source_text,
        }],
        source_reader=lambda _: {
            "text": source_text, "sha256": hashlib.sha256(source_text.encode()).hexdigest(),
        },
        article_task_id="article-render-test",
    )
    return _issue_build_receipt(body)


def test_current_task_fails_closed_if_only_render_visual_pass_strings(monkeypatch, tmp_path):
    _fake_renderer(monkeypatch)
    path, built = _build(tmp_path)
    bound = _task_bound_receipt(built)
    with pytest.raises(CanonicalDeliveryError, match="CURRENT_WORD_RENDER_RECEIPT_REQUIRED"):
        finalize_delivery_evidence(
            bound, source_ref="workspaces/articles/article-render-test/stages/DRAFT.json",
            source_identity="git-blob:" + "a" * 40, render_qa="PASS", visual_qa="PASS",
        )


def test_renderer_requires_a_reviewer_and_same_actual_docx_bytes(monkeypatch, tmp_path):
    _fake_renderer(monkeypatch)
    path, built = _build(tmp_path)
    with pytest.raises(CanonicalDeliveryError, match="CURRENT_WORD_VISUAL_REVIEWER_REQUIRED"):
        render_word_and_review_pages(built, docx_path=path, render_dir=tmp_path / "render", visual_reviewer=None)
    path.write_bytes(path.read_bytes() + b"extra bytes")
    with pytest.raises(CanonicalDeliveryError, match="CURRENT_WORD_BINARY_HASH_MISMATCH"):
        render_word_and_review_pages(built, docx_path=path, render_dir=tmp_path / "render", visual_reviewer=_reviewer)


def test_each_page_must_be_accepted_and_cannot_be_hidden(monkeypatch, tmp_path):
    _fake_renderer(monkeypatch, page_count=2)
    path, built = _build(tmp_path)
    with pytest.raises(CanonicalDeliveryError, match="CURRENT_WORD_PAGE_2_VISUAL_REVIEW_NOT_ACCEPTED"):
        render_word_and_review_pages(
            built, docx_path=path, render_dir=tmp_path / "render",
            visual_reviewer=lambda event: (
                {"status": "PASS", "review_ref": "test://page1"} if event["page_index"] == 1
                else {"status": "OPEN", "review_ref": "test://page2"}
            ),
        )


def test_task_bound_word_requires_actual_two_page_receipt_and_detects_tampering(monkeypatch, tmp_path):
    _fake_renderer(monkeypatch, page_count=2)
    path, built = _build(tmp_path)
    bound = _task_bound_receipt(built)
    proof = render_word_and_review_pages(
        bound, docx_path=path, render_dir=tmp_path / "render", visual_reviewer=_reviewer,
    )
    assert proof["rendered_page_count"] == 2
    assert proof["review_assurance"] == "CALLER_SUPPLIED_REVIEW__INDEPENDENCE_NOT_ESTABLISHED"
    assert [page["page_index"] for page in proof["pages"]] == [1, 2]
    kwargs = {
        "source_ref": "workspaces/articles/article-render-test/stages/DRAFT.json",
        "source_identity": "git-blob:" + "a" * 40, "render_qa": "PASS", "visual_qa": "PASS",
    }
    valid = finalize_delivery_evidence(bound, **kwargs, render_inspection_receipt=proof)
    validate_delivery_evidence({
        "kind": "FINANCE_DEEP_DOCX", "sha256": built["sha256"], **valid,
    })
    corrupted = dict(proof)
    corrupted["pages"] = list(proof["pages"])[:1]
    with pytest.raises(CanonicalDeliveryError, match="CURRENT_WORD_RENDER_RECEIPT_NOT_ISSUED_THIS_SESSION"):
        finalize_delivery_evidence(bound, **kwargs, render_inspection_receipt=corrupted)
    other = {**proof, "artifact_sha256": "a" * 64}
    with pytest.raises(CanonicalDeliveryError, match="CURRENT_WORD_RENDER_RECEIPT_NOT_ISSUED_THIS_SESSION"):
        finalize_delivery_evidence(bound, **kwargs, render_inspection_receipt=other)


def test_corrupt_page_magic_cannot_become_visual_pass(monkeypatch, tmp_path):
    def fake(docx_path, render_dir):
        out = Path(render_dir)
        out.mkdir(parents=True)
        (out / f"{Path(docx_path).stem}.pdf").write_bytes(b"%PDF-1.4 fixture")
        path = out / "page-1.png"
        path.write_bytes(b"not a png")
        return [str(path)]
    monkeypatch.setattr("financial_writing_agent.rendering.render_docx_pages", fake)
    path, built = _build(tmp_path)
    with pytest.raises(CanonicalDeliveryError, match="CURRENT_WORD_PAGE_1_NOT_PNG"):
        render_word_and_review_pages(
            built, docx_path=path, render_dir=tmp_path / "render", visual_reviewer=_reviewer,
        )


def test_current_word_with_real_render_but_no_source_snapshot_is_not_deliverable(monkeypatch, tmp_path):
    _fake_renderer(monkeypatch, page_count=2)
    path, built = _build(tmp_path)
    bound = _task_bound_receipt(built)
    unsigned = {k: v for k, v in bound.items() if k not in ("builder_attestation", "builder_receipt_version")}
    unsigned.pop("claim_trace_binding")
    no_source = _issue_build_receipt(unsigned)
    proof = render_word_and_review_pages(
        no_source, docx_path=path, render_dir=tmp_path / "render",
        visual_reviewer=_reviewer,
    )
    with pytest.raises(CanonicalDeliveryError, match="CURRENT_WORD_SOURCE_TRACE_REQUIRED"):
        finalize_delivery_evidence(
            no_source, source_ref="workspaces/articles/article-render-test/publication/DEEP.json",
            source_identity="git-blob:synthetic", render_qa="PASS", visual_qa="PASS",
            render_inspection_receipt=proof,
        )
