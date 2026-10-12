import ast
import json
from pathlib import Path

from financial_writing_agent.controller import WorkflowController
from financial_writing_agent.engine import ALLOWED_TRANSITIONS, WritingEngine
from financial_writing_agent.github_chat_guard import advance_state, build_initial_state
from financial_writing_agent.models import GateStatus, Stage, TaskContract
from financial_writing_agent.store import SQLiteStateStore
from financial_writing_agent.workflow_spec import (
    BUSINESS_STAGE_NAMES,
    LEGAL_TRANSITIONS,
    invalidated_gate_names_from,
    invalidated_stage_names_from,
    pass_target,
    revision_targets,
)

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_workflow_sequence_and_revision_contract():
    assert BUSINESS_STAGE_NAMES == (
        "INTAKE",
        "RESEARCH",
        "RESEARCH_AUDIT",
        "EDITORIAL",
        "TITLE",
        "DRAFT",
        "EDITORIAL_AUDIT",
        "DELIVERY",
        "MECHANICAL_AUDIT",
        "FINAL_AUDIT",
    )
    assert pass_target(Stage.FINAL_AUDIT) == Stage.COMPLETE
    assert revision_targets(Stage.RESEARCH_AUDIT) == frozenset({Stage.RESEARCH})
    assert revision_targets(Stage.EDITORIAL_AUDIT) == frozenset(
        {Stage.RESEARCH, Stage.EDITORIAL, Stage.TITLE, Stage.DRAFT}
    )
    assert revision_targets(Stage.FINAL_AUDIT) == frozenset(
        {Stage.RESEARCH, Stage.EDITORIAL, Stage.TITLE, Stage.DRAFT, Stage.DELIVERY}
    )
    assert Stage.DRAFT in LEGAL_TRANSITIONS[Stage.DRAFT]


def test_engine_transition_surface_is_derived_from_canonical_graph():
    assert {stage: frozenset(targets) for stage, targets in ALLOWED_TRANSITIONS.items()} == LEGAL_TRANSITIONS


def test_owner_native_draft_revision_loop_is_now_legal(tmp_path):
    engine = WritingEngine(SQLiteStateStore(tmp_path / "state.db"))
    controller = WorkflowController(engine)
    state = engine.start(TaskContract(prompt="draft revise parity"))
    state.stage = Stage.DRAFT
    state.set_gate("draft_output", GateStatus.REVISE, ["deterministic draft guard requested rewrite"])
    revised = controller.advance(state)
    assert revised.stage == Stage.DRAFT
    assert any(event.event == "STAGE_ENTER" and event.stage == Stage.DRAFT for event in revised.trace)


def test_dependency_invalidation_is_derived_from_stage_order():
    assert invalidated_stage_names_from("RESEARCH") == BUSINESS_STAGE_NAMES[1:]
    assert invalidated_stage_names_from("EDITORIAL") == BUSINESS_STAGE_NAMES[3:]
    assert invalidated_stage_names_from("TITLE") == BUSINESS_STAGE_NAMES[4:]
    assert invalidated_stage_names_from("DRAFT") == BUSINESS_STAGE_NAMES[5:]
    assert invalidated_stage_names_from("DELIVERY") == BUSINESS_STAGE_NAMES[7:]
    assert invalidated_gate_names_from(Stage.RESEARCH) == (
        "research_output", "research_audit", "editorial_plan", "title_audit", "draft_output",
        "hook_audit", "style_audit", "editorial_audit", "delivery_output", "mechanical_audit", "final_audit",
    )
    assert invalidated_gate_names_from(Stage.DRAFT) == (
        "draft_output", "hook_audit", "style_audit", "editorial_audit",
        "delivery_output", "mechanical_audit", "final_audit",
    )


