from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "financial-writing-agent" / "SKILL.md"
ROOT_REF = ROOT / "references" / "professional_analysis.md"
SKILL_REF = ROOT / "skills" / "financial-writing-agent" / "references" / "professional_analysis.md"
PACKAGE_REF = ROOT / "financial_writing_agent" / "resources" / "references" / "professional_analysis.md"


def test_professional_analysis_reference_is_mirrored_and_cold_start_loaded():
    root_bytes = ROOT_REF.read_bytes()
    assert root_bytes == SKILL_REF.read_bytes()
    assert root_bytes == PACKAGE_REF.read_bytes()

    skill = SKILL.read_text(encoding="utf-8")
    assert "references/professional_analysis.md" in skill
    assert "event/policy/technology/demand shock" in skill
    assert "industry variable" in skill
    assert "valuation/expectation gap" in skill
    assert "market pricing/stock role" in skill


def test_professional_analysis_prevents_layer_collapse():
    text = ROOT_REF.read_text(encoding="utf-8")
    for marker in (
        "Each arrow is a separate claim",
        "revenue growth ≠ profit growth",
        "accounting profit ≠ cash generation",
        "good company ≠ attractive valuation",
        "positive fundamental change ≠ positive expectation surprise",
        "positive surprise ≠ guaranteed stock-price rise",
    ):
        assert marker in text


def test_metric_comparability_and_realization_stage_are_explicit():
    text = ROOT_REF.read_text(encoding="utf-8")
    for marker in (
        "YoY vs QoQ",
        "TTM, latest quarter, FY actual and forward-year estimates",
        "capacity, output, shipment, sales, order, backlog and recognized revenue",
        "working-capital changes",
        "revenue recognition",
        "cash collection / operating cash flow",
    ):
        assert marker in text


def test_expectation_and_valuation_claims_require_real_baselines():
    text = ROOT_REF.read_text(encoding="utf-8")
    assert "“超预期/低于预期/预期差” requires a real expectation reference" in text
    assert "Do not use “便宜/贵/低估/高估/空间大/估值修复” as decorative adjectives" in text
    assert "Price and intrinsic/business value are not the same" in text
    assert "fundamental change" in text
    assert "current market pricing/positioning" in text


def test_foreign_guidance_is_not_misrepresented_as_a_share_law():
    text = ROOT_REF.read_text(encoding="utf-8")
    assert "only as an analytical/comparability heuristic" in text
    assert "not as Chinese regulatory law" in text
    assert "Chinese law/accounting/disclosure rules" in text
    assert "Never import a foreign regulatory requirement as if it governed an A-share issuer" in text


def test_professionalism_does_not_create_a_fixed_research_template():
    text = ROOT_REF.read_text(encoding="utf-8")
    skill = SKILL.read_text(encoding="utf-8")
    assert "It is not a mandatory fixed article outline" in text
    assert "Do not turn the analytical ladder into a repetitive six-section template" in text
    assert "Use only the financial layers material to the current thesis" in skill
