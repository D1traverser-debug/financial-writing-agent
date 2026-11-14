"""Owner-scoped, current-source whole-product assurance: no acceptance by file presence."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from financial_writing_agent.whole_system_assurance import (
    REQUIRED_PRODUCT_REQUIREMENTS,
    _git_blob_sha,
    inspect_active_article,
    project_whole_system,
)

ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40
TASK = "cross-border-ecommerce-20261016-v3"


def _copy_project(tmp_path):
    # Exact current repo snapshots, not invented "green" Article states.
    shutil.copytree(
        ROOT, tmp_path / "repo",
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache",
                                    ".coverage", "audit", "dist", "*.pyc"),
    )
    return tmp_path / "repo"


def test_current_project_has_single_canonical_owner_and_all_19_requirement_pointers():
    result = project_whole_system(ROOT, head_sha=HEAD)
    assert len(REQUIRED_PRODUCT_REQUIREMENTS) == 19
    assert result["product_requirement_total"] == 19
    assert set(result["product_requirement_traces"]) == REQUIRED_PRODUCT_REQUIREMENTS
    assert all(item["missing_pointers"] == [] for item in result["product_requirement_traces"].values())
    assert all(item["independent_business_outcome"] == "NOT_VERIFIED"
               for item in result["product_requirement_traces"].values())
    assert result["structural_violations"] == []
    assert result["method_catalog"]["record_count"] >= 1
    assert len(result["open_system_gates"]) == 7
    assert result["whole_product_status"].startswith("NOT_READY")
    assert result["next_legal_step"] == "CLOSE_AUTHENTICATED_EXECUTION_PATH_AND_INDEPENDENT_BUSINESS_EVIDENCE__NO_UNREQUESTED_ARTICLE_PRODUCTION"


def test_real_cross_border_v3_is_research_0_of_4_not_a_completed_article():
    report = project_whole_system(ROOT, head_sha=HEAD)
    live = [a for a in report["current_articles"] if a["task_id"] == TASK]
    assert len(live) == 1
    state = live[0]
    assert state["status"] == "IN_PROGRESS"
    assert state["stage"] == "RESEARCH"
    assert state["required_output_count"] == 4
    assert state["recorded_output_count"] == 0
    assert {"full_universe_research_pool", "deep_complete_retained_universe"} == set(
        state["active_task_requirement_ids"]
    )
    assert all(ref["locally_available"] for ref in state["source_readbacks"])
    assert any(x["obligation"] == "private_research_brief" for x in state["open_obligations"])
    assert state["business_outcome"].startswith("NOT_READY")
    assert "cross-border-ecommerce-20261016-v2" in report["historical_article_ids"]


def test_root_cause_probe_detects_plugin_and_policy_mirror_drift_in_one_pass(tmp_path):
    work = _copy_project(tmp_path)
    config = work / "config/CHATGPT_FINANCIAL_PLUGIN.json"
    obj = json.loads(config.read_text(encoding="utf-8"))
    obj["release_id"] = "pluginrel_wrong"
    config.write_text(json.dumps(obj), encoding="utf-8")
    mirror = work / "financial_writing_agent/resources/references/style.md"
    mirror.write_text(mirror.read_text(encoding="utf-8") + "\nUNAPPROVED_EXTRA_RULE\n", encoding="utf-8")
    result = project_whole_system(work, head_sha=HEAD)
    assert "PLUGIN_RELEASE_IDENTITY_DRIFT:release_id" in result["structural_violations"]
    assert "POLICY_REFERENCE_MIRROR_BYTES_DRIFT:style.md" in result["structural_violations"]
    assert result["next_legal_step"] == "REPAIR_STRUCTURAL_VIOLATIONS_BEFORE_ANY_STATE_MUTATION"


def test_fake_terminal_article_is_not_promoted_by_word_metadata(tmp_path):
    work = _copy_project(tmp_path)
    file = work / "workspaces/articles" / TASK / "STATE.json"
    state = json.loads(file.read_text(encoding="utf-8"))
    state["status"] = "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN"
    state["delivery_artifacts"] = {
        kind: {"sha256": "b" * 64} for kind in state["required_outputs"]
    }
    file.write_text(json.dumps(state), encoding="utf-8")
    result = project_whole_system(work, head_sha=HEAD)
    assert any("CURRENT_ARTICLE_AGGREGATE_INVALID" in issue
               for issue in result["structural_violations"])
    assert result["whole_product_status"].startswith("NOT_READY")


def test_immutable_source_and_stage_refs_are_checked_as_bytes_not_trusted_names(tmp_path):
    work = _copy_project(tmp_path)
    file = work / "workspaces/articles" / TASK / "STATE.json"
    state = json.loads(file.read_text(encoding="utf-8"))
    stage_file = file.parent / "stages/RESEARCH.md"
    stage_file.parent.mkdir(exist_ok=True)
    stage_file.write_text("Current research fixture source bytes", encoding="utf-8")
    state["stage_artifacts"]["RESEARCH"] = {
        "path": f"workspaces/articles/{TASK}/stages/RESEARCH.md",
        "blob_sha": "0" * 40,
    }
    file.write_text(json.dumps(state), encoding="utf-8")
    inspected = inspect_active_article(work, file)
    assert "STAGE_ARTIFACT_READBACK_FAILED:RESEARCH" in inspected["structural_violations"]
    assert _git_blob_sha(b"Current research fixture source bytes") != "0" * 40


def test_unverified_owner_live_runtime_does_not_get_silent_acceptance_label():
    result = project_whole_system(ROOT, head_sha=HEAD)
    assert result["external_system_acceptance"].startswith("NOT_READY")
    assert "NATIVE_CHAT_DIRECT_GITHUB_WRITES_DO_NOT_EXECUTE_PYTHON_ADMISSION_GUARD" in result["unverified_runtime_boundaries"]
    assert not any(a["business_outcome"].startswith("READY") for a in result["current_articles"])


def test_audit_proof_must_bind_to_a_real_sha():
    with pytest.raises(ValueError, match="EXACT_SOURCE_HEAD_SHA_REQUIRED"):
        project_whole_system(ROOT, head_sha="main")
