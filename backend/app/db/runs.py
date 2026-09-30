"""SQLite run snapshots; dataset CRUD remains intentionally in memory."""
import sqlite3
from pathlib import Path
from uuid import UUID
from app.schemas.runs import RunRecord


class RunStore:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def save(self, record: RunRecord) -> None:
        with self.connect() as connection:
            connection.execute("INSERT INTO runs (id, payload) VALUES (?, ?)",
                               (str(record.run.id), record.model_dump_json()))

    def get(self, run_id: UUID) -> RunRecord | None:
        with self.connect() as connection:
            row = connection.execute("SELECT payload FROM runs WHERE id = ?", (str(run_id),)).fetchone()
        return RunRecord.model_validate_json(row[0]) if row else None

    def list(self, limit: int = 100) -> list[RunRecord]:
        with self.connect() as connection:
            rows = connection.execute("SELECT payload FROM runs ORDER BY rowid DESC LIMIT ?", (limit,)).fetchall()
        return [RunRecord.model_validate_json(row[0]) for row in rows]
