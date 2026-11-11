"""Historical parent inheritance removed: finance adopts its own methods."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_financial_cognition_and_executor_are_direct_not_hosted():
    contract = _json("config/EXECUTION_CONTRACT.json")
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    caps = _json("config/FINANCIAL_CAPABILITIES.json")
    assert manifest["controller"] == "FINANCIAL_WRITING_OWNER"
    assert contract["standalone_governance"]["external_parent_required"] is False
    assert caps["independent_parent_free"] is True
    assert contract["problem_and_evolution"]["generic_problem_cognition_owner"] == "FINANCIAL_WRITING_OWNER"
    assert contract["cognition_and_decision"]["problem_or_architecture_change_requires_external_method_evidence"] is True
    assert contract["execution"]["route_selection"] == "DIRECT_FINANCIAL_ONLY"


def test_financial_evolution_does_not_upcall_parent():
    contract = _json("config/EXECUTION_CONTRACT.json")
    ownership = _json("config/rule_ownership.json")
    assert contract["problem_and_evolution"]["common_or_cross_domain_change_uses_parent_upcall"] is False
    assert contract["problem_and_evolution"]["systemic_change_requires_regression_or_eval_evidence"] is True
    assert contract["problem_and_evolution"]["post_promotion_observation_required_for_evolution_closure"] is True
    assert contract["problem_and_evolution"]["one_off_observation_auto_promotes_to_global_rule"] is False
    assert "financial_local_cross_domain_method_adaptation" in ownership["cognition"]
    assert "financial_only_method_adaptation_and_revalidation" in ownership["maintenance"]


def test_financial_product_and_maintenance_have_no_parent_authority():
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    product = (ROOT / "docs/product_requirements.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    maint = (ROOT / "references/maintenance.md").read_text(encoding="utf-8")
    assert manifest["product_requirements"] == "docs/product_requirements.md"
    assert manifest["architecture"] == "docs/architecture.md"
    for fragment in ("Product outcome", "Primary user journeys", "Functional requirement map",
                     "Failure and recovery semantics", "Explicit non-goals",
                     "Product completion criteria", "Acceptance evidence"):
        assert fragment in product
    assert "Financial-owned cognition" in architecture
    assert "standalone Financial" in architecture
    assert "Decision loop" in maint and "Execution loop" in maint
    assert "no parent upcall" in maint


def test_all_packaged_financial_maintenance_mirrors_equal():
    root = (ROOT / "references/maintenance.md").read_text(encoding="utf-8")
    packed = (ROOT / "financial_writing_agent/resources/references/maintenance.md").read_text(encoding="utf-8")
    skill = (ROOT / "skills/financial-writing-agent/references/maintenance.md").read_text(encoding="utf-8")
    assert root == packed == skill
    assert "standalone" in root
    assert "independent" in root.lower()
    assert "record_proactive_resolution_state" in root


def test_financial_skill_alone_starts_owner_directly():
    skill = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    contract = _json("config/EXECUTION_CONTRACT.json")
    assert "standalone_runtime.py" in skill
    assert "current_admission" in skill
    assert contract["execution"]["direct_domain_activation"] is True
    assert contract["execution"]["live_parent_business_proxy_required"] is False
