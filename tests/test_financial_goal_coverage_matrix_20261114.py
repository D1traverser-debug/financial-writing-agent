"""Product acceptance cannot be inferred from a repository unit-test count.

The Matrix is the minimum user-goal ledger. A new PR requirement cannot silently
evade simulation coverage when docs/product_requirements.md changes.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "evals" / "FINANCIAL_GOAL_FIRST_REQUIREMENT_MATRIX_20261114.json"


def _read():
    return json.loads(MATRIX.read_text(encoding="utf-8"))


def test_every_actual_product_requirement_has_one_current_goal_and_real_gap():
    document = (ROOT / "docs" / "product_requirements.md").read_text(encoding="utf-8")
    declared = set(re.findall(r"^### (PR-\d{2}A?) — ", document, flags=re.MULTILINE))
    assert len(declared) >= 19
    matrix = _read()
    records = matrix["requirements"]
    ids = [row["requirement_id"] for row in records]
    assert len(ids) == len(set(ids))
    assert set(ids) == declared, (
        f"User goals added/removed without updating real business replay matrix: "
        f"missing={sorted(declared - set(ids))}, extraneous={sorted(set(ids) - declared)}"
    )
    for row in records:
        assert row["real_user_business_goal_status"] == "OPEN"
        assert row["necessary_unproven_outcome"]
        ref = ROOT / row["engineering_evidence_test"]
        assert ref.is_file(), f"orphaned engineering proof ref: {row['requirement_id']}"
        assert row["engineering_proof_status"] == "AUTOMATED_COMPONENT_OR_SYNTHETIC_REPLAY_ONLY"
    assert matrix["all_user_requirements_business_accepted"] is False
    assert matrix["live_finance_deep_broad_four_word_user_quality_verified"] is False


def test_counterexamples_cover_the_user_journey_not_only_git_ci_and_security():
    matrix = _read()
    covered = set()
    case_ids = set()
    for case in matrix["counterexample_scenarios"]:
        assert case["id"] not in case_ids
        case_ids.add(case["id"])
        assert (ROOT / case["verifier"]).is_file()
        assert case["failure_injection"] and case["user_goal"]
        assert "PASS" not in case["outcome"] or case["outcome"].endswith("_ONLY")
        covered.update(case["requirement_ids"])
    assert len(case_ids) >= 10
    assert len(covered) >= 15
    assert {"PR-04", "PR-06", "PR-07", "PR-09", "PR-10", "PR-11",
            "PR-12", "PR-13", "PR-14", "PR-15"} <= covered


def test_business_outcome_cannot_be_promoted_by_all_green_synthetic_ci():
    matrix = _read()
    assert matrix["status"] == "USER_WRITING_OUTCOME_NOT_READY"
    assert any("real current primary sources" in item
               for item in matrix["required_live_business_outcome"])
    assert any("user's real evaluation" in item
               for item in matrix["required_live_business_outcome"])
