import ast
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from financial_writing_agent import runtime_service as runtime
from financial_writing_agent.models import GateStatus, Stage, TaskContract, WritingState
from financial_writing_agent.store import SQLiteStateStore, StateConflictError

ROOT = Path(__file__).resolve().parents[1]


def _state(task_id: str, *, stage: Stage, updated_at: datetime | None = None) -> WritingState:
    return WritingState(
        contract=TaskContract(task_id=task_id, prompt=f"task {task_id}"),
        stage=stage,
        updated_at=updated_at or datetime.now(timezone.utc),
    )


def test_stale_owner_native_writer_cannot_overwrite_newer_checkpoint(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    original = _state("cas-task", stage=Stage.RESEARCH)
    store.save(original)
    assert original.checkpoint_version == 1

    writer_a = store.load("cas-task")
    writer_b = store.load("cas-task")
    assert writer_a is not None and writer_b is not None
    assert writer_a.checkpoint_version == writer_b.checkpoint_version == 1

    writer_a.add_trace("WRITER_A", "first writer wins")
    store.save(writer_a)
    assert writer_a.checkpoint_version == 2

    writer_b.add_trace("WRITER_B", "stale overwrite attempt")
    with pytest.raises(StateConflictError, match="stale state write"):
        store.save(writer_b)

    persisted = store.load("cas-task")
    assert persisted is not None
    assert persisted.checkpoint_version == 2
    assert any(event.event == "WRITER_A" for event in persisted.trace)
    assert not any(event.event == "WRITER_B" for event in persisted.trace)


def test_legacy_sqlite_rows_gain_checkpoint_version_without_data_rebuild(tmp_path):
    db = tmp_path / "legacy.db"
    legacy = _state("legacy-task", stage=Stage.RESEARCH)
    payload = legacy.model_dump(mode="json")
    payload.pop("checkpoint_version", None)

    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE runs (task_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO runs(task_id,payload,updated_at) VALUES(?,?,?)",
            (legacy.contract.task_id, json.dumps(payload), legacy.updated_at.isoformat()),
        )

    store = SQLiteStateStore(db)
    loaded = store.load("legacy-task")
    assert loaded is not None
    assert loaded.stage == Stage.RESEARCH
    assert loaded.checkpoint_version == 1

    loaded.add_trace("MIGRATED", "legacy row remains writable")
    store.save(loaded)
    assert loaded.checkpoint_version == 2

    with sqlite3.connect(db) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(runs)")}
        version = conn.execute(
            "SELECT checkpoint_version FROM runs WHERE task_id='legacy-task'"
        ).fetchone()[0]
    assert "checkpoint_version" in columns
    assert version == 2


def test_recent_task_scan_is_not_shadowed_by_newer_clean_completions(tmp_path, monkeypatch):
    store = SQLiteStateStore(tmp_path / "state.db")
    base = datetime(2026, 10, 12, 3, 0, tzinfo=timezone.utc)

    # More than one runtime page of clean completions intentionally sits ahead of the
    # active task. LIMIT-before-filter would return no continuation candidate.
    for i in range(55):
        state = _state(
            f"complete-{i:02d}",
            stage=Stage.COMPLETE,
            updated_at=base - timedelta(seconds=i),
        )
        store.save(state)

    active = _state("active-after-clean-completions", stage=Stage.RESEARCH, updated_at=base - timedelta(hours=1))
    store.save(active)
    monkeypatch.setattr(runtime, "store", store)

    rows = runtime.list_recent_writing_tasks(limit=1, include_complete=False)
    assert [row["task_id"] for row in rows] == ["active-after-clean-completions"]
    assert rows[0]["status"] == "IN_PROGRESS"


def test_completed_task_with_open_maintenance_debt_remains_discoverable(tmp_path, monkeypatch):
    store = SQLiteStateStore(tmp_path / "state.db")
    state = _state("complete-with-debt", stage=Stage.COMPLETE)
    state.working["system_impact_signals"] = [
        {
            "signal_id": "impact-0001",
            "status": "PENDING_REVIEW",
            "signal_type": "WRITING_QUALITY_SYSTEM_IMPACT_REVIEW",
        }
    ]
    store.save(state)
    monkeypatch.setattr(runtime, "store", store)

    rows = runtime.list_recent_writing_tasks(limit=10, include_complete=False)
    assert [row["task_id"] for row in rows] == ["complete-with-debt"]
    assert rows[0]["status"] == "COMPLETE"
    assert rows[0]["open_system_impact_count"] == 1
    assert "review_writing_system_impact" in rows[0]["next_action"]


def test_pending_revision_cleanup_is_reconciled_on_next_load_and_is_idempotent(tmp_path, monkeypatch):
    store = SQLiteStateStore(tmp_path / "state.db")
    state = _state("revision-crash", stage=Stage.RESEARCH)
    for gate in (
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
        "final_audit",
    ):
        state.set_gate(gate, GateStatus.PASS, ["stale evidence"])
    state.working["editorial_plan"] = {"stale": True}
    state.working["draft"] = {"stale": True}
    state.working["_pending_revision_cleanup"] = {
        "target": "RESEARCH",
        "reason": "simulated crash after revision transition",
    }
    store.save(state)
    monkeypatch.setattr(runtime, "store", store)

    recovered = runtime._load("revision-crash")
    assert recovered.stage == Stage.RESEARCH
    assert recovered.checkpoint_version == 2
    assert "_pending_revision_cleanup" not in recovered.working
    assert "editorial_plan" not in recovered.working
    assert "draft" not in recovered.working
    assert all(record.status == GateStatus.NOT_RUN for record in recovered.gates.values())
    assert any(event.event == "RECOVERY_RECONCILED" for event in recovered.trace)

    second = runtime._load("revision-crash")
    assert second.checkpoint_version == 2
    assert sum(event.event == "RECOVERY_RECONCILED" for event in second.trace) == 1


def test_pending_revision_cleanup_fails_closed_on_stage_mismatch(tmp_path, monkeypatch):
    store = SQLiteStateStore(tmp_path / "state.db")
    state = _state("revision-corrupt", stage=Stage.EDITORIAL)
    state.working["_pending_revision_cleanup"] = {
        "target": "RESEARCH",
        "reason": "corrupt recovery marker",
    }
    store.save(state)
    monkeypatch.setattr(runtime, "store", store)

    with pytest.raises(ValueError, match="pending revision cleanup stage mismatch"):
        runtime._load("revision-corrupt")


def test_plugin_recent_task_tool_delegates_to_runtime_single_filter():
    source = (ROOT / "financial_writing_agent/plugin_server.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    func = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "list_recent_writing_tasks")

    calls_runtime = False
    calls_store_directly = False
    for node in ast.walk(func):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "impl" and node.func.attr == "list_recent_writing_tasks":
            calls_runtime = True
        if (
            node.func.attr == "list_recent"
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "impl"
            and node.func.value.attr == "store"
        ):
            calls_store_directly = True

    assert calls_runtime is True
    assert calls_store_directly is False
