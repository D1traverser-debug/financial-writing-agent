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


def test_evolution_index_tracks_pr67_production_without_rewriting_historical_audit():
    assessment = _json("evals/EVOLUTION_INDEX.json")["active_system_assessment"]
    history = assessment["owner_governance_rebuild_20261112"]
    latest = assessment["latest_production_verification"]
    assert assessment["status"] == "PRODUCTION_MAIN_CI_PASS__SYSTEM_EXTERNAL_ACCEPTANCE_NOT_READY"
    assert history["production"]["pr_number"] == 66
    assert history["independent_acceptance_candidate"]["pull_request"] == 67
    assert history["independent_acceptance_candidate"]["pull_request_merged"] is False
    assert latest["merged_pr"] == 67
    assert latest["main_sha"] == "2296223fa3b61a854cf2f4965fe93d96be333b4c"
    assert latest["production_ci_conclusion"] == "success"
    assert latest["current_open_pull_requests_at_observation"] == 0
    assert latest["main_protected_at_observation"] is False
    assert latest["system_acceptance"] == "NOT_READY__SEVEN_GATES_REQUIRE_REAL_EXTERNAL_EVIDENCE"
