from __future__ import annotations

from copy import deepcopy
import json

import pytest

from financial_writing_agent.writing_kernel import (
    INTERNAL_PORTFOLIO_STAGE_SEQUENCE,
    WritingPassExecutionError,
    execute_portfolio_stage,
    resume_portfolio_context,
    start_portfolio_context,
    validate_portfolio_context,
)
from test_financial_portfolio_execution_20261114 import (
    _executor,
    _research_audit,
    _seed,
)


def _requirement(requirement_id, scopes, stage):
    return {
        "requirement_id": requirement_id,
        "statement": f"Explicit task constraint {requirement_id}",
        "scopes": scopes,
        "affects_from_stage": stage,
        "evidence_ref": f"owner-instruction://{requirement_id}",
        "source_kind": "USER_EXPLICIT",
    }


def _contexts(digest, requirements):
    scopes = (
        "ALL", "RESEARCH", "PRIVATE_RESEARCH",
        "FINANCE_DEEP", "FINANCE_BROAD", "PLATFORM_INTERACTION",
    )
    result = {}
    for scope in scopes:
        selected = [
            item for item in requirements
            if "ALL" in item["scopes"] or scope in item["scopes"]
        ]
        result[scope] = {
            "contract_version": "1.0",
            "revision": 1,
            "digest": digest,
            "requirements": deepcopy(selected),
        }
    return result


def _start(requirements=()):
    seed = _seed()
    task_id = seed.pop("task_id")
    digest = seed.pop("requirement_digest")
    return start_portfolio_context(
        seed,
        required_outputs=[
            "AUDIT_DOCX",
            "FINANCE_DEEP_DOCX",
            "FINANCE_BROAD_DOCX",
            "PLATFORM_INTERACTION_PACK_DOCX",
        ],
        task_id=task_id,
        requirement_digest=digest,
        requirement_contexts=_contexts(digest, list(requirements)) if requirements else None,
    )


def test_every_shared_pass_receives_exact_scoped_requirement_contexts():
    requirements = [
        _requirement("general-research", ["ALL"], "RESEARCH"),
        _requirement("private-research", ["PRIVATE_RESEARCH"], "RESEARCH"),
        _requirement("deep-editorial", ["FINANCE_DEEP"], "EDITORIAL"),
    ]
    context = _start(requirements)
    seen = []

    def execute(node, inputs):
        seen.append((node.value, inputs.get("task_requirement_contexts")))
        return _executor([])(node, inputs)

    context = execute_portfolio_stage(
        context,
        stage="RESEARCH",
        execute_pass=execute,
        requirement_satisfaction=[
            {
                "requirement_id": "general-research",
                "result": "SATISFIED",
                "evidence_refs": ["source://general"],
            },
            {
                "requirement_id": "private-research",
                "result": "SATISFIED",
                "evidence_refs": ["source://private"],
            },
        ],
    )
    assert seen
    assert all(item[1] is not None for item in seen)
    assert all(set(item[1]) == {"ALL", "RESEARCH", "PRIVATE_RESEARCH"} for item in seen)
    assert context["stage_receipts"][0]["requirement_satisfaction"][0]["requirement_id"] == "general-research"
    validate_portfolio_context(json.loads(json.dumps(context)))


def test_missing_or_incomplete_requirement_satisfaction_stops_before_any_pass():
    requirement = _requirement("must-cover", ["RESEARCH"], "RESEARCH")
    context = _start([requirement])
    calls = []
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_REQUIREMENT_SATISFACTION_REQUIRED"):
        execute_portfolio_stage(
            context,
            stage="RESEARCH",
            execute_pass=_executor(calls),
        )
    assert calls == []


def test_requirement_context_with_stale_digest_is_rejected():
    seed = _seed()
    task_id = seed.pop("task_id")
    digest = seed.pop("requirement_digest")
    stale = _contexts("b" * 64, [])
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_TASK_REQUIREMENT_CONTEXT_INVALID"):
        start_portfolio_context(
            seed,
            required_outputs=["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"],
            task_id=task_id,
            requirement_digest=digest,
            requirement_contexts=stale,
        )


