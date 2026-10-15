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
from financial_writing_agent.owner_lifecycle import block_review_failure_state, resume_blocked_state


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
            {
                "ref": "filing-a",
                "kind": "CURRENT_FACT",
                "summary": "company evidence",
                "source_family": "company-filing",
            },
            {
                "ref": "policy-b",
                "kind": "CURRENT_FACT",
                "summary": "policy evidence",
                "source_family": "government",
            },
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
        "counterexamples": ["macro overseas-warehouse volume rose while a warehouse operator's revenue did not"],
        "rejected_paths": ["A failed the company-level counterexample"],
        "selected_candidate_id": "B",
        "selection_rationale": "B survives the observed company-level contradiction",
        "saturation": {
            "sweeps": [
                {
                    "sweep_no": 1,
                    "query_or_scope": "industry and company scan",
                    "source_families": ["company-filing", "government"],
                    "new_material_candidates": ["B"],
                    "changed_decision": True,
                },
                {
                    "sweep_no": 2,
                    "query_or_scope": "counterexample scan",
                    "source_families": ["platform", "company-filing"],
                },
                {
                    "sweep_no": 3,
                    "query_or_scope": "saturation scan",
                    "source_families": ["government", "industry"],
                },
            ],
            "stop_reason": "two consecutive sweeps produced no decision-changing delta",
        },
        "verification_plan": ["research audit", "company decision map"],
    }


def _blueprint(mode: str) -> dict:
    sections = [
        {
            "sequence_label": "一、",
            "working_heading": "第一环节",
            "reader_question": "第一环节发生了什么",
            "new_information": ["事实1"],
            "company_anchors": ["公司A"],
            "value_chain_classes": ["seller"],
            "evidence_refs": ["e1"],
            "tension_or_open_loop": "量与利润分化",
            "section_payoff": "解释卖家端",
            "bridge_to_next": "成本继续向品牌端传导",
        },
        {
            "sequence_label": "二、",
            "working_heading": "第二环节",
            "reader_question": "品牌如何吸收成本",
            "new_information": ["事实2"],
            "company_anchors": ["公司B"],
            "value_chain_classes": ["brand"],
            "evidence_refs": ["e2"],
            "tension_or_open_loop": "高毛利也有费用代价",
            "section_payoff": "解释品牌端",
            "bridge_to_next": "履约仍决定最终成本",
        },
        {
            "sequence_label": "三、",
            "working_heading": "第三环节",
            "reader_question": "履约为何不是稳赚",
            "new_information": ["事实3"],
            "company_anchors": ["公司C"],
            "value_chain_classes": ["fulfilment"],
            "evidence_refs": ["e3"],
            "tension_or_open_loop": "业务量和收入不等价",
            "section_payoff": "解释履约端",
            "bridge_to_next": "回到整条利润池",
        },
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
        "FACT_INTEGRITY",
        "RETENTION",
        "COMPANY_GROUNDING",
        "STRUCTURE_NUMBERING",
        "ORIGINALITY",
        "AUTHORIAL_STYLE",
        "COMPLIANCE",
        "PAYOFF",
    ):
        gates.append(
            {
                "gate": gate,
                "status": status,
                "evidence": [
                    {
                        "location": "opening/section",
                        "excerpt": "具体文本证据",
                        "finding": f"{gate} checked",
                        "severity": "INFO" if status == "PASS" else "MAJOR",
                    }
                ],
                "checked_items": ["opening", "section", "ending"],
                "revision_actions": [] if status == "PASS" else ["rewrite affected span"],
            }
        )
    return {
        "product_mode": mode,
        "gates": gates,
        "originality_checks": [
            {
                "compared_source_ref": "source-1",
                "checked_phrase_or_passage": "candidate passage",
                "result": "NO_MATERIAL_OVERLAP",
                "notes": "checked against material source",
            }
        ],
        "assurance": "CHAT_SELF_REVIEW",
        "final_status": status,
    }


def _new_state(task_id: str = "admission-test") -> dict:
    return build_initial_state(
        task_id=task_id,
        prompt="写一篇行业财经文章",
        source_refs=[],
        executor_identity="test",
    )


