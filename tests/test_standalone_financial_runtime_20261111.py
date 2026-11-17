"""Financial standalone transport tests: no external parent or Host imported."""
from copy import deepcopy
import json
from pathlib import Path
from datetime import datetime, timezone
import hashlib
from uuid import uuid4

import pytest

from financial_writing_agent import portfolio_coordinator
from financial_writing_agent.current_admission import build_initial_state, validate_state
from financial_writing_agent.private_research import REQUIRED_MODULES
from financial_writing_agent.writing_kernel import WritingPass
from test_financial_portfolio_execution_20261114 import _executor, _seed
from financial_writing_agent.standalone_runtime import (
    DOMAIN_ID, FinancialAdmissionError, FinancialEffectUnverified,
    _blob_sha, admit_article_action, observe_article,
)
from trusted_provider_testkit import (
    signed_action_authorization, signed_action_effect,
    signed_owner_change_approval, signed_owner_message,
)

ROOT = Path(__file__).resolve().parents[1]


class Provider:
    def __init__(self):
        self.store = {}
        self.artifacts = {}
        self.sources = {}
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

    def read_effect(self, path):
        if path not in self.store:
            return None
        raw = self.store[path]
        return {"content": raw, "blob_sha": _blob_sha(raw)}

    def write_bundle(self, state_path, previous, files):
        old = self.store.get(state_path)
        if previous is None:
            if old is not None:
                raise RuntimeError("create-only conflict")
        elif old is None or _blob_sha(old) != previous:
            raise RuntimeError("conditional CAS conflict")
        for path in files:
            if path != state_path and path in self.store:
                raise RuntimeError("effect receipt create-only conflict")
        if not self.fake_write:
            self.store.update(files)
        return {
            "blob_shas": {path: _blob_sha(content) for path, content in files.items()},
            "commit_ref": "ci:mock-remote-bundle",
        }

    def artifact(self, path):
        if path not in self.artifacts:
            return None
        raw = self.artifacts[path]
        return {"content": raw, "blob_sha": _blob_sha(raw)}

    def source(self, ref):
        return self.sources.get(ref)

    def write_artifact_bundle(self, files):
        batch = dict(files)
        for path, content in batch.items():
            if path in self.artifacts and self.artifacts[path] != content:
                raise RuntimeError("immutable artifact path already contains different bytes")
        self.artifacts.update(batch)
        return {
            "blob_shas": {
                path: _blob_sha(content) for path, content in batch.items()
            }
        }


def proposal(op, *, sha=None, params=None, task_id="solo-article-01", action=None):
    return {
        "schema_version": "1.0", "domain_id": DOMAIN_ID,
        "action_id": action or f"financial-{op.lower()}-{uuid4()}",
        "task_id": task_id,
        "operation": op,
        "expected_state_blob_sha": sha,
        "parameters": params or {},
    }


def run(p, request, auth=None, owner_reader=None):
    return admit_article_action(
        request, state_reader=p.read, cas_writer=p.write,
        authorization_verifier=auth or signed_action_authorization,
        bundle_cas_writer=p.write_bundle,
        effect_attestation_signer=signed_action_effect,
        effect_receipt_reader=p.read_effect,
        artifact_reader=p.artifact,
        source_snapshot_reader=p.source, owner_instruction_reader=owner_reader,
        owner_semantic_verifier=signed_owner_change_approval,
    )


def create(p):
    return run(p, proposal("CREATE_ARTICLE", params={
        "prompt": "中国游戏行业公司经济性报道", "source_refs": [],
    }))


