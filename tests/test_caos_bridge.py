"""Executable CAOS child bridge contract and independent mocked-provider readback.

Mock callbacks certify ONLY the branch's deterministic contract. They do not
represent a live connected CAOS Host, authenticated ChatGPT invocation, or
independent editorial/audience outcome.
"""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from financial_writing_agent.caos_bridge import (
    CAOSChildAdmissionError,
    CAOSChildEffectUnverified,
    PARENT_REPOSITORY,
    _blob_sha,
    admit_parent_article_action,
    observe_article,
)
from financial_writing_agent.current_admission import validate_state


def _request(operation, *, task_id="caos-article-01", sha=None, params=None):
    return {
        "schema_version": "1.0",
        "parent_repository": PARENT_REPOSITORY,
        "goal_id": "goal-abc",
        "goal_revision": 2,
        "action_id": f"caos:{operation}:01",
        "task_id": task_id,
        "operation": operation,
        "expected_state_blob_sha": sha,
        "parameters": params or {},
    }


class SimulatedExactCAS:
    def __init__(self):
        self.files = {}
        self.unknown_result = False
        self.fail_readback = False

    def read(self, path):
        x = self.files.get(path)
        if x is None or self.fail_readback:
            return None
        return {"state": json.loads(x[0]), "blob_sha": x[1]}

    def write(self, path, previous_sha, payload):
        was = self.files.get(path)
        if previous_sha is None:
            if was is not None:
                raise RuntimeError("create-only conflict")
        elif was is None or previous_sha != was[1]:
            raise RuntimeError("CAS conflict")
        sha = _blob_sha(payload)
        self.files[path] = (payload, sha)
        if self.unknown_result:
            return {"blob_sha": "a" * 40}
        return {"blob_sha": sha, "commit_ref": "test-only-commit"}


def _created(provider):
    request = _request("CREATE_ARTICLE", params={"prompt": "财经写作", "source_refs": []})
    return admit_parent_article_action(
        request, state_reader=provider.read, cas_writer=provider.write,
        grant_verifier=lambda proposed: proposed["parent_repository"] == PARENT_REPOSITORY,
    )


def test_caos_bridge_end_to_end_owner_native_create_requirement_and_stage():
    provider = SimulatedExactCAS()
    created = _created(provider)
    assert created["child_state_cas_verified"] is True
    assert created["parent_business_acceptance"] is False
    path = "workspaces/articles/caos-article-01/STATE.json"
    state = provider.read(path)["state"]
    validate_state(state)
    assert state["writing_kernel_version"] == "1.0"

    change = _request(
        "CHANGE_REQUIREMENTS", sha=provider.read(path)["blob_sha"],
        params={
            "evidence_ref": "user://test-scope",
            "upserts": [
                {
                    "requirement_id": "company-comparisons",
                    "statement": "对重要公司做可证伪的经济比较",
                    "scopes": ["FINANCE_DEEP"],
                    "affects_from_stage": "EDITORIAL",
                    "evidence_ref": "user://test-scope",
                    "source_kind": "USER_EXPLICIT",
                }
            ],
        },
    )
    result = admit_parent_article_action(
        change, state_reader=provider.read, cas_writer=provider.write,
        grant_verifier=lambda _: True,
    )
    assert result["resulting_stage"] == "INTAKE"
    assert provider.read(path)["state"]["task_requirement_authority"]["revision"] == 1

    advance = _request("ADVANCE_STAGE", sha=provider.read(path)["blob_sha"])
    result = admit_parent_article_action(
        advance, state_reader=provider.read, cas_writer=provider.write,
        grant_verifier=lambda _: True,
    )
    assert result["resulting_stage"] == "RESEARCH"
    observation = observe_article("caos-article-01", state_reader=provider.read)
    assert observation["stage"] == "RESEARCH"
    assert observation["requirement_revision"] == 1
    assert observation["owner_outcome_independently_verified"] is False
    assert observation["parent_controller_may_rewrite_child_state"] is False


def test_no_external_grant_or_cas_cannot_mutate():
    p = SimulatedExactCAS()
    req = _request("CREATE_ARTICLE", params={"prompt": "研究"})
    for writer, grant in [
        (None, lambda _: True),
        (p.write, None),
        (p.write, lambda _: False),
    ]:
        with pytest.raises(CAOSChildAdmissionError):
            admit_parent_article_action(req, state_reader=p.read, cas_writer=writer, grant_verifier=grant)
    assert p.files == {}


