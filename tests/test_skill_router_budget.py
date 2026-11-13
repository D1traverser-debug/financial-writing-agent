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


def test_only_financial_skill_is_an_operating_entry():
    import json

    manifest = json.loads((ROOT / "config/FINANCIAL_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["skill_entrypoint"] == "skills/financial-writing-agent/SKILL.md"
    for retired in ("FINANCIAL_SKILL.md", "CAOS_SKILL.md", "UAOS_SKILL.md", ".uaos"):
        assert not (ROOT / retired).exists()
