"""SQLite storage for activities and their Strava-style streams."""

import json
import sqlite3

_SCHEMA = """
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    streams TEXT
)
"""


def init_schema(conn):
    conn.execute(_SCHEMA)


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    return conn


def upsert_activity(conn, activity_id, name, start_time, streams=None):
    """Insert or update an activity. streams=None keeps any stored streams."""
    conn.execute(
        """
        INSERT INTO activities (id, name, start_time, streams)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            start_time = excluded.start_time,
            streams = COALESCE(excluded.streams, activities.streams)
        """,
        (
            activity_id,
            name,
            start_time,
            None if streams is None else json.dumps(streams),
        ),
    )


def get_activity(conn, activity_id):
    row = conn.execute(
        "SELECT id, name, start_time, streams FROM activities WHERE id = ?",
        (activity_id,),
    ).fetchone()
    if row is None:
        return None
    activity = dict(row)
    if activity["streams"] is not None:
        activity["streams"] = json.loads(activity["streams"])
    return activity


def list_activities(conn):
    """All activities, newest first, without their streams."""
    rows = conn.execute(
        "SELECT id, name, start_time FROM activities ORDER BY start_time DESC"
    ).fetchall()
    return [dict(row) for row in rows]