@pytest.mark.parametrize(
    "patch",
    [
        {"parent_repository": "D1traverser-debug/universal-agent-os"},
        {"goal_revision": True},
        {"goal_revision": 0},
        {"action_id": "../bad"},
        {"task_id": "../escape"},
        {"operation": "WRITE_REPO_ARBITRARY"},
        {"parameters": {"_current_admission_token": "bypass"}},
        {"expected_state_blob_sha": "a" * 40},
    ],
)
def test_parent_proposals_do_not_create_grants_or_change_child_scope(patch):
    p = SimulatedExactCAS()
    req = _request("CREATE_ARTICLE", params={"prompt": "财经写作"})
    req.update(patch)
    with pytest.raises(CAOSChildAdmissionError):
        admit_parent_article_action(
            req, state_reader=p.read, cas_writer=p.write,
            grant_verifier=lambda _: True,
        )
    assert p.files == {}


def test_stale_child_sha_fails_before_write_even_if_grant_is_true():
    p = SimulatedExactCAS()
    _created(p)
    req = _request("ADVANCE_STAGE", sha="a" * 40)
    before = deepcopy(p.files)
    with pytest.raises(CAOSChildAdmissionError, match="CHILD_STATE_CHANGED_CONCURRENTLY"):
        admit_parent_article_action(req, state_reader=p.read, cas_writer=p.write, grant_verifier=lambda _: True)
    assert p.files == before


def test_provider_returned_receipt_is_not_enough_without_readback():
    p = SimulatedExactCAS()
    p.unknown_result = True
    req = _request("CREATE_ARTICLE", params={"prompt": "研究"})
    with pytest.raises(CAOSChildEffectUnverified, match="UNVERIFIED_BLOB"):
        admit_parent_article_action(req, state_reader=p.read, cas_writer=p.write, grant_verifier=lambda _: True)


def test_dropped_or_failed_readback_never_becomes_verified_delivery():
    p = SimulatedExactCAS()
    def unreadable_write(path, old, payload):
        receipt = p.write(path, old, payload)
        p.fail_readback = True
        return receipt
    with pytest.raises(CAOSChildEffectUnverified, match="READBACK_MISMATCH"):
        admit_parent_article_action(
            _request("CREATE_ARTICLE", params={"prompt": "研究"}),
            state_reader=p.read, cas_writer=unreadable_write, grant_verifier=lambda _: True,
        )


def test_caos_parent_manifest_matches_real_parent_read_only_contract_shape():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / ".uaos/MANIFEST.json").read_text(encoding="utf-8"))
    adapter = json.loads((root / ".uaos/ADAPTER.json").read_text(encoding="utf-8"))
    caps = json.loads((root / ".uaos/CAPABILITIES.json").read_text(encoding="utf-8"))
    assert manifest["controller"] == adapter["controller"] == PARENT_REPOSITORY + "@main"
    assert manifest["binding"]["adapter_ref"] == ".uaos/ADAPTER.json"
    assert manifest["binding"]["capability_ref"] == ".uaos/CAPABILITIES.json"
    skill = manifest["skill"]["entrypoint"]
    assert skill == "CAOS_SKILL.md" and (root / skill).is_file()
    assert caps["domain_id"] == manifest["domain_id"] == adapter["domain_id"] == "financial_writing"
    ids = [x["capability_id"] for x in caps["capabilities"]]
    assert len(ids) == len(set(ids)) and all(x.isidentifier() for x in ids)
    active = "\n".join(json.dumps(x) for x in (manifest, adapter, caps))
    assert "D1traverser-debug/universal-agent-os" not in active
    assert caps["hosted_cognition_semantics"]["implementation_evidence"] == "NOT_EQUIVALENT_TO_NATIVE_HOST_ACTIVATION"


def test_provider_readback_rejects_bool_integer_type_confusion_despite_claimed_blob_sha():
    """A malicious or buggy state decoder cannot turn 0 into False and be admitted."""
    provider = SimulatedExactCAS()

    def wrong_typed_reader(path):
        observed = provider.read(path)
        if observed:
            observed["state"]["execution_receipts"][-1]["input_bindings"]["task_requirement_revision"] = False
        return observed

    with pytest.raises(CAOSChildEffectUnverified, match="CHILD_PROVIDER_READBACK_MISMATCH"):
        admit_parent_article_action(
            _request("CREATE_ARTICLE", params={"prompt": "财经写作"}),
            state_reader=wrong_typed_reader,
            cas_writer=provider.write,
            grant_verifier=lambda _: True,
        )


def test_unhashable_child_operation_fails_closed_as_admission_error():
    provider = SimulatedExactCAS()
    proposal = _request("CREATE_ARTICLE", params={"prompt": "财经写作"})
    proposal["operation"] = ["CREATE_ARTICLE"]
    with pytest.raises(CAOSChildAdmissionError, match="UNSUPPORTED_CHILD_MUTATION"):
        admit_parent_article_action(
            proposal,
            state_reader=provider.read,
            cas_writer=provider.write,
            grant_verifier=lambda _: True,
        )
    assert provider.files == {}
