from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_maintenance_routes_to_proactive_resolution_and_problem_journal():
    maintenance = _read("references/maintenance.md")
    assert "Revision: `1.1`" in maintenance
    assert "references/proactive_resolution.md" in maintenance
    assert "evals/PROBLEM_EVOLUTION_JOURNAL.md" in maintenance
    assert "A missing ideal input is not automatically a user blocker" in maintenance
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
    assert "UPCALL_RECOMMENDED_FOR_COMMON_CAPABILITY_GENERALIZATION" in rule


def test_problem_journal_keeps_failures_repairs_and_parent_queue_together():
    journal = _read("evals/PROBLEM_EVOLUTION_JOURNAL.md")
    required_entries = {
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
    }
    for entry in required_entries:
        assert entry in journal
    assert "Wrong path tried" in journal
    assert "Parent Guidance Queue" in journal
    assert "PROACTIVE_RESOLUTION_GAP" in journal
    assert "VERSION_METADATA_DRIFT" in journal
    assert "INHERITANCE_BEHAVIOR_VS_DECLARATION" in journal
