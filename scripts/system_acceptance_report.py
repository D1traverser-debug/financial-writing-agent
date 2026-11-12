#!/usr/bin/env python3
"""Report Financial system acceptance separately from green engineering CI.

No unchecked repository field, mock callback or CI test count can certify
real ChatGPT activation, user-text authority or independent business quality.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from financial_writing_agent.acceptance_gates import evaluate_system_acceptance

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="audit/financial_system_acceptance.json")
    parser.add_argument("--assert-not-prematurely-certified", action="store_true")
    arguments = parser.parse_args()
    sha = (os.environ.get("FINANCIAL_SOURCE_HEAD_SHA")
           or os.environ.get("GITHUB_SHA") or "0" * 40)
    if os.environ.get("GITHUB_ACTIONS") == "true":
        import subprocess
        checked_out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        if sha != checked_out:
            raise SystemExit("FINANCIAL_SOURCE_HEAD_NOT_ACTUALLY_CHECKED_OUT")
    index = json.loads((ROOT / "evals/EVOLUTION_INDEX.json").read_text(encoding="utf-8"))
    qual = json.loads((ROOT / "evals/quality_regression.json").read_text(encoding="utf-8"))
    plugin = json.loads((ROOT / "config/CHATGPT_FINANCIAL_PLUGIN.json").read_text(encoding="utf-8"))
    # No external source provider is available in the CI runner, by design.
    # Never load 'verified' labels from the source repository as independent
    # runtime receipts or the acceptance check becomes self-certifying.
    assessment = evaluate_system_acceptance(head_sha=sha, code_tests_passed=True)
    report = {
        "schema_version": "1.0",
        "exact_ci_head_sha": sha,
        "engineering_contract_tests": "PASS__UPSTREAM_CI_TEST_STEP_REQUIRED",
        "whole_system_acceptance": assessment,
        "native_plugin": {
            "plugin_id": plugin["plugin_id"],
            "release_id": plugin["release_id"],
            "private_skill_archive": "CREATED__EXTERNALLY_READBACK",
            "actually_installed_in_user_client": "NOT_VERIFIED",
            "custom_hosted_python_mcp": "NOT_DEPLOYED",
            "real_owner_message_provider": "NOT_VERIFIED",
        },
        "actual_user_scoped_governance": index["active_system_assessment"][
            "owner_governance_rebuild_20261112"
        ]["engineering_status"],
        "editorial_quality_baseline": {
            "general": qual["current_readiness"]["GENERAL_EDITORIAL_QUALITY"]["status"],
            "personalized": qual["current_readiness"]["PERSONALIZED_WRITING_DNA"]["status"],
        },
        "release_readiness": assessment["system_status"],
        "assurance_ceiling": "ENGINEERING_CI_AND_PROVIDER_MOCK_REPLAY",
        "remaining_action_required": [
            "independent provider attestation of exact user-approved semantic change",
            "native Financial plugin actual user installation and fresh-chat invocation",
            "real authenticated GitHub CAS/revocation test, not mock callback",
            "independent adversarial review and actual effect readback",
            "provider-confirmed branch archival/readback and single-main status",
        ],
        "caos_parent_repo_modified": False,
    }
    p = ROOT / arguments.out
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")
    print(json.dumps({
        "head": sha,
        "system_status": report["release_readiness"],
        "open_gates": assessment["open_gates"],
        "plugin_release_created": plugin["release_id"],
        "native_client_installed": False,
        "note": "green CI != Financial independent system acceptance",
    }, ensure_ascii=False, indent=2))
    if arguments.assert_not_prematurely_certified and (
        assessment["system_status"] != "NOT_READY__REQUIRES_EXTERNAL_EVIDENCE"
    ):
        raise SystemExit("FINANCIAL_UNEXPECTED_PREMATURE_COMPLETION")


if __name__ == "__main__":
    main()
