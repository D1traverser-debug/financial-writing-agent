import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_financial_manifest_and_capabilities_bind_common_behavior_1_3():
    manifest = load(".uaos/MANIFEST.json")
    caps = load(".uaos/CAPABILITIES.json")
    assert manifest["binding"]["common_behavior_assurance_min"] == "1.3.0"
    assert manifest["domain_authority"]["root_scope_action_admission"] == "financial_writing_agent/problem_action_admission.py"
    assert manifest["domain_authority"]["canonical_evolution_evidence"] == "evals/EVOLUTION_INDEX.json"
    assert caps["profile_version"] >= 19
    assert caps["uaos_common_behavior_assurance_contract_min"] == "1.3.0"
    assert caps["canonical_evolution_evidence_ref"] == "evals/EVOLUTION_INDEX.json"
    by_id = {row["capability_id"]: row for row in caps["capabilities"]}
    assert "cognition_governance_admission" in by_id
    assert "problem_root_scope_and_action_admission" in by_id
    assert "DecisionEnvelope" in " ".join(by_id["problem_root_scope_and_action_admission"]["required"])
    assert "ROOT_SCOPE" in caps["hosted_behavior_semantics"]["root_scope_admission"]
    assert "TYPED_DECISION_ENVELOPE_EVOLUTION_DISPOSITION" in caps["hosted_behavior_semantics"]["evolution_before_action"]


def test_financial_skill_preserves_existing_cognition_and_adds_root_scope_bridge():
    skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    assert "Common Behavior 1.3" in skill
    assert "DecisionEnvelope` remains" in skill
    assert "financial_writing_agent.problem_action_admission" in skill
    assert "RootScopeReceipt" in skill
    assert "invented support refs fail admission" in skill
    assert "evals/EVOLUTION_INDEX.json" in skill


def test_evolution_index_tracks_owner_native_1_3_adoption_without_rewriting_history():
    index = load("evals/EVOLUTION_INDEX.json")
    assert index["owner"] == "DOMAIN:financial_writing"
    assert index["common_behavior_assurance_min"] == "1.3.0"
    assert "F-20261016-COMMON-BEHAVIOR-1-3-ROOT-SCOPE-ADOPTION" in index["current_open_items"]
    historical = set(index["historical_evidence_refs"])
    assert "evals/COGNITION_GOVERNANCE_AUDIT.json" in historical
    assert "evals/OWNER_SESSION_LIFECYCLE_AUDIT.json" in historical
    assert "evals/PROACTIVE_RESOLUTION_AUDIT.json" in historical
