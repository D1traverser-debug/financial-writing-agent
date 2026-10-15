from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_value_chain_preflight_is_hard_before_thesis_selection():
    text = (ROOT / "references" / "research.md").read_text(encoding="utf-8")
    required = [
        "Mandatory value-chain preflight",
        "hard pre-thesis requirement",
        "No research package may call its thesis",
        "Thesis selection happens **after** the map exists",
        "Value-Chain Coverage Map is COMPLETE or explicitly BOUNDED_WITH_GAPS",
    ]
    for marker in required:
        assert marker in text


def test_knowledge_reuse_has_recall_revalidate_writeback_loop():
    text = (ROOT / "references" / "knowledge.md").read_text(encoding="utf-8")
    required = [
        "Mandatory recall-before-expansion choreography",
        "repository-native prior Financial research/artifacts",
        "Stable structural knowledge",
        "Semi-stable operating knowledge",
        "Ephemeral knowledge",
        "revalidation trigger or expiry condition",
        "prior cognition recall -> current value-chain coverage -> current evidence expansion/revalidation -> thesis selection -> reusable knowledge candidates -> future recall",
    ]
    for marker in required:
        assert marker in text


def test_prior_knowledge_cannot_waive_value_chain_coverage():
    text = (ROOT / "references" / "knowledge.md").read_text(encoding="utf-8")
    assert "Prior knowledge can accelerate the Value-Chain Coverage Map, but it can never waive it." in text
