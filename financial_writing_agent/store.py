from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import WritingState


class StateConflictError(RuntimeError):
    """Raised when a stale WritingState attempts to overwrite a newer checkpoint."""


class SQLiteStateStore:
    """SQLite reference store with atomic, version-checked checkpoint writes."""

    def __init__(self, path: str | Path = "financial_writing_state.db"):
        self.path = str(path)

    def _connect(self) -> sqlite3.Connection:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=30.0)
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS runs ("
            "task_id TEXT PRIMARY KEY, "
            "payload TEXT NOT NULL, "
            "updated_at TEXT NOT NULL, "
            "version INTEGER NOT NULL DEFAULT 0"
            ")"
        )
        columns = {row[1] for row in conn.execute("PRAGMA table_info(runs)").fetchall()}
        if "version" not in columns:
            try:
                conn.execute("ALTER TABLE runs ADD COLUMN version INTEGER NOT NULL DEFAULT 0")
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    conn.close()
                    raise
        conn.commit()
        return conn

    def save(self, state: WritingState) -> None:
        previous_version = state.checkpoint_version
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT version FROM runs WHERE task_id=?",
                (state.contract.task_id,),
            ).fetchone()

            if row is None:
                if previous_version != 0:
                    raise StateConflictError(
                        f"checkpoint disappeared or was replaced for {state.contract.task_id}: "
                        f"state_version={previous_version}, stored_version=missing"
                    )
                new_version = 1
                state.checkpoint_version = new_version
                payload = state.model_dump_json()
                conn.execute(
                    "INSERT INTO runs(task_id,payload,updated_at,version) VALUES(?,?,?,?)",
                    (state.contract.task_id, payload, state.updated_at.isoformat(), new_version),
                )
            else:
                stored_version = int(row[0])
                if previous_version != stored_version:
                    raise StateConflictError(
                        f"stale checkpoint for {state.contract.task_id}: "
                        f"state_version={previous_version}, stored_version={stored_version}"
                    )
                new_version = stored_version + 1
                state.checkpoint_version = new_version
                payload = state.model_dump_json()
                cursor = conn.execute(
                    "UPDATE runs SET payload=?, updated_at=?, version=? "
                    "WHERE task_id=? AND version=?",
                    (
                        payload,
                        state.updated_at.isoformat(),
                        new_version,
                        state.contract.task_id,
                        stored_version,
                    ),
                )
                if cursor.rowcount != 1:
                    raise StateConflictError(
                        f"checkpoint changed during save for {state.contract.task_id}"
                    )
            conn.commit()
        except Exception:
            conn.rollback()
            state.checkpoint_version = previous_version
            raise
        finally:
            conn.close()

    def load(self, task_id: str) -> WritingState | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT payload, version FROM runs WHERE task_id=?",
                (task_id,),
            ).fetchone()
        finally:
            conn.close()
        if not row:
            return None
        state = WritingState.model_validate_json(row[0])
        state.checkpoint_version = int(row[1])
        return state

    def list_recent(self, limit: int = 10) -> list[WritingState]:
        safe_limit = max(1, min(int(limit), 100))
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT payload, version FROM runs ORDER BY updated_at DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()
        finally:
            conn.close()
        states: list[WritingState] = []
        for payload, version in rows:
            state = WritingState.model_validate_json(payload)
            state.checkpoint_version = int(version)
            states.append(state)
        return states
