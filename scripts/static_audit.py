from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "financial-writing-agent" / "SKILL.md"
SKILL_REFS = ROOT / "skills" / "financial-writing-agent" / "references"
RUNTIME_REFS = ROOT / "references"


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
    expected_refs = {path.name for path in RUNTIME_REFS.glob("*.md")}
    skill_refs = {path.name for path in SKILL_REFS.glob("*.md")}
    if expected_refs != skill_refs:
        fail(f"skill/runtime reference set mismatch: runtime={sorted(expected_refs)} skill={sorted(skill_refs)}")
    for name in sorted(expected_refs):
        if (RUNTIME_REFS / name).read_bytes() != (SKILL_REFS / name).read_bytes():
            fail(f"skill/runtime reference drift: {name}")


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


def check_dead_contracts_removed() -> None:
    if (ROOT / "financial_writing_agent" / "contracts.py").exists():
        fail("legacy duplicate contracts.py must remain removed")


def main() -> None:
    groups = check_rule_ownership()
    check_skill_bundle()
    tools = check_mcp_tool_descriptions()
    check_activation_inventory()
    check_dead_contracts_removed()
    print(f"PASS: {groups} unique rule ownership keys; skill bundle/reference mirrors aligned; {tools} MCP tools described; activation inventory present")


if __name__ == "__main__":
    main()
