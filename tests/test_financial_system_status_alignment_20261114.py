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

def test_pr84_requirement_scope_candidate_matches_live_merge_receipts():
    index = _json("evals/EVOLUTION_INDEX.json")
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    candidate = index["current_system_candidate"]
    assert candidate["pull_request"] == 84
    assert candidate["status"] == "MERGED_TO_MAIN__EXACT_MAIN_CI_PASS__INDEPENDENT_REVIEW_OPEN__REAL_ARTICLE_QUALITY_OPEN"
    assert candidate["candidate_head_sha"] == "8c8dc0595aae9f63c889363db6a78216b81af6fe"
    assert candidate["exact_head_ci_run"] == 43833247888
    assert candidate["merged_main_sha"] == "7dbde945e98712856d7d6a19b8fe06b2efc500ab"
    assert candidate["exact_main_ci_run"] == 43833864946
    assert candidate["exact_main_ci_conclusion"] == "success"
    assert index["active_system_assessment"]["latest_requirement_scope_dataflow_candidate"] == candidate

    for name in (
        "task_requirement_scope_contract",
        "full_universe_research_evidence_contract",
        "research_to_editorial_dataflow",
    ):
        record = manifest[name]
        assert record["status"] == "MERGED_TO_MAIN__EXACT_PR_AND_MAIN_CI_PASS__INDEPENDENT_REVIEW_OPEN"
        assert record["verified_code_head_sha"] == candidate["candidate_head_sha"]
        assert record["exact_code_head_ci_run"] == candidate["exact_head_ci_run"]
        assert record["merged_main_sha"] == candidate["merged_main_sha"]
        assert record["exact_main_ci_run"] == candidate["exact_main_ci_run"]

    phase = index["active_system_assessment"]["next_legal_phase"]
    assert "PR #84 remains Draft" not in phase
    assert "PR #84" in phase and "PR #85" in phase and "PR #86" in phase and "PR #87" in phase and "PR #88" in phase
    latest_validated_head = index["active_system_assessment"]["general_writing_stability"]["latest_main_head_sha"]
    assert manifest["general_writing_stability"]["last_completed_ci_head"] == latest_validated_head


def test_pr85_caos_governance_candidate_matches_live_merge_receipts_without_caos_mutation():
    index = _json("evals/EVOLUTION_INDEX.json")
    candidate = index["current_governance_candidate"]
    assert candidate["pull_request"] == 85
    assert candidate["status"] == "MERGED_TO_MAIN__EXACT_MAIN_CI_PASS__CAOS_SOURCE_UNMODIFIED"
    assert candidate["candidate_head_sha"] == "c28410e3925276f3bd040acdcfba69dd5cb0d993"
    assert candidate["merge_commit_sha"] == "d024da5aff37dcd00cbf69467d8333e0c7d37132"
    assert candidate["exact_main_ci_head_sha"] == "b2098e69367f78c452e0a595bf95d86388d6a449"
    assert candidate["exact_main_ci_run"] == 43626092503
    assert candidate["exact_main_ci_conclusion"] == "success"
    assert candidate["caos_source_mutation"] == "FORBIDDEN"


def test_pr86_interaction_quality_evaluator_is_merged_but_real_quality_is_not_promoted():
    index = _json("evals/EVOLUTION_INDEX.json")
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    candidate = index["current_quality_evaluator_candidate"]
    assert candidate["pull_request"] == 86
    assert candidate["candidate_head_sha"] == "355d03c99247be4a151cf89be35d405f956e4e21"
    assert candidate["exact_head_ci_run"] == 43838790518
    assert candidate["exact_head_ci_conclusion"] == "success"
    assert candidate["tests_passed"] == 730
    assert candidate["source_line_coverage_percent"] == 88
    assert "NO_REAL_INTERACTION_USER_REJECTION_CASE" in candidate["limitations"]
    assert "NO_TWO_COMPLETE_INTERACTION_HELDOUT_TOPIC_FAMILIES" in candidate["limitations"]
    assert manifest["general_writing_stability"]["portfolio_quality_readiness"]["PLATFORM_INTERACTION"] == "NOT_READY__MODE_SUPPORTED__MODE_SPECIFIC_REJECTION_AND_TWO_HELDOUT_FAMILIES_MISSING"


def test_last_independently_validated_main_head_ci_is_recorded_separately_from_last_code_merge():
    index = _json("evals/EVOLUTION_INDEX.json")
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    stability = index["active_system_assessment"]["general_writing_stability"]
    assert stability["latest_main_head_sha"] == "44eeaea6f871ed4006d7e98a36dd9375a5fc87ea"
    assert stability["latest_main_head_ci_run"] == 43924128311
    assert stability["latest_main_head_ci_conclusion"] == "success"
    assert manifest["general_writing_stability"]["latest_main_head_sha"] == stability["latest_main_head_sha"]
    assert manifest["general_writing_stability"]["latest_main_head_ci_run"] == stability["latest_main_head_ci_run"]

