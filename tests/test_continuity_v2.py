from __future__ import annotations

from financial_writing_agent.continuity import is_bare_inherit_candidate, list_resumable_states
from financial_writing_agent.mcp_contracts import WritingTaskSummary
from financial_writing_agent.models import ResumeVisibility, Stage, TaskClass, TaskContract, WritingState
from financial_writing_agent.routing import build_task_contract
from financial_writing_agent.store import SQLiteStateStore


def test_public_task_builder_marks_new_user_work_resumable():
    contract = build_task_contract(prompt="写一篇测试文章", visuals_enabled=False)
    assert contract.task_class == TaskClass.USER
    assert contract.resume_eligible is True
    assert contract.resume_visibility == ResumeVisibility.DEFAULT
    assert contract.contract_version == "2.0"
    assert contract.runtime_version == "0.2.1"


def test_legacy_checkpoint_without_continuity_fields_fails_closed():
    state = WritingState(contract=TaskContract(prompt="legacy task"))
    payload = state.model_dump(mode="json")
    for key in [
        "task_class",
        "resume_eligible",
        "resume_visibility",
        "contract_version",
        "runtime_version",
        "skill_version",
    ]:
        payload["contract"].pop(key, None)

    loaded = WritingState.model_validate(payload)
    assert loaded.contract.task_class == TaskClass.MIGRATION
    assert loaded.contract.resume_eligible is False
    assert loaded.contract.resume_visibility == ResumeVisibility.EXPLICIT_ONLY
    assert loaded.contract.contract_version == "legacy-unclassified"
    assert is_bare_inherit_candidate(loaded) is False


def test_safe_recent_discovery_excludes_fixture_migration_hidden_and_complete(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")

    user = WritingState(contract=build_task_contract(prompt="user", visuals_enabled=False), stage=Stage.RESEARCH)
    store.save(user)

    fixture = WritingState(
        contract=build_task_contract(
            prompt="fixture",
            visuals_enabled=False,
            task_class=TaskClass.FIXTURE,
        ),
        stage=Stage.RESEARCH,
    )
    store.save(fixture)

    legacy = WritingState(contract=TaskContract(prompt="legacy"), stage=Stage.EDITORIAL)
    store.save(legacy)

    hidden_user = WritingState(
        contract=build_task_contract(
            prompt="hidden user",
            visuals_enabled=False,
            task_class=TaskClass.USER,
            resume_eligible=True,
            resume_visibility=ResumeVisibility.HIDDEN,
        ),
        stage=Stage.RESEARCH,
    )
    store.save(hidden_user)

    complete = WritingState(contract=build_task_contract(prompt="complete", visuals_enabled=False), stage=Stage.COMPLETE)
    store.save(complete)

    resumable = list_resumable_states(store, limit=20)
    assert [state.contract.task_id for state in resumable] == [user.contract.task_id]

    with_complete = list_resumable_states(store, limit=20, include_complete=True)
    assert {state.contract.task_id for state in with_complete} == {user.contract.task_id, complete.contract.task_id}
    assert fixture.contract.task_id not in {state.contract.task_id for state in with_complete}
    assert legacy.contract.task_id not in {state.contract.task_id for state in with_complete}
    assert hidden_user.contract.task_id not in {state.contract.task_id for state in with_complete}


def test_public_summary_schema_accepts_broad_derivation_and_continuity_metadata():
    summary = WritingTaskSummary.model_validate(
        {
            "task_id": "task-1",
            "status": "IN_PROGRESS",
            "current_stage": "BROAD_DERIVATION",
            "prompt_preview": "x",
            "effective_time_boundary": "2026-10-09T00:00:00+00:00",
            "content_mode": "FORMAL_ARTICLE",
            "distribution_mode": "DUAL",
            "delivery_channel": "WORD_FILE_ONLY",
            "visuals_enabled": False,
            "required_outputs": ["AUDIT_DOCX", "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"],
            "gate_status": {},
            "updated_at": "2026-10-09T00:00:00+00:00",
            "next_action": "derive broad",
            "task_class": "USER",
            "resume_eligible": True,
            "resume_visibility": "DEFAULT",
            "contract_version": "2.0",
            "runtime_version": "0.2.1",
        }
    )
    assert summary.current_stage == "BROAD_DERIVATION"
    assert summary.task_class == "USER"
