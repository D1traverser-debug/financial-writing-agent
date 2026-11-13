"""Financial's current system authority does not point back to the retired parent."""
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_single_current_financial_evolution_ref_is_standalone_and_local():
    idx = _json("evals/EVOLUTION_INDEX.json")["active_system_assessment"]
    m = _json("config/FINANCIAL_MANIFEST.json")
    assert idx["current_method_owner"] == m["controller"] == "FINANCIAL_WRITING_OWNER"
    assert idx["current_runtime_authority"] == "config/FINANCIAL_MANIFEST.json"
    assert idx["review_ref"] == "evals/FINANCIAL_STANDALONE_REBUILD_AUDIT_20261111.md"
    assert idx["current_operating_skill"] == m["skill_entrypoint"]
    assert "parent_governance_ref" not in idx
    assert idx["standalone_reconstruction"]["active_parent_dependency"] is False
    assert idx["standalone_reconstruction"]["production_merge_verified"] is True
    assert idx["standalone_reconstruction"]["editorial_acceptance"] == "NOT_READY"


def test_product_version_tracks_independent_package_not_prior_child_era():
    package = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = (ROOT / "docs/product_requirements.md").read_text(encoding="utf-8")
    assert package["project"]["version"] == "1.1.0"
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    assert manifest["skill_entrypoint"] == "skills/financial-writing-agent/SKILL.md"
    assert manifest["data_authority"] == "config/DATA_AUTHORITY.json"
    assert "1.1.0_STANDALONE_FINANCIAL" in requirements
    assert "no external parent" in requirements.lower()
