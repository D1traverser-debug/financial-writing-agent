"""Financial-only architecture, file authority and reference-integrity audit."""
from __future__ import annotations
import json
from pathlib import Path
from financial_writing_agent.writing_kernel import validate_kernel
ROOT = Path(__file__).resolve().parents[1]
PRIMARY = "FINANCIAL_WRITING_OWNER"
REFERENCE_NAMES = ("research.md","knowledge.md","private_research.md","reader_value.md","market_explanation.md","audit.md","editorial.md","hooks.md","style.md","platforms.md","delivery.md","maintenance.md","proactive_resolution.md")
RETIRED_ARTIFACTS = (".uaos","CAOS_SKILL.md","UAOS_SKILL.md","FINANCIAL_SKILL.md","docs/CAOS_CHILD_INTERFACE.md","config/PERSISTENT_ASSET_PROFILE.json","config/retired_runtime_paths.json","scripts/retired_runtime_static_audit.py","tests/test_retired_runtime_absence.py","tests/test_uaos_cognition_evolution_inheritance.py","evals/FINANCIAL_UAOS_COGNITION_EVOLUTION_PRODUCT_AUDIT_2026-10-15.md","evals/PARENT_GUIDANCE_HANDOFF.md","evals/PARENT_GUIDANCE_HANDOFF_20261016_CROSS_BORDER_STALE_RESUME.md","evals/uaos_article_binding_2026-10-14.json","references")

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def require(value,message):
    if not value: raise SystemExit(message)

