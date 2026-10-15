from __future__ import annotations

import inspect
from copy import deepcopy

import pytest

from financial_writing_agent import owner_guard
from financial_writing_agent.authoritative_state import AuthoritativeStateSnapshot
from financial_writing_agent.current_admission import advance_state, build_initial_state
from financial_writing_agent.owner_lifecycle import review_system_impact_state
from financial_writing_agent.proactive_resolution import record_proactive_resolution_state


def _decision() -> dict:
    return {
        "decision_id": "authority-thesis",
        "operation": "select article thesis",
        "objective": "select the strongest evidence-bounded explanation",
        "operation_class": "MATERIAL_JUDGMENT",
        "evidence": [
            {
                "ref": "filing-a",
                "kind": "CURRENT_FACT",
                "summary": "company evidence",
                "source_family": "company-filing",
            },
            {
                "ref": "policy-b",
                "kind": "CURRENT_FACT",
                "summary": "policy evidence",
                "source_family": "government",
            },
        ],
        "assumptions_challenged": ["macro growth automatically means the largest listed beneficiary"],
        "alternatives": [
            {
                "candidate_id": "A",
                "mechanism": "macro-volume thesis",
                "advantages": ["simple"],
                "failure_modes": ["company transmission may diverge"],
                "fit_conditions": ["company revenue tracks volume"],
                "misfit_conditions": ["company data diverges"],
            },
            {
                "candidate_id": "B",
                "mechanism": "profit-pool migration thesis",
                "advantages": ["explains company divergence"],
                "failure_modes": ["requires broader chain evidence"],
                "fit_conditions": ["multiple chain nodes show divergent economics"],
                "misfit_conditions": ["all companies move together"],
            },
        ],
        "counterexamples": ["macro volume rose while a listed operator's revenue did not"],
        "rejected_paths": ["A failed the company-level counterexample"],
        "selected_candidate_id": "B",
        "selection_rationale": "B survives the observed company-level contradiction",
        "saturation": {
            "sweeps": [
                {
                    "sweep_no": 1,
                    "query_or_scope": "industry and company scan",
                    "source_families": ["company-filing", "government"],
                    "new_material_candidates": ["B"],
                    "changed_decision": True,
                },
                {
                    "sweep_no": 2,
                    "query_or_scope": "counterexample scan",
                    "source_families": ["platform", "company-filing"],
                },
                {
                    "sweep_no": 3,
                    "query_or_scope": "saturation scan",
                    "source_families": ["government", "industry"],
                },
            ],
            "stop_reason": "two consecutive sweeps produced no decision-changing delta",
        },
        "verification_plan": ["research audit", "company decision map"],
    }


def _artifact(task_id: str, stage: str) -> dict:
    return {
        "artifact_key": stage,
        "artifact_path": f"workspaces/articles/{task_id}/{stage}.json",
        "artifact_blob_sha": f"blob-{stage.lower()}",
    }


def _new_current(task_id: str) -> dict:
    return build_initial_state(
        task_id=task_id,
        prompt="写一篇行业财经文章",
        source_refs=[],
        executor_identity="strict-test",
    )


def _install_authority(monkeypatch: pytest.MonkeyPatch, state: dict, sha: str = "a" * 40) -> dict:
    holder = {"state": deepcopy(state), "sha": sha}

    def _fake(task_id: str, *, repository="D1traverser-debug/financial-writing-agent", ref="main", timeout=10.0):
        assert task_id == holder["state"]["task_id"]
        return AuthoritativeStateSnapshot(
            task_id=task_id,
            state=deepcopy(holder["state"]),
            blob_sha=holder["sha"],
            path=f"workspaces/articles/{task_id}/STATE.json",
            ref="main",
        )

    monkeypatch.setattr(owner_guard, "fetch_authoritative_state", _fake)
    return holder


@pytest.mark.strict_authority
def test_current_state_cannot_be_downgraded_by_deleting_kernel_marker(monkeypatch: pytest.MonkeyPatch):
    authoritative = _new_current("authority-marker")
    _install_authority(monkeypatch, authoritative)

    tampered = deepcopy(authoritative)
    tampered["schema_version"] = owner_guard.CURRENT_STATE_SCHEMA_VERSION
    tampered.pop("writing_kernel_version", None)
    tampered.pop("quality_evidence", None)
    for receipt in tampered["execution_receipts"]:
        receipt["input_bindings"].pop("writing_kernel_version", None)
        receipt["input_bindings"].pop("quality_admission_path", None)

    with pytest.raises(owner_guard.GithubChatGuardError, match="differs from authoritative GitHub STATE.json"):
        owner_guard.validate_state(tampered)


@pytest.mark.strict_authority
def test_correct_state_with_wrong_previous_blob_sha_is_rejected(monkeypatch: pytest.MonkeyPatch):
    state = _new_current("authority-blob")
    holder = _install_authority(monkeypatch, state, "a" * 40)

    with pytest.raises(owner_guard.GithubChatGuardError, match="previous_state_blob_sha"):
        owner_guard.advance_state(
            state,
            previous_state_blob_sha="b" * 40,
            executor_identity="strict-test",
        )
    assert holder["state"] == state


