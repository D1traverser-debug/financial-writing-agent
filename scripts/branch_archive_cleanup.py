#!/usr/bin/env python3
"""Tag-first, freeze-gated consolidation of Financial remote branch refs.

GitHub's Delete a Git Reference API is not an expected-SHA compare-and-delete.
Therefore deletion is forbidden unless an active branch update/creation freeze,
an immutable archive-tag ruleset, protected main, and a reviewer-protected
GitHub Environment are all read back from GitHub before mutation.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

ARCHIVE_PREFIX = "archive/financial-20261112/"
APPROVAL = "I_APPROVE_ARCHIVE_AND_PRUNE"
REPO = "D1traverser-debug/financial-writing-agent"
ENVIRONMENT = "financial-branch-archive"
BRANCH_FREEZE_RULESET = "Financial archive write freeze"
TAG_LOCK_RULESET = "Financial archive tag lock"


def branch_candidates(
    branches: list[dict[str, Any]],
    open_prs: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Archive inactive refs, preserving exact heads; never touch main/protected/open-PR."""
    active_pr_heads = {
        p.get("head", {}).get("ref")
        for p in open_prs
        if p.get("head", {}).get("repo", {}).get("full_name") == REPO
    }
    candidates, skipped = [], []
    seen: set[str] = set()
    for branch in branches:
        name = branch.get("name")
        sha = branch.get("commit", {}).get("sha")
        if not isinstance(name, str) or not isinstance(sha, str) or len(sha) != 40:
            raise ValueError("BRANCH_HYGIENE_INVALID_PROVIDER_DATA")
        if name in seen:
            raise ValueError("BRANCH_HYGIENE_DUPLICATE_BRANCH")
        seen.add(name)
        row = {"branch": name, "head_sha": sha}
        if name == "main" or branch.get("protected") is True or name in active_pr_heads:
            skipped.append({**row, "reason": "MAIN_OR_PROTECTED_OR_ACTIVE_PR"})
        else:
            candidates.append(row)
    return candidates, skipped


