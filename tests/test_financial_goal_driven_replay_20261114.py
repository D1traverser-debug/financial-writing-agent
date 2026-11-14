"""User-goal-first integration cases: prove graph interfaces and requirement flow.

No callback here is a real LLM, stock researcher or independent editor.
Successful simulations are structural only, never an editorial PASS.
"""
from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace

import pytest

from financial_writing_agent.current_admission import (
    CurrentAdmissionError, advance_state, apply_task_requirement_change,
    build_initial_state,
)
from financial_writing_agent.task_publication import (
    TaskPublicationError, verify_task_publication_scope,
)
from financial_writing_agent.writing_kernel import (
    PASS_CONTRACTS, PRE_RESEARCH_EXTERNAL_INPUTS,
    WritingPass, WritingPassExecutionError,
    execute_writing_passes, execution_order, validate_pass_dataflow,
)
from financial_writing_agent.document import ArticleDocument, Block

from test_current_admission_v1 import (
    _artifact, _brief, _blueprint, _decision, _fitness,
)


def _seed():
    seed = {name: f"actual-host-supplied:{name}" for name in PRE_RESEARCH_EXTERNAL_INPUTS}
    seed["product_mode"] = "FINANCE_DEEP"
    return seed


def _executor(node, inputs):
    assert set(inputs) == set(PASS_CONTRACTS[node].required_inputs)
    return {name: f"synthetic-work-product:{node.value}:{name}"
            for name in PASS_CONTRACTS[node].outputs}


def _research_audit(inputs):
    assert "selected_thesis" in inputs
    assert "adversarial_package" in inputs
    assert "private_research_brief" in inputs
    return {
        "status": "PASS", "evidence_refs": ["simulation://audited-research"],
        "audited_evidence": {"synthetic": True, "quality_certified": False},
    }


def test_portfolio_pass_dataflow_is_closed_from_explicit_stage_inputs_not_implicit_global_guesswork():
    assert validate_pass_dataflow() == []
    ordered = execution_order()
    assert len(ordered) == 16
    assert ordered.index(WritingPass.PRIVATE_RESEARCH_SYNTHESIS) < ordered.index(WritingPass.THESIS_ADJUDICATION)
    assert ordered.index(WritingPass.THESIS_ADJUDICATION) < ordered.index(WritingPass.STORY_ARCHITECTURE)
    assert ordered.index(WritingPass.STORY_ARCHITECTURE) < ordered.index(WritingPass.HEADLINE_ADJUDICATION)
    assert ordered.index(WritingPass.HEADLINE_ADJUDICATION) < ordered.index(WritingPass.DRAFT_GENERATION)
    assert ordered.index(WritingPass.PLATFORM_INTERACTION_ADAPTATION) < ordered.index(WritingPass.PLATFORM_INTERACTION_AUDIT)
    assert "discovery_package" in PASS_CONTRACTS[WritingPass.RESEARCH_DISCOVERY].outputs
    assert "adversarial_package" in PASS_CONTRACTS[WritingPass.RESEARCH_ADVERSARIAL].outputs
    assert "decision_envelope" in PASS_CONTRACTS[WritingPass.THESIS_ADJUDICATION].outputs
    assert PASS_CONTRACTS[WritingPass.HEADLINE_ADJUDICATION].outputs == ("headline_decision",)


def test_full_single_product_and_interaction_pass_callbacks_execute_in_dependency_order_after_research_audit():
    invoked = []
    def worker(node, inputs):
        invoked.append(node.value)
        return _executor(node, inputs)
    output = execute_writing_passes(_seed(), execute_pass=worker,
                                     research_audit=_research_audit)
    assert invoked == [item.value for item in execution_order()]
    assert output["pass_count"] == 16
    assert output["research_audit_boundary_reached"] is True
    assert len(output["trace"]) == 17
    assert output["trace"][5]["pass"] == "RESEARCH_AUDIT_BOUNDARY"
    assert "NOT_PORTFOLIO_OR_EDITORIAL_ACCEPTANCE" in output["assurance"]
    assert output["products"]["publication_candidate"].startswith("synthetic-work-product")
    assert "NOT_INDEPENDENT_EDITORIAL" in output["assurance"]


