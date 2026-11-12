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
from datetime import date
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
from financial_writing_agent.schemas import AuditProvenance
from financial_writing_agent.standalone_runtime import (
    FinancialAdmissionError, _blob_sha, admit_article_action, observe_article,
)
from financial_writing_agent.story_quality import (
    AuditStatus, GateAudit, OriginalityEvidence, ProductMode,
    PublicationFitness, TextEvidence,
)

ROOT = Path(__file__).resolve().parents[1]
TASK = "cross-border-ecommerce-20261016-v3"
DATE = date(2026, 11, 12)


def run() -> dict:
    observations = {}
    state_path = ROOT / "workspaces" / "articles" / TASK / "STATE.json"
    raw_state = state_path.read_bytes()
    state = json.loads(raw_state)
    validate_state(state)
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
    observations["04_historical_research_freshness"] = {
        "old_as_of": old_date.isoformat(),
        "age_days_at_replay": (DATE - old_date).days,
        "structure_accepted_as_complete": accepted_old["coverage_state"] == "COMPLETE",
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
        observations["05_fabricated_brief_schema"] = {
            "result": "STRUCTURAL_ACCEPTANCE",
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
    self_fitness = PublicationFitness(
        **base, assurance="CHAT_SELF_REVIEW",
        audit_provenance=AuditProvenance(assurance="CHAT_SELF_REVIEW"),
    )
    observations["07_self_scored_editorial_fitness"] = {
        "self_pass_admitted": self_fitness.final_status.value == "PASS",
        "assurance": self_fitness.assurance,
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
