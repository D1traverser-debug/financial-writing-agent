import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUARANTINE = ROOT / "config" / "retired_runtime_paths.json"


def _retired_paths() -> list[str]:
    payload = json.loads(QUARANTINE.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    paths = payload["retired_current_tree_paths"]
    assert len(paths) == len(set(paths))
    return paths


def test_retired_second_runtime_cannot_reenter_current_tree():
    offenders = [path for path in _retired_paths() if (ROOT / path).exists()]
    assert offenders == [], f"retired Financial runtime files returned to current tree: {offenders}"


def test_current_owner_components_exist():
    required = (
        "continuity/FINANCIAL_OWNER_EXECUTION.json",
        "financial_writing_agent/owner_guard.py",
        "financial_writing_agent/owner_lifecycle.py",
        "financial_writing_agent/workflow_spec.py",
        "financial_writing_agent/models.py",
    )
    missing = [path for path in required if not (ROOT / path).is_file()]
    assert missing == [], f"current Financial owner components missing: {missing}"
