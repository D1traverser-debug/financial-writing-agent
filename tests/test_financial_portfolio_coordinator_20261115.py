from __future__ import annotations

import json
from types import SimpleNamespace


import pytest

from financial_writing_agent import current_admission, portfolio_coordinator, standalone_runtime
from financial_writing_agent.portfolio_coordinator import PortfolioCoordinatorError
from financial_writing_agent.standalone_runtime import FinancialAdmissionError
from financial_writing_agent.writing_kernel import WritingPass
from test_current_admission_v1 import _brief, _decision
from test_financial_portfolio_execution_20261114 import _executor, _seed
from test_financial_portfolio_requirement_governance_20261114 import (
    _contexts,
    _requirement,
    _start,
)


def _store_provider():
    store: dict[str, bytes] = {}
    writes: list[dict[str, bytes]] = []

    def reader(path: str):
        if path not in store:
            return None
        content = store[path]
        return {
            "content": content,
            "blob_sha": standalone_runtime._blob_sha(content),
        }

    def writer(files):
        batch = dict(files)
        writes.append(batch)
        for path, content in batch.items():
            if path in store and store[path] != content:
                raise RuntimeError("immutable provider path already contains different bytes")
        store.update(batch)
        return {
            "blob_shas": {
                path: standalone_runtime._blob_sha(content)
                for path, content in batch.items()
            }
        }

    return store, reader, writer, writes


def test_artifact_bundle_write_is_idempotent_after_successful_persistence():
    _, reader, writer, writes = _store_provider()
    files = {
        "workspaces/articles/task-1/stages/RESEARCH-a.json": b'{"stage":"RESEARCH"}',
        "workspaces/articles/task-1/portfolio/contexts/1-a.json": b'{"stage":"RESEARCH_AUDIT"}',
    }

    first = portfolio_coordinator._write_and_verify_bundle(
        files,
        writer=writer,
        artifact_reader=reader,
        context_reader=reader,
        context_path="workspaces/articles/task-1/portfolio/contexts/1-a.json",
    )
    second = portfolio_coordinator._write_and_verify_bundle(
        files,
        writer=writer,
        artifact_reader=reader,
        context_reader=reader,
        context_path="workspaces/articles/task-1/portfolio/contexts/1-a.json",
    )

    assert first == second
    assert len(writes) == 1
    assert set(first) == set(files)


def test_artifact_bundle_write_recovers_when_provider_committed_but_lost_response():
    store, reader, _, _ = _store_provider()
    files = {
        "workspaces/articles/task-1/stages/RESEARCH-a.json": b'{"stage":"RESEARCH"}',
        "workspaces/articles/task-1/portfolio/contexts/1-a.json": b'{"stage":"RESEARCH_AUDIT"}',
    }

    def write_then_lose_response(batch):
        store.update(dict(batch))
        raise TimeoutError("provider committed, response was lost")

    verified = portfolio_coordinator._write_and_verify_bundle(
        files,
        writer=write_then_lose_response,
        artifact_reader=reader,
        context_reader=reader,
        context_path="workspaces/articles/task-1/portfolio/contexts/1-a.json",
    )

    assert set(verified) == set(files)
    assert all(store[path] == content for path, content in files.items())


def test_partial_bundle_write_fails_closed_then_retry_writes_only_missing_objects():
    store, reader, writer, writes = _store_provider()
    files = {
        "workspaces/articles/task-1/stages/RESEARCH-a.json": b'{"stage":"RESEARCH"}',
        "workspaces/articles/task-1/portfolio/contexts/1-a.json": b'{"stage":"RESEARCH_AUDIT"}',
    }

    def partial_write(batch):
        first_path = next(iter(batch))
        store[first_path] = batch[first_path]
        raise TimeoutError("partial provider commit")

    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_ARTIFACT_BUNDLE_WRITE_OUTCOME_UNKNOWN",
    ):
        portfolio_coordinator._write_and_verify_bundle(
            files,
            writer=partial_write,
            artifact_reader=reader,
            context_reader=reader,
            context_path="workspaces/articles/task-1/portfolio/contexts/1-a.json",
        )

    verified = portfolio_coordinator._write_and_verify_bundle(
        files,
        writer=writer,
        artifact_reader=reader,
        context_reader=reader,
        context_path="workspaces/articles/task-1/portfolio/contexts/1-a.json",
    )
    assert set(verified) == set(files)
    assert len(writes) == 1
    assert len(writes[0]) == 1


def test_artifact_bundle_never_overwrites_conflicting_immutable_bytes():
    store, reader, writer, _ = _store_provider()
    path = "workspaces/articles/task-1/stages/RESEARCH-a.json"
    store[path] = b'{"stage":"DRAFT"}'

    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_ARTIFACT_BUNDLE_EXISTING_BYTES_CONFLICT",
    ):
        portfolio_coordinator._write_and_verify_bundle(
            {path: b'{"stage":"RESEARCH"}'},
            writer=writer,
            artifact_reader=reader,
            context_reader=reader,
            context_path="unused-context-path",
        )


