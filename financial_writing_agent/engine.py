from __future__ import annotations

import hashlib
from pathlib import Path

from .models import ArtifactKind, ContentMode, DistributionMode, GateStatus, Stage, TaskContract, WritingState
from .store import SQLiteStateStore


class WorkflowError(RuntimeError):
    pass


ALLOWED_TRANSITIONS: dict[Stage, set[Stage]] = {
    Stage.INTAKE: {Stage.RESEARCH, Stage.BLOCKED},
    Stage.RESEARCH: {Stage.RESEARCH_AUDIT, Stage.BLOCKED},
    Stage.RESEARCH_AUDIT: {Stage.RESEARCH, Stage.EDITORIAL, Stage.BLOCKED},
    Stage.EDITORIAL: {Stage.TITLE, Stage.BLOCKED},
    Stage.TITLE: {Stage.TITLE, Stage.DRAFT, Stage.BLOCKED},
    Stage.DRAFT: {Stage.BROAD_DERIVATION, Stage.EDITORIAL_AUDIT, Stage.BLOCKED},
    Stage.BROAD_DERIVATION: {Stage.EDITORIAL_AUDIT, Stage.BLOCKED},
    Stage.EDITORIAL_AUDIT: {Stage.TITLE, Stage.DRAFT, Stage.DELIVERY, Stage.BLOCKED},
    Stage.DELIVERY: {Stage.MECHANICAL_AUDIT, Stage.BLOCKED},
    Stage.MECHANICAL_AUDIT: {Stage.DELIVERY, Stage.FINAL_AUDIT, Stage.BLOCKED},
    Stage.FINAL_AUDIT: {
        Stage.RESEARCH,
        Stage.EDITORIAL,
        Stage.TITLE,
        Stage.DRAFT,
        Stage.DELIVERY,
        Stage.COMPLETE,
        Stage.BLOCKED,
    },
    Stage.COMPLETE: set(),
    Stage.BLOCKED: {
        Stage.INTAKE,
        Stage.RESEARCH,
        Stage.RESEARCH_AUDIT,
        Stage.EDITORIAL,
        Stage.TITLE,
        Stage.DRAFT,
        Stage.BROAD_DERIVATION,
        Stage.EDITORIAL_AUDIT,
        Stage.DELIVERY,
        Stage.MECHANICAL_AUDIT,
        Stage.FINAL_AUDIT,
    },
}


REVISION_GATES: dict[Stage, tuple[str, ...]] = {
    Stage.RESEARCH: (
        "research_output",
        "research_audit",
        "editorial_plan",
        "acceptance_contract",
        "title_audit",
        "draft_output",
        "broad_derivation",
        "style_audit",
        "editorial_audit",
        "visual_assets",
        "delivery_output",
        "mechanical_audit",
        "final_audit",
    ),
    Stage.EDITORIAL: (
        "editorial_plan",
        "acceptance_contract",
        "title_audit",
        "draft_output",
        "broad_derivation",
        "style_audit",
        "editorial_audit",
        "visual_assets",
        "delivery_output",
        "mechanical_audit",
        "final_audit",
    ),
    Stage.TITLE: (
        "acceptance_contract",
        "title_audit",
        "draft_output",
        "broad_derivation",
        "style_audit",
        "editorial_audit",
        "visual_assets",
        "delivery_output",
        "mechanical_audit",
        "final_audit",
    ),
    Stage.DRAFT: (
        "draft_output",
        "broad_derivation",
        "style_audit",
        "editorial_audit",
        "visual_assets",
        "delivery_output",
        "mechanical_audit",
        "final_audit",
    ),
    Stage.DELIVERY: (
        "delivery_output",
        "mechanical_audit",
        "final_audit",
    ),
}


DELIVERY_ARTIFACTS = {
    ArtifactKind.FINANCE_DEEP_DOCX,
    ArtifactKind.FINANCE_BROAD_DOCX,
    ArtifactKind.WECHAT_STICKER_DOCX,
    ArtifactKind.AUDIT_DOCX,
    ArtifactKind.CHAT_TEXT,
}


