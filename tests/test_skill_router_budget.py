from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "UAOS_SKILL.md"
DISCOVERY = ROOT / "skills/financial-writing-agent/SKILL.md"


def test_current_skill_is_thin_current_entry_not_domain_rulebook_dump():
    text = CURRENT.read_text(encoding="utf-8")
    assert len(text.encode("utf-8")) <= 8192
    for ref in (
        ".uaos/ADAPTER.json", ".uaos/MANIFEST.json", ".uaos/CAPABILITIES.json",
        "config/EXECUTION_CONTRACT.json", "references/research.md", "references/audit.md",
        "references/editorial.md", "references/hooks.md", "references/style.md",
        "references/delivery.md", "references/maintenance.md",
    ):
        assert ref in text
    assert "continuity/" not in text


def test_packaged_skill_is_discovery_pointer_only():
    text = DISCOVERY.read_text(encoding="utf-8")
    assert "Discovery Pointer" in text
    assert "UAOS_SKILL.md" in text
    assert len(text.encode("utf-8")) < 4096
    assert "continuity/" not in text
