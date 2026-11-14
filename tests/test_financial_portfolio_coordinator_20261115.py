from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from financial_writing_agent import portfolio_coordinator, standalone_runtime
from financial_writing_agent.portfolio_coordinator import PortfolioCoordinatorError
from financial_writing_agent.schemas import ResearchPackage
from financial_writing_agent.standalone_runtime import FinancialAdmissionError
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
    outputs = {"research_package": {"topic": "typed package fixture"}}
    stage_result = {"stage": "RESEARCH", "stage_outputs": outputs}
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
        "task_requirement_authority": {
            "active_requirements": [{"requirement_id": "full_universe_research_pool"}],
        },
    }
    return artifact, content, blob_sha, path, candidate


def test_coordinator_research_envelope_validates_nested_typed_research_package(monkeypatch):
    artifact, content, blob_sha, path, candidate = _portfolio_research_artifact()
    captured = []

    def fake_model_validate(cls, value):
        captured.append(value)
        return SimpleNamespace(value=value)

    monkeypatch.setattr(
        ResearchPackage, "model_validate", classmethod(fake_model_validate),
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

    assert captured == [artifact["payload"]["research_package"]]
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
    assert result["assurance"] == "EXACT_PROVIDER_BYTES_AND_CONTEXT_CROSS_BINDING"

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
