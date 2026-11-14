from __future__ import annotations

from collections import Counter

import pytest

from financial_writing_agent.writing_kernel import (
    INTERACTION_PRODUCT_PASSES,
    LONGFORM_PRODUCT_PASSES,
    PASS_CONTRACTS,
    SHARED_RESEARCH_PASSES,
    WritingPass,
    WritingPassExecutionError,
    execute_portfolio_writing,
)


def _seed(*, interaction=True):
    values = {
        "topic_or_task": "A current financial topic with a defined reader job",
        "knowledge_sources": ["knowledge://methods"],
        "topic": "current financial topic",
        "current_sources": ["source://primary/current"],
        "research_requirements": ["company universe", "counterevidence", "causal transmission"],
        "reader_job": "understand what changed and which company economics are actually exposed",
        "voice_evidence": ["voice://available-evidence"],
        "material_sources": ["source://primary/current"],
        "headline_search_evidence": ["search://headline-context"],
    }
    if interaction:
        values["platform_context"] = {
            "target_platforms": ["WECHAT_IMAGE_TEXT", "TOUTIAO_MICRO", "GENERIC_DYNAMIC"],
        }
    return values


def _fitness(mode, *, revise=False, omit_gates=False):
    gates = [
        {
            "gate": name,
            "status": "REVISE" if revise and name == "FACT_INTEGRITY" else "PASS",
            "evidence": [{
                "location": "section 1",
                "excerpt": "source-bounded example text",
                "finding": "Synthetic gate exercise, NOT authentic editorial evidence",
                "severity": "INFO",
            }],
            "checked_items": ["test artifact claim trace"],
            "revision_actions": ["Recheck source data"] if revise and name == "FACT_INTEGRITY" else [],
        }
        for name in (
            "FACT_INTEGRITY", "RETENTION", "COMPANY_GROUNDING",
            "STRUCTURE_NUMBERING", "ORIGINALITY", "AUTHORIAL_STYLE",
            "COMPLIANCE", "PAYOFF",
        )
    ]
    return {
        "product_mode": mode,
        "gates": [] if omit_gates else gates,
        "originality_checks": [{
            "compared_source_ref": "source://synthetic",
            "checked_phrase_or_passage": "source-bounded example text",
            "result": "COMMON_LANGUAGE",
            "notes": "synthetic fixture, not independent originality review",
        }],
        "assurance": "CHAT_SELF_REVIEW",
        "review_scope": "INTERNAL_DELIVERY_READINESS",
        "audit_provenance": {
            "assurance": "CHAT_SELF_REVIEW",
            "reviewed_article_sha256": "a" * 64,
        },
        "final_status": "REVISE" if revise else "PASS",
    }


