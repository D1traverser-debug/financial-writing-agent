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
