from pathlib import Path

from docx import Document

from financial_writing_agent.adapters.deterministic import DeliveryExecutor, MechanicalAuditExecutor, finalize_audit_artifact
from financial_writing_agent.models import ArtifactKind, DistributionMode, GateStatus, TaskContract, WritingState


def _risk():
    return (
        "本文基于公开信息进行行业与公司研究，仅用于财经信息交流，不构成投资建议或收益承诺。"
        "政策、需求、价格、订单、竞争格局、公司业绩及市场情绪均可能变化，请以最新公告为准并独立判断。"
    )


def _deep_payload():
    return {
        "title": "测试：利润与估值",
        "stock_names": ["国电南瑞"],
        "risk_disclaimer": _risk(),
        "skim_path_anchors": ["利润兑现", "订单增长", "估值重算"],
        "blocks": [
            {"kind": "lead", "text": "导读涉及国电南瑞，**利润兑现**开始进入财报。"},
            {"kind": "h1", "text": "订单为什么开始变成利润"},
            {"kind": "body", "text": "国电南瑞用于实体比较，同时**订单增长**推动**估值重算**。"},
        ],
    }


def _broad_payload():
    return {
        "title": "测试：为什么财经读者也该看",
        "stock_names": ["国电南瑞"],
        "risk_disclaimer": _risk(),
        "skim_path_anchors": ["需求变化", "订单增长", "利润弹性"],
        "blocks": [
            {"kind": "lead", "text": "**需求变化**正在穿过产业链。"},
            {"kind": "h1", "text": "为什么这件事和利润有关"},
            {"kind": "body", "text": "国电南瑞的**订单增长**最终要看**利润弹性**。"},
        ],
    }


def _draft():
    return {"finance_deep": _deep_payload(), "finance_broad": _broad_payload()}


def test_delivery_builds_dual_word_and_appends_risk_deterministically(tmp_path):
    state = WritingState(contract=TaskContract(prompt="写文章", distribution_mode=DistributionMode.DUAL))
    state.working["draft"] = _draft()
    state = DeliveryExecutor(root=tmp_path).execute(state)
    assert state.gates["delivery_output"].status == GateStatus.PASS
    assert Path(state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX].path).exists()
    assert Path(state.artifacts[ArtifactKind.FINANCE_BROAD_DOCX].path).exists()
    assert all(str(tmp_path) not in item for item in state.gates["delivery_output"].evidence)


def test_mechanical_audit_checks_bold_skim_anchors(tmp_path):
    state = WritingState(contract=TaskContract(prompt="写文章", distribution_mode=DistributionMode.DUAL))
    state.working["draft"] = _draft()
    state = DeliveryExecutor(root=tmp_path).execute(state)
    state = MechanicalAuditExecutor(require_render=False).execute(state)
    assert state.gates["mechanical_audit"].status == GateStatus.PASS, state.gates["mechanical_audit"].notes


def test_mechanical_audit_fails_when_required_word_artifact_is_missing(tmp_path):
    state = WritingState(contract=TaskContract(prompt="写文章", distribution_mode=DistributionMode.FINANCE_DEEP))
    state.working["draft"] = {"finance_deep": _deep_payload(), "finance_broad": None}
    state.working["output_dir"] = str(tmp_path)
    state = MechanicalAuditExecutor(require_render=False).execute(state)
    assert state.gates["mechanical_audit"].status == GateStatus.REVISE
    assert "required Word artifact mapping missing" in state.gates["mechanical_audit"].notes


def test_audit_artifact_is_visible_required_output_and_hides_runtime_paths(tmp_path):
    state = WritingState(contract=TaskContract(prompt="写文章", distribution_mode=DistributionMode.FINANCE_DEEP))
    state.working["output_dir"] = str(tmp_path)
    article_path = tmp_path / "FINANCE_DEEP.docx"
    article_path.write_bytes(b"stub")
    from financial_writing_agent.models import Artifact
    state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(
        kind=ArtifactKind.FINANCE_DEEP_DOCX,
        path=str(article_path),
        exists=True,
        sha256="abc123",
    )
    state.set_gate("research_output", GateStatus.PASS, [f"server path was {article_path}"])
    finalize_audit_artifact(state)
    audit_path = Path(state.artifacts[ArtifactKind.AUDIT_DOCX].path)
    assert audit_path.exists()
    text = "\n".join(p.text for p in Document(audit_path).paragraphs)
    assert str(tmp_path) not in text
    assert "FINANCE_DEEP.docx" in text
