from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_maintenance_routes_to_proactive_resolution_and_problem_journal():
    maintenance = _read("references/maintenance.md")
    assert "Revision: `1.2`" in maintenance
    assert "references/proactive_resolution.md" in maintenance
    assert "financial_writing_agent/proactive_resolution.py" in maintenance
    assert "evals/PROBLEM_EVOLUTION_JOURNAL.md" in maintenance
    assert "A missing ideal input is not automatically a user blocker" in maintenance
    assert "record_proactive_resolution_state" in maintenance
    assert "require_user_escalation_admission" in maintenance
    assert "Problem-to-action closure" in maintenance
    assert "Every encountered problem must appear" in maintenance
    assert "Do not rewrite the journal into a success-only narrative" in maintenance


def test_proactive_resolution_recovers_before_user_escalation():
    rule = _read("references/proactive_resolution.md")
    assert "recover, infer provisionally, test, and only then escalate" in rule
    assert "Missing highest-tier evidence is not automatically a blocker" in rule
    assert "user-approved or user-edited writing samples" in rule
    assert "explicit durable user corrections, rejections, constraints and accepted outcomes" in rule
    assert "current conversation/context signals" in rule
    assert "Ask the user only when" in rule
    assert "Do not ask merely because the best evidence is imperfect" in rule


def test_problem_journal_keeps_failures_repairs_and_parent_queue_together():
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
    }
    for entry in required_entries:
        assert entry in journal
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
    assert "INHERITED_COGNITION_AUTO_ACTIVATION_GAP" in journal


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