def test_research_audit_revise_rewinds_to_research_and_preserves_revision_history():
    context = execute_portfolio_stage(
        _start(),
        stage="RESEARCH",
        execute_pass=_executor([]),
    )

    def revise(_):
        return {
            "status": "REVISE",
            "evidence_refs": ["audit://research-revision"],
            "revision_target": "RESEARCH",
        }

    revised = execute_portfolio_stage(
        context,
        stage="RESEARCH_AUDIT",
        research_audit=revise,
    )
    assert revised["current_stage"] == "RESEARCH"
    assert revised["initial_stage"] == "RESEARCH"
    assert revised["generation"] == 1
    assert revised["stage_receipts"] == []
    assert revised["shared"] == revised["seed_inputs"]
    assert revised["revision_history"][-1]["record_type"] == "REVISION"
    assert revised["last_stage_result"]["status"] == "REVISE"
    validate_portfolio_context(json.loads(json.dumps(revised)))


def test_editorial_audit_revise_preserves_only_upstream_outputs_before_draft_reentry():
    context = _start()
    for stage in INTERNAL_PORTFOLIO_STAGE_SEQUENCE[:-1]:
        if stage == "RESEARCH_AUDIT":
            context = execute_portfolio_stage(
                context, stage=stage, research_audit=_research_audit([]),
            )
        else:
            context = execute_portfolio_stage(
                context, stage=stage, execute_pass=_executor([]),
            )

    revised = execute_portfolio_stage(
        context,
        stage="EDITORIAL_AUDIT",
        execute_pass=_executor([], revise_mode="FINANCE_DEEP"),
    )
    assert revised["current_stage"] == "DRAFT"
    assert revised["generation"] == 1
    assert revised["last_stage_result"]["reviewed_products"] == ["FINANCE_DEEP"]
    for product in revised["products"].values():
        assert "story_blueprint" in product
        assert "headline_decision" in product
        assert "draft" not in product
        assert "publication_candidate" not in product
        assert "publication_fitness" not in product
    assert revised["interaction"] == {}
    validate_portfolio_context(json.loads(json.dumps(revised)))


def test_failed_review_blocks_context_until_owner_resume_and_then_restarts_same_stage():
    context = execute_portfolio_stage(
        _start(),
        stage="RESEARCH",
        execute_pass=_executor([]),
    )

    def fail(_):
        return {
            "status": "FAIL",
            "evidence_refs": ["audit://research-failure"],
            "revision_target": "RESEARCH",
        }

    blocked = execute_portfolio_stage(
        context,
        stage="RESEARCH_AUDIT",
        research_audit=fail,
    )
    assert blocked["execution_status"] == "BLOCKED"
    assert blocked["blocked_stage"] == "RESEARCH_AUDIT"
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_CONTEXT_BLOCKED_REQUIRES_OWNER_RESUME"):
        execute_portfolio_stage(
            blocked,
            stage="RESEARCH_AUDIT",
            research_audit=_research_audit([]),
        )

    resumed = resume_portfolio_context(
        blocked,
        owner_state={
            "task_id": blocked["task_id"],
            "task_requirement_digest": blocked["requirement_digest"],
            "current_stage": "RESEARCH_AUDIT",
            "status": "IN_PROGRESS",
        },
    )
    assert resumed["execution_status"] == "ACTIVE"
    assert resumed["current_stage"] == "RESEARCH_AUDIT"
    assert resumed["generation"] == 1
    assert resumed["stage_receipts"] == []
    assert "research_audit_result" not in resumed["shared"]
    validate_portfolio_context(json.loads(json.dumps(resumed)))


def test_full_universe_requirement_requires_a_typed_research_package():
    requirement = _requirement(
        "full_universe_research_pool", ["RESEARCH"], "RESEARCH",
    )
    context = _start([requirement])
    with pytest.raises(
        WritingPassExecutionError,
        match="PORTFOLIO_FULL_UNIVERSE_RESEARCH_PACKAGE_REQUIRED",
    ):
        execute_portfolio_stage(
            context,
            stage="RESEARCH",
            execute_pass=_executor([]),
            requirement_satisfaction=[{
                "requirement_id": "full_universe_research_pool",
                "result": "SATISFIED",
                "evidence_refs": ["source://universe"],
            }],
        )
