"""Financial-only reproducible red-team replay, pinned to 2026-11-12.

This is NOT a fact-check, editorial review, user acceptance or external-service
test. It exercises actual production module functions against malformed-but-
plausible research and delivery inputs, and reports current assurance gaps.

Run from repo root:
    python scripts/real_financial_workflow_redteam.py
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from financial_writing_agent import delivery_pipeline
from financial_writing_agent.claim_trace import SourceTraceError, verify_publication_source_trace
from financial_writing_agent.current_admission import validate_state
from financial_writing_agent.delivery_pipeline import (
    CanonicalDeliveryError, _issue_build_receipt,
    finalize_delivery_evidence, validate_delivery_evidence,
)
from financial_writing_agent.models import ArtifactKind
from financial_writing_agent.private_research import (
    REQUIRED_MODULES, validate_private_research_brief,
)
from financial_writing_agent.current_research_sources import (
    CurrentResearchEvidenceError, verify_current_research_sources,
)
from financial_writing_agent.schemas import AuditProvenance
from financial_writing_agent.standalone_runtime import (
    FinancialAdmissionError, _blob_sha, admit_article_action, observe_article,
    _verify_requirement_satisfaction_sources,
)
from financial_writing_agent.story_quality import (
    AuditStatus, GateAudit, OriginalityEvidence, ProductMode,
    PublicationFitness, TextEvidence,
)
from financial_writing_agent.checks import check_deep_company_grounding

ROOT = Path(__file__).resolve().parents[1]
TASK = "cross-border-ecommerce-20261016-v3"
DATE = date(2026, 11, 12)


def run() -> dict:
    observations = {}
    state_path = ROOT / "workspaces" / "articles" / TASK / "STATE.json"
    raw_state = state_path.read_bytes()
    state = json.loads(raw_state)
    validate_state(state)
    # A complete-looking set of Word resources must not turn an unfinished
    # article into a visible, user-deliverable FINAL_AUDIT result.
    from financial_writing_agent.delivery_availability import (
        DeliveryAvailabilityError, build_visible_delivery_receipt,
    )
    for blocked_status in ("IN_PROGRESS", "BLOCKED"):
        fake_ready = dict(state)
        fake_ready["status"] = blocked_status
        fake_ready["delivery_artifacts"] = {
            kind: {"sha256": "a" * 64} for kind in state["required_outputs"]
        }
        try:
            build_visible_delivery_receipt(
                fake_ready, resources=[], resource_verifier=lambda _: True,
            )
        except DeliveryAvailabilityError as exc:
            assert "VISIBLE_DELIVERY_REQUIRES_TERMINAL_ARTICLE_STATE" in str(exc)
        else:
            raise AssertionError("nonterminal article was certified for visible delivery")
    observations["00_live_delivery_state_gate"] = (
        "PASS__NONTERMINAL_AND_BLOCKED_WORD_RESOURCE_REPLAY_REJECTED"
    )
    observations["01_actual_article_state"] = {
        "stage": state["current_stage"],
        "status": state["status"],
        "quality_evidence_items": len(state["quality_evidence"]),
        "stage_artifact_items": len(state["stage_artifacts"]),
        "delivered_output_items": len(state["delivery_artifacts"]),
        "owner_required_outputs": len(state["required_outputs"]),
    }

    def state_reader(path):
        if path == f"workspaces/articles/{TASK}/STATE.json":
            return {"content": raw_state, "state": state, "blob_sha": _blob_sha(raw_state)}
        return None

    observed = observe_article(TASK, state_reader=state_reader)
    assert observed["stage"] == "RESEARCH"
    assert observed["independent_editorial_quality_verified"] is False
    observations["02_standalone_read_only_owner"] = {
        "stage": observed["stage"],
        "observed_git_blob_sha": observed["state_blob_sha"],
        "editorial_verified": observed["independent_editorial_quality_verified"],
    }
    # Direct, unauthenticated mutation must be denied even with a valid-looking
    # task ID and source blob; do not modify the repository or task state.
    proposal = {
        "schema_version": "1.0", "domain_id": "financial_writing",
        "action_id": "audit:denied", "task_id": TASK,
        "operation": "ADVANCE_STAGE",
        "expected_state_blob_sha": _blob_sha(raw_state),
        "parameters": {},
    }
    try:
        admit_article_action(
            proposal, state_reader=state_reader,
            cas_writer=lambda *_: {"blob_sha": "0" * 40},
            authorization_verifier=None,
        )
        observations["03_unauthenticated_mutation"] = "UNEXPECTEDLY_ACCEPTED"
    except FinancialAdmissionError as exc:
        observations["03_unauthenticated_mutation"] = f"DENIED:{exc}"

    historical_path = (
        ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v2"
        / "research/PRIVATE_RESEARCH_BRIEF_1_1_20261016.json"
    )
    old_brief = json.loads(historical_path.read_text(encoding="utf-8"))
    accepted_old = validate_private_research_brief(
        old_brief, expected_contract_version="1.1"
    )
    old_date = date.fromisoformat(accepted_old["as_of"][:10])
    try:
        verify_current_research_sources(
            accepted_old,
            source_reader=lambda _: None,
            as_of=datetime(2026, 11, 12, tzinfo=timezone.utc),
        )
        old_runtime_result = "ACCEPTED"
    except CurrentResearchEvidenceError as exc:
        old_runtime_result = f"BLOCKED:{exc}"
    observations["04_historical_research_freshness"] = {
        "old_as_of": old_date.isoformat(),
        "age_days_at_replay": (DATE - old_date).days,
        "structure_accepted_as_complete": accepted_old["coverage_state"] == "COMPLETE",
        "current_admission_result": old_runtime_result,
        "live_news_or_policy_rechecked_by_this_validator": False,
    }

    placeholder = {
        "contract_version": "1.1",
        "as_of": DATE.isoformat(),
        "coverage_state": "COMPLETE",
        "modules": {
            name: {
                "status": "APPLICABLE",
                "summary": f"{name} done, source may not actually exist",
                "evidence_refs": ["audit-example://nonexistent"],
            }
            for name in REQUIRED_MODULES
        },
        "unresolved_gaps": [],
    }
    try:
        fake = validate_private_research_brief(placeholder, expected_contract_version="1.1")
        try:
            verify_current_research_sources(
                fake, source_reader=lambda _: None,
                as_of=datetime(2026, 11, 12, tzinfo=timezone.utc),
            )
            live_result = "ACCEPTED"
        except CurrentResearchEvidenceError as exc:
            live_result = f"BLOCKED:{exc}"
        observations["05_fabricated_brief_schema"] = {
            "result": "STRUCTURAL_ACCEPTANCE",
            "current_admission_result": live_result,
            "module_count": len(fake["modules"]),
            "source_provider_bytes_read": 0,
        }
    except ValueError as exc:
        observations["05_fabricated_brief_schema"] = {"result": f"BLOCKED:{exc}"}

    # Same company, reporting period and figure; business direction is inverted.
    # This is intentionally an invalid financial claim.
    source_text = "甲公司2026年营业收入同比下降20%，主要由于订单减少。"
    public_text = "甲公司2026年营业收入同比增长20%，主要由于订单增加。"
    article = SimpleNamespace(
        title="收入趋势判断",
        blocks=[SimpleNamespace(kind="body", text=public_text)],
    )
    binding = [{
        "claim_id": "opposite-direction",
        "block_index": 0,
        "claim_excerpt": "甲公司2026年营业收入同比增长20%",
        "source_ref": "audit-example://issuer-financial",
        "source_excerpt": source_text,
    }]
    try:
        trace = verify_publication_source_trace(
            article, binding, article_task_id=TASK,
            source_reader=lambda _: {
                "text": source_text,
                "sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            },
        )
        observations["06_opposite_direction_source_claim"] = {
            "result": "STRUCTURAL_TRACE_ACCEPTED",
            "semantic_fact_entailment_verified": trace["semantic_fact_entailment_verified"],
            "primary_source_authority_verified": trace["primary_source_authority_verified"],
        }
    except SourceTraceError as exc:
        observations["06_opposite_direction_source_claim"] = {"result": f"BLOCKED:{exc}"}

    names = (
        "FACT_INTEGRITY", "RETENTION", "COMPANY_GROUNDING",
        "STRUCTURE_NUMBERING", "ORIGINALITY", "AUTHORIAL_STYLE",
        "COMPLIANCE", "PAYOFF",
    )
    gates = [
        GateAudit(
            gate=name, status=AuditStatus.PASS,
            evidence=[TextEvidence(
                location="unverified-paragraph",
                excerpt="这是没有实际核实的示例文字",
                finding="自评未发现问题", severity="INFO",
            )],
            checked_items=["self-asserted-check"],
        )
        for name in names
    ]
    base = {
        "product_mode": ProductMode.FINANCE_DEEP,
        "gates": gates,
        "originality_checks": [OriginalityEvidence(
            compared_source_ref="audit-example://not-read",
            checked_phrase_or_passage="这是一段示例文字",
            result="NO_MATERIAL_OVERLAP",
            notes="没有真实相似度查验",
        )],
        "final_status": AuditStatus.PASS,
    }
    try:
        self_fitness = PublicationFitness(
            **base, assurance="CHAT_SELF_REVIEW",
            audit_provenance=AuditProvenance(assurance="CHAT_SELF_REVIEW"),
        )
        observations["07_self_scored_editorial_fitness"] = {
            "self_pass_admitted": self_fitness.final_status.value == "PASS",
            "assurance": self_fitness.assurance,
            "independent_reader_or_fact_evidence": False,
        }
    except ValueError as exc:
        observations["07_self_scored_editorial_fitness"] = {
            "self_pass_admitted": False,
            "result": f"BLOCKED:{exc}",
            "independent_reader_or_fact_evidence": False,
        }
    try:
        PublicationFitness(
            **base, assurance="INDEPENDENT_EXECUTOR",
            audit_provenance=AuditProvenance(
                assurance="INDEPENDENT_EXECUTOR", reviewer_identity="external",
                author_identity="author", execution_ref="audit-example://review",
            ),
        )
        observations["08_external_editor_assurance"] = "ACCEPTED"
    except ValueError as exc:
        observations["08_external_editor_assurance"] = f"REJECTED:{str(exc)[:180]}"

    # A deliberately synthetic internal builder receipt with no DOCX file.
    # This probes generic (non-task-bound) evidence path only. Do not mistake
    # private _issue_build_receipt access for an untrusted public API.
    fake_build = _issue_build_receipt({
        "schema_version": "1.1",
        "canonical_delivery_path": "financial_writing_agent.delivery_pipeline",
        "artifact_kind": ArtifactKind.AUDIT_DOCX.value,
        "file_name": "intentionally-nonexistent-audit.docx",
        "sha256": "a" * 64,
        "mechanical_qa": "PASS",
        "constraint_qa": "PASS",
    })
    try:
        final = finalize_delivery_evidence(
            fake_build,
            source_ref=f"workspaces/articles/{TASK}/reviews/nonexistent.json",
            source_identity="audit-example://no-real-blob",
            render_qa="PASS", visual_qa="PASS",
        )
        validated = {
            "kind": ArtifactKind.AUDIT_DOCX.value,
            "sha256": "a" * 64,
            **final,
        }
        validate_delivery_evidence(validated)
        observations["09_generic_word_without_binary"] = {
            "result": "INTERNAL_GENERIC_RECEIPT_ACCEPTED",
            "file_exists": False,
            "render_page_receipt_exists": "render_inspection_receipt" in final["delivery_evidence"],
            "external_resource_verifier_invoked": False,
        }
    except CanonicalDeliveryError as exc:
        observations["09_generic_word_without_binary"] = {"result": f"BLOCKED:{exc}"}


    # The real v3 owner requires the *full retained* universe. The gate cannot
    # establish whether the research provider silently omitted 171 names:
    # it only checks internal consistency of whatever list it was handed.
    from financial_writing_agent.document import ArticleDocument, Block
    from financial_writing_agent.task_publication import (
        TaskPublicationError, verify_task_publication_scope,
    )
    fake_research = SimpleNamespace(
        universe=[
            SimpleNamespace(name="甲公司", materiality="MATERIAL", value_chain_class="跨境卖家"),
            SimpleNamespace(name="乙公司", materiality="MATERIAL", value_chain_class="跨境卖家"),
            SimpleNamespace(name="丙公司", materiality="REFERENCE_ONLY", value_chain_class="营销"),
        ],
        company_decision_map=object(),
        universe_coverage=SimpleNamespace(
            status="COMPLETE",
            classes=[
                SimpleNamespace(included_companies=["甲公司", "乙公司"]),
                SimpleNamespace(included_companies=["丙公司"]),
            ],
        ),
    )
    fake_article = ArticleDocument(
        title="三家公司不能代表174家上市公司",
        stock_names=["甲公司", "乙公司", "丙公司"],
        blocks=[
            Block(kind="h1", text="一、两种经营兑现"),
            Block(kind="body", text="甲公司收入兑现强于乙公司；乙公司库存成本更高，现金回流更慢。"),
            Block(kind="body", text="丙公司只是间接概念标签，缺乏直接营收兑现证据。"),
        ],
    )
    try:
        narrow = verify_task_publication_scope(state, fake_article, fake_research)
        observations["10_three_company_universe_as_complete"] = {
            "result": "STRUCTURAL_SCOPE_ACCEPTED",
            "claimed_complete_count": narrow["company_names_checked"],
            "historical_retained_universe_count": 174,
            "verified_market_completeness": False,
        }
    except TaskPublicationError as exc:
        observations["10_three_company_universe_as_complete"] = {"result": f"BLOCKED:{exc}"}

    # Requirement-satisfaction evidence strings alone do not prove source
    # availability or factual sufficiency. This remains protected by human and
    # source checks outside this schema.
    from financial_writing_agent.current_admission import _normalize_requirement_satisfaction
    try:
        satisfied = _normalize_requirement_satisfaction(
            state, "RESEARCH", [{
                "requirement_id": "full_universe_research_pool",
                "result": "SATISFIED",
                "evidence_refs": ["audit-example://nonexistent-company-universe"],
                "notes": "no issuer research was actually read",
            }],
        )
        try:
            readback = _verify_requirement_satisfaction_sources(
                satisfied, {"snapshots": []},
            )
            source_readback_result = "ACCEPTED"
        except FinancialAdmissionError as source_exc:
            readback = None
            source_readback_result = f"BLOCKED:{source_exc}"
        observations["11_unsupported_task_satisfaction"] = {
            "result": "STRUCTURAL_SATISFACTION_ACCEPTED",
            "source_readback_result": source_readback_result,
            "record_count": len(satisfied),
            "provider_sources_verified": 0,
            "semantic_support_verified": bool(readback and readback["semantic_support_verified"]),
        }
    except ValueError as exc:
        observations["11_unsupported_task_satisfaction"] = {"result": f"BLOCKED:{exc}"}


    # Real retained source CSV has two company names padded with internal spaces.
    # The historical Deep visibly names the same companies without the spaces.
    csv_path = (
        ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v2"
        / "research/UNIVERSE_EASTMONEY_BK1115_20261016.csv"
    )
    old_draft_path = (
        ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v2"
        / "stages/DRAFT_V2_20261016.md"
    )
    rows = [
        line.split(",", 1)
        for line in csv_path.read_text(encoding="utf-8").splitlines()[1:]
        if line.strip()
    ]
    assert len(rows) == 170
    old_draft = old_draft_path.read_text(encoding="utf-8")
    raw_missing = [{"ticker": code, "csv_name": name} for code, name in rows if name not in old_draft]
    normalized_missing = [
        {"ticker": code, "normalized_name": "".join(name.split())}
        for code, name in rows if "".join(name.split()) not in old_draft
    ]
    observations["12_real_csv_to_draft_name_identity"] = {
        "csv_company_rows": len(rows),
        "csv_unique_tickers": len({code for code, _ in rows}),
        "raw_name_mismatch_count": len(raw_missing),
        "raw_name_mismatches": raw_missing,
        "normalized_name_missing_count": len(normalized_missing),
    }

    # Source vendors sometimes insert internal spaces in the display name.
    # The identity-aware grounding check must compare canonical issuer names.
    raw_name_research = SimpleNamespace(
        universe=[
            SimpleNamespace(name="生 意 宝", materiality="MATERIAL"),
            SimpleNamespace(name="焦点科技", materiality="MATERIAL"),
        ],
        company_decision_map=object(),
    )
    scoped_article = ArticleDocument(
        title="B2B业务的财务比较",
        stock_names=["生意宝", "焦点科技"],
        blocks=[
            Block(kind="h1", text="一、贸易获客结构"),
            Block(kind="body", text="焦点科技的交易收入兑现强于生意宝；生意宝成本更高，利润兑现较慢。"),
            Block(kind="h1", text="后续验证"),
            Block(kind="body", text="后续继续核对生意宝和焦点科技的订单、回款及利润变化。"),
        ],
    )
    try:
        grounding_errors = check_deep_company_grounding(scoped_article, raw_name_research)
        raw_name_result = "ACCEPTED" if not grounding_errors else f"REJECTED:{grounding_errors}"
    except Exception as exc:
        raw_name_result = f"REJECTED:{type(exc).__name__}:{exc}"
    observations["13_name_spacing_false_negative"] = {
        "raw_csv_name_result": raw_name_result,
        "normalized_same_company_result": "NOT_NEEDED__CANONICALIZED_AT_CHECK_BOUNDARY",
        "semantic_company_identity_same": True,
    }

    reproduced_gaps = []
    for key, label, expected in (
        ("06_opposite_direction_source_claim", "CONTRADICTORY_FINANCIAL_CLAIM", "STRUCTURAL_TRACE_ACCEPTED"),
        ("09_generic_word_without_binary", "GENERIC_WORD_RECEIPT_WITHOUT_BINARY", "INTERNAL_GENERIC_RECEIPT_ACCEPTED"),
        ("10_three_company_universe_as_complete", "UNIVERSE_TRUNCATION_3_VS_174", "STRUCTURAL_SCOPE_ACCEPTED"),
    ):
        value = observations.get(key, {})
        if isinstance(value, dict) and value.get("result") == expected:
            reproduced_gaps.append(label)
    if observations.get("05_fabricated_brief_schema", {}).get("current_admission_result") == "ACCEPTED":
        reproduced_gaps.append("RESEARCH_FAKE_SOURCE_REFS")
    if observations.get("11_unsupported_task_satisfaction", {}).get("source_readback_result") == "ACCEPTED":
        reproduced_gaps.append("UNREAD_REQUIREMENT_EVIDENCE")
    if observations["07_self_scored_editorial_fitness"]["self_pass_admitted"]:
        reproduced_gaps.append("SELF_REVIEW_PASS_WITHOUT_INDEPENDENT_JUDGMENT")
    if observations["12_real_csv_to_draft_name_identity"]["normalized_name_missing_count"]:
        reproduced_gaps.append("CSV_NAME_CANONICALIZATION")
    if observations["13_name_spacing_false_negative"]["raw_csv_name_result"] != "ACCEPTED":
        reproduced_gaps.append("COMPANY_IDENTITY_NORMALIZATION_FAILURE")
    observations["00_business_assurance_conclusion"] = {
        "product_readiness": "NOT_READY",
        "reason": "LIVE_V3_0_OF_4_DELIVERABLES__INDEPENDENT_EDITORIAL_NOT_VERIFIED",
        "reproduced_weak_assurance_paths": sorted(reproduced_gaps),
        "successful_safety_controls": [
            "UNAUTHENTICATED_STATE_CHANGE_DENIED",
            "READ_ONLY_OBSERVATION_NO_INDEPENDENT_CERTIFICATION",
            "STALE_RESEARCH_BLOCKED_AT_CURRENT_ADMISSION",
            "FAKE_SOURCE_REFS_BLOCKED_BY_PROVIDER_READBACK",
            "UNREAD_REQUIREMENT_REFS_BLOCKED",
            "SAME_SESSION_EDITORIAL_SELF_PASS_BLOCKED",
            "WORD_DELIVERY_WITHOUT_RENDER_RECEIPT_BLOCKED",
            "COMPANY_IDENTITY_NORMALIZED_AT_GROUNDING_BOUNDARY",
        ],
        "open_assurance_limits": [
            "RESEARCH_SOURCE_AUTHORITY_AND_FACT_ENTAILMENT_NOT_VERIFIED",
            "REQUIREMENT_SEMANTIC_SUPPORT_NOT_CERTIFIED_BY_SOURCE_READBACK",
            "PAGE_REVIEW_INDEPENDENCE_NOT_ESTABLISHED",
            "REAL_ARTICLE_EDITORIAL_AND_READER_OUTCOME_NOT_VERIFIED",
        ],
        "ci_success_means": "NEGATIVE_REPLAY_EXECUTED__NOT_PUBLICATION_ACCEPTANCE",
    }
    return observations


def main():
    report = run()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    assert report["01_actual_article_state"]["stage"] == "RESEARCH"
    assert report["01_actual_article_state"]["delivered_output_items"] == 0
    assert report["03_unauthenticated_mutation"].startswith("DENIED:")
    # Red-team deficiencies are reported, NOT described as business PASS.


if __name__ == "__main__":
    main()
