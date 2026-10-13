from pathlib import Path

from financial_writing_agent.structure_geometry import analyze_structure_geometry


ROOT = Path(__file__).resolve().parents[1]


def test_extreme_five_by_three_geometry_requires_revise():
    text = "\n".join(
        [
            "## 一、A", "### （1）a", "### （2）b", "### （3）c",
            "## 二、B", "### （1）a", "### （2）b", "### （3）c",
            "## 三、C", "### （1）a", "### （2）b", "### （3）c",
            "## 四、D", "### （1）a", "### （2）b", "### （3）c",
            "## 五、E", "### （1）a", "### （2）b", "### （3）c",
        ]
    )
    result = analyze_structure_geometry(text)
    assert result.h2_counts == (3, 3, 3, 3, 3)
    assert result.max_same_child_count_run == 5
    assert result.mechanical_symmetry_alert is True
    assert result.requires_revise is True


def test_short_or_mixed_geometry_does_not_false_fail():
    text = "\n".join(
        [
            "## 一、A", "### （1）a", "### （2）b", "### （3）c",
            "## 二、B", "### （1）a", "### （2）b",
            "## 三、C", "### （1）a", "### （2）b", "### （3）c", "### （4）d",
            "## 四、D",
        ]
    )
    result = analyze_structure_geometry(text)
    assert result.h2_counts == (3, 2, 4, 0)
    assert result.requires_revise is False


def test_live_ice_snow_deep_exposes_the_regression_case():
    path = ROOT / "workspaces" / "articles" / "ice-snow-economy-20261013" / "publication" / "FINANCE_DEEP.md"
    result = analyze_structure_geometry(path.read_text(encoding="utf-8"))
    assert result.h2_counts == (3, 3, 3, 3, 3)
    assert result.requires_revise is True


def test_live_ice_snow_broad_remains_legal_h1_only_compression():
    path = ROOT / "workspaces" / "articles" / "ice-snow-economy-20261013" / "publication" / "FINANCE_BROAD.md"
    result = analyze_structure_geometry(path.read_text(encoding="utf-8"))
    assert result.h2_counts == (0, 0, 0, 0)
    assert result.requires_revise is False
