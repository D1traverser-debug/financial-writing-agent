"""CI structural conformance: one Financial owner under opt-in CAOS cognition."""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PARENT = "D1traverser-debug/cognition-agent-os@main"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def main() -> None:
    paths = (
        "CAOS_SKILL.md", "UAOS_SKILL.md", ".uaos/MANIFEST.json",
        ".uaos/ADAPTER.json", ".uaos/CAPABILITIES.json",
        "config/EXECUTION_CONTRACT.json", "docs/product_requirements.md",
        "docs/architecture.md", "docs/CAOS_CHILD_INTERFACE.md",
        "financial_writing_agent/caos_bridge.py", "financial_writing_agent/path_identity.py",
        "financial_writing_agent/owner_guard.py",
        "financial_writing_agent/current_admission.py",
        "financial_writing_agent/owner_lifecycle.py",
        "financial_writing_agent/proactive_resolution.py",
        "financial_writing_agent/problem_action_admission.py",
        "financial_writing_agent/workflow_spec.py",
        "financial_writing_agent/models.py", "evals/EVOLUTION_INDEX.json",
        "evals/quality_regression.json", "tests/test_caos_bridge.py",
    )
    for path in paths:
        require((ROOT / path).is_file(), f"missing Financial authority: {path}")
    for retired in ("continuity", "state", "financial_writing_agent/uaos_binding.py",
                    "financial_writing_agent/github_chat_guard.py", "tests/test_uaos_article_binding.py"):
        require(not (ROOT / retired).exists(), f"retired control authority returned: {retired}")

    m, a, c, e = (load(path) for path in (
        ".uaos/MANIFEST.json", ".uaos/ADAPTER.json",
        ".uaos/CAPABILITIES.json", "config/EXECUTION_CONTRACT.json"))
    require(m["controller"] == a["controller"] == e["authority"]["controller"] == PARENT,
            "CAOS parent identity mismatch")
    require(m["skill"]["entrypoint"] == "CAOS_SKILL.md", "parent native discovery skill not canonical")
    require(m["binding"]["adapter_ref"] == ".uaos/ADAPTER.json"
            and m["binding"]["capability_ref"] == ".uaos/CAPABILITIES.json",
            "CAOS domain_contract.py compatibility read path mismatch")
    require(m["binding"]["controller_ref"] == PARENT + ":src/cognition_agent_os/domain_contract.py",
            "CAOS native parent interface reference drift")
    require(m["binding"]["protocol"] == "CHILD_CONTRACT_OBSERVATION_V1",
            "nonexistent parent contract version advertised")
    require(a["caos_parent_contract_kind"] == "domain_contract"
            and a["caos_child_adapter"] == "financial_writing_agent.caos_bridge",
            "CAOS child action adapter not declared")
    require(c["caos_domain_contract_ref"] == m["binding"]["controller_ref"],
            "CAOS child capability metadata uses inconsistent interface")
    for doc in (m, a, c, e):
        require("D1traverser-debug/universal-agent-os" not in json.dumps(doc),
                "active Financial governance still points to old UAOS parent")
    require(m["domain_id"] == a["domain_id"] == c["domain_id"] == e["domain_id"] == "financial_writing",
            "domain identity drift")
    owner = m["domain_authority"]
    require(owner["article_identity"] == "workspaces/articles/{task_id}/STATE.json::task_id",
            "child article authority drift")
    require(owner["current_admission_guard"] == "financial_writing_agent/current_admission.py",
            "current domain aggregate admission drift")
    require(owner["canonical_evolution_evidence"] == "evals/EVOLUTION_INDEX.json",
            "second evolution owner or missing canonical evidence")
    require(a["business_state_authority"] == "workspaces/articles/{task_id}/STATE.json"
            and a["common_or_cross_domain_evolution_authority"] == "CAOS",
            "parent and child business authority conflated")
    require("NO_EQUALITY_REQUIREMENT" in a["identity_boundary"],
            "CAOS/Financial task ID namespaces must remain distinct")
    require(e["authority"]["alternate_business_state_authority_allowed"] is False
            and e["identity"]["parent_child_id_equality_required"] is False,
            "duplicate parent/child state owner")
    require(e["execution"]["direct_domain_activation"] is True
            and e["execution"]["live_parent_business_proxy_required"] is False
            and e["execution"]["free_form_article_fallback_allowed"] is False,
            "Financial current route and hard gates weakened")
    require(e["hosted_governance"]["parent_read_only_observation"] is True,
            "read-only CAOS parent observer falsely described as executor")
    require(e["hosted_governance"]["child_business_action_requires_owner_native_gate"] is True,
            "child business admission bypass advertised")
    require(e["hosted_governance"]["parent_host_or_plugin_assumed_connected"] is False,
            "phantom connected CAOS Host claimed")
    require(e["hosted_governance"]["common_cross_domain_evolution_owner"] == "CAOS",
            "Financial common method upcall not CAOS")
    require(e["problem_and_evolution"]["generic_problem_cognition_owner"]
            == "CAOS_OPT_IN_COGNITION_PARENT", "old cognition owner active")
    require(e["problem_and_evolution"]["one_off_observation_auto_promotes_to_global_rule"] is False,
            "user feedback can auto-promote global rules")

    caps = c["capabilities"]
    ids = [x.get("capability_id") for x in caps]
    require(bool(ids) and len(ids) == len(set(ids)) and all(
        isinstance(cid, str) and re.fullmatch(r"[a-z][a-z0-9_]{1,79}", cid) for cid in ids
    ), "CAOS parent native child capability declaration cannot be read")
    require(all(x.get("side_channel_allowed") is False for x in caps),
            "side channels bypass Financial owner")
    by_id = {x["capability_id"]: x for x in caps}
    for cid in (
        "financial_owner_workflow", "domain_owned_article_identity_and_state",
        "high_judgment_generation_stages", "problem_cognition_root_scope_admission",
        "problem_action_closure_admission", "proactive_resolution_admission",
        "quality_regression_promotion_gate", "domain_product_requirements_traceability",
    ):
        require(cid in by_id, f"missing scoped capability: {cid}")
    require("CAOS:domain_internal_work_orchestration"
            in by_id["high_judgment_generation_stages"].get("required", []),
            "subsystem still depends on UAOS for writing")
    require(c["hosted_cognition_semantics"]["implementation_evidence"]
            == "NOT_EQUIVALENT_TO_NATIVE_HOST_ACTIVATION",
            "parent contract falsely claims a native Host was invoked")
    expected = {
        "original_goal_and_correction_fidelity",
        "competing_causal_hypotheses_and_falsification",
        "independent_child_business_outcome_readback",
        "permission_and_effect_separation",
    }
    require(expected.issubset(set(c["required_caos_parent_responsibilities"])),
            "full owner goal/cognition/verification duties were lost")

    entry = (ROOT / "CAOS_SKILL.md").read_text(encoding="utf-8")
    discovery = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    retired_skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    for required in (
        "cognition-agent-os", "current_admission", "caos_bridge",
        "evals/EVOLUTION_INDEX.json#active_system_assessment",
        "references/private_research.md", "references/editorial.md",
        "references/delivery.md", "references/maintenance.md",
    ):
        require(required in entry, f"CAOS child Skill omitted live route: {required}")
    require(len(entry.encode("utf-8")) <= 8192, "current CAOS Skill exceeds thin entry budget")
    require("CAOS_SKILL.md" in discovery and "Discovery Pointer" in discovery,
            "discovery points to retired parent")
    require("non-authoritative" in retired_skill, "old UAOS skill not explicitly retired")

    models_text = (ROOT / "financial_writing_agent/models.py").read_text(encoding="utf-8")
    require("task_id:" not in models_text, "TaskContract now duplicates article identity")
    pkg = "\n".join(f.read_text(encoding="utf-8")
                    for f in (ROOT / "financial_writing_agent").glob("*.py"))
    for forbidden in ("DeliberationController", "EvolutionController", "validate_uaos_article_binding"):
        require(forbidden not in pkg, f"duplicate controller leaked into child: {forbidden}")
    require("require_user_escalation_admission" in pkg,
            "Financial native recovery-before-escalation disappeared")

    for name in ("research.md", "knowledge.md", "private_research.md",
                 "reader_value.md", "market_explanation.md", "audit.md",
                 "editorial.md", "hooks.md", "style.md", "platforms.md",
                 "delivery.md", "maintenance.md"):
        orig = (ROOT / "references" / name).read_bytes()
        packaged = (ROOT / "financial_writing_agent/resources/references" / name).read_bytes()
        skill_ref = (ROOT / "skills/financial-writing-agent/references" / name).read_bytes()
        require(orig == packaged == skill_ref, f"reference packaging drift: {name}")

    print("PASS: CAOS parent source contract, Financial single owner, actual child write/permission boundary, "
          "legacy bridge-file compatibility and mirrored domain policy are coherent; "
          "independent editorial outcome remains a separate admission.")


if __name__ == "__main__":
    main()
