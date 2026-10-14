import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_domain_repo_contains_no_controller_task_index_or_system_infra_checkpoint():
    assert not (ROOT / "continuity").exists()
    assert not (ROOT / "TASK_INDEX.json").exists()
    assert not (ROOT / "TASK_INDEX.md").exists()
    assert not list(ROOT.glob("**/HANDOFF.md")), "domain repo must not host controller handoff state"


def test_comparison_dimensions_are_topic_specific_not_technology_template():
    policy = json.loads((ROOT / "config/policy.json").read_text(encoding="utf-8"))
    editorial = policy["editorial"]
    assert editorial["company_comparison_dimensions_policy"] == "TOPIC_SPECIFIC_FROM_CURRENT_AUDITED_EVIDENCE"
    assert editorial["fixed_cross_topic_comparison_dimension_list_forbidden"] is True
    assert "company_comparison_dimensions" not in editorial


def test_visible_delivery_is_not_proven_by_filename_and_hash():
    policy = json.loads((ROOT / "config/policy.json").read_text(encoding="utf-8"))
    visible = policy["visible_delivery"]
    assert visible["fresh_current_session_resource_required"] is True
    assert visible["filename_and_hash_alone_are_availability_proof"] is False
    assert visible["regenerated_binary_is_new_instance"] is True
    skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    assert "current" in skill.lower()
    assert "deliver" in skill.lower() or "Completion" in skill


def test_delivery_reference_mirrors_include_current_resource_availability_contract():
    source = (ROOT / "references/delivery.md").read_bytes()
    skill = (ROOT / "skills/financial-writing-agent/references/delivery.md").read_bytes()
    package = (ROOT / "financial_writing_agent/resources/references/delivery.md").read_bytes()
    assert source == skill == package
    text = source.decode("utf-8")
    assert "Current visible-delivery availability" in text
    assert "filename + SHA-256 alone is artifact identity, not current resource availability" in text
