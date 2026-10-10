from __future__ import annotations

import json
from pathlib import Path

from ..checks import check_docx, load_policy, sha256_file
from ..document import ArticleDocument, AuditLine, Block, build_article_docx, build_audit_docx
from ..models import Artifact, ArtifactKind, DistributionMode, GateStatus, WritingState
from ..rendering import render_docx_pages
from ..resources import load_packaged_policy
from ..schemas import DraftPackage


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

    def execute(self, state: WritingState) -> WritingState:
        outdir = self.root / state.contract.task_id
        outdir.mkdir(parents=True, exist_ok=True)
        state.working["output_dir"] = str(outdir)
        draft = DraftPackage.model_validate(state.working["draft"])

        built: list[str] = []
        if state.contract.distribution_mode in {DistributionMode.FINANCE_DEEP, DistributionMode.DUAL}:
            if draft.finance_deep is None:
                state.set_gate("delivery_output", GateStatus.FAIL, [], "FINANCE_DEEP payload missing")
                return state
            p = build_article_docx(self._article(draft.finance_deep), outdir / "FINANCE_DEEP.docx", self.policy)
            digest = sha256_file(p)
            state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(kind=ArtifactKind.FINANCE_DEEP_DOCX, path=str(p), exists=True, sha256=digest)
            built.append(f"FINANCE_DEEP_DOCX built; sha256={digest}")

        if state.contract.distribution_mode in {DistributionMode.FINANCE_BROAD, DistributionMode.DUAL}:
            if draft.finance_broad is None:
                state.set_gate("delivery_output", GateStatus.FAIL, [], "FINANCE_BROAD payload missing")
                return state
            p = build_article_docx(self._article(draft.finance_broad), outdir / "FINANCE_BROAD.docx", self.policy)
            digest = sha256_file(p)
            state.artifacts[ArtifactKind.FINANCE_BROAD_DOCX] = Artifact(kind=ArtifactKind.FINANCE_BROAD_DOCX, path=str(p), exists=True, sha256=digest)
            built.append(f"FINANCE_BROAD_DOCX built; sha256={digest}")

        state.set_gate("delivery_output", GateStatus.PASS, built)
        return state


class MechanicalAuditExecutor:
    def __init__(self, *, policy_path: str | Path | None = None, require_render: bool = True):
        self.policy = load_policy(policy_path) if policy_path else load_packaged_policy()
        self.require_render = require_render

    @staticmethod
    def _expected_article_pairs(state: WritingState, draft: DraftPackage):
        pairs = []
        if state.contract.distribution_mode in {DistributionMode.FINANCE_DEEP, DistributionMode.DUAL}:
            pairs.append((ArtifactKind.FINANCE_DEEP_DOCX, draft.finance_deep))
        if state.contract.distribution_mode in {DistributionMode.FINANCE_BROAD, DistributionMode.DUAL}:
            pairs.append((ArtifactKind.FINANCE_BROAD_DOCX, draft.finance_broad))
        return pairs

    def execute(self, state: WritingState) -> WritingState:
        draft = DraftPackage.model_validate(state.working["draft"])
        evidence: list[str] = []
        errors: list[str] = []
        render_manifest: dict[str, list[str]] = {}

        for kind, payload in self._expected_article_pairs(state, draft):
            if payload is None:
                errors.append(f"required draft payload missing during mechanical audit: {kind.value}")
                continue

            artifact = state.artifacts.get(kind)
            if artifact is None:
                errors.append(f"required Word artifact mapping missing during mechanical audit: {kind.value}")
                continue
            path = Path(artifact.path)
            if not artifact.exists or not path.is_file():
                errors.append(f"required Word artifact file missing during mechanical audit: {kind.value}")
                continue

            result = check_docx(
                path,
                stock_names=payload.stock_names,
                policy=self.policy,
                required_bold_anchors=payload.skim_path_anchors,
                require_deep_navigation=kind == ArtifactKind.FINANCE_DEEP_DOCX,
            )
            evidence.append(f"{kind.value}: {json.dumps(result, ensure_ascii=False)}")
            errors.extend(f"{kind.value}: {error}" for error in result["errors"])

            if self.require_render:
                outdir = Path(state.working["output_dir"]) / f"render_{kind.value.lower()}"
                try:
                    pages = render_docx_pages(path, outdir)
                except Exception as exc:
                    errors.append(f"render failed for {kind.value}: {type(exc).__name__}: {exc}")
                else:
                    render_manifest[kind.value] = pages
                    evidence.append(f"rendered {kind.value}: {len(pages)} page(s)")

        state.working["render_manifest"] = render_manifest
        status = GateStatus.PASS if not errors else GateStatus.REVISE
        state.set_gate("mechanical_audit", status, evidence, "; ".join(errors))
        return state


