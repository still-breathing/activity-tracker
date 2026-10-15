"""Ride metrics computed from Strava-style streams dicts."""

DEFAULT_MIN_SPEED = 0.5  # m/s; intervals at or below this are stops

_ZONE_LOWER_BOUNDS = (0.6, 0.7, 0.8, 0.9)  # fraction of max HR starting zones 2-5


def _data(streams, key):
    return streams.get(key, {}).get("data") or []


def _intervals(streams):
    """Yield (dt, v_start, v_end, hr_end) for each consecutive sample pair.

    Speed and heart rate are None when their stream is missing.
    """
    time = _data(streams, "time")
    velocity = _data(streams, "velocity_smooth")
    heartrate = _data(streams, "heartrate")
    for i in range(len(time) - 1):
        yield (
            time[i + 1] - time[i],
            velocity[i] if velocity else None,
            velocity[i + 1] if velocity else None,
            heartrate[i + 1] if heartrate else None,
        )


def total_distance_km(streams):
    metres = sum(
        dt * (v0 + v1) / 2
        for dt, v0, v1, _ in _intervals(streams)
        if v0 is not None
    )
    return metres / 1000


def elapsed_time_s(streams):
    time = _data(streams, "time")
    return time[-1] - time[0] if time else 0


def moving_time_s(streams, min_speed=DEFAULT_MIN_SPEED):
    return sum(
        dt
        for dt, _, v1, _ in _intervals(streams)
        if v1 is not None and v1 > min_speed
    )


def avg_speed_kmh(streams, min_speed=DEFAULT_MIN_SPEED):
    moving = moving_time_s(streams, min_speed)
    if moving == 0:
        return 0.0
    return total_distance_km(streams) / (moving / 3600)


def avg_heart_rate(streams):
    hr = _data(streams, "heartrate")
    return sum(hr) / len(hr) if hr else None


def max_heart_rate(streams):
    hr = _data(streams, "heartrate")
    return max(hr) if hr else None


def time_in_hr_zones(streams, max_hr):
    if max_hr <= 0:
        raise ValueError("max_hr must be positive")
    zones = {zone: 0 for zone in range(1, 6)}
    bounds = [max_hr * f for f in _ZONE_LOWER_BOUNDS]
    for dt, _, _, hr in _intervals(streams):
        if hr is None:
            continue
        zone = 1 + sum(hr >= bound for bound in bounds)
        zones[zone] += dt
    return zones
