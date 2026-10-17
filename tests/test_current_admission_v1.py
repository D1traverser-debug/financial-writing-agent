import hashlib
import json
from copy import deepcopy

import pytest

from financial_writing_agent import owner_guard
from financial_writing_agent.current_admission import (
    CurrentAdmissionError,
    advance_state,
    build_initial_state,
    validate_state,
)
from financial_writing_agent.private_research import (
    PRIVATE_RESEARCH_CONTRACT_VERSION,
    REQUIRED_MODULES,
    V1_0_REQUIRED_MODULES,
    validate_private_research_brief,
)


def _artifact(task_id: str, stage: str) -> dict:
    return {
        "artifact_key": stage,
        "artifact_path": f"workspaces/articles/{task_id}/{stage}.json",
        "artifact_blob_sha": f"blob-{stage.lower()}",
    }


def _decision() -> dict:
    return {
        "decision_id": "thesis-1",
        "operation": "select article thesis",
        "objective": "select the strongest evidence-bounded explanation",
        "operation_class": "MATERIAL_JUDGMENT",
        "evidence": [
            {"ref": "filing-a", "kind": "CURRENT_FACT", "summary": "company evidence", "source_family": "company-filing"},
            {"ref": "policy-b", "kind": "CURRENT_FACT", "summary": "policy evidence", "source_family": "government"},
        ],
        "assumptions_challenged": ["macro growth automatically means the largest listed beneficiary"],
        "alternatives": [
            {
                "candidate_id": "A",
                "mechanism": "macro-volume thesis",
                "advantages": ["simple"],
                "failure_modes": ["company transmission may diverge"],
                "fit_conditions": ["company revenue tracks volume"],
                "misfit_conditions": ["company data diverges"],
            },
            {
                "candidate_id": "B",
                "mechanism": "profit-pool migration thesis",
                "advantages": ["explains company divergence"],
                "failure_modes": ["requires broader chain evidence"],
                "fit_conditions": ["multiple chain nodes show divergent economics"],
                "misfit_conditions": ["all companies move together"],
            },
        ],
        "counterexamples": ["industry volume rose while a relevant company did not realize revenue"],
        "rejected_paths": ["A failed the company-level counterexample"],
        "selected_candidate_id": "B",
        "selection_rationale": "B survives the observed company-level contradiction",
        "saturation": {
            "sweeps": [
                {"sweep_no": 1, "query_or_scope": "industry/company scan", "source_families": ["company-filing", "government"], "new_material_candidates": ["B"], "changed_decision": True},
                {"sweep_no": 2, "query_or_scope": "counterexample scan", "source_families": ["platform", "company-filing"]},
                {"sweep_no": 3, "query_or_scope": "saturation scan", "source_families": ["government", "industry"]},
            ],
            "stop_reason": "two consecutive sweeps produced no decision-changing delta",
        },
        "verification_plan": ["research audit", "company decision map"],
    }


def _brief(version: str = PRIVATE_RESEARCH_CONTRACT_VERSION) -> dict:
    modules = REQUIRED_MODULES if version == "1.1" else V1_0_REQUIRED_MODULES
    return {
        "contract_version": version,
        "as_of": "2026-10-16T15:00:00+08:00",
        "coverage_state": "COMPLETE",
        "modules": {
            name: {
                "status": "APPLICABLE",
                "summary": f"{name} completed with evidence",
                "evidence_refs": [f"{name}-evidence"],
            }
            for name in modules
        },
        "unresolved_gaps": [],
    }


