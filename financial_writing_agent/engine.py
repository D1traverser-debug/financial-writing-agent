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
    Stage.DRAFT: {Stage.EDITORIAL_AUDIT, Stage.BLOCKED},
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
    Stage.BLOCKED: {Stage.INTAKE, Stage.RESEARCH, Stage.EDITORIAL, Stage.DELIVERY, Stage.FINAL_AUDIT},
}


REVISION_GATES: dict[Stage, tuple[str, ...]] = {
    Stage.RESEARCH: (
        "research_output",
        "research_audit",
        "editorial_plan",
        "acceptance_contract",
        "title_audit",
        "draft_output",
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
        "style_audit",
        "editorial_audit",
        "visual_assets",
        "delivery_output",
        "mechanical_audit",
        "final_audit",
    ),
    Stage.DRAFT: (
        "draft_output",
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


FORMAL_FINAL_CRITERIA = (
    "selected_title",
    "independent_lead",
    "h1_structure",
    "side_focus",
    "company_selection_basis",
    "headline_anchor",
    "opening_payoff",
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


class WritingEngine:
    def __init__(self, store: SQLiteStateStore):
        self.store = store

    def start(self, contract: TaskContract) -> WritingState:
        state = WritingState(contract=contract)
        state.add_trace("RUNTIME_STARTED", "TaskContract initialized before source retrieval or drafting")
        state.set_gate("runtime_initialized", GateStatus.PASS, ["TaskContract exists", "State store active"])
        state.set_gate("knowledge_sync", GateStatus.NOT_RUN, [], "Explicit PASS/N_A writeback decision required before final completion")
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
            self.transition(state, Stage.BLOCKED, reason=reason)
        self.store.save(state)
        return state

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
        return required

    @staticmethod
    def _required_final_evidence_keys(state: WritingState) -> set[str]:
        keys = {"GLOBAL.evidence_boundary", "GLOBAL.required_outputs"}
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
        for mode in modes:
            keys.update(f"{mode}.{criterion}" for criterion in FORMAL_FINAL_CRITERIA)
            if state.contract.visuals_enabled:
                keys.add(f"{mode}.visual_alignment")
        if state.contract.distribution_mode == DistributionMode.DUAL:
            keys.add("DUAL.cross_version_consistency")
        return keys

    @classmethod
    def _validate_final_acceptance_evidence(cls, state: WritingState) -> None:
        final_audit = state.working.get("final_audit") or {}
        entries = final_audit.get("acceptance_evidence") or []
        provided: dict[str, str] = {}
        for entry in entries:
            if not isinstance(entry, str) or ":" not in entry:
                continue
            key, evidence = entry.split(":", 1)
            if key.strip() and evidence.strip():
                provided[key.strip()] = evidence.strip()
        required = cls._required_final_evidence_keys(state)
        missing = sorted(required - set(provided))
        if missing:
            raise WorkflowError(f"Final acceptance evidence missing required criterion(s): {missing}")

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
            if artifact.sha256 and self._sha256(path) != artifact.sha256:
                corrupted.append(kind)

        if missing:
            raise WorkflowError(f"Missing required outputs after readback: {missing}")
        if corrupted:
            raise WorkflowError(f"Required output checksum mismatch: {corrupted}")
        self._validate_final_acceptance_evidence(state)
        if state.stage != Stage.FINAL_AUDIT:
            raise WorkflowError("Completion is only legal from FINAL_AUDIT")

    def complete(self, state: WritingState) -> WritingState:
        self.assert_can_complete(state)
        return self.transition(state, Stage.COMPLETE, reason="All mandatory gates, acceptance evidence and required outputs passed")
