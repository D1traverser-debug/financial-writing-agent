"""Financial asset authority is singular; outside systems are typed resources, not controllers."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _j(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_financial_caos_asset_register_declares_exactly_one_github_business_authority():
    p = _j("config/PERSISTENT_ASSET_PROFILE.json")
    assert p["domain_id"] == "financial_writing"
    assert p["parent_method_ref"].startswith("D1traverser-debug/cognition-agent-os@main:")
    assert "universal-agent-os" not in json.dumps(p)
    assert p["authority_cardinality"] == "EXACTLY_ONE_CURRENT_FINANCIAL_BUSINESS_AUTHORITY__GITHUB_MAIN"
    assert len(p["current_authority_assets"]) == 1
    owner = p["current_authority_assets"][0]
    assert owner["resource_ref"] == owner["canonical_authority_ref"] == "github://D1traverser-debug/financial-writing-agent@main"
    assert owner["role"] == "AUTHORITY" and owner["lifecycle"] == "CURRENT"


def test_notions_drive_library_memory_and_sandbox_cannot_gain_owner_authority():
    p = _j("config/PERSISTENT_ASSET_PROFILE.json")
    items = p["non_authority_assets"]
    assert items
    assert {"CHAT", "MEMORY", "CUSTOM_INSTRUCTIONS", "NOTION", "GOOGLE_DRIVE",
            "LIBRARY", "AUTOMATION", "GMAIL", "TEMP_SANDBOX"} <= {i["surface"] for i in items}
    assert all(i["role"] != "AUTHORITY" and i["lifecycle"] != "CURRENT" for i in items)
    assert p["storage_reconciliation_rule"].startswith("For each new chat/Work session")
    assert "NOT_PHYSICALLY_INTERCEPTED" in p["independent_acceptance_boundary"]


def test_migrated_sources_are_explicit_history_and_not_current_grants():
    p = _j("config/PERSISTENT_ASSET_PROFILE.json")
    assets = {item["asset_id"]: item for item in p["non_authority_assets"]}
    for asset in ("notion-migrated-control-pages", "gdrive-migrated-financial-continuity"):
        assert assets[asset]["role"] == "MIGRATED_HISTORY"
        assert assets[asset]["lifecycle"] == "OBSERVED_DECOMMISSIONED"
    assert assets["notion-financial-research-resources"]["role"] == "SHARED_RESEARCH_RESOURCE"
    assert assets["library-financial-outputs"]["role"] == "DELIVERY_HISTORY"
    assert assets["old-parent-watch"]["lifecycle"] == "UNVERIFIED_CURRENT"


def test_caos_parent_discovery_and_asset_register_do_not_duplicate_evolution_or_state():
    manifest = _j(".uaos/MANIFEST.json")
    profile = _j("config/PERSISTENT_ASSET_PROFILE.json")
    assert manifest["controller"] == "D1traverser-debug/cognition-agent-os@main"
    assert manifest["domain_authority"]["article_identity"] == "workspaces/articles/{task_id}/STATE.json::task_id"
    assert len(profile["current_authority_assets"]) == 1
    assert not (ROOT / "TASK_INDEX.json").exists()
    assert not (ROOT / "continuity").exists()
