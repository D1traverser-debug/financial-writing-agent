"""Financial data authority and Drive-backed source-storage contract stay explicit and fail closed."""
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
    assert data["source_library"]["raw_object_provider"] == "GOOGLE_DRIVE"
    assert data["source_library"]["metadata_authority"] == "sources/{source_id}/SOURCE.json"
    assert data["source_library"]["task_binding"] == (
        "workspaces/articles/{task_id}/research/SOURCE_BINDINGS.json"
    )
    assert data["no_parallel_article_ledger"] is True
    assert data["no_parallel_source_metadata_ledger"] is True
    assert data["no_external_parent_runtime"] is True


def test_private_repository_gate_and_drive_source_folder_are_explicit():
    data = _json("config/DATA_AUTHORITY.json")
    security = data["repository_security"]
    source = data["source_library"]

    assert security["required_visibility"] == "PRIVATE"
    assert security["observed_visibility_at_2026_11_19"] == "PUBLIC"
    assert security["canonical_private_data_writes"].startswith("BLOCKED_UNTIL_PRIVATE")
    assert security["preserve_existing_git_history"] is True
    assert security["do_not_add_private_source_metadata_or_task_bindings_while_public"] is True
    assert source["raw_folder_path"] == "ChatGPT/Financial Writing Agent/00_Source_Library"
    assert source["raw_folder_id_ref"] == "REQUIRED_PRIVATE_PROVIDER_CONFIGURATION:FINANCIAL_SOURCE_DRIVE_FOLDER_ID"
    assert source["raw_folder_visibility"] == "PRIVATE_VERIFIED_NOT_SHARED_2026_11_19"
    assert source["status"] == "FOLDER_PROVISIONED__DOMAIN_TRANSITIONS_IMPLEMENTED__SOURCE_PROVIDER_NOT_DEPLOYED"
    assert data["operations"]["source_create"].startswith("BLOCKED")


def test_article_workspace_binds_exact_source_versions_without_duplicate_ledger():
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