def test_resume_refreshes_scoped_requirement_projection_even_when_digest_is_unchanged():
    old_requirement = _requirement("old-scope-rule", ["RESEARCH"], "RESEARCH")
    new_requirement = _requirement("new-scope-rule", ["RESEARCH"], "RESEARCH")
    context = _start([old_requirement])
    digest = context["requirement_digest"]
    fresh_contexts = _contexts(digest, [new_requirement])

    refreshed = portfolio_coordinator._refresh_context_requirements(
        context,
        requirement_digest=digest,
        requirement_contexts=fresh_contexts,
        owner_stage="RESEARCH",
    )

    assert refreshed["requirement_digest"] == digest
    assert refreshed["requirement_contexts"] == fresh_contexts
    assert refreshed["requirement_contexts"] != context["requirement_contexts"]


def _portfolio_research_artifact():
    task_id = "task-1"
    digest = "a" * 64
    receipt_sha = "b" * 64
    outputs = {
        "research_package": {"topic": "typed package fixture"},
        "company_decision_map": {"fixture": "same admitted decision"},
        "change_conditions": ["fixture condition"],
    }
    stage_result = {
        "stage": "RESEARCH",
        "status": "PASS",
        "revision_target": None,
        "requirement_satisfaction": [],
        "stage_outputs": outputs,
    }
    artifact = {
        "schema_version": "1.0",
        "artifact_type": "FINANCIAL_PORTFOLIO_BUSINESS_STAGE",
        "task_id": task_id,
        "stage": "RESEARCH",
        "requirement_digest": digest,
        "owner_state_stage_before": "RESEARCH",
        "stage_result": stage_result,
        "payload": outputs,
        "pass_receipt_sha256s": [receipt_sha],
        "assurance": (
            "TYPED_STAGE_OUTPUT_ENVELOPE__OWNER_ADMISSION_AND_PROVIDER_READBACK_REQUIRED"
        ),
    }
    content = (
        json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    blob_sha = standalone_runtime._blob_sha(content)
    path = f"workspaces/articles/{task_id}/stages/RESEARCH-{receipt_sha}.json"
    candidate = {
        "task_id": task_id,
        "task_requirement_digest": digest,
        "execution_receipts": [{
            "stage": "RESEARCH",
            "input_bindings": {
                "required_artifact_key": "RESEARCH",
                "required_artifact_blob_sha": blob_sha,
                "portfolio_context_ref": {"path": "context-ref-present"},
            },
        }],
        "stage_artifacts": {"RESEARCH": {"path": path, "blob_sha": blob_sha}},
        "required_outputs": ["AUDIT_DOCX", "FINANCE_DEEP_DOCX"],
        "task_requirement_authority": {"active_requirements": []},
    }
    return artifact, content, blob_sha, path, candidate


def test_coordinator_research_envelope_validates_nested_typed_research_package(monkeypatch):
    artifact, content, blob_sha, path, candidate = _portfolio_research_artifact()
    candidate["task_requirement_authority"]["active_requirements"] = [{
        "requirement_id": "full_universe_research_pool",
        "statement": "Retain the full requested company universe.",
        "scopes": ["FINANCE_DEEP"],
        "affects_from_stage": "RESEARCH",
        "evidence_ref": "owner-instruction://full-universe",
        "source_kind": "USER_EXPLICIT",
    }]
    captured = []

    def fake_validate(value, company_decision_map, change_conditions):
        captured.append((value, company_decision_map, change_conditions))
        return SimpleNamespace(
            value=value,
            company_decision_map=SimpleNamespace(
                model_dump=lambda mode: company_decision_map,
                change_conditions=change_conditions,
            ),
        )

    monkeypatch.setattr(
        standalone_runtime, "validate_full_universe_decision_handoff", fake_validate,
    )
    monkeypatch.setattr(
        standalone_runtime,
        "require_retained_universe_reconciliation",
        lambda task_id, research: {"task_id": task_id, "verified": True},
    )

    result = standalone_runtime._verify_stage_bytes(
        candidate,
        lambda requested: (
            {"content": content, "blob_sha": blob_sha}
            if requested == path else None
        ),
    )

    assert captured == [(
        artifact["payload"]["research_package"],
        artifact["payload"]["company_decision_map"],
        artifact["payload"]["change_conditions"],
    )]
    assert result["retained_universe_reconciliation"] == {
        "task_id": "task-1",
        "verified": True,
    }
    assert result["portfolio_stage_artifact"] == artifact


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("artifact_type", "WRONG_TYPE", "FINANCIAL_PORTFOLIO_STAGE_ARTIFACT_TYPE_INVALID"),
        ("task_id", "other-task", "FINANCIAL_PORTFOLIO_STAGE_ARTIFACT_OWNER_BINDING_MISMATCH"),
        ("stage", "DRAFT", "FINANCIAL_PORTFOLIO_STAGE_ARTIFACT_OWNER_BINDING_MISMATCH"),
        ("requirement_digest", "c" * 64, "FINANCIAL_PORTFOLIO_STAGE_ARTIFACT_OWNER_BINDING_MISMATCH"),
        ("payload", {"research_package": {"wrong": True}}, "FINANCIAL_PORTFOLIO_STAGE_ARTIFACT_PAYLOAD_MISMATCH"),
    ],
)
def test_portfolio_stage_artifact_rejects_wrong_type_or_owner_binding(
    monkeypatch, field, value, message,
):
    artifact, content, blob_sha, path, candidate = _portfolio_research_artifact()
    artifact[field] = value
    changed = (
        json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    changed_sha = standalone_runtime._blob_sha(changed)
    candidate["execution_receipts"][-1]["input_bindings"]["required_artifact_blob_sha"] = changed_sha
    candidate["stage_artifacts"]["RESEARCH"]["blob_sha"] = changed_sha

    with pytest.raises(FinancialAdmissionError, match=message):
        standalone_runtime._verify_stage_bytes(
            candidate,
            lambda requested: (
                {"content": changed, "blob_sha": changed_sha}
                if requested == path else None
            ),
        )


def test_portfolio_stage_artifact_readback_must_match_context_and_trace():
    artifact, _, blob_sha, path, candidate = _portfolio_research_artifact()
    stage_bytes = {
        "path": path,
        "verified_blob_sha": blob_sha,
        "portfolio_stage_artifact": artifact,
    }
    context = {
        "task_id": "task-1",
        "requirement_digest": "a" * 64,
        "last_stage_result": artifact["stage_result"],
        "trace": [{
            "business_stage": "RESEARCH",
            "receipt_sha256": "b" * 64,
        }],
    }

    result = standalone_runtime._verify_portfolio_stage_artifact_context(
        stage_bytes, context, candidate,
    )
    assert result["stage"] == "RESEARCH"
    assert result["pass_receipt_count"] == 1
    assert result["assurance"] == "EXACT_PROVIDER_BYTES__CONTEXT__OWNER_OUTCOME_CROSS_BINDING"

    tampered_context = dict(context)
    tampered_context["trace"] = [{
        "business_stage": "RESEARCH",
        "receipt_sha256": "d" * 64,
    }]
    with pytest.raises(
        FinancialAdmissionError,
        match="FINANCIAL_PORTFOLIO_STAGE_ARTIFACT_CONTEXT_CROSS_BINDING_MISMATCH",
    ):
        standalone_runtime._verify_portfolio_stage_artifact_context(
            stage_bytes, tampered_context, candidate,
        )


def test_portfolio_stage_review_outcome_must_match_owner_admission():
    task_id = "task-1"
    digest = "a" * 64
    pass_sha = "b" * 64
    stage = "RESEARCH_AUDIT"
    outputs = {"research_audit_result": {"status": "REVISE"}}
    stage_result = {
        "stage": stage,
        "status": "REVISE",
        "revision_target": "RESEARCH",
        "requirement_satisfaction": [],
        "stage_outputs": outputs,
    }
    artifact = {
        "schema_version": "1.0",
        "artifact_type": "FINANCIAL_PORTFOLIO_BUSINESS_STAGE",
        "task_id": task_id,
        "stage": stage,
        "requirement_digest": digest,
        "owner_state_stage_before": stage,
        "stage_result": stage_result,
        "payload": outputs,
        "pass_receipt_sha256s": [pass_sha],
        "assurance": "TYPED_STAGE_OUTPUT_ENVELOPE__OWNER_ADMISSION_AND_PROVIDER_READBACK_REQUIRED",
    }
    path = f"workspaces/articles/{task_id}/stages/{stage}-{pass_sha}.json"
    stage_bytes = {
        "path": path,
        "verified_blob_sha": "c" * 40,
        "portfolio_stage_artifact": artifact,
    }
    context = {
        "task_id": task_id,
        "requirement_digest": digest,
        "last_stage_result": stage_result,
        "trace": [{"business_stage": stage, "receipt_sha256": pass_sha}],
    }
    candidate = {
        "task_id": task_id,
        "task_requirement_digest": digest,
        "execution_receipts": [{
            "stage": stage,
            "input_bindings": {"review_status": "PASS"},
        }],
    }

    with pytest.raises(
        FinancialAdmissionError,
        match="FINANCIAL_PORTFOLIO_STAGE_OUTCOME_OWNER_BINDING_MISMATCH",
    ):
        standalone_runtime._verify_portfolio_stage_artifact_context(
            stage_bytes, context, candidate,
        )

    candidate["execution_receipts"][-1]["input_bindings"] = {
        "review_status": "REVISE",
        "revision_target": "RESEARCH",
    }
    result = standalone_runtime._verify_portfolio_stage_artifact_context(
        stage_bytes, context, candidate,
    )
    assert result["owner_outcome_verified"] is True


def test_portfolio_stage_requirement_satisfaction_must_match_owner_receipt():
    artifact, _, blob_sha, path, candidate = _portfolio_research_artifact()
    stage_result = {
        **artifact["stage_result"],
        "requirement_satisfaction": [{
            "requirement_id": "deep-complete",
            "result": "SATISFIED",
            "evidence_refs": ["source-ref://deep-complete"],
            "notes": "checked against the retained universe",
        }],
    }
    artifact["stage_result"] = stage_result
    context = {
        "task_id": "task-1",
        "requirement_digest": "a" * 64,
        "last_stage_result": stage_result,
        "trace": [{"business_stage": "RESEARCH", "receipt_sha256": "b" * 64}],
    }
    stage_bytes = {
        "path": path,
        "verified_blob_sha": blob_sha,
        "portfolio_stage_artifact": artifact,
    }
    candidate["execution_receipts"][-1]["input_bindings"]["task_requirement_satisfaction"] = [{
        "requirement_id": "deep-complete",
        "requirement_sha256": "d" * 64,
        "result": "SATISFIED",
        "evidence_refs": ["source-ref://deep-complete", path],
        "notes": "checked against the retained universe",
    }]

    result = standalone_runtime._verify_portfolio_stage_artifact_context(
        stage_bytes, context, candidate,
    )
    assert result["requirement_satisfaction_count"] == 1

    candidate["execution_receipts"][-1]["input_bindings"]["task_requirement_satisfaction"][0]["evidence_refs"] = [
        "source-ref://deep-complete", " source-ref://deep-complete ", path,
    ]
    with pytest.raises(
        FinancialAdmissionError,
        match="FINANCIAL_PORTFOLIO_STAGE_REQUIREMENT_SATISFACTION_INVALID",
    ):
        standalone_runtime._verify_portfolio_stage_artifact_context(
            stage_bytes, context, candidate,
        )

    candidate["execution_receipts"][-1]["input_bindings"]["task_requirement_satisfaction"][0]["evidence_refs"] = [
        "source-ref://different-evidence", path,
    ]
    with pytest.raises(
        FinancialAdmissionError,
        match="FINANCIAL_PORTFOLIO_STAGE_REQUIREMENT_SATISFACTION_OWNER_BINDING_MISMATCH",
    ):
        standalone_runtime._verify_portfolio_stage_artifact_context(
            stage_bytes, context, candidate,
        )


def test_changed_provider_bytes_are_rejected_even_when_reader_claims_old_sha():
    _, content, blob_sha, path, candidate = _portfolio_research_artifact()
    changed = content + b"tampered"
    with pytest.raises(
        FinancialAdmissionError,
        match="FINANCIAL_STAGE_ARTIFACT_BYTES_SHA_MISMATCH",
    ):
        standalone_runtime._verify_stage_bytes(
            candidate,
            lambda requested: (
                {"content": changed, "blob_sha": blob_sha}
                if requested == path else None
            ),
        )


def _serialized_owner_state(state):
    content = json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + chr(10)
    return {
        "state": state,
        "blob_sha": standalone_runtime._blob_sha(content),
        "content": content,
    }


def _coordinator_dependencies(monkeypatch, state, admission):
    store, artifact_reader, artifact_writer, writes = _store_provider()
    state_path = standalone_runtime._state_path(state["task_id"])
    state_record = _serialized_owner_state(state)
    proposals = []

    def state_reader(path):
        return state_record if path == state_path else None

    def fake_admit(proposal, **kwargs):
        proposals.append(proposal)
        return {
            "task_id": proposal["task_id"],
            "action_id": proposal["action_id"],
            **admission,
        }

    monkeypatch.setattr(standalone_runtime, "admit_article_action", fake_admit)
    return {
        "state_reader": state_reader,
        "artifact_reader": artifact_reader,
        "portfolio_context_reader": artifact_reader,
        "artifact_bundle_writer": artifact_writer,
        "authorization_verifier": lambda request: None,
        "bundle_cas_writer": lambda *args: {},
        "effect_attestation_signer": lambda claims: None,
        "effect_receipt_reader": lambda path: None,
    }, store, writes, proposals


def _valid_research_executor(calls):
    fallback = _executor(calls)

    def execute(node, inputs):
        result = fallback(node, inputs)
        if node == WritingPass.PRIVATE_RESEARCH_SYNTHESIS:
            result["private_research_brief"] = _brief()
        elif node == WritingPass.THESIS_ADJUDICATION:
            result["decision_envelope"] = _decision()
        return result

    return execute


def test_run_next_portfolio_stage_intake_persists_context_and_requires_owner_readback(monkeypatch):
    task_id = "coordinator-intake-test"
    state = current_admission.build_initial_state(
        task_id=task_id,
        prompt="Write a financial article",
        source_refs=[],
        executor_identity="test",
    )
    deps, store, writes, proposals = _coordinator_dependencies(
        monkeypatch,
        state,
        {
            "stage": "RESEARCH",
            "business_status": "IN_PROGRESS",
            "child_state_cas_verified": True,
            "effect_receipt_readback_verified": True,
        },
    )

    result = portfolio_coordinator.run_next_portfolio_stage(
        task_id,
        seed_inputs=_seed(),
        **deps,
    )

    assert result["executed_stage"] == "INTAKE"
    assert result["next_stage"] == "RESEARCH"
    assert result["stage_artifact_ref"] is None
    assert result["portfolio_context_ref"]["path"] in store
    assert len(writes) == 1
    assert proposals[0]["parameters"]["portfolio_context_ref"] == result["portfolio_context_ref"]


@pytest.mark.parametrize(
    ("admission", "message"),
    [
        (
            {
                "stage": "EDITORIAL",
                "business_status": "IN_PROGRESS",
                "child_state_cas_verified": True,
                "effect_receipt_readback_verified": True,
            },
            "PORTFOLIO_OWNER_ADMISSION_STAGE_READBACK_MISMATCH",
        ),
        (
            {
                "stage": "RESEARCH",
                "business_status": "IN_PROGRESS",
                "child_state_cas_verified": True,
                "effect_receipt_readback_verified": False,
            },
            "PORTFOLIO_OWNER_ADMISSION_EFFECT_READBACK_NOT_VERIFIED",
        ),
    ],
)
def test_run_next_portfolio_stage_intake_rejects_incomplete_owner_admission(
    monkeypatch, admission, message,
):
    task_id = "coordinator-intake-reject"
    state = current_admission.build_initial_state(
        task_id=task_id,
        prompt="Write a financial article",
        source_refs=[],
        executor_identity="test",
    )
    deps, _, _, _ = _coordinator_dependencies(monkeypatch, state, admission)

    with pytest.raises(PortfolioCoordinatorError, match=message):
        portfolio_coordinator.run_next_portfolio_stage(
            task_id,
            seed_inputs=_seed(),
            **deps,
        )


def test_run_next_portfolio_stage_research_executes_one_stage_and_binds_both_readbacks(monkeypatch):
    task_id = "coordinator-research-test"
    state = current_admission.build_initial_state(
        task_id=task_id,
        prompt="Write a financial article",
        source_refs=[],
        executor_identity="test",
    )
    state = current_admission.advance_state(
        state,
        previous_state_blob_sha="s0",
        executor_identity="test",
    )
    deps, store, writes, proposals = _coordinator_dependencies(
        monkeypatch,
        state,
        {
            "stage": "RESEARCH_AUDIT",
            "business_status": "IN_PROGRESS",
            "child_state_cas_verified": True,
            "effect_receipt_readback_verified": True,
        },
    )
    calls = []

    result = portfolio_coordinator.run_next_portfolio_stage(
        task_id,
        seed_inputs=_seed(),
        execute_pass=_valid_research_executor(calls),
        **deps,
    )

    assert result["executed_stage"] == "RESEARCH"
    assert result["next_stage"] == "RESEARCH_AUDIT"
    assert result["stage_artifact_ref"]["path"] in store
    assert result["portfolio_context_ref"]["path"] in store
    assert len(writes) == 1
    assert set(writes[0]) == {
        result["stage_artifact_ref"]["path"],
        result["portfolio_context_ref"]["path"],
    }
    assert result["owner_admission"]["child_state_cas_verified"] is True
    assert proposals[0]["parameters"]["artifact_path"] == result["stage_artifact_ref"]["path"]
    assert proposals[0]["parameters"]["decision_envelope"] == _decision()
    assert proposals[0]["parameters"]["private_research_brief"] == _brief()
    assert calls


def test_run_next_portfolio_stage_rejects_missing_owner_state_before_any_provider_write():
    task_id = "coordinator-missing-state"
    _, reader, writer, writes = _store_provider()

    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_ARTICLE_STATE_NOT_FOUND",
    ):
        portfolio_coordinator.run_next_portfolio_stage(
            task_id,
            state_reader=lambda path: None,
            artifact_reader=reader,
            portfolio_context_reader=reader,
            artifact_bundle_writer=writer,
            authorization_verifier=lambda request: None,
            bundle_cas_writer=lambda *args: {},
            effect_attestation_signer=lambda claims: None,
            effect_receipt_reader=lambda path: None,
        )
    assert writes == []