class GitHubAPI:
    def __init__(self, repo: str, token: str | None):
        if repo != REPO:
            raise ValueError("branch archive is restricted to Financial repository only")
        self.repo, self.token = repo, token

    def call(
        self, method: str, path: str, payload: dict[str, Any] | None = None,
        *, allow_404: bool = False,
    ):
        if not path.startswith("/repos/" + REPO + "/"):
            raise ValueError("CROSS_REPOSITORY_MUTATION_FORBIDDEN")
        url = "https://api.github.com" + path
        raw = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "financial-branch-archive-guard",
        }
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        request = Request(url, data=raw, headers=headers, method=method)
        try:
            with urlopen(request, timeout=20) as response:
                contents = response.read()
                return json.loads(contents) if contents else None
        except HTTPError as exc:
            if exc.code == 404 and allow_404:
                return None
            raise RuntimeError(f"GITHUB_{method}_{path}_HTTP_{exc.code}") from exc

    def paginate(self, suffix: str):
        items = []
        for page in range(1, 1001):
            separator = "&" if "?" in suffix else "?"
            path = f"/repos/{self.repo}/{suffix}{separator}per_page=100&page={page}"
            values = self.call("GET", path)
            if not isinstance(values, list):
                raise ValueError("BRANCH_HYGIENE_BAD_GITHUB_COLLECTION")
            items.extend(values)
            if len(values) < 100:
                return items
        raise ValueError("BRANCH_HYGIENE_PAGINATION_EXCEEDED")

    def exact_branch_head(self, name: str) -> str | None:
        ref = self.call(
            "GET", f"/repos/{self.repo}/git/ref/heads/{quote(name, safe='/')}",
            allow_404=True,
        )
        return ref.get("object", {}).get("sha") if ref else None

    def archived_tag_head(self, name: str) -> str | None:
        tag = self.call(
            "GET", f"/repos/{self.repo}/git/ref/tags/{quote(ARCHIVE_PREFIX + name, safe='/')}",
            allow_404=True,
        )
        return tag.get("object", {}).get("sha") if tag else None

    def tag_archive(self, name: str, sha: str):
        existing = self.archived_tag_head(name)
        if existing is not None:
            if existing != sha:
                raise ValueError("ARCHIVE_TAG_CONFLICT_HEAD_NOT_IDENTICAL")
            return
        self.call("POST", f"/repos/{self.repo}/git/refs",
                  {"ref": "refs/tags/" + ARCHIVE_PREFIX + name, "sha": sha})
        if self.archived_tag_head(name) != sha:
            raise RuntimeError("ARCHIVE_TAG_SECOND_READBACK_FAILED")

    def prune_branch(self, name: str, sha: str):
        if name == "main":
            raise ValueError("CANNOT_DELETE_MAIN")
        if self.exact_branch_head(name) != sha:
            raise ValueError("BRANCH_HEAD_MOVED_NO_DELETE")
        if self.archived_tag_head(name) != sha:
            raise ValueError("ARCHIVE_TAG_NOT_PINNED_NO_DELETE")
        # The preceding freeze ruleset is the concurrency control. GitHub's
        # delete-ref API has no expected-SHA condition; without the freeze,
        # this operation must not be called.
        try:
            self.call("DELETE", f"/repos/{self.repo}/git/refs/heads/{quote(name, safe='/')}")
        except RuntimeError as exc:
            # Do not collapse 404 into success. An external actor may have
            # deleted the ref; report it as ambiguous, even though the tag is safe.
            raise RuntimeError("BRANCH_DELETE_OUTCOME_AMBIGUOUS__" + str(exc)) from exc
        if self.exact_branch_head(name) is not None:
            raise RuntimeError("BRANCH_DELETE_READBACK_FAILED")
        if self.archived_tag_head(name) != sha:
            raise RuntimeError("ARCHIVE_TAG_CHANGED_AFTER_BRANCH_DELETE")

    def _ruleset(self, name: str) -> dict[str, Any]:
        summaries = self.paginate("rulesets?includes_parents=true")
        matches = [x for x in summaries if x.get("name") == name]
        if len(matches) != 1:
            raise ValueError("REQUIRED_RULESET_MISSING_OR_DUPLICATED:" + name)
        detail = self.call(
            "GET", f"/repos/{self.repo}/rulesets/{matches[0]['id']}?includes_parents=true",
        )
        if not isinstance(detail, dict):
            raise ValueError("REQUIRED_RULESET_DETAIL_UNAVAILABLE:" + name)
        return detail

    def verify_archive_controls(self) -> dict[str, Any]:
        env = self.call(
            "GET", f"/repos/{self.repo}/environments/{quote(ENVIRONMENT, safe='')}",
        )
        protection = env.get("protection_rules", []) if isinstance(env, dict) else []
        reviewer_rules = [
            item for item in protection
            if item.get("type") == "required_reviewers" and item.get("reviewers")
        ]
        if not reviewer_rules:
            raise ValueError("ARCHIVE_ENVIRONMENT_REQUIRES_CONFIGURED_REVIEWERS")

        branch = self._ruleset(BRANCH_FREEZE_RULESET)
        branch_ref = branch.get("conditions", {}).get("ref_name", {})
        branch_types = {x.get("type") for x in branch.get("rules", [])}
        if (
            branch.get("target") != "branch" or branch.get("enforcement") != "active"
            or "~ALL" not in branch_ref.get("include", [])
            or "refs/heads/main" not in branch_ref.get("exclude", [])
            or not {"creation", "update"}.issubset(branch_types)
            or branch.get("bypass_actors", [])
        ):
            raise ValueError("BRANCH_WRITE_FREEZE_RULESET_NOT_STRICT")

        tags = self._ruleset(TAG_LOCK_RULESET)
        tag_ref = tags.get("conditions", {}).get("ref_name", {})
        tag_types = {x.get("type") for x in tags.get("rules", [])}
        if (
            tags.get("target") != "tag" or tags.get("enforcement") != "active"
            or "refs/tags/" + ARCHIVE_PREFIX + "**" not in tag_ref.get("include", [])
            or not {"update", "deletion"}.issubset(tag_types)
            or tags.get("bypass_actors", [])
        ):
            raise ValueError("ARCHIVE_TAG_IMMUTABILITY_RULESET_NOT_STRICT")
        return {
            "environment": ENVIRONMENT,
            "reviewer_protected_environment": True,
            "branch_write_freeze_ruleset_id": branch["id"],
            "archive_tag_lock_ruleset_id": tags["id"],
            "branch_updates_and_creations_frozen": True,
            "archive_tags_update_and_delete_blocked": True,
        }


