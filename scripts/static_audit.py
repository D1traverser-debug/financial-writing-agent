from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    require(not (ROOT / "continuity").exists(), "retired continuity namespace returned")
    for path in (
        "UAOS_SKILL.md", ".uaos/MANIFEST.json", ".uaos/ADAPTER.json",
        ".uaos/CAPABILITIES.json", "config/EXECUTION_CONTRACT.json",
        "financial_writing_agent/owner_guard.py", "financial_writing_agent/owner_lifecycle.py",
        "financial_writing_agent/workflow_spec.py", "financial_writing_agent/models.py",
    ):
        require((ROOT / path).is_file(), f"missing current Financial authority: {path}")

    manifest = load(".uaos/MANIFEST.json")
    adapter = load(".uaos/ADAPTER.json")
    caps = load(".uaos/CAPABILITIES.json")
    execution = load("config/EXECUTION_CONTRACT.json")
    require(manifest["controller"] == "D1traverser-debug/universal-agent-os@main", "controller drift")
    require(manifest["skill"]["entrypoint"] == "UAOS_SKILL.md", "skill drift")
    require(adapter["task_identity_authority"] == "UAOS", "task authority drift")
    require(adapter["legacy_controller_compatibility"] == "NONE", "legacy controller compatibility returned")
    require(execution["execution"]["route_selection"] == "NONE", "route selector returned")
    require(execution["authority"]["alternate_business_state_authority_allowed"] is False, "alternate state authority enabled")
    require(all(cap.get("side_channel_allowed") is False for cap in caps["capabilities"]), "side channel enabled")

    current_skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    discovery = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    require("continuity/" not in current_skill, "current Skill references retired namespace")
    require("Discovery Pointer" in discovery and "continuity/" not in discovery, "discovery Skill is not a clean pointer")

    reference_names = ("research.md","knowledge.md","market_explanation.md","audit.md","editorial.md","hooks.md","style.md","platforms.md","delivery.md","maintenance.md")
    for name in reference_names:
        source = (ROOT / "references" / name).read_bytes()
        skill = (ROOT / "skills/financial-writing-agent/references" / name).read_bytes()
        package = (ROOT / "financial_writing_agent/resources/references" / name).read_bytes()
        require(source == skill == package, f"reference mirror drift: {name}")

    print("PASS: Financial current authority uses UAOS + .uaos bindings; retired continuity namespace absent")


if __name__ == "__main__":
    main()
