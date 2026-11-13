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
    needed=("config/FINANCIAL_MANIFEST.json","config/FINANCIAL_CAPABILITIES.json","config/EXECUTION_CONTRACT.json","config/DATA_AUTHORITY.json","skills/financial-writing-agent/SKILL.md","docs/product_requirements.md","docs/architecture.md","docs/STANDALONE_INTERFACE.md","financial_writing_agent/standalone_runtime.py","financial_writing_agent/current_admission.py","financial_writing_agent/owner_guard.py","financial_writing_agent/owner_lifecycle.py","financial_writing_agent/cognition_governance.py","financial_writing_agent/private_research.py","financial_writing_agent/story_quality.py","financial_writing_agent/claim_trace.py","financial_writing_agent/delivery_pipeline.py","evals/EVOLUTION_INDEX.json","evals/quality_regression.json","knowledge/METHOD_KNOWLEDGE_CATALOG.json")
    for path in needed: require((ROOT/path).is_file(),f"missing Financial source: {path}")
    manifest,caps,contract,data=(load(x) for x in ("config/FINANCIAL_MANIFEST.json","config/FINANCIAL_CAPABILITIES.json","config/EXECUTION_CONTRACT.json","config/DATA_AUTHORITY.json"))
    plugin=load("config/CHATGPT_FINANCIAL_PLUGIN.json")
    plugin_release=manifest["client_skill_plugin"]
    require(plugin["plugin_id"]==plugin_release["plugin_id"] and plugin["release_id"]==plugin_release["release_id"] and plugin.get("version")==plugin_release["version"],"Financial ChatGPT plugin identity/release drift")
    require(manifest["controller"]==caps["owner"]==contract["authority"]["controller"]==PRIMARY,"Financial authority mismatch")
    require(manifest["domain_id"]==caps["domain_id"]==contract["domain_id"]=="financial_writing","domain identity drift")
    require(manifest["skill_entrypoint"]==caps["entrypoint"]=="skills/financial-writing-agent/SKILL.md","Financial Skill entrypoint mismatch")
    require(manifest["data_authority"]==contract["authority"]["data_authority"]=="config/DATA_AUTHORITY.json","data authority pointer mismatch")
    require(manifest["state_authority"]==data["article_state_pattern"]=="workspaces/articles/{task_id}/STATE.json","Article Aggregate identity changed")
    require(manifest["provider_adapter"]=="financial_writing_agent.standalone_runtime","Financial reference adapter entry missing")
    native=manifest["chatgpt_native_runtime"]
    require(native["orchestrator"]=="CHATGPT_MODEL_WITH_FINANCIAL_SKILL" and native["persistence_provider"]=="CONNECTED_USER_GITHUB_CONNECTOR","native ChatGPT runtime/provider missing")
    require(native["requires_hosted_python_mcp"] is False and native["write_protocol"]=="GIT_BLOB_TREE_COMMIT_UPDATE_REF_EXPECTED_SHA","native GitHub CAS contract drift")
    require(manifest["external_parent_required"] is False and manifest["external_host_required"] is False,"external parent/Host became mandatory")
    require(caps["independent_parent_free"] is True and caps["independence_clause"]=="NO_EXTERNAL_PARENT_REPOSITORY_OR_HOST_INVOCATION","external runtime dependency declared")
    require(contract["execution"]["route_selection"]=="DIRECT_FINANCIAL_ONLY" and contract["execution"]["direct_domain_activation"] is True,"execution is no longer direct Financial")
    require(contract["authority"]["alternate_business_state_authority_allowed"] is False,"second business-state authority slipped in")
    require(data["business_authority"]=="github://D1traverser-debug/financial-writing-agent@main","canonical business authority changed")
    require(data["method_catalog"]=="knowledge/METHOD_KNOWLEDGE_CATALOG.json" and data["system_evolution"]=="evals/EVOLUTION_INDEX.json","method/evolution authority drift")
    require(data["no_parallel_article_ledger"] is True and data["no_external_parent_runtime"] is True,"parallel state or external parent runtime enabled")
    for relative in RETIRED_ARTIFACTS: require(not (ROOT/relative).exists(),f"retired Financial artifact remains: {relative}")
    skill=(ROOT/manifest["skill_entrypoint"]).read_text(encoding="utf-8")
    for marker in ("Independent Operating Skill","Decision Loop","Execution Loop","PrivateResearchBrief","FINANCE_DEEP_DOCX","FINANCE_BROAD_DOCX","standalone_runtime.py","no external parent","article","originality","create_blob","create_tree","create_commit","update_ref","expected_sha","fetch_file"): require(marker.lower() in skill.lower(),f"operating Skill lacks Financial duty/runtime protocol: {marker}")
    from financial_writing_agent.standalone_runtime import DOMAIN_ID,OPERATIONS
    require(DOMAIN_ID=="financial_writing","Financial standalone module domain drift")
    require({"CREATE_ARTICLE","ADVANCE_STAGE","CHANGE_REQUIREMENTS","ATTACH_FEEDBACK","RESUME_BLOCKED","RECORD_PROACTIVE_RESOLUTION","REVIEW_SYSTEM_IMPACT"}<=OPERATIONS,"owner mutation operations incomplete")
    require(validate_kernel()==[],"Financial writing-pass graph invalid")
    ids=[x["id"] for x in caps["capabilities"]]
    require(len(ids)==len(set(ids)) and len(ids)>=8,"Financial capabilities missing or duplicated")
    package_refs=ROOT/"financial_writing_agent/resources/references";skill_refs=ROOT/"skills/financial-writing-agent/references"
    for name in REFERENCE_NAMES: require((package_refs/name).read_bytes()==(skill_refs/name).read_bytes(),f"Financial reference mirror drift: {name}")
    print("PASS: one Financial Skill, one article-state authority, one method catalog, two synchronized reference surfaces, no retired parent artifacts")

if __name__=="__main__": main()