def test_missing_actual_work_or_failing_research_audit_stops_before_writer():
    with pytest.raises(WritingPassExecutionError, match="EXTERNAL_INPUTS_MISSING"):
        execute_writing_passes({"topic": "test"}, execute_pass=_executor,
                               research_audit=_research_audit)
    assert "audited_evidence" not in _seed()
    with pytest.raises(WritingPassExecutionError, match="PRESEED_FORBIDDEN"):
        execute_writing_passes({**_seed(), "audited_evidence": "fake"},
                               execute_pass=_executor,
                               research_audit=_research_audit)
    called = []
    def worker(node, inputs):
        called.append(node.value)
        return _executor(node, inputs)
    with pytest.raises(WritingPassExecutionError, match="RESEARCH_AUDIT_NOT_ADMITTED"):
        execute_writing_passes(_seed(), execute_pass=worker,
                               research_audit=lambda _: {"status": "PASS"})
    assert "DRAFT_GENERATION" not in called
    assert "FINAL_SYNTHESIS" not in called


def test_partial_research_product_and_later_review_failure_never_reach_final_synthesis():
    def incomplete(node, inputs):
        if node is WritingPass.RESEARCH_DISCOVERY:
            return {"value_chain_map": "fake", "company_universe": "fake"}
        return _executor(node, inputs)
    with pytest.raises(WritingPassExecutionError, match="WRITING_PASS_OUTPUT_MISSING:RESEARCH_DISCOVERY"):
        execute_writing_passes(_seed(), execute_pass=incomplete,
                               research_audit=_research_audit)

    called = []
    def failing(node, inputs):
        called.append(node.value)
        if node is WritingPass.FACT_INTEGRITY_AUDIT:
            raise ValueError("2026 company disclosure contradictory")
        return _executor(node, inputs)
    with pytest.raises(WritingPassExecutionError, match="WRITING_PASS_EXECUTION_FAILED:FACT_INTEGRITY_AUDIT"):
        execute_writing_passes(_seed(), execute_pass=failing,
                               research_audit=_research_audit)
    assert "FINAL_SYNTHESIS" not in called


def _shared_requirement(affected="DELIVERY"):
    return {
        "requirement_id": "owner_cross_platform_financial_angle",
        "statement": "深度文章和泛读文章都应解释政策变化如何影响企业利润，而不是介绍概念股。",
        "scopes": ["ALL"],
        "affects_from_stage": affected,
        "evidence_ref": "chat://owner/finance-writing-requirement",
        "source_kind": "USER_EXPLICIT",
    }


