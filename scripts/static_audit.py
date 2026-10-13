from __future__ import annotations

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
RULE_OWNERSHIP = ROOT / "config" / "rule_ownership.json"
PYPROJECT = ROOT / "pyproject.toml"
AGENT_MANIFEST = ROOT / "continuity" / "AGENT_MANIFEST.json"
CAPABILITIES = ROOT / "continuity" / "EXECUTION_CAPABILITIES.json"
OWNER_EXECUTION = ROOT / "continuity" / "FINANCIAL_OWNER_EXECUTION.json"
UNIVERSAL_ADAPTER = ROOT / "continuity" / "UNIVERSAL_PROTOCOL_ADAPTER.json"
TASK_MANIFEST = ROOT / "continuity" / "tasks" / "financial-writing-main" / "TASK_MANIFEST.json"
HANDOFF = ROOT / "continuity" / "tasks" / "financial-writing-main" / "HANDOFF.md"
TASK_INDEX = ROOT / "continuity" / "TASK_INDEX.md"
README = ROOT / "README.md"
ARCHITECTURE = ROOT / "docs" / "architecture.md"
SITE_SPEC = ROOT / "deploy" / "chatgpt-site" / "SITE_SPEC.md"
CI = ROOT / ".github" / "workflows" / "ci.yml"
LEGACY_EXECUTION_CONTRACT = ROOT / "continuity" / "GITHUB_CHAT_EXECUTION.json"
PLUGIN_MANIFEST = ROOT / "plugin.json"
LEGACY_SDK_SMOKE = ROOT / "scripts" / "sdk_smoke.py"
LEGACY_MCP_SMOKE = ROOT / "scripts" / "mcp_smoke.py"
MODELS = ROOT / "financial_writing_agent" / "models.py"
WORKFLOW = ROOT / "financial_writing_agent" / "workflow_spec.py"
GUARD = ROOT / "financial_writing_agent" / "github_chat_guard.py"
LIFECYCLE = ROOT / "financial_writing_agent" / "owner_lifecycle.py"
CHECKS = ROOT / "financial_writing_agent" / "checks.py"
DOCUMENT = ROOT / "financial_writing_agent" / "document.py"

CURRENT_VERSION = "0.8.1"
CURRENT_LABEL = "v0.8"


