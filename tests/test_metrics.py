import pytest

from app.services import metrics


def _stream(time, velocity=None, heartrate=None):
    streams = {"time": {"data": time}}
    if velocity is not None:
        streams["velocity_smooth"] = {"data": velocity}
    if heartrate is not None:
        streams["heartrate"] = {"data": heartrate}
    return streams


# --- distance ---------------------------------------------------------------


def test_total_distance_km_for_fixture(ride_streams):
    assert metrics.total_distance_km(ride_streams) == pytest.approx(0.07115, abs=1e-4)


def test_total_distance_km_integrates_speed_over_time():
    streams = _stream([0, 10, 20], velocity=[5, 5, 5])
    assert metrics.total_distance_km(streams) == pytest.approx(0.1)


def test_total_distance_km_is_zero_when_never_moving():
    streams = _stream([0, 1, 2], velocity=[0, 0, 0])
    assert metrics.total_distance_km(streams) == 0.0


# --- elapsed time -----------------------------------------------------------


def test_elapsed_time_s_for_fixture(ride_streams):
    assert metrics.elapsed_time_s(ride_streams) == 19


def test_elapsed_time_s_includes_stops():
    streams = _stream([0, 10, 30], velocity=[5, 0, 0])
    assert metrics.elapsed_time_s(streams) == 30


# --- moving time ------------------------------------------------------------


def test_moving_time_s_excludes_stops_for_fixture(ride_streams):
    moving = metrics.moving_time_s(ride_streams)
    assert moving == 15
    assert moving < metrics.elapsed_time_s(ride_streams)


def test_moving_time_s_respects_min_speed(ride_streams):
    # v > 3.0 at samples 2-7 and 14-19; sample 8 is exactly 3.0 and excluded.
    assert metrics.moving_time_s(ride_streams, min_speed=3.0) == 12


def test_moving_time_s_counts_intervals_not_samples():
    assert metrics.moving_time_s(_stream([0, 1, 2], velocity=[0.0, 5, 5])) == 2
    assert metrics.moving_time_s(_stream([0, 1, 2], velocity=[5, 0.0, 0.0])) == 0


def test_moving_time_s_equals_elapsed_time_without_stops():
    streams = _stream([0, 1, 2, 3], velocity=[4, 4, 4, 4])
    assert metrics.moving_time_s(streams) == metrics.elapsed_time_s(streams) == 3


# --- heart rate -------------------------------------------------------------


def test_avg_heart_rate_for_fixture(ride_streams):
    assert metrics.avg_heart_rate(ride_streams) == pytest.approx(108.8)


def test_max_heart_rate_for_fixture(ride_streams):
    assert metrics.max_heart_rate(ride_streams) == 121


@pytest.mark.parametrize("streams", [{}, {"heartrate": {"data": []}}])
def test_heart_rate_is_none_without_data(streams):
    assert metrics.avg_heart_rate(streams) is None
    assert metrics.max_heart_rate(streams) is None


# --- heart rate zones -------------------------------------------------------


def test_time_in_hr_zones_max_hr_190(ride_streams):
    assert metrics.time_in_hr_zones(ride_streams, max_hr=190) == {
        1: 11, 2: 8, 3: 0, 4: 0, 5: 0,
    }


def test_time_in_hr_zones_max_hr_140(ride_streams):
    assert metrics.time_in_hr_zones(ride_streams, max_hr=140) == {
        1: 0, 2: 1, 3: 9, 4: 9, 5: 0,
    }


@pytest.mark.parametrize("max_hr", [190, 140])
def test_time_in_hr_zones_sum_to_elapsed_time(ride_streams, max_hr):
    zones = metrics.time_in_hr_zones(ride_streams, max_hr=max_hr)
    assert sum(zones.values()) == metrics.elapsed_time_s(ride_streams)


def test_time_in_hr_zones_lower_bound_is_inclusive():
    # 60/70/80/90% of 200 are 120/140/160/180; each starts the next zone.
    streams = _stream([0, 1, 2, 3, 4], heartrate=[100, 120, 140, 160, 180])
    assert metrics.time_in_hr_zones(streams, max_hr=200) == {
        1: 0, 2: 1, 3: 1, 4: 1, 5: 1,
    }


@pytest.mark.parametrize("max_hr", [0, -1])
def test_time_in_hr_zones_rejects_invalid_max_hr(ride_streams, max_hr):
    with pytest.raises(ValueError):
        metrics.time_in_hr_zones(ride_streams, max_hr=max_hr)