def _sanitize_runtime_paths(state: WritingState, text: str) -> str:
    """Keep the audit artifact useful without publishing server-local filesystem paths."""
    redacted = text
    replacements: list[tuple[str, str]] = []
    output_dir = state.working.get("output_dir")
    if output_dir:
        replacements.append((str(output_dir), "<runtime-output>"))
    for artifact in state.artifacts.values():
        if artifact.path:
            replacements.append((str(artifact.path), Path(artifact.path).name))
    for raw, replacement in sorted(replacements, key=lambda item: len(item[0]), reverse=True):
        redacted = redacted.replace(raw, replacement)
    return redacted


def finalize_audit_artifact(state: WritingState) -> None:
    outdir = Path(state.working["output_dir"])
    lines = [
        AuditLine(
            area=name,
            status=gate.status.value,
            evidence=_sanitize_runtime_paths(state, " | ".join(gate.evidence)),
            notes=_sanitize_runtime_paths(state, gate.notes),
        )
        for name, gate in state.gates.items()
    ]
    artifact_lines = [
        f"{kind.value}: file={Path(artifact.path).name} | sha256={artifact.sha256 or ''}"
        for kind, artifact in state.artifacts.items()
        if kind != ArtifactKind.AUDIT_DOCX
    ]
    research = state.working.get("research") or {}
    cognition = research.get("cognition") or {}
    editorial = state.working.get("editorial_plan") or {}
    summary_lines = [
        f"分发模式：{state.contract.distribution_mode.value}｜交付：WORD_FILE_ONLY",
        f"来源边界：{research.get('source_boundary', 'N/A')}",
        f"研究覆盖：{json.dumps(research.get('coverage', {}), ensure_ascii=False)}",
        f"股票Universe覆盖：{json.dumps(research.get('universe_coverage', {}), ensure_ascii=False)}",
        f"市场解释范围：{research.get('market_explanation_scope', 'N/A')}｜{research.get('market_explanation_scope_reason', '')}",
        f"财经完整覆盖义务：{json.dumps((editorial.get('finance_deep') or {}).get('completeness_obligations', []), ensure_ascii=False)}",
        f"Deep公司覆盖义务：{json.dumps((editorial.get('finance_deep') or {}).get('company_coverage_obligations', []), ensure_ascii=False)}",
        f"复用知识引用：{len(cognition.get('prior_knowledge_refs', []))}｜知识回写候选：{len(research.get('knowledge_writeback_candidates', []))}｜回写凭据：{len(state.working.get('knowledge_writeback_refs', []))}",
    ]
    path = build_audit_docx(
        title=f"写作审计报告｜{state.contract.task_id}",
        lines=lines,
        artifacts=artifact_lines,
        output=outdir / "WRITING_AUDIT_REPORT.docx",
        summary_lines=summary_lines,
    )
    state.artifacts[ArtifactKind.AUDIT_DOCX] = Artifact(kind=ArtifactKind.AUDIT_DOCX, path=str(path), exists=True, sha256=sha256_file(path))