def test_manifest_capabilities_and_execution_contract_bind_drive_source_adapter():
    manifest = _json("config/FINANCIAL_MANIFEST.json")
    capabilities = _json("config/FINANCIAL_CAPABILITIES.json")
    execution = _json("config/EXECUTION_CONTRACT.json")

    assert manifest["source_storage_contract"] == "config/SOURCE_STORAGE_CONTRACT.json"
    assert manifest["chatgpt_native_runtime"]["persistence_provider"] == (
        "FINANCIAL_HOSTED_PROVIDER_ACTION_USING_LEAST_PRIVILEGE_GITHUB_APP"
    )
    assert manifest["chatgpt_native_runtime"]["source_provider"].endswith(
        "GOOGLE_DRIVE_SOURCE_ADAPTER"
    )
    assert manifest["chatgpt_native_runtime"]["source_crud_status"].startswith("DOMAIN_MODELS_AND_TRANSITIONS_IMPLEMENTED")
    assert manifest["chatgpt_native_runtime"]["source_domain_model"] == "financial_writing_agent.source_lifecycle"
    source_receipt = manifest["provider_action_effect_receipt"]["source_asset_contract"]
    assert source_receipt["task_binding_set"]["schema"] == (
        "financial_writing_agent.source_lifecycle.SourceBindingSet"
    )
    assert source_receipt["task_binding_set"]["exact_evidence_ref_coverage_required"] is True
    assert source_receipt["task_binding_set"]["source_ref_collector"] == (
        "financial_writing_agent.source_lifecycle.collect_research_source_refs"
    )
    assert set(source_receipt["task_binding_set"]["coverage_artifacts"]) == {
        "DecisionEnvelope", "PrivateResearchBrief", "ResearchPackage",
    }
    assert manifest["provider_action_endpoint"]["source_store_connector"].startswith("CONNECTED_GOOGLE_DRIVE")
    assert set(manifest["provider_action_endpoint"]["required_for"]) == {
        "CANONICAL_ARTICLE_STATE_CREATE_OR_ADVANCE",
        "CANONICAL_REQUIREMENT_MUTATION",
        "METHOD_CATALOG_MUTATION",
        "SIGNED_CANONICAL_ACTION_AND_EFFECT_RECEIPTS",
        "SOURCE_FILE_CRUD__DRIVE_OBJECT_READBACK__GITHUB_SOURCE_METADATA_AND_EFFECT_CAS",
    }
    source_capability = next(
        item for item in capabilities["capabilities"]
        if item["id"] == "versioned_source_file_crud_and_drive_readback"
    )
    assert source_capability["assurance"].startswith("DOMAIN_MODELS_AND_TRANSITIONS_IMPLEMENTED")
    assert "CONNECTED_GOOGLE_DRIVE_ACCESS_TO_PRIVATE_FINANCIAL_SOURCE_FOLDER" in (
        capabilities["required_external_capabilities_at_execution"]
    )
    assert "EXACT_SOURCE_BINDING_SET_COVERAGE_AGAINST_PRIVATE_RESEARCH_BRIEF_AND_RESEARCH_PACKAGE" in (
        capabilities["required_provider_action_requirements"]
    )
    assert execution["authority"]["source_storage_contract"] == (
        "config/SOURCE_STORAGE_CONTRACT.json"
    )
    assert execution["chatgpt_native_execution"]["persistence_provider"] == (
        "FINANCIAL_HOSTED_PROVIDER_ACTION_USING_LEAST_PRIVILEGE_GITHUB_APP"
    )
    assert execution["chatgpt_native_execution"]["source_provider"].endswith(
        "GOOGLE_DRIVE_SOURCE_ADAPTER"
    )
    assert execution["chatgpt_native_execution"]["source_file_crud_status"] == "NOT_DEPLOYED"
    source_mutation = execution["standalone_governance"]["source_file_mutation"]
    assert source_mutation["status"].startswith("DOMAIN_MODELS_AND_TRANSITIONS_IMPLEMENTED")
    assert source_mutation["domain_model_module"] == "financial_writing_agent.source_lifecycle"
    assert source_mutation["planned_entrypoint"] == "financial_writing_agent.source_provider.admit_source_action"
    assert source_mutation["planned_provider_entrypoint"] == "financial_writing_agent.source_provider.admit_source_action"
    assert source_mutation["task_binding_schema"] == (
        "financial_writing_agent.source_lifecycle.SourceBindingSet"
    )
    assert source_mutation["exact_evidence_ref_coverage_required"] is True
    assert source_mutation["source_ref_collector"] == (
        "financial_writing_agent.source_lifecycle.collect_research_source_refs"
    )


