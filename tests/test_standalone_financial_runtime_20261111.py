"""Financial standalone transport tests: no external parent or Host imported."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from financial_writing_agent.current_admission import validate_state
from financial_writing_agent.private_research import REQUIRED_MODULES
from financial_writing_agent.standalone_runtime import (
    DOMAIN_ID, FinancialAdmissionError, FinancialEffectUnverified,
    _blob_sha, admit_article_action, observe_article,
)

ROOT = Path(__file__).resolve().parents[1]


class Provider:
    def __init__(self):
        self.store = {}
        self.artifacts = {}
        self.bad_readback = False
        self.fake_write = False

    def read(self, path):
        if self.bad_readback or path not in self.store:
            return None
        raw = self.store[path]
        return {"state": json.loads(raw), "blob_sha": _blob_sha(raw), "content": raw}

    def write(self, path, previous, content):
        old = self.store.get(path)
        if previous is None:
            if old is not None:
                raise RuntimeError("create-only conflict")
        elif old is None or _blob_sha(old) != previous:
            raise RuntimeError("conditional CAS conflict")
        if not self.fake_write:
            self.store[path] = content
        return {"blob_sha": _blob_sha(content), "commit_ref": "ci:mock-remote"}

    def artifact(self, path):
        if path not in self.artifacts:
            return None
        raw = self.artifacts[path]
        return {"content": raw, "blob_sha": _blob_sha(raw)}


def proposal(op, *, sha=None, params=None, task_id="solo-article-01", action=None):
    return {
        "schema_version": "1.0", "domain_id": DOMAIN_ID,
        "action_id": action or f"financial-{op.lower()}-01",
        "task_id": task_id,
        "operation": op,
        "expected_state_blob_sha": sha,
        "parameters": params or {},
    }


def run(p, request, auth=lambda _: True):
    return admit_article_action(
        request, state_reader=p.read, cas_writer=p.write,
        authorization_verifier=auth, artifact_reader=p.artifact,
    )


def create(p):
    return run(p, proposal("CREATE_ARTICLE", params={
        "prompt": "中国跨境电商公司经济性报道", "source_refs": [],
    }))


def test_standalone_can_create_and_observe_real_financial_article_without_parent():
    p = Provider()
    created = create(p)
    assert created["child_state_cas_verified"] is True
    assert created["operation"] == "CREATE_ARTICLE"
    assert created["stage"] == "INTAKE"
    path = "workspaces/articles/solo-article-01/STATE.json"
    assert "caos" not in json.dumps(created).lower()
    state = p.read(path)["state"]
    validate_state(state)
    observation = observe_article("solo-article-01", state_reader=p.read)
    assert observation["state_blob_sha"] == p.read(path)["blob_sha"]
    assert observation["required_outputs"] == [
        "AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX",
        "PLATFORM_INTERACTION_PACK_DOCX",
    ]
    assert observation["owner_outcome_verified"] is False


def test_direct_financial_routing_and_requirement_change_revises_article_only():
    p = Provider()
    create(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    result = run(p, proposal("CHANGE_REQUIREMENTS", sha=p.read(path)["blob_sha"], params={
        "evidence_ref": "chat://owner/explicit-scoped-instruction",
        "upserts": [{
            "requirement_id": "deep_companies_full",
            "statement": "在财经Deep中完整保留本次经济相关公司池",
            "scopes": ["FINANCE_DEEP"], "affects_from_stage": "DRAFT",
            "source_kind": "USER_EXPLICIT",
            "evidence_ref": "chat://owner/explicit-scoped-instruction",
        }],
    }))
    assert result["stage"] == "INTAKE"
    assert p.read(path)["state"]["task_requirement_authority"]["revision"] == 1
    assert observe_article("solo-article-01", state_reader=p.read)["requirement_revision"] == 1


def test_standalone_feedback_stays_on_single_current_owner_article():
    p = Provider()
    create(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    result = run(p, proposal("ATTACH_FEEDBACK", sha=p.read(path)["blob_sha"], params={
        "sample": {"sample_type": "USER_REJECTION", "summary": "正文没有解释公司利润差异"},
        "system_impact": {"signal_id": "synthetic-feedback-001", "status": "OPEN",
                          "trigger_sample_type": "USER_REJECTION"},
    }))
    assert result["child_state_cas_verified"] is True
    state = p.read(path)["state"]
    assert len(state["learning_evidence"]) == 1
    assert state["open_system_impact"][0]["status"] == "OPEN"


def test_standalone_advance_from_intake_to_research():
    p = Provider()
    create(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    result = run(p, proposal("ADVANCE_STAGE", sha=p.read(path)["blob_sha"]))
    assert result["stage"] == "RESEARCH"
    assert result["required_stage_artifact_verified"] is None


def _decision():
    return json.loads(
        (ROOT / "evals/FINANCIAL_WRITING_KERNEL_DECISION_ENVELOPE_2026-10-15.json")
        .read_text(encoding="utf-8")
    )


def _brief():
    return {
        "contract_version": "1.1", "as_of": "2026-11-11T18:00:00+08:00",
        "coverage_state": "COMPLETE", "unresolved_gaps": [],
        "modules": {
            name: {"status": "APPLICABLE", "summary": "synthetic test body; not factual market evidence",
                   "evidence_refs": ["synthetic:test"]}
            for name in REQUIRED_MODULES
        },
    }


def research_proposal(p, artifact_path=None, fake_sha=None):
    path = "workspaces/articles/solo-article-01/STATE.json"
    artifact = artifact_path or "workspaces/articles/solo-article-01/stages/RESEARCH.json"
    content = b'{"synthetic":"source"}\n'
    p.artifacts[artifact] = content
    return proposal("ADVANCE_STAGE", sha=p.read(path)["blob_sha"], params={
        "decision_envelope": _decision(), "private_research_brief": _brief(),
        "artifact_key": "RESEARCH", "artifact_path": artifact,
        "artifact_blob_sha": fake_sha or _blob_sha(content),
    })


def test_standalone_research_artifact_bytes_checked_before_stage_commit():
    p = Provider()
    create(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    run(p, proposal("ADVANCE_STAGE", sha=p.read(path)["blob_sha"]))
    req = research_proposal(p)
    out = run(p, req)
    assert out["stage"] == "RESEARCH_AUDIT"
    assert out["required_stage_artifact_verified"]["artifact_key"] == "RESEARCH"
    validate_state(p.read(path)["state"])


def test_forged_artifact_digest_does_not_advance_financial_workflow():
    p = Provider()
    create(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    run(p, proposal("ADVANCE_STAGE", sha=p.read(path)["blob_sha"]))
    req = research_proposal(p, fake_sha="f" * 40)
    before = deepcopy(p.store)
    with pytest.raises(FinancialAdmissionError, match="FINANCIAL_STAGE_ARTIFACT_BYTES_SHA_MISMATCH"):
        run(p, req)
    assert p.store == before


@pytest.mark.parametrize("bad", [
    {"domain_id": "cognition-agent-os"},
    {"operation": "MODIFY_PARENT"},
    {"task_id": "../other"},
    {"action_id": "../malformed"},
    {"expected_state_blob_sha": "a" * 40},
    {"parameters": {"_current_admission_token": "bypass"}},
])
def test_malformed_and_parent_actions_are_not_standalone_permissions(bad):
    p = Provider()
    req = proposal("CREATE_ARTICLE", params={"prompt": "test", "source_refs": []})
    req.update(bad)
    with pytest.raises(FinancialAdmissionError):
        run(p, req)
    assert p.store == {}


@pytest.mark.parametrize("verifier, writer", [
    (None, True),
    (lambda _: False, True),
    (lambda _: True, False),
])
def test_no_user_permission_or_provider_cas_means_no_financial_mutation(verifier, writer):
    p = Provider()
    with pytest.raises(FinancialAdmissionError):
        admit_article_action(
            proposal("CREATE_ARTICLE", params={"prompt": "some topic", "source_refs": []}),
            state_reader=p.read, cas_writer=p.write if writer else None,
            authorization_verifier=verifier,
        )
    assert not p.store


def test_stale_state_blob_blocks_late_requirements_without_write():
    p = Provider()
    create(p)
    before = deepcopy(p.store)
    req = proposal("ADVANCE_STAGE", sha="a" * 40)
    with pytest.raises(FinancialAdmissionError, match="FINANCIAL_STATE_CHANGED_CONCURRENTLY"):
        run(p, req)
    assert p.store == before


def test_provider_must_return_exact_state_content_not_claimed_sha_only():
    p = Provider()
    create(p)
    def tampered(path):
        obs = p.read(path)
        obs["content"] = obs["content"].replace('"INTAKE"', '"RESEARCH"')
        return obs
    with pytest.raises(FinancialAdmissionError, match="PROVIDER_STATE_BLOB_SHA_MISMATCH"):
        admit_article_action(
            proposal("ADVANCE_STAGE", sha=p.read("workspaces/articles/solo-article-01/STATE.json")["blob_sha"]),
            state_reader=tampered, cas_writer=p.write, authorization_verifier=lambda _: True,
        )


def test_unknown_remote_write_outcome_never_becomes_verified_success():
    p = Provider()
    p.fake_write = True
    with pytest.raises(FinancialEffectUnverified, match="FINANCIAL_STATE_READBACK_MISMATCH"):
        run(p, proposal("CREATE_ARTICLE", params={"prompt": "test only", "source_refs": []}))
