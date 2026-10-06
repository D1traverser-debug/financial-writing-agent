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
PUBLIC_MCP = ROOT / "financial_writing_agent" / "plugin_server.py"

EXPECTED_TOOLS = {
    "start_writing_task",
    "get_writing_task",
    "list_recent_writing_tasks",
    "record_knowledge_context",
    "submit_research",
    "submit_research_audit",
    "submit_editorial_plan",
    "submit_headlines",
    "submit_draft",
    "submit_style_audit",
    "submit_editorial_audit",
    "submit_visual_package",
    "build_and_mechanically_audit_delivery",
    "record_knowledge_writeback",
    "submit_final_audit",
}


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
        "The MCP runtime checkpoint is the executable task authority",
        "WECHAT_STICKER_POST",
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


def _decorator_keywords(decorator: ast.expr) -> set[str]:
    if not isinstance(decorator, ast.Call):
        return set()
    target = decorator.func
    if not (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "mcp" and target.attr == "tool"):
        return set()
    return {kw.arg for kw in decorator.keywords if kw.arg}


def check_public_mcp_contract() -> int:
    if not PUBLIC_MCP.is_file():
        fail("typed public MCP surface missing: financial_writing_agent/plugin_server.py")
    source = PUBLIC_MCP.read_text(encoding="utf-8")
    tree = ast.parse(source)
    tool_nodes: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            keywords = _decorator_keywords(decorator)
            if not keywords:
                continue
            tool_nodes[node.name] = node
            doc = ast.get_docstring(node) or ""
            if len(doc.strip()) < 60:
                fail(f"public MCP tool description too short/missing: {node.name}")
            required_keywords = {"title", "annotations", "structured_output"}
            if not required_keywords.issubset(keywords):
                fail(f"public MCP tool missing decorator metadata {required_keywords - keywords}: {node.name}")
            if node.returns is None:
                fail(f"public MCP tool missing return type/output schema: {node.name}")
            rendered_return = ast.unparse(node.returns)
            if "Any" in rendered_return or rendered_return.startswith("dict["):
                fail(f"public MCP tool has weak/indeterminate output type: {node.name} -> {rendered_return}")

    names = set(tool_nodes)
    if names != EXPECTED_TOOLS:
        fail(f"public MCP tool inventory mismatch: missing={sorted(EXPECTED_TOOLS - names)}, extra={sorted(names - EXPECTED_TOOLS)}")
    if 'meta={"openai/fileParams": ["files"]}' not in source:
        fail("submit_visual_package must declare ChatGPT fileParams")
    if "ToolAnnotations" not in source:
        fail("public MCP tools must use explicit ToolAnnotations")
    return len(names)


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
    base = pyproject.split("[project.optional-dependencies]", 1)[0]
    if '"mcp>=2.0,<3"' not in base:
        fail("MCP must be a base dependency because financial-writing-mcp is a core entry point")
    if 'financial-writing-mcp = "financial_writing_agent.plugin_server:main"' not in pyproject:
        fail("financial-writing-mcp must point at typed public plugin_server")
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
    tools = check_public_mcp_contract()
    check_activation_inventory()
    check_packaging_contract()
    check_dead_contracts_removed()
    print(
        f"PASS: {groups} unique rule ownership keys; Skill/source/package references aligned; "
        f"packaged policy aligned; {tools} typed/annotated public MCP tools; activation and packaging contracts present"
    )


if __name__ == "__main__":
    main()