def _executor(calls, *, wrong_scope_for=None, fail_at=None,
              revise_mode=None, omit_gates_for=None,
              cloned_bodies=False, incomplete_interaction=False):
    def run(node, inputs):
        mode = inputs.get("product_mode")
        calls.append((node, mode))
        if fail_at == (node, mode):
            raise RuntimeError("deliberate adversarial failure")
        if node in {
            WritingPass.STORY_ARCHITECTURE,
            WritingPass.HEADLINE_ADJUDICATION,
            WritingPass.DRAFT_GENERATION,
            WritingPass.FINAL_SYNTHESIS,
        }:
            scope = (
                ("FINANCE_BROAD" if mode == "FINANCE_DEEP" else "FINANCE_DEEP")
                if wrong_scope_for == (node, mode) else mode
            )
            if node == WritingPass.STORY_ARCHITECTURE:
                return {"story_blueprint": {"product_mode": scope, "sections": ["story"]}}
            if node == WritingPass.HEADLINE_ADJUDICATION:
                return {"headline_decision": {"product_mode": scope, "selected_title": f"{mode} title"}}
            if node == WritingPass.DRAFT_GENERATION:
                return {"draft": {"product_mode": scope, "title": f"{mode} title", "body": "actual draft body"}}
            return {
                "publication_candidate": {
                    "product_mode": scope,
                    "body": "same body" if cloned_bodies else f"{mode} final candidate",
                },
                "publication_fitness": _fitness(
                    scope, revise=(revise_mode == mode),
                    omit_gates=(omit_gates_for == mode),
                ),
            }
        if node == WritingPass.PLATFORM_INTERACTION_ADAPTATION:
            return {
                "platform_interaction_pack": {
                    "topic": "current financial topic",
                    "posts": [
                        {
                            "platform_family": "WECHAT_IMAGE_TEXT",
                            "hook": "native one",
                            "body": "native post one",
                            "interaction_prompt": "Question one?",
                        },
                        {
                            "platform_family": "TOUTIAO_MICRO",
                            "hook": "native two",
                            "body": "native post two",
                            "interaction_prompt": "Question two?",
                        },
                        {
                            "platform_family": "GENERIC_DYNAMIC",
                            "hook": "native three",
                            "body": "native post three",
                            "interaction_prompt": "Question three?",
                        },
                    ][:2] if incomplete_interaction else [
                        {
                            "platform_family": family,
                            "hook": f"native hook {i}",
                            "body": f"native post {i}",
                            "interaction_prompt": f"Reader question {i}?",
                        }
                        for i, family in enumerate((
                            "WECHAT_IMAGE_TEXT", "TOUTIAO_MICRO", "GENERIC_DYNAMIC"
                        ))
                    ],
                    "evidence_boundary": "only claims in audited evidence",
                    "independent_rewrite_from_long_form": True,
                }
            }
        if node == WritingPass.PLATFORM_INTERACTION_AUDIT:
            return {"platform_interaction_fitness": {"status": "PASS", "evidence_refs": ["audit://interaction"]}}
        return {
            name: f"synthetic-work-product:{node.value}:{name}"
            for name in PASS_CONTRACTS[node].outputs
        }
    return run


def _research_audit(calls):
    def audit(inputs):
        calls.append("RESEARCH_AUDIT")
        assert "decision_envelope" in inputs
        assert "private_research_brief" in inputs
        return {
            "status": "PASS",
            "evidence_refs": ["audit://research"],
            "audited_evidence": {"source_refs": ["source://primary/current"], "synthetic": True},
        }
    return audit


def test_every_longform_pass_receives_explicit_product_mode_and_interaction_pass_receives_product_scope():
    for node in LONGFORM_PRODUCT_PASSES:
        assert "product_mode" in PASS_CONTRACTS[node].required_inputs
    for node in INTERACTION_PRODUCT_PASSES:
        assert "product_scope" in PASS_CONTRACTS[node].required_inputs


def test_portfolio_executes_shared_research_once_and_independent_products_separately():
    calls = []
    audit_calls = []
    result = execute_portfolio_writing(
        _seed(),
        required_outputs=[
            "AUDIT_DOCX",
            "FINANCE_DEEP_DOCX",
            "FINANCE_BROAD_DOCX",
            "PLATFORM_INTERACTION_PACK_DOCX",
        ],
        execute_pass=_executor(calls),
        research_audit=_research_audit(audit_calls),
    )

    counts = Counter(node for node, _ in calls)
    for node in SHARED_RESEARCH_PASSES:
        assert counts[node] == 1
    for node in LONGFORM_PRODUCT_PASSES:
        assert counts[node] == 2
        assert {mode for called, mode in calls if called == node} == {"FINANCE_DEEP", "FINANCE_BROAD"}
    for node in INTERACTION_PRODUCT_PASSES:
        assert counts[node] == 1
        assert (node, None) in calls

    assert audit_calls == ["RESEARCH_AUDIT"]
    assert result["execution_scope"] == "FINANCIAL_PRODUCT_PORTFOLIO"
    assert result["pass_count"] == 25
    assert len(result["trace"]) == 26
    assert result["shared_research_pass_count"] == 5
    assert set(result["longform_products"]) == {"FINANCE_DEEP", "FINANCE_BROAD"}
    assert result["longform_products"]["FINANCE_DEEP"]["story_blueprint"]["product_mode"] == "FINANCE_DEEP"
    assert result["longform_products"]["FINANCE_BROAD"]["story_blueprint"]["product_mode"] == "FINANCE_BROAD"
    assert result["platform_interaction"]["platform_interaction_pack"]["independent_rewrite_from_long_form"] is True
    assert result["assurance"] == (
        "PORTFOLIO_CALLBACK_DATAFLOW_EXECUTED"
        "__NOT_SEMANTIC_QUALITY_OR_INDEPENDENT_EDITORIAL_ACCEPTANCE"
    )


