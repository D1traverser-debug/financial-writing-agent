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
        "FINANCE_DEEP", "FINANCE_BROAD", "PLATFORM_INTERACTION", "DELIVERY",
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
    if requirements:
        fixed_ids = [
            item["requirement_id"] for item in requirements
            if item["source_kind"] in {"USER_EXPLICIT", "USER_CORRECTION"}
        ]
        preference_ids = [
            item["requirement_id"] for item in requirements
            if item["source_kind"] == "USER_PREFERENCE"
        ]
        decision_domains = []
        for item in requirements:
            requirement_id = item["requirement_id"]
            if item["source_kind"] in {"USER_EXPLICIT", "USER_CORRECTION"}:
                decision_domains.append({
                    "domain": "REQUIREMENT_" + requirement_id.upper().replace("-", "_"),
                    "disposition": "LOCKED",
                    "scopes": item["scopes"],
                    "requirement_ids": [requirement_id],
                    "preference_ids": [],
                    "rationale": item["statement"],
                })
            else:
                decision_domains.append({
                    "domain": "PREFERENCE_" + requirement_id.upper().replace("-", "_"),
                    "disposition": "OPEN",
                    "scopes": item["scopes"],
                    "requirement_ids": [],
                    "preference_ids": [requirement_id],
                    "rationale": item["statement"],
                })
        decision_domains.extend([
            {
                "domain": name,
                "disposition": "OPEN",
                "scopes": ["ALL"],
                "requirement_ids": [],
                "preference_ids": [],
                "rationale": "No binding user requirement fixes this editorial decision.",
            }
            for name in ("THESIS", "ANGLE", "NARRATIVE_ENGINE", "TITLE", "SECTION_ORDER")
        ])
        seed["writing_execution_profile"] = {
            "schema_version": "1.1",
            "workflow_contract": "FINANCIAL_ARTICLE_10_STAGE_V1",
            "fixed_requirement_ids": fixed_ids,
            "preference_requirement_ids": preference_ids,
            "decision_domains": decision_domains,
            "conditional_modules": ["COMPANY_UNIVERSE"],
            "execution_rationale": "The article workflow remains fixed; each locked/open domain is linked to the existing requirement authority.",
        }
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
        _requirement("deep-research", ["FINANCE_DEEP"], "RESEARCH"),
        _requirement("deep-editorial", ["FINANCE_DEEP"], "EDITORIAL"),
    ]
    context = _start(requirements)
    seen = []

    def execute(node, inputs):
        seen.append((node.value, inputs.get("task_requirement_contexts"), inputs.get("writing_execution_profile")))
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
            {
                "requirement_id": "deep-research",
                "result": "SATISFIED",
                "evidence_refs": ["source://deep"],
            },
        ],
    )
    assert seen
    assert all(item[1] is not None for item in seen)
    assert all(item[2] == context["shared"]["writing_execution_profile"] for item in seen)
    assert all(
        set(item[1]) == {"ALL", "RESEARCH", "PRIVATE_RESEARCH", "FINANCE_DEEP"}
        for item in seen
    )
    deep_context = seen[0][1]["FINANCE_DEEP"]["requirements"]
    assert [item["requirement_id"] for item in deep_context] == ["deep-research"]
    satisfied = {
        item["requirement_id"]
        for item in context["stage_receipts"][0]["requirement_satisfaction"]
    }
    assert satisfied == {"general-research", "private-research", "deep-research"}
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
        "full_universe_research_pool", ["FINANCE_DEEP"], "RESEARCH",
    )
    context = _start([requirement])
    with pytest.raises(
        WritingPassExecutionError,
        match="PORTFOLIO_FULL_UNIVERSE_RESEARCH_EVIDENCE_CONTRACT_REQUIRED",
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

def test_rebind_requires_a_refreshed_work_profile_when_requirements_change():
    from financial_writing_agent.writing_kernel import rebind_portfolio_context_requirements

    context = _start()
    digest = "b" * 64
    requirements = [_requirement("new-fixed-title", ["ALL"], "TITLE")]
    contexts = _contexts(digest, requirements)
    with pytest.raises(
        WritingPassExecutionError,
        match="PORTFOLIO_WRITING_EXECUTION_PROFILE_REFRESH_REQUIRED",
    ):
        rebind_portfolio_context_requirements(
            context,
            requirement_digest=digest,
            requirement_contexts=contexts,
            current_stage="RESEARCH",
        )

    profile = {
        "schema_version": "1.0",
        "workflow_contract": "FINANCIAL_ARTICLE_10_STAGE_V1",
        "source_prompt_sha256": context["seed_inputs"]["source_prompt_sha256"],
        "fixed_requirement_ids": ["new-fixed-title"],
        "preference_requirement_ids": [],
        "locked_decision_domains": ["TITLE"],
        "open_decision_domains": ["THESIS", "ANGLE", "NARRATIVE_ENGINE"],
        "conditional_modules": ["COMPANY_UNIVERSE"],
        "execution_rationale": "The exact title is fixed; thesis and narrative decisions remain open.",
    }
    rebound = rebind_portfolio_context_requirements(
        context,
        requirement_digest=digest,
        requirement_contexts=contexts,
        current_stage="RESEARCH",
        writing_execution_profile=profile,
    )
    assert rebound["seed_inputs"]["writing_execution_profile"] == profile
    assert rebound["shared"]["writing_execution_profile"] == profile
    validate_portfolio_context(rebound)


def test_every_writing_pass_accepts_the_bound_writing_execution_profile_as_optional_context():
    from financial_writing_agent.writing_kernel import PASS_CONTRACTS, WritingPass

    assert set(PASS_CONTRACTS) == set(WritingPass)
    assert all("writing_execution_profile" in contract.optional_inputs for contract in PASS_CONTRACTS.values())

