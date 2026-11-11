"""Run against CAOS's real imported domain_contract._native_contract, not a copy.

The CI job must clone the public CAOS parent at the exact pinned source commit
and put its src/ directory on PYTHONPATH. This checks a genuine parent
implementation against child bytes without changing the parent or deploying.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re

from cognition_agent_os.domain_contract import FILES, _native_contract

ROOT = Path(__file__).resolve().parents[1]
PARENT = "D1traverser-debug/cognition-agent-os@main"


def main() -> None:
    manifest = json.loads((ROOT / FILES[0]).read_text(encoding="utf-8"))
    assert manifest["controller"] == PARENT
    entrypoint = manifest["skill"]["entrypoint"]
    files = {path: (ROOT / path).read_bytes() for path in (*FILES, entrypoint)}
    sha = os.environ.get("GITHUB_SHA", "a" * 40)
    if not re.fullmatch(r"[a-f0-9]{40}", sha):
        sha = "a" * 40
    observation = _native_contract(
        files,
        {
            "kind": "domain_contract",
            "repo": "D1traverser-debug/financial-writing-agent",
            "ref": sha,
            "domain_id": "financial_writing",
        },
    )
    assert observation["kind"] == "CHILD_CONTRACT_OBSERVATION_V1"
    assert observation["declared_controller"] == PARENT
    assert observation["declared_skill_entrypoint"] == "CAOS_SKILL.md"
    assert observation["read_only_source_identity_verified"] is True
    assert observation["legacy_parent_binding_refs"] == []
    assert observation["legacy_parent_bound"] is False
    assert observation["child_business_identity_reissued"] is False
    assert observation["child_business_state_modified"] is False
    assert observation["child_business_result_verified"] is False
    assert observation["parent_replacement_admitted"] is False
    assert observation["requires_child_native_admission_for_effect"] is True
    assert "financial_owner_workflow" in observation["advertised_capability_ids"]
    assert "high_judgment_generation_stages" in observation["advertised_capability_ids"]
    assert all(path in observation["source_sha256"] for path in files)
    print("PASS: real pinned CAOS native domain_contract independently accepts Financial "
          "child contract and detects no residual legacy-parent binding; execution "
          "grants and business outcome remain child-native and unclaimed.")


if __name__ == "__main__":
    main()
