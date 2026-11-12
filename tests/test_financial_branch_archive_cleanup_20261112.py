"""Adversarial tests for manifest-bound, two-phase branch archive/prune."""
import json
from pathlib import Path
import pytest

from scripts.branch_archive_cleanup import (
    GitHubAPI, REPO, archive_only, branch_rows, create_plan, prune_only, sha256,
)

A, B, C, D = "a"*40, "b"*40, "c"*40, "d"*40


class FakeAPI:
    def __init__(self, *, deletion_frozen=True, open_prs=None):
        self.branches = {
            "main": {"sha": A, "protected": True},
            "old/one": {"sha": B, "protected": False},
            "old/two": {"sha": C, "protected": False},
        }
        self.tags = {}
        self.open_prs = list(open_prs or [])
        self.deletion_frozen = deletion_frozen
        self.calls = []
        self.open_pr_reads = 0
        self.add_pr_on_read = None
        self.move_main_on_read = None
        self.main_reads = 0
        self.ambiguous_delete = set()

    def verify_controls(self, phase):
        self.calls.append("controls:" + phase)
        return {
            "branch_ruleset_id": 11,
            "tag_ruleset_id": 22,
            "branch_rule_types": (
                ["creation", "update", "deletion"] if self.deletion_frozen
                else ["creation", "update"]
            ),
            "tag_rule_types": ["update", "deletion"],
        }

    def paginate(self, suffix):
        if suffix == "branches":
            return [
                {"name": name, "commit": {"sha": data["sha"]},
                 "protected": data["protected"]}
                for name, data in sorted(self.branches.items())
            ]
        if suffix == "pulls?state=open":
            self.open_pr_reads += 1
            if self.add_pr_on_read == self.open_pr_reads:
                self.open_prs = [{
                    "head": {"ref": "old/two", "repo": {"full_name": REPO}}
                }]
            return list(self.open_prs)
        raise AssertionError("unexpected collection " + suffix)

    def branch_head(self, name):
        if name == "main":
            self.main_reads += 1
            if self.move_main_on_read == self.main_reads:
                self.branches["main"]["sha"] = D
        data = self.branches.get(name)
        return data["sha"] if data else None

    def tag_head(self, name):
        return self.tags.get(name)

    def tag_branch_head(self, name, sha):
        self.calls.append("tag:" + name)
        old = self.tags.get(name)
        if old is not None and old != sha:
            raise ValueError("tag conflict")
        self.tags[name] = sha

    def delete_branch(self, name, sha):
        self.calls.append("delete:" + name)
        assert self.branch_head(name) == sha
        assert self.tag_head(name) == sha
        del self.branches[name]
        if name in self.ambiguous_delete:
            return {"branch": name, "status": "AMBIGUOUS_RESPONSE_BUT_ABSENCE_AND_TAG_VERIFIED"}
        return {"branch": name, "status": "DELETE_AND_READBACK_VERIFIED"}


class RulesetAPI(GitHubAPI):
    def __init__(self, *, omit_bypass=False, bypass=None, phase_deletion=True):
        self.token = "synthetic-test-token"
        self.omit_bypass = omit_bypass
        self.bypass = bypass or []
        self.phase_deletion = phase_deletion

    def paginate(self, suffix):
        assert suffix == "rulesets?includes_parents=true"
        return [{"id": 11, "name": "Financial archive write freeze"},
                {"id": 22, "name": "Financial archive tag lock"}]

    def call(self, method, path, payload=None, *, allow_404=False):
        if "/environments/" in path:
            return {"protection_rules": [{"type": "required_reviewers", "reviewers": [{"type":"User","id":1}]}]}
        if "/rulesets/11?" in path:
            result = {
                "id": 11, "target": "branch", "enforcement": "active",
                "conditions": {"ref_name": {"include": ["~ALL"], "exclude": ["refs/heads/main"]}},
                "rules": [{"type":"creation"},{"type":"update"}] +
                         ([{"type":"deletion"}] if self.phase_deletion else []),
            }
            if not self.omit_bypass:
                result["bypass_actors"] = self.bypass
            return result
        if "/rulesets/22?" in path:
            return {
                "id": 22, "target": "tag", "enforcement": "active",
                "conditions": {"ref_name": {"include": ["refs/tags/archive/financial-20261112/**"]}},
                "rules": [{"type":"update"},{"type":"deletion"}],
                "bypass_actors": [],
            }
        raise AssertionError(path)


def make_plan(tmp_path):
    api = FakeAPI()
    path = tmp_path / "plan.json"
    plan = create_plan(api, out=path)
    return api, path, plan


def test_branch_inventory_rejects_duplicate_or_invalid_metadata():
    with pytest.raises(ValueError):
        branch_rows([{"name":"main","commit":{"sha":"bad"}}])
    with pytest.raises(ValueError):
        branch_rows([
            {"name":"main","commit":{"sha":A}},
            {"name":"main","commit":{"sha":A}},
        ])


def test_plan_is_stable_exact_head_manifest_and_has_no_mutation(tmp_path):
    api, path, plan = make_plan(tmp_path)
    assert plan["manifest"]["main_sha"] == A
    assert plan["manifest"]["candidate_heads"] == [
        {"branch":"old/one","head_sha":B},
        {"branch":"old/two","head_sha":C},
    ]
    assert plan["manifest_sha256"] == sha256(plan["manifest"])
    assert plan["plan_status"] == "READY_FOR_REVIEW__NO_MUTATION"
    assert not api.tags
    assert not any(x.startswith("delete:") for x in api.calls)
    assert json.loads(path.read_text())["manifest_sha256"] == plan["manifest_sha256"]


