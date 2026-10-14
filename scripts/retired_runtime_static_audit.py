from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUARANTINE = ROOT / "config/retired_runtime_paths.json"


def main() -> None:
    payload = json.loads(QUARANTINE.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "2.0":
        raise SystemExit("retired runtime quarantine schema drift")
    paths = payload.get("retired_current_tree_paths", [])
    if not isinstance(paths, list) or not paths or len(paths) != len(set(paths)):
        raise SystemExit("retired runtime quarantine path list invalid")
    offenders = [path for path in paths if (ROOT / path).exists()]
    if offenders:
        raise SystemExit(f"retired Financial controller/runtime paths returned: {offenders}")
    required = [
        ".uaos/MANIFEST.json", ".uaos/ADAPTER.json", ".uaos/CAPABILITIES.json",
        "config/EXECUTION_CONTRACT.json", "UAOS_SKILL.md",
        "financial_writing_agent/owner_guard.py", "financial_writing_agent/owner_lifecycle.py",
        "financial_writing_agent/workflow_spec.py", "financial_writing_agent/models.py",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(f"current Financial components missing: {missing}")
    print(f"PASS: {len(paths)} retired controller/runtime paths absent; current owner components present")


if __name__ == "__main__":
    main()