def create_legacy(p):
    """Seed a pre-coordinator owner state for legacy action-admission tests."""
    state = build_initial_state(
        task_id="solo-article-01",
        prompt="历史兼容性测试：财经文章",
        source_refs=[],
        executor_identity="legacy-test-fixture",
    )
    state.pop("portfolio_execution_contract_version")
    state["execution_receipts"][-1]["input_bindings"].pop(
        "portfolio_execution_contract_version"
    )
    raw = json.dumps(state, ensure_ascii=False, sort_keys=True) + "\n"
    p.store["workspaces/articles/solo-article-01/STATE.json"] = raw
    return {
        "operation": "LEGACY_FIXTURE",
        "stage": state["current_stage"],
        "child_state_cas_verified": False,
    }


def _run_portfolio_stage(
    p, *, seed_inputs=None, execute_pass=None, research_audit=None,
    method_catalog_reader=True,
):
    path = "workspaces/articles/solo-article-01/STATE.json"
    if method_catalog_reader is True:
        method_catalog_reader = p.read
    return portfolio_coordinator.run_next_portfolio_stage(
        "solo-article-01",
        seed_inputs=seed_inputs,
        execute_pass=execute_pass,
        research_audit=research_audit,
        state_reader=p.read,
        artifact_reader=p.artifact,
        portfolio_context_reader=p.artifact,
        artifact_bundle_writer=p.write_artifact_bundle,
        authorization_verifier=signed_action_authorization,
        bundle_cas_writer=p.write_bundle,
        effect_attestation_signer=signed_action_effect,
        effect_receipt_reader=p.read_effect,
        source_snapshot_reader=p.source,
        method_catalog_reader=method_catalog_reader,
    )


def _portfolio_research_executor(decision_envelope=None):
    calls = []
    fallback = _executor(calls)

    def execute(node, inputs):
        result = fallback(node, inputs)
        if node == WritingPass.PRIVATE_RESEARCH_SYNTHESIS:
            result["private_research_brief"] = _brief()
        elif node == WritingPass.THESIS_ADJUDICATION:
            result["decision_envelope"] = deepcopy(
                decision_envelope if decision_envelope is not None else _decision()
            )
        return result

    return execute


def test_standalone_can_create_and_observe_real_financial_article_without_parent():
    p = Provider()
    created = create(p)
    assert created["child_state_cas_verified"] is True
    assert created["operation"] == "CREATE_ARTICLE"
    assert created["stage"] == "INTAKE"
    path = "workspaces/articles/solo-article-01/STATE.json"
    assert "caos" not in json.dumps(created).lower()
    state = p.read(path)["state"]
    assert state["task_intake_contract_version"] == "1.0"
    assert state["execution_receipts"][0]["input_bindings"]["task_intake_contract_version"] == "1.0"
    validate_state(state)
    observation = observe_article(
        "solo-article-01", state_reader=p.read, effect_receipt_reader=p.read_effect,
    )
    assert observation["state_blob_sha"] == p.read(path)["blob_sha"]
    assert observation["required_outputs"] == [
        "AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX",
        "PLATFORM_INTERACTION_PACK_DOCX",
    ]
    assert observation["owner_outcome_verified"] is False
    assert observation["authorization_history"]["verified_signed_receipts"] == 1
    assert observation["authorization_history"]["legacy_self_attested_receipts"] == 0
    assert observation["authorization_history"]["verified_effect_receipts"] == 1
    assert created["effect_receipt_readback_verified"] is True
    effect_raw = p.store[created["effect_receipt_ref"]]
    effect = json.loads(effect_raw)
    assert effect["resulting_state_blob_sha"] == created["observed_new_blob_sha"]


def test_article_receipt_preserves_full_signed_provider_authorization_without_raw_request():
    p = Provider()
    create(p)
    state = p.read("workspaces/articles/solo-article-01/STATE.json")["state"]
    receipt = state["execution_receipts"][-1]
    proof = receipt["input_bindings"]["authorization_verification"]
    assert proof["attestation_type"] == "action_authorization"
    assert proof["audience"] == "financial-writing-agent"
    assert proof["authenticated_actor"] == "synthetic-financial-owner"
    assert proof["task_id"] == "solo-article-01"
    assert proof["operation"] == "CREATE_ARTICLE"
    assert proof["expected_state_blob_sha"] is None
    assert receipt["input_bindings"]["authorization_contract_version"] == "1.1"
    assert receipt["input_bindings"]["effect_receipt_ref"].endswith(".effect.json")
    assert len(proof["request_sha256"]) == 64
    assert len(proof["signature"]) == 64
    assert "parameters" not in proof
    assert "prompt" not in proof


