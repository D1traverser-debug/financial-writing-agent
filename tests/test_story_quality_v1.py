import pytest
from pydantic import ValidationError

from financial_writing_agent.story_quality import (
    AuditStatus,
    GateAudit,
    NarrativeEngine,
    OpeningDesign,
    OriginalityEvidence,
    ProductMode,
    PublicationFitness,
    SectionBlueprint,
    StoryBlueprint,
    TextEvidence,
    generic_scaffolding_findings,
    publication_structure_findings,
)


def _opening() -> OpeningDesign:
    return OpeningDesign(
        concrete_anchor="乐歌海外仓出口行业量大增但公司收入没有同步增长",
        hard_fact_or_scene="行业海外仓出口增长与公司收入形成反差",
        reader_information_gap="为什么量涨了，利润池却没有同步落到仓企收入",
        why_reader_should_care="这决定跨境电商价值链中谁真正吸收新增成本",
        early_payoff="先证明海外仓不是无条件赢家",
        deliberately_withheld_payoff="最终比较利润池在品牌、B2B、履约、支付与合规间如何迁移",
    )


def _section(label: str, heading: str, company: str, chain: str) -> SectionBlueprint:
    return SectionBlueprint(
        sequence_label=label,
        working_heading=heading,
        reader_question=f"{heading}为什么成立",
        new_information=["new evidence"],
        company_anchors=[company],
        value_chain_classes=[chain],
        evidence_refs=[f"evidence:{company}"],
        tension_or_open_loop="当前数据与直觉冲突",
        section_payoff="给出公司级解释",
        bridge_to_next="上一环节的成本转移到下一环节",
    )


def _deep() -> StoryBlueprint:
    return StoryBlueprint(
        product_mode=ProductMode.FINANCE_DEEP,
        reader_job="理解跨境电商利润池迁移并区分公司",
        reader_starting_state="知道行业增长但容易把概念股视为一类",
        article_promise="把价值链全部展开并用公司逐环节验证",
        central_question="规则变化后利润池到底向哪里迁移",
        author_stance="拒绝单环节赢家叙事，按单位经济性比较",
        narrative_engine=NarrativeEngine.COMPANY_CONFLICT,
        opening=_opening(),
        sections=[
            _section("一、", "低价直邮先变难", "华凯易佰", "seller"),
            _section("二、", "品牌与精品能否吸收成本", "安克创新", "brand"),
            _section("三、", "海外仓不是稳赚牌", "乐歌股份", "fulfilment"),
            _section("四、", "B2B与支付承接复杂度", "焦点科技", "infrastructure"),
        ],
        material_value_chain_classes=["seller", "brand", "fulfilment", "infrastructure"],
        default_word_limit=None,
        ending_payoff="回到利润池迁移并给出可验证条件",
        voice_evidence_refs=["user-approved-style"],
    )


def test_deep_blueprint_requires_explicit_numbering_company_grounding_and_full_chain_coverage():
    deep = _deep()
    assert [section.sequence_label for section in deep.sections] == ["一、", "二、", "三、", "四、"]

    data = deep.model_dump()
    data["sections"][1]["company_anchors"] = []
    with pytest.raises(ValidationError):
        StoryBlueprint.model_validate(data)


def test_deep_has_no_default_word_ceiling():
    data = _deep().model_dump()
    data["default_word_limit"] = 3500
    with pytest.raises(ValidationError):
        StoryBlueprint.model_validate(data)


def _gate(name: str, status: AuditStatus = AuditStatus.PASS, severity: str = "INFO") -> GateAudit:
    return GateAudit(
        gate=name,
        status=status,
        evidence=[
            TextEvidence(
                location="opening/section",
                excerpt="具体文本证据",
                finding="checked against the gate",
                severity=severity,
            )
        ],
        checked_items=["opening", "H1 transitions", "ending"],
        revision_actions=["rewrite span"] if status == AuditStatus.REVISE else [],
    )


def _all_gates() -> list[GateAudit]:
    return [
        _gate("FACT_INTEGRITY"),
        _gate("RETENTION"),
        _gate("COMPANY_GROUNDING"),
        _gate("STRUCTURE_NUMBERING"),
        _gate("ORIGINALITY"),
        _gate("AUTHORIAL_STYLE"),
        _gate("COMPLIANCE"),
        _gate("PAYOFF"),
    ]


def _originality() -> list[OriginalityEvidence]:
    return [
        OriginalityEvidence(
            compared_source_ref="source",
            checked_phrase_or_passage="phrase",
            result="NO_MATERIAL_OVERLAP",
            notes="checked",
        )
    ]


def test_publication_fitness_cannot_self_pass_without_all_text_evidence_gates():
    gates = _all_gates()[:-1]
    with pytest.raises(ValidationError):
        PublicationFitness(
            product_mode=ProductMode.FINANCE_DEEP,
            gates=gates,
            originality_checks=_originality(),
            assurance="CHAT_SELF_REVIEW",
            final_status=AuditStatus.PASS,
        )


def test_originality_rewrite_blocks_pass():
    with pytest.raises(ValidationError):
        PublicationFitness(
            product_mode=ProductMode.FINANCE_DEEP,
            gates=_all_gates(),
            originality_checks=[
                OriginalityEvidence(
                    compared_source_ref="source",
                    checked_phrase_or_passage="distinctive phrase",
                    result="NEEDS_REWRITE",
                    notes="too close to source expression",
                )
            ],
            assurance="CHAT_SELF_REVIEW",
            final_status=AuditStatus.PASS,
        )


def test_independent_publication_fitness_requires_distinct_bound_provenance():
    with pytest.raises(ValidationError):
        PublicationFitness(
            product_mode=ProductMode.FINANCE_DEEP,
            gates=_all_gates(),
            originality_checks=_originality(),
            assurance="INDEPENDENT_EXECUTOR",
            final_status=AuditStatus.PASS,
        )

    with pytest.raises(ValidationError):
        PublicationFitness(
            product_mode=ProductMode.FINANCE_DEEP,
            gates=_all_gates(),
            originality_checks=_originality(),
            assurance="INDEPENDENT_EXECUTOR",
            audit_provenance={
                "assurance": "INDEPENDENT_EXECUTOR",
                "reviewer_identity": "reviewer-1",
                "author_identity": "reviewer-1",
                "execution_ref": "run://independent-1",
            },
            final_status=AuditStatus.PASS,
        )

    valid = PublicationFitness(
        product_mode=ProductMode.FINANCE_DEEP,
        gates=_all_gates(),
        originality_checks=_originality(),
        assurance="INDEPENDENT_EXECUTOR",
        audit_provenance={
            "assurance": "INDEPENDENT_EXECUTOR",
            "reviewer_identity": "reviewer-2",
            "author_identity": "author-1",
            "execution_ref": "run://independent-2",
        },
        final_status=AuditStatus.PASS,
    )
    assert valid.audit_provenance.execution_ref == "run://independent-2"


def test_deterministic_tripwires_find_missing_sequences_and_generic_scaffolding_clusters():
    assert publication_structure_findings(["行业变化", "二、第二节"])
    text = "值得关注。需要注意。这意味着。问题在于。" * 8
    result = generic_scaffolding_findings(text)
    assert result["requires_semantic_style_review"] is True
