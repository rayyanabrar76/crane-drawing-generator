"""SQLite storage for saved crane designs."""
import json
import sqlite3
from datetime import datetime, timezone

DB_FILE = "cranes.db"


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS designs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                inputs TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


def _now():
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "inputs": json.loads(row["inputs"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_design(name, inputs):
    now = _now()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO designs (name, inputs, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (name, json.dumps(inputs), now, now),
        )
        new_id = cur.lastrowid
    return get_design(new_id)


def list_designs():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM designs ORDER BY updated_at DESC").fetchall()
    return [_row_to_dict(r) for r in rows]


def get_design(design_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM designs WHERE id = ?", (design_id,)).fetchone()
    return _row_to_dict(row) if row else None


def update_design(design_id, name, inputs):
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE designs SET name = ?, inputs = ?, updated_at = ? WHERE id = ?",
            (name, json.dumps(inputs), _now(), design_id),
        )
        if cur.rowcount == 0:
            return None
    return get_design(design_id)


def delete_design(design_id):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM designs WHERE id = ?", (design_id,))
    return cur.rowcount > 0