def test_historical_dual_output_does_not_invent_an_interaction_product():
    calls = []
    result = execute_portfolio_writing(
        _seed(interaction=False),
        required_outputs=["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"],
        execute_pass=_executor(calls),
        research_audit=_research_audit([]),
    )
    assert set(result["longform_products"]) == {"FINANCE_DEEP", "FINANCE_BROAD"}
    assert result["platform_interaction"] is None
    assert not any(node in INTERACTION_PRODUCT_PASSES for node, _ in calls)
    assert result["pass_count"] == 23


def test_acquisition_mode_runs_broad_and_interaction_without_fabricating_deep():
    calls = []
    result = execute_portfolio_writing(
        _seed(),
        required_outputs=["AUDIT_DOCX", "FINANCE_BROAD_DOCX", "PLATFORM_INTERACTION_PACK_DOCX"],
        execute_pass=_executor(calls),
        research_audit=_research_audit([]),
    )
    assert set(result["longform_products"]) == {"FINANCE_BROAD"}
    assert result["platform_interaction"] is not None
    assert not any(mode == "FINANCE_DEEP" for _, mode in calls)
    assert result["pass_count"] == 16


def test_research_audit_failure_stops_before_any_product_branch():
    calls = []
    invoked = []
    def audit(inputs):
        invoked.append("RESEARCH_AUDIT")
        return {"status": "PASS", "evidence_refs": []}

    with pytest.raises(WritingPassExecutionError, match="WRITING_RESEARCH_AUDIT_NOT_ADMITTED"):
        execute_portfolio_writing(
            _seed(),
            required_outputs=["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"],
            execute_pass=_executor(calls),
            research_audit=audit,
        )
    assert invoked == ["RESEARCH_AUDIT"]
    assert not any(node in LONGFORM_PRODUCT_PASSES for node, _ in calls)


def test_deep_branch_failure_stops_before_broad_and_interaction_branches():
    calls = []
    with pytest.raises(
        WritingPassExecutionError,
        match="WRITING_PASS_EXECUTION_FAILED:FACT_INTEGRITY_AUDIT:FINANCE_DEEP",
    ):
        execute_portfolio_writing(
            _seed(),
            required_outputs=[
                "AUDIT_DOCX",
                "FINANCE_DEEP_DOCX",
                "FINANCE_BROAD_DOCX",
                "PLATFORM_INTERACTION_PACK_DOCX",
            ],
            execute_pass=_executor(
                calls, fail_at=(WritingPass.FACT_INTEGRITY_AUDIT, "FINANCE_DEEP"),
            ),
            research_audit=_research_audit([]),
        )
    assert not any(mode == "FINANCE_BROAD" for _, mode in calls)
    assert not any(node in INTERACTION_PRODUCT_PASSES for node, _ in calls)


