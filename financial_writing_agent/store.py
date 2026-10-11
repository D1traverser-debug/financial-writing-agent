from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import WritingState


class SQLiteStateStore:
    """SQLite reference store with no filesystem writes at import/construction time.

    The persistence boundary also protects one cross-action invariant: if the newest
    learning sample is material corrective/negative feedback, it must not be committed
    without its system-impact review obligation. This closes the crash window between
    raw learning-sample capture and the higher-level plugin receipt path without turning
    persistence into a methodology attestation surface.
    """

    def __init__(self, path: str | Path = "financial_writing_state.db"):
        self.path = str(path)

    def _connect(self) -> sqlite3.Connection:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS runs (task_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )
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

    def save(self, state: WritingState) -> None:
        self._reconcile_persistence_invariants(state)
        payload = state.model_dump_json()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO runs(task_id,payload,updated_at) VALUES(?,?,?) "
                "ON CONFLICT(task_id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at",
                (state.contract.task_id, payload, state.updated_at.isoformat()),
            )

    def load(self, task_id: str) -> WritingState | None:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM runs WHERE task_id=?", (task_id,)).fetchone()
        return WritingState.model_validate_json(row[0]) if row else None

    def list_recent(self, limit: int = 10) -> list[WritingState]:
        safe_limit = max(1, min(int(limit), 100))
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT payload FROM runs ORDER BY updated_at DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()
        return [WritingState.model_validate_json(row[0]) for row in rows]
