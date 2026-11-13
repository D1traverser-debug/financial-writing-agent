#!/usr/bin/env python3
"""Manifest-bound two-phase archive/prune; no destructive action in archive phase."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

REPO = "D1traverser-debug/financial-writing-agent"
PREFIX = "archive/financial-20261112/"
ENVIRONMENTS = ("financial-branch-archive", "financial-branch-prune")
BRANCH_RULESET = "Financial archive write freeze"
TAG_RULESET = "Financial archive tag lock"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def branch_rows(branches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    seen = set()
    for item in branches:
        commit = item.get("commit") if isinstance(item, dict) else None
        name = item.get("name") if isinstance(item, dict) else None
        sha = commit.get("sha") if isinstance(commit, dict) else None
        if (not isinstance(name, str) or not name
            or not isinstance(sha, str) or re.fullmatch(r"[a-f0-9]{40}", sha) is None
            or name in seen):
            raise ValueError("BRANCH_INVENTORY_INVALID_OR_DUPLICATED")
        seen.add(name)
        rows.append({"name": name, "sha": sha, "protected": item.get("protected") is True})
    return sorted(rows, key=lambda x: x["name"])


class GitHubAPI:
    def __init__(self, token: str | None):
        if not token:
            raise ValueError("FINANCIAL_ARCHIVE_PROVIDER_TOKEN_REQUIRED")
        self.token = token

    def call(self, method: str, path: str, payload=None, *, allow_404=False):
        if not path.startswith("/repos/" + REPO + "/"):
            raise ValueError("CROSS_REPOSITORY_MUTATION_FORBIDDEN")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "financial-branch-archive-guard",
            "Authorization": "Bearer " + self.token,
        }
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        attempts = 3 if method == "GET" else 1
        for attempt in range(attempts):
            try:
                with urlopen(Request("https://api.github.com" + path, data=data,
                                     headers=headers, method=method), timeout=20) as response:
                    body = response.read()
                    return json.loads(body) if body else None
            except HTTPError as exc:
                if exc.code == 404 and allow_404:
                    return None
                retry = exc.headers.get("Retry-After") if exc.headers else None
                if method == "GET" and exc.code in {403, 429} and retry and attempt < attempts - 1:
                    try:
                        time.sleep(min(max(float(retry), 1), 30))
                    except ValueError:
                        time.sleep(2)
                    continue
                raise RuntimeError(f"GITHUB_{method}_{path}_HTTP_{exc.code}") from exc
            except (TimeoutError, URLError) as exc:
                if method == "GET" and attempt < attempts - 1:
                    time.sleep(attempt + 1)
                    continue
                raise RuntimeError(f"GITHUB_{method}_{path}_TRANSPORT_FAILURE") from exc
        raise RuntimeError("GITHUB_GET_RETRY_EXHAUSTED")

    def paginate(self, suffix: str):
        all_items = []
        for page in range(1, 1001):
            sep = "&" if "?" in suffix else "?"
            values = self.call("GET", f"/repos/{REPO}/{suffix}{sep}per_page=100&page={page}")
            if not isinstance(values, list):
                raise ValueError("GITHUB_COLLECTION_INVALID")
            all_items.extend(values)
            if len(values) < 100:
                return all_items
        raise ValueError("GITHUB_PAGINATION_EXCEEDED")

    def branch_head(self, name: str):
        ref = self.call("GET", f"/repos/{REPO}/git/ref/heads/{quote(name, safe='/')}", allow_404=True)
        return ref.get("object", {}).get("sha") if ref else None

    def tag_head(self, name: str):
        ref = self.call("GET", f"/repos/{REPO}/git/ref/tags/{quote(PREFIX + name, safe='/')}", allow_404=True)
        return ref.get("object", {}).get("sha") if ref else None

    def tag_branch_head(self, name: str, sha: str):
        old = self.tag_head(name)
        if old is not None:
            if old != sha:
                raise ValueError("ARCHIVE_TAG_CONFLICT")
            return
        self.call("POST", f"/repos/{REPO}/git/refs",
                  {"ref": "refs/tags/" + PREFIX + name, "sha": sha})
        if self.tag_head(name) != sha:
            raise RuntimeError("ARCHIVE_TAG_READBACK_FAILED")

    def main_protection(self):
        raw = self.call(
            "GET", f"/repos/{REPO}/branches/main/protection", allow_404=True,
        )
        if not isinstance(raw, dict):
            raise ValueError("MAIN_BRANCH_PROTECTION_MISSING")

        status = raw.get("required_status_checks")
        if not isinstance(status, dict):
            raise ValueError("MAIN_FINANCIAL_CI_REQUIRED_CHECK_MISSING")
        raw_contexts = status.get("contexts", [])
        if not isinstance(raw_contexts, list):
            raw_contexts = []
        contexts = {
            item for item in raw_contexts
            if isinstance(item, str) and item
        }
        checks = status.get("checks", [])
        if isinstance(checks, list):
            contexts.update(
                item.get("context") for item in checks
                if isinstance(item, dict) and isinstance(item.get("context"), str)
                and item.get("context")
            )
        if "test" not in contexts:
            raise ValueError("MAIN_FINANCIAL_CI_REQUIRED_CHECK_MISSING")

        reviews = raw.get("required_pull_request_reviews")
        if not isinstance(reviews, dict):
            raise ValueError("MAIN_PULL_REQUEST_REQUIRED_RULE_MISSING")
        approvals = reviews.get("required_approving_review_count")
        if type(approvals) is not int or approvals < 1:
            raise ValueError("MAIN_INDEPENDENT_APPROVAL_REQUIRED")

        force_pushes = raw.get("allow_force_pushes")
        if not isinstance(force_pushes, dict) or force_pushes.get("enabled") is not False:
            raise ValueError("MAIN_FORCE_PUSH_NOT_DISABLED")
        deletions = raw.get("allow_deletions")
        if not isinstance(deletions, dict) or deletions.get("enabled") is not False:
            raise ValueError("MAIN_DELETION_NOT_DISABLED")

        return {
            "pull_requests_required": True,
            "required_approving_review_count": approvals,
            "required_status_checks": sorted(contexts),
            "force_pushes_enabled": False,
            "deletions_enabled": False,
        }

    def delete_branch(self, name: str, sha: str):
        if name == "main" or self.branch_head(name) != sha or self.tag_head(name) != sha:
            raise ValueError("BRANCH_OR_ARCHIVE_TAG_PRECONDITION_FAILED")
        try:
            self.call("DELETE", f"/repos/{REPO}/git/refs/heads/{quote(name, safe='/')}")
        except Exception as exc:
            try:
                head, tag = self.branch_head(name), self.tag_head(name)
            except Exception as read_exc:
                raise RuntimeError("DELETE_OUTCOME_AMBIGUOUS_READBACK_FAILED") from read_exc
            if head is None and tag == sha:
                return {"branch": name, "status": "AMBIGUOUS_RESPONSE_BUT_ABSENCE_AND_TAG_VERIFIED"}
            if head == sha and tag == sha:
                raise RuntimeError("DELETE_FAILED_REF_PRESERVED") from exc
            raise RuntimeError("DELETE_OUTCOME_AMBIGUOUS_HEAD_OR_TAG_MISMATCH") from exc
        if self.branch_head(name) is not None or self.tag_head(name) != sha:
            raise RuntimeError("DELETE_POSTCONDITION_FAILED")
        return {"branch": name, "status": "DELETE_AND_READBACK_VERIFIED"}

    def ruleset(self, name: str):
        found = [x for x in self.paginate("rulesets?includes_parents=true") if x.get("name") == name]
        if len(found) != 1:
            raise ValueError("RULESET_MISSING_OR_DUPLICATED:" + name)
        detail = self.call("GET", f"/repos/{REPO}/rulesets/{found[0]['id']}?includes_parents=true")
        if not isinstance(detail, dict):
            raise ValueError("RULESET_DETAIL_UNAVAILABLE:" + name)
        return detail

    def verify_controls(self, phase: str):
        main_protection = self.main_protection()
        for env_name in ENVIRONMENTS:
            env = self.call("GET", f"/repos/{REPO}/environments/{env_name}")
            rules = env.get("protection_rules", []) if isinstance(env, dict) else []
            if not any(x.get("type") == "required_reviewers" and x.get("reviewers") for x in rules):
                raise ValueError("REQUIRED_REVIEWER_ENVIRONMENT_MISSING:" + env_name)

        branch = self.ruleset(BRANCH_RULESET)
        branch_types = {x.get("type") for x in branch.get("rules", [])}
        refs = branch.get("conditions", {}).get("ref_name", {})
        if "bypass_actors" not in branch or not isinstance(branch["bypass_actors"], list):
            raise ValueError("BRANCH_BYPASS_ACTORS_NOT_VISIBLE_FAIL_CLOSED")
        if branch["bypass_actors"]:
            raise ValueError("BRANCH_BYPASS_ACTORS_MUST_BE_EMPTY")
        if not (
            branch.get("target") == "branch" and branch.get("enforcement") == "active"
            and "~ALL" in refs.get("include", [])
            and "refs/heads/main" in refs.get("exclude", [])
            and {"creation", "update"}.issubset(branch_types)
        ):
            raise ValueError("BRANCH_WRITE_FREEZE_INVALID")
        if phase in {"PLAN", "ARCHIVE"} and "deletion" not in branch_types:
            raise ValueError("BRANCH_DELETION_MUST_BE_FROZEN_FOR_PLAN_AND_ARCHIVE")
        if phase == "PRUNE" and "deletion" in branch_types:
            raise ValueError("REMOVE_ONLY_DELETION_RULE_BEFORE_PRUNE")

        tags = self.ruleset(TAG_RULESET)
        tag_types = {x.get("type") for x in tags.get("rules", [])}
        tag_refs = tags.get("conditions", {}).get("ref_name", {})
        if "bypass_actors" not in tags or not isinstance(tags["bypass_actors"], list):
            raise ValueError("TAG_BYPASS_ACTORS_NOT_VISIBLE_FAIL_CLOSED")
        if tags["bypass_actors"]:
            raise ValueError("TAG_BYPASS_ACTORS_MUST_BE_EMPTY")
        if not (
            tags.get("target") == "tag" and tags.get("enforcement") == "active"
            and "refs/tags/" + PREFIX + "**" in tag_refs.get("include", [])
            and {"update", "deletion"}.issubset(tag_types)
        ):
            raise ValueError("ARCHIVE_TAG_LOCK_INVALID")
        return {
            "branch_ruleset_id": branch["id"], "tag_ruleset_id": tags["id"],
            "branch_rule_types": sorted(branch_types), "tag_rule_types": sorted(tag_types),
            "reviewer_environments_configured": list(ENVIRONMENTS),
            "main_protection": main_protection,
            "current_run_approval": "GITHUB_ACTIONS_ENVIRONMENT_GATE__NOT_INFERRED_BY_SCRIPT",
        }


def live_manifest(api: GitHubAPI, controls: dict[str, Any]):
    branches1 = branch_rows(api.paginate("branches"))
    prs1 = api.paginate("pulls?state=open")
    closed1 = api.paginate("pulls?state=closed")
    main1 = api.branch_head("main")
    branches2 = branch_rows(api.paginate("branches"))
    prs2 = api.paginate("pulls?state=open")
    closed2 = api.paginate("pulls?state=closed")
    main2 = api.branch_head("main")
    if (branches1 != branches2 or prs1 != prs2 or closed1 != closed2
        or main1 is None or main1 != main2):
        raise ValueError("LIVE_INVENTORY_NOT_STABLE")
    main = next((x for x in branches2 if x["name"] == "main"), None)
    if not main or not main["protected"] or main["sha"] != main2:
        raise ValueError("MAIN_MUST_BE_PROTECTED_AND_MATCH_LIVE_SHA")
    if prs2:
        raise ValueError("OPEN_PULL_REQUESTS_MUST_BE_CLOSED")
    non_main_protected = [x for x in branches2 if x["name"] != "main" and x["protected"]]
    if non_main_protected:
        raise ValueError("NON_MAIN_PROTECTED_BRANCHES_PREVENT_SINGLE_MAIN")

    merged_main_prs = []
    for pr in closed2:
        head = pr.get("head", {})
        base = pr.get("base", {})
        if pr.get("merged_at") and base.get("ref") == "main":
            number, head_sha, head_ref = pr.get("number"), head.get("sha"), head.get("ref")
            if (type(number) is not int or not isinstance(head_sha, str)
                or len(head_sha) != 40 or not isinstance(head_ref, str) or not head_ref):
                raise ValueError("MERGED_PR_HEAD_EVIDENCE_INVALID")
            merged_main_prs.append({
                "number": number, "head_ref": head_ref,
                "head_sha": head_sha, "merged_at": pr["merged_at"],
            })
    merged_main_prs.sort(key=lambda x: x["number"])
    candidates = [{"branch": x["name"], "head_sha": x["sha"]}
                  for x in branches2 if x["name"] != "main"]
    branch_review = []
    for item in candidates:
        matching = [pr["number"] for pr in merged_main_prs
                    if pr["head_sha"] == item["head_sha"]]
        branch_review.append({
            **item,
            "exact_merged_main_pr_numbers": matching,
            "disposition": (
                "EXACT_HEAD_OF_MERGED_MAIN_PR"
                if matching else "NO_EXACT_MERGED_MAIN_PR__REQUIRES_EXPLICIT_REVIEW"
            ),
        })
    manifest = {
        "schema_version": "5.0", "repo": REPO, "main_sha": main2,
        "main_protection": controls["main_protection"],
        "branches": branches2, "candidate_heads": candidates,
        "merged_main_prs": merged_main_prs,
        "branch_review": branch_review,
        "unverified_branch_heads": [
            item for item in branch_review if not item["exact_merged_main_pr_numbers"]
        ],
        "control_ids": {"branch_ruleset_id": controls["branch_ruleset_id"],
                        "tag_ruleset_id": controls["tag_ruleset_id"]},
        "open_prs": [],
    }
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> None:
    if not isinstance(manifest, dict) or manifest.get("repo") != REPO:
        raise ValueError("MANIFEST_IDENTITY_MISMATCH")
    if manifest.get("schema_version") != "5.0":
        raise ValueError("MANIFEST_SCHEMA_VERSION_MISMATCH")
    raw_branches = manifest.get("branches")
    if not isinstance(raw_branches, list):
        raise ValueError("MANIFEST_BRANCH_INVENTORY_INVALID")
    branches = []
    seen_names = set()
    for item in raw_branches:
        if (not isinstance(item, dict)
            or not isinstance(item.get("name"), str) or not item["name"]
            or item["name"] in seen_names
            or not isinstance(item.get("sha"), str)
            or re.fullmatch(r"[a-f0-9]{40}", item["sha"]) is None
            or type(item.get("protected")) is not bool):
            raise ValueError("MANIFEST_BRANCH_INVENTORY_INVALID_OR_DUPLICATED")
        seen_names.add(item["name"])
        branches.append({
            "name": item["name"], "sha": item["sha"],
            "protected": item["protected"],
        })
    if branches != sorted(branches, key=lambda x: x["name"]):
        raise ValueError("MANIFEST_BRANCH_INVENTORY_NOT_CANONICAL")
    main = next((item for item in branches if item["name"] == "main"), None)
    if (main is None or main["protected"] is not True
        or main["sha"] != manifest.get("main_sha")
        or any(item["name"] != "main" and item["protected"] for item in branches)):
        raise ValueError("MANIFEST_MAIN_IDENTITY_INVALID_OR_NON_MAIN_PROTECTED")
    expected_candidates = [
        {"branch": item["name"], "head_sha": item["sha"]}
        for item in branches if item["name"] != "main"
    ]
    if manifest.get("candidate_heads") != expected_candidates:
        raise ValueError("MANIFEST_CANDIDATE_SET_INCOMPLETE_OR_MUTATED")
    if manifest.get("open_prs") != []:
        raise ValueError("MANIFEST_CONTAINS_OPEN_PULL_REQUESTS")
    merged = manifest.get("merged_main_prs")
    if not isinstance(merged, list):
        raise ValueError("MANIFEST_MERGED_PR_EVIDENCE_MISSING")
    seen_prs = set()
    for item in merged:
        if (not isinstance(item, dict) or type(item.get("number")) is not int
            or item["number"] <= 0 or item["number"] in seen_prs
            or not isinstance(item.get("head_ref"), str) or not item["head_ref"]
            or not isinstance(item.get("head_sha"), str)
            or re.fullmatch(r"[a-f0-9]{40}", item["head_sha"]) is None
            or not isinstance(item.get("merged_at"), str) or not item["merged_at"]):
            raise ValueError("MANIFEST_MERGED_PR_EVIDENCE_INVALID")
        seen_prs.add(item["number"])
    if merged != sorted(merged, key=lambda x: x["number"]):
        raise ValueError("MANIFEST_MERGED_PR_EVIDENCE_NOT_CANONICAL")
    expected_review = []
    for item in expected_candidates:
        matching = [pr["number"] for pr in merged
                    if pr["head_sha"] == item["head_sha"]]
        expected_review.append({
            **item,
            "exact_merged_main_pr_numbers": matching,
            "disposition": (
                "EXACT_HEAD_OF_MERGED_MAIN_PR"
                if matching else "NO_EXACT_MERGED_MAIN_PR__REQUIRES_EXPLICIT_REVIEW"
            ),
        })
    if manifest.get("branch_review") != expected_review:
        raise ValueError("MANIFEST_BRANCH_REVIEW_BINDING_INVALID")
    expected_unverified = [
        item for item in expected_review if not item["exact_merged_main_pr_numbers"]
    ]
    if manifest.get("unverified_branch_heads") != expected_unverified:
        raise ValueError("MANIFEST_UNVERIFIED_BRANCH_SET_INVALID")
    protection = manifest.get("main_protection")
    if (
        not isinstance(protection, dict)
        or protection.get("pull_requests_required") is not True
        or type(protection.get("required_approving_review_count")) is not int
        or protection["required_approving_review_count"] < 1
        or not isinstance(protection.get("required_status_checks"), list)
        or "test" not in protection["required_status_checks"]
        or protection.get("force_pushes_enabled") is not False
        or protection.get("deletions_enabled") is not False
    ):
        raise ValueError("MANIFEST_MAIN_PROTECTION_INVALID")

    controls = manifest.get("control_ids")
    if (not isinstance(controls, dict)
        or type(controls.get("branch_ruleset_id")) is not int
        or type(controls.get("tag_ruleset_id")) is not int
        or controls["branch_ruleset_id"] <= 0
        or controls["tag_ruleset_id"] <= 0):
        raise ValueError("MANIFEST_CONTROL_IDS_INVALID")


def stable_snapshot(api: GitHubAPI, phase: str):
    before = api.verify_controls(phase)
    manifest = live_manifest(api, before)
    after = api.verify_controls(phase)
    if (before["branch_ruleset_id"] != after["branch_ruleset_id"]
        or before["tag_ruleset_id"] != after["tag_ruleset_id"]
        or before["branch_rule_types"] != after["branch_rule_types"]
        or before["tag_rule_types"] != after["tag_rule_types"]
        or before["main_protection"] != after["main_protection"]):
        raise ValueError("RULESET_CHANGED_DURING_INVENTORY")
    return manifest, sha256(manifest), after


def read_plan(path: Path, approved: str):
    record = json.loads(path.read_text(encoding="utf-8"))
    manifest = record.get("manifest")
    actual = sha256(manifest)
    if record.get("manifest_sha256") != actual or approved != actual:
        raise ValueError("APPROVED_MANIFEST_SHA256_MISMATCH")
    validate_manifest(manifest)
    return manifest, actual


def create_plan(api: GitHubAPI, out: Path):
    manifest, checksum, controls = stable_snapshot(api, "PLAN")
    result = {"manifest": manifest, "manifest_sha256": checksum,
              "plan_status": "READY_FOR_REVIEW__NO_MUTATION", "controls": controls}
    write_json(out, result)
    return result


def archive_only(api: GitHubAPI, manifest_path: Path, approved: str, out: Path):
    manifest, checksum = read_plan(manifest_path, approved)
    current, current_sha, controls = stable_snapshot(api, "ARCHIVE")
    if current_sha != checksum or current != manifest:
        raise ValueError("CURRENT_INVENTORY_DIFFERS_FROM_REVIEWED_PLAN")
    tagged = []
    for item in manifest["candidate_heads"]:
        api.tag_branch_head(item["branch"], item["head_sha"])
        tagged.append(item)
    for item in manifest["candidate_heads"]:
        if api.branch_head(item["branch"]) != item["head_sha"] or api.tag_head(item["branch"]) != item["head_sha"]:
            raise ValueError("ARCHIVE_READBACK_MISMATCH:" + item["branch"])
    if api.branch_head("main") != manifest["main_sha"] or api.paginate("pulls?state=open"):
        raise ValueError("MAIN_OR_PR_STATE_CHANGED_DURING_ARCHIVE")
    again, again_sha, final_controls = stable_snapshot(api, "ARCHIVE")
    if again_sha != checksum or again != manifest:
        raise ValueError("INVENTORY_CHANGED_DURING_ARCHIVE")
    result = {"manifest_sha256": checksum, "archive_status": "ALL_TAGS_VERIFIED__NO_BRANCHES_DELETED",
              "tagged": tagged, "deleted": [], "controls": final_controls}
    write_json(out, result)
    return result


def _require_protected_main(
    api: GitHubAPI, expected_sha: str, phase: str,
    expected_protection: dict[str, Any] | None = None,
):
    """Re-read main and require the exact planned protection snapshot to remain active."""
    rows = branch_rows(api.paginate("branches"))
    main = next((item for item in rows if item["name"] == "main"), None)
    if main is None or main["protected"] is not True or main["sha"] != expected_sha:
        raise ValueError("MAIN_PROTECTION_OR_HEAD_INVALID:" + phase)
    protection = api.main_protection()
    if expected_protection is not None and protection != expected_protection:
        raise ValueError("MAIN_PROTECTION_CHANGED:" + phase)
    return rows


def prune_only(
    api: GitHubAPI, manifest_path: Path, approved: str, out: Path, *,
    confirm_unverified_branch_archive: bool = False,
):
    manifest, checksum = read_plan(manifest_path, approved)
    if manifest["unverified_branch_heads"] and not confirm_unverified_branch_archive:
        raise ValueError(
            "UNVERIFIED_BRANCH_HEADS_REQUIRE_EXPLICIT_ARCHIVE_PRUNE_CONFIRMATION"
        )
    controls = api.verify_controls("PRUNE")
    if controls["main_protection"] != manifest["main_protection"]:
        raise ValueError("MAIN_PROTECTION_CHANGED_AFTER_ARCHIVE")
    if (controls["branch_ruleset_id"] != manifest["control_ids"]["branch_ruleset_id"]
        or controls["tag_ruleset_id"] != manifest["control_ids"]["tag_ruleset_id"]):
        raise ValueError("RULESET_ID_CHANGED_AFTER_ARCHIVE")
    current_rows = _require_protected_main(
        api, manifest["main_sha"], "BEFORE_PRUNE",
        expected_protection=manifest["main_protection"],
    )
    if api.paginate("pulls?state=open"):
        raise ValueError("OPEN_PULL_REQUESTS_MUST_BE_CLOSED_BEFORE_PRUNE")
    planned = {x["name"]: x["sha"] for x in manifest["branches"]}
    current = {x["name"]: x["sha"] for x in current_rows}
    if any(name not in planned or planned[name] != sha for name, sha in current.items()):
        raise ValueError("UNPLANNED_OR_MOVED_BRANCH_AFTER_ARCHIVE")
    for item in manifest["candidate_heads"]:
        if api.tag_head(item["branch"]) != item["head_sha"]:
            raise ValueError("ARCHIVE_TAG_MISSING_OR_CHANGED:" + item["branch"])

    deleted, absent, failures = [], [], []
    for item in manifest["candidate_heads"]:
        name, sha = item["branch"], item["head_sha"]
        try:
            controls_now = api.verify_controls("PRUNE")
            if (
                controls_now["branch_ruleset_id"] != manifest["control_ids"]["branch_ruleset_id"]
                or controls_now["tag_ruleset_id"] != manifest["control_ids"]["tag_ruleset_id"]
                or controls_now["branch_rule_types"] != controls["branch_rule_types"]
                or controls_now["tag_rule_types"] != controls["tag_rule_types"]
                or controls_now["main_protection"] != manifest["main_protection"]
            ):
                raise ValueError("PRUNE_RULESET_CHANGED_DURING_PRUNE")
            _require_protected_main(
                api, manifest["main_sha"], "DURING_PRUNE",
                expected_protection=manifest["main_protection"],
            )
        except Exception as exc:
            failures.append({"branch": name, "reason": str(exc)})
            break
        if api.paginate("pulls?state=open"):
            failures.append({"branch": name, "reason": "OPEN_PR_CREATED_DURING_PRUNE"})
            break
        if api.tag_head(name) != sha:
            failures.append({"branch": name, "reason": "ARCHIVE_TAG_CHANGED_BEFORE_DELETE"})
            break
        head = api.branch_head(name)
        if head is None:
            absent.append({"branch": name, "status": "ABSENT__TAG_CONFIRMED"})
        elif head != sha:
            failures.append({"branch": name, "reason": "BRANCH_HEAD_CHANGED_BEFORE_DELETE"})
            break
        else:
            try:
                deleted.append(api.delete_branch(name, sha))
            except Exception as exc:
                failures.append({"branch": name, "reason": str(exc)})
                break

    after = branch_rows(api.paginate("branches"))
    prs_after = api.paginate("pulls?state=open")
    main_after = api.branch_head("main")
    main_after_row = next((item for item in after if item["name"] == "main"), None)
    main_protected_after = bool(main_after_row and main_after_row["protected"])
    rulesets_verified_after = False
    try:
        final_controls = api.verify_controls("PRUNE")
        rulesets_verified_after = (
            final_controls["branch_ruleset_id"] == manifest["control_ids"]["branch_ruleset_id"]
            and final_controls["tag_ruleset_id"] == manifest["control_ids"]["tag_ruleset_id"]
            and final_controls["branch_rule_types"] == controls["branch_rule_types"]
            and final_controls["tag_rule_types"] == controls["tag_rule_types"]
            and final_controls["main_protection"] == manifest["main_protection"]
        )
        if not rulesets_verified_after:
            failures.append({"branch": "main", "reason": "PRUNE_RULESET_CHANGED_AFTER_PRUNE"})
    except Exception as exc:
        failures.append({"branch": "main", "reason": str(exc)})
        final_controls = {**controls, "main_protection": None}
    for item in manifest["candidate_heads"]:
        if api.tag_head(item["branch"]) != item["head_sha"]:
            failures.append({"branch": item["branch"], "reason": "FINAL_TAG_READBACK_FAILED"})
    if not main_protected_after:
        failures.append({"branch": "main", "reason": "MAIN_PROTECTION_REMOVED_DURING_PRUNE"})
    complete = (
        [x["name"] for x in after] == ["main"]
        and main_after == manifest["main_sha"]
        and main_protected_after
        and final_controls.get("main_protection") == manifest["main_protection"]
        and rulesets_verified_after
        and not prs_after and not failures
    )
    result = {
        "manifest_sha256": checksum, "before_branch_count": len(manifest["branches"]),
        "after_branch_names": [x["name"] for x in after],
        "tagged_branch_count": len(manifest["candidate_heads"]),
        "deleted": deleted, "already_absent_after_archive": absent,
        "open_pr_count_after": len(prs_after), "main_sha_after": main_after,
        "main_protected_after": main_protected_after,
        "main_protection_after": final_controls.get("main_protection"),
        "main_protection_verified_after": final_controls.get("main_protection") == manifest["main_protection"],
        "prune_rulesets_verified_after": rulesets_verified_after,
        "unresolved_failures": failures, "complete": complete, "controls": final_controls,
    }
    write_json(out, result)
    return result


def dry_run(api: GitHubAPI, out: Path):
    branches = branch_rows(api.paginate("branches"))
    prs = api.paginate("pulls?state=open")
    result = {"mode": "DRY_RUN__NO_MUTATION", "branch_count": len(branches),
              "open_pr_count": len(prs), "branch_inventory": branches}
    write_json(out, result)
    return result


def require_workflow(token: str | None):
    if (os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
        or not os.environ.get("GITHUB_RUN_ID") or not token):
        raise SystemExit("ARCHIVE_ACTION_REQUIRES_MAIN_WORKFLOW_AND_ENVIRONMENT_TOKEN")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--plan", action="store_true")
    group.add_argument("--archive-only", action="store_true")
    group.add_argument("--prune-only", action="store_true")
    parser.add_argument(
        "--confirm-unverified-branch-archive", action="store_true",
        help="explicitly authorize pruning non-main heads without an exact merged-to-main PR head",
    )
    parser.add_argument("--manifest", default="audit/financial_branch_plan.json")
    parser.add_argument("--approved-manifest-sha256", default="")
    parser.add_argument("--out", default="audit/financial_branch_archive.json")
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN")
    if args.plan or args.archive_only or args.prune_only:
        require_workflow(token)
    api = GitHubAPI(token)
    out = Path(args.out)
    if args.plan:
        result = create_plan(api, out)
    elif args.archive_only:
        result = archive_only(api, Path(args.manifest), args.approved_manifest_sha256, out)
    elif args.prune_only:
        result = prune_only(
            api, Path(args.manifest), args.approved_manifest_sha256, out,
            confirm_unverified_branch_archive=args.confirm_unverified_branch_archive,
        )
        if not result["complete"]:
            raise SystemExit("PRUNE_INCOMPLETE__ARCHIVE_TAGS_RETAINED")
    else:
        result = dry_run(api, out)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.plan:
        output = os.environ.get("GITHUB_OUTPUT")
        if output:
            with open(output, "a", encoding="utf-8") as f:
                f.write("manifest_sha256=" + result["manifest_sha256"] + "\n")
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a", encoding="utf-8") as f:
                f.write("# Financial branch archive plan\n\n")
                f.write("Manifest SHA-256: " + result["manifest_sha256"] + "\n\n")
                f.write("Main SHA: " + result["manifest"]["main_sha"] + "\n\n")
                f.write("Branch count: " + str(len(result["manifest"]["branches"])) + "\n\n")
                f.write("Candidate count: " + str(len(result["manifest"]["candidate_heads"])) + "\n\n")
                f.write("No repository refs were modified.\n")


if __name__ == "__main__":
    main()