BASE_COMPLETION_GATES = {
    "runtime_initialized",
    "knowledge_context",
    "research_output",
    "research_audit",
    "editorial_plan",
    "acceptance_contract",
    "title_audit",
    "draft_output",
    "style_audit",
    "editorial_audit",
    "delivery_output",
    "mechanical_audit",
    "knowledge_sync",
    "final_audit",
}


GLOBAL_FINAL_CRITERIA = (
    "evidence_boundary",
    "source_completion",
    "omission_scan",
    "count_reconciliation",
    "time_integrity",
    "market_data_boundary",
    "counterexample_scan",
    "required_outputs",
)

FORMAL_FINAL_CRITERIA = (
    "selected_title",
    "independent_lead",
    "opening_first_three_sentences",
    "h1_structure",
    "side_focus",
    "company_selection_basis",
    "headline_anchor",
    "opening_payoff",
    "hook_quality",
    "stock_judgment_clarity",
    "bold_scan_skeleton",
    "reasoning_continuity",
    "compliance_risk",
)

STICKER_FINAL_CRITERIA = (
    "platform_constraints",
    "title_body_payoff",
    "useful_body",
    "image_copy_complement",
    "compliance_risk",
)


VACUOUS_FINAL_EVIDENCE_VALUES = {
    "pass",
    "passed",
    "ok",
    "checked",
    "done",
    "na",
    "n/a",
    "通过",
    "已通过",
    "已检查",
    "检查通过",
    "符合",
    "已符合",
    "无问题",
    "没问题",
    "完成",
}


def _is_vacuous_final_evidence(value: str) -> bool:
    normalized = "".join(value.lower().split()).strip(".,。!！;；:：")
    return normalized in VACUOUS_FINAL_EVIDENCE_VALUES


