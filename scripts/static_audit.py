from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "financial-writing-agent" / "SKILL.md"
SKILL_REFS = ROOT / "skills" / "financial-writing-agent" / "references"
SOURCE_REFS = ROOT / "references"
PACKAGE_REFS = ROOT / "financial_writing_agent" / "resources" / "references"
SOURCE_POLICY = ROOT / "config" / "policy.json"
PACKAGE_POLICY = ROOT / "financial_writing_agent" / "resources" / "policy.json"


def fail(message: str) -> None:
    raise SystemExit(message)


def check_rule_ownership() -> int:
    ownership = json.loads((ROOT / "config" / "rule_ownership.json").read_text(encoding="utf-8"))
    seen: dict[str, str] = {}
    for owner, keys in ownership.items():
        for key in keys:
            if key in seen:
                fail(f"duplicate rule owner: {key}: {seen[key]} and {owner}")
            seen[key] = owner
    return len(seen)


def check_skill_bundle() -> None:
    if (ROOT / "SKILL.md").exists():
        fail("root SKILL.md is forbidden: packaged skill is the single discoverable Skill authority")
    if not SKILL.is_file():
        fail("packaged SKILL.md missing")
    text = SKILL.read_text(encoding="utf-8")
    required_phrases = [
        "list_recent_writing_tasks",
        "start_writing_task",
        "Do not use for standalone stock-picking/recommendation",
        "references/research.md",
        "references/visuals.md",
        "record_knowledge_writeback",
        "submit_visual_package",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"packaged Skill missing required boundary/instruction: {phrase}")

    sets = {
        "source": {path.name for path in SOURCE_REFS.glob("*.md")},
        "skill": {path.name for path in SKILL_REFS.glob("*.md")},
        "package": {path.name for path in PACKAGE_REFS.glob("*.md")},
    }
    if not sets["source"] or sets["source"] != sets["skill"] or sets["source"] != sets["package"]:
        fail(f"reference-set mismatch: { {k: sorted(v) for k, v in sets.items()} }")
    for name in sorted(sets["source"]):
        source = (SOURCE_REFS / name).read_bytes()
        if source != (SKILL_REFS / name).read_bytes():
            fail(f"skill/source reference drift: {name}")
        if source != (PACKAGE_REFS / name).read_bytes():
            fail(f"package/source reference drift: {name}")
    if SOURCE_POLICY.read_bytes() != PACKAGE_POLICY.read_bytes():
        fail("packaged policy drift from config/policy.json")


def check_mcp_tool_descriptions() -> int:
    path = ROOT / "financial_writing_agent" / "mcp_server.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tool_names: list[str] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        is_tool = False
        for decorator in node.decorator_list:
            target = decorator.func if isinstance(decorator, ast.Call) else decorator
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "mcp" and target.attr == "tool":
                is_tool = True
        if not is_tool:
            continue
        tool_names.append(node.name)
        doc = ast.get_docstring(node) or ""
        if len(doc.strip()) < 60:
            fail(f"MCP tool description too short/missing: {node.name}")
    if len(tool_names) < 15:
        fail(f"unexpected MCP tool count: {len(tool_names)}")
    source = path.read_text(encoding="utf-8")
    if 'meta={"openai/fileParams": ["files"]}' not in source:
        fail("submit_visual_package must declare ChatGPT fileParams")
    return len(tool_names)


def check_activation_inventory() -> None:
    payload = json.loads((ROOT / "evals" / "activation_cases.json").read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    if len(cases) < 8:
        fail("activation inventory is too small")
    if not any(case.get("should_activate") is True for case in cases):
        fail("activation inventory has no positive cases")
    if not any(case.get("should_activate") is False for case in cases):
        fail("activation inventory has no negative cases")


def check_packaging_contract() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    if '"mcp>=2.0,<3"' not in pyproject.split("[project.optional-dependencies]", 1)[0]:
        fail("MCP must be a base dependency because financial-writing-mcp is a core entry point")
    if 'resources/references/*.md' not in pyproject or 'resources/policy.json' not in pyproject:
        fail("wheel package-data declarations for runtime resources are missing")
    openai_adapter = (ROOT / "financial_writing_agent" / "adapters" / "openai_agents.py").read_text(encoding="utf-8")
    if "gpt-6.1-sol" in openai_adapter:
        fail("local adapter must not hard-code an unverified model default")
    cli = (ROOT / "financial_writing_agent" / "cli.py").read_text(encoding="utf-8")
    if "--with-visuals" in cli:
        fail("legacy CLI --with-visuals default inversion must remain removed")


def check_dead_contracts_removed() -> None:
    if (ROOT / "financial_writing_agent" / "contracts.py").exists():
        fail("legacy duplicate contracts.py must remain removed")


def main() -> None:
    groups = check_rule_ownership()
    check_skill_bundle()
    tools = check_mcp_tool_descriptions()
    check_activation_inventory()
    check_packaging_contract()
    check_dead_contracts_removed()
    print(
        f"PASS: {groups} unique rule ownership keys; Skill/source/package references aligned; "
        f"packaged policy aligned; {tools} MCP tools described; activation and packaging contracts present"
    )


if __name__ == "__main__":
    main()
