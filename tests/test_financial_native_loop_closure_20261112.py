"""Financial-only owner-native action-closure replay.

These are deterministic synthetic state-transition tests, not financial articles,
external authorization proof, or independent editorial certification.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_writing_agent.private_research import REQUIRED_MODULES
from financial_writing_agent.standalone_runtime import (
    DOMAIN_ID, FinancialAdmissionError, _blob_sha,
    admit_article_action, observe_article,
)
from trusted_provider_testkit import signed_action_authorization
from test_current_admission_v1 import EDITORIAL_ATTESTATIONS

FIXTURE = Path(__file__).resolve().parents[1] / "evals/FINANCIAL_WRITING_KERNEL_DECISION_ENVELOPE_2026-10-15.json"
TASK = "synthetic-financial-loop"
STATE_PATH = f"workspaces/articles/{TASK}/STATE.json"


class Provider:
    def __init__(self):
        self.states = {}
        self.artifacts = {}
        self.sources = {}

    def read(self, path):
        raw = self.states.get(path)
        return None if raw is None else {
            "state": json.loads(raw), "blob_sha": _blob_sha(raw), "content": raw
        }

    def write(self, path, expected, content):
        old = self.states.get(path)
        if expected is None:
            if old is not None:
                raise RuntimeError("create-only")
        elif old is None or _blob_sha(old) != expected:
            raise RuntimeError("CAS stale")
        self.states[path] = content
        return {"blob_sha": _blob_sha(content), "commit_ref": "synthetic-provider"}

    def artifact(self, path):
        raw = self.artifacts.get(path)
        return None if raw is None else {"content": raw, "blob_sha": _blob_sha(raw)}

    def source(self, ref):
        return self.sources.get(ref)


def act(p, operation, params=None, *, auth=None, sha=None):
    expected = p.read(STATE_PATH)["blob_sha"] if sha is None and p.read(STATE_PATH) else sha
    def editorial_verifier(request):
        return EDITORIAL_ATTESTATIONS[request["execution_ref"]]
    return admit_article_action({
        "schema_version": "1.0", "domain_id": DOMAIN_ID,
        "action_id": f"synthetic-{operation.lower()}-{len(p.states.get(STATE_PATH, ''))}",
        "task_id": TASK, "operation": operation,
        "expected_state_blob_sha": expected if operation != "CREATE_ARTICLE" else None,
        "parameters": params or {},
    }, state_reader=p.read, cas_writer=p.write,
       authorization_verifier=auth or signed_action_authorization,
       artifact_reader=p.artifact, source_snapshot_reader=p.source,
       independent_editorial_verifier=editorial_verifier)


def test_requirement_satisfaction_source_refs_require_actual_readback_and_do_not_claim_semantic_support():
    from financial_writing_agent.standalone_runtime import _verify_requirement_satisfaction_sources

    satisfaction = [{
        "requirement_id": "full_universe_research_pool",
        "result": "SATISFIED",
        "evidence_refs": ["source://issuer-universe"],
        "notes": "synthetic only",
    }]
    with pytest.raises(FinancialAdmissionError, match="SATISFACTION_UNREAD_SOURCE"):
        _verify_requirement_satisfaction_sources(satisfaction, {"snapshots": []})
    readback = _verify_requirement_satisfaction_sources(
        satisfaction,
        {"snapshots": [{
            "source_ref_sha256": hashlib.sha256(
                b"source://issuer-universe"
            ).hexdigest(),
            "body_sha256": "a" * 64,
            "source_family": "issuer-filing",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }]},
    )
    assert readback["checked_evidence_ref_count"] == 1
    assert readback["semantic_support_verified"] is False
    assert readback["assurance"] == "SOURCE_BYTE_READBACK_ONLY__SEMANTIC_SUPPORT_NOT_CERTIFIED"


def test_requirement_satisfaction_must_bind_the_actual_current_stage_artifact():
    from financial_writing_agent.standalone_runtime import _verify_requirement_satisfaction_sources

    satisfaction = [{
        "requirement_id": "draft-structure",
        "result": "SATISFIED",
        "evidence_refs": ["source://issuer-universe"],
    }]
    sources = {"snapshots": [{
        "source_ref_sha256": hashlib.sha256(b"source://issuer-universe").hexdigest(),
        "body_sha256": "a" * 64,
        "source_family": "issuer-filing",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }]}
    with pytest.raises(FinancialAdmissionError, match="CURRENT_STAGE_ARTIFACT_NOT_BOUND"):
        _verify_requirement_satisfaction_sources(
            satisfaction, sources,
            stage_artifact_path="workspaces/articles/synthetic-financial-loop/stages/DRAFT.json",
        )

    satisfaction[0]["evidence_refs"].append(
        "workspaces/articles/synthetic-financial-loop/stages/DRAFT.json"
    )
    proof = _verify_requirement_satisfaction_sources(
        satisfaction, sources,
        stage_artifact_path="workspaces/articles/synthetic-financial-loop/stages/DRAFT.json",
    )
    assert proof["checked_evidence_ref_count"] == 2
    assert proof["semantic_support_verified"] is False


def make():
    p = Provider()
    act(p, "CREATE_ARTICLE", {"prompt": "Synthetic financial systems transition replay"})
    return p


def stage_artifact(p, name):
    path = f"workspaces/articles/{TASK}/stages/{name}.json"
    data = json.dumps({"stage": name, "synthetic": True}).encode()
    p.artifacts[path] = data
    return {"artifact_key": name, "artifact_path": path, "artifact_blob_sha": _blob_sha(data)}


def into_research_audit(p):
    act(p, "ADVANCE_STAGE")
    now = datetime.now(timezone.utc).isoformat()
    brief = {
        "contract_version": "1.1", "as_of": now,
        "coverage_state": "COMPLETE", "unresolved_gaps": [],
        "modules": {
            name: {
                "status": "APPLICABLE", "summary": f"synthetic only {name}",
                "evidence_refs": [f"simulation://source/{i}"],
            } for i, name in enumerate(REQUIRED_MODULES)
        },
    }
    for i, _ in enumerate(REQUIRED_MODULES):
        data = f"Synthetic provider source {i} with complete byte and hash readback."
        p.sources[f"simulation://source/{i}"] = {
            "text": data,
            "sha256": hashlib.sha256(data.encode()).hexdigest(),
            "retrieved_at": now,
            "source_family": "ISSUER" if i % 2 else "REGULATOR",
        }
    decision = json.loads(FIXTURE.read_text(encoding="utf-8"))
    act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "RESEARCH"),
        "decision_envelope": decision, "private_research_brief": brief,
    })
    assert observe_article(TASK, state_reader=p.read)["stage"] == "RESEARCH_AUDIT"


def block(p, target="RESEARCH"):
    return act(p, "ADVANCE_STAGE", {
        **stage_artifact(p, "RESEARCH_AUDIT"), "review_status": "FAIL",
        "revision_target": target,
    })


def test_full_native_fail_recover_replay_invalidates_upstream_and_rechecks_cas():
    p = make()
    into_research_audit(p)
    failed = block(p)
    assert failed["business_status"] == "BLOCKED"
    frozen = deepcopy(p.states)
    with pytest.raises(Exception):
        act(p, "ADVANCE_STAGE")
    assert p.states == frozen
    with pytest.raises(FinancialAdmissionError, match="AUTHORIZATION_NOT_VERIFIED"):
        act(p, "RESUME_BLOCKED", {"repair_evidence": ["simulation://repair"]},
            auth=lambda _: False)
    assert p.states == frozen
    with pytest.raises(FinancialAdmissionError, match="EXPECTED_STATE_BLOB_REQUIRED|STATE_CHANGED_CONCURRENTLY"):
        act(p, "RESUME_BLOCKED", {"repair_evidence": ["simulation://repair"]}, sha="f" * 40)
    assert p.states == frozen
    with pytest.raises(Exception, match="repair_evidence"):
        act(p, "RESUME_BLOCKED", {"repair_evidence": []})
    assert p.states == frozen
    effect = act(p, "RESUME_BLOCKED", {"repair_evidence": ["simulation://repair", "simulation://negative-test"]})
    assert effect["stage"] == "RESEARCH"
    assert effect["child_state_cas_verified"] is True
    recovered = p.read(STATE_PATH)["state"]
    assert recovered["status"] == "IN_PROGRESS"
    assert recovered["stage_artifacts"] == {}
    assert recovered["quality_evidence"] == {}
    assert recovered["recovery_history"][-1]["resume_target"] == "RESEARCH"
    assert "RESUME_BLOCKED" in recovered["execution_receipts"][-1]["action_id"]
    with pytest.raises(Exception):
        act(p, "RESUME_BLOCKED", {"repair_evidence": ["simulation://wrong-stage"]})


def test_illegal_blocking_cursor_is_rejected_before_remote_mutation():
    p = make()
    into_research_audit(p)
    frozen = deepcopy(p.states)
    with pytest.raises(Exception, match="FAIL.*revision_target"):
        block(p, "TITLE")
    assert p.states == frozen


def test_proactive_resolution_is_an_authorized_article_action_with_readback():
    p = make()
    result = act(p, "RECORD_PROACTIVE_RESOLUTION", {
        "target": "missing-company-evidence",
        "attempted_sources": ["simulation://company-registry"],
        "evidence_refs": ["simulation://company-registry/record"],
        "outcome": "PROVISIONAL", "candidate": "review and compare",
        "confidence": "LOW", "validation_plan": ["compare issuer report"],
        "safe_to_continue": True,
    })
    assert result["child_state_cas_verified"] is True
    state = p.read(STATE_PATH)["state"]
    assert state["proactive_resolution_history"][-1]["outcome"] == "PROVISIONAL"
    assert state["current_stage"] == "INTAKE"
    assert "PROACTIVE_RESOLUTION" in state["execution_receipts"][-1]["action_id"]


def _impact_params():
    return {
        "signal_id": "synthetic-impact-1",
        "problem_statement": "missing finance loop recovery route",
        "root_cause_layer": "PRODUCT_CAPABILITY",
        "generalization_scope": "standalone action interface",
        "alternatives": [
            {"mechanism": "reuse native owner loop", "failure_mode": "adapter integration risk"},
            {"mechanism": "duplicate new controller", "failure_mode": "two sources of authority"},
        ],
        "selected_mechanism": "reuse native owner loop",
        "selection_rationale": "single owner plus authenticated CAS",
        "authority_surface": "financial_writing_agent.standalone_runtime",
        "regression_or_eval_plan": ["synthetic fail/resume and feedback replay"],
        "evidence_refs": ["simulation://failure/reproduction"],
        "decision": "NO_CHANGE_WITH_REASON",
        "decision_reason": "simulated dry review with no external changes",
    }


def test_feedback_impact_review_closes_using_one_authorized_state_owner():
    p = make()
    act(p, "ATTACH_FEEDBACK", {
        "sample": {"sample_type": "USER_REJECTION", "summary": "simulation negative"},
        "system_impact": {"signal_id": "synthetic-impact-1", "status": "OPEN",
                          "trigger_sample_type": "USER_REJECTION"},
    })
    previous = p.read(STATE_PATH)["blob_sha"]
    with pytest.raises(FinancialAdmissionError, match="AUTHORIZATION_NOT_VERIFIED"):
        act(p, "REVIEW_SYSTEM_IMPACT", _impact_params(), auth=lambda _: False)
    assert p.read(STATE_PATH)["blob_sha"] == previous
    receipt = act(p, "REVIEW_SYSTEM_IMPACT", _impact_params())
    assert receipt["child_state_cas_verified"] is True
    state = p.read(STATE_PATH)["state"]
    assert state["open_system_impact"] == []
    assert state["system_impact_history"][-1]["review"]["decision"] == "NO_CHANGE_WITH_REASON"
    assert "SYSTEM_IMPACT_REVIEW" in state["execution_receipts"][-1]["action_id"]
    with pytest.raises(Exception):
        act(p, "REVIEW_SYSTEM_IMPACT", _impact_params())


def test_read_only_observation_reports_real_blocker_and_next_action():
    p = make()
    act(p, "ATTACH_FEEDBACK", {
        "sample": {"sample_type": "USER_REJECTION", "summary": "synthetic improvement request"},
        "system_impact": {"signal_id": "synthetic-open-obligation", "status": "OPEN",
                          "trigger_sample_type": "USER_REJECTION"},
    })
    into_research_audit(p)
    block(p)
    before = deepcopy(p.states)
    observation = observe_article(TASK, state_reader=p.read)
    assert observation["next_action"]
    assert observation["blocked_recovery_target"] == "RESEARCH"
    assert observation["open_system_impact"] == [{"signal_id": "synthetic-open-obligation", "status": "OPEN"}]
    assert observation["active_requirement_ids"] == []
    assert p.states == before