def test_observation_reverifies_persisted_provider_signature_and_rejects_tampering():
    p = Provider()
    create(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    state = json.loads(p.store[path])
    proof = state["execution_receipts"][-1]["input_bindings"]["authorization_verification"]
    proof["signature"] = "0" * 64
    p.store[path] = json.dumps(state, ensure_ascii=False, sort_keys=True) + "\n"
    with pytest.raises(FinancialAdmissionError, match="PERSISTED_ACTION_AUTHORIZATION_INVALID"):
        observe_article("solo-article-01", state_reader=p.read, effect_receipt_reader=p.read_effect)


def test_persisted_action_effect_receipt_is_required_and_signature_bound_to_exact_state_bytes():
    p = Provider()
    created = create(p)
    effect_ref = created["effect_receipt_ref"]
    p.store.pop(effect_ref)
    with pytest.raises(FinancialAdmissionError, match="ACTION_EFFECT_RECEIPT_MISSING"):
        observe_article(
            "solo-article-01", state_reader=p.read, effect_receipt_reader=p.read_effect,
        )

    p = Provider()
    created = create(p)
    effect_ref = created["effect_receipt_ref"]
    effect = json.loads(p.store[effect_ref])
    effect["resulting_state_blob_sha"] = "0" * 40
    p.store[effect_ref] = json.dumps(effect, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    with pytest.raises(FinancialAdmissionError, match="PERSISTED_ACTION_EFFECT_INVALID"):
        observe_article(
            "solo-article-01", state_reader=p.read, effect_receipt_reader=p.read_effect,
        )


def test_signed_authorization_v1_0_is_preserved_as_effect_unbound_legacy_history():
    p = Provider()
    create(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    state = p.read(path)["state"]
    bindings = state["execution_receipts"][-1]["input_bindings"]
    effect_ref = bindings["effect_receipt_ref"]
    bindings["authorization_contract_version"] = "1.0"
    bindings.pop("effect_contract_version")
    bindings.pop("effect_receipt_ref")
    p.store.pop(effect_ref)
    p.store[path] = json.dumps(state, ensure_ascii=False, sort_keys=True) + "\n"
    observed = observe_article(
        "solo-article-01", state_reader=p.read, effect_receipt_reader=p.read_effect,
    )
    assert observed["authorization_history"]["verified_signed_receipts"] == 1
    assert observed["authorization_history"]["legacy_effect_unbound_receipts"] == 1
    assert observed["authorization_history"]["verified_effect_receipts"] == 0
    assert observed["authorization_history"]["assurance"].startswith("SIGNED_ACTIONS")


def test_signed_legacy_action_cannot_be_appended_after_effect_bound_history():
    p = Provider()
    create_legacy(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    run(p, proposal("ATTACH_FEEDBACK", sha=p.read(path)["blob_sha"], params={
        "sample": {"sample_type": "USER_REJECTION", "summary": "synthetic first signed action"},
        "system_impact": {"signal_id": "synthetic-legacy-rollback-001", "status": "OPEN",
                          "trigger_sample_type": "USER_REJECTION"},
    }))
    _run_portfolio_stage(p, seed_inputs=_seed())
    state = p.read(path)["state"]
    last = state["execution_receipts"][-1]
    bindings = last["input_bindings"]
    effect_ref = bindings["effect_receipt_ref"]
    bindings["authorization_contract_version"] = "1.0"
    bindings.pop("effect_contract_version")
    bindings.pop("effect_receipt_ref")
    p.store.pop(effect_ref)
    p.store[path] = json.dumps(state, ensure_ascii=False, sort_keys=True) + "\n"
    with pytest.raises(FinancialAdmissionError, match="EFFECT_BOUND_HISTORY_ROLLBACK"):
        observe_article(
            "solo-article-01", state_reader=p.read, effect_receipt_reader=p.read_effect,
        )


def test_persisted_article_action_history_rejects_replayed_action_id_and_nonce():
    from financial_writing_agent.standalone_runtime import (
        _verify_persisted_action_authorization_history,
    )
    p = Provider()
    create(p)
    state = p.read("workspaces/articles/solo-article-01/STATE.json")["state"]
    state["execution_receipts"].append(deepcopy(state["execution_receipts"][-1]))
    with pytest.raises(FinancialAdmissionError, match="ACTION_ID_REPLAYED"):
        _verify_persisted_action_authorization_history(
            state, effect_receipt_reader=p.read_effect,
            current_state_blob_sha=p.read("workspaces/articles/solo-article-01/STATE.json")["blob_sha"],
        )


def test_legacy_self_attested_receipts_are_reported_as_legacy_not_signed():
    p = Provider()
    create(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    state = json.loads(p.store[path])
    bindings = state["execution_receipts"][-1]["input_bindings"]
    bindings.pop("authorization_contract_version")
    bindings.pop("authorization_verification")
    bindings.pop("effect_contract_version")
    bindings.pop("effect_receipt_ref")
    for effect_path in [key for key in p.store if key.endswith(".effect.json")]:
        p.store.pop(effect_path)
    p.store[path] = json.dumps(state, ensure_ascii=False, sort_keys=True) + "\n"
    observed = observe_article(
        "solo-article-01", state_reader=p.read, effect_receipt_reader=p.read_effect,
    )
    assert observed["authorization_history"]["verified_signed_receipts"] == 0
    assert observed["authorization_history"]["legacy_self_attested_receipts"] == 1
    assert observed["authorization_history"]["legacy_effect_unbound_receipts"] == 0
    assert observed["authorization_history"]["assurance"].startswith("SIGNED_ACTIONS")


def test_direct_financial_routing_and_requirement_change_revises_article_only():
    p = Provider()
    create_legacy(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    result = run(p, proposal("CHANGE_REQUIREMENTS", sha=p.read(path)["blob_sha"], params={
        "evidence_ref": "chat://owner/explicit-scoped-instruction",
        "intent_evidence": {
            "intent": "USER_REQUIREMENT", "source_ref": "chat://owner/explicit-scoped-instruction",
            "verbatim_excerpt": "在财经Deep中完整保留本次经济相关公司池",
            "classification_reason": "authenticated user directly requested complete company scope",
        },
        "upserts": [{
            "requirement_id": "deep_companies_full",
            "statement": "在财经Deep中完整保留本次经济相关公司池",
            "scopes": ["FINANCE_DEEP"], "affects_from_stage": "DRAFT",
            "source_kind": "USER_EXPLICIT",
            "evidence_ref": "chat://owner/explicit-scoped-instruction",
        }],
    }), owner_reader=lambda ref: signed_owner_message(
        ref, "在财经Deep中完整保留本次经济相关公司池",
    ))
    assert result["stage"] == "INTAKE"
    assert p.read(path)["state"]["task_requirement_authority"]["revision"] == 1
    assert observe_article(
        "solo-article-01", state_reader=p.read, effect_receipt_reader=p.read_effect,
    )["requirement_revision"] == 1


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


def test_standalone_legacy_intake_to_research_uses_portfolio_coordinator():
    p = Provider()
    create_legacy(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    result = _run_portfolio_stage(p, seed_inputs=_seed())
    assert result["executed_stage"] == "INTAKE"
    assert result["next_stage"] == "RESEARCH"
    assert p.read(path)["state"]["current_stage"] == "RESEARCH"
    assert p.read(path)["state"]["portfolio_execution_contract_version"] == "1.0"


def _decision():
    return json.loads(
        (ROOT / "evals/FINANCIAL_WRITING_KERNEL_DECISION_ENVELOPE_2026-10-15.json")
        .read_text(encoding="utf-8")
    )


def _brief():
    return {
        "contract_version": "1.1", "as_of": datetime.now(timezone.utc).isoformat(),
        "coverage_state": "COMPLETE", "unresolved_gaps": [],
        "modules": {
            name: {"status": "APPLICABLE", "summary": "synthetic test body; not factual market evidence",
                   "evidence_refs": [f"synthetic:source:{i}"]}
            for i, name in enumerate(REQUIRED_MODULES)
        },
    }


def _prepare_sources(p):
    for i, _ in enumerate(REQUIRED_MODULES):
        body = f"本条测试源 {i} 是模拟的公司业务和经济传导原始文本，仅用于检验快照字节和哈希。"
        p.sources[f"synthetic:source:{i}"] = {
            "text": body, "sha256": hashlib.sha256(body.encode()).hexdigest(),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "source_family": "ISSUER_RECORD" if i % 2 else "REGULATOR_RECORD",
        }


def test_standalone_legacy_research_stage_runs_through_coordinator_and_verifies_owner_readback():
    p = Provider()
    create_legacy(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    _run_portfolio_stage(p, seed_inputs=_seed())
    _prepare_sources(p)
    out = _run_portfolio_stage(
        p,
        execute_pass=_portfolio_research_executor(),
    )
    assert out["executed_stage"] == "RESEARCH"
    assert out["next_stage"] == "RESEARCH_AUDIT"
    assert out["owner_admission"]["required_stage_artifact_verified"]["artifact_key"] == "RESEARCH"
    assert out["owner_admission"]["portfolio_stage_artifact_readback"]["owner_outcome_verified"] is True
    validate_state(p.read(path)["state"])


def test_current_financial_task_rejects_direct_internal_stage_advance_without_coordinator_context():
    p = Provider()
    create(p)
    path = "workspaces/articles/solo-article-01/STATE.json"
    before = deepcopy(p.store)
    with pytest.raises(
        FinancialAdmissionError,
        match="FINANCIAL_PORTFOLIO_CONTEXT_REQUIRED_FOR_CURRENT_TASK",
    ):
        run(p, proposal("ADVANCE_STAGE", sha=p.read(path)["blob_sha"]))
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
    create_legacy(p)
    before = deepcopy(p.store)
    req = proposal("ADVANCE_STAGE", sha="a" * 40)
    with pytest.raises(FinancialAdmissionError, match="FINANCIAL_STATE_CHANGED_CONCURRENTLY"):
        run(p, req)
    assert p.store == before


def test_provider_must_return_exact_state_content_not_claimed_sha_only():
    p = Provider()
    create_legacy(p)
    def tampered(path):
        obs = p.read(path)
        obs["content"] = obs["content"].replace('"INTAKE"', '"RESEARCH"')
        return obs
    with pytest.raises(FinancialAdmissionError, match="PROVIDER_STATE_BLOB_SHA_MISMATCH"):
        admit_article_action(
            proposal("ADVANCE_STAGE", sha=p.read("workspaces/articles/solo-article-01/STATE.json")["blob_sha"]),
            state_reader=tampered, cas_writer=p.write,
            authorization_verifier=signed_action_authorization,
            bundle_cas_writer=p.write_bundle, effect_attestation_signer=signed_action_effect,
            effect_receipt_reader=p.read_effect,
        )


def test_unknown_remote_write_outcome_never_becomes_verified_success():
    p = Provider()
    p.fake_write = True
    with pytest.raises(FinancialEffectUnverified, match="FINANCIAL_STATE_READBACK_MISMATCH"):
        run(p, proposal("CREATE_ARTICLE", params={"prompt": "test only", "source_refs": []}))
