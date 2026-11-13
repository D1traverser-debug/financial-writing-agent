"""Regression: retired integration artifacts cannot re-enter the Financial runtime."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_retired_parent_stubs_and_duplicate_control_surfaces_are_absent():
    retired=(".uaos","CAOS_SKILL.md","UAOS_SKILL.md","docs/CAOS_CHILD_INTERFACE.md","FINANCIAL_SKILL.md","references","config/PERSISTENT_ASSET_PROFILE.json","config/retired_runtime_paths.json","scripts/retired_runtime_static_audit.py","tests/test_retired_runtime_absence.py","tests/test_uaos_cognition_evolution_inheritance.py","evals/FINANCIAL_UAOS_COGNITION_EVOLUTION_PRODUCT_AUDIT_2026-10-15.md","evals/PARENT_GUIDANCE_HANDOFF.md","evals/PARENT_GUIDANCE_HANDOFF_20261016_CROSS_BORDER_STALE_RESUME.md","evals/uaos_article_binding_2026-10-14.json")
    assert [p for p in retired if (ROOT/p).exists()]==[]

def test_only_two_synchronized_financial_reference_surfaces_remain():
    names=("research.md","knowledge.md","private_research.md","reader_value.md","market_explanation.md","audit.md","editorial.md","hooks.md","style.md","platforms.md","delivery.md","maintenance.md","proactive_resolution.md")
    package=ROOT/"financial_writing_agent/resources/references";skill=ROOT/"skills/financial-writing-agent/references"
    assert not (ROOT/"references").exists()
    for name in names: assert (package/name).read_bytes()==(skill/name).read_bytes()