def test_drive_source_storage_contract_defines_versioned_crud_and_fail_closed_provider():
    contract = _json("config/SOURCE_STORAGE_CONTRACT.json")

    assert contract["domain_id"] == "financial_writing"
    assert contract["status"].startswith("DOMAIN_MODELS_AND_TRANSITIONS_IMPLEMENTED")
    assert contract["domain_model_module"] == "financial_writing_agent.source_lifecycle"
    assert set(contract["domain_model_functions"]) == {
        "create_source_record", "append_source_version", "retire_source",
        "restore_source", "bind_source_version", "validate_source_binding_coverage",
        "collect_research_source_refs",
    }
    assert set(contract["domain_model_types"]) == {
        "DriveObjectReference", "SourceVersion", "SourceRecord",
        "SourceBinding", "SourceBindingSet",
    }
    assert contract["task_binding"]["schema"] == (
        "financial_writing_agent.source_lifecycle.SourceBindingSet"
    )
    assert "scope" in contract["task_binding"]["fields"]
    assert "rights_basis" in contract["task_binding"]["fields"]
    assert "source_task_id" in contract["task_binding"]["fields"]
    assert "exact equality" in contract["research_admission"]["exact_coverage_rule"]
    assert set(contract["research_admission"]["source_ref_collector"]["artifacts"]) == {
        "DecisionEnvelope", "PrivateResearchBrief", "ResearchPackage",
    }
    assert "prior_knowledge_refs" in contract["research_admission"]["source_ref_collector"]["excludes"]
    assert contract["canonical_store"]["raw_object_store"]["provider"] == "GOOGLE_DRIVE"
    assert contract["canonical_store"]["raw_object_store"]["folder_id_ref"] == (
        "REQUIRED_PRIVATE_PROVIDER_CONFIGURATION:FINANCIAL_SOURCE_DRIVE_FOLDER_ID"
    )
    assert contract["canonical_store"]["metadata_and_lifecycle_authority"]["provider"] == "GITHUB"
    assert contract["canonical_store"]["repository_visibility_required"] == "PRIVATE"
    assert contract["paths"]["drive_source_root"] == (
        "ChatGPT/Financial Writing Agent/00_Source_Library/"
    )
    assert contract["paths"]["github_source_record"] == "sources/{source_id}/SOURCE.json"
    assert contract["paths"]["article_task_binding"] == (
        "workspaces/articles/{task_id}/research/SOURCE_BINDINGS.json"
    )
    assert contract["identity"]["reference_scheme"] == (
        "financial-source://{source_id}/{version_id}"
    )
    assert contract["identity"]["latest_version_alias_allowed"] is False
    assert contract["version_contract"]["one_new_drive_file_per_immutable_source_version"] is True
    assert contract["version_contract"]["overwrite_existing_drive_version_forbidden"] is True
    assert "exact immutable Drive file payload" in contract["version_contract"]["raw_sha256_semantics"]
    assert "only when storage_policy=RAW_PRESERVED" in contract["version_contract"]["raw_sha256_semantics"]
    assert "not an unretained full source body" in contract["version_contract"]["normalized_text_sha256_semantics"]
    assert "permitted excerpts/metadata" in contract["crud"]["create"]
    assert "Do not imply full-source verification" in contract["crud"]["read"]
    assert set(contract["crud"]) == {
        "create", "read", "update", "delete", "list_search",
    }
    assert "RETIRE" in contract["crud"]["delete"]
    assert "new Drive file" in contract["crud"]["update"]
    assert "exact" in contract["crud"]["read"].lower()
    assert "list_sources" in contract["provider_surface"]["read_only"]
    assert "observe_source" in contract["provider_surface"]["read_only"]
    assert "read_source_version" in contract["provider_surface"]["read_only"]
    assert "admit_source_action" in contract["provider_surface"]["owner_mutations"]
    assert contract["source_reader"]["current_status"] == (
        "NO_DRIVE_SOURCE_RESOLVER_OR_SOURCE_CRUD_PROVIDER_IS_DEPLOYED"
    )
    assert "not the source CRUD manager" in contract["source_reader"]["verifier_role"]
    assert "Do not copy full copyrighted articles by default" in (
        contract["rights_and_retention"]["news_or_paywalled_material"]
    )
    assert "news-reading scripts" in contract["input_boundary"]["excluded_by_default"]
    assert "Word document merge inputs" in contract["input_boundary"]["excluded_by_default"]
    admission = contract["research_admission"]
    assert admission["canonical_evidence_reference_scheme"] == (
        "financial-source://{source_id}/{version_id}"
    )
    assert admission["raw_url_semantics"].startswith("DISCOVERY_OR_CITATION_METADATA_ONLY")
    assert admission["no_unbound_evidence"] is True
    assert admission["no_floating_latest_reference"] is True
    assert "exact equality" in admission["exact_coverage_rule"]
    assert "SOURCE_BINDINGS.json" in admission["exact_coverage_rule"]
    assert "raw external URLs used as admitted research evidence refs" in admission["provider_must_reject"]
    assert "TaskContract.source_refs may contain user-supplied discovery URLs" in (
        admission["compatibility_boundary"]
    )
