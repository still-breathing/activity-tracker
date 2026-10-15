import sqlite3

import pytest

from app.services import db

START = "2026-10-14T02:30:00Z"


@pytest.fixture
def conn():
    connection = db.connect(":memory:")
    yield connection
    connection.close()


def _count(conn):
    return conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]


def test_init_schema_is_idempotent(conn):
    db.init_schema(conn)
    db.init_schema(conn)


def test_upsert_then_get_returns_fields(conn):
    db.upsert_activity(conn, 1001, "Morning commute", START)
    activity = db.get_activity(conn, 1001)
    assert activity["id"] == 1001
    assert activity["name"] == "Morning commute"
    assert activity["start_time"] == START


def test_streams_round_trip_matches_fixture(conn, ride_streams):
    db.upsert_activity(conn, 1001, "Morning commute", START, ride_streams)
    assert db.get_activity(conn, 1001)["streams"] == ride_streams


def test_upserting_same_id_twice_leaves_one_row(conn, ride_streams):
    db.upsert_activity(conn, 1001, "Morning commute", START, ride_streams)
    db.upsert_activity(conn, 1001, "Morning commute", START, ride_streams)
    assert _count(conn) == 1


def test_second_upsert_updates_fields(conn, ride_streams):
    db.upsert_activity(conn, 1001, "Old name", START, {"time": {"data": [0, 1]}})
    db.upsert_activity(conn, 1001, "New name", "2026-10-14T03:00:00Z", ride_streams)
    activity = db.get_activity(conn, 1001)
    assert activity["name"] == "New name"
    assert activity["start_time"] == "2026-10-14T03:00:00Z"
    assert activity["streams"] == ride_streams


def test_second_upsert_without_streams_keeps_existing_streams(conn, ride_streams):
    db.upsert_activity(conn, 1001, "Morning commute", START, ride_streams)
    db.upsert_activity(conn, 1001, "Renamed", START)
    activity = db.get_activity(conn, 1001)
    assert activity["name"] == "Renamed"
    assert activity["streams"] == ride_streams


def test_different_ids_create_separate_rows(conn):
    db.upsert_activity(conn, 1001, "A", START)
    db.upsert_activity(conn, 1002, "B", START)
    assert _count(conn) == 2


def test_get_unknown_id_returns_none(conn):
    assert db.get_activity(conn, 999) is None


def test_activity_without_streams_has_none_streams(conn):
    db.upsert_activity(conn, 1001, "No streams", START)
    assert db.get_activity(conn, 1001)["streams"] is None


def test_list_activities_newest_first_without_streams(conn, ride_streams):
    db.upsert_activity(conn, 1, "oldest", "2026-10-01T07:00:00Z", ride_streams)
    db.upsert_activity(conn, 2, "newest", "2026-10-14T07:00:00Z", ride_streams)
    db.upsert_activity(conn, 3, "middle", "2026-10-07T07:00:00Z", ride_streams)
    activities = db.list_activities(conn)
    assert [a["name"] for a in activities] == ["newest", "middle", "oldest"]
    assert all("streams" not in a for a in activities)


def test_file_backed_db_persists_across_connections(tmp_path, ride_streams):
    path = tmp_path / "activities.db"
    first = db.connect(path)
    db.upsert_activity(first, 1001, "Morning commute", START, ride_streams)
    first.commit()
    first.close()

    second = db.connect(path)
    try:
        activity = db.get_activity(second, 1001)
        assert activity["name"] == "Morning commute"
        assert activity["streams"] == ride_streams
    finally:
        second.close()


def test_raw_duplicate_insert_violates_primary_key(conn):
    db.upsert_activity(conn, 1001, "A", START)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO activities (id, name, start_time) VALUES (?, ?, ?)",
            (1001, "dup", START),
        )
