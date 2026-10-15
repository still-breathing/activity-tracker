# Personal Activity tracker

Single-user PWA that shows my cycling activities from Strava.

## Stack

- Backend: Python, FastAPI, SQLite
- Frontend: vanilla JS, Leaflet, Chart.js, installable PWA
- Tests: pytest, run before declaring any task done

## Rules

- Secrets live in .env only. Never print, log, or commit them.
- Develop against fixtures in tests/fixtures/, not the live API.
- Write tests first. One small change at a time.
- Show a plan before editing multiple files.
- Most of the rides are commutes, so moving time matters, average speed both matters.

## Metric conventions (do not change without updating tests)

- Moving time: an interval counts if its END sample speed is strictly above 0.5 m/s
- HR zones: an interval goes to the zone of its END sample heart rate, lower bound inclusive, compared with integer percent math
- Distance: trapezoid over both samples, across all intervals
- Invalid input: non-decreasing time required, and a present stream must match time in length, otherwise ValueError

## Known limitations

- avg_speed_kmh divides all distance by moving time, so slow creeping below 0.5 m/s nudges it up
- A missing velocity_smooth stream gives 0.0 distance, the same as a ride with no movement
