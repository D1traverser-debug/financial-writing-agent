"""Machine-checkable concordance of Financial research/private versus public Deep scope."""

import json
from pathlib import Path

from financial_writing_agent.resources import load_packaged_policy


ROOT = Path(__file__).resolve().parents[1]


def test_deep_policy_is_research_complete_and_default_publication_selective():
    source = load_packaged_policy()
    assert source["contract_version"] == "0.9.2"
    research = source["research"]
    editorial = source["editorial"]
    assert research["silent_company_omission_forbidden"] is True
    assert editorial["finance_deep_material_research_complete_required"] is True
    assert editorial["finance_deep_publication_scope_decisions_required_for_omitted_material_classes"] is True
    assert editorial["finance_deep_selected_company_economic_comparison_required"] is True
    assert editorial["finance_deep_complete_company_visibility_only_for_admitted_task_requirement"] is True
    assert editorial["finance_deep_default_mode"] == "RESEARCH_COMPLETE__PUBLICATION_SELECTIVE__SOURCE_BOUND"
    assert editorial["finance_deep_material_complete"] is False
    assert editorial["finance_deep_material_company_mentions_required"] is False
    assert editorial["finance_deep_representative_stock_shortcut_forbidden"] is False


def test_deep_policy_migration_does_not_remove_current_v3_task_specific_requirement():
    state = json.loads(
        (ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v3/STATE.json")
        .read_text(encoding="utf-8")
    )
    ids = {r["requirement_id"] for r in state["task_requirement_authority"]["active_requirements"]}
    assert {"full_universe_research_pool", "deep_complete_retained_universe"}.issubset(ids)
