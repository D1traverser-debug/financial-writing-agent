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
MCP_CONTRACTS = ROOT / "financial_writing_agent" / "mcp_contracts.py"
RUNTIME_SERVICE = ROOT / "financial_writing_agent" / "runtime_service.py"
LEGACY_MCP_SHIM = ROOT / "financial_writing_agent" / "mcp_server.py"
SCHEMAS = ROOT / "financial_writing_agent" / "schemas.py"
SITE_SPEC = ROOT / "deploy" / "chatgpt-site" / "SITE_SPEC.md"

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


def _is_tool_decorator(decorator: ast.expr) -> bool:
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    return (
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == "mcp"
        and target.attr == "tool"
    )


def _decorator_keywords(decorator: ast.expr) -> set[str]:
    if not _is_tool_decorator(decorator) or not isinstance(decorator, ast.Call):
        return set()
    return {kw.arg for kw in decorator.keywords if kw.arg}


def _tool_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(_is_tool_decorator(decorator) for decorator in node.decorator_list):
            names.add(node.name)
    return names


def check_public_mcp_contract() -> int:
    for required in (PUBLIC_MCP, MCP_CONTRACTS, RUNTIME_SERVICE, LEGACY_MCP_SHIM):
        if not required.is_file():
            fail(f"required MCP/runtime file missing: {required.relative_to(ROOT)}")

    source = PUBLIC_MCP.read_text(encoding="utf-8")
    contracts = MCP_CONTRACTS.read_text(encoding="utf-8")
    runtime = RUNTIME_SERVICE.read_text(encoding="utf-8")
    legacy = LEGACY_MCP_SHIM.read_text(encoding="utf-8")

    for marker in ("ToolAnnotations", "READ_ONLY_TOOL", "STATE_WRITE_TOOL", "FILE_INGEST_TOOL", "WritingTaskSummary", "WritingTaskList", "ArtifactSummary"):
        if marker not in contracts:
            fail(f"shared MCP contract metadata missing: {marker}")
    for marker in ("READ_ONLY_TOOL", "STATE_WRITE_TOOL", "FILE_INGEST_TOOL", "WritingTaskSummary", "WritingTaskList"):
        if marker not in source:
            fail(f"public MCP surface does not use shared contract owner: {marker}")

    tree = ast.parse(source)
    tool_nodes: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        tool_decorators = [decorator for decorator in node.decorator_list if _is_tool_decorator(decorator)]
        if not tool_decorators:
            continue
        if len(tool_decorators) != 1:
            fail(f"public MCP function has duplicate tool decorators: {node.name}")
        decorator = tool_decorators[0]
        keywords = _decorator_keywords(decorator)
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
    if _tool_names(RUNTIME_SERVICE):
        fail("runtime_service.py must not register MCP tools")
    if _tool_names(LEGACY_MCP_SHIM):
        fail("mcp_server.py compatibility shim must not register MCP tools")
    if "MCPServer(" in runtime:
        fail("runtime_service.py must not instantiate a second MCP server")
    if "from .plugin_server import main, mcp" not in legacy:
        fail("legacy mcp_server.py must be a thin compatibility shim")

    if 'meta={"openai/fileParams": ["files"]}' not in source:
        fail("submit_visual_package must declare ChatGPT fileParams")
    for uri in ("writing-docx://{task_id}/{kind}", "writing-json://{task_id}/{kind}", "writing-text://{task_id}/{kind}"):
        if uri not in source:
            fail(f"artifact resource template missing: {uri}")
    if "ResourceLink" not in source or "structured_content=summary.model_dump" not in source:
        fail("artifact-returning tools must expose both structured output and MCP ResourceLink content")
    if "path: str" in contracts or "trace_tail" in contracts:
        fail("public result contract must not expose server-local paths or internal trace logs")
    return len(names)


def check_schema_strictness() -> None:
    text = SCHEMAS.read_text(encoding="utf-8")
    if 'ConfigDict(extra="forbid", str_strip_whitespace=True)' not in text:
        fail("stage schemas must fail closed on unknown fields and whitespace-only strings")
    for model in ("ResearchPackage", "EditorialPlan", "HeadlinePackage", "ArticlePayload", "DraftPackage", "VisualPackage", "StyleAuditDecision", "GateDecision"):
        if f"class {model}(StrictModel)" not in text:
            fail(f"stage schema must inherit StrictModel: {model}")
    for marker in ("candidate structure names must be unique", "candidates must contain unique titles", "platform constraint snapshot is stale", "validate_public_https_url"):
        if marker not in text:
            fail(f"schema ambiguity/freshness/safety guard missing: {marker}")


def check_activation_inventory() -> None:
    payload = json.loads((ROOT / "evals" / "activation_cases.json").read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    if len(cases) < 8:
        fail("activation inventory is too small")
    if not any(case.get("should_activate") is True for case in cases):
        fail("activation inventory has no positive cases")
    if not any(case.get("should_activate") is False for case in cases):
        fail("activation inventory has no negative cases")


def check_deployment_boundary() -> None:
    if not SITE_SPEC.is_file():
        fail("ChatGPT Site deployment specification missing")
    text = SITE_SPEC.read_text(encoding="utf-8")
    for marker in (
        "personal/private deployment only",
        "Do not enable public sharing",
        "Do not silently fall back to ephemeral container/local disk",
        "public/multi-user sharing remains disabled for v0.2",
    ):
        if marker not in text:
            fail(f"deployment safety boundary missing: {marker}")


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
    check_schema_strictness()
    check_activation_inventory()
    check_deployment_boundary()
    check_packaging_contract()
    check_dead_contracts_removed()
    print(
        f"PASS: {groups} unique rule ownership keys; Skill/source/package references aligned; "
        f"one {tools}-tool typed/annotated MCP surface; strict schemas; artifact resources; "
        "activation, deployment-safety and packaging contracts present"
    )


if __name__ == "__main__":
    main()