def test_run_next_portfolio_stage_rejects_state_task_identity_mismatch(monkeypatch):
    task_id = "coordinator-requested-task"
    wrong_state = {
        "task_id": "coordinator-other-task",
        "status": "IN_PROGRESS",
        "current_stage": "INTAKE",
    }
    record = _serialized_owner_state(wrong_state)
    _, reader, writer, _ = _store_provider()

    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_ARTICLE_IDENTITY_MISMATCH",
    ):
        portfolio_coordinator.run_next_portfolio_stage(
            task_id,
            state_reader=lambda path: record,
            artifact_reader=reader,
            portfolio_context_reader=reader,
            artifact_bundle_writer=writer,
            authorization_verifier=lambda request: None,
            bundle_cas_writer=lambda *args: {},
            effect_attestation_signer=lambda claims: None,
            effect_receipt_reader=lambda path: None,
        )


@pytest.mark.parametrize(
    ("status", "message"),
    [
        ("BLOCKED", "PORTFOLIO_OWNER_STATE_BLOCKED_REQUIRES_EXPLICIT_RECOVERY"),
        ("DELIVERED", "PORTFOLIO_OWNER_STATE_NOT_IN_PROGRESS"),
    ],
)
def test_run_next_portfolio_stage_fails_closed_for_non_executable_owner_status(
    monkeypatch, status, message,
):
    task_id = "coordinator-owner-status"
    state = {
        "task_id": task_id,
        "status": status,
        "current_stage": "RESEARCH",
    }
    record = _serialized_owner_state(state)
    _, reader, writer, _ = _store_provider()
    monkeypatch.setattr(current_admission, "validate_state", lambda candidate: None)

    with pytest.raises(PortfolioCoordinatorError, match=message):
        portfolio_coordinator.run_next_portfolio_stage(
            task_id,
            state_reader=lambda path: record,
            artifact_reader=reader,
            portfolio_context_reader=reader,
            artifact_bundle_writer=writer,
            authorization_verifier=lambda request: None,
            bundle_cas_writer=lambda *args: {},
            effect_attestation_signer=lambda claims: None,
            effect_receipt_reader=lambda path: None,
        )


