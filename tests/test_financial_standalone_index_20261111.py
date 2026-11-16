"""Financial's current system authority does not point back to the retired parent."""
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_single_current_financial_evolution_ref_is_standalone_and_local():
    idx = _json("evals/EVOLUTION_INDEX.json")["active_system_assessment"]
    m = _json("config/FINANCIAL_MANIFEST.json")
    assert idx["current_method_owner"] == m["controller"] == "FINANCIAL_WRITING_OWNER"
    assert idx["current_runtime_authority"] == "config/FINANCIAL_MANIFEST.json"
    assert idx["review_ref"] == "evals/FINANCIAL_STANDALONE_REBUILD_AUDIT_20261111.md"
    assert idx["current_operating_skill"] == m["skill_entrypoint"]
    assert "parent_governance_ref" not in idx
    assert m["external_parent_required"] is False
    assert m["external_host_required"] is True
    assert m["provider_action_required"] is True
    assert m["client_skill_plugin"]["custom_hosted_service_required"] is True
    assert "active_parent_dependency" not in idx["standalone_reconstruction"]
    assert idx["standalone_reconstruction"]["production_merge_verified"] is True
    assert idx["standalone_reconstruction"]["editorial_acceptance"] == "NOT_READY"


def test_current_system_candidate_records_exact_requirement_scope_repair_evidence():
    index = _json("evals/EVOLUTION_INDEX.json")
    candidate = index["current_system_candidate"]
    assert candidate["id"] == "FIN-REQUIREMENT-SCOPE-STAGE-DATAFLOW-20261116"
    assert candidate["pull_request"] == 84
    assert isinstance(candidate["candidate_head_sha"], str) and len(candidate["candidate_head_sha"]) == 40
    assert isinstance(candidate["exact_head_ci_run"], int) and candidate["exact_head_ci_run"] > 0
    assert candidate["exact_head_ci_conclusion"] == "success"
    assert isinstance(candidate["tests_passed"], int) and candidate["tests_passed"] > 0
    assert candidate["source_line_coverage_percent"] >= 0
    assert candidate["status"] == "CANDIDATE__EXACT_CODE_HEAD_CI_PASS__NOT_MERGED__INDEPENDENT_REVIEW_OPEN"
    assert "PROVIDER_ACTION_NOT_DEPLOYED" in candidate["limitations"]
    assert "TOP_LEVEL_COMPANY_DECISION_MAP_AND_CHANGE_CONDITIONS_EXACTLY_MATCH_VALIDATED_RESEARCH_PACKAGE" in candidate["verified"]
    assert index["active_system_assessment"]["latest_requirement_scope_dataflow_candidate"] == candidate

    manifest = _json("config/FINANCIAL_MANIFEST.json")
    scope_contract = manifest["task_requirement_scope_contract"]
    assert scope_contract["status"] == "CANDIDATE_FIX__EXACT_CODE_HEAD_CI_PASS__INDEPENDENT_REVIEW_OPEN"
    assert scope_contract["verified_code_head_sha"] == candidate["candidate_head_sha"]
    assert scope_contract["exact_code_head_ci_run"] == candidate["exact_head_ci_run"]

    audit = (ROOT / candidate["audit_ref"]).read_text(encoding="utf-8")
    assert f"**Verified candidate code head:** `{candidate['candidate_head_sha']}`" in audit
    assert f"**Exact code-head CI:** [{candidate['exact_head_ci_run']}]" in audit

    journal_index = _json("evals/PROBLEM_EVOLUTION_JOURNAL_INDEX.json")
    assert journal_index["revision"] == index["active_system_assessment"]["problem_journal_revision"]
    assert journal_index["latest_incident_id"] == "P-20261116-04"
    assert journal_index["latest_incident_ref"].endswith("#P-20261116-04")
    journal = (ROOT / "evals/PROBLEM_EVOLUTION_JOURNAL.md").read_text(encoding="utf-8")
    assert candidate["problem_ref"] in journal
    assert journal_index["latest_incident_id"] in journal
    assert candidate["candidate_head_sha"] in journal
    assert str(candidate["exact_head_ci_run"]) in journal


def test_product_version_tracks_independent_package_not_prior_child_era():
    package = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = (ROOT / "docs/product_requirements.md").read_text(encoding="utf-8")
    assert package["project"]["version"] == "1.1.0"
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    assert manifest["skill_entrypoint"] == "skills/financial-writing-agent/SKILL.md"
    assert manifest["data_authority"] == "config/DATA_AUTHORITY.json"
    assert "1.1.0_STANDALONE_FINANCIAL" in requirements
    assert "no external parent" in requirements.lower()
