STREAM_TYPES = {"time", "heartrate", "velocity_smooth", "altitude", "latlng"}


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
