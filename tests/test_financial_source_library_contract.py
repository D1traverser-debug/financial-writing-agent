import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_google_drive_source_library_is_canonical_and_does_not_need_private_github():
    contract = load("config/SOURCE_STORAGE_CONTRACT.json")
    data = load("config/DATA_AUTHORITY.json")
    manifest = load("config/FINANCIAL_MANIFEST.json")
    execution = load("config/EXECUTION_CONTRACT.json")

    assert contract["canonical_store"]["metadata_and_lifecycle_authority"]["provider"] == "GOOGLE_DRIVE"
    assert contract["canonical_store"]["registry_tabs"] == ["Sources", "Versions", "Events"]
    assert contract["canonical_store"]["repository_visibility"] == "OWNER_ACCEPTED_PUBLIC__NO_CHANGE_REQUESTED"
    assert contract["canonical_store"]["no_parallel_source_metadata_ledger"] is True
    assert contract["canonical_store"]["no_parallel_article_ledger"] is True
    assert contract["identity"]["drive_revision_id_required"] is False
    assert data["source_library"]["provider"] == "GOOGLE_DRIVE"
    assert data["article_state_pattern"] == "workspaces/articles/{task_id}/STATE.json"
    assert data["method_catalog"] == "knowledge/METHOD_KNOWLEDGE_CATALOG.json"
    assert manifest["source_library"]["status"].startswith("PROVISIONED_EMPTY")
    assert manifest["provider_action_endpoint"]["status"] == "NOT_DEPLOYED"
    session = execution["execution_modes"]["SESSION_DRAFT_DELIVERY"]
    assert session["source_library_crud_allowed"] is True
    assert session["canonical_article_state_mutation_allowed"] is False
    assert session["method_catalog_mutation_allowed"] is False
    assert session["source_library_does_not_authorize_article_state_or_method_mutation"] is True


def test_no_live_private_drive_identifiers_are_committed_to_the_public_repository():
    paths = [
        "config/SOURCE_STORAGE_CONTRACT.json",
        "config/DATA_AUTHORITY.json",
        "config/FINANCIAL_MANIFEST.json",
        "config/FINANCIAL_CAPABILITIES.json",
        "config/EXECUTION_CONTRACT.json",
        "docs/FINANCIAL_SOURCE_LIBRARY.md",
        "skills/financial-writing-agent/SKILL.md",
    ]
    forbidden = (
        "1l9STZjrrqg37_qKrBcKZ2zRkjC7pM0MQ",
        "12mFmuL7yiMwWv6uDkt_daGa8srtaefOrNSzlgZq4DG4",
        "1XOJW7et3VZIGx4YRTUcKHuoSZt6CSIAa",
    )
    for path in paths:
        content = (ROOT / path).read_text(encoding="utf-8")
        assert all(value not in content for value in forbidden)


def test_source_registry_has_no_parallel_article_bindings_tab():
    contract = load("config/SOURCE_STORAGE_CONTRACT.json")
    assert "Bindings" not in contract["canonical_store"]["registry_tabs"]
    assert "task_bindings" in contract["registry"]
    assert "Article Aggregate" in contract["registry"]["task_bindings"]


def test_skill_router_stays_under_delivery_limit_and_exposes_drive_source_library():
    skill = (ROOT / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    assert len(skill.encode("utf-8")) <= 12000
    assert "financial-source://" in skill
    assert "docs/FINANCIAL_SOURCE_LIBRARY.md" in skill
    assert "Google Drive" in skill