def _at_delivery_with_cross_platform_requirement(*, affected="DELIVERY"):
    task_id = f"finance-cross-platform-{affected.lower()}"
    state = build_initial_state(
        task_id=task_id, executor_identity="synthetic-test",
        prompt="要求两篇不同文章围绕同一经济问题", source_refs=[],
    )
    state = apply_task_requirement_change(
        state, previous_state_blob_sha="0" * 40,
        executor_identity="synthetic-test",
        evidence_ref="chat://owner/finance-writing-requirement",
        upserts=[_shared_requirement(affected)],
    )
    state = advance_state(state, previous_state_blob_sha="1" * 40,
                          executor_identity="synthetic-test")
    options = {
        "previous_state_blob_sha": "2" * 40,
        "executor_identity": "synthetic-test",
        **_artifact(task_id, "RESEARCH"),
        "decision_envelope": _decision(),
        "private_research_brief": _brief(),
    }
    if affected == "RESEARCH":
        options["requirement_satisfaction"] = [{
            "requirement_id": _shared_requirement(affected)["requirement_id"],
            "result": "SATISFIED",
            "evidence_refs": [options["artifact_path"]],
        }]
    state = advance_state(state, **options)
    state = advance_state(state, previous_state_blob_sha="3" * 40,
                          executor_identity="synthetic-test",
                          review_status="PASS", **_artifact(task_id, "RESEARCH_AUDIT"))
    state = advance_state(
        state, previous_state_blob_sha="4" * 40,
        executor_identity="synthetic-test",
        story_blueprints=[_blueprint("FINANCE_DEEP"), _blueprint("FINANCE_BROAD")],
        **_artifact(task_id, "EDITORIAL"),
    )
    title = {
        "previous_state_blob_sha": "5" * 40,
        "executor_identity": "synthetic-test", **_artifact(task_id, "TITLE"),
    }
    if affected == "TITLE":
        title["requirement_satisfaction"] = [{
            "requirement_id": _shared_requirement(affected)["requirement_id"],
            "result": "SATISFIED", "evidence_refs": [title["artifact_path"]],
        }]
    state = advance_state(state, **title)
    draft = {
        "previous_state_blob_sha": "6" * 40,
        "executor_identity": "synthetic-test", **_artifact(task_id, "DRAFT"),
    }
    if affected == "DRAFT":
        draft["requirement_satisfaction"] = [{
            "requirement_id": _shared_requirement(affected)["requirement_id"],
            "result": "SATISFIED", "evidence_refs": [draft["artifact_path"]],
        }]
    state = advance_state(state, **draft)
    state = advance_state(
        state, previous_state_blob_sha="7" * 40,
        executor_identity="synthetic-test",
        review_status="PASS",
        publication_fitnesses=[_fitness("FINANCE_DEEP"), _fitness("FINANCE_BROAD")],
        **_artifact(task_id, "EDITORIAL_AUDIT"),
    )
    return state


def _article():
    return ArticleDocument(
        title="行业投资链条不是一张概念股清单",
        stock_names=["甲公司", "乙公司"],
        blocks=[
            Block(kind="h1", text="公司之间的利润兑现为何分化"),
            Block(kind="body", text=(
                "甲公司的订单兑现强于乙公司，甲公司成本更低，"
                "乙公司仍需跨越交付与验收，现金回款兑现更慢。"
            )),
        ],
    )


def _research():
    return SimpleNamespace(
        universe=[
            SimpleNamespace(name="甲公司", materiality="MATERIAL", value_chain_class="power"),
            SimpleNamespace(name="乙公司", materiality="MATERIAL", value_chain_class="power"),
        ],
        company_decision_map=object(),
    )


@pytest.mark.parametrize("affected", ["RESEARCH", "TITLE", "DRAFT", "DELIVERY"])
def test_owner_written_all_scope_requirement_handoff_no_longer_deadlocks_either_product(affected):
    state = _at_delivery_with_cross_platform_requirement(affected=affected)
    assert state["current_stage"] == "DELIVERY"
    for mode in ("FINANCE_DEEP", "FINANCE_BROAD"):
        result = verify_task_publication_scope(
            state, _article(), _research() if mode == "FINANCE_DEEP" else None,
            product_mode=mode,
        )
        assert result["mode"] == mode
        assert result["semantic_unverified_requirement_ids"] == [
            "owner_cross_platform_financial_angle"
        ]
        if affected == "DELIVERY":
            assert result["pending_delivery_requirement_ids"] == [
                "owner_cross_platform_financial_angle"
            ]
            assert result["structurally_accounted_requirement_ids"] == []
        else:
            assert result["pending_delivery_requirement_ids"] == []
            assert result["structurally_accounted_requirement_ids"] == [
                "owner_cross_platform_financial_angle"
            ]


def test_user_requirement_not_yet_due_is_neither_autopassed_nor_silently_discarded():
    state = build_initial_state(
        task_id="finance-user-goal-not-due", prompt="考虑两篇财报文章",
        executor_identity="test", source_refs=[],
    )
    state = apply_task_requirement_change(
        state, previous_state_blob_sha="0" * 40, executor_identity="test",
        evidence_ref="chat://owner/finance-writing-requirement",
        upserts=[_shared_requirement("DRAFT")],
    )
    with pytest.raises(TaskPublicationError, match="REQUIREMENTS_NOT_YET_ADMITTED"):
        verify_task_publication_scope(state, _article(), None, product_mode="FINANCE_BROAD")