def test_current_integration_status_candidate_has_exact_code_head_ci_and_stack_boundary():
    index = _json("evals/EVOLUTION_INDEX.json")
    candidate = index["current_integration_status_candidate"]
    assert candidate["pull_request"] == 87
    assert candidate["status"] == "MERGED_TO_MAIN__EXACT_PR_AND_MAIN_CI_PASS__LIVE_EDITORIAL_QUALITY_OPEN"
    assert candidate["candidate_code_head_sha"] == "09d0d1ab43e2ce0c61337038ea640e08caf99f61"
    assert candidate["exact_code_head_ci_run"] == 43840533953
    assert candidate["exact_code_head_ci_conclusion"] == "success"
    assert candidate["tests_passed"] == 734
    assert candidate["source_line_coverage_percent"] == 88
    assert candidate["exact_main_ci_tests_passed"] == 735
    assert candidate["base_branch"] == "main"
    assert candidate["base_head_sha"] == "56527db2461cc54ee04165cfae7e1c692662d700"
    assert candidate["merged_main_sha"] == "01a8eace63cd0a60c6351e7db8584031a1503d3c"
    assert candidate["exact_main_ci_run"] == 43908127624
    assert candidate["exact_main_ci_conclusion"] == "success"



def test_pr88_execution_profile_candidate_is_merged_with_exact_main_ci():
    index = _json("evals/EVOLUTION_INDEX.json")
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    candidate = index["current_writing_execution_profile_candidate"]
    assert candidate["pull_request"] == 88
    assert candidate["status"] == "MERGED_TO_MAIN__EXACT_PR_AND_MAIN_CI_PASS__REAL_EDITORIAL_ACCEPTANCE_OPEN"
    assert candidate["candidate_head_sha"] == "fa09b5b981d10bfcd68396bbcc7c8f3ec8b92e57"
    assert candidate["exact_head_ci_run"] == 43908350311
    assert candidate["exact_head_ci_conclusion"] == "success"
    assert candidate["tests_passed"] == 746
    assert candidate["merged_main_sha"] == "3fea4dd079785cd534827d24e72898c9e8c793c4"
    assert candidate["exact_main_ci_run"] == 43908728749
    assert candidate["exact_main_ci_conclusion"] == "success"
    assert manifest["general_writing_stability"]["execution_profile_implementation"]["merged_main_sha"] == candidate["merged_main_sha"]
    assert candidate["skill_utf8_bytes"] == 11403


def test_pr89_decision_domain_binding_is_merged_with_exact_pr_and_main_ci():
    index = _json("evals/EVOLUTION_INDEX.json")
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    candidate = index["current_execution_profile_decision_binding_candidate"]
    assert candidate == index["active_system_assessment"]["current_execution_profile_decision_binding_candidate"]
    assert candidate["pull_request"] == 89
    assert candidate["status"] == "MERGED_TO_MAIN__EXACT_PR_AND_MAIN_CI_PASS__INDEPENDENT_TECHNICAL_REVIEW_OPEN__REAL_MODEL_SEMANTIC_ACCEPTANCE_OPEN"
    assert candidate["candidate_code_head_sha"] == "d7db51af2b7d9c91489b489929528ce39cd6c951"
    assert candidate["final_pr_head_sha"] == "fabdd6a0b41ffeaf509350720f3b8e370525bcb0"
    assert candidate["exact_head_ci_run"] == 43922363378
    assert candidate["exact_head_ci_conclusion"] == "success"
    assert candidate["exact_head_tests_passed"] == 758
    assert candidate["merged_main_sha"] == "44eeaea6f871ed4006d7e98a36dd9375a5fc87ea"
    assert candidate["exact_main_ci_run"] == 43924128311
    assert candidate["exact_main_ci_conclusion"] == "success"
    assert candidate["exact_main_ci_tests_passed"] == 758
    implementation = manifest["general_writing_stability"]["execution_profile_decision_binding_implementation"]
    assert implementation["merged_main_sha"] == candidate["merged_main_sha"]
    assert implementation["exact_head_ci_run"] == candidate["exact_head_ci_run"]
    assert implementation["exact_main_ci_run"] == candidate["exact_main_ci_run"]
    assert manifest["general_writing_stability"]["latest_main_head_sha"] == candidate["merged_main_sha"]
    assert manifest["general_writing_stability"]["latest_main_head_ci_run"] == candidate["exact_main_ci_run"]
    assert manifest["general_writing_stability"]["execution_profile"]["schema_version"] == "1.1"
