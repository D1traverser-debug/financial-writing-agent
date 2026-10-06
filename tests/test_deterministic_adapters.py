from pathlib import Path

from financial_writing_agent.adapters.deterministic import DeliveryExecutor, MechanicalAuditExecutor, finalize_audit_artifact
from financial_writing_agent.models import ArtifactKind, DeliveryChannel, DistributionMode, GateStatus, TaskContract, WritingState


def _draft():
    return {
        "finance_deep": {
            "title": "测试：利润与估值",
            "stock_names": ["国电南瑞"],
            "blocks": [
                {"kind": "lead", "text": "导读涉及国电南瑞。"},
                {"kind": "h1", "text": "一、核心矛盾"},
                {"kind": "body", "text": "国电南瑞用于验证自动加粗。"},
                {"kind": "h1", "text": "二、风险提示与免责声明"},
                {"kind": "body", "text": "本文仅作信息研究，不构成投资建议。"},
            ],
        },
        "finance_broad": {
            "title": "测试：为什么财经读者也该看",
            "stock_names": ["国电南瑞"],
            "blocks": [
                {"kind": "lead", "text": "导读。"},
                {"kind": "h1", "text": "一、问题"},
                {"kind": "body", "text": "国电南瑞。"},
                {"kind": "h1", "text": "二、风险提示与免责声明"},
                {"kind": "body", "text": "本文仅作信息研究，不构成投资建议。"},
            ],
        },
    }


def test_delivery_builds_dual_word(tmp_path):
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


def test_audit_artifact_is_visible_required_output(tmp_path):
    state = WritingState(contract=TaskContract(prompt="写文章", distribution_mode=DistributionMode.FINANCE_DEEP))
    state.working["output_dir"] = str(tmp_path)
    state.set_gate("research_output", GateStatus.PASS, ["ledger"])
    finalize_audit_artifact(state)
    assert Path(state.artifacts[ArtifactKind.AUDIT_DOCX].path).exists()
