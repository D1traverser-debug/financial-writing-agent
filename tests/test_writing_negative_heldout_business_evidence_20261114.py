"""Live historical article-text regression; no LLM-judged editorial certification.

Keep one real owner-rejected multi-company draft and a cross-topic held-out
historical baseline. These tests prove known structural warning signals are
executable and do not simply reject all long-form writing.
"""
from pathlib import Path

from financial_writing_agent.checks import analyze_template_scaffolding
from financial_writing_agent.structure_geometry import analyze_structure_geometry

ROOT = Path(__file__).resolve().parents[1] / "evals" / "artifacts"
WIND = "offshore-wind-2026-10-10-rejected-deep-v071.md"
RUTILE = "rutile-2026-10-06-heldout-baseline.md"


def _publication(name: str) -> str:
    raw = (ROOT / name).read_text(encoding="utf-8")
    # Metadata is provenance, not text to be scored as user-facing prose.
    text = raw.split("\n\n", 2)
    assert len(text) == 3
    marker = "> This snapshot" if name == WIND else "> This is"
    start = raw.index(marker)
    boundary = raw.index("\n\n", start)
    result = raw[boundary:].strip()
    assert len(result) > 2000
    return result


def test_real_rejected_wind_draft_trips_existing_repetitive_section_geometry():
    content = _publication(WIND)
    result = analyze_structure_geometry(content)
    assert result.h1_count == 8
    assert result.h2_counts[:4] == (3, 3, 3, 3)
    assert result.max_same_child_count_run >= 4
    assert result.requires_revise is True

    # Reader rejected meta-organizing prose and repetitive company summaries.
    # This is a mechanistic signal, not proof of the entire literary complaint.
    result = analyze_template_scaffolding(content)
    assert result["requires_revise"] is True
    assert result["counts"]["not_x_but_y"] >= 3


def test_different_topic_does_not_trigger_universal_template_rejection():
    content = _publication(RUTILE)
    result = analyze_structure_geometry(content)
    assert result.h1_count == 8
    assert result.h2_counts == (0, 0, 0, 0, 0, 0, 0, 0)
    assert result.requires_revise is False
    result = analyze_template_scaffolding(content)
    assert result["requires_revise"] is False
