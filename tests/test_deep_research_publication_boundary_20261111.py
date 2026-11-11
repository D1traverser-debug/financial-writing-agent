"""R2 regression: complete private company research does not force Deep list dumping."""
import json
from pathlib import Path
from types import SimpleNamespace

from financial_writing_agent.checks import check_deep_company_grounding
from financial_writing_agent.current_admission import requirement_context_for_scope


ROOT = Path(__file__).resolve().parents[1]


def _payload(text):
    return SimpleNamespace(blocks=[SimpleNamespace(kind="body", text=text)])


def _research():
    return SimpleNamespace(
        universe=[
            SimpleNamespace(name="甲公司", materiality="MATERIAL"),
            SimpleNamespace(name="乙公司", materiality="MATERIAL"),
            SimpleNamespace(name="丙公司", materiality="MATERIAL"),
            SimpleNamespace(name="弱标签", materiality="NON_MATERIAL"),
        ],
        company_decision_map=object(),
    )


def test_deep_default_selects_economically_decisive_company_pair_not_all_research_names():
    draft = _payload(
        "甲公司的合同履约强于乙公司，财务兑现更快；乙公司仍受验收周期影响。"
        "丙公司虽被研究但在此比较中不影响当前结论。"
    )
    # With all present the strict and the selective contracts both pass.
    assert check_deep_company_grounding(draft, _research()) == []


def test_deep_default_does_not_force_weak_or_unselected_material_names():
    draft = _payload("甲公司的经营兑现强于乙公司；乙公司的现金周期更长，因此当前证据强度较弱。")
    assert check_deep_company_grounding(draft, _research()) == []


def test_explicit_full_universe_requirement_still_forbids_silent_omission():
    draft = _payload("甲公司的利润兑现强于乙公司，且乙公司的现金回收滞后。")
    errors = check_deep_company_grounding(
        draft, _research(), require_complete_material_universe=True
    )
    assert errors == [
        "FINANCE_DEEP omitted required full-universe MATERIAL company: 丙公司"
    ]


def test_scope_override_is_derived_from_actual_child_requirement_context_not_policy_guess():
    state = json.loads(
        (ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v3/STATE.json")
        .read_text(encoding="utf-8")
    )
    context = requirement_context_for_scope(state, "FINANCE_DEEP")
    ids = {item["requirement_id"] for item in context["requirements"]}
    assert "deep_complete_retained_universe" in ids
    assert context["revision"] == state["task_requirement_authority"]["revision"]
    assert context["digest"] == state["task_requirement_digest"]


def test_deep_still_requires_real_named_comparison_even_when_some_companies_omitted():
    draft = _payload("甲公司有优势，乙公司也不错。")
    issues = check_deep_company_grounding(draft, _research())
    assert any("named evidence-bounded comparative verdict" in item for item in issues)
