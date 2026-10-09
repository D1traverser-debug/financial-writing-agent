from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_human_voice_craft_mirrors_are_identical():
    root = _read("references/human_voice_craft.md")
    assert root == _read("skills/financial-writing-agent/references/human_voice_craft.md")
    assert root == _read("financial_writing_agent/resources/references/human_voice_craft.md")
    for token in (
        "Fresh-reader blind pass for finance",
        "The five human-reading engines",
        "Real friction creates human texture",
        "Show once, explain once",
        "Do not try to “add human flavor”",
    ):
        assert token in root


def test_headline_craft_mirrors_are_identical():
    root = _read("references/headline_craft.md")
    assert root == _read("skills/financial-writing-agent/references/headline_craft.md")
    assert root == _read("financial_writing_agent/resources/references/headline_craft.md")
    for token in (
        "The headline promise equation",
        "Specificity sweet spot",
        "HeadlineRawMaterial",
        "Title tournament: destructive selection",
        "A good headline does not hide the article",
    ):
        assert token in root


def test_skill_cold_start_routes_to_craft_packs():
    skill = _read("skills/financial-writing-agent/SKILL.md")
    assert "TITLE: everything required by EDITORIAL plus **`references/headline_craft.md`**" in skill
    assert "DRAFT / BROAD_DERIVATION" in skill
    assert "`references/human_voice_craft.md`" in skill
    assert "headline_craft.md` pack is mandatory" in skill
    assert "Fresh Reader blind pass" in skill
    assert "recognizable subject, reader stake, one useful unresolved hinge" in skill


def test_craft_packs_preserve_truth_boundary():
    human = _read("references/human_voice_craft.md")
    headline = _read("references/headline_craft.md")
    assert "never allowed to invent a scene, thought, quote, emotion or fact" in human
    assert "Do not create a false inference" in headline
    assert "A title is part of the factual product" in headline
