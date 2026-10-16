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
        reader_job="理解跨境电商利润如何迁移并区分公司",
        reader_starting_state="知道行业增长但容易把概念股视为一类",
        article_promise="从完整研究图里只选决定利润迁移的核心链路，用公司验证传导",
        central_question="规则变化后利润池到底向哪里迁移",
        author_stance="拒绝把研究目录当文章目录，按单位经济性和公司兑现选择正文",
        narrative_engine=NarrativeEngine.COMPANY_CONFLICT,
        opening=_opening(),
        sections=[
            _section("一、", "低价直邮先变难", "华凯易佰", "seller"),
            _section("二、", "品牌与精品能否吸收成本", "安克创新", "brand"),
            _section("三、", "海外仓不是稳赚牌", "乐歌股份", "fulfilment"),
            _section("四、", "B2B承接部分订单结构变化", "焦点科技", "infrastructure"),
        ],
        material_value_chain_classes=["seller", "brand", "fulfilment", "infrastructure", "marketing", "returns"],
        publication_scope_decisions=[
            {"value_chain_class": "seller", "disposition": "CORE", "rationale": "规则变化首先进入卖家单位经济性", "evidence_refs": ["seller"]},
            {"value_chain_class": "brand", "disposition": "CORE", "rationale": "品牌/精品是成本吸收能力的核心反例", "evidence_refs": ["brand"]},
            {"value_chain_class": "fulfilment", "disposition": "CORE", "rationale": "海外仓量价背离直接检验利润传导", "evidence_refs": ["fulfilment"]},
            {"value_chain_class": "infrastructure", "disposition": "SUPPORT", "rationale": "B2B说明订单结构可以改变但不是全文主线", "evidence_refs": ["b2b"]},
            {"value_chain_class": "marketing", "disposition": "OMIT_WITH_REASON", "rationale": "当前证据不足以改变主线，保留研究不进入正文", "evidence_refs": ["marketing"]},
            {"value_chain_class": "returns", "disposition": "OMIT_WITH_REASON", "rationale": "属于完整研究地图但不是当前事件的主要利润传导节点", "evidence_refs": ["returns"]},
        ],
        default_word_limit=None,
        ending_payoff="回到利润池迁移并给出可验证条件",
        voice_evidence_refs=["user-approved-style"],
    )


def test_deep_blueprint_requires_numbering_company_grounding_and_explicit_publication_scope():
    deep = _deep()
    assert [section.sequence_label for section in deep.sections] == ["一、", "二、", "三、", "四、"]
    assert len(deep.material_value_chain_classes) > len({c for section in deep.sections for c in section.value_chain_classes})

    data = deep.model_dump()
    data["sections"][1]["company_anchors"] = []
    with pytest.raises(ValidationError):
        StoryBlueprint.model_validate(data)

    data = deep.model_dump()
    data["publication_scope_decisions"] = []
    with pytest.raises(ValidationError):
        StoryBlueprint.model_validate(data)


def test_deep_research_completeness_does_not_force_every_class_into_publication():
    deep = _deep()
    omitted = {d.value_chain_class for d in deep.publication_scope_decisions if d.disposition.value == "OMIT_WITH_REASON"}
    covered = {c for section in deep.sections for c in section.value_chain_classes}
    assert omitted == {"marketing", "returns"}
    assert not (omitted & covered)


def test_deep_has_no_default_word_ceiling():
    data = _deep().model_dump()
    data["default_word_limit"] = 3500
    with pytest.raises(ValidationError):
        StoryBlueprint.model_validate(data)


def test_event_to_company_requires_full_causal_transmission_per_material_section():
    data = _deep().model_dump()
    data["narrative_engine"] = "EVENT_TO_COMPANY"
    with pytest.raises(ValidationError):
        StoryBlueprint.model_validate(data)

    for section in data["sections"]:
        section["causal_transmission"] = {
            "trigger_or_change": "低值进口规则变化",
            "mechanism": "固定合规/关税成本改变低客单价商品单位经济性",
            "company_exposure": f"{section['company_anchors'][0]}通过对应业务暴露于该变化",
            "operating_or_financial_expression": "收入结构、毛利、库存或费用出现可观察变化",
            "verification_or_reversal_condition": "后续公告若显示成本被平台补贴或提价完全吸收则削弱该判断",
        }
    blueprint = StoryBlueprint.model_validate(data)
    assert blueprint.narrative_engine == NarrativeEngine.EVENT_TO_COMPANY


def _gate(name: str, status: AuditStatus = AuditStatus.PASS, severity: str = "INFO") -> GateAudit:
    return GateAudit(
        gate=name,
        status=status,
        evidence=[TextEvidence(location="opening/section", excerpt="具体文本证据", finding="checked against the gate", severity=severity)],
        checked_items=["opening", "H1 transitions", "ending"],
        revision_actions=["rewrite span"] if status == AuditStatus.REVISE else [],
    )


def _all_gates() -> list[GateAudit]:
    return [_gate(name) for name in ("FACT_INTEGRITY", "RETENTION", "COMPANY_GROUNDING", "STRUCTURE_NUMBERING", "ORIGINALITY", "AUTHORIAL_STYLE", "COMPLIANCE", "PAYOFF")]


def _originality() -> list[OriginalityEvidence]:
    return [OriginalityEvidence(compared_source_ref="source", checked_phrase_or_passage="phrase", result="NO_MATERIAL_OVERLAP", notes="checked")]


def test_publication_fitness_cannot_self_pass_without_all_text_evidence_gates():
    with pytest.raises(ValidationError):
        PublicationFitness(product_mode=ProductMode.FINANCE_DEEP, gates=_all_gates()[:-1], originality_checks=_originality(), assurance="CHAT_SELF_REVIEW", final_status=AuditStatus.PASS)


def test_originality_rewrite_blocks_pass():
    with pytest.raises(ValidationError):
        PublicationFitness(product_mode=ProductMode.FINANCE_DEEP, gates=_all_gates(), originality_checks=[OriginalityEvidence(compared_source_ref="source", checked_phrase_or_passage="distinctive phrase", result="NEEDS_REWRITE", notes="too close to source expression")], assurance="CHAT_SELF_REVIEW", final_status=AuditStatus.PASS)


def test_independent_publication_fitness_is_fail_closed_without_trusted_execution_resolver():
    independent_claims = [None, {"assurance": "INDEPENDENT_EXECUTOR", "reviewer_identity": "reviewer-1", "author_identity": "reviewer-1", "execution_ref": "run://same-identity"}, {"assurance": "INDEPENDENT_EXECUTOR", "reviewer_identity": "reviewer-2", "author_identity": "author-1", "execution_ref": "run://caller-supplied-only"}]
    for provenance in independent_claims:
        kwargs = {} if provenance is None else {"audit_provenance": provenance}
        with pytest.raises(ValidationError):
            PublicationFitness(product_mode=ProductMode.FINANCE_DEEP, gates=_all_gates(), originality_checks=_originality(), assurance="INDEPENDENT_EXECUTOR", final_status=AuditStatus.PASS, **kwargs)


def test_deterministic_tripwires_find_missing_sequences_and_generic_scaffolding_clusters():
    assert publication_structure_findings(["行业变化", "二、第二节"])
    result = generic_scaffolding_findings("值得关注。需要注意。这意味着。问题在于。" * 8)
    assert result["requires_semantic_style_review"] is True
