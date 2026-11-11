"""Finance standalone assets: only one current GitHub authority."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _j(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_financial_asset_register_has_one_standalone_current_owner():
    assets = _j("config/PERSISTENT_ASSET_PROFILE.json")
    manifest = _j("config/FINANCIAL_MANIFEST.json")
    assert assets["domain_id"] == manifest["domain_id"] == "financial_writing"
    assert assets["standalone_runtime"] == "financial_writing_agent.standalone_runtime"
    assert assets["authority_cardinality"] == "EXACTLY_ONE_CURRENT_FINANCIAL_BUSINESS_AUTHORITY__GITHUB_MAIN"
    assert len(assets["current_authority_assets"]) == 1
    owner = assets["current_authority_assets"][0]
    assert owner["role"] == "AUTHORITY" and owner["lifecycle"] == "CURRENT"
    assert owner["resource_ref"] == owner["canonical_authority_ref"] == "github://D1traverser-debug/financial-writing-agent@main"
    assert manifest["external_parent_required"] is False


def test_notions_drive_library_memory_and_sandbox_are_not_controllers():
    assets = _j("config/PERSISTENT_ASSET_PROFILE.json")
    items = assets["non_authority_assets"]
    assert {"CHAT", "MEMORY", "CUSTOM_INSTRUCTIONS", "NOTION", "GOOGLE_DRIVE",
            "LIBRARY", "AUTOMATION", "GMAIL", "TEMP_SANDBOX"} <= {i["surface"] for i in items}
    assert all(item["role"] != "AUTHORITY" and item["lifecycle"] != "CURRENT" for item in items)
    assert assets["storage_reconciliation_rule"].startswith("For each new chat/Work session")
    assert "NOT_PHYSICALLY_INTERCEPTED" in assets["independent_acceptance_boundary"]


def test_history_and_other_assets_cannot_steal_business_authority():
    assets = _j("config/PERSISTENT_ASSET_PROFILE.json")
    entries = {i["asset_id"]: i for i in assets["non_authority_assets"]}
    for key in ("notion-migrated-control-pages", "gdrive-migrated-financial-continuity"):
        assert entries[key]["role"] == "MIGRATED_HISTORY"
    assert entries["notion-financial-research-resources"]["role"] == "SHARED_RESEARCH_RESOURCE"
    assert entries["library-financial-outputs"]["role"] == "DELIVERY_HISTORY"
    assert entries["old-parent-watch"]["lifecycle"] == "UNVERIFIED_CURRENT"


def test_retired_parent_manifest_no_longer_required_for_standalone_runtime():
    manifest = _j("config/FINANCIAL_MANIFEST.json")
    assert manifest["controller"] == "FINANCIAL_WRITING_OWNER"
    assert manifest["provider_adapter"] == "financial_writing_agent.standalone_runtime"
    assert not (ROOT / "TASK_INDEX.json").exists()
