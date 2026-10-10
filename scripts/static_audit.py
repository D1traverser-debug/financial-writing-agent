from __future__ import annotations

import ast
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "financial-writing-agent" / "SKILL.md"
SOURCE_REFS = ROOT / "references"
SKILL_REFS = ROOT / "skills" / "financial-writing-agent" / "references"
PACKAGE_REFS = ROOT / "financial_writing_agent" / "resources" / "references"
SOURCE_POLICY = ROOT / "config" / "policy.json"
PACKAGE_POLICY = ROOT / "financial_writing_agent" / "resources" / "policy.json"
PUBLIC_MCP = ROOT / "financial_writing_agent" / "plugin_server.py"
MCP_CONTRACTS = ROOT / "financial_writing_agent" / "mcp_contracts.py"
MODELS = ROOT / "financial_writing_agent" / "models.py"
ENGINE = ROOT / "financial_writing_agent" / "engine.py"
RUNTIME = ROOT / "financial_writing_agent" / "runtime_service.py"
SCHEMAS = ROOT / "financial_writing_agent" / "schemas.py"
CHECKS = ROOT / "financial_writing_agent" / "checks.py"
DOCUMENT = ROOT / "financial_writing_agent" / "document.py"
OPENAI_ADAPTER = ROOT / "financial_writing_agent" / "adapters" / "openai_agents.py"
SITE_SPEC = ROOT / "deploy" / "chatgpt-site" / "SITE_SPEC.md"
README = ROOT / "README.md"
ARCHITECTURE = ROOT / "docs" / "architecture.md"
PLUGIN_JSON = ROOT / "plugin.json"
PYPROJECT = ROOT / "pyproject.toml"
CAPABILITIES = ROOT / "continuity" / "EXECUTION_CAPABILITIES.json"

