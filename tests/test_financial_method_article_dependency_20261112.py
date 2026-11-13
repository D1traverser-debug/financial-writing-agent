"""Provider-bound article/method interlock; synthetic only, no finance articles."""
import json
from copy import deepcopy

import pytest

from financial_writing_agent.method_governance import CATALOG_PATH
from financial_writing_agent.standalone_runtime import (
    FinancialAdmissionError, admit_article_action,
)
from trusted_provider_testkit import signed_action_authorization
from test_standalone_financial_runtime_20261111 import (
    Provider, create, run, proposal, research_proposal,
)
from test_financial_method_governance_20261112 import (
    METHOD_ID, original, method, mutate, promotion_verifier,
)

ARTICLE = "solo-article-01"
STATE_PATH = f"workspaces/articles/{ARTICLE}/STATE.json"


def _active_catalog():
    cat, _ = mutate(original(), "CREATE", proposed=method())
    cat, _ = mutate(cat, "PROMOTE", promotion_evidence={
        "validation_refs": ["synthetic-ci://exact-change-test"],
        "review_ref": "simulation://independent-review",
    }, promotion_verifier=promotion_verifier)
    return cat


def _catalog_write(p, catalog):
    p.store[CATALOG_PATH] = json.dumps(catalog, ensure_ascii=False, sort_keys=True) + "\n"


def _native_action(p, operation, *, parameters=None, reader=None, grant=True):
    return admit_article_action(
        proposal(operation, sha=p.read(STATE_PATH)["blob_sha"],
                 params=parameters or {}, task_id=ARTICLE),
        state_reader=p.read, cas_writer=p.write,
        authorization_verifier=signed_action_authorization if grant else (lambda _: False),
        artifact_reader=p.artifact, source_snapshot_reader=p.source,
        method_catalog_reader=p.read if reader is None else reader,
    )


def _used_method_state():
    p = Provider()
    create(p)
    _catalog_write(p, _active_catalog())
    run(p, proposal("ADVANCE_STAGE", sha=p.read(STATE_PATH)["blob_sha"], task_id=ARTICLE))
    research = research_proposal(p)
    research["parameters"]["decision_envelope"]["learned_items"] = [METHOD_ID]
    observed = admit_article_action(
        research,
        state_reader=p.read, cas_writer=p.write,
        authorization_verifier=signed_action_authorization,
        artifact_reader=p.artifact, source_snapshot_reader=p.source,
        method_catalog_reader=p.read,
    )
    assert observed["stage"] == "RESEARCH_AUDIT"
    return p


def _review_artifact(p):
    path = f"workspaces/articles/{ARTICLE}/reviews/RESEARCH_AUDIT.json"
    body = b'{"synthetic_research_review":"PASS"}'
    p.artifacts[path] = body
    from financial_writing_agent.standalone_runtime import _blob_sha
    return {
        "artifact_key": "RESEARCH_AUDIT",
        "artifact_path": path,
        "artifact_blob_sha": _blob_sha(body),
        "review_status": "PASS",
    }


def test_used_method_has_exact_catalog_provenance_receipt_and_unrelated_edit_does_not_reopen():
    p = _used_method_state()
    prior = p.read(STATE_PATH)["state"]
    receipt = next(x for x in reversed(prior["execution_receipts"]) if x["stage"] == "RESEARCH")
    assert receipt["input_bindings"]["method_usage_snapshot"]["methods"][0]["knowledge_id"] == METHOD_ID
    assert receipt["input_bindings"]["method_catalog_blob_sha"] == p.read(CATALOG_PATH)["blob_sha"]
    cat = p.read(CATALOG_PATH)["state"]
    different = method()
    different["knowledge_id"] = "METHOD-SYNTHETIC-UNRELATED"
    cat, _ = mutate(cat, "CREATE", method_id=different["knowledge_id"], proposed=different)
    _catalog_write(p, cat)
    advanced = _native_action(p, "ADVANCE_STAGE", parameters=_review_artifact(p))
    assert advanced["stage"] == "EDITORIAL"
    assert advanced["method_usage_readback"]["stale_methods"] == []


def test_retired_method_prevents_stale_work_and_reopens_earliest_affected_stage():
    p = _used_method_state()
    old = p.read(STATE_PATH)["state"]
    before_digest = old["task_requirement_digest"]
    retired, _ = mutate(p.read(CATALOG_PATH)["state"], "RETIRE")
    _catalog_write(p, retired)
    frozen = deepcopy(p.store)
    with pytest.raises(FinancialAdmissionError, match="METHOD_DEPENDENCY_STALE"):
        _native_action(p, "ADVANCE_STAGE", parameters=_review_artifact(p))
    assert p.store == frozen
    with pytest.raises(FinancialAdmissionError, match="AUTHORIZATION"):
        _native_action(p, "REOPEN_METHOD_DEPENDENCY", grant=False)
    assert p.store == frozen
    reopened = _native_action(p, "REOPEN_METHOD_DEPENDENCY")
    assert reopened["stage"] == "RESEARCH"
    new = p.read(STATE_PATH)["state"]
    assert new["task_requirement_digest"] == before_digest
    assert new["task_requirement_authority"] == old["task_requirement_authority"]
    assert new["stage_artifacts"] == {}
    assert new["quality_evidence"] == {}
    assert new["method_dependency_reopen_history"][-1]["changed_methods"][0]["knowledge_id"] == METHOD_ID
    assert new["execution_receipts"][:-1] == old["execution_receipts"]


def test_method_catalog_omission_cannot_be_bypassed_when_knowledge_is_claimed_in_research():
    p = Provider()
    create(p)
    run(p, proposal("ADVANCE_STAGE", sha=p.read(STATE_PATH)["blob_sha"], task_id=ARTICLE))
    research = research_proposal(p)
    research["parameters"]["decision_envelope"]["learned_items"] = [METHOD_ID]
    frozen = deepcopy(p.store)
    with pytest.raises(FinancialAdmissionError, match="METHOD_CATALOG"):
        admit_article_action(
            research, state_reader=p.read, cas_writer=p.write,
            authorization_verifier=signed_action_authorization,
            artifact_reader=p.artifact, source_snapshot_reader=p.source,
            method_catalog_reader=None,
        )
    assert p.store == frozen


def test_method_reopen_not_admitted_without_real_dependency_change():
    p = _used_method_state()
    frozen = deepcopy(p.store)
    with pytest.raises(FinancialAdmissionError, match="NO_DEPENDENCY_CHANGE"):
        _native_action(p, "REOPEN_METHOD_DEPENDENCY")
    assert p.store == frozen
