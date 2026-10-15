PERSONAL ACTIVITY TRACKER
=========================

A single-user progressive web app (PWA) that shows my cycling activities from
Strava. Most rides are commutes, so moving time and average speed are the key
metrics, not just elapsed time.

STATUS
------
Early development. The project skeleton, test setup and a synthetic ride
fixture are in place. The metrics tests are written first and currently FAIL
on purpose; app/services/metrics.py is still empty. Most other modules are
empty placeholders. The app does not run yet.


STACK
-----
Backend   Python, FastAPI, SQLite
Frontend  Vanilla JS, Leaflet (maps), Chart.js (charts), installable PWA
Tests     pytest


PROJECT LAYOUT
--------------
app/
  main.py             FastAPI app entry point
  config.py           Settings loaded from the environment (.env)
  db.py               SQLite connection and schema
  models.py           Pydantic schemas
  data_source/
    auth.py           Strava OAuth token exchange and refresh
    client.py         Strava API calls (activities, streams)
  services/
    metrics.py        Ride metrics computed from Strava streams
  routers/
    activities.py     Activity list/detail endpoints
    oauth.py          OAuth login and callback endpoints
frontend/
  index.html, manifest.webmanifest, service-worker.js
  css/style.css
  js/app.js, api.js, map.js (Leaflet), charts.js (Chart.js)
  icons/              PWA icons (to be added)
tests/
  conftest.py         Shared fixtures (ride_streams)
  fixtures/
    ride_streams.json Synthetic Strava streams response (no real data)
  test_fixtures.py    Checks the fixture is well formed and consistent
  test_metrics.py     Tests for app/services/metrics.py


SETUP (Windows)
---------------
1. Create and activate a virtual environment:

     python -m venv .venv
     .venv\Scripts\activate

2. Install dependencies:

     pip install -r requirements.txt

3. Create a .env file in the project root for Strava credentials. It is
   ignored by git. Never commit it, print it, or paste it into logs or chats.


RUNNING THE TESTS
-----------------
     python -m pytest

Right now the tests in tests/test_metrics.py fail because the metrics module
is not implemented yet. The tests in tests/test_fixtures.py pass.


METRICS (as specified by the tests)
-----------------------------------
All metrics are computed from Strava streams: time, velocity_smooth,
heartrate, altitude and latlng.

total_distance_km     Trapezoid integral of velocity_smooth over time, in km.
elapsed_time_s        Last time minus first time, stops included.
moving_time_s         Seconds in intervals where speed is above min_speed
                      (default 0.5 m/s). Each interval uses the speed at its
                      ending sample.
avg_speed_kmh         Distance divided by moving time (not elapsed time).
avg_heart_rate        Mean heart rate. None if there is no heart rate data.
max_heart_rate        Highest heart rate. None if there is no data.
time_in_hr_zones      Seconds in five zones given max_hr: Z1 below 60%,
                      Z2 60-70%, Z3 70-80%, Z4 80-90%, Z5 90% and above.
                      The lower edge of each zone is inclusive.


DEVELOPMENT RULES
-----------------
- Secrets live in .env only. Never print, log or commit them.
- Develop against fixtures in tests/fixtures/, not the live Strava API.
  Fixtures named real_* are git-ignored.
- Write tests first. Make one small change at a time.
- Show a plan before editing multiple files.
- Run pytest before calling any task done.
