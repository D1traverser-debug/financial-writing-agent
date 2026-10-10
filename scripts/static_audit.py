from __future__ import annotations

import ast
import json
import re
import tomllib
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
OPENAI_ADAPTER = ROOT / "financial_writing_agent" / "adapters" / "openai_agents.py"
SITE_SPEC = ROOT / "deploy" / "chatgpt-site" / "SITE_SPEC.md"
README = ROOT / "README.md"
ARCHITECTURE = ROOT / "docs" / "architecture.md"
PLUGIN_JSON = ROOT / "plugin.json"
PYPROJECT = ROOT / "pyproject.toml"
CAPABILITIES = ROOT / "continuity" / "EXECUTION_CAPABILITIES.json"

CURRENT_VERSION = "0.6.0"
CURRENT_LABEL = "v0.6"

EXPECTED_TOOLS = {
    "start_writing_task",
    "get_writing_task",
    "list_recent_writing_tasks",
    "resume_blocked_task",
    "record_writing_learning_sample",
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

    required = {
        "runtime": {"blocked_recovery", "downstream_invalidation"},
        "market_explanation": {"explicit_scope_activation", "stock_universe_not_activation"},
        "editorial": {"topic_specific_structures", "macro_structural_coherence"},
        "hooks": {"reader_funnel", "continuation_value"},
        "style": {"natural_authorial_prose", "raw_learning_sample_ledger", "argument_progression"},
        "delivery": {"explicit_bold_preservation", "artifact_path_privacy", "render_idempotency"},
        "audit": {"authorial_prose_judge", "reader_funnel_judge"},
        "maintenance": {"version_consistency", "learning_sample_promotion"},
    }
    for owner, markers in required.items():
        if owner not in ownership:
            fail(f"missing rule owner: {owner}")
        missing = markers - set(ownership[owner])
        if missing:
            fail(f"{owner} missing v0.6 ownership keys: {sorted(missing)}")

    stale = {"human_voice_judge", "stock_bold", "logical_transitions", "cross_finance_title_clickability"}
    leaked = stale & set(seen)
    if leaked:
        fail(f"stale/duplicate ownership keys remain: {sorted(leaked)}")
    if "visuals" in ownership:
        fail("visual ownership must remain removed")
    return len(seen)


def check_skill_and_reference_bundle() -> None:
    if not SKILL.is_file():
        fail("packaged Financial Writing SKILL.md missing")
    skill = SKILL.read_text(encoding="utf-8")
    for phrase in (
        "Financial Writing Agent v0.6",
        "resume_blocked_task",
        "record_writing_learning_sample",
        "market_explanation_scope = REQUIRED",
        "company universe alone is **not** enough",
        "not a universal hard requirement",
        "Publication articles do not use tables",
        "24px = 18pt",
        "20px = 15pt",
        "18px = 13.5pt",
        "Do not automatically bold every company/stock-name occurrence",
    ):
        if phrase not in skill:
            fail(f"Skill missing v0.6 instruction: {phrase}")
    for stale in (
        "references/structure_patterns.md",
        "Company/stock names remain bold on every occurrence",
        "When the ResearchPackage contains a company universe, `market_explanation` is mandatory",
        "Human Voice Gate",
        "submit_visual_package",
        "CHAT_TEXT",
        "writing-text://",
    ):
        if stale in skill:
            fail(f"legacy/stale Skill instruction remains: {stale}")

    sets = {
        "source": {p.name for p in SOURCE_REFS.glob("*.md")},
        "skill": {p.name for p in SKILL_REFS.glob("*.md")},
        "package": {p.name for p in PACKAGE_REFS.glob("*.md")},
    }
    if sets["source"] != sets["skill"] or sets["source"] != sets["package"]:
        fail(f"reference-set mismatch: { {k: sorted(v) for k, v in sets.items()} }")
    for forbidden in ("visuals.md", "structure_patterns.md"):
        if forbidden in sets["source"]:
            fail(f"obsolete reference must remain deleted: {forbidden}")
    for required in ("research.md", "market_explanation.md", "hooks.md", "style.md", "editorial.md", "delivery.md", "audit.md", "maintenance.md"):
        if required not in sets["source"]:
            fail(f"required reference missing: {required}")
    for name in sorted(sets["source"]):
        source = (SOURCE_REFS / name).read_bytes()
        if source != (SKILL_REFS / name).read_bytes():
            fail(f"skill/source reference drift: {name}")
        if source != (PACKAGE_REFS / name).read_bytes():
            fail(f"package/source reference drift: {name}")
    if SOURCE_POLICY.read_bytes() != PACKAGE_POLICY.read_bytes():
        fail("packaged policy drift from config/policy.json")


def check_policy() -> None:
    policy = json.loads(SOURCE_POLICY.read_text(encoding="utf-8"))
    if policy.get("contract_version") != CURRENT_VERSION:
        fail("policy contract_version mismatch")
    expected_sizes = {"h1_px": 24, "h1_pt": 18, "h2_px": 20, "h2_pt": 15, "body_px": 18, "body_pt": 13.5}
    for key, value in expected_sizes.items():
        if policy["word"].get(key) != value:
            fail(f"exact publication typography drift: {key}")
    if policy["word"].get("auto_bold_company_names") is not False:
        fail("company names must not return as blanket automatic bold")
    if policy["word"].get("allow_tables") is not False or policy["word"].get("tables_are_hard_fail") is not True:
        fail("publication tables must remain hard-failed")
    if policy["style"].get("optimize_for_ai_detector") is not False:
        fail("AI-detector evasion must not become a writing objective")
    dna = policy["style"].get("writing_dna_learning") or {}
    for marker in ("one_off_edit_is_candidate_only", "external_skill_rules_are_candidates_only", "raw_learning_sample_ledger_enabled"):
        if dna.get(marker) is not True:
            fail(f"Writing DNA discipline missing: {marker}")
    market = policy.get("market_explanation") or {}
    if market.get("activation_policy") != "EXPLICIT_SCOPE" or market.get("stock_universe_alone_is_not_activation") is not True:
        fail("Market Explanation must use explicit scope, not company-universe proxy activation")
    if set(policy["style"].get("hard_fail_extreme_phrases", [])) != {"注定暴涨", "必然上涨", "唯一机会"}:
        fail("deterministic extreme-language list should contain only unambiguous promotional promises")


def _is_tool_decorator(decorator: ast.expr) -> bool:
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    return isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "mcp" and target.attr == "tool"


def _tool_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(_is_tool_decorator(d) for d in node.decorator_list)
    }


