from pathlib import Path

from financial_writing_agent.story_quality import (
    NarrativeEngine,
    OpeningDesign,
    ProductMode,
    SectionBlueprint,
    StoryBlueprint,
    publication_structure_findings,
)

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _h1_headings(markdown: str) -> list[str]:
    return [line[3:].strip() for line in markdown.splitlines() if line.startswith("## ")]


def test_rejected_cross_border_legacy_audit_is_not_current_publication_fitness_evidence():
    audit = _read("workspaces/articles/cross-border-ecommerce-20261015/reviews/EDITORIAL_AUDIT.md")
    assert "Decision: `PASS`" in audit
    assert "Final decision: `PASS -> DELIVERY`" in audit

    mandatory_gates = {
        "FACT_INTEGRITY",
        "RETENTION",
        "COMPANY_GROUNDING",
        "STRUCTURE_NUMBERING",
        "ORIGINALITY",
        "AUTHORIAL_STYLE",
        "COMPLIANCE",
        "PAYOFF",
    }
    present = {gate for gate in mandatory_gates if gate in audit}
    assert present != mandatory_gates
    for evidence_field in ("location", "excerpt", "finding", "severity"):
        assert evidence_field not in audit


def test_rejected_cross_border_replay_exposes_temporal_fact_integrity_risk():
    draft = _read("workspaces/articles/cross-border-ecommerce-20261015/stages/DRAFT.md")
    research = _read("workspaces/articles/cross-border-ecommerce-20261015/stages/RESEARCH.md")
    # The task date is 2026-10-15, so an unqualified November 1 rule cannot be narrated as already effective.
    assert "2026年11月1日" in research or "11 月 1 日" in research or "11月1日" in draft
    assert "Task: `cross-border-ecommerce-20261015`" in draft


def test_held_out_ice_snow_article_has_compatible_non_cross_border_story_geometry():
    article = _read("workspaces/articles/ice-snow-economy-20261013/publication/FINANCE_DEEP.md")
    headings = _h1_headings(article)
    assert len(headings) >= 3
    assert publication_structure_findings(headings[: min(len(headings), 10)]) == []
    for company in ("长白山", "天府文旅", "冰山冷热", "雪人集团", "三夫户外"):
        assert company in article

    blueprint = StoryBlueprint(
        product_mode=ProductMode.FINANCE_DEEP,
        reader_job="区分冰雪经济不同现金流位置和利润传导",
        reader_starting_state="知道产业规模增长但容易把相关公司视为同一种受益",
        article_promise="用目的地、设备工程和品牌消费三种经济模型拆开利润来源",
        central_question="同一个冰雪经济为什么公司赚的是三种不同的钱",
        author_stance="产业规模是需求底座，不是上市公司利润保证",
        narrative_engine=NarrativeEngine.SYSTEM_MAP,
        opening=OpeningDesign(
            concrete_anchor="同一产业里长白山扭亏、天府文旅亏损、雪人集团增收不增利",
            hard_fact_or_scene="三家公司在同一主题下给出方向不同的中报结果",
            reader_information_gap="为什么产业增长没有沿同一条链传导到利润",
            why_reader_should_care="现金流位置不同决定了公司真正该验证的指标不同",
            early_payoff="先把公司分成客流、工程和品牌三类",
            deliberately_withheld_payoff="最后比较三类模式的兑现距离和主要反例",
        ),
        sections=[
            SectionBlueprint(
                sequence_label="一、",
                working_heading="客流型：需求和天气直接改写结果",
                reader_question="目的地运营为什么对经营季和单位客流价值敏感",
                new_information=["长白山与天府文旅在同一需求底座下出现相反利润结果"],
                company_anchors=["长白山", "天府文旅"],
                value_chain_classes=["destination"],
                evidence_refs=["ice-snow-heldout:destination"],
                tension_or_open_loop="需求增长为什么仍可能亏损",
                section_payoff="天气、经营季和固定成本解释利润弹性",
                bridge_to_next="如果把自然条件拿掉，室内化仍要经过项目和毛利关口",
            ),
            SectionBlueprint(
                sequence_label="二、",
                working_heading="工程型：订单之后还有交付和毛利",
                reader_question="场馆扩张为什么不等于设备企业利润同步增长",
                new_information=["冰山冷热与雪人集团说明收入和利润可以继续分化"],
                company_anchors=["冰山冷热", "雪人集团"],
                value_chain_classes=["equipment"],
                evidence_refs=["ice-snow-heldout:equipment"],
                tension_or_open_loop="新增场馆如何穿透到项目利润",
                section_payoff="交付节奏、原材料、竞争和回款决定兑现",
                bridge_to_next="消费端则要从一次体验走到持续复购",
            ),
            SectionBlueprint(
                sequence_label="三、",
                working_heading="品牌型：参与人数不是复购",
                reader_question="专业化消费如何才会形成持续品牌收入",
                new_information=["三夫户外和探路者需要区分冰雪相关增长与集团其他业务"],
                company_anchors=["三夫户外", "探路者"],
                value_chain_classes=["brand"],
                evidence_refs=["ice-snow-heldout:brand"],
                tension_or_open_loop="参与人数增长能否转成复购和品牌利润",
                section_payoff="渠道效率、产品结构和复购决定消费端兑现",
                bridge_to_next="三类现金流位置最终形成不同验证指标",
            ),
        ],
        material_value_chain_classes=["destination", "equipment", "brand"],
        default_word_limit=None,
        ending_payoff="形成不依赖跨境电商主题的现金流位置比较模型",
        voice_evidence_refs=["heldout-existing-publication"],
    )
    assert blueprint.narrative_engine == NarrativeEngine.SYSTEM_MAP
