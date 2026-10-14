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

    require(not (ROOT / "financial_writing_agent/uaos_binding.py").exists(), "parent identity validator leaked into Financial business package")
    require(not (ROOT / "tests/test_uaos_article_binding.py").exists(), "retired parent/child ID-equality regression test remains")

    manifest = load(".uaos/MANIFEST.json")
    adapter = load(".uaos/ADAPTER.json")
    caps = load(".uaos/CAPABILITIES.json")
    execution = load("config/EXECUTION_CONTRACT.json")
    require(manifest["controller"] == "D1traverser-debug/universal-agent-os@main", "controller drift")
    require(manifest["skill"]["entrypoint"] == "UAOS_SKILL.md", "skill drift")
    require(adapter["controller_task_identity_authority"] == "UAOS", "controller identity authority drift")
    require("financial_writing_agent.models.TaskContract.task_id" in adapter["domain_task_identity_authority"], "Financial task identity authority drift")
    require("NO_EQUALITY_REQUIREMENT" in adapter["identity_boundary"], "parent/domain identity namespaces collapsed")
    require(adapter["legacy_controller_compatibility"] == "NONE", "legacy controller compatibility returned")
    require(manifest["domain_authority"]["task_contract"] == "financial_writing_agent/models.py:TaskContract", "domain task contract drift")
    require(execution["execution"]["route_selection"] == "NONE", "route selector returned")
    require(execution["authority"]["alternate_business_state_authority_allowed"] is False, "alternate state authority enabled")
    require(execution["identity"]["task_id_owner"] == "FINANCIAL_WRITING", "Financial identity ownership drift")
    require(execution["identity"]["parent_child_id_equality_required"] is False, "parent/child task ID equality returned")
    require(bool(caps.get("required_uaos_common_capabilities")), "required UAOS common capabilities are undeclared")
    require(all(cap.get("side_channel_allowed") is False for cap in caps["capabilities"]), "side channel enabled")

    current_skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    discovery = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    require("continuity/" not in current_skill, "current Skill references retired namespace")
    require("no equality requirement" in current_skill.lower(), "current Skill does not state the identity boundary")
    require("Discovery Pointer" in discovery and "continuity/" not in discovery, "discovery Skill is not a clean pointer")

    business_package_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "financial_writing_agent").glob("*.py")
    )
    require("UAOS_ARTICLE_TASK_ID" not in business_package_text, "parent identity semantics leaked into Financial package")
    require("validate_uaos_article_binding" not in business_package_text, "UAOS binding validator leaked into Financial package")

    reference_names = ("research.md","knowledge.md","market_explanation.md","audit.md","editorial.md","hooks.md","style.md","platforms.md","delivery.md","maintenance.md")
    for name in reference_names:
        source = (ROOT / "references" / name).read_bytes()
        skill = (ROOT / "skills/financial-writing-agent/references" / name).read_bytes()
        package = (ROOT / "financial_writing_agent/resources/references" / name).read_bytes()
        require(source == skill == package, f"reference mirror drift: {name}")

    print("PASS: Financial business package is domain-owned; UAOS remains adapter metadata only")


if __name__ == "__main__":
    main()