def check_public_mcp_contract() -> int:
    for path in (PUBLIC_MCP, MCP_CONTRACTS, MODELS, RUNTIME_SERVICE):
        if not path.is_file():
            fail(f"required MCP/runtime file missing: {path.relative_to(ROOT)}")
    if (ROOT / "financial_writing_agent" / "mcp_server.py").exists():
        fail("obsolete mcp_server.py compatibility shim must remain deleted")

    names = _tool_names(PUBLIC_MCP)
    if names != EXPECTED_TOOLS:
        fail(f"public MCP tool inventory mismatch: missing={sorted(EXPECTED_TOOLS - names)}, extra={sorted(names - EXPECTED_TOOLS)}")
    if _tool_names(RUNTIME_SERVICE):
        fail("runtime_service.py must not register MCP tools")

    source = PUBLIC_MCP.read_text(encoding="utf-8")
    contracts = MCP_CONTRACTS.read_text(encoding="utf-8")
    models = MODELS.read_text(encoding="utf-8")
    for required in ("resume_blocked_task", "record_writing_learning_sample", "WritingTaskSummary", "LearningSampleSummary", "writing-docx://{task_id}/{kind}"):
        if required not in source + contracts:
            fail(f"v0.6 public contract marker missing: {required}")
    for forbidden in ("submit_visual_package", "WECHAT_STICKER_POST", "writing-text://", "CHAT_TEXT", "Human Voice"):
        if forbidden in source + contracts + models:
            fail(f"legacy public contract leaked back: {forbidden}")
    if "path: str" in contracts or "trace_tail" in contracts:
        fail("public result contract must not expose server-local paths/trace logs")
    return len(names)


def check_schema_and_runtime() -> None:
    schema = SCHEMAS.read_text(encoding="utf-8")
    runtime = RUNTIME_SERVICE.read_text(encoding="utf-8")
    engine = (ROOT / "financial_writing_agent" / "engine.py").read_text(encoding="utf-8")
    if 'ConfigDict(extra="forbid", str_strip_whitespace=True)' not in schema:
        fail("stage schemas must reject unknown fields")
    for marker in (
        'MarketExplanationScope = Literal["REQUIRED", "NOT_MATERIAL"]',
        "market_explanation_scope=REQUIRED requires market_explanation",
        "market_explanation_scope=NOT_MATERIAL must not include market_explanation",
        "class AuthorialProseAuditRubric(StrictModel)",
        "REVISE authorial-prose audit requires revision_target=DRAFT",
        "REVISE reader-funnel hook audit requires revision_target",
        "FAIL requires at least one defect",
    ):
        if marker not in schema:
            fail(f"v0.6 schema guard missing: {marker}")
    for stale in (
        "HumanVoiceAuditRubric",
        "stock/theme research with a company universe requires market_explanation",
        "transition_findings",
        "cross_finance_click_reason",
    ):
        if stale in schema:
            fail(f"superseded schema field/contract remains: {stale}")
    for marker in ("blocked_resume_stage", "resume_blocked", "RUNTIME_UNBLOCKED"):
        if marker not in engine + models:
            fail(f"recoverable BLOCKED semantics missing: {marker}")
    for marker in ("record_writing_learning_sample", "RAW_EVIDENCE_ONLY", "_cleanup_after_revision"):
        if marker not in runtime:
            fail(f"runtime hardening marker missing: {marker}")