CURRENT_VERSION = "0.7.0"
CURRENT_LABEL = "v0.7"
EXPECTED_TOOLS = {
    "start_writing_task", "get_writing_task", "list_recent_writing_tasks",
    "resume_blocked_task", "record_writing_learning_sample", "record_knowledge_context",
    "submit_research", "submit_research_audit", "submit_editorial_plan", "submit_headlines",
    "submit_draft", "submit_hook_audit", "submit_style_audit", "submit_editorial_audit",
    "build_and_mechanically_audit_delivery", "record_knowledge_writeback", "submit_final_audit",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            fail(f"{label} missing invariant: {marker}")


def forbid(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker in text:
            fail(f"{label} contains removed/legacy invariant: {marker}")


def check_versions() -> None:
    pyproject = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    policy = json.loads(SOURCE_POLICY.read_text(encoding="utf-8"))
    versions = {pyproject["project"]["version"], plugin.get("version"), policy.get("contract_version")}
    if versions != {CURRENT_VERSION}:
        fail(f"machine-readable version drift: {versions}")
    for path in (README, ARCHITECTURE, SITE_SPEC, SKILL):
        if CURRENT_LABEL not in path.read_text(encoding="utf-8"):
            fail(f"human-readable version drift: {path.relative_to(ROOT)}")
    if "human-voice" in plugin.get("description", "").lower():
        fail("plugin manifest still advertises obsolete Human Voice semantics")


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
        "research": {"universe_class_coverage", "universe_recall_sources", "material_company_classification"},
        "market_explanation": {"explicit_scope_activation", "stock_universe_not_activation"},
        "editorial": {"topic_specific_structures", "macro_structural_coherence", "finance_deep_company_coverage", "stock_grounded_validation_sections", "company_comparison_decision_map", "deep_numbered_navigation"},
        "hooks": {"reader_funnel", "continuation_value", "headline_angle_family_diversity", "finance_broad_non_niche_stake"},
        "style": {"natural_authorial_prose", "raw_learning_sample_ledger", "argument_progression", "major_section_bridge", "template_cluster_guard"},
        "delivery": {"explicit_bold_preservation", "no_underlines", "no_end_source_section", "risk_italic", "artifact_path_privacy", "render_idempotency"},
        "audit": {"authorial_prose_judge", "reader_funnel_judge", "semantic_audit_provenance", "chat_self_review_no_pass", "universe_article_reconciliation", "covert_recommendation_evasion_check"},
        "maintenance": {"version_consistency", "learning_sample_promotion"},
    }
    for owner, markers in required.items():
        missing = markers - set(ownership.get(owner, []))
        if missing:
            fail(f"{owner} missing ownership keys: {sorted(missing)}")
    stale = {"human_voice_judge", "stock_bold", "logical_transitions", "cross_finance_title_clickability"}
    if stale & set(seen):
        fail(f"stale ownership keys remain: {sorted(stale & set(seen))}")
    if "visuals" in ownership:
        fail("visual ownership must remain removed")
    return len(seen)


def check_reference_bundle() -> None:
    sets = {
        "source": {p.name for p in SOURCE_REFS.glob("*.md")},
        "skill": {p.name for p in SKILL_REFS.glob("*.md")},
        "package": {p.name for p in PACKAGE_REFS.glob("*.md")},
    }
    if len({frozenset(v) for v in sets.values()}) != 1:
        fail(f"reference-set mismatch: { {k: sorted(v) for k, v in sets.items()} }")
    for obsolete in ("visuals.md", "structure_patterns.md"):
        if obsolete in sets["source"]:
            fail(f"obsolete reference returned: {obsolete}")
    for name in sets["source"]:
        source = (SOURCE_REFS / name).read_bytes()
        if source != (SKILL_REFS / name).read_bytes() or source != (PACKAGE_REFS / name).read_bytes():
            fail(f"reference mirror drift: {name}")
    if SOURCE_POLICY.read_bytes() != PACKAGE_POLICY.read_bytes():
        fail("packaged policy drift")

    skill = SKILL.read_text(encoding="utf-8")
    lower = skill.lower()
    require(skill, (
        "resume_blocked_task",
        "record_writing_learning_sample",
        "Universe Coverage Ledger",
        "MATERIAL / SECONDARY / REFERENCE_ONLY",
        "company_coverage_obligations",
        "company comparison decision map",
        "cold-reader test",
        "major H1 sections must also be **earned transitions**",
        "zero underlines",
        "风险提示：",
        "angle_family",
        "template-cluster guard",
        "CHAT_SELF_REVIEW",
        "Do not automatically bold every company/stock-name occurrence",
    ), "Skill")
    if "publication articles do not use tables" not in lower:
        fail("Skill must prohibit publication tables")
    forbid(skill, ("references/structure_patterns.md", "Company/stock names remain bold on every occurrence", "Human Voice Gate", "CHAT_TEXT", "writing-text://"), "Skill")


def _tool_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            target = decorator.func if isinstance(decorator, ast.Call) else decorator
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "mcp" and target.attr == "tool":
                names.add(node.name)
    return names


def check_runtime_contract() -> int:
    tools = _tool_names(PUBLIC_MCP)
    if tools != EXPECTED_TOOLS:
        fail(f"MCP inventory mismatch: missing={sorted(EXPECTED_TOOLS-tools)}, extra={sorted(tools-EXPECTED_TOOLS)}")
    if _tool_names(RUNTIME):
        fail("runtime_service must not register MCP tools")

    public = PUBLIC_MCP.read_text(encoding="utf-8")
    contracts = MCP_CONTRACTS.read_text(encoding="utf-8")
    models = MODELS.read_text(encoding="utf-8")
    engine = ENGINE.read_text(encoding="utf-8")
    runtime = RUNTIME.read_text(encoding="utf-8")
    schemas = SCHEMAS.read_text(encoding="utf-8")
    checks = CHECKS.read_text(encoding="utf-8")
    document = DOCUMENT.read_text(encoding="utf-8")

    require(public + contracts, ("resume_blocked_task", "record_writing_learning_sample", "LearningSampleSummary", "writing-docx://{task_id}/{kind}"), "public MCP")
    forbid(public + contracts + models, ("submit_visual_package", "WECHAT_STICKER_POST", "writing-text://", "CHAT_TEXT", "Human Voice"), "public MCP")
    if "path: str" in contracts or "trace_tail" in contracts:
        fail("public contract exposes local path/trace")

    require(engine + models, ("blocked_resume_stage", "resume_blocked", "RUNTIME_UNBLOCKED"), "recovery runtime")
    require(runtime, ("record_writing_learning_sample", "RAW_EVIDENCE_ONLY", "_cleanup_after_revision"), "runtime service")
    require(schemas, (
        'MarketExplanationScope = Literal["REQUIRED", "NOT_MATERIAL"]',
        "class UniverseCoverage(StrictModel)",
        "value_chain_class",
        "materiality: CompanyMateriality",
        "company_coverage_obligations",
        "angle_family: HeadlineAngleFamily",
        "headline_strategy_diversity",
        "CHAT_SELF_REVIEW",
        "chat self-review cannot PASS",
        "class AuthorialProseAuditRubric(StrictModel)",
    ), "schemas")
    require(checks, (
        "analyze_template_scaffolding",
        "check_deep_company_grounding",
        "check_payload_navigation",
        "monitoring/validation section is detached",
        "publication article must not contain end source section",
        "risk disclaimer must be italic",
        "publication article contains prohibited underline(s)",
    ), "deterministic content guards")
    require(document, (
        "risk_mode",
        'render_text = f"风险提示：{render_text.strip()}"',
        "run.underline = False",
        "italic=is_risk",
    ), "Word builder")
    forbid(schemas, ("HumanVoiceAuditRubric", "transition_findings", "cross_finance_click_reason", "stock/theme research with a company universe requires market_explanation"), "schemas")
    return len(tools)


def check_policy_and_executor() -> None:
    policy = json.loads(SOURCE_POLICY.read_text(encoding="utf-8"))
    if policy["market_explanation"].get("activation_policy") != "EXPLICIT_SCOPE" or policy["market_explanation"].get("stock_universe_alone_is_not_activation") is not True:
        fail("Market Explanation activation drift")
    if policy["research"].get("universe_class_coverage_required") is not True or policy["research"].get("universe_recall_sources_min", 0) < 2:
        fail("universe-recall hardening drift")
    if policy["editorial"].get("finance_deep_representative_stock_shortcut_forbidden") is not True or policy["editorial"].get("stock_grounded_validation_sections_required") is not True:
        fail("Deep company-completeness hardening drift")
    if policy["editorial"].get("company_comparison_decision_map_required") is not True or len(policy["editorial"].get("company_comparison_dimensions", [])) < 4:
        fail("company comparison decision-map hardening drift")
    if policy["hooks"].get("headline_angle_families_min", 0) < 5 or policy["hooks"].get("synonym_only_headline_pool_is_fail") is not True:
        fail("headline strategy-diversity hardening drift")
    if policy["hooks"].get("finance_broad_non_niche_stake_required") is not True or not policy["hooks"].get("finance_broad_stake_dimensions"):
        fail("broad-finance cold-reader stake drift")
    if policy["style"].get("template_cluster_guard_required") is not True or policy["style"].get("deep_numbered_navigation_required_when_branching") is not True or policy["style"].get("major_section_bridge_required") is not True:
        fail("prose/navigation/bridge hardening drift")
    if policy["audit"].get("semantic_pass_requires_independent_executor") is not True or policy["audit"].get("chat_self_review_cannot_pass") is not True:
        fail("semantic audit provenance hardening drift")
    if policy["finance_compliance"].get("no_covert_recommendation_evasion") is not True or policy["finance_compliance"].get("company_comparison_must_remain_non_actionable") is not True:
        fail("covert-recommendation compliance boundary drift")
    if policy["word"].get("auto_bold_company_names") is not False:
        fail("blanket company bolding returned")
    if policy["word"].get("allow_tables") is not False or policy["word"].get("tables_are_hard_fail") is not True:
        fail("table prohibition drift")
    if policy["word"].get("allow_underline") is not False or policy["word"].get("end_source_section_allowed") is not False:
        fail("Word underline/source-tail prohibition drift")
    if policy["risk_disclaimer"].get("italic") is not True or policy["risk_disclaimer"].get("inline_paragraph") is not True or policy["risk_disclaimer"].get("visible_heading") is not False:
        fail("risk disclaimer presentation drift")
    if set(policy["style"].get("hard_fail_extreme_phrases", [])) != {"注定暴涨", "必然上涨", "唯一机会"}:
        fail("deterministic extreme-language boundary drift")
    dna = policy["style"].get("writing_dna_learning", {})
    if not dna.get("raw_learning_sample_ledger_enabled") or not dna.get("one_off_edit_is_candidate_only"):
        fail("Writing DNA evidence discipline drift")

    adapter = OPENAI_ADAPTER.read_text(encoding="utf-8")
    require(adapter, (
        "RunConfig",
        'workflow_name="Financial Writing Agent"',
        "group_id=state.contract.task_id",
        "trace_include_sensitive_data=False",
        "universe_coverage",
        "value-chain class",
        "check_deep_company_grounding",
        "analyze_template_scaffolding",
        "angle_family",
        "INDEPENDENT_EXECUTOR",
        "Financial Writing Authorial Prose Judge",
    ), "OpenAI executor")
    forbid(adapter, ("Human Voice Judge", "Each candidate must state a cross-finance click reason", "structure_patterns.md"), "OpenAI executor")


def check_site_and_dead_contracts() -> None:
    site = SITE_SPEC.read_text(encoding="utf-8")
    require(site, ("personal/private deployment only", "17 tools", "resume_blocked_task", "record_writing_learning_sample", "Do not silently fall back to ephemeral container/local disk"), "Site spec")
    forbid(site, ("15 tools", "16-tool", "submit_visual_package", "WECHAT_STICKER_POST", "writing-text://", "company-name bolding"), "Site spec")
    for path in (
        ROOT / "financial_writing_agent" / "contracts.py",
        ROOT / "financial_writing_agent" / "mcp_server.py",
        ROOT / "references" / "visuals.md",
        ROOT / "references" / "structure_patterns.md",
        ROOT / "continuity" / "HANDOFF_COMPACTION_PLAN.json",
        ROOT / "continuity" / "tasks" / "ai-pharma-writing" / "HANDOFF.md",
        ROOT / "continuity" / "tasks" / "site-runtime-gate-a2" / "HANDOFF.md",
    ):
        if path.exists():
            fail(f"obsolete file remains: {path.relative_to(ROOT)}")
    if not CAPABILITIES.is_file():
        fail("execution capability manifest missing")


def main() -> None:
    check_versions()
    groups = check_rule_ownership()
    check_reference_bundle()
    tools = check_runtime_contract()
    check_policy_and_executor()
    check_site_and_dead_contracts()
    print(f"PASS: v0.7 versions aligned; {groups} owned rules; mirrored references aligned; {tools} typed MCP tools; Universe Coverage + company decision map + broad cold-reader stake + major-section bridges + clean Word presentation + independent semantic audits protected")


if __name__ == "__main__":
    main()
