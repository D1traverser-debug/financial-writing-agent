#!/usr/bin/env python3
"""Archive (tag) former Financial branches before removing their branch refs.

A GitHub PR is a permanent review record; no API action can or should rewrite it.
This procedure is a one-time, provider-readback, fail-closed Financial MAIN
branch consolidation. It never touches CAOS and never loses a former head SHA.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

ARCHIVE_PREFIX = "archive/financial-20261112/"
APPROVAL = "I_APPROVE_ARCHIVE_AND_PRUNE"
REPO = "D1traverser-debug/financial-writing-agent"


def branch_candidates(
    branches: list[dict[str, Any]],
    open_prs: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Do not prune main, protected or any still-open PR head; no implicit moves."""
    protected = {
        p.get("head", {}).get("ref")
        for p in open_prs if p.get("head", {}).get("repo", {}).get("full_name") == REPO
    }
    candidates, skipped = [], []
    seen: set[str] = set()
    for b in branches:
        name = b.get("name")
        sha = b.get("commit", {}).get("sha")
        if not isinstance(name, str) or not isinstance(sha, str) or len(sha) != 40:
            raise ValueError("BRANCH_HYGIENE_INVALID_PROVIDER_DATA")
        if name in seen:
            raise ValueError("BRANCH_HYGIENE_DUPLICATE_BRANCH")
        seen.add(name)
        row = {"branch": name, "head_sha": sha}
        if name == "main" or b.get("protected") is True or name in protected:
            skipped.append({**row, "reason": "MAIN_OR_PROTECTED_OR_ACTIVE_PR"})
        else:
            candidates.append(row)
    return candidates, skipped


class GitHubAPI:
    def __init__(self, repo: str, token: str | None):
        if repo != REPO:
            raise ValueError("branch archive is restricted to Financial repository only")
        self.repo, self.token = repo, token

    def call(self, method: str, path: str, payload: dict[str, Any] | None = None):
        if not path.startswith("/repos/" + REPO + "/"):
            raise ValueError("CROSS_REPOSITORY_MUTATION_FORBIDDEN")
        from urllib.request import Request
        url = "https://api.github.com" + path
        raw = json.dumps(payload).encode("utf-8") if payload is not None else None
        h = {"Accept": "application/vnd.github+json",
             "X-GitHub-Api-Version": "2022-11-28",
             "User-Agent": "financial-branch-archive-guard"}
        if self.token:
            h["Authorization"] = "Bearer " + self.token
        request = Request(url, data=raw, headers=h, method=method)
        try:
            with urlopen(request, timeout=20) as resp:
                contents = resp.read()
                return json.loads(contents) if contents else None
        except HTTPError as exc:
            if exc.code == 404:
                return None
            raise RuntimeError(f"GITHUB_{method}_{path}_HTTP_{exc.code}") from exc

    def paginate(self, suffix):
        items = []
        for page in range(1, 100):
            values = self.call("GET", f"/repos/{self.repo}/{suffix}?per_page=100&page={page}")
            if not isinstance(values, list):
                raise ValueError("BRANCH_HYGIENE_BAD_GITHUB_COLLECTION")
            items.extend(values)
            if len(values) < 100:
                return items
        raise ValueError("BRANCH_HYGIENE_PAGINATION_EXCEEDED")

    def exact_branch_head(self, name: str) -> str | None:
        ref = self.call("GET", f"/repos/{self.repo}/git/ref/heads/{quote(name, safe='/')}")
        if ref is None:
            return None
        return ref.get("object", {}).get("sha")

    def archived_tag_head(self, name: str) -> str | None:
        tag = self.call("GET", f"/repos/{self.repo}/git/ref/tags/{quote(ARCHIVE_PREFIX + name, safe='/')}")
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
        self.call("DELETE", f"/repos/{self.repo}/git/refs/heads/{quote(name, safe='/')}")
        if self.exact_branch_head(name) is not None:
            raise RuntimeError("BRANCH_DELETE_READBACK_FAILED")


def run(api: GitHubAPI, *, apply: bool, out_path: Path) -> dict[str, Any]:
    branches = api.paginate("branches")
    open_prs: list[dict[str, Any]] = []
    # The collection uses a fixed query string; keep pagination explicit.
    for page in range(1, 20):
        values = api.call(
            "GET", f"/repos/{REPO}/pulls?state=open&per_page=100&page={page}",
        )
        if not isinstance(values, list):
            raise ValueError("BRANCH_HYGIENE_OPEN_PR_LIST_UNAVAILABLE")
        open_prs.extend(values)
        if len(values) < 100:
            break
    candidates, skipped = branch_candidates(branches, open_prs)
    changes: list[dict[str, str]] = []
    for item in candidates:
        name, sha = item["branch"], item["head_sha"]
        archive_tag = ARCHIVE_PREFIX + name
        if not apply:
            changes.append({**item, "archive_tag": archive_tag, "action": "DRY_RUN"})
            continue
        try:
            if api.exact_branch_head(name) != sha:
                changes.append({**item, "action": "SKIP_MOVED_HEAD"})
                continue
            api.tag_archive(name, sha)
            api.prune_branch(name, sha)
            changes.append({**item, "archive_tag": archive_tag, "action": "ARCHIVED_AND_PRUNED"})
        except Exception as exc:
            changes.append({**item, "archive_tag": archive_tag,
                            "action": "FAILED_KEEP_BRANCH", "reason": str(exc)})
    # Every non-main candidate must be verified by a fresh HEAD GET after the
    # attempted deletion. Never infer branch disappearance from HTTP 204 alone.
    still_present = [
        item["branch"] for item in candidates
        if apply and api.exact_branch_head(item["branch"]) is not None
    ]
    result = {
        "schema_version": "1.0", "repo": REPO, "mode": "APPLY" if apply else "DRY_RUN",
        "candidate_branch_heads_still_present": still_present,
        "observed_branch_count": len(branches), "open_pr_count": len(open_prs),
        "candidates": len(candidates), "skipped": skipped, "changes": changes,
        "total_archived_and_pruned": sum(x["action"] == "ARCHIVED_AND_PRUNED" for x in changes),
        "unresolved_failures": [x for x in changes if x["action"] == "FAILED_KEEP_BRANCH"],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    p.add_argument("--out", default="audit/financial_branch_archive.json")
    args = p.parse_args()
    if args.apply and (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
        or os.environ.get("RUN_FINANCIAL_BRANCH_ARCHIVE") != APPROVAL
        or not os.environ.get("GITHUB_TOKEN")
    ):
        raise SystemExit("BRANCH_ARCHIVE_APPLY_REQUIRES_EXPLICIT_MAIN_JOB_AUTHORIZATION")
    api = GitHubAPI(REPO, os.environ.get("GITHUB_TOKEN"))
    result = run(api, apply=args.apply, out_path=Path(args.out))
    print(json.dumps({key: result[key] for key in (
        "mode", "observed_branch_count", "open_pr_count", "candidates",
        "total_archived_and_pruned", "unresolved_failures"
    )}, ensure_ascii=False))
    if result["unresolved_failures"] or (
        args.apply and result["candidate_branch_heads_still_present"]
    ):
        raise SystemExit("ARCHIVE_NOT_COMPLETE__PRESERVED_UNRESOLVED_BRANCHES")


if __name__ == "__main__":
    main()
