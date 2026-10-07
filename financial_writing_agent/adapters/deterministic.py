from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ..checks import check_docx, load_policy, sha256_file
from ..document import ArticleDocument, AuditLine, Block, DocumentImage, build_article_docx, build_audit_docx
from ..models import Artifact, ArtifactKind, ContentMode, DeliveryChannel, DistributionMode, GateStatus, WritingState
from ..rendering import render_docx_pages
from ..resources import load_packaged_policy
from ..schemas import DraftPackage, ResolvedVisualPackage


class DeliveryExecutor:
    def __init__(self, *, root: str | Path = "runs", policy_path: str | Path | None = None):
        self.root = Path(root)
        self.policy = load_policy(policy_path) if policy_path else load_packaged_policy()

    @staticmethod
    def _article(payload) -> ArticleDocument:
        blocks = [Block(kind=b.kind, text=b.text) for b in payload.blocks]
        blocks.extend([
            Block(kind="h1", text="风险提示与免责声明"),
            Block(kind="body", text=payload.risk_disclaimer),
        ])
        return ArticleDocument(title=payload.title, stock_names=payload.stock_names, blocks=blocks)

    @staticmethod
    def _sticker_article(payload) -> ArticleDocument:
        blocks = [Block(kind="body", text=payload.body)]
        if payload.interaction_prompt.strip():
            blocks.append(Block(kind="body", text=payload.interaction_prompt.strip()))
        blocks.extend([
            Block(kind="h1", text="风险提示与免责声明"),
            Block(kind="body", text=payload.risk_disclaimer),
        ])
        return ArticleDocument(title=payload.title, stock_names=payload.stock_names, blocks=blocks)

    @staticmethod
    def _images(package: ResolvedVisualPackage | None, mode: str) -> list[DocumentImage]:
        if package is None:
            return []
        assets = [a for a in package.assets if a.article_mode == mode]
        if not assets:
            raise ValueError(f"visual package has no assets for {mode}")
        if mode == "WECHAT_STICKER_POST":
            if not any(a.role in {"sticker", "hero"} for a in assets):
                raise ValueError("WeChat sticker package requires at least one sticker/hero visual")
        elif len([a for a in assets if a.role == "hero"]) != 1:
            raise ValueError(f"{mode} requires exactly one hero visual")
        if package.avatar_required and any(not a.avatar_included for a in assets):
            raise ValueError(f"visual package has asset without required avatar for {mode}")
        return [
            DocumentImage(
                local_path=a.local_path,
                role="hero" if a.role == "sticker" else a.role,
                anchor_after_block=a.anchor_after_block,
                hook_text=a.hook_text,
            )
            for a in assets
        ]

    def execute(self, state: WritingState) -> WritingState:
        outdir = self.root / state.contract.task_id
        outdir.mkdir(parents=True, exist_ok=True)
        state.working["output_dir"] = str(outdir)
        draft = DraftPackage.model_validate(state.working["draft"])

        if state.contract.delivery_channel == DeliveryChannel.CHAT_TEXT:
            pieces: list[str] = []
            for payload in [draft.finance_deep, draft.finance_broad]:
                if payload:
                    body = "\n".join(b.text for b in payload.blocks)
                    pieces.append("\n".join([payload.title, body, "风险提示与免责声明", payload.risk_disclaimer]))
            if draft.wechat_sticker_post:
                p = draft.wechat_sticker_post
                pieces.append("\n".join(x for x in [p.title, p.body, p.interaction_prompt, p.risk_disclaimer] if x))
            text_path = outdir / "CHAT_TEXT.txt"
            text_path.write_text("\n\n---\n\n".join(pieces), encoding="utf-8")
            state.artifacts[ArtifactKind.CHAT_TEXT] = Artifact(
                kind=ArtifactKind.CHAT_TEXT,
                path=str(text_path),
                exists=True,
                sha256=sha256_file(text_path),
            )
            state.set_gate("delivery_output", GateStatus.PASS, [text_path.name])
            return state

        visual_package: ResolvedVisualPackage | None = None
        if state.contract.visuals_enabled:
            raw_visuals = state.working.get("resolved_visual_package")
            if not raw_visuals:
                state.set_gate("delivery_output", GateStatus.FAIL, [], "resolved visual package missing while visuals_enabled=true")
                return state
            visual_package = ResolvedVisualPackage.model_validate(raw_visuals)
            manifest_path = outdir / "VISUAL_MANIFEST.json"
            manifest_path.write_text(json.dumps(state.working.get("visual_package"), ensure_ascii=False, indent=2), encoding="utf-8")
            state.artifacts[ArtifactKind.VISUAL_MANIFEST_JSON] = Artifact(
                kind=ArtifactKind.VISUAL_MANIFEST_JSON,
                path=str(manifest_path),
                exists=True,
                sha256=sha256_file(manifest_path),
            )

        built: list[str] = []
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            if draft.wechat_sticker_post is None:
                state.set_gate("delivery_output", GateStatus.FAIL, [], "WECHAT_STICKER_POST payload missing")
                return state
            images = self._images(visual_package, "WECHAT_STICKER_POST") if state.contract.visuals_enabled else []
            p = build_article_docx(self._sticker_article(draft.wechat_sticker_post), outdir / "WECHAT_STICKER_POST.docx", self.policy, images=images)
            state.artifacts[ArtifactKind.WECHAT_STICKER_DOCX] = Artifact(kind=ArtifactKind.WECHAT_STICKER_DOCX, path=str(p), exists=True, sha256=sha256_file(p))
            state.working["platform_constraint_snapshot"] = draft.wechat_sticker_post.constraints.model_dump(mode="json")
            built.append(p.name)
            state.set_gate("delivery_output", GateStatus.PASS, built)
            return state

        if state.contract.distribution_mode in {DistributionMode.FINANCE_DEEP, DistributionMode.DUAL}:
            if draft.finance_deep is None:
                state.set_gate("delivery_output", GateStatus.FAIL, [], "FINANCE_DEEP payload missing")
                return state
            images = self._images(visual_package, "FINANCE_DEEP") if state.contract.visuals_enabled else []
            p = build_article_docx(self._article(draft.finance_deep), outdir / "FINANCE_DEEP.docx", self.policy, images=images)
            state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(kind=ArtifactKind.FINANCE_DEEP_DOCX, path=str(p), exists=True, sha256=sha256_file(p))
            built.append(p.name)

        if state.contract.distribution_mode in {DistributionMode.FINANCE_BROAD, DistributionMode.DUAL}:
            if draft.finance_broad is None:
                state.set_gate("delivery_output", GateStatus.FAIL, [], "FINANCE_BROAD payload missing")
                return state
            images = self._images(visual_package, "FINANCE_BROAD") if state.contract.visuals_enabled else []
            p = build_article_docx(self._article(draft.finance_broad), outdir / "FINANCE_BROAD.docx", self.policy, images=images)
            state.artifacts[ArtifactKind.FINANCE_BROAD_DOCX] = Artifact(kind=ArtifactKind.FINANCE_BROAD_DOCX, path=str(p), exists=True, sha256=sha256_file(p))
            built.append(p.name)

        state.set_gate("delivery_output", GateStatus.PASS, built)
        return state


