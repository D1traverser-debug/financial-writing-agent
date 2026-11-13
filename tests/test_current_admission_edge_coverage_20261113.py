from copy import deepcopy

import pytest

from financial_writing_agent import owner_guard
from financial_writing_agent.current_admission import (
    CurrentAdmissionError,
    _archive_invalidated_quality,
    _latest_receipt_digest,
    _normalize_requirement_satisfaction,
    _planned_quality_invalidations,
    _require_persisted_digest,
    _validate_requirement_satisfaction_history,
    advance_state,
    apply_task_requirement_change,
    migrate_task_requirement_authority,
    WRITING_KERNEL_VERSION,
)
from test_current_admission_v1 import (
    _artifact, _brief, _decision, _new_state,
)
from test_task_requirement_authority_20261017 import EXECUTOR, _req, _state


def test_latest_receipt_digest_ignores_malformed_or_non_admission_receipts():
    assert _latest_receipt_digest(
        {"execution_receipts": "not-a-list"}, "proof", admitting_stage="RESEARCH"
    ) is None
    state = {"execution_receipts": [
        None,
        {"stage": "EDITORIAL", "input_bindings": {"proof": "wrong-stage"}},
        {"stage": "RESEARCH", "input_bindings": []},
        {"stage": "RESEARCH", "input_bindings": {"quality_admission_path": "other", "proof": "wrong-path"}},
        {"stage": "RESEARCH", "input_bindings": {"quality_admission_path": "financial_writing_agent.current_admission"}},
    ]}
    assert _latest_receipt_digest(state, "proof", admitting_stage="RESEARCH") is None
    state["execution_receipts"].append({
        "stage": "RESEARCH",
        "input_bindings": {
            "quality_admission_path": "financial_writing_agent.current_admission",
            "proof": "sha256:admitted",
        },
    })
    assert _latest_receipt_digest(state, "proof", admitting_stage="RESEARCH") == "sha256:admitted"


def test_persisted_digest_requires_current_admission_receipt_and_exact_value():
    evidence = {"decision": "selected"}
    digest = "sha256:" + "a" * 64
    state = {"execution_receipts": [{
        "stage": "RESEARCH",
        "input_bindings": {
            "quality_admission_path": "financial_writing_agent.current_admission",
            "decision_sha256": digest,
        },
    }]}
    from financial_writing_agent.current_admission import _canonical_digest
    state["execution_receipts"][-1]["input_bindings"]["decision_sha256"] = _canonical_digest(evidence)
    _require_persisted_digest(
        state, evidence_key="research_decision", binding_key="decision_sha256",
        admitting_stage="RESEARCH", evidence_value=evidence,
    )
    with pytest.raises(CurrentAdmissionError, match="lacks a RESEARCH current-admission receipt"):
        _require_persisted_digest(
            {"execution_receipts": []}, evidence_key="research_decision",
            binding_key="decision_sha256", admitting_stage="RESEARCH", evidence_value=evidence,
        )
    with pytest.raises(CurrentAdmissionError, match="no longer matches"):
        _require_persisted_digest(
            state, evidence_key="research_decision", binding_key="decision_sha256",
            admitting_stage="RESEARCH", evidence_value={"decision": "tampered"},
        )


def test_requirement_satisfaction_normalization_covers_empty_due_and_every_rejection():
    empty = _new_state("empty-due")
    assert _normalize_requirement_satisfaction(empty, "INTAKE", None) == []
    with pytest.raises(CurrentAdmissionError, match="must be empty"):
        _normalize_requirement_satisfaction(
            empty, "INTAKE",
            [{"requirement_id": "invented", "result": "SATISFIED", "evidence_refs": ["x"]}],
        )

    state = apply_task_requirement_change(
        _state(), previous_state_blob_sha="a" * 40, executor_identity=EXECUTOR,
        evidence_ref="chat://user/research-requirement",
        upserts=[_req(requirement_id="research-scope", stage="RESEARCH")],
    )
    with pytest.raises(CurrentAdmissionError, match="requires task requirement satisfaction"):
        _normalize_requirement_satisfaction(state, "RESEARCH", None)
    valid = {"requirement_id": "research-scope", "result": "SATISFIED", "evidence_refs": ["source://filing"]}
    with pytest.raises(CurrentAdmissionError, match="unexpected"):
        _normalize_requirement_satisfaction(
            state, "RESEARCH", [{**valid, "requirement_id": "unknown"}]
        )
    with pytest.raises(CurrentAdmissionError, match="duplicate"):
        _normalize_requirement_satisfaction(state, "RESEARCH", [valid, valid])
    with pytest.raises(CurrentAdmissionError, match="must be SATISFIED"):
        _normalize_requirement_satisfaction(
            state, "RESEARCH", [{**valid, "result": "OPEN"}]
        )
    with pytest.raises(CurrentAdmissionError, match="requires evidence_refs"):
        _normalize_requirement_satisfaction(
            state, "RESEARCH", [{**valid, "evidence_refs": []}]
        )
    normalized = _normalize_requirement_satisfaction(state, "RESEARCH", [valid])
    assert normalized[0]["requirement_id"] == "research-scope"
    assert normalized[0]["requirement_sha256"]
    assert normalized[0]["evidence_refs"] == ["source://filing"]