def _advance_to_editorial(state: dict) -> dict:
    task_id = state["task_id"]
    state = advance_state(state, previous_state_blob_sha="s0", executor_identity="test")
    state = advance_state(
        state,
        previous_state_blob_sha="s1",
        executor_identity="test",
        decision_envelope=_decision(),
        **_artifact(task_id, "RESEARCH"),
    )
    state = advance_state(
        state,
        previous_state_blob_sha="s2",
        executor_identity="test",
        review_status="PASS",
        **_artifact(task_id, "RESEARCH_AUDIT"),
    )
    return state


def _advance_to_editorial_audit(state: dict) -> dict:
    task_id = state["task_id"]
    state = _advance_to_editorial(state)
    state = advance_state(
        state,
        previous_state_blob_sha="s3",
        executor_identity="test",
        story_blueprints=[_blueprint("FINANCE_DEEP"), _blueprint("FINANCE_BROAD")],
        **_artifact(task_id, "EDITORIAL"),
    )
    state = advance_state(
        state,
        previous_state_blob_sha="s4",
        executor_identity="test",
        **_artifact(task_id, "TITLE"),
    )
    state = advance_state(
        state,
        previous_state_blob_sha="s5",
        executor_identity="test",
        **_artifact(task_id, "DRAFT"),
    )
    return state


def _advance_to_delivery(state: dict) -> dict:
    task_id = state["task_id"]
    state = _advance_to_editorial_audit(state)
    return advance_state(
        state,
        previous_state_blob_sha="s6",
        executor_identity="test",
        review_status="PASS",
        publication_fitnesses=[_fitness("FINANCE_DEEP"), _fitness("FINANCE_BROAD")],
        **_artifact(task_id, "EDITORIAL_AUDIT"),
    )


def _delivery_artifacts(state: dict) -> list[dict]:
    return [
        {"kind": kind, "file_name": f"{kind}.docx", "sha256": "0" * 64}
        for kind in state["required_outputs"]
        if kind != "AUDIT_DOCX"
    ]


