import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_chatgpt_plugin_record_matches_canonical_manifest_release():
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    plugin = _json("config/CHATGPT_FINANCIAL_PLUGIN.json")
    canonical = manifest["client_skill_plugin"]
    assert plugin["plugin_id"] == canonical["plugin_id"]
    assert plugin["release_id"] == canonical["release_id"]
    assert plugin["version"] == canonical["version"]


def test_evolution_index_records_pr67_as_merged_not_as_open_candidate():
    assessment = _json("evals/EVOLUTION_INDEX.json")["active_system_assessment"]
    production = assessment["owner_governance_rebuild_20261112"]["production"]
    latest = assessment["latest_production_verification"]
    assert assessment["status"] == "PRODUCTION_MAIN_CI_PASS__SYSTEM_EXTERNAL_ACCEPTANCE_NOT_READY"
    assert production["pr_number"] == 67
    assert production["production_merge"] == "MERGED"
    assert production["merged_main_sha"] == latest["main_sha"]
    assert production["post_merge_ci_conclusion"] == "success"
    assert latest["current_open_pull_requests"] == 0
    assert latest["main_protected"] is False
    assert latest["system_acceptance"] == "NOT_READY__SEVEN_GATES_REQUIRE_REAL_EXTERNAL_EVIDENCE"