def test_requirement_satisfaction_history_rejects_missing_receipt_and_accepts_exact_revision():
    state = apply_task_requirement_change(
        _state(), previous_state_blob_sha="a" * 40, executor_identity=EXECUTOR,
        evidence_ref="chat://user/research-requirement",
        upserts=[_req(requirement_id="research-scope", stage="RESEARCH")],
    )
    state["current_stage"] = "RESEARCH_AUDIT"
    with pytest.raises(CurrentAdmissionError, match="has no admitted satisfaction evidence"):
        _validate_requirement_satisfaction_history(state)

    from financial_writing_agent.current_admission import _canonical_digest
    requirement = state["task_requirement_authority"]["active_requirements"][0]
    state["execution_receipts"].append({
        "stage": "RESEARCH",
        "input_bindings": {
            "task_requirement_satisfaction": [{
                "requirement_id": "research-scope",
                "requirement_sha256": _canonical_digest(requirement),
                "result": "SATISFIED",
                "evidence_refs": ["source://filing"],
            }],
        },
    })
    _validate_requirement_satisfaction_history(state)
    state["execution_receipts"][-1]["input_bindings"]["task_requirement_satisfaction"][0]["requirement_sha256"] = "0" * 64
    with pytest.raises(CurrentAdmissionError, match="has no admitted satisfaction evidence"):
        _validate_requirement_satisfaction_history(state)


def test_quality_invalidation_planning_and_archive_preserve_prior_evidence():
    quality = {
        "research_decision": {"id": 1},
        "private_research_brief": {"id": 2},
        "story_blueprints": [{"id": 3}],
        "publication_fitnesses": [{"id": 4}],
    }
    state = {"quality_evidence": quality}
    assert _planned_quality_invalidations(state, "RESEARCH") == sorted(quality)
    assert _planned_quality_invalidations(state, "EDITORIAL") == ["publication_fitnesses", "story_blueprints"]
    assert _planned_quality_invalidations(state, "DRAFT") == ["publication_fitnesses"]
    assert _planned_quality_invalidations(state, "FINAL_AUDIT") == []

    no_quality = {"quality_evidence": {}}
    _archive_invalidated_quality(no_quality, reason="test", earliest_stage="RESEARCH")
    assert "quality_evidence_history" not in no_quality

    _archive_invalidated_quality(state, reason="test", earliest_stage="EDITORIAL")
    archived = state["quality_evidence_history"][-1]
    assert archived["reason"] == "test"
    assert archived["invalidated_from_stage"] == "EDITORIAL"
    assert archived["quality_evidence"] == quality


def test_pre_requirement_migration_rejects_current_authority_and_migrates_legacy_state():
    current = _new_state("already-current")
    with pytest.raises(CurrentAdmissionError, match="already has Task Requirement Authority"):
        migrate_task_requirement_authority(
            current, previous_state_blob_sha="a" * 40, executor_identity="test",
            evidence_ref="chat://user/migration", requirements=[],
        )

    legacy = owner_guard.build_initial_state(
        task_id="legacy-requirement-migration", prompt="legacy", source_refs=[],
        executor_identity="test", _current_admission_token=owner_guard._CURRENT_ADMISSION_TOKEN,
    )
    # A pre-P10 state is still current-kernel state; a pre-kernel historical
    # state must remain blocked and require a current-kernel successor.
    with pytest.raises(owner_guard.GithubChatGuardError, match="historical Financial state cannot be materially advanced"):
        owner_guard.advance_state(
            legacy, previous_state_blob_sha="b" * 40, executor_identity="test",
            artifact_key="INTAKE", artifact_path=f"workspaces/articles/{legacy['task_id']}/INTAKE.json",
            artifact_blob_sha="intake-blob",
            _current_admission_token=owner_guard._CURRENT_ADMISSION_TOKEN,
        )

    legacy["writing_kernel_version"] = WRITING_KERNEL_VERSION
    legacy["quality_evidence"] = {}
    legacy = owner_guard.advance_state(
        legacy, previous_state_blob_sha="b" * 40, executor_identity="test",
        artifact_key="INTAKE", artifact_path=f"workspaces/articles/{legacy['task_id']}/INTAKE.json",
        artifact_blob_sha="intake-blob",
        _current_admission_token=owner_guard._CURRENT_ADMISSION_TOKEN,
    )
    legacy["quality_evidence"] = {"research_decision": {"historical": "retained"}}
    migrated = migrate_task_requirement_authority(
        legacy, previous_state_blob_sha="c" * 40, executor_identity="test",
        evidence_ref="chat://user/migration",
        requirements=[_req(requirement_id="migrated-research", stage="RESEARCH")],
    )
    assert migrated["task_requirement_authority"]["revision"] == 1
    assert migrated["current_stage"] == "RESEARCH"
    assert migrated["quality_evidence"] == {}
    assert migrated["quality_evidence_history"][-1]["reason"] == "TASK_REQUIREMENT_AUTHORITY_MIGRATION"
    assert migrated["execution_receipts"][-1]["input_bindings"]["migration_from_missing_requirement_authority"] is True
