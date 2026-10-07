from pathlib import Path

from docx import Document

from financial_writing_agent.adapters.deterministic import DeliveryExecutor, MechanicalAuditExecutor, finalize_audit_artifact
from financial_writing_agent.checks import sha256_file
from financial_writing_agent.models import Artifact, ArtifactKind, DeliveryChannel, DistributionMode, GateStatus, TaskContract, WritingState


def _risk():
    return (
        "本文基于公开信息进行行业与公司研究，仅用于财经信息交流，不构成投资建议或收益承诺。"
        "政策、需求、价格、订单、竞争格局、公司业绩及市场情绪均可能变化，请以最新公告为准并独立判断。"
    )


def _draft():
    return {
        "finance_deep": {
            "title": "测试：利润与估值",
            "stock_names": ["国电南瑞"],
            "risk_disclaimer": _risk(),
            "blocks": [
                {"kind": "lead", "text": "导读涉及国电南瑞。"},
                {"kind": "h1", "text": "核心矛盾"},
                {"kind": "body", "text": "国电南瑞用于验证自动加粗。"},
            ],
        },
        "finance_broad": {
            "title": "测试：为什么财经读者也该看",
            "stock_names": ["国电南瑞"],
            "risk_disclaimer": _risk(),
            "blocks": [
                {"kind": "lead", "text": "导读。"},
                {"kind": "h1", "text": "问题"},
                {"kind": "body", "text": "国电南瑞。"},
            ],
        },
    }


def test_delivery_builds_dual_word_and_appends_risk_deterministically(tmp_path):
    state = WritingState(contract=TaskContract(prompt="写文章", distribution_mode=DistributionMode.DUAL))
    state.working["draft"] = _draft()
    state = DeliveryExecutor(root=tmp_path).execute(state)
    assert state.gates["delivery_output"].status == GateStatus.PASS
    assert Path(state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX].path).exists()
    assert Path(state.artifacts[ArtifactKind.FINANCE_BROAD_DOCX].path).exists()


def test_chat_delivery_makes_mechanical_audit_na(tmp_path):
    c = TaskContract(prompt="聊天框发正文", delivery_channel=DeliveryChannel.CHAT_TEXT, distribution_mode=DistributionMode.FINANCE_DEEP)
    state = WritingState(contract=c)
    state.working["draft"] = _draft()
    state = DeliveryExecutor(root=tmp_path).execute(state)
    state = MechanicalAuditExecutor(require_render=False).execute(state)
    assert state.gates["mechanical_audit"].status == GateStatus.N_A


def test_audit_artifact_contains_acceptance_evidence_and_safe_artifact_identity(tmp_path):
    state = WritingState(contract=TaskContract(prompt="写文章", distribution_mode=DistributionMode.FINANCE_DEEP))
    state.working["output_dir"] = str(tmp_path)
    final_path = tmp_path / "FINANCE_DEEP.docx"
    final_path.write_bytes(b"final-content")
    state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(
        kind=ArtifactKind.FINANCE_DEEP_DOCX,
        path=str(final_path),
        exists=True,
        sha256=sha256_file(final_path),
    )
    state.working["research"] = {
        "source_boundary": "公开一手来源 + 独立核验",
        "coverage": {"coverage_status": "SATURATED", "sweeps_completed": 2},
        "cognition": {"prior_knowledge_refs": ["stockbase-readonly"]},
        "evidence_ledger": [
            {
                "claim": "核心事实",
                "source": "原始公告",
                "core_safe": True,
                "verification_status": "INDEPENDENTLY_CROSS_CHECKED",
            }
        ],
        "review_queue": [],
        "failed_tools_or_sources": [],
        "knowledge_writeback_candidates": ["产业关系"],
    }
    state.working["acceptance_contract"] = {
        "finance_deep": {
            "selected_title": "测试：利润与估值",
            "selected_structure_name": "结构A",
            "expected_h1_count": 1,
            "expected_section_functions": ["核心矛盾"],
            "lead_required": 1,
            "side_focus_statement": "本篇聚焦利润兑现",
            "company_selection_basis": ["产业传导位置"],
        },
        "required_outputs": ["AUDIT_DOCX", "FINANCE_DEEP_DOCX"],
        "delivery_channel": "WORD_FILE_ONLY",
        "visuals_enabled": False,
    }
    state.working["final_audit"] = {
        "acceptance_evidence": ["FINANCE_DEEP title/lead/H1/company basis checked on final content"],
        "reviewed_render_pages": [],
    }
    state.working["knowledge_writeback_refs"] = ["articlebase://receipt-1"]
    state.set_gate("acceptance_contract", GateStatus.PASS, ["frozen"])
    state.set_gate("final_audit", GateStatus.PASS, ["red team"])
    state.set_gate("knowledge_sync", GateStatus.PASS, ["articlebase://receipt-1"])

    finalize_audit_artifact(state)
    audit_path = Path(state.artifacts[ArtifactKind.AUDIT_DOCX].path)
    assert audit_path.exists()
    text = "\n".join(p.text for p in Document(audit_path).paragraphs)
    assert "Writing Acceptance Contract" in text
    assert "Final Acceptance Evidence" in text
    assert "recorded_sha_match=True" in text
    assert "FINANCE_DEEP_DOCX: file=FINANCE_DEEP.docx" in text
    assert str(tmp_path) not in text