def main():
    needed=("config/CAOS_GOVERNANCE.json","CAOS_FINANCIAL_ENTRY.md","config/FINANCIAL_MANIFEST.json","config/FINANCIAL_CAPABILITIES.json","config/EXECUTION_CONTRACT.json","config/DATA_AUTHORITY.json","skills/financial-writing-agent/SKILL.md","docs/product_requirements.md","docs/architecture.md","docs/STANDALONE_INTERFACE.md","docs/SESSION_DRAFT_DELIVERY.md","financial_writing_agent/standalone_runtime.py","financial_writing_agent/current_admission.py","financial_writing_agent/owner_guard.py","financial_writing_agent/owner_lifecycle.py","financial_writing_agent/cognition_governance.py","financial_writing_agent/private_research.py","financial_writing_agent/story_quality.py","financial_writing_agent/claim_trace.py","financial_writing_agent/delivery_pipeline.py","evals/EVOLUTION_INDEX.json","evals/quality_regression.json","knowledge/METHOD_KNOWLEDGE_CATALOG.json")
    for path in needed: require((ROOT/path).is_file(),f"missing Financial source: {path}")
    governance,manifest,caps,contract,data=(load(x) for x in ("config/CAOS_GOVERNANCE.json","config/FINANCIAL_MANIFEST.json","config/FINANCIAL_CAPABILITIES.json","config/EXECUTION_CONTRACT.json","config/DATA_AUTHORITY.json"))
    plugin=load("config/CHATGPT_FINANCIAL_PLUGIN.json")
    plugin_release=manifest["client_skill_plugin"]
    require(plugin["plugin_id"]==plugin_release["plugin_id"] and plugin["release_id"]==plugin_release["release_id"] and plugin.get("version")==plugin_release["version"],"Financial ChatGPT plugin identity/release drift")
    require(manifest["controller"]==caps["owner"]==contract["authority"]["controller"]==PRIMARY,"Financial authority mismatch")
    caos=governance["governance"]
    require(caos["system"]=="CAOS" and caos["mode"]=="CHAT_GOVERNED_EXTERNAL","CAOS governance identity/mode mismatch")
    require(caos["runtime_dependency"] is False and caos["api_dependency"] is False and caos["source_mutation"]=="FORBIDDEN","CAOS runtime/API/source boundary drift")
    require(governance["execution_boundary"]["business_owner"]==PRIMARY and governance["execution_boundary"]["parent_task_identity"] is False and governance["execution_boundary"]["parent_business_state_mirror"] is False and governance["execution_boundary"]["runtime_upcall"] is False and governance["execution_boundary"]["caos_permission_grant"] is False,"CAOS business authority boundary drift")
    require(manifest["governance_authority"]=="CAOS_CHAT_GOVERNED_EXTERNAL" and manifest["governance_mode"]=="CHAT_GOVERNED_EXTERNAL" and manifest["governance_contract"]=="config/CAOS_GOVERNANCE.json" and manifest["governance_entrypoint"]=="CAOS_FINANCIAL_ENTRY.md","Financial manifest CAOS governance binding drift")
    require(caps["caos_governance_ref"]=="config/CAOS_GOVERNANCE.json" and caps["caos_governance_mode"]=="CHAT_GOVERNED_EXTERNAL__NO_RUNTIME_OR_API_DEPENDENCY","Financial capability CAOS binding drift")
    require(caps["source_of_cognition"]=="CAOS_EXTERNAL_CHAT_GOVERNANCE_WITH_FINANCIAL_OWNER_NATIVE_EVIDENCE_ADMISSIONS","Financial cognition authority drift")
    require(caps["independence_clause"]=="NO_EXTERNAL_PARENT_REPOSITORY_OR_CONTROLLER__HOSTED_FINANCIAL_PROVIDER_ACTION_IS_ONLY_THE_TRUSTED_TRANSPORT_AND_ADMISSION_ADAPTER","Financial standalone runtime boundary drift")
    require(contract["authority"]["governance_authority"]=="CAOS_CHAT_GOVERNED_EXTERNAL" and contract["authority"]["caos_governance_contract"]=="config/CAOS_GOVERNANCE.json","Financial execution contract CAOS binding drift")
    require(contract["governance"]["runtime_dependency"] is False and contract["governance"]["api_dependency"] is False,"Financial CAOS runtime/API dependency enabled")
    require(manifest["domain_id"]==caps["domain_id"]==contract["domain_id"]=="financial_writing","domain identity drift")
    require(manifest["skill_entrypoint"]==caps["entrypoint"]=="skills/financial-writing-agent/SKILL.md","Financial Skill entrypoint mismatch")
    require(manifest["data_authority"]==contract["authority"]["data_authority"]=="config/DATA_AUTHORITY.json","data authority pointer mismatch")
    require(manifest["state_authority"]==data["article_state_pattern"]=="workspaces/articles/{task_id}/STATE.json","Article Aggregate identity changed")
    require(manifest["provider_adapter"]=="financial_writing_agent.standalone_runtime","Financial reference adapter entry missing")
    native=manifest["chatgpt_native_runtime"]
    require(native["orchestrator"]=="CHATGPT_MODEL_WITH_FINANCIAL_SKILL" and native["persistence_provider"]=="FINANCIAL_HOSTED_PROVIDER_ACTION_USING_LEAST_PRIVILEGE_GITHUB_APP","native ChatGPT runtime/provider missing")
    require(native["requires_hosted_python_mcp"] is True and native["write_protocol"]=="GIT_BLOB_TREE_COMMIT_UPDATE_REF_EXPECTED_SHA__OWNER_STATE_OR_METHOD_CATALOG_AND_SIGNED_EFFECT_RECEIPT_ATOMIC_BUNDLE","native provider CAS contract drift")
    require(manifest["external_parent_required"] is False and manifest["external_host_required"] is True and manifest["provider_action_required"] is True,"Financial-owned provider host requirement drift")
    require(manifest["external_host_required_scope"]=="CANONICAL_OWNER_STATE_AND_METHOD_CATALOG_MUTATIONS_ONLY" and manifest["provider_action_required_scope"]=="CANONICAL_OWNER_STATE_AND_METHOD_CATALOG_MUTATIONS_ONLY","Provider host scope broadened beyond canonical mutations")
    require(manifest["chatgpt_native_runtime"]["session_draft_delivery_without_provider"] is True,"session-only draft delivery route missing")
    session_guide=(ROOT/"docs/SESSION_DRAFT_DELIVERY.md").read_text(encoding="utf-8")
    require("SESSION_DRAFT_DELIVERED__NONCANONICAL__NOT_PUBLICATION_CERTIFIED" in session_guide and "PUBLICATION_CERTIFICATION" in session_guide,"session delivery guide assurance boundary missing")
    require((ROOT/"skills/financial-writing-agent/SKILL.md").stat().st_size<=12000,"Financial operating Skill exceeds 12,000-byte delivery limit")
    modes=contract["execution_modes"]
    require(modes["SESSION_DRAFT_DELIVERY"]["provider_action_required"] is False and modes["SESSION_DRAFT_DELIVERY"]["canonical_article_state_mutation_allowed"] is False and modes["SESSION_DRAFT_DELIVERY"]["method_catalog_mutation_allowed"] is False,"session draft delivery acquired canonical mutation authority")
    require(modes["CANONICAL_OWNER_EXECUTION"]["provider_action_required"] is True and modes["CANONICAL_OWNER_EXECUTION"]["signed_action_and_effect_receipts_required"] is True,"canonical provider/effect boundary weakened")
    require(caps["execution_mode_scopes"]["SESSION_DRAFT_DELIVERY"]["provider_action_required"] is False and caps["execution_mode_scopes"]["CANONICAL_OWNER_EXECUTION"]["provider_action_required"] is True,"capability execution-mode scope drift")
    require(manifest["provider_action_endpoint"]["protocol"]=="MCP_OVER_HTTPS" and manifest["provider_action_endpoint"]["status"]=="NOT_DEPLOYED","Financial provider endpoint deployment state drift")
    require(caps["independent_parent_free"] is True and caps["independence_clause"]=="NO_EXTERNAL_PARENT_REPOSITORY_OR_CONTROLLER__HOSTED_FINANCIAL_PROVIDER_ACTION_IS_ONLY_THE_TRUSTED_TRANSPORT_AND_ADMISSION_ADAPTER","external runtime dependency declared")
    require(contract["execution"]["route_selection"]=="DIRECT_FINANCIAL_ONLY" and contract["execution"]["direct_domain_activation"] is True,"execution is no longer direct Financial")
    require(contract["authority"]["alternate_business_state_authority_allowed"] is False,"second business-state authority slipped in")
    require(data["business_authority"]=="github://D1traverser-debug/financial-writing-agent@main","canonical business authority changed")
    require(data["method_catalog"]=="knowledge/METHOD_KNOWLEDGE_CATALOG.json" and data["system_evolution"]=="evals/EVOLUTION_INDEX.json","method/evolution authority drift")
    require(data["no_parallel_article_ledger"] is True and data["no_external_parent_runtime"] is True,"parallel state or external parent runtime enabled")
    for relative in RETIRED_ARTIFACTS: require(not (ROOT/relative).exists(),f"retired Financial artifact remains: {relative}")
    skill=(ROOT/manifest["skill_entrypoint"]).read_text(encoding="utf-8")
    for marker in ("Independent Operating Skill","CAOS_FINANCIAL_ENTRY.md","CAOS governance","Decision Loop","Execution Loop","PrivateResearchBrief","FINANCE_DEEP_DOCX","FINANCE_BROAD_DOCX","standalone_runtime.py","no runtime/API dependency or permission authority","article","originality","create_blob","create_tree","create_commit","update_ref","expected_sha","fetch_file","SESSION_DRAFT_DELIVERY"): require(marker.lower() in skill.lower(),f"operating Skill lacks Financial duty/runtime protocol: {marker}")
    from financial_writing_agent.standalone_runtime import DOMAIN_ID,OPERATIONS
    require(DOMAIN_ID=="financial_writing","Financial standalone module domain drift")
    require({"CREATE_ARTICLE","ADVANCE_STAGE","CHANGE_REQUIREMENTS","ATTACH_FEEDBACK","RESUME_BLOCKED","RECORD_PROACTIVE_RESOLUTION","REVIEW_SYSTEM_IMPACT"}<=OPERATIONS,"owner mutation operations incomplete")
    require(validate_kernel()==[],"Financial writing-pass graph invalid")
    ids=[x["id"] for x in caps["capabilities"]]
    require(len(ids)==len(set(ids)) and len(ids)>=8,"Financial capabilities missing or duplicated")
    package_refs=ROOT/"financial_writing_agent/resources/references";skill_refs=ROOT/"skills/financial-writing-agent/references"
    for name in REFERENCE_NAMES: require((package_refs/name).read_bytes()==(skill_refs/name).read_bytes(),f"Financial reference mirror drift: {name}")
    print("PASS: one Financial business Skill, CAOS external chat governance, one article-state authority, one method catalog, two synchronized reference surfaces, no retired runtime artifacts")

if __name__=="__main__": main()