def check_openai_executor() -> None:
    text = OPENAI_ADAPTER.read_text(encoding="utf-8")
    for required in (
        "RunConfig",
        'workflow_name="Financial Writing Agent"',
        "group_id=state.contract.task_id",
        "trace_include_sensitive_data=False",
        "market_explanation_scope=REQUIRED only when",
        "Broader cross-industry finance relevance is optional",
        "Financial Writing Authorial Prose Judge",
    ):
        if required not in text:
            fail(f"OpenAI stage executor missing v0.6 behavior: {required}")
    for stale in ("Human Voice Judge", "Each candidate must state a cross-finance click reason", "structure_patterns.md"):
        if stale in text:
            fail(f"old execution semantics remain in OpenAI adapter: {stale}")


def check_version_consistency() -> None:
    pyproject = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    project_version = pyproject["project"]["version"]
    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    policy = json.loads(SOURCE_POLICY.read_text(encoding="utf-8"))
    if {project_version, plugin.get("version"), policy.get("contract_version")} != {CURRENT_VERSION}:
        fail(f"machine-readable version drift: pyproject={project_version}, plugin={plugin.get('version')}, policy={policy.get('contract_version')}")
    for path in (README, ARCHITECTURE, SITE_SPEC, SKILL):
        if CURRENT_LABEL not in path.read_text(encoding="utf-8"):
            fail(f"human-readable contract version drift: {path.relative_to(ROOT)}")
    if "human-voice" in plugin.get("description", "").lower():
        fail("plugin description still advertises obsolete Human Voice semantics")


def check_deployment_and_packaging() -> None:
    site = SITE_SPEC.read_text(encoding="utf-8")
    for marker in (
        "personal/private deployment only",
        "Do not enable public sharing",
        "Do not silently fall back to ephemeral container/local disk",
        "17 tools",
        "resume_blocked_task",
        "record_writing_learning_sample",
    ):
        if marker not in site:
            fail(f"Site v0.6 boundary missing: {marker}")
    for stale in ("15 tools", "16-tool", "submit_visual_package", "WECHAT_STICKER_POST", "writing-text://", "company-name bolding"):
        if stale in site:
            fail(f"stale Site contract remains: {stale}")

    pyproject_text = PYPROJECT.read_text(encoding="utf-8")
    base = pyproject_text.split("[project.optional-dependencies]", 1)[0]
    if '"mcp>=2.0,<3"' not in base:
        fail("MCP must remain a base dependency")
    if 'financial-writing-mcp = "financial_writing_agent.plugin_server:main"' not in pyproject_text:
        fail("financial-writing-mcp entry point drift")
    if "resources/references/*.md" not in pyproject_text or "resources/policy.json" not in pyproject_text:
        fail("wheel package-data declarations missing")
    if not CAPABILITIES.is_file():
        fail("execution capability manifest missing")


def check_dead_contracts_removed() -> None:
    for path in (
        ROOT / "financial_writing_agent" / "contracts.py",
        ROOT / "financial_writing_agent" / "mcp_server.py",
        ROOT / "references" / "visuals.md",
        ROOT / "references" / "structure_patterns.md",
        ROOT / "skills" / "financial-writing-agent" / "references" / "visuals.md",
        ROOT / "skills" / "financial-writing-agent" / "references" / "structure_patterns.md",
        ROOT / "financial_writing_agent" / "resources" / "references" / "visuals.md",
        ROOT / "financial_writing_agent" / "resources" / "references" / "structure_patterns.md",
        ROOT / "continuity" / "tasks" / "ai-pharma-writing" / "HANDOFF.md",
        ROOT / "continuity" / "tasks" / "site-runtime-gate-a2" / "HANDOFF.md",
    ):
        if path.exists():
            fail(f"obsolete file must remain deleted: {path.relative_to(ROOT)}")


def main() -> None:
    groups = check_rule_ownership()
    check_skill_and_reference_bundle()
    check_policy()
    tools = check_public_mcp_contract()
    check_schema_and_runtime()
    check_openai_executor()
    check_version_consistency()
    check_deployment_and_packaging()
    check_dead_contracts_removed()
    print(
        f"PASS: {groups} unique rule ownership keys; v0.6 reference mirrors aligned; "
        f"one {tools}-tool Word-only MCP surface; recoverable BLOCKED state + raw Writing DNA ledger; "
        "explicit Market Explanation scope; selective bold; no legacy visual/text/template contracts; versions aligned"
    )


if __name__ == "__main__":
    main()
