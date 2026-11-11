from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "skills/financial-writing-agent/SKILL.md"
ROOT_POINTER = ROOT / "FINANCIAL_SKILL.md"


def test_financial_skill_is_self_sufficient_domain_workflow():
    text = PRIMARY.read_text(encoding="utf-8")
    assert 1000 < len(text.encode("utf-8")) < 12000
    for keyword in (
        "Financial Writing", "Independent Operating Skill", "Decision", "Execution",
        "PrivateResearchBrief", "Deep", "Broad", "DOCX",
        "standalone_runtime.py", "current_admission", "requirements",
        "source", "originality", "quality",
    ):
        assert keyword.lower() in text.lower(), keyword
    assert "continuity/" not in text


def test_root_pointer_and_old_paths_have_no_active_control():
    assert "skills/financial-writing-agent/SKILL.md" in ROOT_POINTER.read_text(encoding="utf-8")
    assert "non-authoritative" in (ROOT / "CAOS_SKILL.md").read_text(encoding="utf-8")
    assert "non-authoritative" in (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