class MechanicalAuditExecutor:
    def __init__(self, *, policy_path: str | Path | None = None, require_render: bool = True):
        self.policy = load_policy(policy_path) if policy_path else load_packaged_policy()
        self.require_render = require_render

    def execute(self, state: WritingState) -> WritingState:
        if state.contract.delivery_channel == DeliveryChannel.CHAT_TEXT:
            state.set_gate("mechanical_audit", GateStatus.N_A, ["CHAT_TEXT delivery"])
            return state

        draft = DraftPackage.model_validate(state.working["draft"])
        stock_names: set[str] = set()
        for payload in [draft.finance_deep, draft.finance_broad]:
            if payload:
                stock_names.update(payload.stock_names)
        if draft.wechat_sticker_post:
            stock_names.update(draft.wechat_sticker_post.stock_names)

        visual_package = ResolvedVisualPackage.model_validate(state.working["resolved_visual_package"]) if state.contract.visuals_enabled else None
        evidence: list[str] = []
        errors: list[str] = []
        render_manifest: dict[str, list[str]] = {}
        kind_mode_pairs = [
            (ArtifactKind.FINANCE_DEEP_DOCX, "FINANCE_DEEP"),
            (ArtifactKind.FINANCE_BROAD_DOCX, "FINANCE_BROAD"),
            (ArtifactKind.WECHAT_STICKER_DOCX, "WECHAT_STICKER_POST"),
        ]
        for kind, mode in kind_mode_pairs:
            artifact = state.artifacts.get(kind)
            if not artifact:
                continue
            expected_images = None
            if visual_package is not None:
                expected_images = len([a for a in visual_package.assets if a.article_mode == mode])
            result = check_docx(artifact.path, stock_names=sorted(stock_names), policy=self.policy, expected_images=expected_images)
            evidence.append(f"{kind.value}: {json.dumps(result, ensure_ascii=False)}")
            errors.extend(result["errors"])
            if self.require_render:
                outdir = Path(state.working["output_dir"]) / f"render_{kind.value.lower()}"
                try:
                    pages = render_docx_pages(artifact.path, outdir)
                except Exception as exc:
                    errors.append(f"render failed for {kind.value}: {type(exc).__name__}: {exc}")
                else:
                    render_manifest[kind.value] = pages
                    evidence.append(f"rendered {kind.value}: {len(pages)} page(s)")

        state.working["render_manifest"] = render_manifest
        status = GateStatus.PASS if not errors else GateStatus.REVISE
        state.set_gate("mechanical_audit", status, evidence, "; ".join(errors))
        return state