def test_archive_phase_tags_all_exact_heads_and_deletes_nothing(tmp_path):
    api, plan_path, plan = make_plan(tmp_path)
    report = archive_only(
        api, manifest_path=plan_path, approved=plan["manifest_sha256"],
        out=tmp_path / "archive.json",
    )
    assert report["archive_status"] == "ALL_TAGS_VERIFIED__NO_BRANCHES_DELETED"
    assert api.tags == {"old/one":B, "old/two":C}
    assert set(api.branches) == {"main","old/one","old/two"}
    assert not any(x.startswith("delete:") for x in api.calls)


def test_archive_phase_rejects_manifest_change_before_any_tag(tmp_path):
    api, plan_path, plan = make_plan(tmp_path)
    api.branches["old/one"]["sha"] = D
    with pytest.raises(ValueError, match="CURRENT_INVENTORY_DIFFERS"):
        archive_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                     out=tmp_path / "archive.json")
    assert api.tags == {}
    assert set(api.branches) == {"main","old/one","old/two"}


def test_archive_phase_rejects_wrong_approved_digest(tmp_path):
    api, plan_path, plan = make_plan(tmp_path)
    with pytest.raises(ValueError, match="APPROVED_MANIFEST_SHA256_MISMATCH"):
        archive_only(api, manifest_path=plan_path, approved="0"*64,
                     out=tmp_path / "archive.json")
    assert api.tags == {}


def test_prune_refuses_while_deletion_rule_is_still_frozen(tmp_path):
    api, plan_path, plan = make_plan(tmp_path)
    archive_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                 out=tmp_path / "archive.json")
    with pytest.raises(ValueError, match="REMOVE_ONLY_DELETION_RULE"):
        prune_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                   out=tmp_path / "prune.json")
    assert set(api.branches) == {"main","old/one","old/two"}


def test_prune_after_deletion_rule_removed_keeps_tags_and_leaves_only_main(tmp_path):
    api, plan_path, plan = make_plan(tmp_path)
    archive_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                 out=tmp_path / "archive.json")
    api.deletion_frozen = False
    report = prune_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                        out=tmp_path / "prune.json")
    assert report["complete"] is True
    assert report["after_branch_names"] == ["main"]
    assert api.tags == {"old/one":B, "old/two":C}
    assert [x for x in api.calls if x.startswith("delete:")] == ["delete:old/one","delete:old/two"]


def test_prune_refuses_a_moved_branch_even_when_old_tag_is_preserved(tmp_path):
    api, plan_path, plan = make_plan(tmp_path)
    archive_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                 out=tmp_path / "archive.json")
    api.deletion_frozen = False
    api.branches["old/two"]["sha"] = D
    with pytest.raises(ValueError, match="UNPLANNED_OR_MOVED_BRANCH"):
        prune_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                   out=tmp_path / "prune.json")
    assert set(api.branches) == {"main","old/one","old/two"}


def test_open_pr_appearing_during_prune_stops_next_delete(tmp_path):
    api, plan_path, plan = make_plan(tmp_path)
    archive_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                 out=tmp_path / "archive.json")
    api.deletion_frozen = False
    api.add_pr_on_read = api.open_pr_reads + 3
    report = prune_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                        out=tmp_path / "prune.json")
    assert report["complete"] is False
    assert "old/two" in api.branches
    assert api.tags["old/two"] == C


def test_main_moving_during_prune_prevents_false_completion(tmp_path):
    api, plan_path, plan = make_plan(tmp_path)
    archive_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                 out=tmp_path / "archive.json")
    api.deletion_frozen = False
    api.move_main_on_read = api.main_reads + 2
    report = prune_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                        out=tmp_path / "prune.json")
    assert report["complete"] is False
    assert report["main_sha_after"] == D


def test_ambiguous_delete_response_is_accepted_only_after_absence_and_tag_readback(tmp_path):
    api, plan_path, plan = make_plan(tmp_path)
    archive_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                 out=tmp_path / "archive.json")
    api.deletion_frozen = False
    api.ambiguous_delete.add("old/one")
    report = prune_only(api, manifest_path=plan_path, approved=plan["manifest_sha256"],
                        out=tmp_path / "prune.json")
    assert report["complete"] is True
    assert report["deleted"][0]["status"] == "AMBIGUOUS_RESPONSE_BUT_ABSENCE_AND_TAG_VERIFIED"


def test_ruleset_bypass_actors_must_be_visible_and_empty():
    with pytest.raises(ValueError, match="BYPASS_ACTORS_NOT_VISIBLE"):
        RulesetAPI(omit_bypass=True).verify_controls("PLAN")
    with pytest.raises(ValueError, match="BYPASS_ACTORS_MUST_BE_EMPTY"):
        RulesetAPI(bypass=[{"actor_type":"Integration","actor_id":7,"bypass_mode":"always"}]).verify_controls("PLAN")


def test_ruleset_deletion_rule_is_required_for_plan_but_forbidden_for_prune():
    with pytest.raises(ValueError, match="DELETION_MUST_BE_FROZEN"):
        RulesetAPI(phase_deletion=False).verify_controls("PLAN")
    RulesetAPI(phase_deletion=False).verify_controls("PRUNE")
