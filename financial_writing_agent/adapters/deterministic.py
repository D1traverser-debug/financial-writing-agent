from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ..checks import check_docx, load_policy, sha256_file
from ..document import ArticleDocument, AuditLine, Block, DocumentImage, build_article_docx, build_audit_docx
from ..models import Artifact, ArtifactKind, ContentMode, DeliveryChannel, DistributionMode, GateStatus, WritingState
from ..schemas import DraftPackage, VisualPackage


class DeliveryExecutor:
    def __init__(self, *, root: str | Path = "runs", policy_path: str | Path | None = None):
        project_root = Path(__file__).resolve().parents[2]
        self.root = Path(root)
        self.policy_path = Path(policy_path) if policy_path else project_root / "config" / "policy.json"
        self.policy = load_policy(self.policy_path)

    def _article(self, payload) -> ArticleDocument:
        return ArticleDocument(
            title=payload.title,
            stock_names=payload.stock_names,
            blocks=[Block(kind=b.kind, text=b.text) for b in payload.blocks],
        )

    @staticmethod
    def _sticker_article(payload) -> ArticleDocument:
        blocks = [Block(kind="body", text=payload.body)]
        if payload.interaction_prompt.strip():
            blocks.append(Block(kind="body", text=payload.interaction_prompt.strip()))
        blocks.extend(
            [
                Block(kind="h1", text="风险提示与免责声明"),
                Block(kind="body", text=payload.risk_disclaimer),
            ]
        )
        return ArticleDocument(title=payload.title, stock_names=payload.stock_names, blocks=blocks)

    @staticmethod
    def _images(package: VisualPackage | None, mode: str) -> list[DocumentImage]:
        if package is None:
            return []
        assets = [a for a in package.assets if a.article_mode == mode]
        if not assets:
            raise ValueError(f"visual package has no assets for {mode}")
        if mode == "WECHAT_STICKER_POST":
            if not any(a.role in {"sticker", "hero"} for a in assets):
                raise ValueError("WeChat sticker package requires at least one sticker/hero visual")
        elif not any(a.role == "hero" for a in assets):
            raise ValueError(f"visual package has no hero for {mode}")
        if package.avatar_required and any(not a.avatar_included for a in assets):
            raise ValueError(f"visual package has asset without required avatar for {mode}")
        return [
            DocumentImage(
                source_uri=a.source_uri,
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
                    pieces.append(payload.title + "\n" + "\n".join(b.text for b in payload.blocks))
            if draft.wechat_sticker_post:
                p = draft.wechat_sticker_post
                pieces.append("\n".join(x for x in [p.title, p.body, p.interaction_prompt, p.risk_disclaimer] if x))
            text_path = outdir / "CHAT_TEXT.txt"
            text_path.write_text("\n\n---\n\n".join(pieces), encoding="utf-8")
            art = Artifact(kind=ArtifactKind.CHAT_TEXT, path=str(text_path), exists=True, sha256=sha256_file(text_path))
            state.artifacts[ArtifactKind.CHAT_TEXT] = art
            state.set_gate("delivery_output", GateStatus.PASS, [str(text_path)])
            return state

        visual_package: VisualPackage | None = None
        if state.contract.visuals_enabled:
            raw_visuals = state.working.get("visual_package")
            if not raw_visuals:
                state.set_gate("delivery_output", GateStatus.FAIL, [], "visual package missing while visuals_enabled=true")
                return state
            visual_package = VisualPackage.model_validate(raw_visuals)
            manifest_path = outdir / "VISUAL_MANIFEST.json"
            manifest_path.write_text(visual_package.model_dump_json(indent=2), encoding="utf-8")
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
            p = build_article_docx(
                self._sticker_article(draft.wechat_sticker_post),
                outdir / "WECHAT_STICKER_POST.docx",
                self.policy,
                images=images,
            )
            state.artifacts[ArtifactKind.WECHAT_STICKER_DOCX] = Artifact(
                kind=ArtifactKind.WECHAT_STICKER_DOCX, path=str(p), exists=True, sha256=sha256_file(p)
            )
            state.working["platform_constraint_snapshot"] = draft.wechat_sticker_post.constraints.model_dump(mode="json")
            built.append(str(p))
            state.set_gate("delivery_output", GateStatus.PASS, built)
            return state

        if state.contract.distribution_mode in {DistributionMode.FINANCE_DEEP, DistributionMode.DUAL}:
            if draft.finance_deep is None:
                state.set_gate("delivery_output", GateStatus.FAIL, [], "FINANCE_DEEP payload missing")
                return state
            images = self._images(visual_package, "FINANCE_DEEP") if state.contract.visuals_enabled else []
            p = build_article_docx(self._article(draft.finance_deep), outdir / "FINANCE_DEEP.docx", self.policy, images=images)
            state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(
                kind=ArtifactKind.FINANCE_DEEP_DOCX, path=str(p), exists=True, sha256=sha256_file(p)
            )
            built.append(str(p))

        if state.contract.distribution_mode in {DistributionMode.FINANCE_BROAD, DistributionMode.DUAL}:
            if draft.finance_broad is None:
                state.set_gate("delivery_output", GateStatus.FAIL, [], "FINANCE_BROAD payload missing")
                return state
            images = self._images(visual_package, "FINANCE_BROAD") if state.contract.visuals_enabled else []
            p = build_article_docx(self._article(draft.finance_broad), outdir / "FINANCE_BROAD.docx", self.policy, images=images)
            state.artifacts[ArtifactKind.FINANCE_BROAD_DOCX] = Artifact(
                kind=ArtifactKind.FINANCE_BROAD_DOCX, path=str(p), exists=True, sha256=sha256_file(p)
            )
            built.append(str(p))

        state.set_gate("delivery_output", GateStatus.PASS, built)
        return state


class MechanicalAuditExecutor:
    def __init__(self, *, policy_path: str | Path | None = None, require_render: bool = True):
        project_root = Path(__file__).resolve().parents[2]
        self.project_root = project_root
        self.policy = load_policy(policy_path or project_root / "config" / "policy.json")
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

        visual_package = VisualPackage.model_validate(state.working["visual_package"]) if state.contract.visuals_enabled else None
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
                proc = subprocess.run(
                    [sys.executable, str(self.project_root / "scripts" / "render_docx.py"), artifact.path, "--out", str(outdir)],
                    capture_output=True,
                    text=True,
                )
                if proc.returncode != 0:
                    errors.append(f"render failed for {kind.value}: {proc.stderr.strip() or proc.stdout.strip()}")
                else:
                    pages = [line.strip() for line in proc.stdout.splitlines() if line.strip().endswith(".png")]
                    render_manifest[kind.value] = pages
                    evidence.append(f"rendered {kind.value}: {len(pages)} page(s)")

        state.working["render_manifest"] = render_manifest
        status = GateStatus.PASS if not errors else GateStatus.REVISE
        state.set_gate("mechanical_audit", status, evidence, "; ".join(errors))
        return state


def finalize_audit_artifact(state: WritingState) -> None:
    if state.contract.delivery_channel == DeliveryChannel.CHAT_TEXT:
        return
    outdir = Path(state.working["output_dir"])
    lines = [
        AuditLine(area=name, status=gate.status.value, evidence=" | ".join(gate.evidence), notes=gate.notes)
        for name, gate in state.gates.items()
    ]
    artifact_lines = [
        f"{kind.value}: {artifact.path} | sha256={artifact.sha256 or ''}"
        for kind, artifact in state.artifacts.items()
        if kind != ArtifactKind.AUDIT_DOCX
    ]
    path = build_audit_docx(
        title=f"写作审计报告｜{state.contract.task_id}",
        lines=lines,
        artifacts=artifact_lines,
        output=outdir / "WRITING_AUDIT_REPORT.docx",
    )
    state.artifacts[ArtifactKind.AUDIT_DOCX] = Artifact(
        kind=ArtifactKind.AUDIT_DOCX, path=str(path), exists=True, sha256=sha256_file(path)
    )
