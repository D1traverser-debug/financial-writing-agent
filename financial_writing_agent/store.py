from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import WritingState


class StateConflictError(RuntimeError):
    """Raised when an owner-native writer attempts to save a stale WritingState."""


class SQLiteStateStore:
    """SQLite reference store with optimistic versioned writes.

    The persistence boundary protects two cross-action invariants:

    1. material corrective/negative learning evidence cannot be committed without its
       immediate system-impact review obligation;
    2. a writer may update only the checkpoint version it actually loaded, so a stale
       session cannot silently overwrite a newer task checkpoint.

    The store performs an additive legacy-schema migration for the internal
    ``checkpoint_version`` column. The database version is authoritative on read even
    when an older serialized payload predates the model field.
    """

    def __init__(self, path: str | Path = "financial_writing_state.db"):
        self.path = str(path)

    def _connect(self) -> sqlite3.Connection:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS runs ("
            "task_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL, "
            "checkpoint_version INTEGER NOT NULL DEFAULT 1)"
        )
        columns = {row[1] for row in conn.execute("PRAGMA table_info(runs)").fetchall()}
        if "checkpoint_version" not in columns:
            conn.execute("ALTER TABLE runs ADD COLUMN checkpoint_version INTEGER NOT NULL DEFAULT 1")
        return conn

    @staticmethod
    def _reconcile_persistence_invariants(state: WritingState) -> None:
        samples = state.working.get("learning_samples") or []
        if not samples:
            return
        latest = samples[-1]
        if latest.get("sample_type") not in {"USER_EDIT", "USER_FEEDBACK", "USER_REJECTION"}:
            return
        if latest.get("system_impact_signal_id"):
            return
        # Local import avoids making system-impact construction part of store import time.
        # The helper mutates only the in-memory WritingState that is about to be committed.
        from .system_impact import ensure_system_impact_signal_for_latest_sample

        signal = ensure_system_impact_signal_for_latest_sample(state)
        if signal is None or signal.get("status") != "PENDING_REVIEW":
            raise ValueError("material negative feedback cannot persist without PENDING_REVIEW system-impact obligation")

    @staticmethod
    def _payload_for_version(state: WritingState, version: int) -> str:
        snapshot = state.model_copy(deep=True)
        snapshot.checkpoint_version = version
        return snapshot.model_dump_json()

    @staticmethod
    def _restore(payload: str, version: int) -> WritingState:
        state = WritingState.model_validate_json(payload)
        state.checkpoint_version = int(version)
        return state

    def save(self, state: WritingState) -> None:
        self._reconcile_persistence_invariants(state)
        task_id = state.contract.task_id
        expected = int(state.checkpoint_version)
        next_version = expected + 1
        payload = self._payload_for_version(state, next_version)

        with self._connect() as conn:
            if expected == 0:
                try:
                    conn.execute(
                        "INSERT INTO runs(task_id,payload,updated_at,checkpoint_version) VALUES(?,?,?,?)",
                        (task_id, payload, state.updated_at.isoformat(), next_version),
                    )
                except sqlite3.IntegrityError as exc:
                    current = conn.execute(
                        "SELECT checkpoint_version FROM runs WHERE task_id=?", (task_id,)
                    ).fetchone()
                    current_version = int(current[0]) if current else -1
                    raise StateConflictError(
                        f"stale state create for {task_id}: expected new task version 0, current={current_version}"
                    ) from exc
            else:
                cursor = conn.execute(
                    "UPDATE runs SET payload=?, updated_at=?, checkpoint_version=? "
                    "WHERE task_id=? AND checkpoint_version=?",
                    (payload, state.updated_at.isoformat(), next_version, task_id, expected),
                )
                if cursor.rowcount != 1:
                    current = conn.execute(
                        "SELECT checkpoint_version FROM runs WHERE task_id=?", (task_id,)
                    ).fetchone()
                    current_version = int(current[0]) if current else -1
                    raise StateConflictError(
                        f"stale state write for {task_id}: expected checkpoint_version={expected}, current={current_version}"
                    )

        state.checkpoint_version = next_version

    def load(self, task_id: str) -> WritingState | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload, checkpoint_version FROM runs WHERE task_id=?", (task_id,)
            ).fetchone()
        return self._restore(row[0], row[1]) if row else None

    def list_recent(self, limit: int = 10, *, offset: int = 0) -> list[WritingState]:
        safe_limit = max(1, min(int(limit), 100))
        safe_offset = max(0, int(offset))
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT payload, checkpoint_version FROM runs "
                "ORDER BY updated_at DESC, task_id DESC LIMIT ? OFFSET ?",
                (safe_limit, safe_offset),
            ).fetchall()
        return [self._restore(payload, version) for payload, version in rows]