def test_word_builder_rejects_generic_requirement_semantic_certification_claim():
    state = _at_delivery_with_cross_platform_requirement(affected="DRAFT")
    result = verify_task_publication_scope(
        state, _article(), _research(), product_mode="FINANCE_DEEP",
    )
    assert result["validated_requirement_ids"] == []
    assert result["structurally_accounted_requirement_ids"]
    assert "FACTS_AND_EDITORIAL_NOT_INDEPENDENTLY_VERIFIED" in result["assurance"]


def test_delivery_stage_user_requirement_cannot_advance_without_satisfaction_receipt():
    state = _at_delivery_with_cross_platform_requirement(affected="DELIVERY")
    task_id = state["task_id"]
    manifest = [
        {
            "kind": kind,
            "file_name": kind.lower() + ".docx",
            "sha256": "a" * 64,
            "resource_ref": f"workspaces/articles/{task_id}/delivery/{kind.lower()}.docx",
        }
        for kind in ("FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX",
                     "PLATFORM_INTERACTION_PACK_DOCX")
    ]
    kwargs = {
        "previous_state_blob_sha": "8" * 40,
        "executor_identity": "synthetic-test",
        "delivery_artifacts": manifest,
        **_artifact(task_id, "DELIVERY"),
    }
    with pytest.raises(CurrentAdmissionError, match="DELIVERY transition requires task requirement satisfaction"):
        advance_state(state, **kwargs)
    assert state["current_stage"] == "DELIVERY"
    passed = advance_state(state, **{
        **kwargs, "requirement_satisfaction": [{
            "requirement_id": "owner_cross_platform_financial_angle",
            "result": "SATISFIED",
            "evidence_refs": [kwargs["artifact_path"]],
        }],
    })
    assert passed["current_stage"] == "MECHANICAL_AUDIT"
    assert passed["task_requirement_authority"] == state["task_requirement_authority"]
    # This direct state replay does not verify real external source bytes.
    receipt = passed["execution_receipts"][-1]
    assert receipt["input_bindings"]["task_requirement_satisfaction"]


def test_goal_projection_exposes_unsatisfied_customer_requirements_before_user_notices():
    from financial_writing_agent.user_goal_progress import inspect_user_goal_progress
    before = _at_delivery_with_cross_platform_requirement(affected="TITLE")
    visible = inspect_user_goal_progress(before)
    assert visible["active_user_requirement_count"] == 1
    item = visible["requirement_progress"][0]
    assert item["original_requirement"].startswith("深度文章和泛读文章")
    assert item["stage_structural_status"] == "ADMITTED_STAGE_RECEIPT__SEMANTIC_CORRECTNESS_UNPROVEN"
    assert item["article_semantic_satisfaction_verified"] is False
    assert visible["output_contract_count"] == 4
    assert len(visible["output_metadata_missing"]) == 4
    assert visible["all_user_writing_goals_verified"] is False
    assert visible["business_writing_pass_execution_verified"] is False
    assert visible["current_primary_source_factual_entailment_verified"] is False

    due = inspect_user_goal_progress(
        _at_delivery_with_cross_platform_requirement(affected="DELIVERY")
    )
    assert due["requirement_progress"][0]["stage_structural_status"] == (
        "DUE__STAGE_SATISFACTION_STILL_REQUIRED"
    )


def test_authenticated_observation_exposes_goal_progress_instead_of_only_cas_status():
    from financial_writing_agent.standalone_runtime import observe_article
    from test_financial_native_loop_closure_20261112 import (
        make, TASK,
    )
    p = make()
    read = observe_article(
        TASK, state_reader=p.read, effect_receipt_reader=p.read_effect,
    )
    progress = read["user_goal_progress"]
    assert progress["active_user_requirement_count"] == 0
    assert set(progress["output_metadata_missing"]) == set(read["required_outputs"])
    assert read["user_writing_business_outcome_verified"] is False
    assert progress["all_user_writing_goals_verified"] is False
