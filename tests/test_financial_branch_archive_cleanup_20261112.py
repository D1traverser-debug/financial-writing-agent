"""Branch compression must never erase history or active/changed refs."""
from pathlib import Path
import pytest
from scripts.branch_archive_cleanup import branch_candidates, run, GitHubAPI, REPO

A = "a"*40
B = "b"*40
C = "c"*40


def test_main_protected_open_pr_excluded_and_archive_candidates_keep_heads():
    branches = [
        {"name":"main","commit":{"sha":A},"protected":False},
        {"name":"article/in-progress","commit":{"sha":B},"protected":False},
        {"name":"repair/merged","commit":{"sha":C},"protected":False},
        {"name":"release/protected","commit":{"sha":A},"protected":True},
        {"name":"tmp/orphan","commit":{"sha":"e"*40},"protected":False},
    ]
    prs=[{"head":{"ref":"article/in-progress","repo":{"full_name":REPO}}}]
    candidates, skipped = branch_candidates(branches, prs, [
        {"merged_at":"2026-11-12T00:00:00Z","base":{"ref":"main"},
         "head":{"ref":"repair/merged","sha":C}}
    ])
    assert candidates == [{"branch":"repair/merged","head_sha":C}]
    assert len(skipped) == 4
    assert any(x["reason"].startswith("NO_EXACT_MERGED_PR") for x in skipped)


def test_duplicate_or_untrustworthy_branch_metadata_fails_closed():
    with pytest.raises(ValueError):
        branch_candidates([{"name":"main","commit":{"sha":"bad"},"protected":False}], [], [])
    with pytest.raises(ValueError):
        branch_candidates([{"name":"main","commit":{"sha":A}},{"name":"main","commit":{"sha":A}}], [], [])


def test_cross_repository_request_rejected():
    with pytest.raises(ValueError):
        GitHubAPI("D1traverser-debug/cognition-agent-os", "fake")


class SimulatedAPI:
    def __init__(self, changed=False, fail=False):
        self.branches={"main":A,"test/old":B,"article/active":C}
        self.tags={}
        self.changed=changed
        self.fail=fail
    def paginate(self,suffix):
        assert suffix == "branches"
        return [{"name":k,"commit":{"sha":v},"protected":False}
                for k,v in self.branches.items()]
    def call(self,method,path,payload=None):
        if method=="GET" and path.endswith("pulls?state=open&per_page=100&page=1"):
            return [{"head":{"ref":"article/active","repo":{"full_name":REPO}}}]
        if method=="GET" and path.endswith("pulls?state=closed&per_page=100&page=1"):
            return [{"merged_at":"2026-11-12T00:00:00Z","base":{"ref":"main"},
                     "head":{"ref":"test/old","sha":B}}]
        raise RuntimeError(path)
    def exact_branch_head(self,name):
        return ("f"*40 if self.changed and name=="test/old"
                else self.branches.get(name))
    def tag_archive(self,name,sha):
        assert self.exact_branch_head(name)==sha
        self.tags[name]=sha
    def prune_branch(self,name,sha):
        assert name!="main"
        assert self.tags.get(name)==sha
        if self.fail: raise RuntimeError("permission denied")
        del self.branches[name]


def test_dry_run_retains_all_branches_and_no_tags(tmp_path):
    api=SimulatedAPI()
    outcome=run(api,apply=False,out_path=tmp_path/"audit.json")
    assert outcome["total_archived_and_pruned"]==0
    assert len(api.branches)==3 and api.tags=={}


def test_real_apply_mocks_archive_then_delete_only_inactive_branch(tmp_path):
    api=SimulatedAPI()
    outcome=run(api,apply=True,out_path=tmp_path/"audit.json")
    assert outcome["total_archived_and_pruned"]==1
    assert api.tags["test/old"]==B
    assert set(api.branches)=={"main","article/active"}


def test_moved_head_or_delete_failure_keeps_branch(tmp_path):
    api=SimulatedAPI(changed=True)
    res=run(api,apply=True,out_path=tmp_path/"audit.json")
    assert res["changes"][0]["action"]=="SKIP_MOVED_HEAD"
    assert "test/old" in api.branches
    api=SimulatedAPI(fail=True)
    res=run(api,apply=True,out_path=tmp_path/"audit2.json")
    assert res["changes"][0]["action"]=="FAILED_KEEP_BRANCH"
    assert "test/old" in api.branches and api.tags["test/old"]==B