def test_run_next_portfolio_stage_requires_seed_for_first_intake_call(monkeypatch):
    task_id = "coordinator-seed-required"
    state = current_admission.build_initial_state(
        task_id=task_id,
        prompt="Write a financial article",
        source_refs=[],
        executor_identity="test",
    )
    deps, _, _, _ = _coordinator_dependencies(
        monkeypatch,
        state,
        {
            "stage": "RESEARCH",
            "business_status": "IN_PROGRESS",
            "child_state_cas_verified": True,
            "effect_receipt_readback_verified": True,
        },
    )

    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_INITIAL_SEED_INPUTS_REQUIRED",
    ):
        portfolio_coordinator.run_next_portfolio_stage(task_id, **deps)


@pytest.mark.parametrize(
    ("admission", "message"),
    [
        (
            {
                "task_id": "another-task",
                "stage": "RESEARCH",
                "business_status": "IN_PROGRESS",
                "child_state_cas_verified": True,
                "effect_receipt_readback_verified": True,
            },
            "PORTFOLIO_OWNER_ADMISSION_TASK_ID_MISMATCH",
        ),
        (
            {
                "task_id": "expected-task",
                "stage": "RESEARCH",
                "business_status": "BLOCKED",
                "child_state_cas_verified": True,
                "effect_receipt_readback_verified": True,
            },
            "PORTFOLIO_OWNER_ADMISSION_STATUS_READBACK_MISMATCH",
        ),
        (
            {
                "task_id": "expected-task",
                "stage": "RESEARCH",
                "business_status": "IN_PROGRESS",
                "child_state_cas_verified": False,
                "effect_receipt_readback_verified": True,
            },
            "PORTFOLIO_OWNER_ADMISSION_STATE_CAS_NOT_VERIFIED",
        ),
    ],
)
def test_owner_admission_requires_task_status_and_state_cas_binding(admission, message):
    with pytest.raises(PortfolioCoordinatorError, match=message):
        portfolio_coordinator._verify_owner_admission(
            admission,
            task_id="expected-task",
            expected_stage="RESEARCH",
            expected_status="IN_PROGRESS",
        )


