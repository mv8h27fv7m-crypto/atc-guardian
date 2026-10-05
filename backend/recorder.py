"""Durable SQLite event history. A new session preserves all earlier sessions."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class Recorder:
    def __init__(self, path: str):
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY, created TEXT, scenario TEXT, settings TEXT);
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY, session TEXT, sim_s REAL, wall_utc TEXT,
                kind TEXT, callsign TEXT, message TEXT, data TEXT);
            CREATE INDEX IF NOT EXISTS event_session ON events(session, id);
        """)
        self.db.commit()

    def begin(self, session: str, scenario: str, settings: dict):
        self.db.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)",
                        (session, datetime.now(timezone.utc).isoformat(), scenario, json.dumps(settings)))
        self.db.commit()

    def record(self, session: str, sim_s: float, kind: str, message: str,
               callsign: str | None = None, data: dict | None = None):
        self.db.execute("INSERT INTO events VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
                        (session, sim_s, datetime.now(timezone.utc).isoformat(), kind, callsign, message, json.dumps(data or {})))
        self.db.commit()

    def events(self, session: str, limit: int | None = None) -> list[dict]:
        sql = "SELECT * FROM events WHERE session = ? ORDER BY id DESC"
        rows = self.db.execute(sql + (" LIMIT ?" if limit else ""), (session, limit) if limit else (session,))
        return [{**dict(row), "data": json.loads(row["data"])} for row in rows]

    def close(self):
        self.db.close()
