"""Business-process regression: writing quality stages must be completable.

These provider/Word fixtures are synthetic. A successful graph replay proves
stage coordination and draft export only; it does not prove real editorial
quality, research truth, publication fitness or reader outcome.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib

import pytest

from financial_writing_agent.current_admission import (
    CurrentAdmissionError, _parse_story_blueprints, build_initial_state,
)
from financial_writing_agent.story_quality import PublicationFitness
from financial_writing_agent.standalone_runtime import FinancialAdmissionError, observe_article
from financial_writing_agent.story_quality import ProductMode
from test_current_admission_v1 import _blueprint, _fitness
from test_financial_native_loop_closure_20261112 import (
    TASK, STATE_PATH, act, make, into_research_audit, stage_artifact,
)
from test_financial_native_ten_stage_adversarial_20261112 import _word_output


def test_deep_and_broad_cloned_blueprints_are_rejected_before_drafting():
    state = build_initial_state(
        task_id="portfolio-independent-blueprints",
        prompt="对同一事件准备 Deep 和 Broad，但不能拿 Deep 缩短冒充 Broad。",
        executor_identity="test",
        source_refs=[],
    )
    deep = _blueprint("FINANCE_DEEP")
    broad = _blueprint("FINANCE_BROAD")
    accepted = _parse_story_blueprints(state, [deep, broad])
    assert set(x.product_mode for x in accepted) == {ProductMode.FINANCE_DEEP, ProductMode.FINANCE_BROAD}

    cosmetic_clone = deepcopy(broad)
    for key in ("reader_job", "reader_starting_state", "article_promise",
                "central_question", "narrative_engine", "ending_payoff"):
        cosmetic_clone[key] = deep[key]
    for key in ("concrete_anchor", "reader_information_gap"):
        cosmetic_clone["opening"][key] = deep["opening"][key]
    for idx, section in enumerate(cosmetic_clone["sections"]):
        section["working_heading"] = deep["sections"][idx]["working_heading"]
    with pytest.raises(CurrentAdmissionError, match="BLUEPRINT_NOT_INDEPENDENT"):
        _parse_story_blueprints(state, [deep, cosmetic_clone])


def _internal_fitness(mode: str, draft_raw: bytes):
    raw = _fitness(mode)
    raw["review_scope"] = "INTERNAL_DELIVERY_READINESS"
    raw["assurance"] = "CHAT_SELF_REVIEW"
    raw["audit_provenance"] = {
        "assurance": "CHAT_SELF_REVIEW",
        "reviewer_identity": "chat-self",
        "author_identity": "chat-self",
        "reviewed_article_sha256": hashlib.sha256(draft_raw).hexdigest(),
    }
    return raw


def _to_internal_editorial_audit(p):
    into_research_audit(p)
    act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "RESEARCH_AUDIT"), "review_status": "PASS",
    })
    act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "EDITORIAL"),
        "story_blueprints": [_blueprint("FINANCE_DEEP"), _blueprint("FINANCE_BROAD")],
    })
    act(p, "ADVANCE_STAGE", stage_artifact(p, "TITLE"))
    draft = stage_artifact(p, "DRAFT")
    act(p, "ADVANCE_STAGE", draft)
    return p.artifacts[draft["artifact_path"]]


def test_internal_readiness_draft_sha_is_bound_to_exact_source_bytes():
    raw = _fitness("FINANCE_DEEP")
    raw["review_scope"] = "INTERNAL_DELIVERY_READINESS"
    raw["assurance"] = "CHAT_SELF_REVIEW"
    raw["audit_provenance"] = {
        "assurance": "CHAT_SELF_REVIEW",
        "reviewer_identity": "chat-self",
        "author_identity": "chat-self",
        "reviewed_article_sha256": hashlib.sha256(b"draft").hexdigest(),
    }
    fit = PublicationFitness.model_validate(raw)
    assert fit.review_scope == "INTERNAL_DELIVERY_READINESS"
    assert fit.assurance == "CHAT_SELF_REVIEW"
    assert fit.final_status.value == "PASS"


def test_review_mismatch_blocks_before_state_write_without_weakening_independent_gate():
    p = make()
    draft_raw = _to_internal_editorial_audit(p)
    assert p.read(STATE_PATH)["state"]["current_stage"] == "EDITORIAL_AUDIT"
    old_sha = p.read(STATE_PATH)["blob_sha"]
    deep = _internal_fitness("FINANCE_DEEP", draft_raw)
    broad = _internal_fitness("FINANCE_BROAD", draft_raw)
    broad["audit_provenance"]["reviewed_article_sha256"] = "0" * 64
    with pytest.raises(FinancialAdmissionError, match="INTERNAL_READINESS_WRONG_DRAFT_VERSION"):
        act(p, "ADVANCE_STAGE", {
            **stage_artifact(p, "EDITORIAL_AUDIT"),
            "review_status": "PASS",
            "publication_fitnesses": [deep, broad],
        })
    assert p.read(STATE_PATH)["blob_sha"] == old_sha
    assert p.read(STATE_PATH)["state"]["current_stage"] == "EDITORIAL_AUDIT"


def test_internal_qa_can_complete_full_word_delivery_without_false_independent_certification(tmp_path, monkeypatch):
    p = make()
    draft_raw = _to_internal_editorial_audit(p)
    passed = act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "EDITORIAL_AUDIT"),
        "review_status": "PASS",
        "publication_fitnesses": [
            _internal_fitness("FINANCE_DEEP", draft_raw),
            _internal_fitness("FINANCE_BROAD", draft_raw),
        ],
    })
    assert passed["stage"] == "DELIVERY"
    assert passed["independent_editorial_review_readback"] is None
    readiness = passed["internal_editorial_delivery_readiness"]
    assert readiness["status"] == "WORD_DRAFT_DELIVERY_READY__INDEPENDENT_CERTIFICATION_OPEN"
    assert readiness["reviewed_count"] == 2
    assert readiness["independent_editorial_quality_verified"] is False

    task_state = p.read(STATE_PATH)["state"]
    products = ("FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX", "PLATFORM_INTERACTION_PACK_DOCX")
    produced = [_word_output(p, kind, tmp_path, monkeypatch, task_state=task_state)
                for kind in products]
    delivered = act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "DELIVERY"), "delivery_artifacts": produced,
    })
    assert delivered["stage"] == "MECHANICAL_AUDIT"
    mechanical = act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "MECHANICAL_AUDIT"), "review_status": "PASS",
    })
    assert mechanical["stage"] == "FINAL_AUDIT"
    final = act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "FINAL_AUDIT"),
        "review_status": "PASS",
        "audit_artifact": _word_output(p, "AUDIT_DOCX", tmp_path, monkeypatch),
        "supplemental_delivery_artifacts": [
            _word_output(p, "PRIVATE_RESEARCH_DOCX", tmp_path, monkeypatch),
        ],
    })
    assert final["product_word_binary_readback"]["verified_count"] == 4
    observed = observe_article(TASK, state_reader=p.read, effect_receipt_reader=p.read_effect)
    assert observed["business_status"] == "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN"
    assert final["independent_editorial_quality_verified"] is False
    assert final["owner_outcome_verified"] is False


def test_git_business_change_audit_collects_method_detached_effect_paths(monkeypatch):
    import scripts.system_acceptance_report as report

    captured = []
    def fake_git(cmd, **_kwargs):
        captured.append(cmd)
        return b"knowledge/actions/isolated-method.effect.json\0"

    monkeypatch.setenv("FINANCIAL_CHANGE_BASE_SHA", "a" * 40)
    monkeypatch.setattr("subprocess.check_output", fake_git)
    with pytest.raises(SystemExit, match="METHOD_EFFECT_CHANGED_WITHOUT_CATALOG_REVISION"):
        report._audit_git_business_effects("b" * 40)

    assert captured
    assert captured[0][-3:] == [
        "workspaces/articles",
        "knowledge/METHOD_KNOWLEDGE_CATALOG.json",
        "knowledge/actions",
    ]