def test_read_provider_artifact_accepts_utf8_text_and_recomputes_blob_sha():
    content = '{"stage":"RESEARCH"}'
    expected = content.encode("utf-8")
    result = portfolio_coordinator._read_provider_artifact(
        lambda path: {
            "content": content,
            "blob_sha": standalone_runtime._blob_sha(expected),
        },
        "artifact.json",
    )
    assert result == (expected, standalone_runtime._blob_sha(expected))


@pytest.mark.parametrize(
    ("reader", "message"),
    [
        (
            lambda path: (_ for _ in ()).throw(RuntimeError("provider offline")),
            "PORTFOLIO_PROVIDER_ARTIFACT_READ_FAILED",
        ),
        (lambda path: None, "PORTFOLIO_PROVIDER_ARTIFACT_MISSING"),
        (
            lambda path: {"content": 42, "blob_sha": "abc"},
            "PORTFOLIO_PROVIDER_ARTIFACT_RESPONSE_INVALID",
        ),
        (
            lambda path: {"content": b"actual", "blob_sha": "claimed-old-sha"},
            "PORTFOLIO_PROVIDER_ARTIFACT_BLOB_SHA_MISMATCH",
        ),
    ],
)
def test_read_provider_artifact_fails_closed_on_untrusted_provider_response(reader, message):
    with pytest.raises(PortfolioCoordinatorError, match=message):
        portfolio_coordinator._read_provider_artifact(reader, "artifact.json")


