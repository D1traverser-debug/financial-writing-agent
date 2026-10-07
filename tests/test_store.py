import sqlite3

import pytest

from financial_writing_agent.models import GateStatus, TaskContract, WritingState
from financial_writing_agent.store import SQLiteStateStore, StateConflictError


def test_stale_checkpoint_write_is_rejected_without_lost_update(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    original = WritingState(contract=TaskContract(prompt="concurrency"))
    store.save(original)
    assert original.checkpoint_version == 1

    first = store.load(original.contract.task_id)
    second = store.load(original.contract.task_id)
    assert first is not None and second is not None
    assert first.checkpoint_version == second.checkpoint_version == 1

    first.set_gate("first_writer", GateStatus.PASS, ["winner"])
    store.save(first)
    assert first.checkpoint_version == 2

    second.set_gate("second_writer", GateStatus.PASS, ["stale"])
    with pytest.raises(StateConflictError, match="stale checkpoint"):
        store.save(second)
    assert second.checkpoint_version == 1

    latest = store.load(original.contract.task_id)
    assert latest is not None
    assert latest.checkpoint_version == 2
    assert latest.gates["first_writer"].status == GateStatus.PASS
    assert "second_writer" not in latest.gates


def test_legacy_three_column_store_migrates_without_losing_state(tmp_path):
    db = tmp_path / "legacy.db"
    legacy = WritingState(contract=TaskContract(prompt="legacy checkpoint"))
    payload = legacy.model_dump_json(exclude={"checkpoint_version"})

    conn = sqlite3.connect(db)
    try:
        conn.execute(
            "CREATE TABLE runs (task_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO runs(task_id,payload,updated_at) VALUES(?,?,?)",
            (legacy.contract.task_id, payload, legacy.updated_at.isoformat()),
        )
        conn.commit()
    finally:
        conn.close()

    store = SQLiteStateStore(db)
    loaded = store.load(legacy.contract.task_id)
    assert loaded is not None
    assert loaded.contract.prompt == "legacy checkpoint"
    assert loaded.checkpoint_version == 0

    loaded.set_gate("migrated", GateStatus.PASS, ["legacy row upgraded"])
    store.save(loaded)
    assert loaded.checkpoint_version == 1

    conn = sqlite3.connect(db)
    try:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(runs)").fetchall()}
        version = conn.execute(
            "SELECT version FROM runs WHERE task_id=?", (legacy.contract.task_id,)
        ).fetchone()[0]
    finally:
        conn.close()

    assert "version" in columns
    assert version == 1
    reloaded = store.load(legacy.contract.task_id)
    assert reloaded is not None
    assert reloaded.checkpoint_version == 1
    assert reloaded.gates["migrated"].status == GateStatus.PASS
