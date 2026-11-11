"""Executable Financial product boundary checks under the CAOS cognition parent.

Neither a valid contract nor this script is an independent reader-quality eval.
"""
from __future__ import annotations

import json
from pathlib import Path

from financial_writing_agent.artifact_hygiene import validate_artifact_status_manifest
from financial_writing_agent.caos_bridge import PARENT_REPOSITORY
from financial_writing_agent.current_admission import (
    WRITING_KERNEL_VERSION,
    build_initial_state,
    validate_state,
)
from financial_writing_agent.models import ArtifactKind, DistributionMode, TaskContract
from financial_writing_agent.private_research import PRIVATE_RESEARCH_CONTRACT_VERSION, REQUIRED_MODULES
from financial_writing_agent.writing_kernel import validate_kernel

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    manifest, adapter, caps = [load(path) for path in (
        ".uaos/MANIFEST.json", ".uaos/ADAPTER.json", ".uaos/CAPABILITIES.json")]
    execution = load("config/EXECUTION_CONTRACT.json")
    assert manifest["controller"] == adapter["controller"] == PARENT_REPOSITORY + "@main"
    assert manifest["binding"]["controller_ref"] == PARENT_REPOSITORY + "@main:src/cognition_agent_os/domain_contract.py"
    assert manifest["skill"]["entrypoint"] == "CAOS_SKILL.md"
    assert manifest["binding"]["adapter_ref"] == ".uaos/ADAPTER.json"
    assert manifest["binding"]["capability_ref"] == ".uaos/CAPABILITIES.json"
    assert caps["caos_domain_contract_ref"] == manifest["binding"]["controller_ref"]
    assert caps["hosted_cognition_semantics"]["implementation_evidence"] == "NOT_EQUIVALENT_TO_NATIVE_HOST_ACTIVATION"
    assert execution["hosted_governance"]["child_business_action_requires_owner_native_gate"] is True
    assert execution["hosted_governance"]["parent_read_only_observation"] is True
    assert execution["identity"]["parent_child_id_equality_required"] is False
    assert execution["authority"]["alternate_business_state_authority_allowed"] is False

    contract = TaskContract(prompt="finance test")
    assert not hasattr(contract, "task_id")
    assert contract.distribution_mode == DistributionMode.PORTFOLIO
    assert contract.required_outputs == [
        ArtifactKind.AUDIT_DOCX,
        ArtifactKind.FINANCE_DEEP_DOCX,
        ArtifactKind.FINANCE_BROAD_DOCX,
        ArtifactKind.PLATFORM_INTERACTION_PACK_DOCX,
    ]
    state = build_initial_state(
        task_id="caos-financial-contract-smoke",
        prompt="基于材料撰写可核验的A股财经报道",
        source_refs=[],
        executor_identity="ci:caos-contract",
    )
    validate_state(state)
    assert state["writing_kernel_version"] == WRITING_KERNEL_VERSION == "1.0"
    assert state["private_research_contract_version"] == PRIVATE_RESEARCH_CONTRACT_VERSION == "1.1"
    assert state["task_requirement_contract_version"] == "1.0"
    assert state["task_requirement_authority"]["revision"] == 0
    assert state["quality_evidence"] == {}
    assert state["execution_receipts"][0]["task_id"] == state["task_id"]
    assert len(REQUIRED_MODULES) == 15
    assert not validate_kernel()

    # A genuine current task is still unfinished. Test its actual child state
    # and preservation of admitted task requirements; do not self-complete it.
    v3 = ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v3"
    current = load(str((v3 / "STATE.json").relative_to(ROOT)))
    validate_state(current)
    assert current["current_stage"] == "RESEARCH"
    assert current["status"] == "IN_PROGRESS"
    assert current["quality_evidence"] == {}
    assert {x["requirement_id"] for x in current["task_requirement_authority"]["active_requirements"]} == {
        "full_universe_research_pool", "deep_complete_retained_universe",
    }
    current_manifest = validate_artifact_status_manifest(
        load(str((v3 / "ARTIFACT_STATUS.json").relative_to(ROOT))))
    assert current_manifest["workspace_lifecycle"] == "CURRENT"
    assert current_manifest["statuses"] == {"STATE.json": "KEEP_CURRENT"}

    v2 = ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v2"
    legacy = validate_artifact_status_manifest(
        load(str((v2 / "ARTIFACT_STATUS.json").relative_to(ROOT))))
    assert legacy["workspace_lifecycle"] == "MIGRATED_HISTORY"
    assert legacy["current_authority"] == str((v3 / "STATE.json").relative_to(ROOT))
    assert "KEEP_CURRENT" not in legacy["statuses"].values()

    quality = load("evals/quality_regression.json")
    assert "GENERAL_EDITORIAL_QUALITY" in quality["current_readiness"]
    assert "PERSONALIZED_WRITING_DNA" in quality["current_readiness"]
    idx = load("evals/EVOLUTION_INDEX.json")["active_system_assessment"]
    assert idx["owner"] == "DOMAIN:financial_writing"
    assert "NO_NEW_TASK_INDEX" in idx["boundary"]
    assert (ROOT / idx["review_ref"]).is_file()

    print("PASS: CAOS read-only child contract and Financial canonical task, "
          "private research, product modes, ten-stage kernel, historical provenance, "
          "owner-scoped requirements and explicit outcome-certification limits")


if __name__ == "__main__":
    main()
