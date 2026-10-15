from pathlib import Path

from financial_writing_agent.proactive_resolution import (
    record_proactive_resolution_state,
    require_user_escalation_admission,
)


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_proactive_resolution_rules_exist_and_are_operationally_bound():
    maintenance = _read("references/maintenance.md")
    proactive = _read("references/proactive_resolution.md")
    assert "Proactive resolution before user escalation" in maintenance
    assert "record_proactive_resolution_state" in maintenance
    assert "require_user_escalation_admission" in maintenance
    assert "recover -> infer provisionally -> test -> only then escalate" in proactive


def test_proactive_resolution_receipt_allows_safe_provisional_continue(tmp_path):
    state = {
        "task_id": "demo",
        "current_stage": "INTAKE",
        "status": "RUNNING",
        "working": {},
    }
    path = tmp_path / "STATE.json"
    import json

    path.write_text(json.dumps(state), encoding="utf-8")
    result = record_proactive_resolution_state(
        path,
        dependency="canonical_user_voice_sample",
        attempted_sources=["durable corrections", "approved edited outputs", "current context"],
        evidence=["negative style correction", "explicit anti-AI correction"],
        outcome="PROVISIONAL",
        confidence="medium",
        unknowns=["no canonical approved full article sample"],
        safe_to_continue=True,
        validation_plan=["validate against next real article/user feedback"],
    )
    assert result["outcome"] == "PROVISIONAL"
    assert require_user_escalation_admission(path, dependency="canonical_user_voice_sample") is False


def test_journal_contains_current_executable_bridge_history():
    journal = _read("evals/PROBLEM_EVOLUTION_JOURNAL.md")
    assert "Journal revision: `1.6`" in journal
    assert "PROMOTED__EXECUTABLE_POLICY_AND_TRAJECTORY_VERIFIED__LIVE_ARTICLE_OBSERVATION_OPEN" in journal
    assert "CI #1034" in journal
    assert "CI #1036" in journal
    assert "CI #1037" in journal
    assert "Parent Guidance Queue / adjudication state" in journal
    assert "PROACTIVE_RESOLUTION_GAP" in journal
    assert "DECLARATION_TO_OPERATION_GAP" in journal
    assert "PROBLEM_TO_ACTION_CLOSURE_GAP" in journal
    assert "MAINTENANCE_META_OVERPRODUCTION" in journal
    assert "CONSUMER_COMPLETE_PROPAGATION_REGRESSION" in journal
    assert "SELF_REFERENTIAL_RECEIPT_DRIFT" in journal
    assert "VERSION_METADATA_DRIFT" in journal
    assert "INHERITANCE_BEHAVIOR_VS_DECLARATION" in journal


def test_machine_index_and_parent_handoff_expose_adjudication_and_promotion_receipt():
    index = _read("evals/PROBLEM_EVOLUTION_JOURNAL_INDEX.json")
    handoff = _read("evals/PARENT_GUIDANCE_HANDOFF.md")
    assert '"revision": "1.6"' in index
    assert '"P-20261015-15"' in index
    assert '"P-20261015-16"' in index
    assert '"executable_proactive_resolution_promotion_receipt"' in index
    assert '"executable_proactive_resolution_candidate"' not in index
    assert '"production_ci_number": 1037' in index
    assert '"production_ci_status": "success"' in index
    assert '"latest_production_receipt"' not in index
    for signal in (
        "PROACTIVE_RESOLUTION_GAP",
        "EVOLUTION_HISTORY_INTERFACE",
        "VERSION_METADATA_DRIFT",
        "INHERITANCE_BEHAVIOR_VS_DECLARATION",
        "DECLARATION_TO_OPERATION_GAP",
        "PROBLEM_TO_ACTION_CLOSURE_GAP",
    ):
        assert signal in index
        assert signal in handoff
    assert "INHERITED_COGNITION_AUTO_ACTIVATION_GAP" in index
    assert "INHERITED_COGNITION_AUTO_ACTIVATION_GAP" in handoff
    assert "NEW_LIVE_INHERITANCE_EVIDENCE_PENDING_PARENT_ADJUDICATION" in handoff
    assert "EXECUTABLE_POLICY_AND_TRAJECTORY_VERIFIED" in handoff
