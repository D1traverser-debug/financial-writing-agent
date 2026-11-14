"""Owner-scoped, current-source whole-product assurance: no acceptance by file presence."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from financial_writing_agent.whole_system_assurance import (
    REQUIRED_PRODUCT_REQUIREMENTS,
    _git_blob_sha,
    inspect_active_article,
    project_whole_system, audit_repository_business_changes,
)
from financial_writing_agent.current_admission import build_initial_state
from financial_writing_agent.provider_attestation import payload_sha256, request_sha256
from trusted_provider_testkit import signed_action_authorization, signed_action_effect

ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40
TASK = "cross-border-ecommerce-20261016-v3"


def _copy_project(tmp_path):
    # Exact current repo snapshots, not invented "green" Article states.
    shutil.copytree(
        ROOT, tmp_path / "repo",
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache",
                                    ".coverage", "audit", "dist", "*.pyc"),
    )
    return tmp_path / "repo"


def test_current_project_has_single_canonical_owner_and_all_19_requirement_pointers():
    result = project_whole_system(ROOT, head_sha=HEAD)
    assert len(REQUIRED_PRODUCT_REQUIREMENTS) == 19
    assert result["product_requirement_total"] == 19
    assert set(result["product_requirement_traces"]) == REQUIRED_PRODUCT_REQUIREMENTS
    assert all(item["missing_pointers"] == [] for item in result["product_requirement_traces"].values())
    assert all(item["independent_business_outcome"] == "NOT_VERIFIED"
               for item in result["product_requirement_traces"].values())
    assert result["structural_violations"] == []
    assert result["method_catalog"]["record_count"] >= 1
    assert len(result["open_system_gates"]) == 7
    assert result["whole_product_status"].startswith("NOT_READY")
    assert result["next_legal_step"] == "CLOSE_AUTHENTICATED_EXECUTION_PATH_AND_INDEPENDENT_BUSINESS_EVIDENCE__NO_UNREQUESTED_ARTICLE_PRODUCTION"


def test_real_cross_border_v3_is_research_0_of_4_not_a_completed_article():
    report = project_whole_system(ROOT, head_sha=HEAD)
    live = [a for a in report["current_articles"] if a["task_id"] == TASK]
    assert len(live) == 1
    state = live[0]
    assert state["status"] == "IN_PROGRESS"
    assert state["stage"] == "RESEARCH"
    assert state["required_output_count"] == 4
    assert state["recorded_output_count"] == 0
    assert {"full_universe_research_pool", "deep_complete_retained_universe"} == set(
        state["active_task_requirement_ids"]
    )
    assert all(ref["locally_available"] for ref in state["source_readbacks"])
    assert any(x["obligation"] == "private_research_brief" for x in state["open_obligations"])
    assert state["business_outcome"].startswith("NOT_READY")
    assert "cross-border-ecommerce-20261016-v2" in report["historical_article_ids"]


def test_root_cause_probe_detects_plugin_and_policy_mirror_drift_in_one_pass(tmp_path):
    work = _copy_project(tmp_path)
    config = work / "config/CHATGPT_FINANCIAL_PLUGIN.json"
    obj = json.loads(config.read_text(encoding="utf-8"))
    obj["release_id"] = "pluginrel_wrong"
    config.write_text(json.dumps(obj), encoding="utf-8")
    mirror = work / "financial_writing_agent/resources/references/style.md"
    mirror.write_text(mirror.read_text(encoding="utf-8") + "\nUNAPPROVED_EXTRA_RULE\n", encoding="utf-8")
    result = project_whole_system(work, head_sha=HEAD)
    assert "PLUGIN_RELEASE_IDENTITY_DRIFT:release_id" in result["structural_violations"]
    assert "POLICY_REFERENCE_MIRROR_BYTES_DRIFT:style.md" in result["structural_violations"]
    assert result["next_legal_step"] == "REPAIR_STRUCTURAL_VIOLATIONS_BEFORE_ANY_STATE_MUTATION"


def test_fake_terminal_article_is_not_promoted_by_word_metadata(tmp_path):
    work = _copy_project(tmp_path)
    file = work / "workspaces/articles" / TASK / "STATE.json"
    state = json.loads(file.read_text(encoding="utf-8"))
    state["status"] = "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN"
    state["delivery_artifacts"] = {
        kind: {"sha256": "b" * 64} for kind in state["required_outputs"]
    }
    file.write_text(json.dumps(state), encoding="utf-8")
    result = project_whole_system(work, head_sha=HEAD)
    assert any("CURRENT_ARTICLE_AGGREGATE_INVALID" in issue
               for issue in result["structural_violations"])
    assert result["whole_product_status"].startswith("NOT_READY")


def test_immutable_source_and_stage_refs_are_checked_as_bytes_not_trusted_names(tmp_path):
    work = _copy_project(tmp_path)
    file = work / "workspaces/articles" / TASK / "STATE.json"
    state = json.loads(file.read_text(encoding="utf-8"))
    stage_file = file.parent / "stages/RESEARCH.md"
    stage_file.parent.mkdir(exist_ok=True)
    stage_file.write_text("Current research fixture source bytes", encoding="utf-8")
    state["stage_artifacts"]["RESEARCH"] = {
        "path": f"workspaces/articles/{TASK}/stages/RESEARCH.md",
        "blob_sha": "0" * 40,
    }
    file.write_text(json.dumps(state), encoding="utf-8")
    inspected = inspect_active_article(work, file)
    assert "STAGE_ARTIFACT_READBACK_FAILED:RESEARCH" in inspected["structural_violations"]
    assert _git_blob_sha(b"Current research fixture source bytes") != "0" * 40


def test_unverified_owner_live_runtime_does_not_get_silent_acceptance_label():
    result = project_whole_system(ROOT, head_sha=HEAD)
    assert result["external_system_acceptance"].startswith("NOT_READY")
    assert "NATIVE_CHAT_DIRECT_GITHUB_WRITES_DO_NOT_EXECUTE_PYTHON_ADMISSION_GUARD" in result["unverified_runtime_boundaries"]
    assert not any(a["business_outcome"].startswith("READY") for a in result["current_articles"])


def test_audit_proof_must_bind_to_a_real_sha():
    with pytest.raises(ValueError, match="EXACT_SOURCE_HEAD_SHA_REQUIRED"):
        project_whole_system(ROOT, head_sha="main")


def test_whole_control_change_audit_does_not_invent_changes():
    receipt = audit_repository_business_changes(
        ["docs/product_requirements.md", "financial_writing_agent/story_quality.py"],
        before_reader=lambda _: None, after_reader=lambda _: None,
    )
    assert receipt["violations"] == []
    assert receipt["business_paths_changed"] == 0
    assert receipt["status"] == "NO_UNADMITTED_BUSINESS_CHANGE_OBSERVED"


def test_whole_control_change_audit_rejects_chat_only_state_write():
    ref = f"workspaces/articles/{TASK}/STATE.json"
    raw = (ROOT / ref).read_bytes()
    modified = json.loads(raw)
    modified["next_action"] = "模型自称这个任务已经完成"
    after = json.dumps(modified, ensure_ascii=False).encode("utf-8")
    receipt = audit_repository_business_changes(
        [ref],
        before_reader=lambda rel: raw if rel == ref else None,
        after_reader=lambda rel: after if rel == ref else None,
    )
    assert receipt["status"].startswith("REJECTED")
    assert any("OWNER_ARTICLE_MUTATION_NOT_ADMITTED" in issue for issue in receipt["violations"])


def test_whole_control_change_audit_rejects_artifact_only_write_without_owner_revision():
    path = f"workspaces/articles/{TASK}/stages/DRAFT.md"
    receipt = audit_repository_business_changes(
        [path],
        before_reader=lambda _: None,
        after_reader=lambda ref: b"unbound draft" if ref == path else None,
    )
    assert f"ARTICLE_ARTIFACT_CHANGED_WITHOUT_STATE_REVISION:{TASK}" in receipt["violations"]


def test_whole_control_change_audit_protects_migrated_history():
    archived = "cross-border-ecommerce-20261016-v2"
    marker = f"workspaces/articles/{archived}/ARTIFACT_STATUS.json"
    bytes_ = (ROOT / marker).read_bytes()
    receipt = audit_repository_business_changes(
        [f"workspaces/articles/{archived}/research/MASTER_UNIVERSE_FINAL_20261016.md"],
        before_reader=lambda rel: bytes_ if rel == marker else None,
        after_reader=lambda rel: bytes_ if rel == marker else None,
    )
    assert "MIGRATED_ARTICLE_HISTORY_MUTATED:" + archived in receipt["violations"]


def test_whole_control_change_audit_rejects_method_catalog_without_append_only_event():
    path = "knowledge/METHOD_KNOWLEDGE_CATALOG.json"
    prior = (ROOT / path).read_bytes()
    fake = json.loads(prior)
    fake["records"] = []
    receipt = audit_repository_business_changes(
        [path],
        before_reader=lambda _: prior,
        after_reader=lambda _: json.dumps(fake).encode("utf-8"),
    )
    assert receipt["status"].startswith("REJECTED")
    assert any("METHOD_MUTATION" in v for v in receipt["violations"])


def test_whole_chain_rejects_configured_direct_main_writes_and_skill_rollback(tmp_path):
    work = _copy_project(tmp_path)
    path = work / "config/EXECUTION_CONTRACT.json"
    contract = json.loads(path.read_text(encoding="utf-8"))
    contract["chatgpt_native_execution"]["direct_main_business_mutation_without_guard_allowed"] = True
    path.write_text(json.dumps(contract, ensure_ascii=False), encoding="utf-8")
    skill = work / "skills/financial-writing-agent/SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8").replace(
            "signed provider admission", "ChatGPT model discretion"
        ),
        encoding="utf-8",
    )
    report = project_whole_system(work, head_sha=HEAD)
    assert "NATIVE_CLIENT_OWNER_EFFECT_GUARD_DRIFT" in report["structural_violations"]
    assert "NATIVE_CLIENT_INSTRUCTIONS_EFFECT_GUARD_DRIFT" in report["structural_violations"]


def test_whole_chain_requires_signed_effect_receipt_and_atomic_bundle_cas_contract(tmp_path):
    work = _copy_project(tmp_path)
    capabilities = work / "config/FINANCIAL_CAPABILITIES.json"
    data = json.loads(capabilities.read_text(encoding="utf-8"))
    data["required_external_capabilities_at_execution"].remove(
        "PROVIDER_SIGNED_ACTION_EFFECT_ATTESTATION_FOR_EACH_OWNER_OR_METHOD_MUTATION"
    )
    capabilities.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    report = project_whole_system(work, head_sha=HEAD)
    assert "NATIVE_CLIENT_CAPABILITY_BOUNDARY_DRIFT" in report["structural_violations"]

    contract_root = tmp_path / "contract-drift"
    contract_root.mkdir()
    work = _copy_project(contract_root)
    contract_path = work / "config/EXECUTION_CONTRACT.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract["chatgpt_native_execution"]["business_effect_receipt_contract"] = "AUTHORIZATION_ONLY"
    contract_path.write_text(json.dumps(contract, ensure_ascii=False), encoding="utf-8")
    report = project_whole_system(work, head_sha=HEAD)
    assert "NATIVE_CLIENT_OWNER_EFFECT_GUARD_DRIFT" in report["structural_violations"]


def test_whole_chain_catches_runtime_dependency_silently_dropped(tmp_path):
    work = _copy_project(tmp_path)
    file = work / "config/FINANCIAL_CAPABILITIES.json"
    caps = json.loads(file.read_text(encoding="utf-8"))
    caps["required_external_capabilities_at_execution"].remove(
        "AUTHENTICATED_PROVIDER_ACTION_SIGNER_FOR_OWNER_STATE_OR_METHOD_MUTATION"
    )
    file.write_text(json.dumps(caps), encoding="utf-8")
    report = project_whole_system(work, head_sha=HEAD)
    assert "NATIVE_CLIENT_CAPABILITY_BOUNDARY_DRIFT" in report["structural_violations"]

def _effect_bound_create_fixture():
    task_id = "audit-effect-binding-001"
    action_id = "audit-create-effect-001"
    prompt = "Synthetic owner-authorized article task for effect-binding audit."
    request = {
        "schema_version": "1.0",
        "domain_id": "financial_writing",
        "action_id": action_id,
        "task_id": task_id,
        "operation": "CREATE_ARTICLE",
        "expected_state_blob_sha": None,
        "parameters": {"prompt": prompt, "source_refs": []},
    }
    state = build_initial_state(
        task_id=task_id,
        prompt=prompt,
        source_refs=[],
        executor_identity=f"financial:{action_id}",
    )
    effect_ref = f"workspaces/articles/{task_id}/actions/{action_id}.effect.json"
    bindings = state["execution_receipts"][-1]["input_bindings"]
    bindings["previous_state_blob_sha"] = "NEW_FILE"
    bindings["authorization_contract_version"] = "1.1"
    authorization = signed_action_authorization(request)
    bindings["authorization_verification"] = authorization
    bindings["effect_contract_version"] = "1.0"
    bindings["effect_receipt_ref"] = effect_ref
    state_raw = (json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    effect = signed_action_effect({
        "approved": True,
        "action_id": action_id,
        "task_id": task_id,
        "operation": "CREATE_ARTICLE",
        "previous_state_blob_sha": "NEW_FILE",
        "resulting_state_blob_sha": _git_blob_sha(state_raw),
        "request_sha256": request_sha256(request),
        "authorization_sha256": payload_sha256(authorization),
        "effect_contract_version": "1.0",
        "admission_runtime": "financial_writing_agent.standalone_runtime.admit_article_action",
    })
    effect_raw = (json.dumps(effect, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    state_ref = f"workspaces/articles/{task_id}/STATE.json"
    return state_ref, effect_ref, state_raw, effect_raw


def test_whole_control_audit_requires_signed_effect_bound_to_exact_result_bytes():
    state_ref, effect_ref, state_raw, effect_raw = _effect_bound_create_fixture()
    files = {state_ref: state_raw, effect_ref: effect_raw}
    accepted = audit_repository_business_changes(
        [state_ref, effect_ref],
        before_reader=lambda _: None,
        after_reader=lambda ref: files.get(ref),
    )
    assert accepted["status"] == "NO_UNADMITTED_BUSINESS_CHANGE_OBSERVED"
    assert accepted["violations"] == []

    missing = audit_repository_business_changes(
        [state_ref, effect_ref],
        before_reader=lambda _: None,
        after_reader=lambda ref: state_raw if ref == state_ref else None,
    )
    assert missing["status"].startswith("REJECTED")
    assert any("ACTION_EFFECT" in issue or "EFFECT_RECEIPT" in issue
               for issue in missing["violations"])

    tampered = json.loads(state_raw)
    tampered["next_action"] = "A_DIFFERENT_BUT_STRUCTURALLY_VALID_ACTION"
    tampered_raw = (json.dumps(tampered, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    changed = {state_ref: tampered_raw, effect_ref: effect_raw}
    rejected = audit_repository_business_changes(
        [state_ref, effect_ref],
        before_reader=lambda _: None,
        after_reader=lambda ref: changed.get(ref),
    )
    assert rejected["status"].startswith("REJECTED")
    assert any("ARTICLE_EFFECT_RESULT_STATE_SHA_MISMATCH" in issue
               for issue in rejected["violations"])