def _digest(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_current_tasks_are_marked_v1_while_legacy_builder_remains_compatible():
    current = _new_state("current")
    legacy = owner_guard.build_initial_state(
        task_id="legacy",
        prompt="legacy",
        source_refs=[],
        executor_identity="test",
    )
    assert current["writing_kernel_version"] == "1.0"
    assert current["quality_evidence"] == {}
    assert "writing_kernel_version" not in legacy


def test_research_cannot_advance_on_naked_artifact_without_decision_evidence():
    state = _new_state()
    state = advance_state(state, previous_state_blob_sha="s0", executor_identity="test")
    with pytest.raises(CurrentAdmissionError):
        advance_state(
            state,
            previous_state_blob_sha="s1",
            executor_identity="test",
            **_artifact(state["task_id"], "RESEARCH"),
        )


def test_owner_guard_direct_transition_cannot_bypass_current_research_admission():
    state = _new_state("owner-guard-research-bypass")
    state = advance_state(state, previous_state_blob_sha="b0", executor_identity="test")
    assert state["current_stage"] == "RESEARCH"
    with pytest.raises(owner_guard.GithubChatGuardError):
        owner_guard.advance_state(
            state,
            previous_state_blob_sha="b1",
            executor_identity="test",
            **_artifact(state["task_id"], "RESEARCH"),
        )


def test_editorial_cannot_advance_without_all_required_story_blueprints():
    state = _advance_to_editorial(_new_state())
    with pytest.raises(CurrentAdmissionError):
        advance_state(
            state,
            previous_state_blob_sha="s3",
            executor_identity="test",
            story_blueprints=[_blueprint("FINANCE_DEEP")],
            **_artifact(state["task_id"], "EDITORIAL"),
        )


def test_editorial_audit_pass_requires_evidence_backed_fitness_for_each_longform_product():
    state = _advance_to_editorial_audit(_new_state())
    with pytest.raises(CurrentAdmissionError):
        advance_state(
            state,
            previous_state_blob_sha="s6",
            executor_identity="test",
            review_status="PASS",
            **_artifact(state["task_id"], "EDITORIAL_AUDIT"),
        )

    state = advance_state(
        state,
        previous_state_blob_sha="s6",
        executor_identity="test",
        review_status="PASS",
        publication_fitnesses=[_fitness("FINANCE_DEEP"), _fitness("FINANCE_BROAD")],
        **_artifact(state["task_id"], "EDITORIAL_AUDIT"),
    )
    assert state["current_stage"] == "DELIVERY"
    assert {x["product_mode"] for x in state["quality_evidence"]["publication_fitnesses"]} == {
        "FINANCE_DEEP",
        "FINANCE_BROAD",
    }


def test_persisted_quality_evidence_is_revalidated_and_digest_bound_before_downstream_progress():
    state = _advance_to_delivery(_new_state("persisted-quality"))
    validate_state(state)

    missing = deepcopy(state)
    missing["quality_evidence"].pop("publication_fitnesses")
    with pytest.raises(CurrentAdmissionError):
        validate_state(missing)

    tampered = deepcopy(state)
    tampered["quality_evidence"]["publication_fitnesses"][0]["gates"][0]["evidence"][0]["finding"] = "tampered after admission"
    with pytest.raises(CurrentAdmissionError):
        validate_state(tampered)


def test_owner_guard_direct_delivery_cannot_bypass_tampered_publication_fitness():
    state = _advance_to_delivery(_new_state("owner-guard-delivery-bypass"))
    tampered = deepcopy(state)
    tampered["quality_evidence"].pop("publication_fitnesses")
    with pytest.raises(owner_guard.GithubChatGuardError):
        owner_guard.advance_state(
            tampered,
            previous_state_blob_sha="d7",
            executor_identity="test",
            delivery_artifacts=_delivery_artifacts(tampered),
            **_artifact(tampered["task_id"], "DELIVERY"),
        )


def test_later_wrong_stage_receipt_cannot_spoof_quality_digest_binding():
    state = _advance_to_delivery(_new_state("stage-bound-digest"))
    task_id = state["task_id"]
    state = advance_state(
        state,
        previous_state_blob_sha="s7",
        executor_identity="test",
        delivery_artifacts=_delivery_artifacts(state),
        **_artifact(task_id, "DELIVERY"),
    )
    assert state["current_stage"] == "MECHANICAL_AUDIT"

    tampered = deepcopy(state)
    tampered["quality_evidence"]["publication_fitnesses"][0]["gates"][0]["evidence"][0]["finding"] = "tampered after editorial audit"
    spoof = _digest(tampered["quality_evidence"]["publication_fitnesses"])
    tampered["execution_receipts"][-1]["input_bindings"]["publication_fitnesses_sha256"] = spoof
    assert tampered["execution_receipts"][-1]["stage"] == "DELIVERY"
    with pytest.raises(CurrentAdmissionError):
        validate_state(tampered)


def test_revision_to_research_invalidates_stale_quality_evidence():
    state = _new_state("research-revision")
    task_id = state["task_id"]
    state = advance_state(state, previous_state_blob_sha="r0", executor_identity="test")
    state = advance_state(
        state,
        previous_state_blob_sha="r1",
        executor_identity="test",
        decision_envelope=_decision(),
        **_artifact(task_id, "RESEARCH"),
    )
    assert "research_decision" in state["quality_evidence"]

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


def test_owner_lifecycle_blocked_recovery_uses_central_quality_invalidation():
    state = _new_state("blocked-recovery-quality")
    task_id = state["task_id"]
    state = advance_state(state, previous_state_blob_sha="l0", executor_identity="test")
    state = advance_state(
        state,
        previous_state_blob_sha="l1",
        executor_identity="test",
        decision_envelope=_decision(),
        **_artifact(task_id, "RESEARCH"),
    )
    assert state["current_stage"] == "RESEARCH_AUDIT"
    assert "research_decision" in state["quality_evidence"]

    blocked = block_review_failure_state(
        state,
        previous_state_blob_sha="l2",
        executor_identity="test",
        artifact_key="RESEARCH_AUDIT",
        artifact_path=f"workspaces/articles/{task_id}/RESEARCH_AUDIT.json",
        artifact_blob_sha="blob-research-audit-fail",
        revision_target="RESEARCH",
    )
    assert blocked["status"] == "BLOCKED"

    resumed = resume_blocked_state(
        blocked,
        previous_state_blob_sha="l3",
        executor_identity="test",
        repair_evidence=["re-open research after failed audit"],
    )
    assert resumed["current_stage"] == "RESEARCH"
    assert resumed["quality_evidence"] == {}
    owner_guard.validate_state(resumed)