def _artifact_identity_lines(state: WritingState) -> list[str]:
    lines: list[str] = []
    for kind, artifact in state.artifacts.items():
        if kind == ArtifactKind.AUDIT_DOCX:
            continue
        path = Path(artifact.path)
        exists = path.is_file()
        actual_sha = sha256_file(path) if exists else "MISSING"
        sha_match = bool(exists and artifact.sha256 and actual_sha == artifact.sha256)
        lines.append(
            f"{kind.value}: file={path.name} | exists={exists} | sha256={actual_sha} | recorded_sha_match={sha_match}"
        )
    return lines


def finalize_audit_artifact(state: WritingState) -> None:
    if state.contract.delivery_channel == DeliveryChannel.CHAT_TEXT:
        return
    outdir = Path(state.working["output_dir"])
    research = state.working.get("research") or {}
    cognition = research.get("cognition") or {}
    evidence_items = research.get("evidence_ledger") or []
    verification_counts = Counter(item.get("verification_status", "UNKNOWN") for item in evidence_items)
    core_safe_count = sum(bool(item.get("core_safe")) for item in evidence_items)
    acceptance = state.working.get("acceptance_contract") or {}
    final_audit = state.working.get("final_audit") or {}
    reviewed_pages = final_audit.get("reviewed_render_pages") or []
    acceptance_evidence = final_audit.get("acceptance_evidence") or []
    render_manifest = state.working.get("render_manifest") or {}
    expected_render_pages = sum(len(pages) for pages in render_manifest.values())
    revision_history = state.working.get("revision_history") or []

    lines = [
        AuditLine(area=name, status=gate.status.value, evidence=" | ".join(gate.evidence), notes=gate.notes)
        for name, gate in state.gates.items()
    ]
    lines.extend(
        [
            AuditLine(
                area="Writing Acceptance Contract",
                status=state.gates.get("acceptance_contract").status.value if state.gates.get("acceptance_contract") else "NOT_RUN",
                evidence=json.dumps(acceptance, ensure_ascii=False),
                notes="Frozen article-level contract used for final verification",
            ),
            AuditLine(
                area="Final Acceptance Evidence",
                status=state.gates.get("final_audit").status.value if state.gates.get("final_audit") else "NOT_RUN",
                evidence=json.dumps(acceptance_evidence, ensure_ascii=False),
                notes="Concrete final-content evidence submitted by the independent final auditor",
            ),
            AuditLine(
                area="Render Page Review",
                status="PASS" if len(reviewed_pages) == expected_render_pages else ("N_A" if expected_render_pages == 0 else "FAIL"),
                evidence=json.dumps(reviewed_pages, ensure_ascii=False),
                notes=f"reviewed={len(reviewed_pages)} | expected={expected_render_pages}",
            ),
            AuditLine(
                area="Evidence Verification",
                status="PASS" if core_safe_count > 0 else "FAIL",
                evidence=f"items={len(evidence_items)} | core_safe={core_safe_count} | verification={dict(verification_counts)}",
                notes=f"review_queue={len(research.get('review_queue', []))} | failed_tools_or_sources={len(research.get('failed_tools_or_sources', []))}",
            ),
            AuditLine(
                area="Revision Invalidation History",
                status="N_A" if not revision_history else "PASS",
                evidence=json.dumps(revision_history, ensure_ascii=False),
                notes="Any revision listed here required downstream PASS invalidation/rebuild",
            ),
        ]
    )

    artifact_lines = _artifact_identity_lines(state)
    summary_lines = [
        f"任务ID：{state.contract.task_id}",
        f"内容模式：{state.contract.content_mode.value}｜分发模式：{state.contract.distribution_mode.value}｜交付：{state.contract.delivery_channel.value}",
        f"Required Outputs：{', '.join(kind.value for kind in state.contract.required_outputs)}",
        f"来源边界：{research.get('source_boundary', 'N/A')}",
        f"研究覆盖：{json.dumps(research.get('coverage', {}), ensure_ascii=False)}",
        f"证据：总数={len(evidence_items)}｜Core Safe={core_safe_count}｜核验状态={dict(verification_counts)}",
        f"ReviewQueue={len(research.get('review_queue', []))}｜研究失败/降级记录={len(research.get('failed_tools_or_sources', []))}",
        f"复用知识引用={len(cognition.get('prior_knowledge_refs', []))}｜知识回写候选={len(research.get('knowledge_writeback_candidates', []))}｜回写凭据={len(state.working.get('knowledge_writeback_refs', []))}",
        f"Render页面：expected={expected_render_pages}｜reviewed={len(reviewed_pages)}",
    ]
    path = build_audit_docx(
        title=f"写作审计报告｜{state.contract.task_id}",
        lines=lines,
        artifacts=artifact_lines,
        output=outdir / "WRITING_AUDIT_REPORT.docx",
        summary_lines=summary_lines,
    )
    state.artifacts[ArtifactKind.AUDIT_DOCX] = Artifact(kind=ArtifactKind.AUDIT_DOCX, path=str(path), exists=True, sha256=sha256_file(path))
