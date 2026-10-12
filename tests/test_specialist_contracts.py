import json
from pathlib import Path

import pytest

from financial_writing_agent.adapters.openai_agents import OpenAIStageExecutor, _specialist_instructions, _state_context
from financial_writing_agent.models import Artifact, ArtifactKind, GateStatus, Stage, TaskContract, WritingState
from financial_writing_agent.schemas import GateDecision
from financial_writing_agent.specialist_contracts import SPECIALIST_CONTRACTS, specialist_contract

ROOT = Path(__file__).resolve().parents[1]


def _state(stage: Stage) -> WritingState:
    state = WritingState(contract=TaskContract(task_id="specialist-test", prompt="test specialist boundaries"), stage=stage)
    state.working.update(
        {
            "research": {"visible": "research"},
            "research_audit": {"visible": "research_audit"},
            "editorial_plan": {"visible": "editorial"},
            "headlines": {"visible": "headlines"},
            "draft": {"visible": "draft"},
            "hook_audit": {"visible": "hook"},
            "style_audit": {"visible": "style"},
            "editorial_audit": {"visible": "editorial_audit"},
            "template_signal_report": {"visible": "template"},
            "learning_samples": [{"secret": "not specialist input"}],
            "system_impact_signals": [{"secret": "maintenance plane"}],
            "methodology_profile_runs": [{"secret": "methodology plane"}],
            "knowledge_writeback_refs": ["knowledge://receipt"],
            "knowledge_writeback_notes": ["done"],
            "render_manifest": {"FINANCE_DEEP_DOCX": ["page-1.png"]},
        }
    )
    for name in (
        "runtime_initialized",
        "research_output",
        "research_audit",
        "editorial_plan",
        "title_audit",
        "draft_output",
        "hook_audit",
        "style_audit",
        "editorial_audit",
        "delivery_output",
        "mechanical_audit",
        "knowledge_sync",
    ):
        state.set_gate(name, GateStatus.PASS, [name])
    state.artifacts[ArtifactKind.FINANCE_DEEP_DOCX] = Artifact(
        kind=ArtifactKind.FINANCE_DEEP_DOCX,
        path="/private/runtime/task/FINANCE_DEEP.docx",
        exists=True,
        sha256="a" * 64,
    )
    return state


def test_specialist_contracts_cover_every_model_role_with_typed_outputs_and_forbidden_actions():
    assert set(SPECIALIST_CONTRACTS) == {
        "researcher",
        "research_auditor",
        "editorial_architect",
        "headline_engine",
        "writer",
        "reader_funnel_judge",
        "authorial_prose_judge",
        "general_editorial_judge",
        "final_auditor",
    }
    for specialist_id, contract in SPECIALIST_CONTRACTS.items():
        assert contract.specialist_id == specialist_id
        assert contract.output_schema
        assert contract.reference_names
        assert contract.forbidden_actions
        for ref in contract.reference_names:
            assert (ROOT / "references" / ref).is_file(), (specialist_id, ref)

    assert {sid for sid, c in SPECIALIST_CONTRACTS.items() if c.web_access} == {
        "researcher",
        "research_auditor",
        "headline_engine",
        "reader_funnel_judge",
    }
    assert specialist_contract("writer").web_access is False
    assert specialist_contract("final_auditor").web_access is False
    assert specialist_contract("final_auditor").artifact_metadata_access is True
    assert all(
        not c.artifact_metadata_access
        for sid, c in SPECIALIST_CONTRACTS.items()
        if sid != "final_auditor"
    )


def test_writer_context_is_least_privilege_not_entire_writing_state():
    payload = json.loads(_state_context(_state(Stage.DRAFT), "writer"))
    assert set(payload["working"]) == {"research", "editorial_plan", "headlines"}
    assert set(payload["gates"]) == {"research_audit", "editorial_plan", "title_audit"}
    assert payload["artifacts"] == {}
    for forbidden in ("hook_audit", "style_audit", "learning_samples", "system_impact_signals", "methodology_profile_runs"):
        assert forbidden not in payload["working"]


def test_each_editorial_audit_specialist_gets_only_its_declared_slice():
    state = _state(Stage.EDITORIAL_AUDIT)
    hook = json.loads(_state_context(state, "reader_funnel_judge"))
    prose = json.loads(_state_context(state, "authorial_prose_judge"))
    general = json.loads(_state_context(state, "general_editorial_judge"))

    assert set(hook["working"]) == {"research", "editorial_plan", "headlines", "draft"}
    assert "template_signal_report" not in hook["working"]
    assert set(prose["working"]) == {"research", "editorial_plan", "headlines", "draft", "template_signal_report"}
    assert "hook_audit" not in prose["working"]
    assert {"hook_audit", "style_audit"}.issubset(general["working"])
    assert "learning_samples" not in general["working"]
    assert "system_impact_signals" not in general["working"]


def test_final_auditor_gets_safe_artifact_identity_but_no_server_local_path():
    payload = json.loads(_state_context(_state(Stage.FINAL_AUDIT), "final_auditor"))
    artifact = payload["artifacts"]["FINANCE_DEEP_DOCX"]
    assert artifact == {
        "file_name": "FINANCE_DEEP.docx",
        "exists": True,
        "sha256": "a" * 64,
    }
    encoded = json.dumps(payload, ensure_ascii=False)
    assert "/private/runtime/task" not in encoded
    assert "FINANCE_DEEP.docx" in encoded
    assert "mechanical_audit" in payload["gates"]


def test_stage_and_output_contract_mismatches_fail_before_sdk_invocation():
    writer_state = _state(Stage.DRAFT)
    with pytest.raises(RuntimeError, match="context stage mismatch"):
        _state_context(writer_state, "researcher")

    executor = OpenAIStageExecutor(Stage.DRAFT)
    with pytest.raises(RuntimeError, match="specialist output mismatch"):
        executor._run(state=writer_state, specialist_id="writer", output_type=GateDecision)


def test_openai_adapter_no_longer_copies_domain_rule_paragraphs():
    source = (ROOT / "financial_writing_agent/adapters/openai_agents.py").read_text(encoding="utf-8")
    # These were representative shadow business rules previously hard-coded in the
    # adapter in addition to canonical references/schema/checks.
    forbidden_shadow_fragments = (
        "MATERIAL means omitting",
        "at least five genuinely distinct",
        "FINANCE_DEEP must discharge every completeness_obligation",
        "Use H1s as clear macro navigation",
        "Do not repeatedly stage the argument",
        "Reject a title pool that is mostly one rhetorical mold",
        "Audit the frozen draft against the exact nine-part rubric",
        "Reconfirm universe completeness, MATERIAL-company appearance",
    )
    for fragment in forbidden_shadow_fragments:
        assert fragment not in source
    assert "specialist_contract(" in source
    assert "projected_working" in source
    assert "projected_gates" in source
    assert "projected_artifacts" in source


def test_specialist_instructions_are_canonical_reference_plus_execution_boundary():
    instructions = _specialist_instructions("headline_engine")
    canonical_hooks = (ROOT / "references/hooks.md").read_text(encoding="utf-8")
    assert canonical_hooks in instructions
    assert "EXECUTION BOUNDARY (not a second business-rule source)" in instructions
    assert "Output schema: HeadlinePackage" in instructions
    assert "change durable business rules from one execution" in instructions