def fail(message: str) -> None:
    raise SystemExit(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def require_text(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            fail(f"{label} missing invariant: {marker}")


def forbid_text(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker in text:
            fail(f"{label} contains retired hot-path mechanism: {marker}")


def load_json(path: Path) -> dict:
    require(path.is_file(), f"missing required authority file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def check_versions_and_distribution_surface() -> None:
    pyproject = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    policy = load_json(SOURCE_POLICY)
    versions = {pyproject["project"]["version"], policy.get("contract_version")}
    require(versions == {CURRENT_VERSION}, f"machine-readable version drift: {versions}")
    require(CURRENT_LABEL in SKILL.read_text(encoding="utf-8"), "Skill version label drift")

    # Retired local/plugin runtimes may remain as source history, but current package
    # discovery must not export them as production task authorities.
    require("scripts" not in pyproject["project"], "pyproject still exports a legacy runtime command entrypoint")
    require(not PLUGIN_MANIFEST.exists(), "retired plugin.json rediscovered as a current product entry")
    require(not LEGACY_SDK_SMOKE.exists(), "retired SDK runtime smoke still exists in current scripts")
    require(not LEGACY_MCP_SMOKE.exists(), "retired MCP runtime smoke still exists in current scripts")


def check_reference_bundle() -> None:
    sets = {
        "source": {p.name for p in SOURCE_REFS.glob("*.md")},
        "skill": {p.name for p in SKILL_REFS.glob("*.md")},
        "package": {p.name for p in PACKAGE_REFS.glob("*.md")},
    }
    require(len({frozenset(v) for v in sets.values()}) == 1, f"reference-set mismatch: {sets}")
    for obsolete in ("visuals.md", "structure_patterns.md"):
        require(obsolete not in sets["source"], f"obsolete reference returned: {obsolete}")
    for name in sets["source"]:
        source = (SOURCE_REFS / name).read_bytes()
        require(source == (SKILL_REFS / name).read_bytes(), f"skill reference mirror drift: {name}")
        require(source == (PACKAGE_REFS / name).read_bytes(), f"package reference mirror drift: {name}")
    require(SOURCE_POLICY.read_bytes() == PACKAGE_POLICY.read_bytes(), "packaged policy drift")


def check_rule_ownership() -> None:
    ownership = load_json(RULE_OWNERSHIP)
    seen: dict[str, str] = {}
    for owner, keys in ownership.items():
        for key in keys:
            require(key not in seen, f"duplicate rule owner: {key}: {seen.get(key)} and {owner}")
            seen[key] = owner
    required = {
        "runtime": {"blocked_recovery", "downstream_invalidation", "required_outputs", "delivery_channel", "no_silent_degradation"},
        "research": {"universe_class_coverage", "universe_recall_sources", "material_company_classification"},
        "editorial": {"topic_specific_structures", "finance_deep_company_coverage", "company_comparison_decision_map"},
        "hooks": {"reader_funnel", "headline_angle_family_diversity", "finance_broad_non_niche_stake"},
        "style": {"natural_authorial_prose", "major_section_bridge", "template_cluster_guard"},
        "delivery": {"a_share_company_name_bold", "no_underlines", "no_end_source_section", "risk_italic"},
        "audit": {"chat_self_review_no_pass", "universe_article_reconciliation", "covert_recommendation_evasion_check"},
        "maintenance": {"version_consistency", "learning_sample_promotion"},
    }
    for owner, markers in required.items():
        missing = markers - set(ownership.get(owner, []))
        require(not missing, f"{owner} missing ownership keys: {sorted(missing)}")


def check_single_owner_authority() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    agent = load_json(AGENT_MANIFEST)
    capabilities = load_json(CAPABILITIES)
    execution = load_json(OWNER_EXECUTION)
    universal = load_json(UNIVERSAL_ADAPTER)
    task = load_json(TASK_MANIFEST)
    handoff = HANDOFF.read_text(encoding="utf-8")

    require(not LEGACY_EXECUTION_CONTRACT.exists(), "retired continuity/GITHUB_CHAT_EXECUTION.json still exists in current tree")

    require(agent["product_interface"].get("entry_model") == "SINGLE_OWNER_ENTRY", "agent entry is not single-owner")
    require(agent["product_interface"].get("execution_mode_selection") == "NONE", "agent still exposes execution-mode selection")
    require(agent["runtime"].get("runtime_type") == "SINGLE_GITHUB_BACKED_OWNER", "runtime is not single GitHub-backed owner")
    require(agent["runtime"].get("execution_contract") == "continuity/FINANCIAL_OWNER_EXECUTION.json", "agent points at wrong execution contract")
    require(agent["runtime"].get("canonical_lifecycle_implementation") == "financial_writing_agent/owner_lifecycle.py", "owner lifecycle is not canonical")
    require(agent["runtime"].get("alternate_business_state_runtime_allowed") is False, "alternate business-state runtime is still allowed")
    require(agent["harness"].get("commands") == ["pytest -q", "python scripts/eval_contracts.py", "python scripts/static_audit.py"], "harness still carries retired runtime smokes")

    active_state_refs = set(agent["workflow"].get("state_authority_refs", []))
    for retired_ref in ("financial_writing_agent/store.py", "financial_writing_agent/runtime_service.py", "financial_writing_agent/plugin_server.py", "continuity/GITHUB_CHAT_EXECUTION.json"):
        require(retired_ref not in active_state_refs, f"retired state authority remains active: {retired_ref}")

    require(capabilities.get("profile_version") == 11, "execution capability profile is not 11")
    ids = [item.get("capability_id") for item in capabilities.get("capabilities", [])]
    require(len(ids) == len(set(ids)), "duplicate capability ids")
    require("financial_owner_workflow" in ids, "single owner workflow capability missing")
    for item in capabilities.get("capabilities", []):
        require(item.get("side_channel_allowed") is False, f"side channel enabled: {item.get('capability_id')}")
        require(item.get("safe_degraded_modes") == [], f"degraded alternate mode remains: {item.get('capability_id')}")
    retired_caps = set(capabilities.get("legacy_quarantine", {}).get("not_current_capabilities", []))
    require("owner_plugin_runtime_as_task_authority" in retired_caps, "owner-plugin task authority not quarantined")
    require("SQLite_WritingState_as_task_authority" in retired_caps, "SQLite task authority not quarantined")

    require(execution.get("product_path") == "SINGLE_GITHUB_BACKED_FINANCIAL_OWNER", "execution contract is not single-owner")
    require(execution.get("execution", {}).get("route_selection") == "NONE", "execution contract still selects routes")
    require(execution.get("authority", {}).get("business_state_ref") == "main", "business state ref is not main")
    require(execution.get("authority", {}).get("business_state_root") == "workspaces/articles/{task_id}", "business state root drift")
    require(execution.get("authority", {}).get("alternate_runtime_state_authority_allowed") is False, "alternate runtime state authority allowed")
    require(execution.get("authority", {}).get("per_article_business_state_branches_allowed") is False, "per-article state branches allowed")
    require(execution.get("execution", {}).get("free_form_article_fallback_allowed") is False, "free-form fallback allowed")
    require(execution.get("checkpoint_contract", {}).get("storage_token_status") == "LEGACY_INTERNAL_TOKEN_ONLY__NOT_A_ROUTE_SELECTOR", "legacy execution token is not quarantined")

    binding = universal.get("execution_mode_binding", {})
    require(binding.get("route_selection") == "NONE", "Universal adapter still exposes route selection")
    require(binding.get("execution_contract") == "continuity/FINANCIAL_OWNER_EXECUTION.json", "Universal adapter points at retired execution contract")
    require(binding.get("alternate_business_state_runtime_allowed") is False, "Universal adapter allows alternate business state runtime")
    require(universal.get("execution_capability_profile_version") == 11, "Universal adapter capability profile drift")
    require(universal.get("legacy_quarantine", {}).get("legacy_presence_may_activate_route") is False, "legacy presence may activate a route")

    require(task.get("manifest_version") >= 22, "task manifest not migrated to single owner")
    require("PROFILE_11__SINGLE_GITHUB_BACKED_FINANCIAL_OWNER" in task.get("runtime_version", ""), "task runtime version not single-owner")
    require("continuity/FINANCIAL_OWNER_EXECUTION.json" in task.get("artifact_refs", []), "task manifest missing single owner execution contract")
    require("continuity/GITHUB_CHAT_EXECUTION.json" not in task.get("artifact_refs", []), "task manifest still references retired chat execution contract")

    require_text(skill, (
        "exactly one product/execution path",
        "main/workspaces/articles/{task_id}",
        "FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX",
        "Missing hard capability blocks the affected stage",
        "Historical branches/evals are evidence only",
    ), "Skill")
    forbid_text(skill, (
        "Use exposed persisted owner tools when actually available",
        "Otherwise guarded GitHub-chat execution",
        "choose OWNER_NATIVE",
        "choose `OWNER_NATIVE`",
    ), "Skill")
    require_text(handoff, (
        "one ChatGPT product path",
        "There is no longer a product/runtime decision between `OWNER_NATIVE` and `GITHUB_CHAT`",
        "not current business authority",
    ), "Handoff")


def check_business_contract_and_lifecycle() -> None:
    policy = load_json(SOURCE_POLICY)
    require(policy["defaults"].get("distribution_mode") == "DUAL", "default distribution mode drift")
    require(policy["defaults"].get("delivery_channel") == "WORD_FILE_ONLY", "default delivery channel drift")
    require(policy["word"].get("auto_bold_company_names") is True, "A-share company auto-bold drift")
    require(policy["word"].get("allow_tables") is False and policy["word"].get("tables_are_hard_fail") is True, "table prohibition drift")
    require(policy["word"].get("allow_underline") is False, "underline prohibition drift")
    require(policy["word"].get("end_source_section_allowed") is False, "source-tail prohibition drift")
    risk = policy["risk_disclaimer"]
    require(risk.get("italic") is True and risk.get("inline_paragraph") is True and risk.get("visible_heading") is False, "risk disclaimer presentation drift")

    models = MODELS.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    guard = GUARD.read_text(encoding="utf-8")
    lifecycle = LIFECYCLE.read_text(encoding="utf-8")
    checks = CHECKS.read_text(encoding="utf-8")
    document = DOCUMENT.read_text(encoding="utf-8")

    require_text(models, ("class TaskContract", "required_outputs must exactly match the canonical output set"), "TaskContract")
    require_text(workflow, ("BUSINESS_STAGE_ORDER", "REVISION_TARGETS", "invalidated_stages_from"), "workflow")
    require_text(guard, ("required_outputs", "delivery_artifacts", "article delivery outputs mismatch", "final delivery outputs mismatch", "USER_EXPLICIT_OVERRIDE"), "owner guard")
    require_text(lifecycle, ("block_review_failure_state", "resume_blocked_state", "review_system_impact_state", "canonical recovery cursor", "REGRESSION_VERIFIED"), "owner lifecycle")
    require_text(checks, ("analyze_template_scaffolding", "publication article must not contain end source section", "risk disclaimer must be italic", "publication article contains prohibited underline(s)"), "checks")
    require_text(document, ('render_text = f"风险提示：{render_text.strip()}"', "run.underline = False", "italic=is_risk"), "document")


def check_docs_ci_and_legacy_negative_space() -> None:
    current_docs = [README, ARCHITECTURE, SKILL, TASK_INDEX, HANDOFF, SITE_SPEC]
    forbidden = (
        "two execution adapters behind one business owner",
        "two execution adapters",
        "owner-native Python/plugin 实际可用时",
        "Otherwise guarded GitHub-chat execution",
    )
    for path in current_docs:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            require(marker not in text, f"{path.relative_to(ROOT)} contains retired marker: {marker}")

    ci = CI.read_text(encoding="utf-8")
    forbid_text(ci, ("scripts/sdk_smoke.py", "scripts/mcp_smoke.py", "financial_writing_agent.plugin_server", ".[dev,openai]"), "CI")
    require_text(ci, ("pytest -q", "python scripts/eval_contracts.py", "python scripts/static_audit.py", "financial_writing_agent.owner_lifecycle"), "CI")

    agent = load_json(AGENT_MANIFEST)
    current_refs = json.dumps(agent, ensure_ascii=False)
    forbid_text(current_refs, (
        '"runtime_type": "HYBRID"',
        '"owner_native_mode"',
        '"chat_mode"',
        '"GITHUB_CHAT_EXECUTION.json"',
    ), "Agent manifest")


def main() -> None:
    check_versions_and_distribution_surface()
    check_reference_bundle()
    check_rule_ownership()
    check_single_owner_authority()
    check_business_contract_and_lifecycle()
    check_docs_ci_and_legacy_negative_space()
    print("PASS: v0.8.1 single GitHub-backed Financial owner, canonical TaskContract/lifecycle, legacy quarantine and Word hard boundaries protected")


if __name__ == "__main__":
    main()
