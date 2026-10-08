from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "financial-writing-agent" / "SKILL.md"
ROOT_READER_VALUE = ROOT / "references" / "reader_value.md"
SKILL_READER_VALUE = ROOT / "skills" / "financial-writing-agent" / "references" / "reader_value.md"
PACKAGE_READER_VALUE = ROOT / "financial_writing_agent" / "resources" / "references" / "reader_value.md"
PLATFORMS = ROOT / "references" / "platforms.md"
KNOWLEDGE = ROOT / "references" / "knowledge.md"


def test_reader_value_reference_is_cold_start_loaded_and_mirrored():
    root_bytes = ROOT_READER_VALUE.read_bytes()
    assert root_bytes == SKILL_READER_VALUE.read_bytes()
    assert root_bytes == PACKAGE_READER_VALUE.read_bytes()

    skill = SKILL.read_text(encoding="utf-8")
    assert "references/reader_value.md" in skill
    assert "truthful acquisition" in skill
    assert "non-obvious information delta" in skill
    assert "what the target reader learns that was not obvious before reading" in skill


def test_reader_value_contract_prioritizes_information_gain_without_fake_novelty():
    text = ROOT_READER_VALUE.read_text(encoding="utf-8")
    assert "Non-obvious delta" in text
    assert "Decision/understanding delta" in text
    assert "Professional depth is not measured by how many facts were collected" in text
    assert "Do not manufacture novelty" in text
    assert "information scent" in text
    assert "coherent scan path" in text


def test_platform_experience_samples_preserve_measurement_context():
    text = PLATFORMS.read_text(encoding="utf-8")
    for marker in (
        "ArticleExperienceSample",
        "observation window",
        "traffic-source mix",
        "confounders",
        "reader-feedback samples kept separate from behavioral metrics",
        "promotion_status = SAMPLE_ONLY",
        "0`, missing and unavailable are distinct states",
    ):
        assert marker in text


def test_single_performance_sample_cannot_be_promoted_as_algorithm_law():
    platforms = PLATFORMS.read_text(encoding="utf-8")
    knowledge = KNOWLEDGE.read_text(encoding="utf-8")
    reader_value = ROOT_READER_VALUE.read_text(encoding="utf-8")

    assert "One high- or low-performing article is not a durable method" in platforms
    assert "does **not** implement an automatic cross-task causal-learning/promotion engine" in platforms
    assert "does not yet expose an executable automatic ArticleExperienceSample-to-rule promotion workflow" in knowledge
    assert "may not invent missing metrics or promote one successful/failed article into a causal rule" in reader_value


def test_business_value_does_not_override_truth_or_trust():
    text = ROOT_READER_VALUE.read_text(encoding="utf-8")
    assert "Commercial value without quality arbitrage" in text
    assert "acquisition cannot be optimized independently of opening payoff" in text
    assert "completion cannot be optimized by deleting information that changes the conclusion" in text
    assert "repeat trust, bookmark/share value and author credibility are commercial assets" in text
