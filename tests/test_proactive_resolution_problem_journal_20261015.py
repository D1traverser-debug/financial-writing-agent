import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_maintenance_routes_to_proactive_resolution_and_problem_journal():
    maintenance = _read("skills/financial-writing-agent/references/maintenance.md")
    assert "Revision: 3.0-STANDALONE" in maintenance
    assert "skills/financial-writing-agent/references/proactive_resolution.md" in maintenance
    assert "financial_writing_agent/proactive_resolution.py" in maintenance
    assert "evals/PROBLEM_EVOLUTION_JOURNAL.md" in maintenance
    assert "A missing ideal input is not automatically a user blocker" in maintenance
    assert "record_proactive_resolution_state" in maintenance
    assert "require_user_escalation_admission" in maintenance
    assert "Problem-to-action closure" in maintenance
    assert "Every encountered problem must appear" in maintenance
    assert "Do not rewrite the journal into a success-only narrative" in maintenance


def test_proactive_resolution_recovers_before_user_escalation():
    rule = _read("skills/financial-writing-agent/references/proactive_resolution.md")
    assert "investigate first" in rule
    assert "not an automatic reason to stop or ask the user" in rule
    assert "approved/edited samples and durable corrections" in rule
    assert "accessible conversation context" in rule
    assert "Ask the user only when" in rule
    assert "Do not ask merely because the best evidence is imperfect" in rule


def test_problem_journal_preserves_historical_parent_queue_as_archival_provenance():
    journal = _read("evals/PROBLEM_EVOLUTION_JOURNAL.md")
    required_entries = {
        "P-20261010-01",
        "P-20261011-01",
        "P-20261011-02",
        "P-20261011-03",
        "P-20261012-00",
        "P-20261012-01",
        "P-20261012-05",
        "P-20261013-02",
        "P-20261014-01",
        "P-20261015-02",
        "P-20261015-05",
        "P-20261015-08",
        "P-20261015-09",
        "P-20261015-10",
        "P-20261015-11",
        "P-20261015-12",
        "P-20261015-13",
        "P-20261015-14",
        "P-20261015-15",
        "P-20261015-16",
        "P-20261113-01",
    }
    for entry in required_entries:
        assert entry in journal
    assert "Journal revision: `1.9`" in journal
    assert "DURABLE_PROBLEM_HISTORY__NOT_CURRENT_SYSTEM_STATUS" in journal
    assert "PROMOTED__EXECUTABLE_POLICY_AND_TRAJECTORY_VERIFIED__LIVE_ARTICLE_OBSERVATION_OPEN" in journal
    assert "CI #1034" in journal
    assert "CI #1036" in journal
    assert "CI #1037" in journal
    assert "Historical Parent Guidance Queue / adjudication state (archival only)" in journal
    assert "PROACTIVE_RESOLUTION_GAP" in journal
    assert "DECLARATION_TO_OPERATION_GAP" in journal
    assert "PROBLEM_TO_ACTION_CLOSURE_GAP" in journal
    assert "MAINTENANCE_META_OVERPRODUCTION" in journal
    assert "CONSUMER_COMPLETE_PROPAGATION_REGRESSION" in journal
    assert "SELF_REFERENTIAL_RECEIPT_DRIFT" in journal
    assert "VERSION_METADATA_DRIFT" in journal
    assert "INHERITANCE_BEHAVIOR_VS_DECLARATION" in journal
    assert "INHERITED_COGNITION_AUTO_ACTIVATION_GAP" in journal
    assert "2026-11-13 archival boundary" in journal
    assert "current Financial admission rejects legacy parent-upcall dispositions" in journal
    assert "Final code candidate `0440c5c8bd315825fa8e14500782b8bae6f53f99`" in journal
    assert "514 tests passed" in journal
    assert "no current action returns `PARENT_GUIDANCE_REQUIRED`" in journal
    assert "No further private article/research writes should be made" in journal


def test_machine_index_preserves_parent_history_without_live_parent_handoff():
    payload = json.loads(_read("evals/PROBLEM_EVOLUTION_JOURNAL_INDEX.json"))
    assert payload["revision"] == "1.9"
    assert payload["status"] == "HISTORICAL_PROBLEM_JOURNAL_INDEX__NOT_CURRENT_SYSTEM_STATUS"
    assert payload["system_status_authority"] == "evals/EVOLUTION_INDEX.json"
    assert "P-20261015-15" in payload["open_items_at_2026_10_15"]
    assert "P-20261015-16" in payload["open_items_at_2026_10_15"]
    assert payload["latest_incident_id"] == "P-20261113-01"
    assert payload["latest_incident_ref"].endswith("#P-20261113-01")
    assert "executable_proactive_resolution_promotion_receipt" in payload
    assert "executable_proactive_resolution_candidate" not in payload
    receipt = payload["executable_proactive_resolution_promotion_receipt"]
    assert receipt["production_ci_number"] == 1037
    assert receipt["production_ci_status"] == "success"
    assert payload["historical_parent_guidance_status"] == "ARCHIVAL_ONLY__NO_LIVE_PARENT_DEPENDENCY"
    assert set(payload["historical_parent_guidance_items"]) >= {
        "PROACTIVE_RESOLUTION_GAP",
        "EVOLUTION_HISTORY_INTERFACE",
        "VERSION_METADATA_DRIFT",
        "INHERITANCE_BEHAVIOR_VS_DECLARATION",
        "DECLARATION_TO_OPERATION_GAP",
        "PROBLEM_TO_ACTION_CLOSURE_GAP",
        "INHERITED_COGNITION_AUTO_ACTIVATION_GAP",
    }
    assert all(
        path.startswith("skills/financial-writing-agent/references/") or path.startswith("financial_writing_agent/")
        for path in payload["rule_refs"]
    )
    assert not (ROOT / "evals/PARENT_GUIDANCE_HANDOFF.md").exists()
