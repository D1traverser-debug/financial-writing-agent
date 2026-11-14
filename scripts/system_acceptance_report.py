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
from financial_writing_agent.whole_system_assurance import (
    project_whole_system, audit_repository_business_changes,
)

ROOT = Path(__file__).resolve().parents[1]


def _audit_git_business_effects(head_sha: str) -> dict:
    """Inspect the actual GitHub PR/push byte diff at both immutable revisions."""
    import subprocess

    base = os.environ.get("FINANCIAL_CHANGE_BASE_SHA", "").strip()
    if not base or set(base) == {"0"}:
        if os.environ.get("GITHUB_ACTIONS") == "true":
            raise SystemExit("FINANCIAL_MUTATION_BASE_REVISION_REQUIRED")
        return {
            "status": "NOT_OBSERVED__LOCAL_BASE_SHA_NOT_PROVIDED",
            "assurance": "NO_BUSINESS_MUTATION_REVIEW_WAS_EXECUTED",
        }
    if len(base) != 40 or any(char not in "0123456789abcdef" for char in base):
        raise SystemExit("FINANCIAL_MUTATION_BASE_SHA_INVALID")
    try:
        raw = subprocess.check_output(
            ["git", "diff", "--no-renames", "--name-only", "-z", base, head_sha,
             "--", "workspaces/articles", "knowledge/METHOD_KNOWLEDGE_CATALOG.json",
             "knowledge/actions"],
            cwd=ROOT,
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit("FINANCIAL_MUTATION_BASE_COMPARISON_FAILED") from exc
    changed_paths = [item.decode("utf-8") for item in raw.split(b"\0") if item]

    def before_reader(rel: str) -> bytes | None:
        key = f"{base}:{rel}"
        exists = subprocess.run(
            ["git", "cat-file", "-e", key], cwd=ROOT, capture_output=True,
        )
        if exists.returncode != 0:
            return None
        return subprocess.check_output(["git", "show", key], cwd=ROOT)

    def after_reader(rel: str) -> bytes | None:
        p = ROOT / rel
        return p.read_bytes() if p.is_file() else None

    result = audit_repository_business_changes(
        changed_paths, before_reader=before_reader, after_reader=after_reader,
    )
    result["comparison_base_sha"] = base
    result["comparison_head_sha"] = head_sha
    result["all_changed_business_paths"] = changed_paths
    if result["violations"]:
        raise SystemExit("FINANCIAL_OWNER_EFFECT_ADMISSION_FAILED:" + ";".join(result["violations"]))
    return result


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
    manifest = json.loads((ROOT / "config/FINANCIAL_MANIFEST.json").read_text(encoding="utf-8"))
    canonical_plugin = manifest["client_skill_plugin"]
    if any(plugin.get(key) != canonical_plugin.get(key) for key in ("plugin_id", "release_id", "version")):
        raise SystemExit("FINANCIAL_PLUGIN_CONFIG_MANIFEST_MISMATCH")
    # No external source provider is available in the CI runner, by design.
    # Never load 'verified' labels from the source repository as independent
    # runtime receipts or the acceptance check becomes self-certifying.
    assessment = evaluate_system_acceptance(head_sha=sha, code_tests_passed=True)
    product_projection = project_whole_system(ROOT, head_sha=sha)
    business_effects = _audit_git_business_effects(sha)
    if product_projection["structural_violations"]:
        raise SystemExit("FINANCIAL_WHOLE_SYSTEM_STRUCTURAL_VIOLATIONS:" + ";".join(product_projection["structural_violations"]))
    report = {
        "schema_version": "1.0",
        "exact_ci_head_sha": sha,
        "engineering_contract_tests": "PASS__UPSTREAM_CI_TEST_STEP_REQUIRED",
        "whole_system_acceptance": assessment,
        "live_product_obligation_projection": product_projection,
        "git_revision_business_effect_admission": business_effects,
        "native_plugin": {
            "plugin_id": canonical_plugin["plugin_id"],
            "release_id": canonical_plugin["release_id"],
            "version": canonical_plugin["version"],
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
    }
    p = ROOT / arguments.out
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")
    print(json.dumps({
        "head": sha,
        "system_status": report["release_readiness"],
        "open_gates": assessment["open_gates"],
        "active_article_results": [
            {"task_id": a["task_id"], "stage": a["stage"], "recorded_outputs": a["recorded_output_count"], "required_outputs": a["required_output_count"]}
            for a in product_projection["current_articles"]
        ],
        "traceable_product_requirement_groups": product_projection["product_requirement_total"],
        "plugin_release_created": canonical_plugin["release_id"],
        "native_client_installed": False,
        "note": "green CI != Financial independent system acceptance",
    }, ensure_ascii=False, indent=2))
    if arguments.assert_not_prematurely_certified and (
        assessment["system_status"].startswith("ACCEPTED")
    ):
        raise SystemExit("FINANCIAL_UNEXPECTED_PREMATURE_COMPLETION")


if __name__ == "__main__":
    main()