def test_latest_context_ref_selects_newest_bound_receipt_and_skips_unrelated_receipts():
    expected = {
        "path": "workspaces/articles/task-1/portfolio/contexts/2-current.json",
        "blob_sha": "a" * 40,
        "sha256": "b" * 64,
        "stage": "RESEARCH_AUDIT",
        "generation": 2,
    }
    state = {
        "execution_receipts": [
            None,
            {"input_bindings": "not-a-mapping"},
            {"input_bindings": {"portfolio_context_ref": {"path": "old"}}},
            {"input_bindings": {"portfolio_context_ref": expected}},
        ],
    }
    assert portfolio_coordinator._latest_context_ref(state) == expected


def test_latest_context_ref_rejects_invalid_history_and_returns_none_when_unbound():
    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_OWNER_RECEIPT_HISTORY_INVALID",
    ):
        portfolio_coordinator._latest_context_ref({"execution_receipts": {}})
    assert portfolio_coordinator._latest_context_ref({
        "execution_receipts": [None, {"input_bindings": {}}],
    }) is None


def test_stage_payload_requires_mapping_outputs_and_typed_full_universe_package():
    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_STAGE_OUTPUT_SNAPSHOT_MISSING",
    ):
        portfolio_coordinator._stage_payload(
            {"last_stage_result": {"stage_outputs": []}},
            stage="RESEARCH",
            state={},
        )

    state = {
        "required_outputs": ["AUDIT_DOCX", "FINANCE_DEEP_DOCX"],
        "task_requirement_authority": {
            "active_requirements": [{
                "requirement_id": "full_universe_research_pool",
                "statement": "Retain the full requested company universe.",
                "scopes": ["FINANCE_DEEP"],
                "affects_from_stage": "RESEARCH",
                "evidence_ref": "owner-instruction://full-universe",
                "source_kind": "USER_EXPLICIT",
            }],
        },
    }
    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_FULL_UNIVERSE_RESEARCH_EVIDENCE_CONTRACT_REQUIRED",
    ):
        portfolio_coordinator._stage_payload(
            {
                "last_stage_result": {
                    "stage_outputs": {"research_package": {"topic": "incomplete"}},
                },
            },
            stage="RESEARCH",
            state=state,
        )