def test_product_scope_mismatch_is_rejected_before_another_product_is_run():
    calls = []
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_PRODUCT_SCOPE_MISMATCH"):
        execute_portfolio_writing(
            _seed(),
            required_outputs=["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"],
            execute_pass=_executor(
                calls, wrong_scope_for=(WritingPass.STORY_ARCHITECTURE, "FINANCE_DEEP"),
            ),
            research_audit=_research_audit([]),
        )
    assert not any(mode == "FINANCE_BROAD" for _, mode in calls)


@pytest.mark.parametrize(
    "required_outputs,match",
    [
        (["FINANCE_DEEP_DOCX"], "PORTFOLIO_AUDIT_DOCX_REQUIRED"),
        (["AUDIT_DOCX"], "PORTFOLIO_HAS_NO_PUBLICATION_PRODUCT"),
        (["AUDIT_DOCX", "UNKNOWN_DOCX"], "PORTFOLIO_OUTPUT_KIND_UNSUPPORTED"),
        (["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_DEEP_DOCX"], "PORTFOLIO_REQUIRED_OUTPUTS_INVALID"),
    ],
)
def test_portfolio_output_contract_rejects_missing_or_ambiguous_products(required_outputs, match):
    with pytest.raises(WritingPassExecutionError, match=match):
        execute_portfolio_writing(
            _seed(),
            required_outputs=required_outputs,
            execute_pass=_executor([]),
            research_audit=_research_audit([]),
        )


def test_invalid_publication_gate_cannot_be_hidden_behind_final_synthesis_pass():
    calls = []
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_PUBLICATION_FITNESS_INVALID:FINANCE_DEEP"):
        execute_portfolio_writing(
            _seed(),
            required_outputs=["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"],
            execute_pass=_executor(calls, omit_gates_for="FINANCE_DEEP"),
            research_audit=_research_audit([]),
        )
    assert not any(mode == "FINANCE_BROAD" for _, mode in calls)


def test_revise_gate_blocks_other_publication_products():
    calls = []
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_PUBLICATION_FITNESS_REVISE:FINANCE_DEEP"):
        execute_portfolio_writing(
            _seed(),
            required_outputs=["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"],
            execute_pass=_executor(calls, revise_mode="FINANCE_DEEP"),
            research_audit=_research_audit([]),
        )
    assert not any(mode == "FINANCE_BROAD" for _, mode in calls)


def test_directly_cloned_deep_and_broad_final_body_is_rejected():
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_LONGFORM_BODY_CLONED"):
        execute_portfolio_writing(
            _seed(),
            required_outputs=["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"],
            execute_pass=_executor([], cloned_bodies=True),
            research_audit=_research_audit([]),
        )


def test_incomplete_short_form_platform_pack_is_rejected_by_current_schema():
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_INTERACTION_PACK_INVALID"):
        execute_portfolio_writing(
            _seed(),
            required_outputs=["AUDIT_DOCX", "FINANCE_BROAD_DOCX", "PLATFORM_INTERACTION_PACK_DOCX"],
            execute_pass=_executor([], incomplete_interaction=True),
            research_audit=_research_audit([]),
        )


def test_noncanonical_output_combinations_cannot_bypass_task_contract():
    with pytest.raises(WritingPassExecutionError, match="PORTFOLIO_OUTPUTS_NOT_CANONICAL_TASK_CONTRACT"):
        execute_portfolio_writing(
            _seed(),
            required_outputs=["AUDIT_DOCX", "PLATFORM_INTERACTION_PACK_DOCX"],
            execute_pass=_executor([]),
            research_audit=_research_audit([]),
        )


def test_canonical_modes_are_stable_across_five_distribution_types():
    from financial_writing_agent.models import DistributionMode, TaskContract

    for mode in DistributionMode:
        required = [kind.value for kind in TaskContract(
            prompt="canonical mode test", distribution_mode=mode,
        ).required_outputs]
        result = execute_portfolio_writing(
            _seed(),
            required_outputs=required,
            execute_pass=_executor([]),
            research_audit=_research_audit([]),
        )
        assert set(result["required_output_kinds"]) == set(required)
