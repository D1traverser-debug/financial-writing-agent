"""Adversarial requirement-authority semantics: source bytes alone != owner meaning."""
from copy import deepcopy
import hashlib

import pytest

from financial_writing_agent.standalone_runtime import (
    DOMAIN_ID, FinancialAdmissionError, admit_article_action,
)
from test_financial_goal_intent_governance_20261112 import (
    Provider, SOURCE, TASK, _reader, action as original_action, create, requirement, _proof,
)

WRONG = "财经Deep只能保留3家公司。"
RIGHT = "财经Deep必须保留完整公司池。"


def _submit(provider, statement, *, semantic_verifier=None,
            source=RIGHT, retire_ids=None, intent="USER_REQUIREMENT"):
    path = f"workspaces/articles/{TASK}/STATE.json"
    params = {
        "evidence_ref": SOURCE,
        "upserts": [requirement(statement)] if statement is not None else None,
        "retire_ids": retire_ids,
        "intent_evidence": _proof(source, intent=intent),
    }
    proposal = {
        "schema_version": "1.0", "domain_id": DOMAIN_ID,
        "action_id": "semantic-intent-replay",
        "task_id": TASK, "operation": "CHANGE_REQUIREMENTS",
        "expected_state_blob_sha": provider.read(path)["blob_sha"],
        "parameters": params,
    }
    return admit_article_action(
        proposal, state_reader=provider.read, cas_writer=provider.write,
        authorization_verifier=lambda _: True,
        artifact_reader=provider.artifact,
        source_snapshot_reader=provider.source,
        owner_instruction_reader=_reader(source),
        owner_semantic_verifier=semantic_verifier,
    )


def accepted_owner_approval(request):
    return {
        "approved": True,
        "source_sha256": request["source_sha256"],
        "change_sha256": request["change_sha256"],
        "reviewer_principal": "trusted-independent-owner-confirmation-provider",
        "assurance": "OWNER_EXPLICITLY_CONFIRMED_EXACT_CHANGE",
    }


def test_red_source_hash_and_user_role_are_not_enough_for_semantically_inverted_requirements():
    p = create(Provider())
    frozen = deepcopy(p.states)
    # Perfectly authentic original user source; tampered requirement is a different meaning.
    with pytest.raises(FinancialAdmissionError, match="SEMANTIC"):
        _submit(p, WRONG, semantic_verifier=None)
    assert p.states == frozen


def test_red_no_model_supplied_fake_pass_or_bare_verifier_callback_bypasses_proof():
    p = create(Provider())
    frozen = deepcopy(p.states)
    with pytest.raises(FinancialAdmissionError, match="SEMANTIC"):
        _submit(p, WRONG, semantic_verifier=lambda _: {"approved": True})
    assert p.states == frozen


def test_red_honest_verifier_rejects_contradictory_source_paraphrase():
    p = create(Provider())
    frozen = deepcopy(p.states)
    with pytest.raises(FinancialAdmissionError, match="SEMANTIC"):
        _submit(p, WRONG, semantic_verifier=lambda _: {
            "approved": False, "reason": "source requires entire company universe; only three contradicts",
        })
    assert p.states == frozen


def test_red_provenance_bound_approval_permits_exact_correct_instruction():
    p = create(Provider())
    done = _submit(p, RIGHT, semantic_verifier=accepted_owner_approval)
    assert done["child_state_cas_verified"]
    path = f"workspaces/articles/{TASK}/STATE.json"
    receipt = p.read(path)["state"]["execution_receipts"][-1]["input_bindings"]
    assert receipt["owner_intent_verification"]["semantic_approval"]["approved"] is True
    assert receipt["owner_intent_verification"]["semantic_approval"]["change_sha256"]


def test_red_retirement_requires_verified_scope_binding_and_cannot_retire_arbitrary_id():
    p = create(Provider())
    _submit(p, RIGHT, semantic_verifier=accepted_owner_approval)
    frozen = deepcopy(p.states)
    with pytest.raises(FinancialAdmissionError, match="SEMANTIC"):
        _submit(p, None, source="现在纠正：不需要原来的全量公司池要求了。",
                retire_ids=["deep-universe"],intent="USER_CORRECTION",
                semantic_verifier=None)
    assert p.states == frozen


def test_red_approval_for_another_source_or_mutation_is_invalid():
    p = create(Provider())
    frozen = deepcopy(p.states)
    def forged(request):
        return {
            "approved": True,
            "source_sha256": "0"*64,
            "change_sha256": "1"*64,
            "reviewer_principal": "reviewer",
            "assurance": "OWNER_EXPLICITLY_CONFIRMED_EXACT_CHANGE",
        }
    with pytest.raises(FinancialAdmissionError, match="SEMANTIC"):
        _submit(p, RIGHT, semantic_verifier=forged)
    assert p.states == frozen
