"""Standalone Financial single-owner, reference and runtime-isolation audit.

This proves source-config invariants only, not live app activation, current
financial facts or actual article/reader acceptance.
"""
from __future__ import annotations
import json
from pathlib import Path
from financial_writing_agent.writing_kernel import validate_kernel

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = "FINANCIAL_WRITING_OWNER"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def require(value, message: str):
    if not value:
        raise SystemExit(message)


def main():
    needed = (
        "config/FINANCIAL_MANIFEST.json", "config/FINANCIAL_CAPABILITIES.json",
        "config/EXECUTION_CONTRACT.json", "config/PERSISTENT_ASSET_PROFILE.json",
        "skills/financial-writing-agent/SKILL.md", "FINANCIAL_SKILL.md",
        "docs/product_requirements.md", "docs/architecture.md",
        "docs/STANDALONE_INTERFACE.md", "financial_writing_agent/standalone_runtime.py",
        "financial_writing_agent/current_admission.py", "financial_writing_agent/owner_guard.py",
        "financial_writing_agent/owner_lifecycle.py", "financial_writing_agent/cognition_governance.py",
        "financial_writing_agent/private_research.py", "financial_writing_agent/story_quality.py",
        "financial_writing_agent/claim_trace.py", "financial_writing_agent/delivery_pipeline.py",
        "evals/EVOLUTION_INDEX.json", "evals/quality_regression.json",
    )
    for path in needed:
        require((ROOT / path).is_file(), f"missing standalone Financial source: {path}")
    manifest, caps, contract, assets = (
        load(x) for x in (
            "config/FINANCIAL_MANIFEST.json", "config/FINANCIAL_CAPABILITIES.json",
            "config/EXECUTION_CONTRACT.json", "config/PERSISTENT_ASSET_PROFILE.json"
        )
    )
    require(manifest["controller"] == caps["owner"] == contract["authority"]["controller"] == PRIMARY,
            "standalone Financial authority mismatch")
    require(manifest["domain_id"] == caps["domain_id"] == contract["domain_id"] == "financial_writing",
            "domain identity drift")
    require(manifest["skill_entrypoint"] == caps["entrypoint"] == "skills/financial-writing-agent/SKILL.md",
            "standalone operating Skill mismatch")
    require(manifest["state_authority"] == "workspaces/articles/{task_id}/STATE.json",
            "Article Aggregate identity changed")
    require(manifest["provider_adapter"] == "financial_writing_agent.standalone_runtime",
            "Financial-only provider entry missing")
    require(manifest["external_parent_required"] is False and manifest["external_host_required"] is False,
            "external parent/Host became mandatory")
    require(caps["independent_parent_free"] is True
            and caps["independence_clause"] == "NO_CAOS_UAOS_PARENT_REPOSITORY_OR_HOST_INVOCATION",
            "active capability dependency is external")
    require(contract["product_path"] == "DIRECT_FINANCIAL_STANDALONE"
            and contract["execution"]["route_selection"] == "DIRECT_FINANCIAL_ONLY"
            and contract["execution"]["direct_domain_activation"] is True,
            "current execution no longer direct Financial")
    require(contract["execution"]["live_parent_business_proxy_required"] is False
            and contract["execution"]["free_form_article_fallback_allowed"] is False,
            "fallback or external parent proxy enabled")
    require(contract["standalone_governance"]["external_parent_required"] is False
            and contract["standalone_governance"]["parent_host_or_plugin_assumed_connected"] is False,
            "standalone mode assumes a live Host")
    require(contract["authority"]["alternate_business_state_authority_allowed"] is False,
            "second owner slipped into execution config")
    require(contract["problem_and_evolution"]["generic_problem_cognition_owner"] == PRIMARY,
            "decision loop outsourced")
    require(contract["problem_and_evolution"]["common_or_cross_domain_change_uses_parent_upcall"] is False,
            "Financial evolution depends on parent")
    require(len(assets["current_authority_assets"]) == 1, "not exactly one Financial business authority")
    require(assets["current_authority_assets"][0]["resource_ref"]
            == "github://D1traverser-debug/financial-writing-agent@main",
            "Financial GitHub authority changed")
    require(all(x["role"] != "AUTHORITY" for x in assets["non_authority_assets"]),
            "external asset promoted to business owner")

    active = (manifest, caps, contract, assets)
    all_text = json.dumps(active, ensure_ascii=False)
    for forbidden in ("D1traverser-debug/cognition-agent-os", "D1traverser-debug/universal-agent-os"):
        require(forbidden not in all_text, f"active Financial config still binds retired parent: {forbidden}")
    for path in ("CAOS_SKILL.md", "UAOS_SKILL.md", ".uaos/MANIFEST.json",
                 ".uaos/ADAPTER.json", ".uaos/CAPABILITIES.json"):
        text = (ROOT / path).read_text(encoding="utf-8")
        require("non-authoritative" in text or "RETIRED_HISTORICAL_COMPATIBILITY_ONLY" in text
                or "non-authoritative" in text.lower() or "non-authoritative" in text.lower(),
                f"old entry still looks active: {path}")
    skill = (ROOT / manifest["skill_entrypoint"]).read_text(encoding="utf-8")
    for marker in ("Independent Operating Skill", "Decision", "Execution", "PrivateResearchBrief",
                   "FINANCE", "source", "DOCX", "standalone_runtime.py", "no parent",
                   "article", "originality"):
        require(marker.lower() in skill.lower(), f"operating Skill lacks Financial duty: {marker}")
    from financial_writing_agent.standalone_runtime import DOMAIN_ID, OPERATIONS
    require(DOMAIN_ID == "financial_writing", "Financial standalone module domain drift")
    require({"CREATE_ARTICLE", "ADVANCE_STAGE", "CHANGE_REQUIREMENTS", "ATTACH_FEEDBACK"} <= OPERATIONS,
            "owner mutation operations incomplete")
    require(validate_kernel() == [], "Financial writing-pass graph invalid")
    caps_ids = [item["id"] for item in caps["capabilities"]]
    require(len(caps_ids) == len(set(caps_ids)) and len(caps_ids) >= 8,
            "standalone Financial capabilities missing/duplicated")
    require(not (ROOT / "continuity").exists() and not (ROOT / "TASK_INDEX.json").exists(),
            "parallel Financial task controller returned")
    for name in ("research.md", "knowledge.md", "private_research.md", "reader_value.md",
                 "market_explanation.md", "audit.md", "editorial.md", "hooks.md",
                 "style.md", "platforms.md", "delivery.md", "maintenance.md"):
        reference = (ROOT / "references" / name).read_bytes()
        package = (ROOT / "financial_writing_agent/resources/references" / name).read_bytes()
        skill_ref = (ROOT / "skills/financial-writing-agent/references" / name).read_bytes()
        require(reference == package == skill_ref, f"Financial reference mirror drift: {name}")
    print("PASS: Financial operates with its own standalone Skill, owner state, method/capability "
          "manifest, provider action port and Word/research validators; no active parent "
          "dependency. Live connected app and editorial outcome not certified.")


if __name__ == "__main__":
    main()
