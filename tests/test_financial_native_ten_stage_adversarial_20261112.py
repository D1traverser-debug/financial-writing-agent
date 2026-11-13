"""Synthetic full owner-graph replay; deliberately no real finance article.

The negative case verifies DELIVERY never treats a list of made-up Word hashes
as actual delivered products. Business-language or reader-quality PASS is not
asserted from this transport-only simulation.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import struct
import zlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from test_current_admission_v1 import _blueprint, _fitness
from test_financial_native_loop_closure_20261112 import (
    TASK, STATE_PATH, act, make, into_research_audit, stage_artifact,
)
from financial_writing_agent.delivery_pipeline import (
    build_verified_article_docx, build_verified_audit_docx,
    build_verified_interaction_pack_docx, finalize_delivery_evidence,
    render_word_and_review_pages,
)
from financial_writing_agent.document import ArticleDocument, AuditLine, Block
from financial_writing_agent.models import ArtifactKind
from financial_writing_agent.schemas import PlatformInteractionPack


def _prepare_delivery(p):
    into_research_audit(p)
    act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "RESEARCH_AUDIT"), "review_status": "PASS",
    })
    act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "EDITORIAL"),
        "story_blueprints": [_blueprint("FINANCE_DEEP"), _blueprint("FINANCE_BROAD")],
    })
    act(p, "ADVANCE_STAGE", stage_artifact(p, "TITLE"))
    act(p, "ADVANCE_STAGE", stage_artifact(p, "DRAFT"))
    act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "EDITORIAL_AUDIT"), "review_status": "PASS",
        "publication_fitnesses": [_fitness("FINANCE_DEEP"), _fitness("FINANCE_BROAD")],
    })
    assert p.read(STATE_PATH)["state"]["current_stage"] == "DELIVERY"


def _fake_output(kind):
    return {
        "kind": kind,
        "file_name": kind.lower() + ".docx",
        "sha256": "f" * 64,
        "resource_ref": f"workspaces/articles/{TASK}/delivery/{kind.lower()}.docx",
    }


def _png(width=4, height=4):
    def chunk(kind, data):
        return (
            struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\xff\xff\xff" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    )


def _install_fake_renderer(monkeypatch):
    def fake_render(docx_path, render_dir):
        out = Path(render_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{Path(docx_path).stem}.pdf").write_bytes(b"%PDF-1.4 synthetic render")
        page = out / "page-1.png"
        page.write_bytes(_png())
        return [str(page)]
    monkeypatch.setattr("financial_writing_agent.rendering.render_docx_pages", fake_render)


def _word_output(p, kind, tmp_path, monkeypatch, *, task_state=None):
    """Create a canonical build + exact render receipt; all prose is synthetic."""
    from financial_writing_agent.standalone_runtime import _blob_sha

    _install_fake_renderer(monkeypatch)
    output = tmp_path / (kind.lower() + ".docx")
    if kind in {"FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"}:
        article = ArticleDocument(
            title=f"合成测试稿：{kind}",
            stock_names=[],
            blocks=[
                Block(kind="h1", text="合成事实核验"),
                Block(kind="body", text="这是**可检查语义锚点**的合成审稿文本。"),
            ],
        )
        source_text = "这是可检查语义锚点的合成审稿文本。"
        source_ref = f"simulation://delivery-source/{kind}"
        claim_bindings = [{
            "claim_id": f"synthetic-{kind.lower()}",
            "block_index": 1,
            "claim_excerpt": source_text,
            "source_ref": source_ref,
            "source_excerpt": source_text,
        }]
        kwargs = {}
        if kind == "FINANCE_DEEP_DOCX":
            kwargs["research"] = SimpleNamespace(universe=[], company_decision_map=None)
        build = build_verified_article_docx(
            article, output,
            artifact_kind=ArtifactKind(kind),
            required_bold_anchors=["可检查语义锚点"],
            require_risk_disclaimer=False,
            task_state=task_state,
            claim_bindings=claim_bindings,
            source_reader=lambda _: {
                "text": source_text,
                "sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            },
            **kwargs,
        )
    elif kind == "PLATFORM_INTERACTION_PACK_DOCX":
        pack = PlatformInteractionPack.model_validate({
            "topic": "合成测试",
            "posts": [
                {"platform_family": "WECHAT_IMAGE_TEXT", "hook": "测试开头一",
                 "body": "合成互动正文一。", "interaction_prompt": "你的看法是什么？"},
                {"platform_family": "TOUTIAO_MICRO", "hook": "测试开头二",
                 "body": "合成互动正文二。", "interaction_prompt": "你会如何判断？"},
                {"platform_family": "NETEASE_DYNAMIC", "hook": "测试开头三",
                 "body": "合成互动正文三。", "interaction_prompt": "还有哪些变量？"},
            ],
            "evidence_boundary": "仅为合成测试，不构成事实或投资结论。",
            "independent_rewrite_from_long_form": True,
        })
        build = build_verified_interaction_pack_docx(pack, output)
    elif kind == "AUDIT_DOCX":
        build = build_verified_audit_docx(
            title="合成流程验收记录",
            lines=[AuditLine(area="二进制", status="PASS", evidence="文件可读取", notes="合成测试")],
            artifacts=["synthetic://artifact"],
            output=output,
        )
    else:
        raise AssertionError(f"unsupported synthetic output kind: {kind}")

    render = render_word_and_review_pages(
        build, docx_path=output, render_dir=tmp_path / (kind.lower() + "-render"),
        visual_reviewer=lambda event: {
            "status": "PASS", "review_ref": f"synthetic://visual/{kind}/{event['page_index']}",
        },
    )
    if task_state is not None:
        draft = task_state["stage_artifacts"]["DRAFT"]
        source_ref = draft["path"]
        source_identity = f"git-blob:{draft['blob_sha']}"
    else:
        state = p.read(STATE_PATH)["state"]
        draft = state["stage_artifacts"]["DRAFT"]
        source_ref = draft["path"]
        source_identity = f"git-blob:{draft['blob_sha']}"
    finalized = finalize_delivery_evidence(
        build, source_ref=source_ref, source_identity=source_identity,
        render_qa="PASS", visual_qa="PASS", render_inspection_receipt=render,
    )
    resource_ref = f"workspaces/articles/{TASK}/delivery/{kind.lower()}.docx"
    binary = output.read_bytes()
    p.artifacts[resource_ref] = binary
    return {
        "kind": kind,
        "file_name": output.name,
        "sha256": hashlib.sha256(binary).hexdigest(),
        "resource_ref": resource_ref,
        **finalized,
    }


def test_full_ten_stage_admission_rejects_nonexistent_deliverables_before_terminal_state():
    p = make()
    _prepare_delivery(p)
    frozen = deepcopy(p.states)
    with pytest.raises(Exception, match="WORD|DOCX|BINARY|RESOURCE|DELIVERY"):
        act(p, "ADVANCE_STAGE", {
            **stage_artifact(p, "DELIVERY"),
            "delivery_artifacts": [
                _fake_output("FINANCE_DEEP_DOCX"),
                _fake_output("FINANCE_BROAD_DOCX"),
                _fake_output("PLATFORM_INTERACTION_PACK_DOCX"),
            ],
        })
    assert p.states == frozen
    assert p.read(STATE_PATH)["state"]["current_stage"] == "DELIVERY"


def test_entire_ten_stage_graph_with_canonical_rendered_delivery_evidence_and_bounded_terminal(tmp_path, monkeypatch):
    p = make()
    _prepare_delivery(p)
    task_state = p.read(STATE_PATH)["state"]
    article_kinds = ("FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX", "PLATFORM_INTERACTION_PACK_DOCX")
    metadata = [_word_output(p, kind, tmp_path, monkeypatch, task_state=task_state) for kind in article_kinds]
    delivery = act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "DELIVERY"),
        "delivery_artifacts": metadata,
    })
    assert delivery["stage"] == "MECHANICAL_AUDIT"
    assert delivery["product_word_binary_readback"]["verified_count"] == 3
    assert delivery["product_word_binary_readback"]["assurance"].endswith("EDITORIAL_INDEPENDENCE_OPEN")
    assert all(item["rendered_page_count"] == 1 for item in delivery["product_word_binary_readback"]["files"])
    mechanical = act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "MECHANICAL_AUDIT"), "review_status": "PASS",
    })
    assert mechanical["stage"] == "FINAL_AUDIT"
    audit_meta = _word_output(p, "AUDIT_DOCX", tmp_path, monkeypatch)
    final = act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "FINAL_AUDIT"), "review_status": "PASS",
        "audit_artifact": audit_meta,
    })
    assert final["product_word_binary_readback"]["verified_count"] == 4
    state = p.read(STATE_PATH)["state"]
    assert state["status"] == "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN"
    assert set(state["delivery_artifacts"]) == set(state["required_outputs"])
    assert final["independent_editorial_quality_verified"] is False
    assert final["owner_outcome_verified"] is False
    assert len([r for r in state["execution_receipts"] if "TRANSITION" in r["action_id"]]) == 10


@pytest.mark.parametrize("case", ["missing", "wrong_sha", "foreign_task", "bad_zip", "bad_zip_matching_sha", "wrong_blob", "file_name", "resource_reused"])
def test_delivery_binary_boundary_rejects_mutation_without_exact_provider_word_bytes(case):
    p = make()
    _prepare_delivery(p)
    outputs = [_word_output(p, kind) for kind in (
        "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX", "PLATFORM_INTERACTION_PACK_DOCX"
    )]
    first = outputs[0]
    path = first["resource_ref"]
    if case == "missing":
        del p.artifacts[path]
    elif case == "wrong_sha":
        first["sha256"] = "0" * 64
    elif case == "foreign_task":
        first["resource_ref"] = "workspaces/articles/unrelated/delivery/deep.docx"
    elif case == "bad_zip":
        p.artifacts[path] = b"PKbad"
    elif case == "bad_zip_matching_sha":
        import hashlib
        p.artifacts[path] = b"PKbad"
        first["sha256"] = hashlib.sha256(p.artifacts[path]).hexdigest()
    elif case == "file_name":
        first["file_name"] = "wrong.docx"
    elif case == "resource_reused":
        outputs[1]["resource_ref"] = first["resource_ref"]
        outputs[1]["file_name"] = first["file_name"]
        outputs[1]["sha256"] = first["sha256"]
    elif case == "wrong_blob":
        p.artifact = lambda candidate, prior=p.artifact: (
            {"content": p.artifacts[candidate], "blob_sha": "0" * 40}
            if candidate == path else prior(candidate)
        )
    frozen = deepcopy(p.states)
    with pytest.raises(Exception, match="FINANCIAL_WORD"):
        act(p, "ADVANCE_STAGE", {
            **stage_artifact(p, "DELIVERY"), "delivery_artifacts": outputs,
        })
    assert p.states == frozen


def test_final_audit_rereads_all_existing_docx_before_marking_state_terminal(tmp_path, monkeypatch):
    p = make()
    _prepare_delivery(p)
    task_state = p.read(STATE_PATH)["state"]
    outputs = [_word_output(p, kind, tmp_path, monkeypatch, task_state=task_state) for kind in (
        "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX", "PLATFORM_INTERACTION_PACK_DOCX"
    )]
    act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "DELIVERY"), "delivery_artifacts": outputs,
    })
    act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "MECHANICAL_AUDIT"), "review_status": "PASS",
    })
    assert p.read(STATE_PATH)["state"]["current_stage"] == "FINAL_AUDIT"
    p.artifacts[outputs[0]["resource_ref"]] = b"PKtampered-after-delivery"
    audit = _word_output(p, "AUDIT_DOCX", tmp_path, monkeypatch)
    frozen = deepcopy(p.states)
    with pytest.raises(Exception, match="FINANCIAL_WORD"):
        act(p, "ADVANCE_STAGE", {
            **stage_artifact(p, "FINAL_AUDIT"), "review_status": "PASS",
            "audit_artifact": audit,
        })
    assert p.states == frozen
    assert p.read(STATE_PATH)["state"]["status"] == "IN_PROGRESS"