def test_business_stage_artifact_rejects_result_from_another_stage():
    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_STAGE_RESULT_NOT_BOUND_TO_CONTEXT",
    ):
        portfolio_coordinator._business_stage_artifact(
            {
                "task_id": "task-1",
                "requirement_digest": "a" * 64,
                "last_stage_result": {"stage": "DRAFT", "stage_outputs": {}},
                "trace": [],
            },
            stage="RESEARCH",
            state={"current_stage": "RESEARCH"},
        )


def test_stage_artifact_ref_requires_a_full_sha256_receipt_binding():
    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_STAGE_RECEIPT_SHA_INVALID",
    ):
        portfolio_coordinator._stage_artifact_ref(
            task_id="task-1",
            stage="RESEARCH",
            receipt={"receipt_sha256": "short"},
            content=b"{}",
        )


@pytest.mark.parametrize(
    ("stage", "result", "expected_key"),
    [
        (
            "EDITORIAL",
            {
                "stage_outputs": {
                    "story_blueprints": {
                        "FINANCE_DEEP": {"product_mode": "FINANCE_DEEP"},
                        "FINANCE_BROAD": {"product_mode": "FINANCE_BROAD"},
                    },
                },
                "requirement_satisfaction": [
                    {"requirement_id": "deep-complete", "evidence_refs": []},
                ],
            },
            "story_blueprints",
        ),
        (
            "RESEARCH_AUDIT",
            {
                "status": "PASS",
                "stage_outputs": {},
                "requirement_satisfaction": [],
            },
            "review_status",
        ),
        (
            "EDITORIAL_AUDIT",
            {
                "status": "REVISE",
                "revision_target": "EDITORIAL",
                "stage_outputs": {
                    "publication_fitnesses": {
                        "FINANCE_DEEP": {"final_status": "REVISE"},
                    },
                },
                "requirement_satisfaction": [],
            },
            "publication_fitnesses",
        ),
    ],
)
def test_owner_action_parameters_preserves_stage_specific_admission_payloads(
    stage, result, expected_key,
):
    artifact_path = f"workspaces/articles/task-1/stages/{stage}.json"
    params = portfolio_coordinator._owner_action_parameters(
        {
            "last_stage_result": result,
        },
        stage=stage,
        artifact_ref={"path": artifact_path, "blob_sha": "a" * 40},
        context_ref={
            "path": "workspaces/articles/task-1/portfolio/contexts/1.json",
            "blob_sha": "b" * 40,
            "sha256": "c" * 64,
            "stage": "TITLE",
            "generation": 1,
        },
        state={},
    )
    assert expected_key in params
    assert params["portfolio_context_ref"]["generation"] == 1
    if stage == "EDITORIAL":
        assert params["requirement_satisfaction"][0]["evidence_refs"] == [artifact_path]
    if stage == "EDITORIAL_AUDIT":
        assert params["review_status"] == "REVISE"
        assert params["revision_target"] == "EDITORIAL"


