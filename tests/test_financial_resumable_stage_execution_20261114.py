from __future__ import annotations

from copy import deepcopy
import json

import pytest

from financial_writing_agent.writing_kernel import (
    INTERNAL_PORTFOLIO_STAGE_SEQUENCE,
    WritingPassExecutionError,
    execute_portfolio_stage,
    start_portfolio_context,
    validate_portfolio_context,
)
from test_financial_portfolio_execution_20261114 import (
    _executor,
    _research_audit,
    _seed,
)


def _start():
    seed = _seed()
    task_id = seed.pop("task_id")
    requirement_digest = seed.pop("requirement_digest")
    return start_portfolio_context(
        seed,
        required_outputs=[
            "AUDIT_DOCX",
            "FINANCE_DEEP_DOCX",
            "FINANCE_BROAD_DOCX",
            "PLATFORM_INTERACTION_PACK_DOCX",
        ],
        task_id=task_id,
        requirement_digest=requirement_digest,
    )


def test_each_call_executes_only_one_existing_business_stage_and_can_resume_from_json():
    calls = []
    audit_calls = []
    context = _start()

    for stage in INTERNAL_PORTFOLIO_STAGE_SEQUENCE:
        before = len(calls)
        if stage == "RESEARCH_AUDIT":
            context = execute_portfolio_stage(
                context,
                stage=stage,
                research_audit=_research_audit(audit_calls),
            )
            assert len(calls) == before
        else:
            context = execute_portfolio_stage(
                context,
                stage=stage,
                execute_pass=_executor(calls),
            )
        context = json.loads(json.dumps(context, ensure_ascii=False))
        validate_portfolio_context(context)
        assert context["current_stage"] == (
            INTERNAL_PORTFOLIO_STAGE_SEQUENCE[
                INTERNAL_PORTFOLIO_STAGE_SEQUENCE.index(stage) + 1
            ]
            if stage != "EDITORIAL_AUDIT"
            else "DELIVERY"
        )

    assert audit_calls == ["RESEARCH_AUDIT"]
    assert len(context["stage_receipts"]) == 6
    assert len(context["trace"]) == 26
    assert context["current_stage"] == "DELIVERY"
    assert set(context["products"]) == {"FINANCE_DEEP", "FINANCE_BROAD"}
    assert context["interaction"]["platform_interaction_fitness"]["status"] == "PASS"


def test_stage_cannot_be_skipped_replayed_or_run_after_internal_work_is_complete():
    context = _start()
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_STAGE_OUT_OF_ORDER"):
        execute_portfolio_stage(
            context,
            stage="EDITORIAL",
            execute_pass=_executor([]),
        )

    context = execute_portfolio_stage(
        context,
        stage="RESEARCH",
        execute_pass=_executor([]),
    )
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_STAGE_OUT_OF_ORDER"):
        execute_portfolio_stage(
            context,
            stage="RESEARCH",
            execute_pass=_executor([]),
        )


def test_modified_stage_payload_is_detected_before_resume():
    context = execute_portfolio_stage(
        _start(),
        stage="RESEARCH",
        execute_pass=_executor([]),
    )
    tampered = deepcopy(context)
    tampered["shared"]["private_research_brief"] = {"tampered": True}

    with pytest.raises(
        WritingPassExecutionError,
        match="PORTFOLIO_CONTEXT_OUTPUT_DIGEST_MISMATCH",
    ):
        validate_portfolio_context(tampered)


def test_modified_pass_receipt_is_detected_before_resume():
    context = execute_portfolio_stage(
        _start(),
        stage="RESEARCH",
        execute_pass=_executor([]),
    )
    tampered = deepcopy(context)
    tampered["trace"][0]["output_sha256"] = "0" * 64

    with pytest.raises(
        WritingPassExecutionError,
        match="PORTFOLIO_PASS_RECEIPT_CHAIN_MISMATCH",
    ):
        validate_portfolio_context(tampered)


def test_stage_receipt_chain_is_bound_to_task_and_requirement_digest():
    context = execute_portfolio_stage(
        _start(),
        stage="RESEARCH",
        execute_pass=_executor([]),
    )
    tampered = deepcopy(context)
    tampered["requirement_digest"] = "b" * 64

    with pytest.raises(
        WritingPassExecutionError,
        match="PORTFOLIO_STAGE_RECEIPT_CHAIN_MISMATCH",
    ):
        validate_portfolio_context(tampered)


def test_task_identity_and_requirement_digest_are_mandatory():
    seed = _seed()
    seed.pop("task_id")
    seed.pop("requirement_digest")
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_TASK_ID_REQUIRED"):
        start_portfolio_context(
            seed,
            required_outputs=["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"],
            task_id="",
            requirement_digest="a" * 64,
        )