class WritingEngine:
    def __init__(self, store: SQLiteStateStore):
        self.store = store

    def start(self, contract: TaskContract) -> WritingState:
        state = WritingState(contract=contract)
        state.add_trace("RUNTIME_STARTED", "TaskContract initialized before source retrieval or drafting")
        state.set_gate("runtime_initialized", GateStatus.PASS, ["TaskContract exists", "State store active"])
        state.set_gate(
            "knowledge_context",
            GateStatus.NOT_RUN,
            [],
            "Explicit PASS/N_A durable-knowledge recall decision required before research submission",
        )
        state.set_gate("knowledge_sync", GateStatus.NOT_RUN, [], "Explicit PASS/N_A writeback decision required before final completion")
        if contract.distribution_mode == DistributionMode.DUAL and contract.content_mode == ContentMode.FORMAL_ARTICLE:
            state.set_gate(
                "broad_derivation",
                GateStatus.NOT_RUN,
                [],
                "FINANCE_BROAD must be derived only after the FINANCE_DEEP mother draft is frozen",
            )
            state.working["broad_derivation_phase"] = "WAITING_FOR_DEEP"
        self.store.save(state)
        return state

    def transition(self, state: WritingState, next_stage: Stage, *, reason: str = "") -> WritingState:
        if next_stage not in ALLOWED_TRANSITIONS[state.stage]:
            raise WorkflowError(f"Illegal transition: {state.stage} -> {next_stage}")
        state.add_trace("STAGE_EXIT", reason)
        state.stage = next_stage
        state.add_trace("STAGE_ENTER", reason)
        self.store.save(state)
        return state

    def block(self, state: WritingState, reason: str) -> WritingState:
        state.blocked_reason = reason
        if state.stage != Stage.BLOCKED:
            blocked_from = state.stage
            state.working["blocked_from_stage"] = blocked_from.value
            state.working.setdefault("blocked_history", []).append(
                {"from_stage": blocked_from.value, "reason": reason}
            )
            self.transition(state, Stage.BLOCKED, reason=reason)
        self.store.save(state)
        return state

    def resume_from_blocked(self, state: WritingState) -> WritingState:
        if state.stage != Stage.BLOCKED:
            raise WorkflowError("resume_from_blocked is only legal from BLOCKED")
        raw_target = state.working.get("blocked_from_stage")
        if not raw_target:
            raise WorkflowError("BLOCKED state is missing blocked_from_stage recovery metadata")
        try:
            target = Stage(raw_target)
        except ValueError as exc:
            raise WorkflowError(f"invalid blocked_from_stage={raw_target}") from exc
        if target in {Stage.BLOCKED, Stage.COMPLETE}:
            raise WorkflowError(f"illegal blocked recovery target={target.value}")
        state.blocked_reason = None
        state.working.pop("blocked_from_stage", None)
        state.add_trace("BLOCKED_RESUME", f"resume target={target.value}")
        return self.transition(state, target, reason=f"resume blocked task at original stage {target.value}")

    def record_gate(self, state: WritingState, name: str, status: GateStatus, evidence: list[str], notes: str = "") -> None:
        state.set_gate(name, status, evidence, notes)
        state.add_trace("GATE", f"{name}={status}")
        self.store.save(state)

    def increment_attempt(self, state: WritingState, key: str) -> int:
        state.attempts[key] = state.attempts.get(key, 0) + 1
        self.store.save(state)
        return state.attempts[key]

    def invalidate_for_revision(self, state: WritingState, target: Stage, *, reason: str = "") -> None:
        if target not in REVISION_GATES:
            raise WorkflowError(f"Unsupported revision target: {target.value}")

        revision_history = state.working.setdefault("revision_history", [])
        revision_history.append(
            {
                "from_stage": state.stage.value,
                "target_stage": target.value,
                "reason": reason,
            }
        )

        for gate_name in REVISION_GATES[target]:
            if gate_name in state.gates:
                state.set_gate(
                    gate_name,
                    GateStatus.NOT_RUN,
                    [],
                    f"Invalidated by revision to {target.value}: {reason}",
                )

        if target != Stage.DELIVERY:
            state.set_gate(
                "knowledge_sync",
                GateStatus.NOT_RUN,
                [],
                f"Re-evaluate knowledge writeback after revision to {target.value}",
            )

        for kind in list(state.artifacts):
            if kind in DELIVERY_ARTIFACTS:
                state.artifacts.pop(kind, None)

        if target in {Stage.RESEARCH, Stage.EDITORIAL, Stage.TITLE, Stage.DRAFT}:
            state.artifacts.pop(ArtifactKind.VISUAL_MANIFEST_JSON, None)
            state.working.pop("visual_package", None)
            state.working.pop("resolved_visual_package", None)
            state.working.pop("render_manifest", None)

        if state.contract.distribution_mode == DistributionMode.DUAL and target in {
            Stage.RESEARCH,
            Stage.EDITORIAL,
            Stage.TITLE,
            Stage.DRAFT,
        }:
            state.working["broad_derivation_phase"] = "WAITING_FOR_DEEP"
            state.working.pop("dual_derivation_receipt", None)

        state.add_trace("REVISION_INVALIDATION", f"target={target.value}; reason={reason}")
        self.store.save(state)

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _required_completion_gates(state: WritingState) -> set[str]:
        required = set(BASE_COMPLETION_GATES)
        if state.contract.visuals_enabled:
            required.add("visual_assets")
        if state.contract.content_mode == ContentMode.FORMAL_ARTICLE and state.contract.distribution_mode == DistributionMode.DUAL:
            required.add("broad_derivation")
        return required

    @staticmethod
    def _required_final_evidence_keys(state: WritingState) -> set[str]:
        keys = {f"GLOBAL.{criterion}" for criterion in GLOBAL_FINAL_CRITERIA}
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            keys.update(f"WECHAT_STICKER_POST.{criterion}" for criterion in STICKER_FINAL_CRITERIA)
            if state.contract.visuals_enabled:
                keys.add("WECHAT_STICKER_POST.visual_alignment")
            return keys

        modes: list[str] = []
        if state.contract.distribution_mode in {DistributionMode.FINANCE_DEEP, DistributionMode.DUAL}:
            modes.append("FINANCE_DEEP")
        if state.contract.distribution_mode in {DistributionMode.FINANCE_BROAD, DistributionMode.DUAL}:
            modes.append("FINANCE_BROAD")

        acceptance = state.working.get("acceptance_contract") or {}
        acceptance_key_by_mode = {
            "FINANCE_DEEP": "finance_deep",
            "FINANCE_BROAD": "finance_broad",
        }
        for mode in modes:
            keys.update(f"{mode}.{criterion}" for criterion in FORMAL_FINAL_CRITERIA)
            if state.contract.visuals_enabled:
                keys.add(f"{mode}.visual_alignment")
            mode_contract = acceptance.get(acceptance_key_by_mode[mode]) or {}
            for index, _ in enumerate(mode_contract.get("section_expectations") or [], start=1):
                keys.add(f"{mode}.H1_{index}.promise_payoff")
        if state.contract.distribution_mode == DistributionMode.DUAL:
            keys.update(
                {
                    "DUAL.cross_version_consistency",
                    "DUAL.deep_master_quality",
                    "DUAL.broad_derivation_fidelity",
                    "DUAL.broad_hook_strength",
                }
            )
        return keys

    @classmethod
    def _validate_final_acceptance_evidence(cls, state: WritingState) -> None:
        final_audit = state.working.get("final_audit") or {}
        entries = final_audit.get("acceptance_evidence") or []
        provided: dict[str, str] = {}
        duplicates: set[str] = set()
        for entry in entries:
            if not isinstance(entry, str) or ":" not in entry:
                continue
            key, evidence = entry.split(":", 1)
            key = key.strip()
            evidence = evidence.strip()
            if not key or not evidence:
                continue
            if key in provided:
                duplicates.add(key)
            provided[key] = evidence

        if duplicates:
            raise WorkflowError(f"Final acceptance evidence contains duplicate criterion key(s): {sorted(duplicates)}")

        required = cls._required_final_evidence_keys(state)
        missing = sorted(required - set(provided))
        if missing:
            raise WorkflowError(f"Final acceptance evidence missing required criterion(s): {missing}")

        vacuous = sorted(
            key
            for key in required
            if _is_vacuous_final_evidence(provided[key])
        )
        if vacuous:
            raise WorkflowError(
                "Final acceptance evidence must contain concrete criterion-specific proof, not a bare PASS/checked label; "
                f"vacuous={vacuous}"
            )

    def assert_can_complete(self, state: WritingState) -> None:
        required_gates = self._required_completion_gates(state)
        missing_gates = sorted(required_gates - set(state.gates))
        if missing_gates:
            raise WorkflowError(f"Mandatory completion gates missing: {missing_gates}")

        unresolved_required = [
            name
            for name in sorted(required_gates)
            if state.gates[name].status in {GateStatus.FAIL, GateStatus.REVISE, GateStatus.NOT_RUN}
        ]
        if unresolved_required:
            raise WorkflowError(f"Unresolved mandatory gates: {unresolved_required}")

        unresolved_extra = [
            name
            for name, gate in state.gates.items()
            if name not in required_gates and gate.status in {GateStatus.FAIL, GateStatus.REVISE, GateStatus.NOT_RUN}
        ]
        if unresolved_extra:
            raise WorkflowError(f"Unresolved additional gates: {unresolved_extra}")

        missing: list[ArtifactKind] = []
        unidentified: list[ArtifactKind] = []
        corrupted: list[ArtifactKind] = []
        for kind in state.contract.required_outputs:
            artifact = state.artifacts.get(kind)
            if artifact is None or not artifact.exists:
                missing.append(kind)
                continue
            path = Path(artifact.path)
            if not path.is_file():
                missing.append(kind)
                continue
            if not artifact.sha256:
                unidentified.append(kind)
                continue
            if self._sha256(path) != artifact.sha256:
                corrupted.append(kind)

        if missing:
            raise WorkflowError(f"Missing required outputs after readback: {missing}")
        if unidentified:
            raise WorkflowError(f"Required output checksum missing: {unidentified}")
        if corrupted:
            raise WorkflowError(f"Required output checksum mismatch: {corrupted}")
        self._validate_final_acceptance_evidence(state)
        if state.stage != Stage.FINAL_AUDIT:
            raise WorkflowError("Completion is only legal from FINAL_AUDIT")

    def complete(self, state: WritingState) -> WritingState:
        self.assert_can_complete(state)
        return self.transition(state, Stage.COMPLETE, reason="All mandatory gates, acceptance evidence and required outputs passed")
