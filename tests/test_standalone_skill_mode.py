import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "financial-writing-agent" / "SKILL.md"
SOURCE = ROOT / "references" / "standalone.md"
SKILL_REF = ROOT / "skills" / "financial-writing-agent" / "references" / "standalone.md"
PACKAGE_REF = ROOT / "financial_writing_agent" / "resources" / "references" / "standalone.md"


def test_standalone_profile_is_discoverable_from_cold_start_skill():
    skill = SKILL.read_text(encoding="utf-8")

    assert "references/standalone.md" in skill
    assert "STANDALONE_SKILL" in skill
    assert "ShadowTaskLedger" in skill
    assert "STANDALONE_COMPLETE" in skill
    assert "If Financial Writing Agent MCP Runtime tools are available, use `RUNTIME`" in skill
    assert "do not silently switch an already-started Runtime task into standalone" in skill
    assert "genuinely new task always starts with a fresh `ShadowTaskLedger`" in skill
    assert "Never describe it as deployment-grade determinism or 100% guaranteed execution" in skill


def test_standalone_reference_is_byte_equal_across_all_bundles():
    source = SOURCE.read_bytes()
    assert source
    assert source == SKILL_REF.read_bytes()
    assert source == PACKAGE_REF.read_bytes()


def test_standalone_control_plane_has_state_gates_invalidation_and_completion_barrier():
    text = SOURCE.read_text(encoding="utf-8")

    for marker in (
        "execution_profile = STANDALONE_SKILL",
        "effective_time_boundary",
        "source_obligations",
        "current_stage",
        "revision counters",
        "frozen acceptance contract",
        "exact `next_action`",
        "Revision invalidation is mandatory even without Runtime",
        "SourceCompletion",
        "EvidenceLedger",
        "BROAD_DERIVATION",
        "STANDALONE_COMPLETE",
        "Do not convert “not checked” into PASS",
    ):
        assert marker in text

    assert "research/factual change invalidates editorial, title, draft and all downstream audits/delivery" in text
    assert "draft change invalidates editorial audit, delivery, mechanical audit and final audit" in text
    assert "do not call the task complete" in text


def test_standalone_mode_keeps_dual_deep_first_and_user_reminder_free():
    text = SOURCE.read_text(encoding="utf-8")

    assert "For DUAL, only FINANCE_DEEP is allowed here" in text
    assert "Only after FINANCE_DEEP draft + acceptance contract are frozen" in text
    assert "broad does not introduce a stock absent from the deep mother's material stock set" in text
    assert "Do not ask the user to remind you about normal gates" in text
    assert "title hooks" in text
    assert "stock-judgment specificity" in text


def test_standalone_rules_have_one_registered_owner():
    ownership = json.loads((ROOT / "config" / "rule_ownership.json").read_text(encoding="utf-8"))

    assert ownership["standalone"] == [
        "standalone_execution_profile",
        "shadow_task_ledger",
        "standalone_stage_gating",
        "standalone_revision_invalidation",
        "standalone_completion_barrier",
        "standalone_assurance_boundary",
    ]