def _blueprint(mode: str) -> dict:
    sections = [
        {
            "sequence_label": label,
            "working_heading": heading,
            "reader_question": question,
            "new_information": [fact],
            "company_anchors": [company],
            "value_chain_classes": [chain],
            "evidence_refs": [evidence],
            "tension_or_open_loop": tension,
            "section_payoff": payoff,
            "bridge_to_next": bridge,
        }
        for label, heading, question, fact, company, chain, evidence, tension, payoff, bridge in [
            ("一、", "第一环节", "第一环节发生了什么", "事实1", "公司A", "seller", "e1", "量与利润分化", "解释卖家端", "成本继续向品牌端传导"),
            ("二、", "第二环节", "品牌如何吸收成本", "事实2", "公司B", "brand", "e2", "高毛利也有费用代价", "解释品牌端", "履约仍决定最终成本"),
            ("三、", "第三环节", "履约为何不是稳赚", "事实3", "公司C", "fulfilment", "e3", "业务量和收入不等价", "解释履约端", "回到整条利润池"),
        ]
    ]
    return {
        "product_mode": mode,
        "reader_job": "理解价值链利润如何迁移",
        "reader_starting_state": "知道行业增长但容易把公司视为一类",
        "article_promise": "用公司逐环节拆解",
        "central_question": "利润池向哪里迁移",
        "author_stance": "拒绝无条件赢家叙事",
        "narrative_engine": "COMPANY_CONFLICT",
        "opening": {
            "concrete_anchor": "一个行业量增而公司收入不增的反差",
            "hard_fact_or_scene": "宏观量和公司收入方向不同",
            "reader_information_gap": "为什么行业增长没有平均落到公司利润",
            "why_reader_should_care": "这决定公司经济性如何分化",
            "early_payoff": "先否定无条件赢家",
            "deliberately_withheld_payoff": "最后给出整条价值链利润池地图",
        },
        "sections": sections,
        "material_value_chain_classes": ["seller", "brand", "fulfilment"] if mode == "FINANCE_DEEP" else [],
        "default_word_limit": None if mode == "FINANCE_DEEP" else 3000,
        "ending_payoff": "形成可验证的利润池迁移模型",
        "voice_evidence_refs": ["voice-1"],
    }


def _fitness(mode: str, status: str = "PASS") -> dict:
    gates = []
    for gate in (
        "FACT_INTEGRITY", "RETENTION", "COMPANY_GROUNDING", "STRUCTURE_NUMBERING",
        "ORIGINALITY", "AUTHORIAL_STYLE", "COMPLIANCE", "PAYOFF",
    ):
        gates.append(
            {
                "gate": gate,
                "status": status,
                "evidence": [{"location": "opening/section", "excerpt": "具体文本证据", "finding": f"{gate} checked", "severity": "INFO" if status == "PASS" else "MAJOR"}],
                "checked_items": ["opening", "section", "ending"],
                "revision_actions": [] if status == "PASS" else ["rewrite affected span"],
            }
        )
    return {
        "product_mode": mode,
        "gates": gates,
        "originality_checks": [{"compared_source_ref": "source-1", "checked_phrase_or_passage": "candidate passage", "result": "NO_MATERIAL_OVERLAP", "notes": "checked"}],
        "assurance": "CHAT_SELF_REVIEW",
        "final_status": status,
    }


def _new_state(task_id: str = "admission-test") -> dict:
    return build_initial_state(task_id=task_id, prompt="写一篇行业财经文章", source_refs=[], executor_identity="test")


def _to_editorial(state: dict) -> dict:
    task_id = state["task_id"]
    state = advance_state(state, previous_state_blob_sha="s0", executor_identity="test")
    state = advance_state(
        state,
        previous_state_blob_sha="s1",
        executor_identity="test",
        decision_envelope=_decision(),
        private_research_brief=_brief(),
        **_artifact(task_id, "RESEARCH"),
    )
    return advance_state(
        state,
        previous_state_blob_sha="s2",
        executor_identity="test",
        review_status="PASS",
        **_artifact(task_id, "RESEARCH_AUDIT"),
    )


def _to_editorial_audit(state: dict) -> dict:
    task_id = state["task_id"]
    state = _to_editorial(state)
    state = advance_state(
        state,
        previous_state_blob_sha="s3",
        executor_identity="test",
        story_blueprints=[_blueprint("FINANCE_DEEP"), _blueprint("FINANCE_BROAD")],
        **_artifact(task_id, "EDITORIAL"),
    )
    state = advance_state(state, previous_state_blob_sha="s4", executor_identity="test", **_artifact(task_id, "TITLE"))
    return advance_state(state, previous_state_blob_sha="s5", executor_identity="test", **_artifact(task_id, "DRAFT"))


def test_new_tasks_bind_private_research_1_1_while_legacy_builder_is_unmarked():
    current = _new_state("current")
    legacy = owner_guard.build_initial_state(
        task_id="legacy",
        prompt="legacy",
        source_refs=[],
        executor_identity="test",
        _current_admission_token=owner_guard._CURRENT_ADMISSION_TOKEN,
    )
    assert current["writing_kernel_version"] == "1.0"
    assert current["private_research_contract_version"] == "1.1"
    assert current["quality_evidence"] == {}
    assert "private_research_contract_version" not in legacy


