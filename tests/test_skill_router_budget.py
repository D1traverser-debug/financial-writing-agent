from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/financial-writing-agent/SKILL.md"


def test_financial_skill_is_thin_router_not_domain_rulebook():
    text = SKILL.read_text(encoding="utf-8")
    assert len(text.encode("utf-8")) <= 8192
    assert "This Skill is a thin router" in text
    for ref in (
        "references/research.md",
        "references/audit.md",
        "references/editorial.md",
        "references/hooks.md",
        "references/style.md",
        "references/delivery.md",
        "references/maintenance.md",
        "continuity/EXECUTION_CAPABILITIES.json",
    ):
        assert ref in text
