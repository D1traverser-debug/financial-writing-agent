"""Render and revalidate all four actual Word product types with synthetic text.

This is a BINARY/FORMATTING E2E CI smoke, NOT current issuer research, an
accepted financial article, authenticated user delivery or a blind editorial
review. It deliberately keeps the current real v3 article state untouched.
"""
from __future__ import annotations

import hashlib
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from financial_writing_agent.delivery_pipeline import (
    build_verified_article_docx, build_verified_audit_docx,
    build_verified_interaction_pack_docx, build_verified_private_research_docx,
    finalize_delivery_evidence, render_word_and_review_pages,
    validate_delivery_evidence,
)
from financial_writing_agent.document import ArticleDocument, AuditLine, Block
from financial_writing_agent.models import ArtifactKind
from financial_writing_agent.private_research import REQUIRED_MODULES
from financial_writing_agent.schemas import InteractionPost, PlatformInteractionPack


def _article(deep: bool) -> ArticleDocument:
    if deep:
        return ArticleDocument(
            title="合同增长为什么不一定变成利润：两家企业的履约差异",
            stock_names=["甲公司", "乙公司"],
            blocks=[
                Block(kind="lead", text="**成本如何进入现金流**，才是理解两家公司区别的起点。"),
                Block(kind="h1", text="经营规模不是利润兑现"),
                Block(kind="body", text="甲公司的订单验证链更短；乙公司仍需要等待履约完成，这只是合成示例，并非真实财报结论。"),
                Block(kind="h1", text="风险提示与免责声明"),
                Block(kind="body", text="公司业务、政策和市场均可能变化，本文仅作测试，不构成投资建议。"),
            ],
        )
    return ArticleDocument(
        title="同样接到订单，企业为什么可能赚得不同？",
        stock_names=["甲公司", "乙公司"],
        blocks=[
            Block(kind="lead", text="一个不容易察觉的差别是：**收到订单不等于收到现金**。"),
            Block(kind="h1", text="读者应该先问什么"),
            Block(kind="body", text="甲公司和乙公司都能展示订单，但在这个虚构的教学例子里，履约时间和回款条件不同。"),
            Block(kind="h1", text="风险提示与免责声明"),
            Block(kind="body", text="示例不代表任何公司的真实经营事实，不构成投资建议。"),
        ],
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        built = {}
        for kind, mode in (
            (ArtifactKind.FINANCE_DEEP_DOCX, True),
            (ArtifactKind.FINANCE_BROAD_DOCX, False),
        ):
            article = _article(mode)
            path = root / f"{kind.value.lower()}.docx"
            anchor = "成本如何进入现金流" if mode else "收到订单不等于收到现金"
            built[kind] = (
                path,
                build_verified_article_docx(
                    article, path, artifact_kind=kind,
                    required_bold_anchors=[anchor],
                    require_risk_disclaimer=True,
                ),
            )
        pack = PlatformInteractionPack(
            topic="四类财经产品的独立 Word 渲染测试",
            evidence_boundary="合成数据仅用于检验可见格式；不表示真实行业与公司核验通过。",
            posts=[
                InteractionPost(
                    platform_family="WECHAT_IMAGE_TEXT",
                    hook="订单落地不等于利润落地。",
                    body="公司差异可能来自履约进度和回款条件，案例均为虚构。",
                    interaction_prompt="你会先看订单还是现金流？",
                    stock_names=["甲公司", "乙公司"],
                ),
                InteractionPost(
                    platform_family="TOUTIAO_MICRO",
                    hook="财务确认与现金到账可能不同步。",
                    body="应查证口径、时间及利润兑现，而非只看某个数字。",
                    interaction_prompt="哪一个指标更容易误读？",
                ),
                InteractionPost(
                    platform_family="BAIJIAHAO_DYNAMIC",
                    hook="两个案例不应只按业务标签分组。",
                    body="业务经济性需要对照风险和实际结果。",
                    interaction_prompt="你希望先补充哪个证据？",
                ),
            ],
        )
        kind = ArtifactKind.PLATFORM_INTERACTION_PACK_DOCX
        path = root / "platform_interaction_pack.docx"
        built[kind] = (path, build_verified_interaction_pack_docx(pack, path))
        kind = ArtifactKind.AUDIT_DOCX
        path = root / "article_audit.docx"
        built[kind] = (
            path,
            build_verified_audit_docx(
                title="模拟数据四产品结构审计",
                lines=[
                    AuditLine(area="工程 Word 渲染", status="TEST_ONLY",
                              evidence="真实 DOCX→PDF→PNG 字节回读", notes="不代表独立事实审校"),
                    AuditLine(area="读者质量", status="NOT_VERIFIED",
                              evidence="没有真实读者盲评", notes="不能伪装为 PASS"),
                ],
                artifacts=[kind.value for kind in (
                    ArtifactKind.FINANCE_DEEP_DOCX,
                    ArtifactKind.FINANCE_BROAD_DOCX,
                    ArtifactKind.PLATFORM_INTERACTION_PACK_DOCX,
                    ArtifactKind.AUDIT_DOCX,
                )],
                output=path,
            ),
        )
        assert len(built) == 4
        visible = []
        for kind, (path, receipt) in built.items():
            assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == receipt["sha256"]
            inspected = render_word_and_review_pages(
                receipt,
                docx_path=path,
                render_dir=root / f"rendered_{kind.value}",
                visual_reviewer=lambda page: {
                    "status": "PASS",
                    "review_ref": f"ci:byte-inspected/{kind.value}/{page['page_sha256']}",
                },
            )
            final = finalize_delivery_evidence(
                receipt,
                source_ref=f"workspaces/articles/ci-synthetic/source/{kind.value}.json",
                source_identity="ci:synthetic-source",
                render_qa="PASS", visual_qa="PASS",
                render_inspection_receipt=inspected,
            )
            validate_delivery_evidence({
                "kind": kind.value, "sha256": receipt["sha256"], **final
            })
            assert final["delivery_evidence"]["render_inspection_receipt"]["rendered_page_count"] >= 1
            visible.append(kind.value)
        assert len(set(visible)) == 4
        print("PASS: all four real Word product binaries opened, rendered and signature/page hash checked; synthetic ONLY, editorial/product readiness NOT VERIFIED")


if __name__ == "__main__":
    main()