def run(api: GitHubAPI, *, apply: bool, out_path: Path) -> dict[str, Any]:
    branches = api.paginate("branches")
    open_prs = api.paginate("pulls?state=open")
    candidates, skipped = branch_candidates(branches, open_prs)
    result: dict[str, Any] = {
        "schema_version": "2.0",
        "repo": REPO,
        "mode": "APPLY" if apply else "DRY_RUN",
        "before_branch_count": len(branches),
        "open_pr_count": len(open_prs),
        "candidates": len(candidates),
        "candidate_heads": candidates,
        "skipped": skipped,
        "tagged": [],
        "deleted": [],
        "after_branch_names": [x["name"] for x in branches],
        "archive_controls": None,
        "complete": False,
        "preflight_error": None,
        "unresolved_failures": [],
    }
    if not apply:
        result["changes"] = [
            {**item, "archive_tag": ARCHIVE_PREFIX + item["branch"], "action": "DRY_RUN"}
            for item in candidates
        ]
    else:
        try:
            if open_prs:
                raise ValueError("OPEN_PULL_REQUESTS_MUST_BE_CLOSED_BEFORE_SINGLE_MAIN_ARCHIVE")
            non_main_skipped = [x for x in skipped if x["branch"] != "main"]
            if non_main_skipped:
                raise ValueError("PROTECTED_OR_ACTIVE_BRANCHES_PREVENT_SINGLE_MAIN")
            main = next((x for x in branches if x.get("name") == "main"), None)
            if not main or main.get("protected") is not True:
                raise ValueError("MAIN_MUST_BE_PROTECTED_BEFORE_ARCHIVE")
            reviewed_sha = os.environ.get("FINANCIAL_REVIEWED_MAIN_SHA", "")
            if reviewed_sha != main["commit"]["sha"]:
                raise ValueError("REVIEWED_MAIN_SHA_DOES_NOT_MATCH_LIVE_MAIN")
            result["archive_controls"] = api.verify_archive_controls()
        except Exception as exc:
            result["preflight_error"] = str(exc)
        if result["preflight_error"] is None:
            # Stage 1: tag every exact branch head and read it back. No branch
            # deletion starts unless every inactive head is durably pinned.
            for item in candidates:
                try:
                    name, sha = item["branch"], item["head_sha"]
                    if api.exact_branch_head(name) != sha:
                        raise ValueError("BRANCH_HEAD_MOVED_DURING_FROZEN_INVENTORY")
                    api.tag_archive(name, sha)
                    result["tagged"].append({**item, "tag": ARCHIVE_PREFIX + name})
                except Exception as exc:
                    result["unresolved_failures"].append({
                        **item, "stage": "TAG", "reason": str(exc),
                    })
                    break
            if not result["unresolved_failures"]:
                # Recheck every branch and tag after the full archive phase.
                for item in candidates:
                    if (
                        api.exact_branch_head(item["branch"]) != item["head_sha"]
                        or api.archived_tag_head(item["branch"]) != item["head_sha"]
                    ):
                        result["unresolved_failures"].append({
                            **item, "stage": "PRE_DELETE_READBACK",
                            "reason": "BRANCH_OR_TAG_HEAD_MISMATCH",
                        })
                        break
            # Stage 2: only after every head is tagged and read back, delete refs.
            if not result["unresolved_failures"]:
                for item in candidates:
                    try:
                        api.prune_branch(item["branch"], item["head_sha"])
                        result["deleted"].append(item)
                    except Exception as exc:
                        result["unresolved_failures"].append({
                            **item, "stage": "DELETE", "reason": str(exc),
                        })
                        break
            # Final full inventory, not just re-reading the original candidate list.
            try:
                after = api.paginate("branches")
                after_prs = api.paginate("pulls?state=open")
                result["after_branch_names"] = sorted(x["name"] for x in after)
                result["after_open_pr_count"] = len(after_prs)
                for item in result["tagged"]:
                    if api.archived_tag_head(item["branch"]) != item["head_sha"]:
                        result["unresolved_failures"].append({
                            **item, "stage": "FINAL_TAG_READBACK",
                            "reason": "ARCHIVE_TAG_NOT_DURABLE",
                        })
                result["complete"] = (
                    result["after_branch_names"] == ["main"]
                    and not after_prs
                    and not result["unresolved_failures"]
                    and len(result["deleted"]) == len(candidates)
                )
                if not result["complete"] and not result["unresolved_failures"]:
                    result["unresolved_failures"].append({
                        "stage": "FINAL_INVENTORY",
                        "reason": "REMOTE_REPOSITORY_NOT_SINGLE_MAIN",
                    })
            except Exception as exc:
                result["unresolved_failures"].append({
                    "stage": "FINAL_INVENTORY", "reason": str(exc),
                })
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--out", default="audit/financial_branch_archive.json")
    args = parser.parse_args()
    if args.apply and (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
        or os.environ.get("RUN_FINANCIAL_BRANCH_ARCHIVE") != APPROVAL
        or os.environ.get("FINANCIAL_BRANCH_WRITES_FROZEN") != "true"
        or not os.environ.get("GITHUB_TOKEN")
        or not os.environ.get("FINANCIAL_REVIEWED_MAIN_SHA")
    ):
        raise SystemExit("BRANCH_ARCHIVE_APPLY_REQUIRES_PROTECTED_ENVIRONMENT_AND_EXPLICIT_MAIN_SHA_APPROVAL")
    api = GitHubAPI(REPO, os.environ.get("GITHUB_TOKEN"))
    result = run(api, apply=args.apply, out_path=Path(args.out))
    print(json.dumps({
        "mode": result["mode"],
        "before_branch_count": result["before_branch_count"],
        "open_pr_count": result["open_pr_count"],
        "candidates": result["candidates"],
        "tagged": len(result["tagged"]),
        "deleted": len(result["deleted"]),
        "after_branch_names": result["after_branch_names"],
        "complete": result["complete"],
        "preflight_error": result["preflight_error"],
        "unresolved_failures": result["unresolved_failures"],
    }, ensure_ascii=False))
    if args.apply and not result["complete"]:
        raise SystemExit("ARCHIVE_NOT_COMPLETE__PRESERVED_UNRESOLVED_BRANCHES")


if __name__ == "__main__":
    main()
