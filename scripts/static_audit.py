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
MODELS = ROOT / "financial_writing_agent" / "models.py"
RUNTIME_SERVICE = ROOT / "financial_writing_agent" / "runtime_service.py"
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
    "submit_hook_audit",
    "submit_style_audit",
    "submit_editorial_audit",
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
    for required_owner in ("hooks", "style", "market_explanation"):
        if required_owner not in ownership:
            fail(f"current writing contract must have dedicated rule owner: {required_owner}")
    if "visuals" in ownership:
        fail("visual ownership must be removed from Financial Writing")
    for marker in ("reader_funnel", "qualified_click", "headline_information_value", "headline_curiosity_balance", "completion_payoff"):
        if marker not in ownership["hooks"]:
            fail(f"reader-funnel ownership missing: {marker}")
    if "cross_finance_title_clickability" in ownership["hooks"]:
        fail("cross-industry clickability must not return as a universal hook owner")
    for marker in (
        "fidelity_and_responsibility", "semantic_contribution", "argument_progression", "reader_calibration",
        "authorial_selectivity", "evidence_specificity", "structural_rhythm_naturalness",
        "template_redundancy_control", "uncertainty_rhetoric_calibration", "writing_dna_learning",
    ):
        if marker not in ownership["style"]:
            fail(f"authorial-prose/Writing-DNA ownership missing: {marker}")
    for marker in ("market_explanation_completeness", "causal_confidence_ladder", "hindsight_causality_control"):
        if marker not in ownership["market_explanation"]:
            fail(f"market-explanation ownership missing: {marker}")
    return len(seen)


def check_skill_bundle() -> None:
    if (ROOT / "SKILL.md").exists():
        fail("root SKILL.md is forbidden")
    if not SKILL.is_file():
        fail("packaged SKILL.md missing")
    text = SKILL.read_text(encoding="utf-8")
    required_phrases = [
        "list_recent_writing_tasks",
        "start_writing_task",
        "references/research.md",
        "references/market_explanation.md",
        "references/hooks.md",
        "references/style.md",
        "record_knowledge_writeback",
        "FINANCE_DEEP — 财经完整版本",
        "Reader Funnel / Hook Gate",
        "Natural Authorial Prose / Writing DNA Gate",
        "not a universal hard requirement",
        "VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED",
        "Publication articles do not use tables",
        "no image/cover/section-visual/avatar workflow",
        "24px = 18pt",
        "20px = 15pt",
        "18px = 13.5pt",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"packaged Skill missing required instruction: {phrase}")
    for phrase in ("submit_visual_package", "WECHAT_STICKER_POST", "references/visuals.md", "CHAT_TEXT", "writing-text://"):
        if phrase in text:
            fail(f"legacy contract leaked into packaged Skill: {phrase}")

    sets = {
        "source": {path.name for path in SOURCE_REFS.glob("*.md")},
        "skill": {path.name for path in SKILL_REFS.glob("*.md")},
        "package": {path.name for path in PACKAGE_REFS.glob("*.md")},
    }
    for required_ref in ("research.md", "market_explanation.md", "hooks.md", "style.md", "delivery.md"):
        if required_ref not in sets["source"]:
            fail(f"required reference missing: {required_ref}")
    if "visuals.md" in sets["source"] or "visuals.md" in sets["skill"] or "visuals.md" in sets["package"]:
        fail("visuals.md must remain deleted")
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

    policy = json.loads(SOURCE_POLICY.read_text(encoding="utf-8"))
    expected_sizes = {"h1_px": 24, "h1_pt": 18, "h2_px": 20, "h2_pt": 15, "body_px": 18, "body_pt": 13.5}
    for key, value in expected_sizes.items():
        if policy["word"].get(key) != value:
            fail(f"exact publication typography drift: {key}")
    if policy["style"].get("optimize_for_ai_detector") is not False:
        fail("AI-detector evasion must not be a style objective")
    dna = policy["style"].get("writing_dna_learning") or {}
    if dna.get("one_off_edit_is_candidate_only") is not True or dna.get("external_skill_rules_are_candidates_only") is not True:
        fail("Writing DNA promotion discipline is missing")
    hooks = policy.get("hooks") or {}
    if hooks.get("qualified_click_required") is not True or hooks.get("cross_finance_clickability_required") is not False:
        fail("Reader Funnel must optimize qualified reader fit, not universal cross-industry reach")
    if policy["market_explanation"].get("multi_hypothesis_required") is not True:
        fail("market explanation must remain multi-hypothesis")


