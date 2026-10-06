from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import WritingState


class SQLiteStateStore:
    def __init__(self, path: str | Path = "financial_writing_state.db"):
        self.path = str(path)
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS runs (task_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL)"
            )

    def save(self, state: WritingState) -> None:
        payload = state.model_dump_json()
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT INTO runs(task_id,payload,updated_at) VALUES(?,?,?) "
                "ON CONFLICT(task_id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at",
                (state.contract.task_id, payload, state.updated_at.isoformat()),
            )

    def load(self, task_id: str) -> WritingState | None:
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("SELECT payload FROM runs WHERE task_id=?", (task_id,)).fetchone()
        return WritingState.model_validate_json(row[0]) if row else None
