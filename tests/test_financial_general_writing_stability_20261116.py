from __future__ import annotations

import json
from pathlib import Path

from financial_writing_agent.models import DistributionMode, TaskContract
from financial_writing_agent.quality_regression import evaluate_corpus_readiness
from financial_writing_agent.story_quality import NarrativeEngine
from financial_writing_agent.workflow_spec import BUSINESS_STAGE_NAMES
from financial_writing_agent.writing_kernel import LONGFORM_PRODUCT_PASSES, SHARED_RESEARCH_PASSES

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_different_financial_topics_keep_the_same_canonical_workflow_and_shared_spine():
    prompts = [
        "AI网络安全需求变化与上市公司经营兑现",
        "黄酒高端化与经销渠道重构",
        "冰雪经济的客流、设备和消费链条",
        "Meta新模型对企业软件工作流的影响",
        "某上市公司三季报与现金流质量",
        "宏观政策变化对行业需求和利润的传导",
        "根据用户提供的两份公告分析事件影响",
    ]
    contracts = [TaskContract(prompt=prompt) for prompt in prompts]
    expected_outputs = [item.value for item in contracts[0].required_outputs]

    assert BUSINESS_STAGE_NAMES == (
        "INTAKE", "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE",
        "DRAFT", "EDITORIAL_AUDIT", "DELIVERY", "MECHANICAL_AUDIT",
        "FINAL_AUDIT",
    )
    assert all([item.value for item in contract.required_outputs] == expected_outputs
               for contract in contracts)
    assert tuple(item.value for item in SHARED_RESEARCH_PASSES) == (
        "KNOWLEDGE_RECALL", "RESEARCH_DISCOVERY", "RESEARCH_ADVERSARIAL",
        "PRIVATE_RESEARCH_SYNTHESIS", "THESIS_ADJUDICATION",
    )
    assert tuple(item.value for item in LONGFORM_PRODUCT_PASSES) == (
        "STORY_ARCHITECTURE", "HEADLINE_ADJUDICATION", "DRAFT_GENERATION",
        "READER_RETENTION_AUDIT", "EDITORIAL_TRIM", "ORIGINALITY_AUDIT",
        "FACT_INTEGRITY_AUDIT", "STYLE_AUDIT", "FINAL_SYNTHESIS",
    )


def test_general_stability_contract_separates_fixed_process_from_adaptive_expression():
    contract = _json("config/EXECUTION_CONTRACT.json")
    stability = contract["general_writing_stability"]
    assert stability["applies_to"] == "ALL_FINANCIAL_WRITING_TASKS__NOT_ONE_ARTICLE_OR_TOPIC"
    assert stability["fixed_business_workflow"] == contract["workflow"]
    assert stability["topic_specific_research_modules"].startswith("CONDITIONAL_BY_USER_SCOPE")
    assert stability["expression_policy"].startswith("CONTENT_LED")
    assert stability["self_review_promotion_evidence"] is False
    assert stability["single_article_completion_is_system_completion"] is False
    assert len(NarrativeEngine) >= 8


def test_historical_cross_topic_samples_are_diagnostic_not_quality_promotion_cases():
    corpus = _json("evals/quality_regression.json")
    samples = corpus["diagnostic_samples"]
    assert len(samples) >= 4
    assert len({sample["topic_family"] for sample in samples}) >= 4

    for sample in samples:
        assert sample["assurance"] == "CHAT_SELF_REVIEW"
        assert sample["quality_evidence_status"] == "EMPTY"
        assert sample["promotion_eligible"] is False
        assert len(sample["artifact_bindings"]) >= 3
        assert all(binding["identity_type"] == "GIT_BLOB_SHA"
                   and binding["identity"]
                   for binding in sample["artifact_bindings"])

    readiness = evaluate_corpus_readiness(corpus)
    assert readiness.status == "NOT_READY"
    assert "at_least_two_complete_heldout_topic_families" in readiness.missing_requirements
    assert set(readiness.complete_case_ids) == {
        "offshore-wind-2026-10-10-real-user-rejection-01",
        "rutile-2026-10-06-cross-topic-heldout-01",
    }



def test_three_publishing_products_share_one_task_contract_but_keep_separate_outputs():
    portfolio = TaskContract(prompt="测试同一研究包下的三类财经内容产品")
    assert [item.value for item in portfolio.required_outputs] == [
        "AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX",
        "PLATFORM_INTERACTION_PACK_DOCX",
    ]

    acquisition = TaskContract(
        prompt="测试获客长文",
        distribution_mode=DistributionMode.ACQUISITION,
    )
    assert [item.value for item in acquisition.required_outputs] == [
        "AUDIT_DOCX", "FINANCE_BROAD_DOCX", "PLATFORM_INTERACTION_PACK_DOCX",
    ]

    deep = TaskContract(
        prompt="测试深度财经长文",
        distribution_mode=DistributionMode.FINANCE_DEEP,
    )
    assert [item.value for item in deep.required_outputs] == [
        "AUDIT_DOCX", "FINANCE_DEEP_DOCX",
    ]


def test_system_wide_editorial_obligations_are_fixed_but_content_led():
    contract = _json("config/EXECUTION_CONTRACT.json")
    stability = contract["general_writing_stability"]
    products = stability["publishing_portfolio"]["products"]
    assert {item["mode"] for item in products} == {
        "FINANCE_DEEP", "FINANCE_BROAD", "PLATFORM_INTERACTION",
    }
    obligations = stability["fixed_editorial_quality_obligations"]
    assert "SOURCE_PROVENANCE" in obligations["publication_source_privacy"]
    assert "EVIDENCE_BOUNDED" in obligations["company_comparison"]
    assert "SUBSTANTIVE_SECTION_LEAD" in obligations["section_transition"]
    assert "NO_NEW_FACTS" in obligations["interaction_copy"]
    assert stability["expression_policy"].startswith("CONTENT_LED")



def test_real_huangjiu_user_rejection_source_provenance_is_caught_as_regression():
    from financial_writing_agent.checks import scan_publication_source_leaks

    article = (
        ROOT / "workspaces/articles/huangjiu-high-end-channel-20261015/"
        "publication/FINANCE_DEEP.md"
    ).read_text(encoding="utf-8")
    findings = set(scan_publication_source_leaks(article))
    assert {
        "named_broker_report_framing",
        "named_broker_analyst_attribution",
        "research_report_attribution",
        "named_industry_research_attribution",
        "named_industry_actor_attribution",
    } <= findings


def test_source_provenance_patterns_cover_known_failure_forms_without_banning_company_facts():
    from financial_writing_agent.checks import scan_publication_source_leaks

    rejected_forms = [
        "方正证券10月12日发布的黄酒行业深度报告提出了一个观点。",
        "方正证券进一步指出，渠道利润空间正在收窄。",
        "研报给出的渠道逻辑很直接。",
        "中国酒业协会公开研究显示，行业规模约200亿元。",
        "中国酒业协会此前披露，2024年黄酒销售额约200亿元。",
        "公开资料显示，行业库存仍然偏高。",
    ]
    for sentence in rejected_forms:
        assert scan_publication_source_leaks(sentence), sentence

    ordinary_company_fact = "会稽山2026年上半年中高端黄酒销售收入5.95亿元，同比增长14.17%。"
    assert scan_publication_source_leaks(ordinary_company_fact) == []
