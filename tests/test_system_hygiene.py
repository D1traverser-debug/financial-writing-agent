import json
import tomllib
from pathlib import Path

from financial_writing_agent.models import GateStatus, Stage, TaskContract, WritingState
from financial_writing_agent.runtime_service import _next_action

ROOT = Path(__file__).resolve().parents[1]


def test_agent_architecture_and_continuity_recovery_match_current_owner_contract():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    agent_manifest = json.loads((ROOT / "continuity/AGENT_MANIFEST.json").read_text(encoding="utf-8"))
    adapter = json.loads((ROOT / "continuity/UNIVERSAL_PROTOCOL_ADAPTER.json").read_text(encoding="utf-8"))
    capabilities = json.loads((ROOT / "continuity/EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "continuity/tasks/financial-writing-main/TASK_MANIFEST.json").read_text(encoding="utf-8"))
    handoff = (ROOT / "continuity/tasks/financial-writing-main/HANDOFF.md").read_text(encoding="utf-8")
    index = (ROOT / "continuity/TASK_INDEX.md").read_text(encoding="utf-8")

    assert project["project"]["version"] == "0.8.1"
    assert agent_manifest["owner"] == adapter["owner"] == capabilities["owner"] == "FINANCIAL_WRITING_AGENT_RUNTIME"
    assert agent_manifest["skill"]["role"] == "ROUTER"
    assert agent_manifest["skill"]["entrypoint"] == "skills/financial-writing-agent/SKILL.md"
    assert "financial_writing_agent/plugin_server.py" in agent_manifest["runtime"]["entrypoints"]
    assert "financial_writing_agent/controller.py" in agent_manifest["workflow"]["transition_guard_refs"]
    assert "financial_writing_agent/engine.py" in agent_manifest["workflow"]["transition_guard_refs"]
    assert adapter["owner_contract_version"] == project["project"]["version"]
    assert adapter["execution_capability_profile_version"] == capabilities["profile_version"] == 9
    assert adapter["methodology_assurance"]["owner_execution_hardening"]["public_mcp_tool_count"] == 19
    assert manifest["skill_version"] == "FINANCIAL_WRITING_AGENT_V0_8"
    assert "V0_8_1" in manifest["runtime_version"]
    assert "Financial Writing Agent v0.8.1" in handoff
    assert "receipt contract `1.3`" in handoff
    assert "review_writing_system_impact" in handoff
    assert "run_semantic_audit_stage" in handoff
    assert "v0.8" in index


def test_audit_next_actions_route_pass_through_owner_gateway():
    state = WritingState(contract=TaskContract(prompt="audit routing"))

    state.stage = Stage.RESEARCH_AUDIT
    action = _next_action(state)
    assert "run_semantic_audit_stage" in action
    assert "REVISE/FAIL-only" in action

    state.stage = Stage.EDITORIAL_AUDIT
    action = _next_action(state)
    assert "run_semantic_audit_stage" in action
    assert "submit_*audit is REVISE/FAIL-only" in action

    state.stage = Stage.FINAL_AUDIT
    action = _next_action(state)
    assert "record knowledge writeback" in action
    assert "run_semantic_audit_stage" in action
    state.set_gate("knowledge_sync", GateStatus.N_A, ["test boundary"])
    action = _next_action(state)
    assert action.startswith("call run_semantic_audit_stage")


def test_gate_invalidation_clears_gate_owned_working_payload():
    state = WritingState(contract=TaskContract(prompt="stale payload"))
    state.working["research_audit"] = {"stale": True}
    state.set_gate("research_audit", GateStatus.PASS, ["old proof"])
    state.set_gate("research_audit", GateStatus.NOT_RUN, [], "upstream revision")

    assert state.gates["research_audit"].status == GateStatus.NOT_RUN
    assert "research_audit" not in state.working


def test_semantic_proof_requires_ordered_executor_start_then_end():
    state = WritingState(contract=TaskContract(task_id="proof-order", prompt="proof order"))
    state.stage = Stage.RESEARCH_AUDIT
    state.add_trace("STAGE_ENTER", "audit entered")
    state.working["research_audit"] = {
        "status": "PASS",
        "evidence": ["proof"],
        "provenance": {
            "assurance": "INDEPENDENT_EXECUTOR",
            "reviewer_identity": "Research Auditor",
            "author_identity": "Researcher",
            "execution_ref": "proof-order:RESEARCH_AUDIT:judge-1",
        },
    }
    state.set_gate("research_audit", GateStatus.PASS, ["proof"])

    state.add_trace("EXECUTOR_END", "out of order")
    state.add_trace("EXECUTOR_START", "late start")
    assert state.semantic_gate_proof_valid("research_audit") is False

    state.add_trace("EXECUTOR_END", "ordered end")
    assert state.semantic_gate_proof_valid("research_audit") is True


def test_test_mocks_do_not_live_in_production_package():
    assert not (ROOT / "financial_writing_agent/adapters/mock.py").exists()
