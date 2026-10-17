import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_financial_has_exactly_one_current_business_authority_and_it_is_github():
    profile = load("config/PERSISTENT_ASSET_PROFILE.json")
    current = profile["current_authority_assets"]
    assert len(current) == 1
    assert current[0]["surface"] == "GITHUB"
    assert current[0]["role"] == "AUTHORITY"
    assert current[0]["lifecycle"] == "CURRENT"
    assert current[0]["resource_ref"] == "github://D1traverser-debug/financial-writing-agent@main"
    assert profile["authority_cardinality"] == "EXACTLY_ONE_CURRENT_FINANCIAL_BUSINESS_AUTHORITY__GITHUB_MAIN"


def test_all_other_persistent_surfaces_are_explicitly_non_authoritative():
    profile = load("config/PERSISTENT_ASSET_PROFILE.json")
    assets = profile["non_authority_assets"]
    by_surface = {item["surface"] for item in assets}
    assert {"CHAT", "MEMORY", "CUSTOM_INSTRUCTIONS", "NOTION", "GOOGLE_DRIVE", "LIBRARY", "AUTOMATION", "GMAIL", "TEMP_SANDBOX"} <= by_surface
    assert all(item["role"] != "AUTHORITY" for item in assets)
    assert all(item["lifecycle"] != "CURRENT" for item in assets)


def test_migrated_control_surfaces_are_decommissioned_but_knowledge_and_deliveries_remain_typed():
    profile = load("config/PERSISTENT_ASSET_PROFILE.json")
    assets = {item["asset_id"]: item for item in profile["non_authority_assets"]}
    assert assets["notion-financial-migrated-control"]["lifecycle"] == "DECOMMISSIONED"
    assert assets["drive-financial-legacy-continuity"]["lifecycle"] == "DECOMMISSIONED"
    assert assets["library-financial-migrated-history"]["lifecycle"] == "DECOMMISSIONED"
    assert assets["notion-financial-knowledge"]["role"] == "SHARED_RESOURCE"
    assert assets["library-financial-deliveries"]["role"] == "DELIVERY_HISTORY"


def test_capability_profile_points_to_parent_policy_and_domain_profile_without_copying_parent_semantics():
    capability = load(".uaos/CAPABILITIES.json")
    profile = load("config/PERSISTENT_ASSET_PROFILE.json")
    assert capability["uaos_persistent_asset_policy_ref"] == profile["parent_policy_ref"]
    assert capability["domain_persistent_asset_profile_ref"] == "config/PERSISTENT_ASSET_PROFILE.json"
    assert capability["hosted_behavior_semantics"]["persistent_asset_governance"].startswith("CURRENT_UAOS_PERSISTENT_ASSET_POLICY")
    assert "does not copy or override UAOS" in profile["governing_rule"]


def test_no_financial_calendar_or_business_state_automation_is_invented():
    profile = load("config/PERSISTENT_ASSET_PROFILE.json")
    absent = {item["surface"]: item["status"] for item in profile["known_absent_or_unmanaged"]}
    assert absent["GOOGLE_CALENDAR"] == "NO_FINANCIAL_MANAGED_ASSET_OBSERVED"
    assert absent["AUTOMATION"] == "NO_FINANCIAL_BUSINESS_STATE_AUTOMATION_OBSERVED"


def test_native_chatgpt_storage_boundary_is_not_overclaimed():
    profile = load("config/PERSISTENT_ASSET_PROFILE.json")
    assert "NO_CHILD_REPOSITORY_PHYSICAL_INTERCEPTION" in profile["native_chatgpt_boundary"]
