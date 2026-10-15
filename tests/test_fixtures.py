import math

import pytest

STREAM_TYPES = {"time", "heartrate", "velocity_smooth", "altitude", "latlng"}
EARTH_RADIUS_M = 6371000.0


def _haversine_m(a, b):
    lat1, lat2 = math.radians(a[0]), math.radians(b[0])
    dlat = lat2 - lat1
    dlng = math.radians(b[1] - a[1])
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(h))


def test_ride_streams_has_all_stream_types(ride_streams):
    assert set(ride_streams) == STREAM_TYPES


def test_ride_streams_are_equal_length(ride_streams):
    lengths = {len(s["data"]) for s in ride_streams.values()}
    assert len(lengths) == 1
    for s in ride_streams.values():
        assert s["original_size"] == len(s["data"])


def test_latlng_entries_are_pairs(ride_streams):
    for point in ride_streams["latlng"]["data"]:
        lat, lng = point
        assert -90 <= lat <= 90
        assert -180 <= lng <= 180


def test_ride_includes_a_stop(ride_streams):
    # Moving time must be less than elapsed time for this ride.
    assert 0.0 in ride_streams["velocity_smooth"]["data"][1:]


def test_latlng_path_matches_velocity(ride_streams):
    # The route length and the integrated speed must describe the same ride.
    t = ride_streams["time"]["data"]
    v = ride_streams["velocity_smooth"]["data"]
    pts = ride_streams["latlng"]["data"]
    integral = sum((v[i - 1] + v[i]) / 2 * (t[i] - t[i - 1]) for i in range(1, len(t)))
    path = sum(_haversine_m(pts[i - 1], pts[i]) for i in range(1, len(pts)))
    assert path == pytest.approx(integral, rel=0.02)
