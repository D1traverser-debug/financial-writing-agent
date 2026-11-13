"""Adversarial requirement-authority semantics: source bytes alone != owner meaning."""
from copy import deepcopy
import hashlib

import pytest

from financial_writing_agent.standalone_runtime import (
    DOMAIN_ID, FinancialAdmissionError, admit_article_action,
)
from test_financial_goal_intent_governance_20261112 import (
    Provider, SOURCE, TASK, _reader, create, requirement, _proof,
)
from trusted_provider_testkit import (
    signed_action_authorization, signed_owner_change_approval, signed_owner_message,
)

WRONG = "财经Deep只能保留3家公司。"
RIGHT = "财经Deep必须保留完整公司池。"


def _submit(provider, statement, *, semantic_verifier=None,
            source=RIGHT, excerpt=None, retire_ids=None, intent="USER_REQUIREMENT"):
    path = f"workspaces/articles/{TASK}/STATE.json"
    proof = _proof(source, intent=intent)
    if excerpt is not None:
        proof["verbatim_excerpt"] = excerpt
    params = {
        "evidence_ref": SOURCE,
        "upserts": [requirement(statement)] if statement is not None else None,
        "retire_ids": retire_ids,
        "intent_evidence": proof,
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
        authorization_verifier=signed_action_authorization,
        artifact_reader=provider.artifact,
        source_snapshot_reader=provider.source,
        owner_instruction_reader=_reader(source),
        owner_semantic_verifier=semantic_verifier,
    )


def accepted_owner_approval(request):
    return signed_owner_change_approval(request, approved=True)


def rejected_owner_approval(request):
    return signed_owner_change_approval(request, approved=False)


def test_red_source_hash_and_user_role_are_not_enough_for_semantically_inverted_requirements():
    p = create(Provider())
    frozen = deepcopy(p.states)
    # Perfectly authentic original user source; tampered requirement is a different meaning.
    with pytest.raises(FinancialAdmissionError, match="SEMANTIC"):
        _submit(p, WRONG, semantic_verifier=None)
    assert p.states == frozen


def test_signed_owner_rejection_blocks_a_semantically_inverted_requirement():
    p = create(Provider())
    frozen = deepcopy(p.states)
    # The provider sees the full source and exact proposed mutation, then signs
    # a rejection. A source hash alone is not semantic approval.
    with pytest.raises(FinancialAdmissionError, match="SEMANTIC"):
        _submit(p, WRONG, semantic_verifier=rejected_owner_approval)
    assert p.states == frozen




def test_red_nonbinding_intent_cannot_quote_a_selective_substring():
    p = create(Provider())
    frozen = deepcopy(p.states)
    original = "不要只保留三家公司，必须保留完整公司池。"
    proof = _proof("只保留三家公司", intent="USER_SUGGESTION")
    with pytest.raises(FinancialAdmissionError, match="INTENT"):
        admit_article_action(
            {
                "schema_version": "1.0", "domain_id": DOMAIN_ID,
                "action_id": "selective-nonbinding-quote",
                "task_id": TASK, "operation": "RECORD_OWNER_INTENT",
                "expected_state_blob_sha": p.read(f"workspaces/articles/{TASK}/STATE.json")["blob_sha"],
                "parameters": {"intent_evidence": proof, "summary": "selective quote"},
            },
            state_reader=p.read, cas_writer=p.write,
            authorization_verifier=signed_action_authorization, artifact_reader=p.artifact,
            owner_instruction_reader=lambda ref: signed_owner_message(ref, original),
        )
    assert p.states == frozen

def test_red_negation_cannot_be_removed_by_selecting_a_true_but_misleading_substring():
    p = create(Provider())
    frozen = deepcopy(p.states)
    original = "请不要只保留三家公司。"
    with pytest.raises(FinancialAdmissionError, match="SEMANTIC"):
        _submit(
            p, "只保留三家公司。", source=original,
            semantic_verifier=rejected_owner_approval,
        )
    assert p.states == frozen


def test_red_truncated_excerpt_cannot_drop_context_even_when_statement_matches_it():
    p = create(Provider())
    frozen = deepcopy(p.states)
    original = "不要只保留三家公司，必须保留完整公司池。"
    with pytest.raises(FinancialAdmissionError, match="INTENT"):
        _submit(
            p, "不要只保留三家公司，必须保留完整公司池。",
            source=original, excerpt="只保留三家公司",
            semantic_verifier=accepted_owner_approval,
        )
    assert p.states == frozen


def test_green_complete_owner_utterance_is_preserved_as_source_evidence():
    p = create(Provider())
    original = "不要只保留三家公司，必须保留完整公司池。"
    result = _submit(
        p, original, source=original,
        semantic_verifier=accepted_owner_approval,
    )
    assert result["child_state_cas_verified"]
    state = p.read(f"workspaces/articles/{TASK}/STATE.json")["state"]
    active = state["task_requirement_authority"]["active_requirements"]
    assert active[0]["statement"] == original
    receipt = state["execution_receipts"][-1]["input_bindings"]["owner_intent_verification"]
    assert receipt["source_sha256"] == hashlib.sha256(original.encode("utf-8")).hexdigest()
    assert receipt["excerpt_sha256"] == hashlib.sha256(original.encode("utf-8")).hexdigest()


def test_green_one_full_owner_message_can_be_decomposed_into_multiple_confirmed_requirements():
    p = create(Provider())
    original = "财经Deep应保留完整公司池，并按细分行业比较各公司的订单、盈利能力和现金流。"
    first = requirement("财经Deep应保留完整公司池，并说明各公司纳入或排除的理由。")
    second = requirement("在各细分行业内比较公司的订单、盈利能力和现金流。")
    second["requirement_id"] = "deep-segment-comparison"
    path = f"workspaces/articles/{TASK}/STATE.json"
    proposal = {
        "schema_version": "1.0", "domain_id": DOMAIN_ID,
        "action_id": "multi-requirement-decomposition",
        "task_id": TASK, "operation": "CHANGE_REQUIREMENTS",
        "expected_state_blob_sha": p.read(path)["blob_sha"],
        "parameters": {
            "evidence_ref": SOURCE,
            "upserts": [first, second],
            "retire_ids": None,
            "intent_evidence": _proof(original),
        },
    }
    result = admit_article_action(
        proposal, state_reader=p.read, cas_writer=p.write,
        authorization_verifier=signed_action_authorization,
        artifact_reader=p.artifact, source_snapshot_reader=p.source,
        owner_instruction_reader=_reader(original),
        owner_semantic_verifier=accepted_owner_approval,
    )
    assert result["child_state_cas_verified"]
    state = p.read(path)["state"]
    active = state["task_requirement_authority"]["active_requirements"]
    assert {item["requirement_id"] for item in active} == {
        "deep-universe", "deep-segment-comparison",
    }
    assert {item["statement"] for item in active} == {
        first["statement"], second["statement"],
    }
    receipt = state["execution_receipts"][-1]["input_bindings"]["owner_intent_verification"]
    assert receipt["source_sha256"] == hashlib.sha256(original.encode("utf-8")).hexdigest()
    assert receipt["semantic_approval"]["approved"] is True
    assert receipt["semantic_approval"]["change_sha256"]


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
        _submit(p, WRONG, semantic_verifier=rejected_owner_approval)
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
