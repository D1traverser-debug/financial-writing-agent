"""Synthetic full owner-graph replay; deliberately no real finance article.

The negative case verifies DELIVERY never treats a list of made-up Word hashes
as actual delivered products. Business-language or reader-quality PASS is not
asserted from this transport-only simulation.
"""
from __future__ import annotations

from copy import deepcopy
import pytest

from test_current_admission_v1 import _blueprint, _fitness
from test_financial_native_loop_closure_20261112 import (
    TASK, STATE_PATH, act, make, into_research_audit, stage_artifact,
)


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


def _word_output(p, kind):
    """A genuine DOCX binary whose prose is only a synthetic test marker."""
    from io import BytesIO
    import hashlib
    from docx import Document
    doc = Document()
    doc.add_heading(f"synthetic-only-{kind}", level=1)
    doc.add_paragraph("本文件仅供工作流字节验证，不包含真实金融信息或用户稿件。")
    out = BytesIO()
    doc.save(out)
    binary = out.getvalue()
    resource_ref = f"workspaces/articles/{TASK}/delivery/{kind.lower()}.docx"
    p.artifacts[resource_ref] = binary
    return {
        "kind": kind,
        "file_name": kind.lower() + ".docx",
        "sha256": hashlib.sha256(binary).hexdigest(),
        "resource_ref": resource_ref,
    }


def test_entire_ten_stage_graph_with_genuine_synthetic_word_bytes_and_bounded_terminal():
    p = make()
    _prepare_delivery(p)
    article_kinds = ("FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX", "PLATFORM_INTERACTION_PACK_DOCX")
    metadata = [_word_output(p, kind) for kind in article_kinds]
    delivery = act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "DELIVERY"),
        "delivery_artifacts": metadata,
    })
    assert delivery["stage"] == "MECHANICAL_AUDIT"
    assert delivery["product_word_binary_readback"]["verified_count"] == 3
    assert delivery["product_word_binary_readback"]["assurance"].endswith("PAGE_AND_EDITORIAL_OPEN")
    mechanical = act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "MECHANICAL_AUDIT"), "review_status": "PASS",
    })
    assert mechanical["stage"] == "FINAL_AUDIT"
    audit_meta = _word_output(p, "AUDIT_DOCX")
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


@pytest.mark.parametrize("case", ["missing", "wrong_sha", "foreign_task", "bad_zip", "wrong_blob"])
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
