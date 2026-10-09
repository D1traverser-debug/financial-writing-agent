from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STYLE_PATHS = [
    ROOT / "references" / "style.md",
    ROOT / "skills" / "financial-writing-agent" / "references" / "style.md",
    ROOT / "financial_writing_agent" / "resources" / "references" / "style.md",
]


def test_style_mirrors_match_and_lock_narrative_finance_contract():
    texts = [path.read_text(encoding="utf-8") for path in STYLE_PATHS]
    assert texts[0] == texts[1] == texts[2]
    text = texts[0]

    required = [
        "NARRATIVE_FINANCE_EXPLAINER",
        "ladder of abstraction",
        "dry/light humor as a scalpel, not confetti",
        "Narrative continuity / progressive depth",
        "Company paragraphs should normally be non-permutable",
        "Complexity-aware depth sufficiency",
        "6,000–9,000 Chinese characters",
        "below roughly **5,500 Chinese characters**",
        "Source invisibility / research-process concealment",
        "原报告 / 原摘要 / 研报里提到",
        "full rewrite from a different narrative spine",
    ]
    for phrase in required:
        assert phrase in text, phrase


def test_style_contract_forbids_research_process_leakage():
    text = STYLE_PATHS[0].read_text(encoding="utf-8")
    assert "The final article should **digest** source material" in text
    assert "It should not expose where the writer happened to discover the idea" in text
