from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "financial-writing-agent" / "SKILL.md"


def test_skill_requires_runtime_capability_handshake_before_new_task():
    text = SKILL.read_text(encoding="utf-8")
    required = [
        "capability/schema handshake",
        "Tool presence alone does not make a Runtime authoritative",
        "DUAL is deep-first, not parallel",
        "BROAD_DERIVATION",
        "present but contract-incompatible",
        "Do not import stale Runtime PASS receipts into standalone",
        "Runtime/Skill capability drift is a `SYSTEM_ERROR`",
    ]
    for phrase in required:
        assert phrase in text, phrase


def test_skill_cold_start_exposes_narrative_finance_quality_contract():
    text = SKILL.read_text(encoding="utf-8")
    required = [
        "NARRATIVE_FINANCE_EXPLAINER",
        "non-permutability check",
        "tic-density check",
        "Source invisibility",
        "6,000–9,000 Chinese characters as a diagnostic range",
        "below roughly 5,500 characters",
    ]
    for phrase in required:
        assert phrase in text, phrase