def _is_tool_decorator(decorator: ast.expr) -> bool:
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    return isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "mcp" and target.attr == "tool"


def _decorator_keywords(decorator: ast.expr) -> set[str]:
    if not _is_tool_decorator(decorator) or not isinstance(decorator, ast.Call):
        return set()
    return {kw.arg for kw in decorator.keywords if kw.arg}


def _tool_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(_is_tool_decorator(d) for d in node.decorator_list):
            names.add(node.name)
    return names


def check_public_mcp_contract() -> int:
    for required in (PUBLIC_MCP, MCP_CONTRACTS, MODELS, RUNTIME_SERVICE):
        if not required.is_file():
            fail(f"required MCP/runtime file missing: {required.relative_to(ROOT)}")
    if (ROOT / "financial_writing_agent" / "mcp_server.py").exists():
        fail("obsolete mcp_server.py compatibility shim must remain deleted")

    source = PUBLIC_MCP.read_text(encoding="utf-8")
    contracts = MCP_CONTRACTS.read_text(encoding="utf-8")
    models = MODELS.read_text(encoding="utf-8")
    runtime = RUNTIME_SERVICE.read_text(encoding="utf-8")

    for marker in ("ToolAnnotations", "READ_ONLY_TOOL", "STATE_WRITE_TOOL", "WritingTaskSummary", "WritingTaskList", "ArtifactSummary"):
        if marker not in contracts:
            fail(f"shared MCP contract metadata missing: {marker}")
    for marker in ("READ_ONLY_TOOL", "STATE_WRITE_TOOL", "WritingTaskSummary", "WritingTaskList"):
        if marker not in source:
            fail(f"public MCP surface does not use shared contract owner: {marker}")

    tree = ast.parse(source)
    tool_nodes: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decorators = [d for d in node.decorator_list if _is_tool_decorator(d)]
        if not decorators:
            continue
        if len(decorators) != 1:
            fail(f"public MCP function has duplicate tool decorators: {node.name}")
        keywords = _decorator_keywords(decorators[0])
        tool_nodes[node.name] = node
        doc = ast.get_docstring(node) or ""
        if len(doc.strip()) < 60:
            fail(f"public MCP tool description too short/missing: {node.name}")
        required_keywords = {"title", "annotations", "structured_output"}
        if not required_keywords.issubset(keywords):
            fail(f"public MCP tool missing decorator metadata: {node.name}")
        if node.returns is None:
            fail(f"public MCP tool missing return type: {node.name}")
        rendered_return = ast.unparse(node.returns)
        if "Any" in rendered_return or rendered_return.startswith("dict["):
            fail(f"public MCP tool has weak output type: {node.name} -> {rendered_return}")

    names = set(tool_nodes)
    if names != EXPECTED_TOOLS:
        fail(f"public MCP tool inventory mismatch: missing={sorted(EXPECTED_TOOLS - names)}, extra={sorted(names - EXPECTED_TOOLS)}")
    if _tool_names(RUNTIME_SERVICE):
        fail("runtime_service.py must not register MCP tools")
    if "MCPServer(" in runtime:
        fail("runtime_service.py must not instantiate a second MCP server")

    forbidden = ("submit_visual_package", "WECHAT_STICKER_POST", "writing-json://", "writing-text://", "CHAT_TEXT")
    for marker in forbidden:
        if marker in source or marker in contracts or marker in models:
            fail(f"legacy MCP/model contract leaked back into current runtime: {marker}")
    if "writing-docx://{task_id}/{kind}" not in source:
        fail("Word artifact resource template missing")
    if "ResourceLink" not in source or "structured_content=summary.model_dump" not in source:
        fail("artifact-returning tools must expose structured output plus ResourceLink")
    if "path: str" in contracts or "trace_tail" in contracts:
        fail("public result contract must not expose server-local paths or trace logs")
    return len(names)