def test_artifact_bundle_rejects_missing_writer_and_empty_file_map():
    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_ARTIFACT_BUNDLE_WRITER_REQUIRED",
    ):
        portfolio_coordinator._write_and_verify_bundle(
            {"workspaces/articles/task-1/a.json": b"{}"},
            writer=None,
            artifact_reader=lambda path: None,
            context_reader=lambda path: None,
            context_path="context.json",
        )
    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_ARTIFACT_BUNDLE_FILES_REQUIRED",
    ):
        portfolio_coordinator._write_and_verify_bundle(
            {},
            writer=lambda files: {},
            artifact_reader=lambda path: None,
            context_reader=lambda path: None,
            context_path="context.json",
        )


@pytest.mark.parametrize(
    ("writer", "message"),
    [
        (lambda files: {}, "PORTFOLIO_ARTIFACT_BUNDLE_WRITE_RECEIPT_INVALID"),
        (
            lambda files: {"blob_shas": {"workspaces/articles/task-1/other.json": "x"}},
            "PORTFOLIO_ARTIFACT_BUNDLE_WRITE_RECEIPT_PATH_SET_MISMATCH",
        ),
        (
            lambda files: {"blob_shas": {next(iter(files)): "wrong-sha"}},
            "PORTFOLIO_ARTIFACT_BUNDLE_WRITE_SHA_MISMATCH",
        ),
    ],
)
def test_artifact_bundle_rejects_invalid_provider_write_receipts(writer, message):
    with pytest.raises(PortfolioCoordinatorError, match=message):
        portfolio_coordinator._write_and_verify_bundle(
            {"workspaces/articles/task-1/a.json": b"{}"},
            writer=writer,
            artifact_reader=lambda path: None,
            context_reader=lambda path: None,
            context_path="context.json",
        )


def test_deep_full_universe_requirement_does_not_block_broad_only_task():
    state = {
        "required_outputs": ["AUDIT_DOCX", "FINANCE_BROAD_DOCX"],
        "task_requirement_authority": {
            "active_requirements": [{
                "requirement_id": "full_universe_research_pool",
                "statement": "Retain the full requested company universe.",
                "scopes": ["FINANCE_DEEP"],
                "affects_from_stage": "RESEARCH",
                "evidence_ref": "owner-instruction://full-universe",
                "source_kind": "USER_EXPLICIT",
            }],
        },
    }
    outputs = {"research_package": {"topic": "broad-only research fixture"}}
    assert portfolio_coordinator._has_full_universe_requirement(state) is False
    assert portfolio_coordinator._stage_payload(
        {"last_stage_result": {"stage_outputs": outputs}},
        stage="RESEARCH",
        state=state,
    ) == outputs


def test_standalone_runtime_does_not_reconcile_unrequested_deep_universe(monkeypatch):
    _, content, blob_sha, path, candidate = _portfolio_research_artifact()
    candidate["task_requirement_authority"]["active_requirements"] = [{
        "requirement_id": "full_universe_research_pool",
        "statement": "Retain the full requested company universe.",
        "scopes": ["FINANCE_DEEP"],
        "affects_from_stage": "RESEARCH",
        "evidence_ref": "owner-instruction://full-universe",
        "source_kind": "USER_EXPLICIT",
    }]
    candidate["required_outputs"] = ["AUDIT_DOCX", "FINANCE_BROAD_DOCX"]
    captured = []

    def forbidden_validate(value):
        captured.append(value)
        raise AssertionError("unrequested Deep universe must not be validated")

    monkeypatch.setattr(
        standalone_runtime, "validate_full_universe_decision_handoff", forbidden_validate,
    )
    monkeypatch.setattr(
        standalone_runtime,
        "require_retained_universe_reconciliation",
        lambda *args: (_ for _ in ()).throw(
            AssertionError("unrequested Deep universe must not be reconciled")
        ),
    )

    result = standalone_runtime._verify_stage_bytes(
        candidate,
        lambda requested: (
            {"content": content, "blob_sha": blob_sha}
            if requested == path else None
        ),
    )

    assert captured == []
    assert result["retained_universe_reconciliation"] is None
