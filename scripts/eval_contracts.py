"""Executable Financial product boundary checks for a standalone business owner.

Neither a valid contract nor this script is an independent reader-quality eval.
"""
from __future__ import annotations

import json
from pathlib import Path

from financial_writing_agent.artifact_hygiene import validate_artifact_status_manifest
from financial_writing_agent.standalone_runtime import DOMAIN_ID, OPERATIONS
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
    manifest = load("config/FINANCIAL_MANIFEST.json")
    caps = load("config/FINANCIAL_CAPABILITIES.json")
    execution = load("config/EXECUTION_CONTRACT.json")
    assert DOMAIN_ID == manifest["domain_id"] == caps["domain_id"] == "financial_writing"
    assert manifest["controller"] == caps["owner"] == execution["authority"]["controller"] == "FINANCIAL_WRITING_OWNER"
    assert manifest["external_parent_required"] is False
    assert manifest["external_host_required"] is False
    assert manifest["skill_entrypoint"] == "skills/financial-writing-agent/SKILL.md"
    assert manifest["provider_adapter"] == "financial_writing_agent.standalone_runtime"
    assert {"CREATE_ARTICLE", "CHANGE_REQUIREMENTS", "ADVANCE_STAGE", "ATTACH_FEEDBACK"} <= OPERATIONS
    assert execution["execution"]["route_selection"] == "DIRECT_FINANCIAL_ONLY"
    assert execution["execution"]["live_parent_business_proxy_required"] is False
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
        task_id="standalone-financial-contract-smoke",
        prompt="基于材料撰写可核验的A股财经报道",
        source_refs=[],
        executor_identity="ci:standalone-financial",
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

    print("PASS: standalone Financial manifest, owner action port and canonical task, "
          "private research, product modes, ten-stage kernel, historical provenance, "
          "owner-scoped requirements and explicit outcome-certification limits")


if __name__ == "__main__":
    main()