@pytest.mark.strict_authority
def test_recomputed_quality_digest_inside_tampered_state_is_not_authority(monkeypatch: pytest.MonkeyPatch):
    state = _new_current("authority-digest")
    holder = _install_authority(monkeypatch, state, "a" * 40)

    state = advance_state(
        state,
        previous_state_blob_sha=holder["sha"],
        executor_identity="strict-test",
    )
    holder["state"] = deepcopy(state)
    holder["sha"] = "b" * 40

    state = advance_state(
        state,
        previous_state_blob_sha=holder["sha"],
        executor_identity="strict-test",
        decision_envelope=_decision(),
        **_artifact(state["task_id"], "RESEARCH"),
    )
    holder["state"] = deepcopy(state)
    holder["sha"] = "c" * 40

    tampered = deepcopy(state)
    tampered["quality_evidence"]["research_decision"]["selection_rationale"] = "caller rewrote admitted evidence"
    from financial_writing_agent.current_admission import _canonical_digest

    forged = _canonical_digest(tampered["quality_evidence"]["research_decision"])
    for receipt in tampered["execution_receipts"]:
        if receipt.get("stage") == "RESEARCH":
            receipt["input_bindings"]["decision_envelope_sha256"] = forged

    with pytest.raises(owner_guard.GithubChatGuardError, match="differs from authoritative GitHub STATE.json"):
        owner_guard.validate_state(tampered)


@pytest.mark.strict_authority
def test_proactive_resolution_rejects_non_authoritative_candidate_state(monkeypatch: pytest.MonkeyPatch):
    state = _new_current("authority-proactive")
    holder = _install_authority(monkeypatch, state, "d" * 40)
    tampered = deepcopy(state)
    tampered["prompt"] = "caller altered prompt before mutation"

    with pytest.raises(owner_guard.GithubChatGuardError, match="differs from authoritative GitHub STATE.json"):
        record_proactive_resolution_state(
            tampered,
            previous_state_blob_sha=holder["sha"],
            executor_identity="strict-test",
            target="missing evidence",
            attempted_sources=["official filing"],
            evidence_refs=["ref-1"],
            outcome="UNRESOLVED",
            confidence="NONE",
            contradictions_or_unknowns=["required evidence unavailable"],
            validation_plan=[],
            safe_to_continue=False,
        )


@pytest.mark.strict_authority
def test_system_impact_lifecycle_rejects_non_authoritative_candidate_state(monkeypatch: pytest.MonkeyPatch):
    state = _new_current("authority-lifecycle")
    holder = _install_authority(monkeypatch, state, "e" * 40)

    state = owner_guard.attach_material_feedback(
        state,
        previous_state_blob_sha=holder["sha"],
        executor_identity="strict-test",
        sample={"sample_type": "USER_REJECTION", "summary": "material rejection"},
        system_impact={
            "signal_id": "impact-authority",
            "status": "OPEN",
            "trigger_sample_type": "USER_REJECTION",
        },
    )
    holder["state"] = deepcopy(state)
    holder["sha"] = "f" * 40
    tampered = deepcopy(state)
    tampered["prompt"] = "caller rewrote persisted task before lifecycle mutation"

    with pytest.raises(owner_guard.GithubChatGuardError, match="differs from authoritative GitHub STATE.json"):
        review_system_impact_state(
            tampered,
            previous_state_blob_sha=holder["sha"],
            executor_identity="strict-test",
            signal_id="impact-authority",
            problem_statement="systemic problem",
            root_cause_layer="RUNTIME_OR_SCHEMA",
            generalization_scope="Financial owner",
            alternatives=[
                {"mechanism": "repair guard", "failure_mode": "implementation cost"},
                {"mechanism": "leave open", "failure_mode": "bypass persists"},
            ],
            selected_mechanism="repair guard",
            selection_rationale="authoritative mutation boundary is required",
            authority_surface="financial_writing_agent.owner_lifecycle",
            regression_or_eval_plan=["strict authority regression"],
            evidence_refs=["review://p1"],
            decision="SYSTEM_MAINTENANCE_REQUIRED",
            decision_reason="material bypass",
        )


def test_public_owner_mutation_api_exposes_no_quality_bypass_token():
    for func in (owner_guard.validate_state, owner_guard.advance_state, owner_guard.attach_material_feedback):
        params = inspect.signature(func).parameters
        assert "_current_admission_token" not in params
        assert "admission_token" not in params
        assert "skip_quality_validation" not in params


def test_public_owner_builder_creates_current_quality_state_not_new_legacy_state():
    state = owner_guard.build_initial_state(
        task_id="public-builder-current",
        prompt="新任务必须进入当前写作内核",
        source_refs=[],
        executor_identity="strict-test",
    )
    assert state["schema_version"] == owner_guard.QUALITY_STATE_SCHEMA_VERSION
    assert state["writing_kernel_version"] == owner_guard.CURRENT_WRITING_KERNEL_VERSION
    assert state["quality_evidence"] == {}
    assert state["execution_receipts"][0]["input_bindings"]["quality_admission_path"] == owner_guard.CURRENT_QUALITY_ADMISSION_PATH