def test_runtime_service_consumes_kernel_instead_of_maintaining_gate_route_copies():
    source = (ROOT / "financial_writing_agent/runtime_service.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    imports = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "workflow_spec"
        for alias in node.names
    }
    assert {"invalidated_gate_names_from", "revision_targets"}.issubset(imports)

    apply_cleanup = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_apply_revision_cleanup")
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "invalidated_gate_names_from"
        for node in ast.walk(apply_cleanup)
    )

    stage_change = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_invalidate_for_stage_change")
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "invalidated_gate_names_from"
        for node in ast.walk(stage_change)
    )

    for function_name, expected_stage in (
        ("submit_research_audit", Stage.RESEARCH_AUDIT),
        ("submit_editorial_audit", Stage.EDITORIAL_AUDIT),
        ("submit_final_audit", Stage.FINAL_AUDIT),
    ):
        func = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == function_name)
        calls = [
            node for node in ast.walk(func)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_canonical_revision_target_names"
        ]
        assert len(calls) == 1
        assert isinstance(calls[0].args[0], ast.Attribute)
        assert calls[0].args[0].attr == expected_stage.name

    assert '_validate_revision_target(payload, {"RESEARCH"}' not in source
    assert '_validate_revision_target(payload, {"RESEARCH", "EDITORIAL", "TITLE", "DRAFT"}' not in source


def test_github_chat_contract_points_to_kernel_instead_of_copying_stage_order():
    contract = json.loads((ROOT / "continuity/GITHUB_CHAT_EXECUTION.json").read_text(encoding="utf-8"))
    workflow = contract["workflow"]
    assert contract["schema_version"] == "1.2"
    assert contract["authority"]["canonical_workflow_spec"] == "financial_writing_agent/workflow_spec.py"
    assert workflow["canonical_stage_order_symbol"] == "BUSINESS_STAGE_ORDER"
    assert workflow["canonical_revision_targets_symbol"] == "REVISION_TARGETS"
    assert workflow["canonical_invalidation_symbol"] == "invalidated_stages_from"
    assert "stage_order" not in workflow


def test_github_chat_guard_follows_canonical_initial_forward_edges():
    state = build_initial_state(
        task_id="workflow-parity", prompt="test", distribution_mode="FINANCE_DEEP", source_refs=[], executor_identity="chat-session:test"
    )
    assert state["current_stage"] == "INTAKE"
    state = advance_state(state, previous_state_blob_sha="state-0", executor_identity="chat-session:test")
    assert state["current_stage"] == pass_target(Stage.INTAKE).value
    state = advance_state(
        state,
        previous_state_blob_sha="state-1",
        executor_identity="chat-session:test",
        artifact_key="RESEARCH",
        artifact_path="workspaces/articles/workflow-parity/stages/RESEARCH.json",
        artifact_blob_sha="research-blob",
    )
    assert state["current_stage"] == pass_target(Stage.RESEARCH).value


def test_no_parallel_workflow_tables_are_reintroduced_outside_kernel():
    forbidden_assignments = {"STAGE_ORDER", "REGULAR_FORWARD", "REVIEW_ROUTES", "PASS_TARGET", "REVISION_TARGETS"}
    offenders: list[str] = []
    for path in (ROOT / "financial_writing_agent").rglob("*.py"):
        if path.name == "workflow_spec.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assigned: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        assigned.add(target.id)
        if assigned & forbidden_assignments:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_chat_guard_no_longer_owns_a_second_route_table():
    source = (ROOT / "financial_writing_agent/github_chat_guard.py").read_text(encoding="utf-8")
    assert "STAGE_ORDER =" not in source
    assert "REGULAR_FORWARD =" not in source
    assert "REVIEW_ROUTES =" not in source
    assert "from .workflow_spec import" in source


def test_manifest_declares_canonical_workflow_spec_as_transition_authority():
    manifest = json.loads((ROOT / "continuity/AGENT_MANIFEST.json").read_text(encoding="utf-8"))
    assert "financial_writing_agent/workflow_spec.py" in manifest["workflow"]["transition_guard_refs"]
