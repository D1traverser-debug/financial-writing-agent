"""Owner intent provenance and guarded method-evolution replay (no real article output)."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json

import pytest

from financial_writing_agent.standalone_runtime import (
    DOMAIN_ID, FinancialAdmissionError, _blob_sha, admit_article_action,
)
from financial_writing_agent.task_requirements import (
    TaskRequirement, RequirementError, empty_requirement_authority,
    apply_requirement_changes,
)
from test_financial_native_loop_closure_20261112 import Provider

TASK = "financial-goal-governance-sim"
SOURCE = "user-message://verified/2026-11-12/goal-1"
USER_TEXT = "财经Deep必须保留完整公司池。"
CORRECTION_TEXT = "现在明确修正：财经Deep改成只保留最重要的公司。"


def action(p, op, params, *, reader=None, sha=None):
    path = f"workspaces/articles/{TASK}/STATE.json"
    now = p.read(path) if path in p.states else None
    prev = sha if sha is not None else (now["blob_sha"] if now else None)
    return admit_article_action({
        "schema_version": "1.0", "domain_id": DOMAIN_ID,
        "action_id": f"goal-{op}-{len(p.states.get(path, ''))}",
        "task_id": TASK, "operation": op,
        "expected_state_blob_sha": None if op == "CREATE_ARTICLE" else prev,
        "parameters": params,
    }, state_reader=p.read, cas_writer=p.write,
       authorization_verifier=lambda _: True,
       artifact_reader=p.artifact, source_snapshot_reader=p.source,
       owner_instruction_reader=reader,
       owner_semantic_verifier=lambda request: {
           "approved": True,
           "source_sha256": request["source_sha256"],
           "change_sha256": request["change_sha256"],
           "reviewer_principal": "synthetic-trusted-owner-review",
           "assurance": "OWNER_EXPLICITLY_CONFIRMED_EXACT_CHANGE",
       })


def create(p):
    action(p, "CREATE_ARTICLE", {"prompt": "模拟需求治理任务"})
    return p


def requirement(text=USER_TEXT, *, source_kind="USER_EXPLICIT"):
    return {
        "requirement_id": "deep-universe",
        "statement": text,
        "scopes": ["FINANCE_DEEP"],
        "affects_from_stage": "RESEARCH",
        "source_kind": source_kind,
        "evidence_ref": SOURCE,
    }


def _proof(text=USER_TEXT, *, source_ref=SOURCE, intent="USER_REQUIREMENT"):
    return {
        "intent": intent,
        "source_ref": source_ref,
        "verbatim_excerpt": text,
        "classification_reason": "The authenticated user provided an explicit binding instruction.",
    }


def _reader(text=USER_TEXT, *, role="user", ref=SOURCE, forged_sha=False):
    def read(which):
        if which != ref:
            return None
        return {
            "text": text,
            "sha256": "0" * 64 if forged_sha else hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "source_role": role, "source_ref": ref,
            "authenticated_actor": "account-user" if role == "user" else "agent",
        }
    return read


def test_requirement_source_must_not_default_to_user_explicit():
    with pytest.raises(Exception):
        TaskRequirement.model_validate({
            "requirement_id": "fabricated", "statement": "guess",
            "scopes": ["FINANCE_DEEP"], "affects_from_stage": "RESEARCH",
            "evidence_ref": "memory://guess",
        })


def test_suggestion_or_assistant_hypothesis_cannot_mutate_authoritative_user_requirements():
    p = create(Provider())
    first = deepcopy(p.states)
    params = {
        "evidence_ref": SOURCE, "upserts": [requirement()],
        "intent_evidence": _proof(intent="USER_SUGGESTION"),
    }
    with pytest.raises(FinancialAdmissionError, match="INTENT"):
        action(p, "CHANGE_REQUIREMENTS", params, reader=_reader())
    assert p.states == first
    params["intent_evidence"] = _proof()
    with pytest.raises(FinancialAdmissionError, match="INTENT"):
        action(p, "CHANGE_REQUIREMENTS", params, reader=_reader(role="assistant"))
    assert p.states == first


@pytest.mark.parametrize("fault", ["missing_proof", "missing_reader", "not_found", "sha_mismatch",
                                    "quote_not_in_source", "source_mismatch"])
def test_requirement_admission_must_be_backed_by_exact_authenticated_owner_message(fault):
    p = create(Provider())
    before = deepcopy(p.states)
    params = {
        "evidence_ref": SOURCE, "upserts": [requirement()],
        "intent_evidence": _proof(),
    }
    reader = _reader()
    if fault == "missing_proof":
        del params["intent_evidence"]
    if fault == "missing_reader":
        reader = None
    if fault == "not_found":
        reader = _reader(ref="user-message://another")
    if fault == "sha_mismatch":
        reader = _reader(forged_sha=True)
    if fault == "quote_not_in_source":
        params["intent_evidence"]["verbatim_excerpt"] = "用户没有说过这句"
    if fault == "source_mismatch":
        params["intent_evidence"]["source_ref"] = "user-message://wrong"
    with pytest.raises(FinancialAdmissionError, match="INTENT"):
        action(p, "CHANGE_REQUIREMENTS", params, reader=reader)
    assert p.states == before


def test_verified_user_requirement_and_correction_are_versioned_and_replay_at_research():
    p = create(Provider())
    action(p, "CHANGE_REQUIREMENTS", {
        "evidence_ref": SOURCE, "upserts": [requirement()],
        "intent_evidence": _proof(),
    }, reader=_reader())
    path = f"workspaces/articles/{TASK}/STATE.json"
    s = p.read(path)["state"]
    assert s["task_requirement_authority"]["revision"] == 1
    assert s["task_requirement_authority"]["active_requirements"][0]["source_kind"] == "USER_EXPLICIT"
    assert s["execution_receipts"][-1]["input_bindings"]["owner_intent_verification"]["verified"] is True
    assert s["execution_receipts"][-1]["input_bindings"]["owner_intent_verification"]["source_sha256"]
    action(p, "ADVANCE_STAGE", {})
    assert p.read(path)["state"]["current_stage"] == "RESEARCH"
    action(p, "CHANGE_REQUIREMENTS", {
        "evidence_ref": SOURCE, "upserts": [requirement(CORRECTION_TEXT, source_kind="USER_CORRECTION")],
        "intent_evidence": _proof(CORRECTION_TEXT, intent="USER_CORRECTION"),
    }, reader=_reader(CORRECTION_TEXT))
    s = p.read(path)["state"]
    assert s["current_stage"] == "RESEARCH"
    assert s["task_requirement_authority"]["revision"] == 2
    assert [x["action"] for x in s["task_requirement_authority"]["history"]] == ["ADD", "REPLACE"]


def test_ambiguous_delete_and_upsert_same_requirement_is_not_one_silent_replacement():
    raw = empty_requirement_authority()
    raw, _ = apply_requirement_changes(raw, upserts=[requirement()], evidence_ref=SOURCE)
    with pytest.raises(RequirementError, match="simultaneously"):
        apply_requirement_changes(raw, upserts=[requirement("new content")],
                                  retire_ids=["deep-universe"], evidence_ref=SOURCE)


def test_owner_suggestion_is_preserved_as_nonbinding_article_intent_without_changing_goals():
    p = create(Provider())
    before = p.read(f"workspaces/articles/{TASK}/STATE.json")["state"]
    raw = "要不要考虑把Deep写得更短一些？"
    effect = action(p, "RECORD_OWNER_INTENT", {
        "intent_evidence": _proof(raw, intent="USER_SUGGESTION"),
        "summary": "consider a shorter Deep version",
    }, reader=_reader(raw))
    assert effect["child_state_cas_verified"] is True
    after = p.read(f"workspaces/articles/{TASK}/STATE.json")["state"]
    assert after["task_requirement_digest"] == before["task_requirement_digest"]
    assert after["task_requirement_authority"] == before["task_requirement_authority"]
    assert after["intent_history"][-1]["intent"] == "USER_SUGGESTION"
    assert after["intent_history"][-1]["status"] == "OPEN__NONBINDING"
    assert after["execution_receipts"][-1]["capability_id"] == "financial_owner_intent_intake"
    assert after["current_stage"] == before["current_stage"]


def test_owner_idea_with_forged_source_cannot_be_recorded_as_authentic():
    p = create(Provider())
    frozen = deepcopy(p.states)
    raw = "可以想想新的叙事结构"
    with pytest.raises(FinancialAdmissionError, match="INTENT"):
        action(p, "RECORD_OWNER_INTENT", {
            "intent_evidence": _proof(raw, intent="IMPLEMENTATION_IDEA"),
            "summary": "unverified idea",
        }, reader=_reader(raw, role="assistant"))
    assert p.states == frozen
