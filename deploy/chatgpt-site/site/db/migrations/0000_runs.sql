CREATE TABLE IF NOT EXISTS runs (
  task_id TEXT PRIMARY KEY,
  payload TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS runs_updated_at_idx ON runs(updated_at DESC);
