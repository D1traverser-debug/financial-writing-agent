from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ..checks import check_docx, load_policy, sha256_file
from ..document import ArticleDocument, AuditLine, Block, DocumentImage, build_article_docx, build_audit_docx
from ..models import Artifact, ArtifactKind, DeliveryChannel, DistributionMode, GateStatus, Stage, WritingState
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
    def _images(package: VisualPackage | None, mode: str) -> list[DocumentImage]:
        if package is None:
            return []
        assets = [a for a in package.assets if a.article_mode == mode]
        if not assets:
            raise ValueError(f"visual package has no assets for {mode}")
        if not any(a.role == "hero" for a in assets):
            raise ValueError(f"visual package has no hero for {mode}")
        if package.avatar_required and any(not a.avatar_included for a in assets):
            raise ValueError(f"visual package has asset without required avatar for {mode}")
        return [
            DocumentImage(
                source_uri=a.source_uri,
                role=a.role,
                anchor_after_block=a.anchor_after_block,
                hook_text=a.hook_text,
            )
            for a in assets
        ]

    def execute(self, state: WritingState) -> WritingState:
        outdir = self.root / state.contract.task_id
        outdir.mkdir(parents=True, exist_ok=True)
        state.working["output_dir"] = str(outdir)

        if state.contract.delivery_channel == DeliveryChannel.CHAT_TEXT:
            draft = DraftPackage.model_validate(state.working["draft"])
            pieces: list[str] = []
            for payload in [draft.finance_deep, draft.finance_broad]:
                if payload:
                    pieces.append(payload.title + "\n" + "\n".join(b.text for b in payload.blocks))
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

        draft = DraftPackage.model_validate(state.working["draft"])
        built: list[str] = []
        if state.contract.distribution_mode in {DistributionMode.FINANCE_DEEP, DistributionMode.DUAL}:
            if draft.finance_deep is None:
                state.set_gate("delivery_output", GateStatus.FAIL, [], "FINANCE_DEEP payload missing")
                return state
            images = self._images(visual_package, "FINANCE_DEEP") if state.contract.visuals_enabled else []
            p = build_article_docx(
                self._article(draft.finance_deep),
                outdir / "FINANCE_DEEP.docx",
                self.policy,
                images=images,
            )
            state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(
                kind=ArtifactKind.FINANCE_DEEP_DOCX, path=str(p), exists=True, sha256=sha256_file(p)
            )
            built.append(str(p))

        if state.contract.distribution_mode in {DistributionMode.FINANCE_BROAD, DistributionMode.DUAL}:
            if draft.finance_broad is None:
                state.set_gate("delivery_output", GateStatus.FAIL, [], "FINANCE_BROAD payload missing")
                return state
            images = self._images(visual_package, "FINANCE_BROAD") if state.contract.visuals_enabled else []
            p = build_article_docx(
                self._article(draft.finance_broad),
                outdir / "FINANCE_BROAD.docx",
                self.policy,
                images=images,
            )
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

        visual_package = VisualPackage.model_validate(state.working["visual_package"]) if state.contract.visuals_enabled else None
        evidence: list[str] = []
        errors: list[str] = []
        render_manifest: dict[str, list[str]] = {}
        mode_for_kind = {
            ArtifactKind.FINANCE_DEEP_DOCX: "FINANCE_DEEP",
            ArtifactKind.FINANCE_BROAD_DOCX: "FINANCE_BROAD",
        }
        for kind in [ArtifactKind.FINANCE_DEEP_DOCX, ArtifactKind.FINANCE_BROAD_DOCX]:
            artifact = state.artifacts.get(kind)
            if not artifact:
                continue
            expected_images = None
            if visual_package is not None:
                expected_images = len([a for a in visual_package.assets if a.article_mode == mode_for_kind[kind]])
            result = check_docx(
                artifact.path,
                stock_names=sorted(stock_names),
                policy=self.policy,
                expected_images=expected_images,
            )
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
    """Build the visible audit deliverable after final semantic PASS and before COMPLETE."""
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
