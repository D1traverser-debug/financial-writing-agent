"""Financial data authority and source-storage contract stay explicit and fail closed."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_data_authority_has_one_business_state_method_store_and_source_contract():
    data = _json("config/DATA_AUTHORITY.json")
    manifest = _json("config/FINANCIAL_MANIFEST.json")

    assert data["domain_id"] == manifest["domain_id"] == "financial_writing"
    assert data["business_authority"] == "github://D1traverser-debug/financial-writing-agent@main"
    assert data["article_state_pattern"] == manifest["state_authority"]
    assert data["method_catalog"] == "knowledge/METHOD_KNOWLEDGE_CATALOG.json"
    assert data["system_evolution"] == "evals/EVOLUTION_INDEX.json"
    assert data["source_storage_contract"] == "config/SOURCE_STORAGE_CONTRACT.json"
    assert data["source_library"]["root"] == "sources/"
    assert data["source_library"]["task_binding"] == (
        "workspaces/articles/{task_id}/research/SOURCE_BINDINGS.json"
    )
    assert data["no_parallel_article_ledger"] is True
    assert data["no_parallel_source_ledger"] is True
    assert data["no_external_parent_runtime"] is True


def test_private_repository_gate_blocks_source_writes_until_verified():
    data = _json("config/DATA_AUTHORITY.json")
    security = data["repository_security"]

    assert security["required_visibility"] == "PRIVATE"
    assert security["observed_visibility_at_2026_11_19"] == "PUBLIC"
    assert security["canonical_private_data_writes"].startswith("BLOCKED_UNTIL_PRIVATE")
    assert security["preserve_existing_git_history"] is True
    assert security["do_not_add_private_source_originals_while_public"] is True
    assert data["source_library"]["status"].startswith("DESIGNED_NOT_ACTIVE")
    assert data["operations"]["source_create"].startswith("BLOCKED")


def test_article_workspace_binds_exact_source_versions_without_duplicate_store():
    data = _json("config/DATA_AUTHORITY.json")

    assert data["article_workspace"]["state"] == "STATE.json"
    assert set(data["article_workspace"]) == {
        "state", "research", "source_bindings", "editorial",
        "stage_outputs", "reviews", "delivery", "feedback",
    }
    assert data["article_workspace"]["source_bindings"] == "research/SOURCE_BINDINGS.json"
    assert "append-only history" in data["operations"]["update"]
    assert "Do not erase historical receipts" in data["operations"]["delete"]
    assert "actual DOCX" in data["operations"]["delivery"]


def test_source_storage_contract_defines_versioned_crud_and_fail_closed_provider():
    contract = _json("config/SOURCE_STORAGE_CONTRACT.json")

    assert contract["domain_id"] == "financial_writing"
    assert contract["status"].startswith("DESIGN_ONLY__BLOCKED")
    assert contract["canonical_store"]["required_repository_visibility"] == "PRIVATE"
    assert contract["canonical_store"]["no_external_fallback"] is True
    assert contract["paths"]["source_root"] == "sources/"
    assert contract["paths"]["source_record"] == "sources/{source_id}/SOURCE.json"
    assert contract["paths"]["task_binding"] == (
        "workspaces/articles/{task_id}/research/SOURCE_BINDINGS.json"
    )
    assert contract["identity"]["reference_scheme"] == (
        "financial-source://{source_id}/{version_id}"
    )
    assert contract["identity"]["latest_version_alias_allowed"] is False
    assert contract["version_contract"]["immutable_version_payload"] is True
    assert contract["version_contract"]["overwriting_an_existing_version_forbidden"] is True
    assert set(contract["crud"]) == {
        "create", "read", "update", "delete", "list_search",
    }
    assert "RETIRE" in contract["crud"]["delete"]
    assert "append" in contract["crud"]["update"]
    assert "exact" in contract["crud"]["read"].lower()
    assert "list_sources" in contract["provider_surface"]["read_only"]
    assert "observe_source" in contract["provider_surface"]["read_only"]
    assert "read_source_version" in contract["provider_surface"]["read_only"]
    assert "admit_source_action" in contract["provider_surface"]["owner_mutations"]
    assert contract["source_reader"]["current_status"] == (
        "NO_SOURCE_RESOLVER_OR_SOURCE_CRUD_PROVIDER_IS_DEPLOYED"
    )
    assert "not the source CRUD manager" in contract["source_reader"]["verifier_role"]
    assert "Do not copy full copyrighted articles by default" in (
        contract["rights_and_retention"]["news_or_paywalled_material"]
    )
