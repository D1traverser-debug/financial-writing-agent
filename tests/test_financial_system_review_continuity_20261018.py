"""The child owner resumes full-system work without creating a second task index."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_explicit_financial_system_review_has_durable_current_owner_ref():
    index = _json("evals/EVOLUTION_INDEX.json")
    assessment = index["active_system_assessment"]
    assert assessment["owner"] == "DOMAIN:financial_writing"
    assert assessment["status"].startswith("RUNNING")
    assert assessment["r0_production"]["pr"] == 50
    assert assessment["r0_production"]["ci_run"] == 1416
    assert (ROOT / assessment["review_ref"]).is_file()
    assert assessment["existing_task_ref"].endswith("/STATE.json")
    assert _json(assessment["existing_task_ref"])["status"] == "IN_PROGRESS"
    assert assessment["user_action_now"] == "NONE"


def test_named_system_request_does_not_route_into_a_historical_article():
    entry = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    assert "## Explicit Financial system-wide review / reconstruction" in entry
    assert "evals/EVOLUTION_INDEX.json#active_system_assessment" in entry
    assert "not substitute a historical article's DELIVERED status" in entry
    assert "Ordinary article selection still resolves only its exact" in entry
    assert not (ROOT / "state/TASK_INDEX.json").exists()


def test_review_stays_open_without_semantic_quality_proof():
    index = _json("evals/EVOLUTION_INDEX.json")
    a = index["active_system_assessment"]
    gap = " ".join(a["not_completion_evidence"])
    assert "NOT_READY" in gap
    assert "independently admitted current-kernel" in gap
    assert "NO_NEW_TASK_INDEX" in a["boundary"]