def check_schema_strictness() -> None:
    text = SCHEMAS.read_text(encoding="utf-8")
    if 'ConfigDict(extra="forbid", str_strip_whitespace=True)' not in text:
        fail("stage schemas must fail closed on unknown fields")
    for model in (
        "ResearchPackage", "MarketExplanationHypothesis", "MarketExplanationMap", "EditorialPlan",
        "HeadlinePackage", "ArticlePayload", "DraftPackage", "HookAuditDecision", "StyleAuditDecision", "GateDecision",
    ):
        if f"class {model}(StrictModel)" not in text:
            fail(f"stage schema must inherit StrictModel: {model}")
    for marker in (
        "MATERIAL_COMPLETE plan requires completeness_obligations",
        "stock/theme research with a company universe requires market_explanation",
        "non-UNRESOLVED market explanation requires evidence_refs",
        "skim_path_anchor must appear as an exact explicit bold span",
        "target_reader_click_reason", "promised_payoff", "broader_finance_relevance",
        "audience_promise_fit", "headline_information_value", "headline_curiosity_balance", "completion_payoff",
        "fidelity_and_responsibility", "semantic_contribution", "argument_progression", "reader_calibration",
        "authorial_selectivity", "evidence_specificity", "structural_rhythm_naturalness",
        "template_redundancy_control", "uncertainty_rhetoric_calibration",
    ):
        if marker not in text:
            fail(f"current schema guard missing: {marker}")
    for removed_field in ("cross_finance_click_reason", "template_fingerprint", "discourse_variability", "semantic_progression", "reader_modeling", "narrative_flow"):
        if removed_field in text:
            fail(f"superseded reader/style schema field remains active: {removed_field}")
    for removed in ("VisualPackage", "PlatformConstraintSnapshot", "StickerPostPayload", "OpenAIFileRef"):
        if f"class {removed}(" in text:
            fail(f"removed schema still active: {removed}")


def check_activation_inventory() -> None:
    payload = json.loads((ROOT / "evals" / "activation_cases.json").read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    if len(cases) < 8 or not any(c.get("should_activate") is True for c in cases) or not any(c.get("should_activate") is False for c in cases):
        fail("activation inventory must include enough positive and negative cases")


def check_deployment_boundary() -> None:
    if not SITE_SPEC.is_file():
        fail("ChatGPT Site deployment specification missing")
    text = SITE_SPEC.read_text(encoding="utf-8")
    for marker in ("personal/private deployment only", "Do not enable public sharing", "Do not silently fall back to ephemeral container/local disk"):
        if marker not in text:
            fail(f"deployment safety boundary missing: {marker}")
    for legacy in ("16-tool", "submit_visual_package", "WECHAT_STICKER_POST", "writing-text://", "mcp_server.py"):
        if legacy in text:
            fail(f"legacy Site contract remains in deployment spec: {legacy}")


def check_packaging_contract() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    base = pyproject.split("[project.optional-dependencies]", 1)[0]
    if '"mcp>=2.0,<3"' not in base:
        fail("MCP must be a base dependency")
    if 'financial-writing-mcp = "financial_writing_agent.plugin_server:main"' not in pyproject:
        fail("financial-writing-mcp must point at plugin_server")
    if 'resources/references/*.md' not in pyproject or 'resources/policy.json' not in pyproject:
        fail("wheel package-data declarations missing")
    if "--with-visuals" in (ROOT / "financial_writing_agent" / "cli.py").read_text(encoding="utf-8"):
        fail("visual CLI option must remain removed")


def check_dead_contracts_removed() -> None:
    for path in (
        ROOT / "financial_writing_agent" / "contracts.py",
        ROOT / "financial_writing_agent" / "mcp_server.py",
        ROOT / "continuity" / "tasks" / "ai-pharma-writing" / "HANDOFF.md",
        ROOT / "continuity" / "tasks" / "site-runtime-gate-a2" / "HANDOFF.md",
    ):
        if path.exists():
            fail(f"obsolete compatibility/history file must remain deleted: {path.relative_to(ROOT)}")


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
        f"PASS: {groups} unique rule ownership keys; reference mirrors aligned; "
        f"one {tools}-tool Word-only MCP surface; no legacy shim/text/visual contract; "
        "Reader Funnel + 9-part Natural Authorial Prose/Writing DNA + market-explanation + exact typography contracts present"
    )


if __name__ == "__main__":
    main()
