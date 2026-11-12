"""Branch compression must preserve every head and fail closed on unsafe state."""
from pathlib import Path
import pytest
from scripts.branch_archive_cleanup import branch_candidates, run, GitHubAPI, REPO

A = "a"*40
B = "b"*40
C = "c"*40


def test_main_protected_open_pr_excluded_and_archive_candidates_keep_heads():
    branches = [
        {"name":"main","commit":{"sha":A},"protected":True},
        {"name":"article/in-progress","commit":{"sha":B},"protected":False},
        {"name":"repair/merged","commit":{"sha":C},"protected":False},
        {"name":"release/protected","commit":{"sha":A},"protected":True},
        {"name":"tmp/orphan","commit":{"sha":"e"*40},"protected":False},
    ]
    prs=[{"head":{"ref":"article/in-progress","repo":{"full_name":REPO}}}]
    candidates, skipped = branch_candidates(branches, prs)
    assert candidates == [
        {"branch":"repair/merged","head_sha":C},
        {"branch":"tmp/orphan","head_sha":"e"*40},
    ]
    assert len(skipped) == 3


def test_duplicate_or_untrustworthy_branch_metadata_fails_closed():
    with pytest.raises(ValueError):
        branch_candidates([{"name":"main","commit":{"sha":"bad"},"protected":False}], [])
    with pytest.raises(ValueError):
        branch_candidates([{"name":"main","commit":{"sha":A}},{"name":"main","commit":{"sha":A}}], [])


def test_cross_repository_request_rejected():
    with pytest.raises(ValueError):
        GitHubAPI("D1traverser-debug/cognition-agent-os", "fake")


class SimulatedAPI:
    def __init__(self, changed=False, fail=False, open_prs=None):
        self.branches={"main":A,"test/old":B,"article/active":C}
        self.tags={}
        self.changed=changed
        self.fail=fail
        self.open_prs = open_prs or []
        self.mutation_order = []
    def paginate(self,suffix):
        if suffix == "branches":
            return [{"name":k,"commit":{"sha":v},
                     "protected": k == "main"}
                    for k,v in self.branches.items()]
        if suffix == "pulls?state=open":
            return list(self.open_prs)
        raise AssertionError("unexpected collection: " + suffix)
    def exact_branch_head(self,name):
        return ("f"*40 if self.changed and name=="test/old"
                else self.branches.get(name))
    def archived_tag_head(self,name):
        return self.tags.get(name)
    def verify_archive_controls(self):
        self.mutation_order.append("verify_controls")
        return {"branch_updates_and_creations_frozen": True,
                "archive_tags_update_and_delete_blocked": True}
    def tag_archive(self,name,sha):
        assert self.exact_branch_head(name)==sha
        self.tags[name]=sha
        self.mutation_order.append("tag:" + name)
    def prune_branch(self,name,sha):
        assert name!="main"
        assert self.tags.get(name)==sha
        if self.fail: raise RuntimeError("permission denied")
        self.mutation_order.append("delete:" + name)
        del self.branches[name]


def test_dry_run_retains_all_branches_and_no_tags(tmp_path):
    api=SimulatedAPI()
    outcome=run(api,apply=False,out_path=tmp_path/"audit.json")
    assert outcome["complete"] is False
    assert outcome["mode"] == "DRY_RUN"
    assert outcome["candidates"] == 2
    assert outcome["tagged"] == [] and outcome["deleted"] == []
    assert len(api.branches)==3 and api.tags=={}
    assert outcome["after_branch_names"] == ["main","test/old","article/active"]


def test_apply_tags_every_exact_head_before_deleting_and_finishes_single_main(tmp_path, monkeypatch):
    monkeypatch.setenv("FINANCIAL_REVIEWED_MAIN_SHA", A)
    api=SimulatedAPI()
    outcome=run(api,apply=True,out_path=tmp_path/"audit.json")
    assert outcome["complete"] is True
    assert outcome["after_branch_names"] == ["main"]
    assert outcome["tagged"] == [
        {"branch":"test/old","head_sha":B,"tag":"archive/financial-20261112/test/old"},
        {"branch":"article/active","head_sha":C,"tag":"archive/financial-20261112/article/active"},
    ]
    assert api.tags == {"test/old":B,"article/active":C}
    assert api.mutation_order.index("tag:article/active") < api.mutation_order.index("delete:test/old")
    assert api.mutation_order.index("tag:test/old") < api.mutation_order.index("delete:test/old")


def test_open_pull_request_blocks_all_deletion_and_preserves_every_branch(tmp_path, monkeypatch):
    monkeypatch.setenv("FINANCIAL_REVIEWED_MAIN_SHA", A)
    prs=[{"head":{"ref":"article/active","repo":{"full_name":REPO}}}]
    api=SimulatedAPI(open_prs=prs)
    result=run(api,apply=True,out_path=tmp_path/"audit.json")
    assert result["complete"] is False
    assert result["preflight_error"] == "OPEN_PULL_REQUESTS_MUST_BE_CLOSED_BEFORE_SINGLE_MAIN_ARCHIVE"
    assert set(api.branches) == {"main","test/old","article/active"}
    assert api.tags == {} and api.mutation_order == []


def test_moved_head_or_delete_failure_keeps_unarchived_branch(tmp_path, monkeypatch):
    monkeypatch.setenv("FINANCIAL_REVIEWED_MAIN_SHA", A)
    api=SimulatedAPI(changed=True)
    res=run(api,apply=True,out_path=tmp_path/"audit.json")
    assert res["complete"] is False
    assert "test/old" in api.branches
    assert not res["deleted"]
    api=SimulatedAPI(fail=True)
    res=run(api,apply=True,out_path=tmp_path/"audit2.json")
    assert res["complete"] is False
    assert "test/old" in api.branches and api.tags["test/old"]==B
    assert not res["deleted"]
