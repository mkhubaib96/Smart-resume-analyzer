"""
Storage layer (SQLite) — supports Module 1's "Store resume information"
requirement and gives every module a place to persist results.

This module is DONE / working.
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance", "resume_analyzer.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            target_role TEXT,
            resume_score INTEGER,
            score_breakdown TEXT,   -- JSON string
            ats_score INTEGER,
            missing_keywords TEXT,  -- JSON string (list)
            suggestions TEXT,       -- JSON string (list)
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_analysis(filename, raw_text, target_role=None, resume_score=None,
                   score_breakdown=None, ats_score=None, missing_keywords=None,
                   suggestions=None):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO analyses
           (filename, raw_text, target_role, resume_score, score_breakdown,
            ats_score, missing_keywords, suggestions, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            filename,
            raw_text,
            target_role,
            resume_score,
            json.dumps(score_breakdown or {}),
            ats_score,
            json.dumps(missing_keywords or []),
            json.dumps(suggestions or []),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    analysis_id = cur.lastrowid
    conn.close()
    return analysis_id


def get_analysis(analysis_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    result = dict(row)
    result["score_breakdown"] = json.loads(result["score_breakdown"] or "{}")
    result["missing_keywords"] = json.loads(result["missing_keywords"] or "[]")
    result["suggestions"] = json.loads(result["suggestions"] or "[]")
    return result


def get_history(limit=20):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, filename, target_role, resume_score, ats_score, created_at "
        "FROM analyses ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