def test_historical_private_research_1_0_contract_remains_valid_against_1_0_marker():
    legacy_brief = _brief("1.0")
    assert validate_private_research_brief(legacy_brief, expected_contract_version="1.0") == legacy_brief
    with pytest.raises(ValueError):
        validate_private_research_brief(legacy_brief, expected_contract_version="1.1")


def test_research_requires_decision_and_private_research():
    state = _new_state("research-gate")
    state = advance_state(state, previous_state_blob_sha="s0", executor_identity="test")
    with pytest.raises(CurrentAdmissionError):
        advance_state(state, previous_state_blob_sha="s1", executor_identity="test", **_artifact(state["task_id"], "RESEARCH"))
    with pytest.raises(CurrentAdmissionError):
        advance_state(state, previous_state_blob_sha="s1", executor_identity="test", decision_envelope=_decision(), **_artifact(state["task_id"], "RESEARCH"))


def test_private_research_is_persisted_digest_bound_and_tamper_evident():
    state = _new_state("digest")
    state = advance_state(state, previous_state_blob_sha="p0", executor_identity="test")
    state = advance_state(
        state,
        previous_state_blob_sha="p1",
        executor_identity="test",
        decision_envelope=_decision(),
        private_research_brief=_brief(),
        **_artifact(state["task_id"], "RESEARCH"),
    )
    validate_state(state)
    assert state["quality_evidence"]["private_research_brief"]["contract_version"] == "1.1"
    tampered = deepcopy(state)
    tampered["quality_evidence"]["private_research_brief"]["modules"]["cross_segment_global_selection"]["summary"] = "tampered"
    with pytest.raises(CurrentAdmissionError):
        validate_state(tampered)


def test_direct_owner_guard_cannot_bypass_current_research_admission():
    state = _new_state("owner-bypass")
    state = advance_state(state, previous_state_blob_sha="b0", executor_identity="test")
    with pytest.raises(owner_guard.GithubChatGuardError):
        owner_guard.advance_state(state, previous_state_blob_sha="b1", executor_identity="test", **_artifact(state["task_id"], "RESEARCH"))


def test_editorial_requires_both_longform_blueprints():
    state = _to_editorial(_new_state("blueprints"))
    with pytest.raises(CurrentAdmissionError):
        advance_state(
            state,
            previous_state_blob_sha="s3",
            executor_identity="test",
            story_blueprints=[_blueprint("FINANCE_DEEP")],
            **_artifact(state["task_id"], "EDITORIAL"),
        )


def test_editorial_audit_pass_requires_publication_fitness_for_both_products():
    state = _to_editorial_audit(_new_state("fitness"))
    with pytest.raises(CurrentAdmissionError):
        advance_state(state, previous_state_blob_sha="s6", executor_identity="test", review_status="PASS", **_artifact(state["task_id"], "EDITORIAL_AUDIT"))
    state = advance_state(
        state,
        previous_state_blob_sha="s6",
        executor_identity="test",
        review_status="PASS",
        publication_fitnesses=[_fitness("FINANCE_DEEP"), _fitness("FINANCE_BROAD")],
        **_artifact(state["task_id"], "EDITORIAL_AUDIT"),
    )
    assert state["current_stage"] == "DELIVERY"
    validate_state(state)


def test_revision_to_research_invalidates_research_quality_evidence():
    state = _new_state("revision")
    task_id = state["task_id"]
    state = advance_state(state, previous_state_blob_sha="r0", executor_identity="test")
    state = advance_state(
        state,
        previous_state_blob_sha="r1",
        executor_identity="test",
        decision_envelope=_decision(),
        private_research_brief=_brief(),
        **_artifact(task_id, "RESEARCH"),
    )
    revised = advance_state(
        state,
        previous_state_blob_sha="r2",
        executor_identity="test",
        review_status="REVISE",
        revision_target="RESEARCH",
        **_artifact(task_id, "RESEARCH_AUDIT"),
    )
    assert revised["current_stage"] == "RESEARCH"
    assert revised["quality_evidence"] == {}
    validate_state(revised)
