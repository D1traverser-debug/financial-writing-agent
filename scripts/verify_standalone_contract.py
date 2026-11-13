"""Direct Financial independence gate; deliberately imports no external parent code."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    manifest = json.loads((ROOT / "config/FINANCIAL_MANIFEST.json").read_text(encoding="utf-8"))
    capabilities = json.loads((ROOT / "config/FINANCIAL_CAPABILITIES.json").read_text(encoding="utf-8"))
    contract = json.loads((ROOT / "config/EXECUTION_CONTRACT.json").read_text(encoding="utf-8"))
    assert manifest["controller"] == capabilities["owner"] == contract["authority"]["controller"] == "FINANCIAL_WRITING_OWNER"
    assert manifest["external_parent_required"] is False
    assert manifest["external_host_required"] is False
    assert manifest["direct_activation"] is True
    assert capabilities["independent_parent_free"] is True
    assert contract["execution"]["route_selection"] == "DIRECT_FINANCIAL_ONLY"
    assert manifest["skill_entrypoint"] == "skills/financial-writing-agent/SKILL.md"
    assert (ROOT / manifest["skill_entrypoint"]).is_file()
    from financial_writing_agent import standalone_runtime
    from financial_writing_agent import current_admission
    from financial_writing_agent.writing_kernel import validate_kernel

    assert standalone_runtime.DOMAIN_ID == "financial_writing"
    assert callable(standalone_runtime.admit_article_action)
    assert callable(standalone_runtime.observe_article)
    assert callable(current_admission.build_initial_state)
    assert not validate_kernel()
    assert not any(
        name.startswith("cognition_agent_os") or name.startswith("universal_agent_os")
        for name in sys.modules
    ), "standalone boot imported a former parent runtime"
    from financial_writing_agent.models import TaskContract
    assert len(TaskContract(prompt="isolated Financial").required_outputs) == 4
    print("PASS: direct Financial imports, native owner state, Skill, core writer and "
          "standalone capability contracts initialize without any external parent runtime")


if __name__ == "__main__":
    main()
